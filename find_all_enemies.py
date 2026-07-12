"""Dump EVERY card cluster in the ROM sprite region.
Renders all 8x16 frames as a sprite sheet labeled by ROM address only.
"""

from PIL import Image, ImageDraw, ImageFont

rom = open("Swords and Serpents.bin", "rb").read()

def rom_lo(addr):
    off = (addr - 0x5000) * 2
    return rom[off + 1] if off + 1 < len(rom) else 0

def card_pixels(addr):
    return [[(rom_lo(addr + i) >> (7 - x)) & 1 for x in range(8)] for i in range(8)]

REGIONS = [
    (0x5A00, 0x5D00),
    (0x5DE0, 0x5E40),
    (0x6600, 0x6800),
]

all_frames_16 = []

for rstart, rend in REGIONS:
    addr = rstart
    while addr + 16 <= rend:
        # Check if this 2-card group has any data
        has_data = any(rom_lo(addr + c) != 0 for c in range(16))
        if has_data:
            all_frames_16.append(addr)
        addr += 8  # slide by 1 card so we don't miss offset frames

# Deduplicate frames that start at the same address
# Also add single-card head/tail check
seen = set()
unique_frames = []
for addr in all_frames_16:
    if addr not in seen:
        seen.add(addr)
        unique_frames.append(addr)
unique_frames.sort()

print(f"Found {len(unique_frames)} potential 8x16 sprite frames in the regions")
for addr in unique_frames:
    nxt = addr + 2
    is_double = nxt in seen
    c0 = " ".join(f"{rom_lo(addr+i):02X}" for i in range(8))
    c1 = " ".join(f"{rom_lo(addr+8+i):02X}" for i in range(8))
    print(f"  ${addr:04X}: {c0} | {c1}")

ZOOM = 6
COLS = 5
PAD = 8
CELL_W = 8 * ZOOM + PAD + 50
CELL_H = 16 * ZOOM + 20
ROWS = (len(unique_frames) + COLS - 1) // COLS
W = COLS * CELL_W + PAD
H = ROWS * CELL_H + PAD + 20

sheet = Image.new("RGBA", (W, H), (16, 16, 24, 255))
draw = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype("arial.ttf", 11)
except:
    font = ImageFont.load_default()

draw.text((PAD, 2), "ALL SPRITE FRAMES (8x16) IN $5A00-$5CFF, $5DE0-$5E3F, $6600-$67FF", fill=(200,180,140,255), font=font)

for i, addr in enumerate(unique_frames):
    col = i % COLS
    row = i // COLS
    cx = PAD + col * CELL_W
    cy = 20 + row * CELL_H
    rows0 = card_pixels(addr)
    rows1 = card_pixels(addr + 8)
    all_rows = rows0 + rows1
    for y in range(16):
        for x in range(8):
            if all_rows[y][x]:
                for dy in range(ZOOM):
                    for dx in range(ZOOM):
                        sheet.putpixel((cx + x*ZOOM + dx, cy + y*ZOOM + dy), (220,220,220,255))
    draw.rectangle([cx, cy, cx + 8*ZOOM, cy + 16*ZOOM], outline=(80,80,100,255))
    draw.text((cx + 8*ZOOM + 4, cy + 4), f"${addr:04X}", fill=(180,180,200,255), font=font)

sheet.save("sprites/all_frames.png")
print(f"\nSaved sprites/all_frames.png")

# Also print ASCII art
print("\n=== ASCII ART ===")
for addr in unique_frames:
    r0 = card_pixels(addr)
    r1 = card_pixels(addr + 8)
    print(f"\n${addr:04X}:")
    for row in r0 + r1:
        print("  " + "".join("#" if p else "." for p in row))
