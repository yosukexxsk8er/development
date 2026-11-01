# development

個人用のツール・試作・メモをまとめたリポジトリ。Python 3.10 を前提とし、特に断りがなければリポジトリルートから実行する。

- 掲載対象は git 追跡済みのプロジェクト／スクリプトのみ（未追跡・`.gitignore` 対象は除外）
- 生成物（HTML / CSV / JSON / xlsx など）の多くは `.gitignore` 対象
- 詳細な使い方は各プロジェクトの README を参照

## セットアップ

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

プロジェクトごとに追加の依存が必要。各表のコマンド前に必要な `pip install` を示す。

## プロジェクト一覧

| プロジェクト | 内容 | 実行コマンド |
|---|---|---|
| `loadbike/` | ロードバイクの整備履歴と Garmin 走行距離を集計し、HTML レポートを生成 | `pip install -r loadbike/requirements-loadbike.txt`<br>`python loadbike/main_maintenance_note.py` |
| `weather/` | tenki.jp の天気予報を取得する Tkinter GUI | `pip install -r weather/requirements.txt`<br>`python -m weather.main` |
| `gantt/` | YAML から再現性のあるコンパクトなガントチャート HTML を生成 | `pip install pyyaml`<br>`python gantt/gantt_gen.py gantt/examples/fpga.yaml -o gantt/output/fpga.html` |
| `remove_mosaic/` | DeepMosaics で画像のモザイクを除去 | `remove_mosaic\.venv\Scripts\python.exe remove_mosaic\remove_mosaic.py <画像\|フォルダ>` |
| `excel_arrange_table/` | Excel の表・セル・画像配置を操作する試作集 | `cd excel_arrange_table`<br>`python セルを正方形にする.py` |
| `gen_json_from_csv/` | CSV から指定 ID の設定を JSON 化し、JSON を結合 | `python gen_json_from_csv/gen_json_from_a_selected_id_in_csv.py --input_csv <csv> --output_dir <dir> --target_id <id> --type_name setting` |
| `Clipborad_tools/` | JSON 定義の定型文を GUI ボタンでクリップボードへ | `pip install PySimpleGUI`<br>`python Clipborad_tools/main.py` |
| `conbination/` | Excel の条件表から組み合わせ数と TAT を計算 | `pip install openpyxl pandas numpy`<br>`cd conbination`<br>`python conbination.py` |
| `copy_folder_exclude_someone/` | 除外名を指定してフォルダをコピー | `python copy_folder_exclude_someone/copy_folder_exclude_someone.py` |
| `find/` | 正規表現でファイル名を再帰検索 | `python find/find.py <dir> <pattern> [-o out.txt]` |
| `mapping_activities_loadbike/` | Garmin の GPX / FIT から走行軌跡マップ HTML を生成 | `pip install gpxpy folium fit2gpx tqdm`<br>`cd mapping_activities_loadbike`<br>`python main_map_gpx.py` |
| `outlook/` | テンプレートから Outlook メール下書きを作成 | `pip install pywin32`<br>`cd outlook`<br>`python main.py [Start\|End]` |
| `chrome_addin/list_tabs_in_history/` | 最近のタブ履歴を一覧・切替する Chrome 拡張 | `chrome://extensions` で「パッケージ化されていない拡張機能を読み込む」→ このフォルダを指定 |
| `Tkinter/` | Tkinter / CustomTkinter の GUI 部品・レイアウト試作 | `python Tkinter/Tkinter_練習.py` |
| `Verilog/` | Verilog モジュールの階層・ポートを解析する試作 | `python Verilog/parser_study.py <verilog_dir>` |
| `numpy_trical/` | numpy の多項式フィッティング・線形補間の試作 | `python numpy_trical/多項式.py` |
| `bash_env_setting/` | bash alias とキーボードマップ設定（Linux / WSL） | `source bash_env_setting/alias_commands.sh` |

補足:

- `remove_mosaic/` は初回のみモデルの配置が必要。手順は [remove_mosaic/README.md](remove_mosaic/README.md) を参照
- `copy_folder_exclude_someone/` はコピー元・先・除外名を `main()` 内で指定する
- `mapping_activities_loadbike/` は `main()` 内の `folder_path` を自分の Garmin エクスポート先に変更する
- `outlook/` は `config.json` の宛先・テンプレートを編集してから実行する
- `conbination/` は `conditions.xlsx` を同じディレクトリに置いて実行する

## 複数スクリプトを持つプロジェクト

### `excel_arrange_table/`

`cd excel_arrange_table` してから実行する。

| スクリプト | 内容 | 実行コマンド |
|---|---|---|
| `セルを正方形にする.py` | 指定セル範囲を正方形にする | `python セルを正方形にする.py` |
| `画像を生成.py` | テスト画像を `outputs/` に生成 | `python 画像を生成.py` |
| `画像を並べる.py` | `outputs/` の画像を Excel に貼り付ける | `python 画像を並べる.py` |
| `練習.py` | 画像付き表のレイアウト練習 | ルートから `python -m excel_arrange_table.練習` |
| `arrange_from_list_to_table.py` | 条件リストから表を生成 | `python arrange_from_list_to_table.py` |
| `num_to_col_name.py` | 数値 → Excel 列名の変換（ライブラリ） | `python -c "from num_to_col_name import num_to_col_name; print(num_to_col_name(28))"` |

`練習.py` / `画像を並べる.py` は `outputs/` に画像がある前提。`arrange_from_list_to_table.py` は参照パスをスクリプト内で指定している。

### `gen_json_from_csv/`

| スクリプト | 内容 | 実行コマンド |
|---|---|---|
| `gen_json_from_a_selected_id_in_csv.py` | CSV の指定 ID を JSON 化 | `python gen_json_from_csv/gen_json_from_a_selected_id_in_csv.py --input_csv <csv> --output_dir <dir> --target_id <id> --type_name setting` |
| `merge_json_vertical.py` | JSON を縦方向に結合（試作） | `python gen_json_from_csv/merge_json_vertical.py` |
| `merge_json_horizon.py` | JSON を横方向に結合（`main()` 内のパスを要編集） | `python gen_json_from_csv/merge_json_horizon.py` |
| `find_files_in_folder.py` | フォルダ内のファイル検索（ライブラリ） | `python -c "from gen_json_from_csv.find_files_in_folder import find_files_in_folder; print(find_files_in_folder('.', '.', '.py'))"` |

### `Tkinter/`

`cd Tkinter` してから実行する。

| スクリプト | 内容 | 実行コマンド |
|---|---|---|
| `Tkinter_練習.py` | ドロップダウン・ボタン・ログの基本 | `python Tkinter_練習.py` |
| `Tkinter_配置練習.py` | フレームとボタンの配置 | `python Tkinter_配置練習.py` |
| `Tkinter_trial.py` | メール送信画面の試作 | `python Tkinter_trial.py` |
| `Tkiner_general_trial.py` | ログ表示ウィンドウ | `python Tkiner_general_trial.py` |
| `プルダウンリスト.py` | プルダウンリスト部品 | `python プルダウンリスト.py` |
| `gui_setting.py` | JSON から GUI 設定画面を生成 | `python gui_setting.py` |
| `settings_by_gui.py` | GUI で設定を編集 | `python settings_by_gui.py` |

### `numpy_trical/`

| スクリプト | 内容 | 実行コマンド |
|---|---|---|
| `多項式.py` | 2 点から 1 次式を求める | `python numpy_trical/多項式.py` |
| `線形補間.py` | `numpy.interp` で線形補間 | `python numpy_trical/線形補間.py` |

### `bash_env_setting/`

| スクリプト | 内容 | 実行コマンド |
|---|---|---|
| `alias_commands.sh` | bash alias 集 | `source bash_env_setting/alias_commands.sh` |
| `change_keyboard_map.sh` | Ctrl / CapsLock・Esc / 全角半角の入替（Ubuntu） | `sudo bash bash_env_setting/change_keyboard_map.sh` |

## ルート直下スクリプト

| スクリプト | 内容 | 実行コマンド |
|---|---|---|
| `clip2snip_body.py` | クリップボードの複数行を C 配列文字列に整形 | `pip install pyperclip`<br>`python clip2snip_body.py` |
| `pdf_w_PyMuPDF.py` | PDF のテキストを抽出して Excel に出力 | `pip install pymupdf openpyxl tqdm`<br>`python pdf_w_PyMuPDF.py <pdf> <doc_type>` |
| `md2html.py` | Markdown を HTML 化（`html_style` を利用） | `pip install markdown beautifulsoup4`<br>`python md2html.py` |
| `html_style.py` | HTML / CSS スタイル生成クラスの試作 | `python html_style.py` |
| `gui.py` | Excel パラメータから PySimpleGUI 画面を生成 | `pip install PySimpleGUI openpyxl`<br>`python gui.py` |
| `gui_checkbox_in_table.py` | PySimpleGUI テーブル内チェックボックスの試作 | `pip install PySimpleGUI`<br>`python gui_checkbox_in_table.py` |
| `pysimplegui_table_with_color.py` | 行ごとに色を付けた PySimpleGUI テーブルの試作 | `pip install PySimpleGUI`<br>`python pysimplegui_table_with_color.py` |
| `音声入力.py` | 録音 → OpenAI 文字起こし → クリップボード | `pip install sounddevice numpy pyperclip openai keyboard`<br>`python 音声入力.py` |
| `memo.py` | 時刻丸め・ビット抽出などのメモ用関数 | `python memo.py` |
| `mymisc.py` | 進数変換などの汎用ユーティリティ | `python mymisc.py` |
| `python.json` | VSCode 用 Python スニペット設定 | VSCode のユーザースニペットに配置して使用 |

補足:

- `pdf_w_PyMuPDF.py` は `--start_page` / `--end_page` / `--log-level` を指定できる
- `md2html.py` は入力ファイルをスクリプト内で指定している
- `gui.py` は参照する Excel のパスをスクリプト内で指定している
- `音声入力.py` は `openai.api_key` を自分のキーに置き換える必要がある

## 各プロジェクトの詳細

- [loadbike/README.md](loadbike/README.md)
- [gantt/README.md](gantt/README.md)
- [remove_mosaic/README.md](remove_mosaic/README.md)

## 補足

- OpenCode 用のガントチャートスキル: `.opencode/skills/gantt/SKILL.md`
- 生成物や試作ディレクトリは `.gitignore` で除外しているため、この README には掲載していない
