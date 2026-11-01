# Skill: image-upscale-single

## Purpose
Upscale a single image file by 2x or 4x using Real-ESRGAN, saving the result in the same folder with `_x2` or `_x4` suffix.

## Input Parameters
| Parameter | Description | Example |
|-----------|-------------|---------|
| Input file | Path to source image | `C:\images\photo.png` |
| Scale | 2 or 4 (multiplier) | `2` |
| Model | Optional custom .pth model | bundled `realesr-general-x4v3.pth` |

## Output
- Upscaled image saved as `<original_name>_x{scale}.png` in same directory
- Example: `photo.png` → `photo_x2.png` (2x) or `photo_x4.png` (4x)

## Implementation Steps

### 1. Skill Structure
```
image-upscale-single/
├── SKILL.md          # This documentation
├── models/
│   └── realesr-general-x4v3.pth  (symlink or copy from existing skill)
└── scripts/
    ├── check_env.py       # Reuse from image-pingpong-loop
    └── upscale_single.py  # New script for single file
```

### 2. upscale_single.py Requirements
- Accept `--input` (file path), `--scale` (2 or 4), `--model` (optional)
- Validate input file exists
- Determine output path: `<input_dir>/<stem>_x{scale}.png`
- Load RealESRGANer with 4x model
- For 2x: use outscale=2 (model outputs 4x, then downscale? No - model is 4x only)
  - Actually: realesr-general-x4v3 is 4x model. For 2x, we can:
    - Option A: Run at 4x then downscale by 0.5 with lanczos
    - Option B: Use outscale=2 (but model is fixed 4x architecture)
    - Looking at upscale_images.py: `--outscale` is passed to `enhance()` - this controls the final output scale
    - The model is 4x but `outscale` parameter allows different output scales
- Save as PNG

### 3. Environment Check
Reuse `check_env.py` from image-pingpong-loop skill (same dependencies)

### 4. Usage Example
```powershell
python "C:\path\to\image-upscale-single\scripts\upscale_single.py" `
  --input "E:\tmpGame\etc\kb124784577_p1-2.png" `
  --scale 2
# Output: E:\tmpGame\etc\kb124784577_p1-2_x2.png
```

## Dependencies
Same as image-pingpong-loop:
- Python 3.10
- realesrgan 0.3.0
- basicsr 1.4.2
- torch 1.12.1
- torchvision 0.13.1
- numpy <2
- Pillow
- ffmpeg (not strictly needed for single image, but for consistency)

## Notes
- The 4x model with outscale=2 should work (RealESRGANer handles arbitrary outscale)
- Output format: PNG (lossless)
- Overwrite behavior: overwrite without prompt (or add --force flag)