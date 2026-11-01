# Skill: image-upscale-single

# Single Image AI Upscaler (Real-ESRGAN)

Upscale a single image file by **2x or 4x** using Real-ESRGAN, saving the result
in the same folder with `_x2` or `_x4` suffix.

## 1. Parameters

| Parameter | Required | Description | Example |
| --------- | -------- | ----------- | ------- |
| `--input` | Yes | Path to source image file | `C:\images\photo.png` |
| `--scale` | No (default 2) | Output scale: `2` or `4` | `2` |
| `--model` | No | Custom .pth model path | bundled default |
| `--tile` | No (default 0) | Tile size for VRAM saving | `0` |
| `--half` | No | Use FP16 on GPU | flag |

## 2. Quick Start

```powershell
# 1. Environment check (run once)
python "C:\work\VSCode_Projects\GitLocals\development\.opencode\skills\image-upscale-single\scripts\check_env.py"

# 2. Upscale 2x
python "C:\work\VSCode_Projects\GitLocals\development\.opencode\skills\image-upscale-single\scripts\upscale_single.py" `
  --input "E:\tmpGame\etc\kb124784577_p1-2.png" `
  --scale 2
# Output: E:\tmpGame\etc\kb124784577_p1-2_x2.png

# 3. Upscale 4x
python "C:\work\VSCode_Projects\GitLocals\development\.opencode\skills\image-upscale-single\scripts\upscale_single.py" `
  --input "E:\tmpGame\etc\kb124784577_p1-2.png" `
  --scale 4
# Output: E:\tmpGame\etc\kb124784577_p1-2_x4.png
```

## 3. Output

- Saved as PNG (lossless) in the same directory as input
- Naming: `<original_name>_x{scale}.png`
- Example: `photo.jpg` → `photo_x2.png` (2x) or `photo_x4.png` (4x)

## 4. Model

Uses `realesr-general-x4v3.pth` (SRVGGNetCompact, 4x architecture).
The `outscale` parameter in `RealESRGANer.enhance()` handles arbitrary output scales
(2x, 4x, etc.) from the single 4x model.

## 5. Dependencies

Same as `image-pingpong-loop` skill (validated 2026-09):

| Package | Version |
| ------- | ------- |
| Python | 3.10 |
| realesrgan | 0.3.0 |
| basicsr | 1.4.2 |
| torch | 1.12.1 |
| torchvision | 0.13.1 |
| numpy | <2 (1.26.4) |
| Pillow | any recent |

Run `check_env.py` to verify.

## 6. File Structure

```
image-upscale-single/
├── SKILL.md
├── models/
│   └── realesr-general-x4v3.pth
└── scripts/
    ├── check_env.py
    └── upscale_single.py
```