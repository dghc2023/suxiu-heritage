# -*- coding: utf-8 -*-
"""把页面用到的 PNG 压成 WebP，明显减小手机加载体积。"""
from pathlib import Path
from PIL import Image

BASE = Path(__file__).resolve().parent.parent
IMG = BASE / "images"

# 文件名 -> 最大宽度（按页面实际显示尺寸留余量）
TARGETS = {
    "hero.png": 1600,
    "step1-split.png": 1100,
    "step2-frame.png": 1100,
    "step3-needle.png": 1100,
    "step4-finish.png": 1100,
    "double-sided.png": 1600,
    "texture.png": 1400,
}

total_before = total_after = 0
for name, max_w in TARGETS.items():
    src = IMG / name
    if not src.exists():
        print("missing", src)
        continue
    im = Image.open(src).convert("RGB")
    if im.width > max_w:
        h = round(im.height * max_w / im.width)
        im = im.resize((max_w, h), Image.LANCZOS)
    out = src.with_suffix(".webp")
    im.save(out, "WEBP", quality=82, method=6)
    b, a = src.stat().st_size, out.stat().st_size
    total_before += b
    total_after += a
    print(f"{name:18s} {b/1024:7.0f} KB -> {out.name:18s} {a/1024:6.0f} KB  ({im.width}x{im.height})")

print(f"\nTOTAL {total_before/1024/1024:.1f} MB -> {total_after/1024/1024:.2f} MB")