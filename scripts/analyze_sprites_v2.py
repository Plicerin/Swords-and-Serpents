"""
Refined sprite classifier: analyzes 8x16 sprite structure to identify
Warrior, Knight, Wizard, Serpent/Dragon, and objects/tiles.
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

def make_16x16(top_card, bot_card):
    """Combine two 8x8 cards into a 16-row list of bytes"""
    combined = []
    for b in top_card:
        combined.append(b)
    for b in bot_card:
        combined.append(b)
    return combined

def get_pixel(sprite_16, row, col):
    """Get pixel at (row, col) in 16x8 sprite"""
    if 0 <= row < 16 and 0 <= col < 8:
        return (sprite_16[row] >> (7-col)) & 1
    return 0

def analyze_sprite_structure(sprite_16, name=""):
    """
    Detailed structural analysis of a 16x8 sprite.
    Returns classification based on body shape patterns.
    """
    rows = 16
    cols = 8
    
    # Column density profile
    col_density = []
    for c in range(cols):
        col_density.append(sum(get_pixel(sprite_16, r, c) for r in range(rows)))
    
    # Row density profile
    row_density = [bin(sprite_16[r]).count('1') for r in range(rows)]
    
    total_px = sum(row_density)
    if total_px == 0:
        return {'label': 'EMPTY', 'confidence': 1.0, 'details': {}}
    
    # Find horizontal center of mass
    com_col = sum(c * col_density[c] for c in range(cols)) / total_px
    com_row = sum(r * row_density[r] for r in range(rows)) / total_px
    
    # Symmetry analysis
    sym_score = 0
    for r in range(rows):
        byte = sprite_16[r]
        for c in range(4):
            if ((byte >> (7-c)) & 1) == ((byte >> c) & 1):
                sym_score += 1
    sym_pct = sym_score / (rows * 4) * 100
    
    # === STRUCTURE DETECTION ===
    
    # Find head region (dense cluster in top 5 rows)
    head_rows = []
    for r in range(min(5, rows)):
        if row_density[r] >= 3:
            head_rows.append(r)
    has_head = len(head_rows) >= 2
    
    # Find neck (narrow row after head, between rows 3-8)
    neck_found = False
    neck_row = -1
    for r in range(2, 7):
        if (row_density[r] <= 2 and 
            (r > 0 and row_density[r-1] >= 3) and
            (r+1 < rows and row_density[r+1] >= 3)):
            neck_found = True
            neck_row = r
            break
    
    # Find shoulders (wide row after neck, rows 4-9)
    shoulder_found = False
    for r in range(3, 9):
        if row_density[r] >= 5:
            shoulder_found = True
            break
    
    # Find legs (split bottom - left and right columns occupied, center empty)
    leg_split = False
    # Bottom 4 rows
    bot_left = sum(col_density[c] for c in range(3) if c < 4)
    bot_right = sum(col_density[c] for c in range(4, 8))
    bot_center = sum(col_density[c] for c in range(3, 5))
    if bot_left >= 3 and bot_right >= 3 and bot_center < bot_left * 0.4:
        leg_split = True
    
    # Body width analysis (should it be 1 card wide or 2 cards wide?)
    avg_width = sum(row_density) / rows
    
    # Serpent/dragon detection: 
    # - Long, undulating body
    # - No clear head/torso/legs structure
    # - Rows tend to have similar width
    row_density_variance = sum((rd - avg_width)**2 for rd in row_density) / rows
    
    # Wall/tile detection:
    # - Repeating patterns
    # - Often has vertical stripes
    vertical_repeats = sum(1 for c in range(3) if 
        col_density[c] > 0 and col_density[c] == col_density[c+4])
    
    # Check for weapon (asymmetrical extension on one side)
    left_heavy = sum(col_density[:4])
    right_heavy = sum(col_density[4:])
    weapon_asymmetry = abs(left_heavy - right_heavy) / max(total_px, 1)
    
    # Check for robe/dress (wide at bottom, triangular shape)
    robe_shape = False
    if row_density[10] > row_density[5] * 1.3 and row_density[14] > row_density[7] * 1.2:
        robe_shape = True
    
    # Check for shield (dense block on one side)
    shield_left = col_density[0] >= 4 and col_density[1] >= 5
    shield_right = col_density[7] >= 4 and col_density[6] >= 5
    
    # === HEURISTIC CLASSIFICATION ===
    label = ""
    confidence = 0.0
    reasons = []
    
    if has_head and neck_found and shoulder_found and leg_split:
        label = "WARRIOR"
        confidence = 0.85
        reasons.append("head+neck+shoulders+legs structure")
    elif has_head and shoulder_found and leg_split:
        label = "KNIGHT"
        confidence = 0.75
        reasons.append("head+shoulders+legs, no neck")
    elif has_head and robe_shape:
        label = "WIZARD"
        confidence = 0.70
        reasons.append("head+robe shape")
    elif has_head and (neck_found or shoulder_found):
        if weapon_asymmetry > 0.3:
            label = "WIZARD"
            confidence = 0.60
            reasons.append("head+asymmetric (staff?)")
        else:
            label = "HUMANOID"
            confidence = 0.50
            reasons.append("head structure present")
    elif row_density_variance < 1.0 and avg_width >= 4:
        # Uniform width = serpent/dragon body
        label = "SERPENT/DRAGON"
        confidence = 0.65
        reasons.append("uniform body width")
    elif vertical_repeats >= 2:
        label = "DUNGEON TILE"
        confidence = 0.60
        reasons.append("repeating vertical pattern")
    elif total_px < 25:
        # Check if it's a recognizable small shape
        if sym_pct > 85:
            label = "ITEM/SYMBOL"
            confidence = 0.55
            reasons.append("small symmetric item")
        else:
            label = "DECORATION"
            confidence = 0.40
            reasons.append("sparse")
    else:
        # Fallback: check for serpent features
        if avg_width >= 5 and weapon_asymmetry < 0.2:
            label = "SERPENT/DRAGON"
            confidence = 0.45
            reasons.append("dense uniform body")
        elif weapon_asymmetry > 0.35:
            label = "HUMANOID"
            confidence = 0.35
            reasons.append("asymmetric stance")
        else:
            label = "UNKNOWN"
            confidence = 0.25
            reasons.append("unclassified")
    
    return {
        'label': label,
        'confidence': confidence,
        'reasons': reasons,
        'total_px': total_px,
        'sym_pct': round(sym_pct, 1),
        'has_head': has_head,
        'neck_found': neck_found,
        'shoulder_found': shoulder_found,
        'leg_split': leg_split,
        'robe_shape': robe_shape,
        'weapon_asym': round(weapon_asymmetry, 2),
        'avg_width': round(avg_width, 1),
        'row_var': round(row_density_variance, 1),
        'row_density': row_density,
        'col_density': col_density,
    }

# ============================================================
# ANALYZE ALL SPRITES
# ============================================================
print("="*70)
print("REFINED SPRITE CLASSIFICATION")
print("="*70)

all_sprites = []

print("\n--- DECLE Sprites (Title Screen Characters) ---")
for pair_idx in range(len(decle_cards)//2):
    sprite = make_16x16(decle_cards[pair_idx*2], decle_cards[pair_idx*2+1])
    result = analyze_sprite_structure(sprite, f"DECLE_{pair_idx}")
    all_sprites.append({
        'top': decle_cards[pair_idx*2],
        'bot': decle_cards[pair_idx*2+1],
        'source': f"DECLE pair {pair_idx}",
        **result
    })
    print(f"  DECLE pair {pair_idx}: {result['label']:20s} (conf={result['confidence']:.0%}) "
          f"px={result['total_px']:2d} sym={result['sym_pct']:.1f}% "
          f"head={result['has_head']} neck={result['neck_found']} "
          f"shoulder={result['shoulder_found']} legs={result['leg_split']} "
          f"robe={result['robe_shape']} asym={result['weapon_asym']:.2f} "
          f"avg_w={result['avg_width']:.1f} row_var={result['row_var']:.1f} "
          f"| {', '.join(result['reasons'])}")

print("\n--- RLE Sprites (Dungeon/Serpent Tiles) ---")
for pair_idx in range(len(rle_cards)//2):
    sprite = make_16x16(rle_cards[pair_idx*2], rle_cards[pair_idx*2+1])
    result = analyze_sprite_structure(sprite, f"RLE_{pair_idx}")
    all_sprites.append({
        'top': rle_cards[pair_idx*2],
        'bot': rle_cards[pair_idx*2+1],
        'source': f"RLE pair {pair_idx}",
        **result
    })
    print(f"  RLE pair {pair_idx:2d}: {result['label']:20s} (conf={result['confidence']:.0%}) "
          f"px={result['total_px']:2d} sym={result['sym_pct']:.1f}% "
          f"head={result['has_head']} neck={result['neck_found']} "
          f"shoulder={result['shoulder_found']} legs={result['leg_split']} "
          f"robe={result['robe_shape']} asym={result['weapon_asym']:.2f} "
          f"avg_w={result['avg_width']:.1f} row_var={result['row_var']:.1f} "
          f"| {', '.join(result['reasons'])}")

# ============================================================
# Special analysis: What are the DECLE sprites REALLY?
# ============================================================
print("\n" + "="*70)
print("DETAILED DECLE SPRITE SHAPE PROFILES")
print("="*70)

# Legend: Characters in the title screen of "Swords and Serpents"
# Based on the game's name, we expect: Warrior, Knight, Wizard, Serpent
# Let's analyze each DECLE sprite's combat stance
for pair_idx in range(len(decle_cards)//2):
    sprite = make_16x16(decle_cards[pair_idx*2], decle_cards[pair_idx*2+1])
    rows = 16
    cols = 8
    row_density = [bin(sprite[r]).count('1') for r in range(rows)]
    col_density = [sum(get_pixel(sprite, r, c) for r in range(rows)) for c in range(cols)]
    
    # Find leftmost and rightmost occupied columns
    left_cols = [c for c in range(cols) if col_density[c] > 0]
    rightmost = max(left_cols) if left_cols else 0
    leftmost = min(left_cols) if left_cols else 0
    
    # Check for weapon (thin extension on one side, rows 3-10)
    weapon_side = None
    if col_density[0] > 0 and col_density[1] == 0 and col_density[7] > 0:
        # Both extremes occupied = possible weapon left + body right
        weapon_side = "BOTH"
    elif col_density[0] > 0 and col_density[1] <= 2 and col_density[6] >= 4:
        weapon_side = "LEFT"
    elif col_density[7] > 0 and col_density[6] <= 2 and col_density[1] >= 4:
        weapon_side = "RIGHT"
    
    # Shield detection: dense block on one side, rows 3-8
    shield_side = None
    left_block = sum(1 for r in range(3, 9) if get_pixel(sprite, r, 0) and get_pixel(sprite, r, 1))
    right_block = sum(1 for r in range(3, 9) if get_pixel(sprite, r, 7) and get_pixel(sprite, r, 6))
    if left_block >= 4: shield_side = "LEFT"
    if right_block >= 4: shield_side = "RIGHT"
    
    # Head position
    head_top = -1
    for r in range(5):
        if row_density[r] >= 3:
            head_top = r
            break
    
    print(f"\nDECLE pair {pair_idx}:")
    print(f"  Row density: {row_density}")
    print(f"  Col density: {col_density}")
    print(f"  Head top row: {head_top}")
    print(f"  Weapon side: {weapon_side}")
    print(f"  Shield side: {shield_side}")
    print(f"  Pixel span: col {leftmost}-{rightmost}")

# ============================================================
# Generate labeled composite
# ============================================================
ZOOM = 16
PAD = 40
os.makedirs('sprites', exist_ok=True)

def draw_card(img, x, y, card_bytes, zoom, color=FG):
    for row in range(8):
        byte_val = card_bytes[row]
        for col in range(8):
            if (byte_val >> (7-col)) & 1:
                for dy in range(zoom):
                    for dx in range(zoom):
                        img.putpixel((x + col*zoom + dx, y + row*zoom + dy), color)

COLS = 4
ROWS = (len(all_sprites) + COLS - 1) // COLS
CELL_W = 8 * ZOOM + 20
CELL_H = 16 * ZOOM + 80

composite_w = CELL_W * COLS + PAD * 2
composite_h = CELL_H * ROWS + PAD * 2
composite = Image.new('RGB', (composite_w, composite_h), BG)
draw = ImageDraw.Draw(composite)

try:
    font = ImageFont.truetype("arial.ttf", 14)
except:
    font = ImageFont.load_default()

# Color-code by type
TYPE_COLORS = {
    'WARRIOR': (255, 200, 100),
    'KNIGHT': (100, 200, 255),
    'WIZARD': (200, 150, 255),
    'SERPENT/DRAGON': (100, 255, 150),
    'DUNGEON TILE': (180, 180, 180),
    'DECORATION': (150, 150, 150),
    'ITEM/SYMBOL': (255, 255, 150),
    'HUMANOID': (255, 180, 180),
    'UNKNOWN': (100, 100, 100),
}

for idx, sprite in enumerate(all_sprites):
    col = idx % COLS
    row = idx // COLS
    
    cx = PAD + col * CELL_W + 10
    cy = PAD + row * CELL_H + 10
    
    draw_card(composite, cx, cy, sprite['top'], ZOOM)
    draw_card(composite, cx, cy + 8 * ZOOM, sprite['bot'], ZOOM)
    
    tc = TYPE_COLORS.get(sprite['label'], (200, 200, 200))
    
    draw.text((cx, cy + 16*ZOOM + 3), sprite['source'], fill=(150, 150, 180), font=font)
    draw.text((cx, cy + 16*ZOOM + 20), sprite['label'], fill=tc, font=font)
    draw.text((cx, cy + 16*ZOOM + 37), f"px={sprite['total_px']} sym={sprite['sym_pct']}%", 
              fill=(120, 120, 140), font=font)

composite.save('sprites/all_characters_labeled.png')
print(f"\nSaved: sprites/all_characters_labeled.png ({composite_w}x{composite_h})")
