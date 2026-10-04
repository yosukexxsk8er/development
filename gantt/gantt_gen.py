#!/usr/bin/env python3
"""ガントチャート生成スクリプト（決定論レンダラ）.

使い方:
    python gantt_gen.py examples/fpga.yaml -o output/fpga.html
    python gantt_gen.py input.yaml  # input.html に出力

設計方針:
- AIは YAML（データ）のみ書く。見た目(CSS)はこのスクリプトが凍結保持する。
- 日付 -> %位置、期間表記、色濃淡はすべて自動計算し、手計算ブレを排除する。
- 依存は PyYAML のみ（標準 + yaml）。
"""
from __future__ import annotations

import argparse
import colorsys
import datetime as dt
import html
import sys
from pathlib import Path


# ---------------------------------------------------------------- CSS（凍結）
# 現行 FPGAガントチャート.html から移植。AI・利用者は変更禁止。
# ----------------------------------------------------------------
CSS = """* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', 'Hiragino Kaku Gothic ProN', sans-serif; padding: 12px; background: #f5f6f8; }
h1 { font-size: 14px; margin-bottom: 2px; color: #222; }
.subtitle { font-size: 9px; color: #888; margin-bottom: 6px; }
.gantt-wrap { overflow-x: auto; background: #fff; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,.05); padding: 8px 10px 6px; }
.gw, .gm { display: flex; }
.sp { width: 135px; min-width: 135px; }
.gw-c { flex: 1; display: flex; }
.week { flex: 1; font-size: 7px; color: #999; text-align: center; }
.week:nth-child(even) { color: #ddd; }
.gm-c { flex: 1; position: relative; height: 16px; }
.milestone { position: absolute; top: 2px; transform: translateX(-50%); text-align: center; }
.milestone .diamond { display: block; font-size: 7px; color: #d63031; line-height: 1; }
.milestone .mlbl { display: block; font-size: 6px; color: #999; white-space: nowrap; font-weight: 500; margin-top: -1px; }
.phase-row { display: flex; align-items: stretch; margin-bottom: 1px; }
.phase-label { width: 135px; min-width: 135px; font-size: 9px; font-weight: 600; color: #333; display: flex; align-items: center; padding-right: 6px; }
.phase-label .tag { display: inline-block; font-size: 7px; font-weight: 700; border-radius: 2px; padding: 0 3px; margin-right: 4px; color: #fff; line-height: 14px; }
.phase-track-wrap { flex: 1; min-width: 0; }
.phase-track { position: relative; height: 20px; background: #f0f2f5; border-radius: 3px; overflow: hidden; }
.seg { position: absolute; height: 14px; display: flex; align-items: center; justify-content: center; font-size: 7px; font-weight: 600; color: #fff; cursor: default; }
.seg:hover { opacity: .85; z-index: 2; }
.seg .s-label { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; padding: 0 1px; text-align: center; max-width: 100%; line-height: 1; pointer-events: none; }
.legend { display: flex; flex-wrap: wrap; gap: 4px 12px; margin-top: 4px; padding-top: 4px; border-top: 1px solid #eee; font-size: 9px; color: #555; }
.legend-item { display: flex; align-items: center; gap: 3px; }
.legend-dot { width: 8px; height: 8px; border-radius: 2px; }
.sub-section { margin-top: 8px; }
.sub-section h2 { font-size: 10px; color: #444; margin-bottom: 2px; }
.sub-table { width: 100%; border-collapse: collapse; font-size: 9px; }
.sub-table th { background: #f8f9fb; color: #666; font-weight: 600; padding: 2px 5px; text-align: left; border-bottom: 1px solid #ccc; }
.sub-table td { padding: 1px 5px; border-bottom: 1px solid #eee; color: #444; }
.sub-table td:first-child { font-weight: 500; }
.sub-badge { display: inline-block; font-size: 7px; font-weight: 700; color: #fff; border-radius: 2px; padding: 0 3px; line-height: 13px; }"""

DEFAULT_PALETTE = ["#4a90d9", "#38b25a", "#d9922e", "#d95c5c", "#8a6ec7", "#4faec4"]

LANE_TOP = {0: "3px", 1: "6px"}


def parse_date(v) -> dt.date:
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    s = str(v).strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d", "%m-%d"):
        try:
            d = dt.datetime.strptime(s, fmt).date()
            if fmt in ("%m/%d", "%m-%d"):
                raise ValueError("year needed")
            return d
        except ValueError:
            continue
    raise ValueError(f"日付を解釈できません: {v!r}（YYYY-MM-DDで指定）")


def hex_to_rgb(h: str) -> tuple[float, float, float]:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r = int(h[0:2], 16) / 255.0
    g = int(h[2:4], 16) / 255.0
    b = int(h[4:6], 16) / 255.0
    return r, g, b


def lighten(hex_color: str, step: int) -> str:
    """基色から明度を上げた濃淡色を生成。step=0が基色そのまま。"""
    r, g, b = hex_to_rgb(hex_color)
    h, li, s = colorsys.rgb_to_hls(r, g, b)
    li = min(0.82, li + step * 0.075)
    # 淡くなりすぎたら彩度を少し落として白文字の視認性を保つ
    r2, g2, b2 = colorsys.hls_to_rgb(h, li, max(0.35, s - step * 0.03))
    return "#{:02x}{:02x}{:02x}".format(int(r2 * 255), int(g2 * 255), int(b2 * 255))


def fmt_md(d: dt.date) -> str:
    return f"{d.month}/{d.day}"


def load_yaml(path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAMLが必要です: pip install pyyaml", file=sys.stderr)
        sys.exit(2)
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("YAMLルートはマッピングである必要があります")
    return data


def validate(data: dict) -> None:
    for key in ("title", "start", "phases"):
        if key not in data:
            raise ValueError(f"必須キー '{key}' がありません")
    if not isinstance(data["phases"], list) or not data["phases"]:
        raise ValueError("'phases' は1件以上のリストである必要があります")
    for i, ph in enumerate(data["phases"], 1):
        if "name" not in ph:
            raise ValueError(f"phases[{i}] に 'name' がありません")
        if "tasks" not in ph or not ph["tasks"]:
            raise ValueError(f"phases[{i}] ({ph.get('name')}) に 'tasks' がありません")
        for j, t in enumerate(ph["tasks"], 1):
            for k in ("name", "start", "end"):
                if k not in t:
                    raise ValueError(f"phases[{i}].tasks[{j}] に '{k}' がありません")


def auto_lane(tasks: list[dict]) -> None:
    """lane: auto のタスクに0/1を自動割当。明示指定は尊重。"""
    placed: list[list[tuple[dt.date, dt.date]]] = [[], []]
    # 開始日順に処理（明示laneも占有として登録）
    order = sorted(range(len(tasks)), key=lambda k: (tasks[k]["_s"], tasks[k]["_e"]))
    for k in order:
        t = tasks[k]
        lane = t.get("lane", "auto")
        if lane in (0, 1, "0", "1"):
            li = int(lane)
            t["_lane"] = li
            placed[li].append((t["_s"], t["_e"]))
            continue
        # lane0 と重ならなければ0、重なれば1
        s, e = t["_s"], t["_e"]
        overlap0 = any(not (e < ps or s > pe) for ps, pe in placed[0])
        li = 1 if overlap0 else 0
        t["_lane"] = li
        placed[li].append((s, e))


def render(data: dict) -> str:
    title = str(data["title"])
    subtitle = str(data.get("subtitle", "▼ マウスオーバーでサブタスク詳細"))
    start = parse_date(data["start"])
    weeks = int(data.get("weeks", 22))
    total_days = weeks * 7
    end_exclusive = start + dt.timedelta(days=total_days)

    # 週ラベル
    week_labels = []
    for i in range(weeks):
        week_labels.append(fmt_md(start + dt.timedelta(days=7 * i)))

    # フェーズ準備
    phases = []
    for idx, ph in enumerate(data["phases"]):
        base = str(ph.get("color") or DEFAULT_PALETTE[idx % len(DEFAULT_PALETTE)])
        tasks = []
        for t in ph["tasks"]:
            s = parse_date(t["start"])
            e = parse_date(t["end"])
            if e < s:
                raise ValueError(f"タスク '{t['name']}' の end が start より前です")
            tasks.append({**t, "_s": s, "_e": e})
        auto_lane(tasks)
        # 色割当（開始日順に濃→淡）
        tasks_sorted = sorted(tasks, key=lambda x: (x["_s"], x["_e"]))
        for step, t in enumerate(tasks_sorted):
            t["_color"] = lighten(base, step)
        phases.append({"id": idx + 1, "name": str(ph["name"]), "base": base, "tasks": tasks})

    # マイルストーン
    milestones = []
    for m in data.get("milestones", []):
        at = parse_date(m["at"])
        pct = (at - start).days / total_days * 100.0
        pct = max(0.0, min(100.0, pct))
        milestones.append({"label": str(m["label"]), "pct": pct})

    esc = html.escape
    out: list[str] = []
    out.append("<!DOCTYPE html>")
    out.append('<html lang="ja">')
    out.append("<head>")
    out.append('<meta charset="UTF-8">')
    out.append(f"<title>{esc(title)}</title>")
    out.append("<style>")
    out.append(CSS)
    out.append("</style>")
    out.append("</head>")
    out.append("<body>")
    out.append("")
    out.append(f"<h1>{esc(title)}</h1>")
    out.append(f'<p class="subtitle">{esc(subtitle)}</p>')
    out.append("")
    out.append('<div class="gantt-wrap">')
    out.append("")
    # 週ヘッダ
    out.append("  <!-- Week header -->")
    out.append('  <div class="gw">')
    out.append('    <div class="sp"></div>')
    out.append('    <div class="gw-c">')
    out.append("      " + "".join(f'<div class="week">{w}</div>' for w in week_labels))
    out.append("    </div>")
    out.append("  </div>")
    out.append("")
    # マイルストーン
    out.append("  <!-- Milestones -->")
    out.append('  <div class="gm">')
    out.append('    <div class="sp"></div>')
    out.append('    <div class="gm-c">')
    for m in milestones:
        out.append(f'      <div class="milestone" style="left:{m["pct"]:.2f}%"><span class="diamond">&#9670;</span><span class="mlbl">{esc(m["label"])}</span></div>')
    out.append("    </div>")
    out.append("  </div>")
    out.append("")
    # フェーズ行
    for ph in phases:
        out.append(f"  <!-- Phase {ph['id']} -->")
        out.append('  <div class="phase-row">')
        out.append(f'    <div class="phase-label"><span class="tag" style="background:{ph["base"]}">{ph["id"]}</span>{esc(ph["name"])}</div>')
        out.append('    <div class="phase-track-wrap">')
        out.append('      <div class="phase-track">')
        for t in sorted(ph["tasks"], key=lambda x: (x["_s"], x["_e"])):
            left = (t["_s"] - start).days / total_days * 100.0
            width = ((t["_e"] - t["_s"]).days + 1) / total_days * 100.0
            left = max(0.0, left)
            if left + width > 100.0:
                width = max(0.5, 100.0 - left)
            period = f"{fmt_md(t['_s'])}-{fmt_md(t['_e'])}"
            detail = str(t.get("detail", t["name"]))
            short = str(t.get("short", t["name"]))
            top = LANE_TOP.get(t["_lane"], "3px")
            tip = esc(f"{period} {detail}", quote=True)
            out.append(f'        <div class="seg" style="left:{left:.2f}%;width:{width:.2f}%;top:{top};background:{t["_color"]}" title="{tip}"><span class="s-label">{esc(short)}</span></div>')
        out.append("      </div>")
        out.append("    </div>")
        out.append("  </div>")
        out.append("")
    # 凡例
    out.append("  <!-- Legend -->")
    out.append('  <div class="legend">')
    short_names = {"企画・要件定義": "企画", "RTL設計・実装": "RTL", "論理合成・実装": "合成",
                   "検証": "検証", "実機評価": "実機", "ドキュメント・納品": "Doc"}
    for ph in phases:
        lbl = short_names.get(ph["name"], ph["name"])
        out.append(f'    <div class="legend-item"><div class="legend-dot" style="background:{ph["base"]}"></div>Phase{ph["id"]} {esc(lbl)}</div>')
    out.append('    <div class="legend-item"><span style="color:#d63031;font-size:12px">&#9670;</span> マイルストーン</div>')
    out.append("  </div>")
    out.append("")
    out.append("</div>")
    out.append("")
    # 下部詳細表
    out.append("<!-- Sub-task assignment table -->")
    out.append('<div class="sub-section">')
    out.append("<h2>サブタスク割り当て一覧</h2>")
    out.append('<table class="sub-table">')
    out.append("  <thead>")
    out.append('    <tr><th style="width:20px">#</th><th style="width:140px">サブタスク</th><th style="width:80px">期間</th><th style="width:60px">工数</th><th>担当</th><th>成果物</th></tr>')
    out.append("  </thead>")
    out.append("  <tbody>")
    for ph in phases:
        for t in sorted(ph["tasks"], key=lambda x: (x["_s"], x["_e"])):
            period = f"{fmt_md(t['_s'])}-{fmt_md(t['_e'])}"
            effort = esc(str(t.get("effort", "—")))
            owner = esc(str(t.get("owner", "—")))
            deli = esc(str(t.get("deliverable", "—")))
            out.append(f'    <tr><td><span class="sub-badge" style="background:{t["_color"]}">{ph["id"]}</span></td><td>{esc(str(t["name"]))}</td><td>{period}</td><td>{effort}</td><td>{owner}</td><td>{deli}</td></tr>')
    out.append("  </tbody>")
    out.append("</table>")
    out.append("</div>")
    out.append("")
    out.append(f"<!-- generated from YAML: start={start} weeks={weeks} total_days={total_days} -->")
    out.append("")
    out.append("</body>")
    out.append("</html>")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="ガントチャートHTML生成（決定論レンダラ）")
    ap.add_argument("input", help="入力YAMLパス")
    ap.add_argument("-o", "--output", default=None, help="出力HTMLパス（既定: 入力と同名.html）")
    args = ap.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"ERROR: 入力が見つかりません: {in_path}", file=sys.stderr)
        return 1
    out_path = Path(args.output) if args.output else in_path.with_suffix(".html")

    try:
        data = load_yaml(in_path)
        validate(data)
        html_text = render(data)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_text, encoding="utf-8")
    n_tasks = sum(len(ph.get("tasks", [])) for ph in data["phases"])
    n_ms = len(data.get("milestones", []))
    print(f"OK: {out_path} （フェーズ{len(data['phases'])} / タスク{n_tasks} / マイルストーン{n_ms}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
