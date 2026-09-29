"""tenki.jp から10日間予報を取得してパースする。

- 1都市1リクエスト（発表時刻も同じレスポンスから取る）
- ThreadPoolExecutor で並列取得。1都市が失敗しても全体は止めない
- アイコンは tenki が返している URL をそのまま使う（手動の対応表を持たない）
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from io import BytesIO
from pathlib import Path

import lxml.html
import requests
from PIL import Image

from . import paths
from .settings import load_places

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) weather-forecast-viewer"
MAX_WORKERS = 5
TIMEOUT = 10
RETRIES = 3
_ICON_RETRIES = 2

# 1日 = 1つの dd。10日予報ページは14日分あるが構造は同じ。
_XP_ROWS = '//dd[contains(@class,"forecast10days-actab")]'
_XP_DAY = './div[@class="days"]'
_XP_TELOP = './/span[contains(@class,"forecast-telop")]'
_XP_PROB = './div[@class="prob-precip"]'
_XP_PRECIP = './div[@class="precip"]'
_XP_ICON = './div[@class="forecast"]//img/@src'
_XP_ANNOUNCE = '//div[@id="main-column"]//h2/time'


class FetchError(Exception):
    """1都市の取得に失敗した。メッセージは GUI のログに出す。"""


@dataclass
class Daily:
    date: str          # "09月26日(土)" の表示文字列
    day: str | None    # "2026-09-26"
    telop: str | None  # "雨のち曇"
    prob: str | None   # "80%"
    precip: str | None # "6mm"
    icon_url: str | None

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Daily":
        return Daily(**{k: d.get(k) for k in ("date", "day", "telop", "prob", "precip", "icon_url")})


@dataclass
class PlaceForecast:
    place: str
    announced: str | None = None
    days: list[Daily] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "place": self.place,
            "announced": self.announced,
            "days": [d.to_dict() for d in self.days],
            "error": self.error,
        }

    @staticmethod
    def from_dict(d: dict) -> "PlaceForecast":
        return PlaceForecast(
            place=d["place"],
            announced=d.get("announced"),
            days=[Daily.from_dict(x) for x in d.get("days", [])],
            error=d.get("error"),
        )

    def on(self, day: date) -> Daily | None:
        return next((d for d in self.days if d.day == day.isoformat()), None)


# --- 取得 -------------------------------------------------------------------

def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    return s


def forecast_url(place: str, places: dict[str, str] | None = None) -> str:
    places = places if places is not None else load_places()
    path = places.get(place)
    if path is None:
        raise FetchError(f"『{place}』は対応表にありません")
    return f"{paths.BASE_URL}{path}10days.html"


def _get_text(session: requests.Session, url: str) -> str:
    last = ""
    for attempt in range(RETRIES):
        try:
            r = session.get(url, timeout=TIMEOUT)
            r.raise_for_status()
            # tenki は Content-Type に charset を付けないため自動判定だと文字化けする
            return r.content.decode("utf-8")
        except Exception as e:  # noqa: BLE001 - 1都市の失敗は握り潰してリトライ
            last = f"{type(e).__name__}: {e}"
            if attempt + 1 < RETRIES:
                time.sleep(0.5 * (2**attempt))
    raise FetchError(last)


def parse(html: str) -> tuple[str | None, list[Daily]]:
    tree = lxml.html.fromstring(html)
    announced = None
    nodes = tree.xpath(_XP_ANNOUNCE)
    if nodes:
        announced = nodes[0].text_content().strip() or None

    days: list[Daily] = []
    for dd in tree.xpath(_XP_ROWS):
        raw_day = _text(dd, _XP_DAY)
        if raw_day is None:
            continue
        days.append(
            Daily(
                date=raw_day,
                day=parse_day(raw_day),
                telop=_text(dd, _XP_TELOP),
                prob=_text(dd, _XP_PROB),
                # 予報精度の低い末尾数日には div.precip 自体が無い
                precip=_text(dd, _XP_PRECIP),
                icon_url=_first(dd, _XP_ICON),
            )
        )
    return announced, days


def parse_day(raw: str) -> str | None:
    """'09月26日(土)' -> '2026-09-26'。月日しか無いので、今日にもっとも近い年を割り当てる。"""
    try:
        month, rest = raw.split("月", 1)
        day = int(rest.split("日", 1)[0])
        month = int(month)
    except (ValueError, IndexError):
        return None
    today = date.today()
    candidates = []
    for year in (today.year - 1, today.year, today.year + 1):
        try:
            candidates.append(date(year, month, day))
        except ValueError:
            continue
    if not candidates:
        return None
    return min(candidates, key=lambda d: abs((d - today).days)).isoformat()


def fetch_place(
    place: str, session: requests.Session, places: dict[str, str] | None = None
) -> PlaceForecast:
    """1都市分の取得。失敗しても例外は投げず error に詰める。"""
    try:
        html = _get_text(session, forecast_url(place, places))
        announced, days = parse(html)
        if not days:
            raise FetchError("予報的行が見つかりませんでした（ページ構造の変更？）")
        return PlaceForecast(place=place, announced=announced, days=days)
    except FetchError as e:
        return PlaceForecast(place=place, error=str(e))
    except Exception as e:  # noqa: BLE001 - 想定外でも1都市で止めない
        return PlaceForecast(place=place, error=f"{type(e).__name__}: {e}")


def fetch_all(
    places: list[str],
    on_progress=None,
    force: bool = False,
    cache: "Cache | None" = None,
) -> list[PlaceForecast]:
    """並列取得。on_progress(done, total, place, result) をワーカースレッドから呼ぶ。"""
    total = len(places)
    results: dict[str, PlaceForecast] = {}

    if cache is not None and not force:
        for place in places:
            hit = cache.get(place)
            if hit is not None:
                results[place] = hit
    todo = [p for p in places if p not in results]
    if not todo:
        return [results[p] for p in places]

    done = len(results)

    def task(place: str) -> PlaceForecast:
        # スレッドごとにセッションを持つ（Session はスレッドセーフではない）
        return fetch_place(place, make_session())

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(task, p): p for p in todo}
        for fut in as_completed(futures):
            place = futures[fut]
            try:
                result = fut.result()
            except Exception as e:  # noqa: BLE001
                result = PlaceForecast(place=place, error=f"{type(e).__name__}: {e}")
            results[place] = result
            done += 1
            if on_progress is not None:
                on_progress(done, total, place, result)

    ordered = [results[p] for p in places]
    if cache is not None:
        cache.store(ordered)
    return ordered


# --- キャッシュ ---------------------------------------------------------------

class Cache:
    """JSON ベースの取得キャッシュ。pickle は使わない（クラスの定義が変わると読めなくなる）。"""

    VERSION = 1

    def __init__(self, path: Path = paths.CACHE_JSON):
        self.path = path
        self.data: dict = {"version": self.VERSION, "fetched_at": {}, "places": {}}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            doc = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        if doc.get("version") != self.VERSION:
            return
        if isinstance(doc.get("places"), dict) and isinstance(doc.get("fetched_at"), dict):
            self.data = doc

    def is_fresh(self, places: list[str] | None = None) -> bool:
        """places のすべてを今日取得済みなら True。places 省略時は全キャッシュを見る。"""
        today = date.today()
        targets = places if places is not None else list(self.data["places"])
        if not targets:
            return False
        for place in targets:
            raw = self.data["places"].get(place)
            if not raw or raw.get("error"):
                return False
            stamp = self.data["fetched_at"].get(place)
            if not stamp:
                return False
            try:
                if datetime.fromisoformat(stamp).date() != today:
                    return False
            except ValueError:
                return False
        return True

    def get(self, place: str) -> PlaceForecast | None:
        raw = self.data["places"].get(place)
        if not raw or raw.get("error"):
            return None
        try:
            return PlaceForecast.from_dict(raw)
        except (TypeError, KeyError):
            return None

    def store(self, forecasts: list[PlaceForecast]) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        for f in forecasts:
            if not f.error:
                self.data["places"][f.place] = f.to_dict()
                self.data["fetched_at"][f.place] = now
        self.save()

    def save(self) -> None:
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )


# --- アイコン ----------------------------------------------------------------

class IconStore:
    """tenki が返したアイコンをローカルにキャッシュして PIL Image を返す。"""

    def __init__(self, directory: Path = paths.ICON_CACHE_DIR):
        self.dir = directory
        self.dir.mkdir(parents=True, exist_ok=True)
        self._session = make_session()
        self._session.headers["Referer"] = f"{paths.BASE_URL}/"
        self._memo: dict[str, Image.Image | None] = {}

    def path_for(self, url: str) -> Path:
        return self.dir / url.rsplit("/", 1)[-1]

    def get(self, url: str) -> Image.Image | None:
        """取得失敗時は None。呼び出し側で天気文字列にフォールバックする。"""
        if url in self._memo:
            return self._memo[url]
        image = self._load(url)
        self._memo[url] = image
        return image

    def _load(self, url: str) -> Image.Image | None:
        dest = self.path_for(url)
        if dest.exists() and dest.stat().st_size > 0:
            try:
                return Image.open(dest).convert("RGBA")
            except Exception:  # noqa: BLE001 - 壊れたキャッシュは取り直す
                dest.unlink(missing_ok=True)
        for attempt in range(_ICON_RETRIES):
            try:
                r = self._session.get(url, timeout=TIMEOUT)
                r.raise_for_status()
                image = Image.open(BytesIO(r.content)).convert("RGBA")
                dest.write_bytes(r.content)
                return image
            except Exception as e:  # noqa: BLE001
                if attempt + 1 == _ICON_RETRIES:
                    print(f"アイコンを取得できませんでした {url}: {e}")
        return None

    def cached_paths(self, urls: set[str]) -> list[Path]:
        return [self.path_for(u) for u in sorted(urls) if self.path_for(u).exists()]


# --- 小道具 ------------------------------------------------------------------

def _text(node, xpath: str) -> str | None:
    found = node.xpath(xpath)
    if not found:
        return None
    value = found[0].text_content().strip()
    return value or None


def _first(node, xpath: str) -> str | None:
    found = node.xpath(xpath)
    return found[0] if found else None
