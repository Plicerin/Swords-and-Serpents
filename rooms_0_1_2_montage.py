#!/usr/bin/env python3
"""Stitch rooms 0, 1, and 2 into a single labeled PNG."""
import os
from PIL import Image, ImageDraw, ImageFont

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOMS_DIR = os.path.join(PROJECT_DIR, "sprites", "rooms")
OUT_PATH = os.path.join(PROJECT_DIR, "rooms_0_1_2.png")

ROOM_W, ROOM_H = 1280, 768
LABEL_H = 52
GAP = 4
BORDER = 12

# 3 rooms side-by-side
canvas_w = BORDER * 2 + 3 * ROOM_W + 2 * GAP
canvas_h = BORDER * 2 + ROOM_H + LABEL_H

canvas = Image.new("RGB", (canvas_w, canvas_h), (7, 8, 12))
draw = ImageDraw.Draw(canvas)

font = None
for fp in ["C:\\Windows\\Fonts\\segoeui.ttf",
           "C:\\Windows\\Fonts\\consola.ttf",
           "C:\\Windows\\Fonts\\cour.ttf"]:
    if os.path.exists(fp):
        try:
            font = ImageFont.truetype(fp, 26)
            break
        except Exception:
            continue

for idx, room_num in enumerate([0, 1, 2]):
    x = BORDER + idx * (ROOM_W + GAP)
    y = BORDER

    # Header
    draw.rectangle([(x, y), (x + ROOM_W - 1, y + LABEL_H - 1)], fill=(16, 18, 26), outline=(40, 42, 55), width=1)
    label = f"Room {room_num}"
    if font:
        draw.text((x + 16, y + 7), label, fill=(242, 215, 164), font=font)
    else:
        draw.text((x + 16, y + 10), label, fill=(242, 215, 164))

    # Room image
    png_path = os.path.join(ROOMS_DIR, f"room_{room_num}.png")
    if os.path.exists(png_path):
        room_img = Image.open(png_path)
        canvas.paste(room_img, (x, y + LABEL_H))
        draw.rectangle([(x, y + LABEL_H), (x + ROOM_W - 1, y + LABEL_H + ROOM_H - 1)], outline=(40, 42, 55), width=1)
    else:
        draw.rectangle([(x, y + LABEL_H), (x + ROOM_W - 1, y + LABEL_H + ROOM_H - 1)], fill=(20, 22, 32), outline=(60, 0, 0), width=2)
        draw.text((x + ROOM_W // 2 - 60, y + LABEL_H + ROOM_H // 2 - 12), "MISSING", fill=(200, 60, 60))

canvas.save(OUT_PATH)
print(f"Saved: {OUT_PATH} ({canvas_w}×{canvas_h})")
