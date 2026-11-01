"""loadbike メンテ記録の最小GUI (Streamlit).

起動 (loadbike/ で実行):
    streamlit run app.py

機能:
- レポート表の表示 (output/report.html と同じ内容)
- イベントの追加 (maintenance.yaml に追記。コメント・書式は保持)
"""
import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from maintenance_note import HEADERS, Activities, build_report, load_yaml
from merge_activities import merge_activities

BASE = Path(__file__).resolve().parent
ACTIONS = ["install", "service", "move", "replace", "retire", "memo"]


def save_event(comp_id, event):
    """ruamel.yaml でコメント・書式を保持したままイベントを追記する."""
    from ruamel.yaml import YAML
    yaml = YAML()
    yaml.preserve_quotes = True
    path = BASE / "maintenance.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.load(f)
    for comp in data["components"]:
        if comp["id"] == comp_id:
            comp["events"].append(event)
            comp["events"].sort(key=lambda e: str(e["date"]))
            break
    else:
        raise ValueError(f"unknown component: {comp_id}")
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f)


def main():
    st.title("loadbike メンテ記録")
    data = load_yaml()
    acts = data["activities"]

    if st.button("Activities再マージ + 再計算"):
        merge_activities(BASE / acts["source_dir"], BASE / acts["merged"])
        st.rerun()
    activities = Activities(BASE / acts["merged"])
    rows = build_report(data, activities, datetime.date.today())
    st.dataframe(pd.DataFrame(rows, columns=HEADERS), use_container_width=True)

    st.header("イベント追加")
    comp_map = {f"{c['id']} ({c['name']})": c["id"] for c in data["components"]}
    label = st.selectbox("個体/作業", list(comp_map.keys()))
    comp_id = comp_map[label]
    comp = next(c for c in data["components"] if c["id"] == comp_id)
    action = st.selectbox("Action", ACTIONS)
    date = st.date_input("日付", datetime.date.today())
    detail = st.text_input("detail (内容)")
    memo = st.text_input("memo")
    position = from_ = to = None
    if comp.get("kind") == "consumable" and action in ("install", "retire"):
        position = st.selectbox("position", ["front", "rear"])
    if action == "move":
        from_ = st.selectbox("from", ["front", "rear"])
        to = st.selectbox("to", ["front", "rear"])
    if st.button("追記する"):
        try:
            event = {"date": date.isoformat(), "action": action}
            if detail:
                event["detail"] = detail
            if memo:
                event["memo"] = memo
            if position:
                event["position"] = position
            if action == "move":
                event["from"], event["to"] = from_, to
            save_event(comp_id, event)
            st.success(f"{comp_id} に {date} {action} を追記しました")
            st.rerun()
        except ImportError:
            st.error("ruamel.yaml が未インストールです: pip install ruamel.yaml")
        except Exception as e:  # noqa: BLE001
            st.error(str(e))


if __name__ == "__main__":
    main()
