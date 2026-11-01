"""maintenance.yaml を読み、activities/merged.csv から区間走行距離を集計するライブラリ.

データモデル (maintenance.yaml のヘッダコメント参照):
- Kind: consumable (モノ・個体管理) / service (繰り返し作業)
- Action: install / service / move (タイヤ前後ローテーション) /
           replace (=同日 retire+install に展開) / retire / memo

タイヤ個体は install〜retire の通算距離・日数 (ローテーション引継ぎ) と
位置別 (front/rear) の内訳の両方を出す。
"""
import datetime
from pathlib import Path

import pandas as pd
import yaml

BASE = Path(__file__).resolve().parent
YAML_FILE = BASE / "maintenance.yaml"
MERGED_CSV = BASE / "activities" / "merged.csv"

COL_DATE = "日付"
COL_DIST = "距離"

HEADERS = ["個体/作業", "From", "To", "走行距離", "日数", "状態", "メモ"]


def load_yaml(path=YAML_FILE):
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    for comp in data["components"]:
        events = []
        for e in comp.get("events", []):
            e = dict(e)
            d = e["date"]
            if isinstance(d, (datetime.date, datetime.datetime)):
                d = d.isoformat()
            e["date"] = datetime.date.fromisoformat(str(d))
            # replace は同日の retire + install に展開
            if e["action"] == "replace":
                events.append({**{k: v for k, v in e.items() if k != "action"},
                               "action": "retire"})
                events.append({**{k: v for k, v in e.items() if k != "action"},
                               "action": "install"})
            else:
                events.append(e)
        # 同日複数イベントは記載順を保持 (stable sort)。
        # replace展開 (retire→install) が正順で残るための措置。
        # install→retire同日 (即日パンク等) も記載どおり退役扱いになる。
        events.sort(key=lambda e: e["date"])
        comp["events"] = events
    return data


class Activities:
    """merged.csv を日付昇順 + 累積距離で保持し、区間合計を高速に返す."""

    def __init__(self, csv_file=MERGED_CSV):
        df = pd.read_csv(csv_file, encoding="utf-8-sig")
        df[COL_DATE] = pd.to_datetime(df[COL_DATE], format="mixed",
                                      errors="coerce")
        df[COL_DIST] = pd.to_numeric(df[COL_DIST], errors="coerce")
        df = df.dropna(subset=[COL_DATE, COL_DIST]).sort_values(COL_DATE)
        self.dates = pd.to_datetime(df[COL_DATE]).reset_index(drop=True)
        self.cum = pd.to_numeric(df[COL_DIST]).cumsum().reset_index(drop=True)

    def distance(self, start_date, end_date):
        """start〜end (両端の日を含める) の合計距離.

        旧実装 (日付date同士の比較) と同じく、終了日の深夜の走行まで含める。
        """
        start = pd.to_datetime(start_date).normalize()
        end_next = pd.to_datetime(end_date).normalize() + pd.Timedelta(days=1)
        lo = self.dates.searchsorted(start, side="left")
        hi = self.dates.searchsorted(end_next, side="left") - 1
        if lo > hi or lo >= len(self.cum):
            return 0.0
        hi = min(hi, len(self.cum) - 1)
        return float(self.cum.iloc[hi] - (self.cum.iloc[lo - 1] if lo > 0 else 0.0))


def _fmt(d):
    return d.strftime("%Y/%m/%d")


def expand_component(comp, activities, today):
    """1個体のイベント列を区間行に展開する.

    戻り値: rows (HEADERS順のリスト), lifetime (通算dict or None)
    """
    events = comp["events"]
    name = comp["name"]
    rows = []
    cur_pos = None
    retired = False
    pos_km = {}
    total_km = 0.0
    lifetime_from = events[0]["date"] if events else today

    def push(frm, to, label, memo="", state="", pos=None):
        nonlocal total_km
        km = activities.distance(frm, to)
        days = (to - frm).days
        total_km += km
        if pos:
            pos_km[pos] = pos_km.get(pos, 0.0) + km
        rows.append([name, _fmt(frm), _fmt(to), f"{km:.2f}[km]",
                     str(days), state, memo])

    prev = None
    for e in events:
        if prev is not None:
            seg_pos = cur_pos
            memo = e.get("memo", "")
            state = ""
            # 退役後の区間に実走行があれば異常として可視化
            # (同日の retire→install = replace交換は異常ではない)
            if retired and e["date"] > prev["date"]:
                state = "!退役後"  # 旧JSONのチェーン2脱脂等
            push(prev["date"], e["date"], e["action"], memo=memo,
                 state=state, pos=seg_pos)
        if e["action"] == "install":
            cur_pos = e.get("position", cur_pos)
            retired = False
        elif e["action"] == "move":
            cur_pos = e.get("to", cur_pos)
        elif e["action"] == "retire":
            retired = True
        prev = e
    if prev is not None and not retired:
        push(prev["date"], today, "現役", state="*", pos=cur_pos)

    lifetime = None
    if comp.get("kind") == "consumable" and events:
        end = events[-1]["date"] if retired else today
        days = (end - lifetime_from).days
        pos_info = (" (" + ", ".join(f"{p}:{v:.0f}km"
                                     for p, v in pos_km.items()) + ")"
                    if pos_km else "")
        lifetime = {"from": _fmt(lifetime_from), "to": _fmt(end),
                    "km": total_km, "days": days, "pos_info": pos_info,
                    "active": not retired}
    return rows, lifetime


def yearly_summary(activities, today):
    """年度集計 (4/1区切り。旧「年間走行距離」ダミーの代替).

    戻り値: dict(label/from/to/km/days/progress)のリスト.
    """
    rows = []
    start_year = activities.dates.min().year
    for y in range(start_year, today.year + 2):
        f0, f1 = datetime.date(y, 4, 1), datetime.date(y + 1, 4, 1)
        if f0 > today:
            break
        to = min(f1, today)
        rows.append({"label": f"年間走行距離({y}年度)",
                     "from": _fmt(f0), "to": _fmt(to),
                     "km": activities.distance(f0, to),
                     "days": (to - f0).days,
                     "progress": to < f1})
    return rows


def component_status(comp, activities, today):
    """現役把握用の構造化サマリ (HTMLレポート用).

    戻り値: dict(id/name/kind/active/from/to/km/days/
                 lifespan_km/lifespan_days/ratio_km/ratio_days/
                 exceeded/flags/history) or None (イベントなし).
    - consumable: 通算 (初回install→今日/退役日) を寿命と比較
    - service: 最終イベント→今日 (前回からの距離) を表示。寿命なし
    - flags: "!退役後" (退役後のイベント) / "TODO" (未確定メモ) の有無
    """
    events = comp.get("events", [])
    if not events:
        return None
    rows, lifetime = expand_component(comp, activities, today)
    # 現役 = 最終がretireでなく、退役後イベントもないこと
    # (chain_2の2026-04-21のような異常データは要確認行きにする)
    active = (events[-1]["action"] != "retire"
              and not any(r[5] == "!退役後" for r in rows))
    if comp.get("kind") == "consumable":
        frm, to = lifetime["from"], lifetime["to"]
        km, days = lifetime["km"], lifetime["days"]
    else:
        frm_d = events[-1]["date"]
        km = activities.distance(frm_d, today)
        days = (today - frm_d).days
        frm, to = _fmt(frm_d), _fmt(today)
    lifespan_km = comp.get("lifespan_km")
    lifespan_days = comp.get("lifespan_days")
    ratio_km = km / lifespan_km if lifespan_km else None
    ratio_days = days / lifespan_days if lifespan_days else None
    exceeded = bool(active and (
        (ratio_km is not None and ratio_km >= 1)
        or (ratio_days is not None and ratio_days >= 1)))
    flags = []
    if any(r[5] == "!退役後" for r in rows):
        flags.append("!退役後")
    if any("TODO" in str(e.get("memo", "") or "")
           or "TODO" in str(e.get("detail", "") or "") for e in events):
        flags.append("TODO")
    return {"id": comp["id"], "name": comp["name"],
            "kind": comp.get("kind", ""), "active": active,
            "from": frm, "to": to, "km": km, "days": days,
            "lifespan_km": lifespan_km, "lifespan_days": lifespan_days,
            "ratio_km": ratio_km, "ratio_days": ratio_days,
            "exceeded": exceeded, "flags": flags, "history": rows}


def build_report(data, activities, today=None):
    """全個体の区間行 + 通算行 + 年度集計行を返す."""
    today = today or datetime.date.today()
    all_rows = []
    for comp in data["components"]:
        if not comp.get("events"):
            continue
        rows, lifetime = expand_component(comp, activities, today)
        all_rows.extend(rows)
        if lifetime:
            state = "*" if lifetime["active"] else "通算"
            all_rows.append([comp["name"] + " [通算" + lifetime["pos_info"] + "]",
                             lifetime["from"], lifetime["to"],
                             f"{lifetime['km']:.2f}[km]",
                             str(lifetime["days"]), state,
                             comp.get("memo", "")])
    # 年度集計 (4/1区切り。旧「年間走行距離」ダミーの代替)
    for y in yearly_summary(activities, today):
        state = "*" if y["progress"] else ""
        all_rows.append([y["label"], y["from"], y["to"],
                         f"{y['km']:.2f}[km]", str(y["days"]), state, ""])
    return all_rows


def dump_list(rows):
    for r in rows:
        print("\t".join(r))
    return rows
