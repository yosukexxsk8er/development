"""結果を HTML に出力する。

- 使ったアイコンだけを出力先脇の icons/ にコピーして相対参照で書く（オフラインでも見れる）
- 日付行は position:sticky で固定する
"""
from __future__ import annotations

import html
import shutil
import webbrowser
from datetime import date
from pathlib import Path

from . import paths
from .settings import Item, Term
from .tenki import IconStore, PlaceForecast

WEEKDAYS = "月火水木金土日"

_CSS = """
body { font-family: "Yu Gothic UI", "Meiryo", sans-serif; margin: 16px; color: #222; }
h1 { font-size: 18px; margin: 0 0 4px; }
.announced { font-size: 12px; color: #666; margin-bottom: 12px; }
table { border-collapse: separate; border-spacing: 0; font-size: 12px; }
th, td { border: 1px solid #ccc; padding: 4px 6px; text-align: center; white-space: nowrap; }
th { background: #e8eef5; position: sticky; top: 0; z-index: 1; }
th.rowhead, td.rowhead {
  position: sticky; left: 0; background: #f6f6f6;
  text-align: left; font-weight: normal; z-index: 2;
}
th.rowhead { z-index: 3; }
tr.head-row td { background: #fff4d6; font-weight: bold; text-align: left; }
tr.fail td { background: #fdecea; color: #a12; }
img { width: 47px; height: 30px; vertical-align: middle; }
.precip { display: block; font-size: 11px; color: #555; }
""".strip()


def build_html(
    items: list[Item],
    forecasts: dict[str, PlaceForecast],
    term: Term,
    icons: IconStore | None = None,
    show_icons: bool = True,
    title: str = "天気予報",
) -> str:
    dates = term.dates()
    out: list[str] = []
    announced = next(
        (f.announced for f in forecasts.values() if f.announced and not f.error), None
    )

    out.append("<!DOCTYPE html>")
    out.append('<html lang="ja"><head><meta charset="utf-8">')
    out.append(f"<title>{html.escape(title)}</title>")
    out.append(f"<style>\n{_CSS}\n</style>")
    out.append("</head><body>")
    out.append(f"<h1>{html.escape(title)}</h1>")
    span = f"{term.start_date():%m/%d} 〜 {term.end_date():%m/%d}"
    if announced:
        out.append(f'<p class="announced">{html.escape(span)} の {html.escape(announced)}</p>')
    else:
        out.append(f'<p class="announced">{html.escape(span)}</p>')

    out.append("<table><thead><tr><th class='rowhead'></th>")
    for d in dates:
        out.append(f"<th>{d.month}/{d.day}<br><small>({WEEKDAYS[d.weekday()]})</small></th>")
    out.append("</tr></thead><tbody>")

    for item in items:
        if item.is_header:
            out.append(
                f"<tr class='head-row'><td class='rowhead' colspan='{len(dates) + 1}'>"
                f"{html.escape(item.text)}</td></tr>"
            )
            continue
        forecast = forecasts.get(item.text)
        out.append(_row(item.text, forecast, dates, icons, show_icons))

    out.append("</tbody></table></body></html>")
    return "\n".join(out)


def _row(
    place: str,
    forecast: PlaceForecast | None,
    dates: list[date],
    icons: IconStore | None,
    show_icons: bool,
) -> str:
    name = html.escape(place)
    if forecast is None or forecast.error:
        reason = html.escape(forecast.error) if forecast and forecast.error else "未取得"
        return f"<tr class='fail'><td class='rowhead'>{name}</td><td colspan='{len(dates)}'>{reason}</td></tr>"

    cells = []
    for d in dates:
        daily = forecast.on(d)
        if daily is None:
            cells.append("<td>-</td>")
            continue
        body = _icon_img(daily.icon_url, icons) if show_icons else ""
        if not body:
            body = html.escape(daily.telop or "")
        nums = " ".join(x for x in (daily.prob, daily.precip) if x)
        if nums:
            body += f'<span class="precip">{html.escape(nums)}</span>'
        cells.append(f"<td>{body}</td>")
    return f"<tr><td class='rowhead'>{name}</td>{''.join(cells)}</tr>"


def _icon_img(url: str | None, icons: IconStore | None) -> str:
    """アイコンが取得できるときだけ <img> にする。無理なら空文字（文字列表示に任せる）。"""
    if not url or icons is None:
        return ""
    try:
        if not icons.path_for(url).exists():
            return ""
    except Exception:  # noqa: BLE001
        return ""
    return f'<img src="icons/{url.rsplit("/", 1)[-1]}" alt="">'


def copy_icons(forecasts: dict[str, PlaceForecast], out_dir: Path, icons: IconStore | None) -> int:
    """HTML から参照するアイコンだけを出力先脇にコピーする。"""
    if icons is None:
        return 0
    dest = out_dir / "icons"
    dest.mkdir(parents=True, exist_ok=True)
    count = 0
    for url in used_icon_urls(forecasts):
        src = icons.path_for(url)
        if src.exists() and src.stat().st_size > 0:
            shutil.copy2(src, dest / src.name)
            count += 1
    return count


def used_icon_urls(forecasts: dict[str, PlaceForecast]) -> set[str]:
    return {
        d.icon_url
        for f in forecasts.values()
        if not f.error
        for d in f.days
        if d.icon_url
    }


def save(
    items: list[Item],
    forecasts: dict[str, PlaceForecast],
    term: Term,
    out_path: Path = paths.EXPORT_HTML,
    icons: IconStore | None = None,
    show_icons: bool = True,
    title: str = "天気予報",
) -> Path:
    doc = build_html(items, forecasts, term, icons, show_icons, title)
    out_path.write_text(doc, encoding="utf-8")
    if icons is not None:
        copy_icons(forecasts, out_path.parent, icons)
    return out_path


def open_in_browser(path: Path) -> None:
    webbrowser.open(path.resolve().as_uri())
