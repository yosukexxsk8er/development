#!/usr/bin/env python
"""Environment self-check for the image-pingpong-loop skill.

Verifies that Python, ffmpeg and the pinned library versions required by
Real-ESRGAN 0.3.0 are present. Prints a dependency table and, on any
mismatch, the exact remediation command.

Exit code 0 = all good, 1 = problems found.
"""

import importlib
import importlib.metadata as md
import shutil
import subprocess
import sys


PINNED = {
    "realesrgan": "0.3.0",
    "basicsr": "1.4.2",
    "torch": "1.12.1",
    "torchvision": "0.13.1",
}


def get_version(pkg):
    try:
        return md.version(pkg)
    except md.PackageNotFoundError:
        return None


def ffmpeg_version():
    exe = shutil.which("ffmpeg")
    if not exe:
        return None, None
    try:
        out = subprocess.run(
            [exe, "-version"], capture_output=True, text=True, timeout=30
        )
        first = out.stdout.splitlines()[0] if out.stdout else ""
        return exe, first
    except Exception:
        return exe, "(version check failed)"


def main():
    problems = []

    print("=" * 64)
    print("image-pingpong-loop / environment check")
    print("=" * 64)

    py = sys.version.split()[0]
    py_ok = sys.version_info[:2] == (3, 10)
    print(f"[{'OK ' if py_ok else 'WARN'}] python            {py}  (recommended 3.10)")
    if not py_ok:
        print("       Note: other 3.x usually works but was not validated.")

    exe, ver = ffmpeg_version()
    if exe:
        print(f"[OK ] ffmpeg            {ver}")
    else:
        print("[FAIL] ffmpeg            not found on PATH")
        problems.append("Install ffmpeg and ensure it is on PATH (https://www.gyan.dev/ffmpeg/builds/).")

    versions = {}
    for pkg, want in PINNED.items():
        try:
            importlib.import_module(pkg)
            have = get_version(pkg)
        except Exception as exc:  # import may fail even if metadata exists
            have = get_version(pkg)
            print(f"[FAIL] {pkg:<15} import error: {exc}")
            problems.append(f"pip install {pkg}=={want}")
            versions[pkg] = None
            continue
        versions[pkg] = have
        ok = have == want
        tag = "OK " if ok else "WARN"
        print(f"[{tag}] {pkg:<15} {have}  (pinned {want})")
        if not ok:
            problems.append(f"pip install {pkg}=={want}")

    # numpy must be < 2 for torch 1.12.1
    try:
        import numpy as np
        nv = np.__version__
        nv_ok = int(nv.split(".")[0]) < 2
        print(f"[{'OK ' if nv_ok else 'FAIL'}] {'numpy':<15} {nv}  (must be <2)")
        if not nv_ok:
            problems.append('pip install "numpy<2"')
    except Exception as exc:
        print(f"[FAIL] numpy            import error: {exc}")
        problems.append('pip install "numpy<2"')

    # Pillow and opencv are needed by the scripts
    for pkg, modname in (("Pillow", "PIL"), ("opencv-python", "cv2")):
        try:
            importlib.import_module(modname)
            print(f"[OK ] {pkg:<15} {get_version(pkg)}")
        except Exception as exc:
            print(f"[FAIL] {pkg:<15} import error: {exc}")
            problems.append(f"pip install {pkg}")

    print("-" * 64)
    if problems:
        # de-duplicate while keeping order
        seen = set()
        cmds = [p for p in problems if not (p in seen or seen.add(p))]
        print("PROBLEMS FOUND. Recommended remediation (run in order):")
        print()
        print("  pip install realesrgan")
        print('  pip install torch==1.12.1 torchvision==0.13.1 "numpy<2"')
        for c in cmds:
            if c.startswith("pip install realesrgan"):
                continue
            print(f"  {c}")
        print()
        print("Then re-run this check.")
        return 1

    print("All checks passed. Ready to upscale.")

    print("=" * 64)
    return 0


if __name__ == "__main__":
    sys.exit(main())
