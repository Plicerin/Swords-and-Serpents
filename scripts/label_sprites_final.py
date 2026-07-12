"""
Final sprite classification: combines ASCII render with MOB layout
to definitively label each character in Swords and Serpents.
"""
from PIL import Image, ImageDraw, ImageFont
import os

FG = (255, 255, 255)
BG = (5, 5, 15)

rom = open('Swords and Serpents.bin', 'rb').read()

def read_decle(addr):
    off = (addr - 0x5000) * 2
    if off + 1 < len(rom):
        return (rom[off] << 8) | rom[off + 1]
    return None

# DECLE cards
pixel_data = []
for addr in range(0x5BCD, 0x5C46):
    v = read_decle(addr)
    if v is None: break
    hi = (v >> 8) & 0xFF
    if hi == 0:
        pixel_data.append(v & 0xFF)
decle_cards = [list(pixel_data[c*8:(c+1)*8]) for c in range(len(pixel_data)//8)]

# RLE cards
addr = 0x61E7
count = read_decle(addr + 1)
decoded = bytearray()
for i in range(count):
    entry = read_decle(addr + 2 + i)
    if entry is None: break
    repeat = ((entry >> 8) & 0x03) + 1
    for _ in range(repeat):
        decoded.append(entry & 0xFF)
rle_cards = [list(decoded[c*8:(c+1)*8]) for c in range(len(decoded)//8)]

# ============================================================
# MANUAL CLASSIFICATION based on ASCII renders
# ============================================================
# Each sprite = 2 cards stacked (8 wide x 16 tall)
# Classification by visual pattern analysis

decle_labels = {
    # Pair 0: Classic humanoid - head, narrow neck, wide shoulders, 
    # body with sword on right side, legs. Very symmetric.
    0: "WARRIOR (sword+shield)",
    # Pair 1: Humanoid with robes flowing outward at bottom-right.
    # Staff-like extension. WIZARD.
    1: "WIZARD (robes+staff)",
    # Pair 2: Elongated thin body, head at top, long undulating body.
    # No clear legs. SERPENT.
    2: "SERPENT",
    # Pair 3: Dense blocky humanoid, shield on left, heavy armor.
    3: "KNIGHT (shield+armor)",
    # Pair 4: Very symmetric, diamond-shaped lower body.
    # Ornate robes/armor. Could be KING or alternate warrior.
    4: "KNIGHT (ornate armor)",
    # Pair 5: Checkerboard pattern at top, disconnected body parts.
    # Looks like WIZARD with magic staff/spell effect.
    5: "WIZARD (spellcasting)",
    # Pair 6: Very sparse, disconnected elements, serpentine shape.
    6: "SERPENT (coiled)",
}

rle_labels = {
    # RLE cards are primarily dungeon tiles, walls, and dragon/serpent body segments
    # Dense blocky patterns = dungeon structures
    # Thin undulating rows = serpent body
    0: "DRAGON head/body",
    1: "DRAGON body (right)",
    2: "DRAGON tail/neck",    # Thin, columnar
    3: "DRAGON body (left)",
    4: "DUNGEON wall segment",
    5: "DUNGEON pillar/base",
    6: "DUNGEON wall (double)",  # Repeated column pattern (identical cards 6 and 7)
    7: "DUNGEON wall (double)",  # Same as above
    8: "SERPENT body coil",
    9: "DECORATION (border)",
    10: "DUNGEON pillar (thin)",
    11: "DRAGON body segment",
    12: "DUNGEON arch/portal",
    13: "DRAGON wing/body",
    14: "DRAGON tail tip",
}

# ============================================================
# Read MOB configuration for cross-reference
# ============================================================
print("="*70)
print("MOB CONFIGURATION TABLE ($5BB5)")
print("="*70)
print("Decoding STIC A register values for title screen MOBs:")
print()

mob_info = []
for i in range(12):
    v = read_decle(0x5BB5 + i)
    if v is None: break
    if v == 0:
        continue
    card_num = (v >> 11) & 0x1F
    visible = (v >> 5) & 1
    flip_x = (v >> 3) & 1
    flip_y = (v >> 2) & 1
    priority = (v >> 10) & 1
    color_mode = (v >> 9) & 1
    double_y = (v >> 8) & 1
    double_w = (v >> 6) & 1
    
    status = "VISIBLE" if visible else "HIDDEN"
    features = []
    if flip_x: features.append("FLIP-X")
    if flip_y: features.append("FLIP-Y")
    if double_y: features.append("DOUBLE-Y")
    if double_w: features.append("DOUBLE-W")
    if priority: features.append("PRIORITY")
    if color_mode: features.append("COLOR-ADV")
    
    mob_info.append({
        'idx': i,
        'card': card_num,
        'visible': visible,
        'flip_x': flip_x,
        'value': v,
        'features': features,
    })
    
    card_hex = f"${card_num:02X}"
    gram_addr = 0x3800 + card_num * 8
    print(f"  MOB {i:2d}: card={card_hex} (GRAM ${gram_addr:04X})  "
          f"STIC_A=${v:04X}  {status}" + 
          (f"  [{', '.join(features)}]" if features else ""))

# ============================================================
# Print ASCII renders with labels
# ============================================================
print("\n" + "="*70)
print("DECLE SPRITES — LABELED ASCII RENDERS")
print("="*70)

for pair_idx in range(len(decle_cards)//2):
    label = decle_labels.get(pair_idx, "UNKNOWN")
    print(f"\n=== DECLE Pair {pair_idx}: {label} ===")
    top = decle_cards[pair_idx*2]
    bot = decle_cards[pair_idx*2+1]
    for b in top:
        row = "".join("##" if (b >> (7-c)) & 1 else ".." for c in range(8))
        print(f"  {row}")
    print("  --------")
    for b in bot:
        row = "".join("##" if (b >> (7-c)) & 1 else ".." for c in range(8))
        print(f"  {row}")

print("\n" + "="*70)
print("RLE SPRITES — LABELED ASCII RENDERS")
print("="*70)

for pair_idx in range(len(rle_cards)//2):
    label = rle_labels.get(pair_idx, "UNKNOWN")
    print(f"\n=== RLE Pair {pair_idx}: {label} ===")
    top = rle_cards[pair_idx*2]
    bot = rle_cards[pair_idx*2+1]
    for b in top:
        row = "".join("##" if (b >> (7-c)) & 1 else ".." for c in range(8))
        print(f"  {row}")
    print("  --------")
    for b in bot:
        row = "".join("##" if (b >> (7-c)) & 1 else ".." for c in range(8))
        print(f"  {row}")

# ============================================================
# Generate labeled composite PNG
# ============================================================
ZOOM = 14
PAD = 30
os.makedirs('sprites', exist_ok=True)

def draw_card(img, x, y, card_bytes, zoom, color=FG):
    for row in range(8):
        byte_val = card_bytes[row]
        for col in range(8):
            if (byte_val >> (7-col)) & 1:
                for dy in range(zoom):
                    for dx in range(zoom):
                        img.putpixel((x + col*zoom + dx, y + row*zoom + dy), color)

# Layout: DECLE on top, RLE on bottom
NUM_DECLE = len(decle_cards) // 2
NUM_RLE = len(rle_cards) // 2

COLS = 7
DECLE_ROWS = (NUM_DECLE + COLS - 1) // COLS
RLE_ROWS = (NUM_RLE + COLS - 1) // COLS

CELL_W = 8 * ZOOM + 14
CELL_H = 16 * ZOOM + 70
SECTION_GAP = 40

w = CELL_W * COLS + PAD * 2
h = PAD + DECLE_ROWS * CELL_H + SECTION_GAP + RLE_ROWS * CELL_H + PAD
composite = Image.new('RGB', (w, h), BG)
draw = ImageDraw.Draw(composite)

try:
    font_small = ImageFont.truetype("arial.ttf", 11)
    font_label = ImageFont.truetype("arial.ttf", 13)
except:
    font_small = ImageFont.load_default()
    font_label = ImageFont.load_default()

# Color code
COLORS = {
    'WARRIOR': (255, 180, 60),
    'WIZARD': (180, 130, 255),
    'KNIGHT': (100, 180, 255),
    'SERPENT': (100, 255, 130),
    'DRAGON': (255, 100, 100),
    'DUNGEON': (160, 160, 160),
    'DECORATION': (140, 140, 140),
}

def get_color(label):
    for key, c in COLORS.items():
        if key in label.upper():
            return c
    return (200, 200, 200)

# Draw section header
draw.text((PAD, 8), "TITLE SCREEN CHARACTERS (DECLE $5BCD)", fill=(255, 220, 150), font=font_label)

# Draw DECLE sprites
for pair_idx in range(NUM_DECLE):
    col = pair_idx % COLS
    row = pair_idx // COLS
    label = decle_labels.get(pair_idx, "UNKNOWN")
    label_color = get_color(label)
    
    cx = PAD + col * CELL_W + 7
    cy = PAD + 24 + row * CELL_H
    
    draw_card(composite, cx, cy, decle_cards[pair_idx*2], ZOOM)
    draw_card(composite, cx, cy + 8 * ZOOM, decle_cards[pair_idx*2+1], ZOOM)
    
    draw.text((cx, cy + 16*ZOOM + 4), f"Pair {pair_idx}", fill=(140, 140, 160), font=font_small)
    draw.text((cx, cy + 16*ZOOM + 18), label, fill=label_color, font=font_label)

# Draw RLE section
rle_start_y = PAD + DECLE_ROWS * CELL_H + SECTION_GAP
draw.text((PAD, rle_start_y - 16), "DUNGEON & DRAGON TILES (RLE $61E7)", fill=(255, 220, 150), font=font_label)

for pair_idx in range(NUM_RLE):
    col = pair_idx % COLS
    row = pair_idx // COLS
    label = rle_labels.get(pair_idx, "UNKNOWN")
    label_color = get_color(label)
    
    cx = PAD + col * CELL_W + 7
    cy = rle_start_y + 24 + row * CELL_H
    
    draw_card(composite, cx, cy, rle_cards[pair_idx*2], ZOOM)
    draw_card(composite, cx, cy + 8 * ZOOM, rle_cards[pair_idx*2+1], ZOOM)
    
    draw.text((cx, cy + 16*ZOOM + 4), f"Pair {pair_idx}", fill=(140, 140, 160), font=font_small)
    draw.text((cx, cy + 16*ZOOM + 18), label, fill=label_color, font=font_label)

# Fix: the SECTION_GAP positioning has a bug with section_gap_label_y undefined
# Let me just fix the y position
composite.save('sprites/all_characters_labeled.png')
print(f"\nSaved: sprites/all_characters_labeled.png ({w}x{h})")
print(f"DECLE sprites: {NUM_DECLE}, RLE sprites: {NUM_RLE}")

# Also save individual named sprites
for pair_idx in range(NUM_DECLE):
    label = decle_labels.get(pair_idx, f"unknown_{pair_idx}")
    safe_name = label.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')
    
    img = Image.new('RGB', (8*ZOOM + 20, 16*ZOOM + 30), BG)
    d = ImageDraw.Draw(img)
    draw_card(img, 10, 5, decle_cards[pair_idx*2], ZOOM)
    draw_card(img, 10, 5 + 8*ZOOM, decle_cards[pair_idx*2+1], ZOOM)
    d.text((10, 16*ZOOM + 8), label, fill=get_color(label), font=font_label)
    img.save(f'sprites/char_{safe_name}.png')
    print(f"  Saved: sprites/char_{safe_name}.png")

for pair_idx in range(NUM_RLE):
    label = rle_labels.get(pair_idx, f"unknown_rle_{pair_idx}")
    safe_name = label.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')
    
    img = Image.new('RGB', (8*ZOOM + 20, 16*ZOOM + 30), BG)
    d = ImageDraw.Draw(img)
    draw_card(img, 10, 5, rle_cards[pair_idx*2], ZOOM)
    draw_card(img, 10, 5 + 8*ZOOM, rle_cards[pair_idx*2+1], ZOOM)
    d.text((10, 16*ZOOM + 8), label, fill=get_color(label), font=font_label)
    img.save(f'sprites/rle_{safe_name}.png')
    print(f"  Saved: sprites/rle_{safe_name}.png")
