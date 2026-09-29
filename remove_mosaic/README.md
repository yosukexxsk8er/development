# remove_mosaic — DeepMosaics によるモザイク除去

画像のモザイクを AI（DeepMosaics）で除去して保存するツールです。

- 処理はすべてローカルで完結（モデルの初回ダウンロードのみ別途必要）
- 入力画像と同じフォルダに `<ファイル名>-2.<拡張子>` として保存
  （`-2` が既にあれば `-3`, `-4` … と自動で加算）
- 出力の拡張子は入力と同じ
- CPU で動作（NVIDIA GPU / CUDA が無くても可）

## 構成

```
remove_mosaic/
  .venv\                 … Python 3.10 専用の実行環境（ここに作成済み）
  DeepMosaics\           … HypoX64/DeepMosaics 本体（GPL-3.0。コードはほぼ未改変を流用）
    pretrained_models\mosaic\   … モデル配置先
  remove_mosaic.py       … 実行ラッパー
  README.md
```

## 必要なモデル（無料・別途ダウンロード）

事前学習済みモデルは DeepMosaics リポジトリには含まれていません。
公式 README のバンドルから無料で取得できます（モザイク除去に必要な 2 ファイルが同梱）。

| ファイル | 役割 |
| --- | --- |
| `mosaic_position.pth` | モザイク位置の検出（BiSeNet）… **必須** |
| `clean_face_HD.pth` 等 | モザイク部分の修復（pix2pix）。`clean_face.pth`（128px・CPU 向き・高速）でも可 |

### 入手リンク（公式）

- **Google Drive**: https://drive.google.com/open?id=1LTERcN33McoiztYEwBxMuRjjgxh4DEPs
- **百度云**: https://pan.baidu.com/s/10rN3U3zd5TmfGpO_PEShqQ （提取码: `1x0a`）

### 配置場所

```
remove_mosaic\DeepMosaics\pretrained_models\mosaic\mosaic_position.pth
remove_mosaic\DeepMosaics\pretrained_models\mosaic\clean_face_HD.pth
```

配置後は `remove_mosaic.py` が自動で検出します（clean モデルは同フォルダの
`clean_*.pth` から `clean_face_HD` → `clean_face` → `clean_face_unet_128` … の順に選択）。

## 実行環境（venv）について

`.venv` は Python 3.10 で作成済みです。既存の環境や torch のバグ影響を受けないよう
DeepMosaics 専用に分離しています（torch 1.11.0+cpu / numpy 1.23.5 / opencv-python 4.9 等）。

再構築する場合:

```
py -3.10 -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install torch==1.11.0+cpu torchvision==0.12.0+cpu --index-url https://download.pytorch.org/whl/cpu
.venv\Scripts\python -m pip install numpy==1.23.5 opencv-python==4.9.0.80 scikit-image==0.19.3
```

`remove_mosaic.py` は起動時に自動で `.venv` 配下の python を使い直すため、
普通の `python` で実行しても構いません（推奨は下記の明示指定）。

## 使い方

```
remove_mosaic\.venv\Scripts\python.exe remove_mosaic\remove_mosaic.py <画像パス|画像フォルダ> [オプション]
```

### 例

```
# 1 枚の画像（photo.jpg → photo-2.jpg）
.venv\Scripts\python.exe remove_mosaic.py ..\Pictures\photo.jpg

# フォルダ内の全画像（それぞれ -2 / -3 … として保存）
.venv\Scripts\python.exe remove_mosaic.py ..\Pictures\batch

# 品質より速度優先（エッジのぼかし統合を省略）
.venv\Scripts\python.exe remove_mosaic.py .\imgs\a.png --no_feather

# モデルを明示指定
.venv\Scripts\python.exe remove_mosaic.py a.jpg --model .\models\clean_face.pth
```

### よく使うオプション

| オプション | 説明 |
| --- | --- |
| `--model PATH` | 修復モデルを明示指定 |
| `--position_model PATH` | 位置検出モデルを明示指定 |
| `--netG {auto,HD,unet_128,unet_256,resnet_9blocks}` | モデル構成。auto はファイル名から推定 |
| `--traditional` | ニューラルモデルを使用しない従来方式（ぼかし＋縮小/拡大）。低品質だが `mosaic_position.pth` のみで動作 |
| `--no_feather` | 高速化（エッジ統合省略） |
| `--all_mosaic_area` | 最大の 1 領域だけでなく、検出されたモザイク領域すべてを処理 |
| `--mask_threshold N` | モザイク検出しきい値（既定 64）。小さいほどモザイクと判定されやすい |

### モザイクが検出できない場合

`size <= 100` のときは「モザイク領域を検出できませんでした」と警告し、
入力画像をそのまま出力名でコピーします（上書き保存はされません）。

## 仕組み

1. **BiSeNet**（`mosaic_position.pth`）がモザイク領域をセグメンテーションで検出
2. **pix2pix 系 Generator**（`clean_*.pth`）がその領域を再構築
3. 元画像へフレザリング合成して保存

詳細は DeepMosaics 本家 README / docs を参照してください。

## ライセンス・出典

- 処理本体: [HypoX64/DeepMosaics](https://github.com/HypoX64/DeepMosaics)（GPL-3.0）
  このツールは同プロジェクトのコードを使用しています。
- 学習済みモデルの権利・配布は上記プロジェクトに帰属します。