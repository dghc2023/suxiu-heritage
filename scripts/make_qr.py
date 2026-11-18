# -*- coding: utf-8 -*-
"""生成苏绣页面二维码海报：AI 背景图 + 二维码卡片 + 文字。"""
from io import BytesIO
from pathlib import Path

import segno
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = Path(__file__).resolve().parent.parent
URL = "https://dghc2023.github.io/suxiu-heritage/"
BG = BASE / "qr" / "bg-suxiu.png"
OUT = BASE / "qr" / "suxiu-qr-poster.png"

INK = "#17130F"
MUTED = "#7A7065"
ACCENT = "#A63A32"
CARD = "#FBF7EE"
LINE = "#D9CFBC"

bg = Image.open(BG).convert("RGB")
W, H = bg.size
canvas = bg.copy()
draw = ImageDraw.Draw(canvas)

# --- 二维码，按整数倍缩放保证清晰 ---
qr = segno.make(URL, error="h")
modules_w, _ = qr.symbol_size(scale=1, border=4)
scale = max(1, 520 // modules_w)
buf = BytesIO()
qr.save(buf, kind="png", scale=scale, border=4, dark=INK, light=CARD)
buf.seek(0)
qr_img = Image.open(buf).convert("RGB")
qrw, qrh = qr_img.size

# --- 卡片尺寸与位置 ---
pad = 40
cw, ch = qrw + pad * 2, qrh + pad * 2
cx = (W - cw) // 2
cy = 790

# 阴影
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow)
sd.rounded_rectangle([cx, cy + 12, cx + cw, cy + ch + 12], radius=30, fill=(23, 19, 15, 70))
shadow = shadow.filter(ImageFilter.GaussianBlur(20))
canvas = Image.alpha_composite(canvas.convert("RGBA"), shadow).convert("RGB")
draw = ImageDraw.Draw(canvas)

# 卡片
draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=30, fill=CARD, outline=LINE, width=2)
canvas.paste(qr_img, (cx + pad, cy + pad))

# --- 文字 ---
f_eyebrow = ImageFont.truetype(r"C:\Windows\Fonts\msyhbd.ttc", 22)
f_title = ImageFont.truetype(r"C:\Windows\Fonts\STZHONGS.TTF", 58)
f_sub = ImageFont.truetype(r"C:\Windows\Fonts\simsun.ttc", 26)
f_small = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 22)

draw.text((W // 2, 606), "非 遗 · 苏 绣", font=f_eyebrow, fill=ACCENT, anchor="mm")
draw.text((W // 2, 668), "扫码 · 看苏绣", font=f_title, fill=INK, anchor="mm")
draw.text((W // 2, 728), "一针一线，把江南绣进丝里", font=f_sub, fill=MUTED, anchor="mm")
draw.text((W // 2, 1450), "苏绣非遗科普页 · 扫码打开", font=f_small, fill=MUTED, anchor="mm")

canvas.save(OUT, "PNG")
print("saved", OUT, canvas.size, "qr modules", modules_w, "qr px", qrw)

# --- 自检：解码二维码 ---
import cv2
import numpy as np

qr_img.save(BASE / "qr" / "qr-raw.png")
raw_bgr = cv2.cvtColor(np.array(qr_img), cv2.COLOR_RGB2BGR)
detector = cv2.QRCodeDetector()
d1, p1, _ = detector.detectAndDecode(raw_bgr)
print("raw decoded:", repr(d1))
found, corners = detector.detect(raw_bgr)
print("raw detect:", found, corners)

arr = np.fromfile(str(OUT), dtype=np.uint8)
img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
d2, p2, _ = detector.detectAndDecode(img)
print("poster decoded:", repr(d2))
print("match:", d1 == URL or d2 == URL)