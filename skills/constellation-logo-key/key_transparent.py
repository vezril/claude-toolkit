"""Key checkerboard- or solid-background logo art to a TRANSPARENT PNG mark.

House brand convention: marks ship on transparent alpha (art opaque, neon
bloom as a semi-transparent colored halo), NOT baked onto a background color.
Same difference-matte as the legacy checkerboard keyer, but the output keeps a
straight alpha channel so the mark composites on any surface.

Works on:
  - checkerboard-background art (the two-gray keying aid many image models emit)
  - a flat/solid background (degenerates to a single-gray matte — still keys)

Deps: Pillow + numpy. Zero-install run:
  uv run --with pillow --with numpy python3 key_transparent.py in.jpeg --out out.png

Usage:
  python3 key_transparent.py SRC... [--out DST | --outdir DIR]
                             [--preview [--preview-out P]]
                             [--size 1024] [--margin 0.06] [--bloom 0.55]
                             [--flat #RRGGBB]   # opaque composite instead of alpha
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def _hex(s: str) -> np.ndarray:
    s = s.lstrip("#")
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def key(src: str, size: int, margin: float, bloom: float, flat) -> Image.Image:
    im = Image.open(src).convert("RGB")
    px = np.asarray(im).astype(np.float32)
    h, w, _ = px.shape

    # 1. background gray(s) from the four 48px corners
    corners = np.concatenate([
        px[:48, :48].reshape(-1, 3), px[:48, -48:].reshape(-1, 3),
        px[-48:, :48].reshape(-1, 3), px[-48:, -48:].reshape(-1, 3),
    ])
    lum = corners.mean(axis=1)
    g1 = corners[lum <= np.median(lum)].mean(axis=0)
    g2 = corners[lum > np.median(lum)].mean(axis=0)

    # 2. difference matte vs the nearer background gray
    d1 = np.abs(px - g1).max(axis=2)
    d2 = np.abs(px - g2).max(axis=2)
    nearest_is_1 = d1 <= d2
    dmin = np.where(nearest_is_1, d1, d2)
    gap = float(np.abs(g1 - g2).max())
    threshold = max(14.0, gap * 0.6)
    alpha = np.clip((dmin - threshold) / 60.0, 0.0, 1.0)
    alpha = np.asarray(
        Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(3)),
        dtype=np.float32,
    ) / 255.0

    # 3. recover foreground color (flatten checker light/dark inside partial alpha)
    a3 = alpha[..., None]
    g = np.where(nearest_is_1[..., None], g1, g2)
    g_mean = (g1 + g2) / 2
    fg = np.clip(px - (g - g_mean) * (1 - a3), 0, 255)

    # 4. glow halo: blurred premultiplied art + blurred alpha
    art_premult = (a3 * fg).astype(np.uint8)
    bloom_rgb = np.asarray(
        Image.fromarray(art_premult).filter(ImageFilter.GaussianBlur(8)), dtype=np.float32)
    bloom_a = np.asarray(
        Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(8)),
        dtype=np.float32) / 255.0
    eps = 1e-3
    glow_a = np.clip(bloom_a * bloom, 0.0, 1.0)
    glow_rgb = bloom_rgb / np.maximum(bloom_a[..., None], eps)

    # 5. core (fg, alpha) OVER glow (glow_rgb, glow_a) — straight alpha
    ac, ag = alpha[..., None], glow_a[..., None]
    out_a = ac + ag * (1 - ac)
    out_rgb = np.where(out_a > eps, (fg * ac + glow_rgb * ag * (1 - ac)) / np.maximum(out_a, eps), 0.0)
    out_a2d = out_a[..., 0]

    # 6. crop to content + margin, pad square
    ys, xs = np.where(out_a2d > 0.05)
    if len(ys) == 0:
        raise SystemExit(f"{src}: matte is empty — corners may not be background (art fills them?)")
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    m = int(margin * max(y1 - y0, x1 - x0))
    y0, y1 = max(0, y0 - m), min(h, y1 + m)
    x0, x1 = max(0, x0 - m), min(w, x1 + m)

    if flat is not None:  # legacy: opaque composite onto a color
        comp = out_a2d[..., None] * out_rgb + (1 - out_a2d[..., None]) * flat
        canvas_fill = flat.astype(np.uint8)
        img = np.concatenate([comp, np.full_like(out_a2d[..., None], 255)], axis=2).astype(np.uint8)
        mode = "RGBA"
    else:
        img = np.concatenate([out_rgb, out_a2d[..., None] * 255], axis=2).astype(np.uint8)
        canvas_fill = None
        mode = "RGBA"

    cropped = img[y0:y1, x0:x1]
    ch, cw, _ = cropped.shape
    side = max(ch, cw)
    if canvas_fill is None:
        canvas = np.zeros((side, side, 4), dtype=np.uint8)  # transparent
    else:
        canvas = np.tile(np.append(canvas_fill, 255), (side, side, 1)).astype(np.uint8)
    oy, ox = (side - ch) // 2, (side - cw) // 2
    canvas[oy:oy + ch, ox:ox + cw] = cropped
    out = Image.fromarray(canvas, mode).resize((size, size), Image.LANCZOS)
    a = np.asarray(out)[:, :, 3]
    print(f"{os.path.basename(src)}: grays {g1.mean():.0f}/{g2.mean():.0f} gap {gap:.0f} "
          f"crop {cw}x{ch} alpha {a.min()}/{a.max()} -> {os.path.basename('') or ''}"
          f"{'flat' if flat is not None else 'transparent'}")
    return out


def preview(marks, path, bg=(6, 6, 15), cell=340, pad=24):
    n = len(marks)
    W = n * cell + (n + 1) * pad
    H = cell + 2 * pad + 34
    sheet = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(marks):
        m = im.convert("RGBA").resize((cell, cell), Image.LANCZOS)
        x = pad + i * (cell + pad)
        sheet.paste(m, (x, pad), m)
        d.text((x + cell // 2 - len(name) * 4, pad + cell + 8), name.upper(), fill=(200, 200, 210))
    sheet.save(path)
    print(f"preview -> {path} ({sheet.size[0]}x{sheet.size[1]})")


def main() -> None:
    ap = argparse.ArgumentParser(description="Key logo art to a transparent PNG mark.")
    ap.add_argument("src", nargs="+")
    ap.add_argument("--out", help="output path (single src only)")
    ap.add_argument("--outdir", help="output dir; each src -> <stem>.png")
    ap.add_argument("--size", type=int, default=1024)
    ap.add_argument("--margin", type=float, default=0.06)
    ap.add_argument("--bloom", type=float, default=0.55)
    ap.add_argument("--flat", help="opaque composite onto this #RRGGBB instead of alpha")
    ap.add_argument("--preview", action="store_true", help="also emit a dark-bg contact sheet")
    ap.add_argument("--preview-out", default="_preview_marks.png")
    a = ap.parse_args()

    flat = _hex(a.flat) if a.flat else None
    if a.out and len(a.src) != 1:
        ap.error("--out takes exactly one src; use --outdir for many")

    marks = []
    for src in a.src:
        img = key(src, a.size, a.margin, a.bloom, flat)
        stem = os.path.splitext(os.path.basename(src))[0]
        dst = a.out or (os.path.join(a.outdir, f"{stem}.png") if a.outdir
                        else os.path.splitext(src)[0] + ".png")
        img.save(dst, "PNG")
        marks.append((stem, img))
    if a.preview:
        preview(marks, a.preview_out)


if __name__ == "__main__":
    main()
