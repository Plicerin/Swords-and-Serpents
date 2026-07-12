"""
Swords & Serpents — Comprehensive Sprite Extractor
====================================================
Extracts ALL sprite cards from ROM using verified addresses from
jzIntv debugger breakpoints at $5249 (direct sprite upload path).

Sprite Categories:
  TITLE:  Warrior/Wizard (ROM $62DE-$6317) + RLE cards ($61E7)
  GAME:   Enemies, dragon/serpent, projectiles, effects

Key insight: All sprites are 1bpp (1 bit per pixel). Each ROM
DECLE stores 8 pixels in the lo byte (hi byte = 0x00 for pixel data).
The foreground color comes from the MOB color register.
"""

import re
from PIL import Image, ImageDraw, ImageFont

# ── Load ROM ────────────────────────────────────────────────
rom = open("Swords and Serpents.bin", "rb").read()

def rom_bytes(addr, count):
    """Read count bytes from ROM at logical address.
    Each ROM DECLE stores 8-bit data in the lo byte."""
    off = (addr - 0x5000) * 2
    result = []
    for i in range(count):
        pos = off + 2*i + 1  # lo byte of each 16-bit word
        if pos < len(rom):
            result.append(rom[pos])
        else:
            result.append(0)
    return result

def rom_decile(addr):
    """Read a full 16-bit DECLE word from ROM."""
    off = (addr - 0x5000) * 2
    if off + 1 < len(rom):
        return (rom[off] << 8) | rom[off + 1]
    return 0

# ── RLE Decompressor ($61E7: L_53EA) ───────────────────────
def rle_decode(start_addr):
    """Decode RLE-compressed sprite data using the L_53EA algorithm."""
    gram_off = rom_decile(start_addr)
    count = rom_decile(start_addr + 1)
    result = []
    for i in range(count):
        entry = rom_decile(start_addr + 2 + i)
        byte_val = entry & 0xFF
        repeat = ((entry >> 8) & 0x03) + 1
        result.extend([byte_val] * repeat)
    return gram_off, result

# ── Palettes (transparent + foreground) ─────────────────────
BG = (0, 0, 0, 0)
PAL_WARRIOR  = [BG, (235, 230, 220, 255)]  # white/silver
PAL_WIZARD   = [BG, (60, 100, 210, 255)]    # blue robes
PAL_SERPENT  = [BG, (60, 200, 80, 255)]     # green dragon
PAL_ENEMY    = [BG, (220, 80, 60, 255)]     # red/orange enemy
PAL_EFFECT   = [BG, (255, 220, 60, 255)]    # yellow effect
PAL_ITEM     = [BG, (255, 200, 100, 255)]   # gold item
PAL_REF      = [BG, (255, 200, 100, 255)]   # reference render

# ── Rendering helpers (1bpp) ────────────────────────────────
def card_pixels(data):
    """Convert 8 bytes → 8×8 array of pixel values (0=bg, 1=fg)."""
    rows = []
    for i in range(8):
        b = data[i] if i < len(data) else 0
        rows.append([(b >> (7 - col)) & 1 for col in range(8)])
    return rows

def card_image(data, palette, zoom=10):
    """Render a single 8×8 card as PIL Image at zoom scale."""
    px = card_pixels(data)
    img = Image.new("RGBA", (8, 8))
    for y in range(8):
        for x in range(8):
            img.putpixel((x, y), palette[px[y][x]])
    if zoom > 1:
        img = img.resize((8*zoom, 8*zoom), Image.NEAREST)
    return img

def ascii_card(data):
    """Render card as ASCII art."""
    chars = {0: ".", 1: "#"}
    px = card_pixels(data)
    return "\n".join("".join(chars[p] for p in row) for row in px)

def data_hex(data):
    return " ".join(f"{b:02X}" for b in data)

def find_card_boundary(addr, max_cards=16):
    """Find how many consecutive non-empty cards exist starting at addr.
    A card is empty if all 8 bytes are zero. Stops at first empty card.
    Also stops if address exceeds ROM bounds."""
    cards = []
    rom_end = 0x5000 + len(rom) // 2  # ROM end in logical addresses
    for ci in range(max_cards):
        card_addr = addr + ci * 8
        if card_addr >= rom_end:
            break
        rows = rom_bytes(card_addr, 8)
        if all(b == 0 for b in rows):
            break
        cards.append(rows)
    return cards

# ── Sprite Definitions ──────────────────────────────────────
# Format: (name, category, rom_addr, max_cards, palette, notes)

SPRITES = [
    # === TITLE SCREEN: Warrior (White Knight) ===
    # Verified against jzIntv title screen GRAM dump
    ("warrior_head",     "TITLE", 0x62DE, 1, PAL_WARRIOR, "Warrior head/body (GRAM card 1, verified)"),
    ("warrior_side",     "TITLE", 0x6300, 1, PAL_WARRIOR, "Warrior side frame (GRAM card 2, verified)"),
    # Feet card is RLE-decoded (shared with wizard)

    # === TITLE SCREEN: Wizard (Blue Robe) ===
    # ROM-inferred from sliding-window layout
    ("wizard_head",      "TITLE", 0x6302, 1, PAL_WIZARD, "Wizard head/body (ROM-inferred)"),
    ("wizard_side",      "TITLE", 0x630A, 1, PAL_WIZARD, "Wizard side frame (ROM-inferred)"),

    # === GAMEPLAY: Dragon/Serpent (large, multi-card) ===
    # Captured at $5249: R4=$5BCE → GRAM cards 48-57+
    # Descriptor $5B28 word2+3 = $5BCE
    ("dragon",           "GAME",  0x5BCC, 10, PAL_SERPENT, "Dragon/serpent (10 cards, from jzIntv $5249 capture)"),

    # === GAMEPLAY: Enemy character ===
    # Captured at $5249: R4=$5C1E → GRAM cards 54-57
    ("enemy_char",       "GAME",  0x5C1C, 4, PAL_ENEMY, "Enemy humanoid (4 cards, from jzIntv $5249 capture)"),

    # === GAMEPLAY: Animated sprite (frame A) ===
    # Captured at $5249: R4=$5AE8 → GRAM cards 52-55
    ("anim_sprite_a",    "GAME",  0x5AE6, 4, PAL_ENEMY, "Animated sprite frame A (4 cards)"),

    # === GAMEPLAY: Animated sprite (frame B) ===
    # Captured at $5249: R4=$5CA0 → GRAM cards 52-55
    ("anim_sprite_b",    "GAME",  0x5C9E, 4, PAL_SERPENT, "Animated sprite frame B (4 cards)"),

    # === GAMEPLAY: Projectile / Effect ===
    # Captured at $5249: R4=$5C50 → GRAM card 50
    ("projectile",       "GAME",  0x5C4E, 4, PAL_EFFECT, "Projectile/effect (4 sparse cards)"),

    # === DESCRIPTOR TARGETS (not captured at $5249, but in ROM) ===
    # Descriptor $5B34 → ptr $5DE7
    ("desc3_sprite",     "GAME",  0x5DE5, 4, PAL_ITEM, "Descriptor $5B34 target (4 cards)"),
    # Descriptor $5B2C → ptr $6679
    ("desc1_sprite",     "GAME",  0x6677, 4, PAL_ENEMY, "Descriptor $5B2C target (4 cards)"),
    # Descriptors $5B3C-$5B44 -> ptr $6762
    ("desc567_sprite",   "GAME",  0x6760, 4, PAL_WIZARD, "Descriptor $5B3C-44 target (4 cards)"),

    # === Trailing sprite data at end of $5B00-$5CCF region ===
    ("trailing_data",    "GAME",  0x5CBE, 3, PAL_REF, "Unidentified trailing data (3 cards)"),
]

# ── Decode RLE block ────────────────────────────────────────
rle_gram_off, rle_bytes = rle_decode(0x61E7)
rle_cards_list = [rle_bytes[i*8:(i+1)*8] for i in range(len(rle_bytes) // 8)]
# Card 0 of RLE is the shared feet card
feet_card = rle_cards_list[0]

# ── ASCII Art Display ───────────────────────────────────────
print("=" * 70)
print("  SWORDS & SERPENTS — COMPREHENSIVE SPRITE EXTRACTOR")
print("=" * 70)

print(f"\nROM size: {len(rom)} bytes")
print(f"RLE blocks: {len(rle_cards_list)} cards from ${0x61E7:04X}")
print(f"Defined sprites: {len(SPRITES)}")

# Show each sprite
for name, category, addr, max_cards, palette, notes in SPRITES:
    cards = find_card_boundary(addr, max_cards)
    total_px = sum(sum(bin(b).count('1') for b in c) for c in cards)
    
    print(f"\n-- {name.upper()} ({category}) --")
    print(f"  ROM: ${addr:04X}, {len(cards)} card(s), {total_px} total pixels")
    print(f"  {notes}")
    for ci, card_data in enumerate(cards):
        print(f"  Card {ci} (${addr + ci*8:04X}): {data_hex(card_data)}")
        for line in ascii_card(card_data).split("\n"):
            print(f"    {line}")

# RLE summary
print(f"\n-- RLE DATA (${0x61E7:04X}) --")
print(f"  GRAM offset: ${rle_gram_off:04X} (card {rle_gram_off // 8})")
print(f"  Entries: {rom_decile(0x61E8)}")
print(f"  Decompressed: {len(rle_bytes)} bytes = {len(rle_cards_list)} cards")
print(f"\n  FEET CARD (shared warrior/wizard, GRAM card 3):")
print(f"  {data_hex(feet_card)}")
for line in ascii_card(feet_card).split("\n"):
    print(f"    {line}")
# Show first 6 RLE cards
for ci in range(min(6, len(rle_cards_list))):
    cd = rle_cards_list[ci]
    print(f"\n  RLE Card {ci} (GRAM {rle_gram_off // 8 + ci}): {data_hex(cd)}")

# ── Render PNGs ─────────────────────────────────────────────
import os
os.makedirs("sprites", exist_ok=True)

ZOOM = 12
CARD_PX = 8 * ZOOM
GAP = 16

def render_sprite_strip(name, cards, palette, zoom=ZOOM):
    """Render a horizontal strip of cards with labels."""
    n = len(cards)
    if n == 0:
        return None
    strip_w = n * (CARD_PX + GAP) + 30
    strip_h = CARD_PX + 40
    img = Image.new("RGBA", (strip_w, strip_h), (10, 10, 20, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 11)
    except Exception:
        font = ImageFont.load_default()
    for i, data in enumerate(cards):
        x = 15 + i * (CARD_PX + GAP)
        ci = card_image(data, palette, zoom)
        img.paste(ci, (x, 8), ci)
        draw.text((x + 2, CARD_PX + 12), f"C{i}", fill=(200, 200, 200, 255), font=font)
    return img

def render_sprite_grid(name, cards, palette, zoom=ZOOM, cols=4):
    """Render cards in a grid."""
    n = len(cards)
    if n == 0:
        return None
    rows = (n + cols - 1) // cols
    grid_w = cols * (CARD_PX + GAP) + 20
    grid_h = rows * (CARD_PX + GAP) + 40
    img = Image.new("RGBA", (grid_w, grid_h), (10, 10, 20, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 10)
    except Exception:
        font = ImageFont.load_default()
    
    draw.text((10, 4), name, fill=(255, 220, 150, 255), font=font)
    for i, data in enumerate(cards):
        col = i % cols
        row = i // cols
        x = 10 + col * (CARD_PX + GAP)
        y = 20 + row * (CARD_PX + GAP)
        ci = card_image(data, palette, zoom)
        img.paste(ci, (x, y), ci)
        draw.text((x + 2, y + 2), f"{i}", fill=(255, 255, 255, 180), font=font)
    return img

print("\n-- RENDERING SPRITES --")

rendered = 0
for name, category, addr, max_cards, palette, notes in SPRITES:
    cards = find_card_boundary(addr, max_cards)
    if not cards:
        print(f"  SKIP {name}: no pixel data")
        continue
    
    # Use strip for <=4 cards, grid for >4
    if len(cards) <= 4:
        img = render_sprite_strip(name, cards, palette)
    else:
        img = render_sprite_grid(name, cards, palette, cols=min(8, len(cards)))
    
    if img:
        fname = f"sprites/{name}.png"
        img.save(fname)
        print(f"  Saved {fname} ({len(cards)} cards)")
        rendered += 1

# RLE cards grid
rle_img = render_sprite_grid("RLE Cards (GRAM 3-33)", rle_cards_list, PAL_REF, cols=8)
if rle_img:
    rle_img.save("sprites/rle_all_cards.png")
    print(f"  Saved sprites/rle_all_cards.png ({len(rle_cards_list)} cards)")
    rendered += 1

# Warrior + feet composite
warrior_cards = [
    rom_bytes(0x62DE, 8),  # head
    rom_bytes(0x6300, 8),  # side
    feet_card,              # feet
]
warrior_strip = render_sprite_strip("WARRIOR (white knight)", warrior_cards, PAL_WARRIOR)
if warrior_strip:
    warrior_strip.save("sprites/warrior_complete.png")
    print(f"  Saved sprites/warrior_complete.png (3 cards)")
    rendered += 1

# Wizard + feet composite
wizard_cards = [
    rom_bytes(0x6302, 8),  # head
    rom_bytes(0x630A, 8),  # side
    feet_card,              # feet (shared)
]
wizard_strip = render_sprite_strip("WIZARD (blue robe)", wizard_cards, PAL_WIZARD)
if wizard_strip:
    wizard_strip.save("sprites/wizard_complete.png")
    print(f"  Saved sprites/wizard_complete.png (3 cards)")
    rendered += 1

# ── Master Sprite Atlas ─────────────────────────────────────
# Combine all sprites into a labeled atlas
print("\n-- BUILDING MASTER ATLAS --")

all_sprite_data = []
# Add warrior/wizard
all_sprite_data.append(("WARRIOR", PAL_WARRIOR, warrior_cards))
all_sprite_data.append(("WIZARD", PAL_WIZARD, wizard_cards))
# Add all gameplay sprites
for name, category, addr, max_cards, palette, notes in SPRITES:
    cards = find_card_boundary(addr, max_cards)
    if cards:
        all_sprite_data.append((name.upper(), palette, cards))

# Calculate atlas size
MAX_COLS = 12
col_w = CARD_PX + GAP
row_h = CARD_PX + 48  # card + label area

# Layout items
layout = []
x, y = 10, 10
max_y = 0
for label, palette, cards in all_sprite_data:
    n = len(cards)
    width = n * col_w
    if x + width > MAX_COLS * col_w and x > 10:
        x = 10
        y = max_y + 20
    layout.append((label, palette, cards, x, y))
    x += width + 30
    max_y = max(max_y, y + row_h)

atlas_w = MAX_COLS * col_w + 40
atlas_h = max_y + row_h + 20
atlas = Image.new("RGBA", (atlas_w, atlas_h), (8, 8, 16, 255))
draw = ImageDraw.Draw(atlas)
try:
    label_font = ImageFont.truetype("arial.ttf", 11)
except Exception:
    label_font = ImageFont.load_default()

for label, palette, cards, lx, ly in layout:
    draw.text((lx, ly - 2), label, fill=(255, 220, 150, 255), font=label_font)
    for ci, data in enumerate(cards):
        cx = lx + ci * col_w
        cy = ly + 16
        ci_img = card_image(data, palette, ZOOM)
        atlas.paste(ci_img, (cx, cy), ci_img)
        draw.text((cx + 2, cy + CARD_PX + 2), f"{ci}", fill=(180, 180, 200, 255), font=label_font)

atlas.save("sprites/master_atlas.png")
print(f"  Saved sprites/master_atlas.png ({atlas_w}x{atlas_h})")
rendered += 1

print(f"\nDone! Rendered {rendered} files to sprites/")
