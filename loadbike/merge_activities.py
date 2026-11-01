"""Garmin Activities CSV のマージ処理.

使い方:
    python merge_activities.py  # activities/raw/*.csv -> activities/merged.csv

仕様:
- 入力は activities/raw/ に置くだけ (ファイル名・個数は問わない)。
- 列は名前で特定 (アクティビティタイプ,日付,お気に入り,タイトル,距離) の5列のみ使用。
  Book1.csv のような5列版も、フル版も混在可。ヘッダのみのファイルは無視。
- 日付は YYYY-MM-DD HH:MM:SS / YYYY/M/D H:MM 等を混在許容で解釈。
- 距離のカンマ・'--' を吸収。距離なし行は除外。
- 重複除去: 完全重複 + (タイトル・距離が同じで2分以内は重複とみなす)。
"""
import sys
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
RAW_DIR = BASE / "activities" / "raw"
MERGED = BASE / "activities" / "merged.csv"

COL_TYPE = "アクティビティタイプ"
COL_DATE = "日付"
COL_FAV = "お気に入り"
COL_TITLE = "タイトル"
COL_DIST = "距離"
KEEP = [COL_TYPE, COL_DATE, COL_FAV, COL_TITLE, COL_DIST]
# Garminエクスポートは時期により英語ヘッダが混ざる (日付・タイトルは日本語のまま)
ALIASES = {"Activity Type": COL_TYPE, "Favorite": COL_FAV, "Distance": COL_DIST}


def _read_one(path):
    for enc in ("utf-8-sig", "cp932"):
        try:
            df = pd.read_csv(path, encoding=enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        print(f"skip (decode error): {path.name}", file=sys.stderr)
        return None
    df = df.rename(columns=ALIASES)
    missing = [c for c in KEEP if c not in df.columns]
    if missing:
        print(f"skip (columns missing {missing}): {path.name}", file=sys.stderr)
        return None
    df = df.loc[:, KEEP].copy()
    df["__src"] = path.name
    return df


def _parse_distance(s):
    if isinstance(s, (int, float)):
        return float(s)
    s = str(s).replace(",", "").strip()
    if s in ("", "--", "nan", "None"):
        return float("nan")
    try:
        return float(s)
    except ValueError:
        return float("nan")


def merge_activities(source_dir=RAW_DIR, save_name=MERGED):
    source_dir = Path(source_dir)
    files = sorted(source_dir.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"no csv in {source_dir}")
    dfs = []
    for path in files:
        print(f"Read {path.name} ...")
        df = _read_one(path)
        if df is not None and len(df):
            dfs.append(df)
    df = pd.concat(dfs, ignore_index=True)
    df[COL_DATE] = pd.to_datetime(df[COL_DATE], format="mixed", errors="coerce")
    df[COL_DIST] = df[COL_DIST].map(_parse_distance)
    df = df.dropna(subset=[COL_DATE, COL_DIST]).reset_index(drop=True)
    df = df.drop_duplicates(subset=[COL_DATE, COL_TITLE, COL_DIST])

    # タイトル・距離が同じで2分以内は重複とみなす
    df = df.sort_values(by=[COL_TITLE, COL_DIST, COL_DATE]).reset_index(drop=True)
    keep = [True] * len(df)
    for i in range(1, len(df)):
        prev, curr = df.iloc[i - 1], df.iloc[i]
        if curr[COL_TITLE] == prev[COL_TITLE] and curr[COL_DIST] == prev[COL_DIST]:
            if abs((curr[COL_DATE] - prev[COL_DATE]).total_seconds()) <= 120:
                keep[i] = False
    df = df[keep]

    df = df.sort_values(by=COL_DATE, ascending=False).reset_index(drop=True)
    df[COL_DATE] = df[COL_DATE].dt.strftime("%Y-%m-%d %H:%M:%S")
    if save_name:
        save_name = Path(save_name)
        save_name.parent.mkdir(parents=True, exist_ok=True)
        df.drop(columns=["__src"]).to_csv(save_name, index=False)
        print(f"saved {save_name} ({len(df)} rows)")
    return df


def main():
    merge_activities()


if __name__ == "__main__":
    main()
