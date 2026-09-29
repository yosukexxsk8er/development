#!/usr/bin/env python3
"""
DeepMosaics によるモザイク除去ラッパー

使い方:
    remove_mosaic\remove_mosaic.py <入力画像|画像フォルダ> [オプション]
    remove_mosaic\remove_mosaic.py photo.jpg --mosaic 120,80,200   # 手動指定

オプション:
    --mosaic x,y,width[,height]
                         モザイク領域の左上座標(x,y)と矩形サイズ(width[,height])を px 単位で手動指定。
                         指定時は自動位置検出をスキップし、指定領域を修復する。

出力:
    入力画像と同じフォルダに <stem>-2.<ext> として保存。
    -2 が既に存在すれば -3, -4, ... と自動で加算。

例:
    .venv\Scripts\python.exe remove_mosaic.py photo.jpg
    .venv\Scripts\python.exe remove_mosaic.py .\imgs --no_feather
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEEPMOSAICS_DIR = os.path.join(BASE_DIR, "DeepMosaics")
VENV_PY = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")
MODELS_DIR = os.path.join(DEEPMOSAICS_DIR, "pretrained_models", "mosaic")
LAMA_MODEL_PATH = os.path.join(DEEPMOSAICS_DIR, "pretrained_models", "lama", "lama_fp32.onnx")
LAMA_HELPER = os.path.join(DEEPMOSAICS_DIR, "lama", "inpaint_lama.py")
LAMA_VENV_PY = os.path.join(BASE_DIR, ".venv_lama", "Scripts", "python.exe")

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}
CLEAN_CANDIDATES = [
    "clean_face_HD.pth",
    "clean_face.pth",
    "clean_face_unet_128.pth",
    "clean_unet_128.pth",
    "clean_youknow_resnet_9blocks.pth",
]
POSITION_MODEL_NAME = "mosaic_position.pth"


def _force_utf8_stdio():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def _relaunch_under_venv():
    """未使用の場合は remove_mosaic/.venv の python で自身を再実行する"""
    if not os.path.exists(VENV_PY):
        print("ERROR: .venv が見つかりません: %s" % VENV_PY)
        print("構築手順は README.md を参照してください。")
        sys.exit(1)
    if sys.executable and os.path.normcase(os.path.abspath(sys.executable)) == os.path.normcase(VENV_PY):
        return
    print("DeepMosaics 専用 venv で再実行します: %s" % VENV_PY, flush=True)
    sys.exit(subprocess.call([VENV_PY] + sys.argv))


def parse_args(argv):
    p = argparse.ArgumentParser(
        description="DeepMosaics によるモザイク除去",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("images", nargs="+", metavar="PATH",
                    help="入力画像ファイル（複数可）またはフォルダ")
    p.add_argument("--mosaic", type=str, default=None,
                   help="モザイク領域を手動で指定（例: x,y,width または x,y,width,height。左上原点）")
    p.add_argument("--model", default=None,
                   help="修復(clean)用モデル .pth のパス、または lama（LaMa インペインティング）")
    p.add_argument("--position_model", default=None,
                   help="モザイク位置検出モデル mosaic_position.pth のパス")
    p.add_argument("--netG", default="auto",
                   choices=["auto", "HD", "unet_128", "unet_256", "resnet_9blocks"],
                   help="修復モデルのアーキテクチャ（auto なら .pth ファイル名から推定）")
    p.add_argument("--traditional", action="store_true",
                   help="ニューラルモデルを使わない従来方式（ぼかし+縮小/拡大）。位置検出モデルのみ必要")
    p.add_argument("--no_feather", action="store_true",
                   help="エッジのぼかし統合をやめて高速化")
    p.add_argument("--feather_width", type=int, default=None,
                   help="手動モード(--mosaic 指定)で境界をにじませる幅(px)。大きいほど周囲と馴染む(既定: 自動)")
    p.add_argument("--all_mosaic_area", action="store_true",
                   help="最大領域ではなく検出された全てのモザイク領域を処理")
    p.add_argument("--mask_threshold", type=int, default=64,
                   help="モザイク検出しきい値(0-255)。小さいほどモザイクと判定されやすい")
    p.add_argument("--ex_mult", type=float, default=None,
                   help="モザイク領域の拡大率（auto: face 1.1 / その他 1.5）")
    return p.parse_args(argv)


def detect_netG(model_name):
    name = os.path.basename(model_name)
    if "unet_128" in name:
        return "unet_128"
    if "unet_256" in name:
        return "unet_256"
    if "resnet_9blocks" in name:
        return "resnet_9blocks"
    if "HD" in name and "video" not in name:
        return "HD"
    return None


def resolve_models(args):
    pos = args.position_model or os.path.join(MODELS_DIR, POSITION_MODEL_NAME)
    if not os.path.isfile(pos):
        return None, False, (
            "ERROR: モザイク位置検出モデルが見つかりません: %s\n"
            "  以下の場所に mosaic_position.pth を配置してください:\n"
            "    %s\n"
            "  モデルは公式リンクから無料で取得できます:\n"
            "    Google Drive: https://drive.google.com/open?id=1LTERcN33McoiztYEwBxMuRjjgxh4DEPs\n"
            "    百度云       : https://pan.baidu.com/s/10rN3U3zd5TmfGpO_PEShqQ  (提取码: 1x0a)"
            % (pos, MODELS_DIR)
        )
    if args.traditional:
        return pos, False, None
    if args.model == "lama":
        missing = [p for p in (LAMA_VENV_PY, LAMA_HELPER, LAMA_MODEL_PATH) if not os.path.isfile(p)]
        if missing:
            return None, None, (
                "ERROR: LaMa 用ファイルが見つかりません:\n  %s\n"
                "  .venv_lama の作成:  python -m venv .venv_lama のうえ pip install onnxruntime pillow\n"
                "  モデルDL      :  https://huggingface.co/Carve/LaMa-ONNX/resolve/main/lama_fp32.onnx"
                % "\n  ".join(missing)
            )
        return pos, None, None
    clean = args.model
    if clean is not None and not os.path.isfile(clean):
        return None, False, "ERROR: --model が見つかりません: %s" % clean
    if clean is None:
        for name in CLEAN_CANDIDATES:
            cand = os.path.join(MODELS_DIR, name)
            if os.path.isfile(cand):
                clean = cand
                break
    if clean is None:
        cands = [os.path.join(MODELS_DIR, n) for n in sorted(os.listdir(MODELS_DIR))
                 if n.startswith("clean") and n.endswith(".pth")] if os.path.isdir(MODELS_DIR) else []
        if cands:
            clean = cands[0]
    if clean is None:
        return None, False, (
            "ERROR: 修復(clean)用モデルが見つかりません: %s\n"
            "  clean_face_HD.pth / clean_face.pth などを %s に配置してください。\n"
            "  入手先は上の mosaic_position.pth と同じバンドルに含まれます。" % (MODELS_DIR, MODELS_DIR)
        )
    return pos, clean, None


def collect_images(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, names in os.walk(p):
                for n in sorted(names):
                    if os.path.splitext(n)[1].lower() in IMAGE_EXTS:
                        files.append(os.path.join(root, n))
        elif os.path.isfile(p):
            files.append(p)
        else:
            print("WARNING: 存在しないパスをスキップ: %s" % p)
    return files


def resolve_output_path(in_path):
    dump_dir = os.path.dirname(in_path)
    stem, ext = os.path.splitext(in_path)
    n = 2
    while os.path.exists(os.path.join(dump_dir, "%s-%d%s" % (stem, n, ext))):
        n += 1
    return os.path.join(dump_dir, "%s-%d%s" % (stem, n, ext))


def _convert_to(src_jpg, dst_path):
    ext = os.path.splitext(dst_path)[1].lower()
    if ext in (".jpg", ".jpeg", ""):
        shutil.copyfile(src_jpg, dst_path)
        return
    try:
        import cv2
        import numpy as np
        with open(src_jpg, "rb") as f:
            buf = f.read()
        img = cv2.imdecode(np.frombuffer(buf, np.uint8), cv2.IMREAD_UNCHANGED)
        if img is None:
            raise ValueError("decode failed")
        ok, enc = cv2.imencode(ext, img)
        if not ok:
            raise ValueError("imencode failed: %s" % ext)
        enc.tofile(dst_path)
    except Exception as e:
        print("WARNING: %s への変換に失敗したため jpg のまま保存しました (%s)" % (ext, e))
        shutil.copyfile(src_jpg, dst_path)


def process_one(args, in_path, pos_model, clean_model, netG):
    # DeepMosaics は遅延 import（venv 再実行後にパスを追加してから行う）
    sys.path.insert(0, DEEPMOSAICS_DIR)
    import numpy as np
    import cv2
    from util import image_processing as impro
    from models import loadmodel, runmodel
    from cores import clean

    class Opt:
        pass

    opt = Opt()
    opt.gpu_id = "-1"
    opt.media_path = in_path
    opt.model_path = clean_model or ""
    opt.mosaic_position_model_path = pos_model
    opt.netG = netG or ""
    opt.mask_threshold = args.mask_threshold
    opt.all_mosaic_area = args.all_mosaic_area
    opt.ex_mult = args.ex_mult if args.ex_mult is not None else (
        1.1 if clean_model and "face" in os.path.basename(clean_model) else 1.5)
    opt.traditional = args.traditional
    opt.no_feather = args.no_feather
    opt.tr_blur = 10
    opt.tr_down = 10

    out_path = resolve_output_path(in_path)
    print("\n[IN ] %s\n[OUT] %s" % (in_path, out_path))

    img_origin = impro.imread(in_path)
    if img_origin is None:
        print("ERROR: 画像を読み込めませんでした: %s" % in_path)
        return 1

    netM = None
    if not args.mosaic:
        netM = loadmodel.bisenet(opt, "mosaic")

    netG = None
    use_lama = (args.model == "lama")
    if not opt.traditional and not use_lama:
        netG = loadmodel.pix2pix(opt)

    mask = None
    if args.mosaic:
        try:
            parts = [int(v) for v in args.mosaic.split(',')]
            if len(parts) == 3:
                tl_x, tl_y, rw = parts
                rh = rw
            elif len(parts) == 4:
                tl_x, tl_y, rw, rh = parts
            else:
                raise ValueError
            h_img, w_img = img_origin.shape[:2]
            
            # クロップ領域を画像境界内に収める
            x1 = max(0, tl_x)
            y1 = max(0, tl_y)
            x2 = min(w_img, tl_x + rw)
            y2 = min(h_img, tl_y + rh)
            
            if x2 <= x1 or y2 <= y1:
                print("ERROR: 指定されたモザイク領域が無効または画像範囲外です。")
                return 1
            
            # center_x, center_y, half_size に変換
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            half_size_x = (x2 - x1) // 2
            half_size_y = (y2 - y1) // 2
            # 指定矩形を丸ごと覆う外接正方形にする
            # さらににじみバンド用の余白を確保（DeepMosaics 本体の ex_mult 相当）
            base = max(half_size_x, half_size_y, 1)
            feather_allow = (args.feather_width // 2 if (args.feather_width and not args.no_feather) else 0)
            size = base + feather_allow + base // 10 + 2
            x, y = center_x, center_y
            # 正方形が画像内に収まるよう必要なら中心をずらす
            if size > w_img // 2:
                size = max(w_img // 2, 1)
            if size > h_img // 2:
                size = max(h_img // 2, 1)
            x = min(max(x, size), w_img - size)
            y = min(max(y, size), h_img - size)
            
            # マスク生成 (img_origin と同じサイズで、指定領域を白(255)にする)
            mask = np.zeros(img_origin.shape[:2], dtype=np.uint8)
            mask[y1:y2, x1:x2] = 255 # y1:y2 は行、x1:x2 は列

            # 境界の馴染ませ幅（no_feather はブレンド無しのため無効）
            if not opt.no_feather:
                fw = int(args.feather_width) if args.feather_width else (int(size // 10) + 2)
                fw |= 1  # 必ず奇数
                mask = cv2.blur(mask, (fw, fw))
                print(f"  境界にじみ幅: {fw}px")

            print(f"手動モザイク領域: ({tl_x},{tl_y}) {rw}x{rh} -> 中央({x},{y}) 半径={size}")
            
        except (ValueError, TypeError):
            print("ERROR: --mosaic の形式が不正です。x,y,width または x,y,width,height で指定してください。")
            return 1
    else:
        x, y, size, mask = runmodel.get_mosaic_position(img_origin, netM, opt)
        if size <= 100:
            print("WARNING: モザイク領域を検出できませんでした (size=%d)" % size)
            shutil.copyfile(in_path, out_path)
            print("  入力画像をそのまま %s にコピーしました。" % out_path)
            return 0

    if mask is None: # 手動指定でエラーがないのにマスクが作られてない場合など
        print("ERROR: マスクが生成できませんでした。")
        return 1

    tmpdir = tempfile.mkdtemp(prefix="remove_mosaic_")
    try:
        if use_lama:
            if size <= 50:
                print("WARNING: 指定領域が小さいため品質が低下する可能性があります (size=%d)" % size)
            sy1, sy2 = y - size, y + size
            sx1, sx2 = x - size, x + size
            crop_p = os.path.join(tmpdir, "crop.png")
            crop_mask_p = os.path.join(tmpdir, "crop_mask.png")
            out_p = os.path.join(tmpdir, "lama_out.png")
            crop_rgb = cv2.cvtColor(img_origin[sy1:sy2, sx1:sx2], cv2.COLOR_BGR2RGB)
            impro.imwrite(crop_p, crop_rgb)
            impro.imwrite(crop_mask_p, mask[sy1:sy2, sx1:sx2])
            rc = subprocess.call([LAMA_VENV_PY, LAMA_HELPER, LAMA_MODEL_PATH,
                                  crop_p, crop_mask_p, out_p, str(2 * size), str(2 * size)])
            if rc != 0 or not os.path.isfile(out_p):
                print("ERROR: LaMa インペイントが失敗しました (exit=%d)" % rc)
                return 1
            result = impro.imread(out_p)
            if result.shape[:2] != (2 * size, 2 * size):
                result = cv2.resize(result, (2 * size, 2 * size))
            if opt.no_feather:
                maskf = (mask[sy1:sy2, sx1:sx2].astype(np.float32) / 255.0 >= 0.5).astype(np.float32)
            else:
                maskf = mask[sy1:sy2, sx1:sx2].astype(np.float32) / 255.0
            crop_orig = img_origin[sy1:sy2, sx1:sx2].astype(np.float32)
            blended = np.clip(
                crop_orig * (1.0 - maskf[..., None]) + result.astype(np.float32) * maskf[..., None],
                0, 255).astype(np.uint8)
            img_result = img_origin.copy()
            img_result[sy1:sy2, sx1:sx2] = blended
            tmp_out = os.path.join(tmpdir, "result.png")
            impro.imwrite(tmp_out, img_result)
        elif args.mosaic:
            if size <= 50:
                print("WARNING: 指定領域が小さいため品質が低下する可能性があります (size=%d)" % size)
            img_mosaic = img_origin[y - size:y + size, x - size:x + size]
            if opt.traditional:
                img_fake = runmodel.traditional_cleaner(img_mosaic, opt)
            else:
                img_fake = runmodel.run_pix2pix(img_mosaic, netG, opt)
            img_result = impro.replace_mosaic(img_origin.copy(), img_fake, mask, x, y, size, opt.no_feather)
            tmp_out = os.path.join(tmpdir, "result.png")
            impro.imwrite(tmp_out, img_result)
        else:
            opt.result_dir = tmpdir
            opt.media_path = in_path
            clean.cleanmosaic_img(opt, netG, netM)
            stem = os.path.splitext(os.path.basename(in_path))[0]
            tmp_out = os.path.join(tmpdir, stem + "_clean.jpg")
        if not os.path.isfile(tmp_out):
            print("ERROR: 処理結果が見つかりません: %s" % tmp_out)
            return 1
        _convert_to(tmp_out, out_path)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    print("Done:", out_path)
    return 0


def main(argv=None):
    _force_utf8_stdio()
    _relaunch_under_venv()
    args = parse_args(argv if argv is not None else sys.argv[1:])

    pos_model, clean_model, err = resolve_models(args)
    if err:
        print(err)
        sys.exit(1)

    netG = args.netG
    if netG == "auto" and not args.traditional and clean_model:
        netG = detect_netG(clean_model)
        if netG is None:
            print("ERROR: 修復モデルの種類を判定できません。--netG を指定してください。")
            sys.exit(1)

    files = collect_images(args.images)
    if not files:
        print("ERROR: 処理対象の画像がありません。")
        sys.exit(1)

    print("モデル:")
    print("  位置検出: %s" % pos_model)
    if args.model == "lama":
        print("  修復    : LaMa (ONNX: %s)" % os.path.basename(LAMA_MODEL_PATH))
    elif clean_model:
        print("  修復    : %s (netG=%s)" % (clean_model, netG))
    else:
        print("  修復    : 従来方式 (--traditional)")

    rc = 0
    for f in files:
        rc += process_one(args, f, pos_model, clean_model, netG)
    print("\n全処理が完了しました。")
    sys.exit(rc)


if __name__ == "__main__":
    main()