#!/usr/bin/env python
"""Upscale a single image file with Real-ESRGAN (realesr-general-x4v3).

Example:
  python upscale_single.py ^
    --input "C:\\path\\to\\image.png" ^
    --scale 2

Output: C:\\path\\to\\image_x2.png
"""

import argparse
import os
import sys
import time

import numpy as np
from PIL import Image

from realesrgan import RealESRGANer
from realesrgan.archs.srvgg_arch import SRVGGNetCompact


def parse_args():
    here = os.path.dirname(os.path.abspath(__file__))
    default_model = os.path.normpath(
        os.path.join(here, "..", "models", "realesr-general-x4v3.pth")
    )
    p = argparse.ArgumentParser(description="Real-ESRGAN single image upscaler")
    p.add_argument("--input", required=True, help="path to source image file")
    p.add_argument("--scale", type=int, choices=[2, 4], default=2, help="output scale (2 or 4)")
    p.add_argument("--model", default=default_model, help="path to the .pth model")
    p.add_argument("--tile", type=int, default=0, help="tile size, 0 = whole image")
    p.add_argument("--tile-pad", type=int, default=10)
    p.add_argument("--pre-pad", type=int, default=10)
    p.add_argument("--half", action="store_true", help="use half precision (GPU)")
    return p.parse_args()


def main():
    args = parse_args()

    if not os.path.isfile(args.input):
        print(f"ERROR: input file not found: {args.input}", file=sys.stderr)
        return 1
    if not os.path.isfile(args.model):
        print(f"ERROR: model file not found: {args.model}", file=sys.stderr)
        return 1

    input_dir = os.path.dirname(os.path.abspath(args.input))
    stem = os.path.splitext(os.path.basename(args.input))[0]
    output_path = os.path.join(input_dir, f"{stem}_x{args.scale}.png")

    print(f"Model : {args.model}")
    print(f"Input : {args.input}")
    print(f"Output: {output_path}")
    print(f"Scale : {args.scale}x")
    print("-" * 64)

    model = SRVGGNetCompact(
        num_in_ch=3, num_out_ch=3, num_feat=64, num_conv=32,
        upscale=4, act_type="prelu",
    )
    upsampler = RealESRGANer(
        scale=4,
        model_path=args.model,
        model=model,
        tile=args.tile,
        tile_pad=args.tile_pad,
        pre_pad=args.pre_pad,
        half=args.half,
    )

    t0 = time.time()
    img = Image.open(args.input).convert("RGB")
    arr = np.array(img, dtype=np.float32)
    arr = arr[:, :, ::-1]

    out, _ = upsampler.enhance(arr, outscale=args.scale)
    out = out[:, :, ::-1]

    Image.fromarray(out).save(output_path)

    dt = time.time() - t0
    print("-" * 64)
    print(f"DONE. Upscaled {args.scale}x in {dt:.1f}s -> {output_path}")
    print(f"Output size: {out.shape[1]}x{out.shape[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())