"""Verify a finished brand mark before it's dropped into a project.

Asserts the house-convention shape: square, sized (default 1024), RGBA with
REAL transparency (a transparent background, not a fully-opaque frame), and a
mark that actually fills a sensible fraction of the canvas. Exits non-zero with
a clear reason on any failure, so a workflow can gate on it.

Deps: Pillow + numpy. Zero-install:
  uv run --with pillow --with numpy python3 verify_mark.py mark.png [--size 1024]
"""
import argparse
import sys

import numpy as np
from PIL import Image


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mark")
    ap.add_argument("--size", type=int, default=1024)
    a = ap.parse_args()

    im = Image.open(a.mark)
    problems = []

    if im.mode != "RGBA":
        problems.append(f"mode is {im.mode}, expected RGBA (no alpha channel — not transparent)")
        im = im.convert("RGBA")

    w, h = im.size
    if w != h:
        problems.append(f"not square: {w}x{h}")
    if a.size and (w != a.size or h != a.size):
        problems.append(f"size {w}x{h}, expected {a.size}x{a.size}")

    alpha = np.asarray(im)[:, :, 3]
    amin, amax = int(alpha.min()), int(alpha.max())
    if amin > 5:
        problems.append(f"no transparent pixels (alpha min={amin}) — background is baked in, not keyed out")
    if amax < 250:
        problems.append(f"nothing fully opaque (alpha max={amax}) — the mark art is missing or too faint")

    fill = float((alpha > 10).mean())
    if fill < 0.02:
        problems.append(f"mark fills only {fill:.1%} of the canvas — matte likely lost the art")
    if fill > 0.98:
        problems.append(f"mark fills {fill:.1%} of the canvas — background probably not keyed out")

    tag = a.mark.split("/")[-1]
    if problems:
        print(f"FAIL {tag}: " + "; ".join(problems))
        return 1
    print(f"OK {tag}: RGBA {w}x{h}, alpha {amin}/{amax}, fill {fill:.0%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
