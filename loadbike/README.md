# loadbike メンテ記録

ロードバイクの部品交換・整備履歴と、Garmin走行距離を紐付けて集計する。

## 日常運用 (3ステップ)

1. ガーミンコネクトから Activities CSV をエクスポートし、`activities/raw/` に置く
   (ファイル名・言語(日/英ヘッダ)・個数は問わない。重複は自動除去)
2. `maintenance.yaml` にイベントを1行追記する (または `streamlit run app.py` のGUIから追加)
3. 下の1ライナーを実行 → コンソール + `output/report.html` が自動生成される

```
python loadbike/main_maintenance_note.py
```
(リポジトリルートから実行。`cd` 不要。ブラウザは自動では開かないので
`loadbike/output/report.html` をダブルクリックで開く)

## maintenance.yaml の書き方

日付順にイベントを追記するだけ。距離は自動計算されるので書かない。

```yaml
- id: tire_agilest_f
  name: Agilest DURO TLR
  kind: consumable
  lifespan_km: 5000      # 寿命目安 (任意)。超えたらレポートで警告
  events:
  - date: '2023-10-07'
    action: install
    position: front
  - date: '2026-02-15'
    action: service        # 外さない整備 (シーラント補充等)
  - date: '2026-05-01'
    action: move           # タイヤの前後ローテーション専用
    from: front
    to: rear
```

### Kind (集計の仕方)

| Kind | 意味 | 例 |
|---|---|---|
| `consumable` | モノ。install→retireの通算距離・日数を出す | タイヤ1本、チェーン |
| `service` | 繰り返し作業。前回からの走行距離を出す | グリスアップ、シーラント補充 |

### Action (日付行の動詞)

| Action | 意味 |
|---|---|
| `install` | 付ける (寿命開始) |
| `service` | 外さない整備 (`detail` に内容) |
| `move` | タイヤの前後ローテーション (`from`/`to`)。距離・時間は個体に引継がれる |
| `replace` | 同位置で新品に交換 (= 同日の retire+install に展開される) |
| `retire` | 外す・捨てる (寿命終了) |
| `memo` | 作業なしの記録 |

タイヤは前後で分けず1個体で管理する。`move` でローテーションを記録すると、
通算 (`Yksion 1 [通算 (front:5350km, rear:3827km)]`) と位置別内訳の両方が出る。

### 寿命目安 (`lifespan_km` / `lifespan_days`、任意)

`consumable` に付けると、通算が目安を超えたらレポートの「要確認」に出て
現役一覧で赤色強調される。現在の設定値: タイヤ 5000km、チェーン 4000km、
ブレーキシュー 3000km。`service` 系には付けない
(前回からの距離表示のみ)。

## レポート (`output/report.html`) の見方

単体HTML (CSS/JS内蔵、オフライン可)。ダブルクリックで開ける。

- サマリーカード: 現役個体数・要確認数・総走行距離・管理個体数
- 現役一覧: 消化率のバー付き (80%で黄、100%超で赤)。見出しクリックでソート
- 要確認: 寿命超過・退役後イベント・TODOメモを集約
- 履歴: 個体ごとの折りたたみ。検索欄・「現役のみ」チェックで絞り込み
- 年度集計: 4/1区切り

## ファイル構成

```
loadbike/
  maintenance.yaml        # 人が編集する正本 ★
  maintenance_note.json   # 旧正本 (移行元バックアップ。参照のみ)
  migrate_json_to_yaml.py # JSON→YAML移行スクリプト (移行済み。普段は不要)
  maintenance_note.py     # 集計ライブラリ
  merge_activities.py     # raw/*.csv → merged.csv
  main_maintenance_note.py# エントリポイント
  app.py                  # 最小GUI (streamlit run app.py)
  activities/
    raw/*.csv             # Garminエクスポート置き場 (git管理)
    merged.csv            # 自動生成 (gitignore)
    title_templete.csv    # 手入力用テンプレの残骸 (マージ対象外)
  output/report.html      # 自動生成 (gitignore)
```

要 `pip install -r requirements-loadbike.txt` (pandas, pyyaml, streamlit, ruamel.yaml)。

## 既知の要確認事項 (YAML内のTODO。レポートの「要確認」にも出る)

- `chain_2` の `2026-04-21` 脱脂は、旧EndDate(2023-03-31)より後の日付。
  チェーン3の脱脂の誤記の可能性。レポート上は `!退役後` と表示される。
- `chain_3` の旧ChangeDate(2025-08-01)はチェーン4への交換と解釈して移行
  (旧JSONは両方存続扱いで二重計上になっていた)。
- ブレーキシュー前後は2018年から退役なし (1294%超過表示)。
  途中の `service` は交換作業の可能性。要YAML修正 (`replace` 化)。
