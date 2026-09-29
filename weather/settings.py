"""ユーザー設定の読み書き。GUI が編集する対象はここだけ。"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

from . import paths

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCHEMA_VERSION = 1
HEADER = "header"
PLACE = "place"


@dataclass
class Item:
    """地点リストの1要素。地点その か、ブロックの見出し。"""
    type: str
    text: str

    @property
    def is_header(self) -> bool:
        return self.type == HEADER

    def to_dict(self) -> dict:
        return {"type": self.type, "text": self.text}

    @staticmethod
    def from_dict(d: dict) -> "Item":
        return Item(type=d.get("type", PLACE), text=d.get("text", ""))


@dataclass
class Group:
    """グループ = まとめて取得・表示する地点のまとまり。"""
    name: str
    items: list[Item] = field(default_factory=list)

    def places(self) -> list[str]:
        return [i.text for i in self.items if not i.is_header]

    def headers(self) -> list[str]:
        return [i.text for i in self.items if i.is_header]

    def to_dict(self) -> dict:
        return {"name": self.name, "items": [i.to_dict() for i in self.items]}

    @staticmethod
    def from_dict(d: dict) -> "Group":
        return Group(
            name=d.get("name", ""),
            items=[Item.from_dict(i) for i in d.get("items", [])],
        )


@dataclass
class Term:
    """表示期間。開始日は 'YYYY-MM-DD' で持つ。"" が未設定なら本日。"""

    start: str = ""
    days: int = 10

    def start_date(self) -> date:
        return _parse_iso_date(self.start) or date.today()

    def end_date(self) -> date:
        return self.start_date() + timedelta(days=self.days - 1)

    def dates(self) -> list[date]:
        return [self.start_date() + timedelta(days=i) for i in range(self.days)]

    def set_start(self, d: date) -> None:
        self.start = d.isoformat()

    def to_dict(self) -> dict:
        return {"start": self.start_date().isoformat(), "days": self.days}

    @staticmethod
    def from_dict(d: dict) -> "Term":
        raw = d.get("start")
        if _parse_iso_date(raw if isinstance(raw, str) else ""):
            start = raw
        else:
            # 旧形式 (start_offset_days) は今日起点の相対値なので読み替他日が確定
            try:
                offset = int(d.get("start_offset_days", 0))
            except (TypeError, ValueError):
                offset = 0
            start = (date.today() + timedelta(days=offset)).isoformat()
        return Term(
            start=start,
            days=_clamp(int(d.get("days", 10)), 1, paths.MAX_DAYS),
        )


@dataclass
class Display:
    show_icons: bool = True
    dedupe: bool = True

    def to_dict(self) -> dict:
        return {"show_icons": self.show_icons, "dedupe": self.dedupe}

    @staticmethod
    def from_dict(d: dict) -> "Display":
        return Display(
            show_icons=bool(d.get("show_icons", True)),
            dedupe=bool(d.get("dedupe", True)),
        )


@dataclass
class Settings:
    term: Term = field(default_factory=Term)
    active_groups: list[str] = field(default_factory=list)
    groups: list[Group] = field(default_factory=list)
    display: Display = field(default_factory=Display)

    def group(self, name: str) -> Group | None:
        return next((g for g in self.groups if g.name == name), None)

    def active(self) -> list[Group]:
        return [g for g in self.groups if g.name in self.active_groups]

    def resolved_items(self) -> list[Item]:
        """有効なグループの要素を順に並べる。dedupe が有効なら地点は最初の1回だけ残す。"""
        out: list[Item] = []
        seen: set[str] = set()
        for group in self.active():
            for item in group.items:
                if self.display.dedupe and not item.is_header:
                    if item.text in seen:
                        continue
                    seen.add(item.text)
                out.append(item)
        return out

    def resolved_places(self) -> list[str]:
        """取得対象の場所名のみ。見出しは除く。"""
        return [i.text for i in self.resolved_items() if not i.is_header]

    def to_dict(self) -> dict:
        return {
            "schema_version": SCHEMA_VERSION,
            "term": self.term.to_dict(),
            "active_groups": self.active_groups,
            "groups": [g.to_dict() for g in self.groups],
            "display": self.display.to_dict(),
        }

    def save(self, path: Path | None = None) -> None:
        # パスを実行時に解決する（import 時の既定値に固定しない）
        target = paths.SETTINGS_JSON if path is None else path
        target.write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def load(path: Path | None = None) -> "Settings":
        target = paths.SETTINGS_JSON if path is None else path
        if not target.exists():
            return Settings()
        try:
            return _from_dict(json.loads(target.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            backup = target.with_suffix(".json.corrupt")
            target.replace(backup)
            print(f"設定ファイルが読めませんでした（{e}）。{backup.name} に退避し、初期設定で開始します。")
            return Settings()


def _from_dict(d: dict) -> Settings:
    if not isinstance(d, dict):
        raise ValueError("設定のルートがオブジェクトではありません")
    s = Settings(
        term=Term.from_dict(d.get("term", {})),
        active_groups=list(d.get("active_groups", [])),
        groups=[Group.from_dict(g) for g in d.get("groups", [])],
        display=Display.from_dict(d.get("display", {})),
    )
    # active_groups に消えたグループの名前が残っていても落ちないようにする
    names = {g.name for g in s.groups}
    s.active_groups = [n for n in s.active_groups if n in names]
    return s


def _clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))


def _parse_iso_date(s: str) -> date | None:
    try:
        return date.fromisoformat(s)
    except (ValueError, TypeError):
        return None


# --- 静的な tenki.jp 対応表 -------------------------------------------------

_PLACES_CACHE: dict[str, str] | None = None


def load_places(path: Path | None = None) -> dict[str, str]:
    """地名 -> tenki.jp のパス。data/places.json は静的なのでプロセス内でキャッシュする。"""
    global _PLACES_CACHE
    if _PLACES_CACHE is not None:
        return _PLACES_CACHE
    target = paths.PLACES_JSON if path is None else path
    if not target.exists():
        raise FileNotFoundError(f"対応表がありません: {target}")
    doc = json.loads(target.read_text(encoding="utf-8"))
    places = doc.get("places", doc)
    if not isinstance(places, dict):
        raise ValueError(f"対応表の形式が不正です: {target}")
    _PLACES_CACHE = places
    return places


def search_places(query: str, limit: int = 30) -> list[str]:
    """検索文字列を含む地名。前方一致を優先して返す。"""
    q = query.strip()
    if not q:
        return []
    names = load_places()
    starts = [n for n in names if n.startswith(q)]
    contains = [n for n in names if q in n and not n.startswith(q)]
    return (starts + contains)[:limit]
