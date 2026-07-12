#!/usr/bin/env python3
"""
Stitch all 6 dungeon room renders into a single montage PNG.
Layout: 3 columns × 2 rows, with room labels and a separator grid.
"""
import os
from PIL import Image, ImageDraw, ImageFont

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOMS_DIR = os.path.join(PROJECT_DIR, "sprites", "rooms")
OUT_PATH  = os.path.join(PROJECT_DIR, "sprites", "rooms", "dungeon_montage.png")

ROOM_W, ROOM_H = 1280, 768
COLS, ROWS = 3, 2
LABEL_H = 52       # header strip per room
GAP = 4            # gap between rooms
BORDER = 12        # outer border

# Total canvas size
canvas_w = BORDER * 2 + COLS * ROOM_W + (COLS - 1) * GAP
canvas_h = BORDER * 2 + ROWS * (ROOM_H + LABEL_H) + (ROWS - 1) * GAP

# Dark background
canvas = Image.new("RGB", (canvas_w, canvas_h), (7, 8, 12))
draw = ImageDraw.Draw(canvas)

# Try to get a nice font, fall back to default
font = None
font_small = None
for fp in ["C:\\Windows\\Fonts\\segoeui.ttf",
           "C:\\Windows\\Fonts\\seguiemj.ttf",
           "C:\\Windows\\Fonts\\cour.ttf",
           "C:\\Windows\\Fonts\\consola.ttf"]:
    if os.path.exists(fp):
        try:
            font = ImageFont.truetype(fp, 26)
            font_small = ImageFont.truetype(fp, 16)
            break
        except Exception:
            continue

# Header colors per room (subtle gold/bronze tones)
HEADER_BG = (16, 18, 26)
HEADER_TEXT = (242, 215, 164)      # gold
HEADER_ACCENT = (177, 160, 232)    # lavender

# MOB summary from the renders (for subtitles)
MOB_SUMMARIES = {
    0: "2 MOBs — player + enemy",
    1: "Empty room",
    2: "3 MOBs — guards",
    3: "2 MOBs — guards",
    4: "1 MOB — boss?",
    5: "Empty room",
}

for idx in range(6):
    row = idx // COLS
    col = idx % COLS

    x = BORDER + col * (ROOM_W + GAP)
    y = BORDER + row * (ROOM_H + LABEL_H + GAP)

    # Draw header background
    header_rect = [(x, y), (x + ROOM_W - 1, y + LABEL_H - 1)]
    draw.rectangle(header_rect, fill=HEADER_BG, outline=(40, 42, 55), width=1)

    # Room number and label
    label = f"Room {idx}"
    if font:
        draw.text((x + 16, y + 7), label, fill=HEADER_TEXT, font=font)
        if idx in MOB_SUMMARIES:
            draw.text((x + 16, y + 31), MOB_SUMMARIES[idx], fill=HEADER_ACCENT, font=font_small)
    else:
        draw.text((x + 16, y + 10), label, fill=HEADER_TEXT)
        if idx in MOB_SUMMARIES:
            draw.text((x + 16, y + 34), MOB_SUMMARIES[idx], fill=HEADER_ACCENT)

    # Paste the room image below the header
    png_path = os.path.join(ROOMS_DIR, f"room_{idx}.png")
    if os.path.exists(png_path):
        room_img = Image.open(png_path)
        canvas.paste(room_img, (x, y + LABEL_H))

        # Thin border around the room image
        room_rect = [(x, y + LABEL_H), (x + ROOM_W - 1, y + LABEL_H + ROOM_H - 1)]
        draw.rectangle(room_rect, outline=(40, 42, 55), width=1)
    else:
        # Placeholder if missing
        ph = [(x, y + LABEL_H), (x + ROOM_W - 1, y + LABEL_H + ROOM_H - 1)]
        draw.rectangle(ph, fill=(20, 22, 32), outline=(60, 0, 0), width=2)
        draw.text((x + ROOM_W // 2 - 60, y + LABEL_H + ROOM_H // 2 - 12),
                  "MISSING", fill=(200, 60, 60))

canvas.save(OUT_PATH)
print(f"Saved: {OUT_PATH} ({canvas_w}×{canvas_h})")

# Also print per-room file info
total_bytes = 0
for idx in range(6):
    p = os.path.join(ROOMS_DIR, f"room_{idx}.png")
    if os.path.exists(p):
        sz = os.path.getsize(p)
        total_bytes += sz
        print(f"  room_{idx}.png: {sz:,} bytes")
print(f"  Total: {total_bytes:,} bytes -> montage: {os.path.getsize(OUT_PATH):,} bytes")
