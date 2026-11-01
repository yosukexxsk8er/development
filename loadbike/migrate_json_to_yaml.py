"""maintenance_note.json -> maintenance.yaml への一回きりの移行スクリプト.

変換ルール:
- 「年間走行距離」ダミーは廃止 (年次集計はレポート側で算出)。
- タイヤは個体管理に統合。Yksion 1(前)->Yksion 1(後) のローテーションは
  1個体(tire_yksion_1)の move イベントになる。
- チェーン2(脱脂)はチェーン2個体への service イベントに統合。
  2026-04-21 の脱脂は旧EndDateより後のため TODO メモ付きで保持。
- チェーン3 の ChangeDate(2025-08-01)はチェーン4への交換と解釈し、
  チェーン3 の retire / チェーン4 の install とする (旧JSONは両方を
  存続扱いにしており二重計上になっていた)。
- その他は service 個体/消耗個体の install + service イベントに展開。
- 日付は YYYY-MM-DD に正規化。

使い方: python migrate_json_to_yaml.py
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
JSON_FILE = BASE / "maintenance_note.json"
YAML_FILE = BASE / "maintenance.yaml"


def norm(date_str):
    y, m, d = date_str.split("/")
    return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"


def ev(date_str, action, **kw):
    e = {"date": norm(date_str), "action": action}
    e.update(kw)
    return e


def main():
    with open(JSON_FILE, encoding="utf-8_sig") as f:
        data = json.load(f)
    parts = {p["Name"]: p for p in data["Parts"]}

    def get(name):
        return parts[name]

    components = []

    # ---- タイヤ(個体管理)。前後ローテーションは move で引継ぎ ----
    def tire(comp_id, name, install_date, install_pos, retire_date=None,
             retire_pos=None, retire_memo=None, services=None, spec=None,
             memo=None, move=None):
        events = [ev(install_date, "install", position=install_pos)]
        if move:
            events.append(ev(move["date"], "move", **{k: v for k, v in move.items() if k != "date"}))
        for s in services or []:
            events.append(ev(s, "service"))
        if retire_date:
            kw = {}
            if retire_pos:
                kw["position"] = retire_pos
            if retire_memo:
                kw["memo"] = retire_memo
            events.append(ev(retire_date, "retire", **kw))
        comp = {"id": comp_id, "name": name, "kind": "consumable",
                "events": events}
        if spec:
            comp["spec"] = spec
        if memo:
            comp["memo"] = memo
        components.append(comp)

    yksion1_f = get("Yksion 1(前)")
    yksion1_r = get("Yksion 1(後)")
    tire("tire_yksion_1", "Yksion 1",
         yksion1_f["StartDate"], "front",
         retire_date=yksion1_r["EndDate"], retire_pos="rear",
         retire_memo=yksion1_r.get("Memo"),
         move={"date": yksion1_r["StartDate"], "from": "front", "to": "rear",
               "memo": "前タイヤを後ろへローテーション"},
         spec="Yksion")

    front_tires = [
        ("tire_yksion_3", "Yksion 3(前)"),
        ("tire_yksion_4", "Yksion 4(前)"),
        ("tire_irc_1", "IRC Tire 1(前)"),
        ("tire_vittoria_corsa_f", "Vittoria Corsa(前)"),
        ("tire_agilest_f", "Agilest DURO TLR(前)"),
    ]
    for comp_id, name in front_tires:
        p = get(name)
        tire(comp_id, name.replace("(前)", ""), p["StartDate"], "front",
             retire_date=p["EndDate"], retire_pos="front",
             retire_memo=p.get("Memo") or None,
             services=p.get("ChangeDate") or [],
             spec=p.get("Model") or None,
             memo=p.get("Memo") or None if p.get("EndDate") is None else None)

    # Vittoria ルビーノ(後)は同名2レコードあるので直接扱う
    p = get("Yksion 2(後)")
    tire("tire_yksion_2", "Yksion 2", p["StartDate"], "rear",
         retire_date=p["EndDate"], retire_pos="rear", spec="Yksion")
    p = get("Yksion 5(後)")
    tire("tire_yksion_5", "Yksion 5", p["StartDate"], "rear",
         retire_date=p["EndDate"], retire_pos="rear")
    p = get("Yksion 6(後)")
    tire("tire_yksion_6", "Yksion 6", p["StartDate"], "rear",
         retire_date=p["EndDate"], retire_pos="rear", memo=p.get("Memo"))
    rubinos = [p for p in data["Parts"] if p["Name"] == "Vittoria ルビーノ(後)"]
    rubinos.sort(key=lambda p: p["StartDate"])
    for i, p in enumerate(rubinos, start=1):
        tire(f"tire_vittoria_rubino_{i}", "Vittoria ルビーノ", p["StartDate"],
             "rear", retire_date=p["EndDate"], retire_pos="rear",
             retire_memo=p.get("Memo"))
    p = get("Agilest DURO TLR(後)")
    tire("tire_agilest_r", "Agilest DURO TLR", p["StartDate"], "rear",
         retire_date=p["EndDate"], retire_pos="rear",
         services=p.get("ChangeDate") or [], memo=p.get("Memo"))

    # ---- チェーン(個体管理)。脱脂は同一個体の service ----
    def chain(comp_id, name, install, retire=None, services=None, degrease=None,
              memo=None):
        events = [ev(install, "install")]
        for s in services or []:
            events.append(ev(s, "service"))
        for d in degrease or []:
            if isinstance(d, dict):
                events.append(ev(d["date"], "service", **{k: v for k, v in d.items() if k != "date"}))
            else:
                events.append(ev(d, "service", detail="脱脂"))
        if retire:
            events.append(ev(retire, "retire"))
        comp = {"id": comp_id, "name": name, "kind": "consumable",
                "events": events}
        if memo:
            comp["memo"] = memo
        components.append(comp)

    c1 = get("チェーン1")
    chain("chain_1", "チェーン1", c1["StartDate"], retire=c1["EndDate"])
    c2 = get("チェーン2")
    c2d = get("チェーン2(脱脂)")
    degrease = []
    for d in c2d.get("ChangeDate") or []:
        if d == "2026/04/21":
            degrease.append({"date": d, "detail": "脱脂",
                             "memo": "TODO: 旧データではチェーン2のChangeDateだが"
                                     "旧EndDate(2023-03-31)より後。チェーン3の脱脂の"
                                     "誤記の可能性。要確認"})
        else:
            degrease.append({"date": d, "detail": "脱脂"})
    chain("chain_2", "チェーン2", c2["StartDate"], retire=c2["EndDate"],
          degrease=degrease)
    c3 = get("チェーン3")
    # 旧ChangeDate(2025-08-01)=チェーン4への交換と解釈 (二重計上の修正)
    chain("chain_3", "チェーン3", c3["StartDate"], retire="2025/08/01")
    c4 = get("チェーン4")
    chain("chain_4", "チェーン4", c4["StartDate"], retire=c4["EndDate"])

    # ---- 整備・消耗品 (service / 小物consumable) ----
    service_defs = [
        ("hub_grease", "ハブ グリスアップ", "service"),
        ("sealant_front_replace", "シーラント交換(前)", "service"),
        ("sealant_rear_replace", "シーラント交換(後)", "service"),
        ("sealant_front_topup", "シーラント補充(前)", "service"),
        ("sealant_rear_topup", "シーラント補充(後)", "service"),
        ("shifter_wire_front", "シフトワイヤー(前) 交換", "service"),
        ("shifter_wire_rear", "シフトワイヤー(後) 交換", "service"),
        ("shifter_housing", "シフトアウターケーブル交換", "service"),
        ("brake_wire_front", "ブレーキワイヤー前 交換", "service"),
        ("brake_wire_rear", "ブレーキワイヤー後 交換", "service"),
        ("brake_housing", "ブレーキアウター", "service"),
        ("brake_shoe_front", "ブレーキシュー（前）", "consumable"),
        ("brake_shoe_rear", "ブレーキシュー（後）", "consumable"),
        ("crank", "クランクシャフト", "service"),
        ("rear_light", "リアライト", "service"),
        ("garmin_sensor", "ガーミンセンサー", "service"),
        ("tile", "タイル", "service"),
    ]
    for comp_id, name, kind in service_defs:
        p = get(name)
        events = [ev(p["StartDate"], "install")]
        for d in p.get("ChangeDate") or []:
            events.append(ev(d, "service"))
        if p.get("EndDate"):
            events.append(ev(p["EndDate"], "retire"))
        comp = {"id": comp_id, "name": name, "kind": kind, "events": events}
        model = p.get("Model")
        if model and model != "-":
            comp["spec"] = model
        typ = p.get("Type")
        if typ and typ != "交換":
            comp["detail"] = typ
        pos = p.get("Positon")  # 旧JSONのtypoキー
        if pos:
            comp["position"] = pos
        if p.get("Memo"):
            comp["memo"] = p["Memo"]
        components.append(comp)

    header = """\
# loadbike メンテナンス記録 (人が編集する正本)
#
# 運用: 日付順にイベントを追記するだけ。距離は activities/raw/*.csv から自動計算。
#
# Kind (集計の仕方):
#   consumable ... モノ。installからretireまで距離が貯まる (タイヤ1本、チェーン等)
#   service    ... 作業。service日が記録点。前回からの走行距離を出す (グリスアップ等)
# Action (日付行の動詞):
#   install ... 付ける (寿命開始)
#   service ... 外さない整備 (脱脂・補充等。detailに内容)
#   move    ... 位置移動。タイヤの前後ローテーション専用 (from/to)。距離・時間は個体に引継がれる
#   replace ... 同位置で新品に交換 (= retire+installの省略形)
#   retire  ... 外す・捨てる (寿命終了)
#   memo    ... 作業なしの記録
# 日付は YYYY-MM-DD で統一。
"""
    body = {"bike": {"name": "loadbike", "start_date": "2018-03-24"},
            "activities": {"source_dir": "activities/raw",
                           "merged": "activities/merged.csv"},
            "components": components}
    import yaml
    text = header + yaml.safe_dump(body, allow_unicode=True,
                                   sort_keys=False, default_flow_style=False)
    # retire同日 install/move の可読性のため特に整形しない (safe_dumpのまま)
    with open(YAML_FILE, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"wrote {YAML_FILE} ({len(components)} components)")
    # 簡易検証: 同名タイヤの二重管理が無いこと
    ids = [c["id"] for c in components]
    assert len(ids) == len(set(ids)), "duplicate id!"
    # ローテーション整合: moveのfrom/to位置チェック
    for c in components:
        for e in c["events"]:
            if e["action"] == "move":
                assert "from" in e and "to" in e, c["id"]


if __name__ == "__main__":
    main()
