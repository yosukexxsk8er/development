"""エントリポイント: raw CSVマージ -> 集計 -> コンソール + output/report.html.

使い方 (リポジトリルートから1ライナー):
    python loadbike/main_maintenance_note.py
"""
import datetime
import html
from pathlib import Path

from maintenance_note import (HEADERS, Activities, build_report,
                              component_status, dump_list, load_yaml,
                              yearly_summary)
from merge_activities import merge_activities

BASE = Path(__file__).resolve().parent
OUT_HTML = BASE / "output" / "report.html"

CSS = """
body{font-family:sans-serif;max-width:1100px;margin:16px auto;padding:0 12px;
color:#222}
h1{font-size:1.4em}h2{font-size:1.15em;border-bottom:2px solid #888;
padding-bottom:4px;margin-top:28px}
.cards{display:flex;gap:12px;flex-wrap:wrap;margin:12px 0}
.card{border:1px solid #ccc;border-radius:8px;padding:10px 16px;min-width:130px;
background:#f7f7f7}.card b{font-size:1.5em;display:block}
.card.alert{background:#fde8e8;border-color:#d66}.card.warn{background:#fff4d6;
border-color:#c90}
.toolbar{position:sticky;top:0;background:#fff;padding:8px 0;
border-bottom:1px solid #ccc}
.toolbar input[type=text]{width:280px;padding:4px 8px}
table{border-collapse:collapse;width:100%;margin:8px 0;font-size:0.9em}
th,td{border:1px solid #ccc;padding:4px 8px;text-align:left}
th{background:#eee;white-space:nowrap}th.sort{cursor:pointer}
th.sort::after{content:" \\21D5";color:#888}
td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
tr:nth-child(even) td{background:#fafafa}
tr.over td{background:#fde8e8}
.badge{border-radius:4px;padding:1px 8px;font-size:0.85em;white-space:nowrap}
.badge.active{background:#d6ecd6}.badge.retired{background:#e4e4e4}
.badge.over{background:#f5b5b5}.badge.flag{background:#ffe08a}
.bar{width:120px;height:10px;background:#e0e0e0;border-radius:5px;
display:inline-block;vertical-align:middle}
.bar span{display:block;height:100%;border-radius:5px;background:#4a90d9}
.bar span.warn{background:#e6a800}.bar span.over{background:#d00}
.pct{font-size:0.85em;margin-left:6px}.pct.over{color:#d00;font-weight:bold}
.pct.warn{color:#a67c00}
details{margin:6px 0;border:1px solid #ddd;border-radius:6px;padding:4px 10px}
summary{cursor:pointer;font-weight:bold}
.muted{color:#666;font-size:0.85em}
"""

JS = """
function norm(s){return (s||'').toLowerCase();}
var q=document.getElementById('q');
var onlyActive=document.getElementById('onlyActive');
function apply(){
  var kw=norm(q.value);
  document.querySelectorAll('tr[data-name]').forEach(function(tr){
    var hit=!kw||norm(tr.dataset.name).indexOf(kw)>=0;
    tr.style.display=hit?'':'none';
  });
  document.querySelectorAll('details[data-name]').forEach(function(d){
    var hit=!kw||norm(d.dataset.name).indexOf(kw)>=0;
    if(onlyActive.checked&&d.dataset.active!=='1')hit=false;
    d.style.display=hit?'':'none';
  });
}
q.addEventListener('input',apply);
onlyActive.addEventListener('change',apply);
document.querySelectorAll('th.sort').forEach(function(th){
  th.addEventListener('click',function(){
    var tb=th.closest('table').querySelector('tbody');
    var i=Array.prototype.indexOf.call(th.parentNode.children,th);
    var num=th.dataset.num==='1';
    var dir=th.dataset.dir==='asc'?'desc':'asc';
    th.dataset.dir=dir;
    Array.prototype.slice.call(tb.rows).sort(function(a,b){
      var x=a.cells[i].dataset.v!==undefined?a.cells[i].dataset.v:
        a.cells[i].textContent;
      var y=b.cells[i].dataset.v!==undefined?b.cells[i].dataset.v:
        b.cells[i].textContent;
      if(num){x=parseFloat(x);y=parseFloat(y);}
      return (x<y?-1:x>y?1:0)*(dir==='asc'?1:-1);
    }).forEach(function(r){tb.appendChild(r);});
    apply();
  });
});
"""


def esc(s):
    return html.escape(str(s))


def lifespan_text(st):
    parts = []
    if st["lifespan_km"]:
        parts.append(f"{st['lifespan_km']}km")
    if st["lifespan_days"]:
        parts.append(f"{st['lifespan_days']}日")
    return " / ".join(parts) if parts else "-"


def usage_cell(st):
    """寿命バー + %表示。寿命なしは '-'。"""
    if st["ratio_km"] is None and st["ratio_days"] is None:
        return "<td>-</td>"
    ratio = st["ratio_km"] if st["ratio_km"] is not None else st["ratio_days"]
    pct = ratio * 100
    cls = "over" if ratio >= 1 else ("warn" if ratio >= 0.8 else "")
    base = (f"{st['km']:.0f}/{st['lifespan_km']}km" if st["ratio_km"] is not None
            else f"{st['days']}/{st['lifespan_days']}日")
    return (f'<td data-v="{ratio:.4f}">'
            f'<div class="bar"><span class="{cls}" '
            f'style="width:{min(100.0, pct):.1f}%"></span></div>'
            f'<span class="pct {cls}">{pct:.0f}%</span>'
            f'<div class="muted">{esc(base)}</div></td>')


def badge(st):
    if st["flags"]:
        return '<span class="badge flag">要確認</span>'
    if st["exceeded"]:
        return '<span class="badge over">寿命超過</span>'
    if st["active"]:
        return '<span class="badge active">現役</span>'
    return '<span class="badge retired">退役済</span>'


def reasons(st):
    out = []
    if st["exceeded"]:
        if st["ratio_km"] is not None and st["ratio_km"] >= 1:
            out.append(f"寿命超過: {st['km']:.0f}/{st['lifespan_km']}km"
                       f" ({st['ratio_km']:.0%})")
        if st["ratio_days"] is not None and st["ratio_days"] >= 1:
            out.append(f"寿命超過: {st['days']}/{st['lifespan_days']}日"
                       f" ({st['ratio_days']:.0%})")
    if "!退役後" in st["flags"]:
        out.append("退役後のイベントあり (日付の誤記疑い)")
    if "TODO" in st["flags"]:
        out.append("TODOメモあり (要確認)")
    return " / ".join(out)


def history_table(rows):
    th = "".join(f"<th>{esc(h)}</th>" for h in HEADERS)
    trs = []
    for r in rows:
        cls = ' class="over"' if r[5] == "!退役後" else ""
        trs.append(f"<tr{cls}>" + "".join(
            f"<td>{esc(c)}</td>" for c in r) + "</tr>")
    return f"<table><thead><tr>{th}</tr></thead><tbody>{''.join(trs)}" \
        "</tbody></table>"


def build_html(statuses, yearly, total_km, today):
    active = [s for s in statuses if s["active"]]
    issues = [s for s in statuses if s["exceeded"] or s["flags"]]

    cards = (
        f'<div class="card"><b>{len(active)}</b>現役個体</div>'
        f'<div class="card{" alert" if issues else ""}"><b>{len(issues)}</b>'
        "要確認</div>"
        f'<div class="card"><b>{total_km:,.0f} km</b>総走行距離</div>'
        f'<div class="card"><b>{len(statuses)}</b>管理個体</div>')

    a_rows = []
    for s in sorted(active, key=lambda s: -(s["ratio_km"] or 0)):
        over = ' class="over"' if s["exceeded"] else ""
        a_rows.append(
            f'<tr data-name="{esc(s["name"])}"{over}>'
            f"<td>{esc(s['name'])}{badge(s)}</td>"
            f"<td>{esc(s['from'])} → {esc(s['to'])}</td>"
            f'<td class="num" data-v="{s["km"]:.2f}">{s["km"]:.2f} km</td>'
            f'<td class="num" data-v="{s["days"]}">{s["days"]}日</td>'
            f"<td>{esc(lifespan_text(s))}</td>"
            f"{usage_cell(s)}</tr>")
    active_tbl = (
        '<table><thead><tr><th class="sort">個体</th><th>期間</th>'
        '<th class="sort" data-num="1">走行距離</th>'
        '<th class="sort" data-num="1">日数</th><th>寿命目安</th>'
        '<th class="sort" data-num="1">消化率</th></tr></thead>'
        f"<tbody>{''.join(a_rows)}</tbody></table>")

    if issues:
        i_rows = "".join(
            f'<tr data-name="{esc(s["name"])}">'
            f"<td>{esc(s['name'])}{badge(s)}</td>"
            f"<td>{esc(reasons(s))}</td>"
            f"<td>{esc(s['from'])} → {esc(s['to'])}</td></tr>"
            for s in issues)
        issue_tbl = ("<table><thead><tr><th>個体</th><th>内容</th><th>期間</th>"
                     f"</tr></thead><tbody>{i_rows}</tbody></table>")
    else:
        issue_tbl = "<p>なし</p>"

    details = []
    for s in statuses:
        details.append(
            f'<details data-name="{esc(s["name"])}" '
            f'data-active="{"1" if s["active"] else "0"}">'
            f"<summary>{esc(s['name'])} {badge(s)} "
            f"<span class='muted'>{s['km']:.0f}km / {s['days']}日 "
            f"({esc(s['from'])} → {esc(s['to'])})</span></summary>"
            f"{history_table(s['history'])}</details>")

    y_rows = "".join(
        f"<tr><td>{esc(y['label'])}</td>"
        f"<td>{esc(y['from'])} → {esc(y['to'])}</td>"
        f'<td class="num">{y["km"]:.2f} km</td>'
        f'<td class="num">{y["days"]}日</td>'
        f"<td>{'集計中' if y['progress'] else ''}</td></tr>"
        for y in yearly)
    yearly_tbl = ("<table><thead><tr><th>年度</th><th>期間</th><th>走行距離</th>"
                  f"<th>日数</th><th></th></tr></thead><tbody>{y_rows}</tbody>"
                  "</table>").format(y_rows=y_rows)

    return (
        "<!DOCTYPE html><html lang='ja'><head><meta charset='utf-8'>"
        f"<title>loadbike メンテ記録 ({today})</title>"
        f"<style>{CSS}</style></head><body>"
        f"<h1>loadbike メンテ記録 ({today})</h1>"
        f'<div class="cards">{cards}</div>'
        '<div class="toolbar">'
        '<input type="text" id="q" placeholder="検索 (個体名)"> '
        '<label><input type="checkbox" id="onlyActive"> 現役のみ</label> '
        '<span class="muted">見出しクリックでソート</span></div>'
        "<h2>現役一覧</h2>" + active_tbl +
        "<h2>要確認</h2>" + issue_tbl +
        "<h2>履歴</h2>" + "".join(details) +
        "<h2>年度集計</h2>" + yearly_tbl +
        f"<script>{JS}</script></body></html>")


def main():
    data = load_yaml()
    acts = data["activities"]
    merge_activities(BASE / acts["source_dir"], BASE / acts["merged"])
    activities = Activities(BASE / acts["merged"])
    today = datetime.date.today()
    rows = build_report(data, activities, today)
    dump_list(rows)
    statuses = [s for s in (component_status(c, activities, today)
                            for c in data["components"]) if s]
    yearly = yearly_summary(activities, today)
    total_km = float(activities.cum.iloc[-1])
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(build_html(statuses, yearly, total_km, today),
                        encoding="utf-8")
    print(f"wrote {OUT_HTML}")


if __name__ == "__main__":
    main()
