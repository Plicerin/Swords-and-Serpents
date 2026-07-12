"""Organized sprite sheet of all gameplay sprites from ROM data.
Labels: a1,a2,a3... for 8x16 frames, then items.
"""

from PIL import Image, ImageDraw, ImageFont
import os

rom = open("Swords and Serpents.bin", "rb").read()

def rom_bytes(addr, count):
    off = (addr - 0x5000) * 2
    return [rom[off + 2*i + 1] for i in range(count)]

# Palette definitions (matching extract_all_sprites.py)
BG = (0, 0, 0, 0)
PAL_ENEMY   = [BG, (220, 80, 60, 255)]
PAL_SERPENT = [BG, (60, 200, 80, 255)]
PAL_EFFECT  = [BG, (255, 220, 60, 255)]
PAL_WIZARD  = [BG, (60, 100, 210, 255)]
PAL_ITEM    = [BG, (255, 200, 100, 255)]

PAL_NAMES = {
    (220,80,60):   "ENEMY (red/orange)",
    (60,200,80):   "SERPENT (green)",
    (255,220,60):  "EFFECT (yellow)",
    (60,100,210):  "WIZARD (blue)",
    (255,200,100): "ITEM (gold)",
}

def get_pal_name(p):
    rgb = p[1][:3]
    return PAL_NAMES.get(rgb, "???")

def card_pixels(data):
    rows = []
    for i in range(8):
        b = data[i] if i < len(data) else 0
        rows.append([(b >> (7 - col)) & 1 for col in range(8)])
    return rows

def render_sprite_16(card0, card1, palette, zoom=6):
    rows = card_pixels(card0) + card_pixels(card1)
    img = Image.new("RGBA", (8*zoom, 16*zoom), (0,0,0,0))
    for y in range(16):
        for x in range(8):
            px = palette[rows[y][x]]
            if px[3] == 0: continue
            for dy in range(zoom):
                for dx in range(zoom):
                    img.putpixel((x*zoom+dx, y*zoom+dy), px)
    return img

def render_item_8(data, palette, zoom=6):
    rows = card_pixels(data[:8])
    img = Image.new("RGBA", (8*zoom, 8*zoom), (0,0,0,0))
    for y in range(8):
        for x in range(8):
            px = palette[rows[y][x]]
            if px[3] == 0: continue
            for dy in range(zoom):
                for dx in range(zoom):
                    img.putpixel((x*zoom+dx, y*zoom+dy), px)
    return img

# ── Sprite definitions ─────────────────────────────────────
# Each 8x16 sprite = 2 cards at sequential ROM addresses.
# Format: (label, name, rom_addr_first_card, palette)
SPRITES_16 = [
    # --- Walkers (Phantom Knight) ---
    ("a1", "phantom_knight_stand", 0x5C1C, PAL_ENEMY),
    ("a2", "phantom_knight_walk",  0x5C2C, PAL_ENEMY),

    # --- Green creature ---
    ("a3", "green_creature_f0",    0x5C9E, PAL_SERPENT),
    ("a4", "green_creature_f1",    0x5CAE, PAL_SERPENT),

    # --- Red creature (desc1) ---
    ("a5", "red_creature_f0",      0x6677, PAL_ENEMY),
    ("a6", "red_creature_f1",      0x6687, PAL_ENEMY),

    # --- Blue creature (desc567) ---
    ("a7", "blue_creature_f0",     0x6760, PAL_WIZARD),
    ("a8", "blue_creature_f1",     0x6770, PAL_WIZARD),

    # --- Effects ---
    ("a9", "spawn_effect_f0",      0x5AE6, PAL_ENEMY),
    ("a10","spawn_effect_f1",      0x5AF6, PAL_ENEMY),

    # --- Projectiles ---
    ("a11","fireball_f0",          0x5C4E, PAL_EFFECT),
    ("a12","fireball_f1",          0x5C5E, PAL_EFFECT),

    # --- Item sprite (desc3) ---
    ("a13","item_sprite_f0",       0x5DE5, PAL_ITEM),
    ("a14","item_sprite_f1",       0x5DF5, PAL_ITEM),
]

# 8x8 item sprites
ITEMS_8 = [
    ("a15", "key_sprite",    [0x03,0x02,0x3e,0x22,0x3e,0x20,0x18,0x00], PAL_ITEM),
    ("a16", "potion_sprite", [0x1c,0x3e,0x3e,0x3e,0x7f,0x7f,0x7f,0x2a], PAL_ITEM),
    ("a17", "scroll_sprite", [0x3c,0x24,0x3c,0x24,0x3c,0x24,0x3c,0x00], PAL_ITEM),
]

ZOOM = 8
CELL_W_16 = 8 * ZOOM + 24
CELL_H_16 = 16 * ZOOM + 36
CELL_W_8  = 8 * ZOOM + 24
CELL_H_8  = 8 * ZOOM + 36
PAD = 16
COLS = 4

# ── Build layout ────────────────────────────────────────────
header_h = 28
section_h = 30

def layout_16(sprites, y0):
    rows = (len(sprites) + COLS - 1) // COLS
    w = COLS * CELL_W_16 + PAD
    h = rows * CELL_H_16 + PAD
    return w, h, y0 + h

def layout_8(sprites, y0):
    rows = (len(sprites) + COLS - 1) // COLS
    w = COLS * CELL_W_8 + PAD
    h = rows * CELL_H_8 + PAD
    return w, h, y0 + h

total_h = header_h + section_h
w_16, h_16, y1 = layout_16(SPRITES_16, total_h)
total_h = y1 + section_h
w_8, h_8, y2 = layout_8(ITEMS_8, total_h)
total_h = y2 + PAD

W = max(w_16, w_8)

sheet = Image.new("RGBA", (W, total_h), (16, 16, 24, 255))
draw = ImageDraw.Draw(sheet)
try:
    font_big = ImageFont.truetype("arial.ttf", 16)
    font_sm  = ImageFont.truetype("arial.ttf", 12)
except:
    font_big = font_sm = ImageFont.load_default()

# Title
draw.text((PAD, 4), "SWORDS & SERPENTS — GAMEPLAY SPRITE SHEET", fill=(255,220,150,255), font=font_big)
y = header_h + 8

# ── Section: 8x16 sprites ───
draw.text((PAD, y), "▸ 8×16 SPRITES (2 cards stacked = 16 rows × 8 px)", fill=(180,200,220,255), font=font_sm)
y += section_h

for i, (label, name, addr, palette) in enumerate(SPRITES_16):
    col = i % COLS
    row = i // COLS
    cx = PAD + col * CELL_W_16
    cy = y + row * CELL_H_16

    card0 = rom_bytes(addr, 8)
    card1 = rom_bytes(addr + 8, 8)
    img = render_sprite_16(card0, card1, palette, ZOOM)
    sheet.paste(img, (cx + 2, cy + 2), img)

    # Border
    draw.rectangle([cx, cy, cx + 8*ZOOM + 3, cy + 16*ZOOM + 3], outline=(80,80,100,255))

    # Palette color swatch
    swatch_size = 8
    sx = cx + 8*ZOOM + 6
    sy = cy + 2
    pc = palette[1]
    draw.rectangle([sx, sy, sx + swatch_size, sy + swatch_size], fill=pc[:3])
    pn = get_pal_name(palette)

    draw.text((cx + 2, cy + 16*ZOOM + 6), f"{label}", fill=(255,255,200,255), font=font_sm)
    draw.text((cx + 2, cy + 16*ZOOM + 20), f"${addr:04X} {name}", fill=(160,160,180,255), font=font_sm)
    draw.text((sx, sy + swatch_size + 2), pn, fill=(140,140,160,255), font=font_sm)

y += ((len(SPRITES_16) + COLS - 1) // COLS) * CELL_H_16 + PAD

# ── Section: 8x8 items ───
draw.text((PAD, y), "▸ 8×8 ITEMS (1 card = 8 rows × 8 px)", fill=(180,200,220,255), font=font_sm)
y += section_h

for i, (label, name, data, palette) in enumerate(ITEMS_8):
    col = i % COLS
    row = i // COLS
    cx = PAD + col * CELL_W_8
    cy = y + row * CELL_H_8

    img = render_item_8(data, palette, ZOOM)
    sheet.paste(img, (cx + 2, cy + 2), img)
    draw.rectangle([cx, cy, cx + 8*ZOOM + 3, cy + 8*ZOOM + 3], outline=(80,80,100,255))

    pc = palette[1]
    draw.rectangle([cx + 8*ZOOM + 6, cy + 2, cx + 8*ZOOM + 14, cy + 10], fill=pc[:3])

    draw.text((cx + 2, cy + 8*ZOOM + 6), f"{label}", fill=(255,255,200,255), font=font_sm)
    draw.text((cx + 2, cy + 8*ZOOM + 20), name, fill=(160,160,180,255), font=font_sm)

sheet.save("sprites/enemy_sprite_sheet.png")
print(f"Saved sprites/enemy_sprite_sheet.png ({sheet.size[0]}x{sheet.size[1]})")

# ── Reference table ─────────────────────────────────────────
print()
print("=" * 70)
print("  SPRITE REFERENCE")
print("=" * 70)
print(f"  {'Label':6s} {'ROM':6s} {'Palette':20s} {'Name'}")
print(f"  {'-----':6s} {'------':6s} {'---------------------':20s} {'----'}")
for label, name, addr, palette in SPRITES_16:
    print(f"  {label:6s} ${addr:04X}  {get_pal_name(palette):20s} {name}")
for label, name, data, palette in ITEMS_8:
    print(f"  {label:6s}  ---    {get_pal_name(palette):20s} {name}")
