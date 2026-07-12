from PIL import Image, ImageDraw, ImageFont
import os

# IntelliVision color palette
INTV = [
    (0,0,0), (0,0,255), (200,40,40), (200,170,50),
    (0,128,0), (0,255,0), (255,255,0), (255,255,255),
    (128,128,128), (0,255,255), (255,150,0), (150,130,100),
    (255,100,150), (100,200,255), (200,200,0), (150,60,200),
]
FG = INTV[7]
BG = (10, 10, 25)

rom = open('Swords and Serpents.bin', 'rb').read()

def read_decle(addr):
    off = (addr - 0x5000) * 2
    if off + 1 < len(rom):
        return (rom[off] << 8) | rom[off + 1]
    return None

# ============================================================
# SOURCE 1: DECLE cards from $5BCD-$5C45
# ============================================================
pixel_data = []
for addr in range(0x5BCD, 0x5C46):
    v = read_decle(addr)
    if v is None:
        break
    hi = (v >> 8) & 0xFF
    if hi == 0:
        pixel_data.append(v & 0xFF)

decle_cards = []
for c in range(len(pixel_data)//8):
    decle_cards.append(list(pixel_data[c*8:(c+1)*8]))

# ============================================================
# SOURCE 2: RLE cards from $61E7
# ============================================================
addr = 0x61E7
count = read_decle(addr + 1)
decoded = bytearray()
for i in range(count):
    entry = read_decle(addr + 2 + i)
    if entry is None:
        break
    repeat = ((entry >> 8) & 0x03) + 1
    byte_val = entry & 0xFF
    for _ in range(repeat):
        decoded.append(byte_val)

rle_cards = []
for c in range(len(decoded)//8):
    rle_cards.append(list(decoded[c*8:(c+1)*8]))

# ============================================================
# RENDER ASCII art of each card for visual inspection
# ============================================================
def render_ascii(card_bytes, label=""):
    lines = []
    lines.append(f"--- {label} ---")
    for b in card_bytes:
        row = ""
        for col in range(8):
            if (b >> (7-col)) & 1:
                row += "##"
            else:
                row += ".."
        lines.append(row)
    return "\n".join(lines)

print("="*60)
print("DECLE CARDS ($5BCD) — ASCII RENDER")
print("="*60)
for i, card in enumerate(decle_cards):
    print(render_ascii(card, f"DECLE Card {i}"))
    print()

print("="*60)
print("RLE CARDS ($61E7) — ASCII RENDER")
print("="*60)
for i, card in enumerate(rle_cards):
    print(render_ascii(card, f"RLE Card {i}"))
    print()

# ============================================================
# Now analyze shape characteristics for classification
# ============================================================
def analyze_card(card_bytes):
    row_counts = [bin(b).count('1') for b in card_bytes]
    total_pixels = sum(row_counts)
    weighted_sum = sum((i+1)*rc for i, rc in enumerate(row_counts))
    center_y = weighted_sum / max(total_pixels, 1)
    
    symmetry_score = 0
    for row_byte in card_bytes:
        for col in range(4):
            left_bit = (row_byte >> (7-col)) & 1
            right_bit = (row_byte >> col) & 1
            if left_bit == right_bit:
                symmetry_score += 1
    symmetry_pct = symmetry_score / 32.0 * 100
    
    top_half = sum(row_counts[:4])
    bot_half = sum(row_counts[4:])
    
    left_px = 0
    right_px = 0
    for row_byte in card_bytes:
        for col in range(4):
            left_px += (row_byte >> (7-col)) & 1
            right_px += (row_byte >> col) & 1
    
    # Check for horizontal bands (serpent body segments)
    band_rows = sum(1 for rc in row_counts if rc >= 5)
    
    # Check for thin vertical strips (legs)
    vert_strips = 0
    for col in range(8):
        col_px = sum(1 for b in card_bytes if (b >> (7-col)) & 1)
        if col_px >= 4 and col_px <= 6:  # thin vertical
            vert_strips += 1
    
    return {
        'total_px': total_pixels,
        'center_y': round(center_y, 1),
        'symmetry_pct': round(symmetry_pct, 1),
        'top_half': top_half,
        'bot_half': bot_half,
        'left_px': left_px,
        'right_px': right_px,
        'band_rows': band_rows,
        'vert_strips': vert_strips,
        'row_counts': row_counts,
        'max_band': max(row_counts),
    }

def classify_card_pair(top_a, bot_a):
    total = top_a['total_px'] + bot_a['total_px']
    sym = (top_a['symmetry_pct'] + bot_a['symmetry_pct']) / 2
    
    # Head-like: pixels concentrated in top rows of top card
    head_like = top_a['top_half'] > top_a['bot_half'] * 2
    
    # Legs-like: pixels at bottom of bottom card, split sides
    legs_like = (bot_a['bot_half'] > bot_a['top_half'] * 1.3 and 
                 bot_a['band_rows'] < 2 and bot_a['vert_strips'] >= 1)
    
    # Serpent: horizontal bands across cards
    serpent_like = (top_a['max_band'] >= 6 or bot_a['max_band'] >= 6) and not head_like
    
    # Dense humanoid: lots of pixels, symmetric
    dense_human = total > 50 and sym > 55
    
    # Object: sparse, small
    object_like = total < 25
    
    return {
        'total_px': total,
        'symmetry': round(sym, 1),
        'head_like': head_like,
        'legs_like': legs_like,
        'serpent_like': serpent_like,
        'dense_human': dense_human,
        'object_like': object_like,
    }

print("="*60)
print("FINAL CLASSIFICATION")
print("="*60)

# DECLE classification
print("\n--- DECLE Sprites ---")
decle_results = []
for pair_idx in range(len(decle_cards)//2):
    top = analyze_card(decle_cards[pair_idx*2])
    bot = analyze_card(decle_cards[pair_idx*2 + 1])
    c = classify_card_pair(top, bot)
    
    if c['object_like']:
        label = "OBJECT (treasure/icon)"
    elif c['serpent_like']:
        label = "SERPENT/DRAGON"
    elif c['head_like'] and c['legs_like']:
        if c['symmetry'] > 70:
            label = "WARRIOR (standing, symmetric)"
        else:
            label = "HUMANOID (knight/wizard)"
    elif c['dense_human']:
        label = "HUMANOID"
    else:
        # Check for weapon-carrying stance
        left_bias = abs(top['left_px'] - top['right_px']) > 4
        if left_bias and c['symmetry'] < 60:
            label = "HUMANOID (attack stance)"
        else:
            label = "UNKNOWN"
    
    decle_results.append((f"DECLE pair {pair_idx}", label, top, bot, c))
    print(f"Pair {pair_idx}: px={c['total_px']:3d} sym={c['symmetry']:.1f}% head={c['head_like']} legs={c['legs_like']} serpent={c['serpent_like']} -> {label}")

# RLE classification
print("\n--- RLE Sprites ---")
rle_results = []
for pair_idx in range(len(rle_cards)//2):
    top = analyze_card(rle_cards[pair_idx*2])
    bot = analyze_card(rle_cards[pair_idx*2 + 1])
    c = classify_card_pair(top, bot)
    
    if c['object_like']:
        label = "OBJECT (treasure/icon)"
    elif c['serpent_like']:
        label = "SERPENT/DRAGON"
    elif c['head_like'] and c['legs_like']:
        if c['symmetry'] > 70:
            label = "WARRIOR (standing, symmetric)"
        else:
            label = "HUMANOID (knight/wizard)"
    elif c['dense_human']:
        label = "HUMANOID"
    else:
        left_bias = abs(top['left_px'] - top['right_px']) > 4
        if left_bias and c['symmetry'] < 60:
            label = "HUMANOID (attack stance)"
        elif total_px > 40:
            label = "HUMANOID"
        else:
            label = "UNKNOWN"
    
    rle_results.append((f"RLE pair {pair_idx}", label, top, bot, c))
    print(f"Pair {pair_idx}: px={c['total_px']:3d} sym={c['symmetry']:.1f}% head={c['head_like']} legs={c['legs_like']} serpent={c['serpent_like']} -> {label}")

# ============================================================
# Generate labeled composite PNG
# ============================================================
ZOOM = 16
PAD = 40
os.makedirs('sprites', exist_ok=True)

def draw_card(img, x, y, card_bytes, zoom, color=FG):
    """Draw an 8x8 card at position (x,y) with given zoom"""
    for row in range(8):
        byte_val = card_bytes[row]
        for col in range(8):
            if (byte_val >> (7-col)) & 1:
                for dy in range(zoom):
                    for dx in range(zoom):
                        img.putpixel((x + col*zoom + dx, y + row*zoom + dy), color)

# Render ALL classified sprites into one big composite
all_sprites = []
# Add DECLE sprites
for i in range(len(decle_cards)//2):
    all_sprites.append({
        'top': decle_cards[i*2],
        'bot': decle_cards[i*2+1],
        'label': decle_results[i][1],
        'source': f'DECLE {i}'
    })
# Add RLE sprites
for i in range(len(rle_cards)//2):
    all_sprites.append({
        'top': rle_cards[i*2],
        'bot': rle_cards[i*2+1],
        'label': rle_results[i][1],
        'source': f'RLE {i}'
    })

COLS = 5
ROWS = (len(all_sprites) + COLS - 1) // COLS
CELL_W = 8 * ZOOM + 20
CELL_H = 16 * ZOOM + 80

w = CELL_W * COLS + PAD * 2
h = CELL_H * ROWS + PAD * 2
composite = Image.new('RGB', (w, h), (5, 5, 15))
draw = ImageDraw.Draw(composite)

try:
    font = ImageFont.truetype("arial.ttf", 16)
except:
    font = ImageFont.load_default()

for idx, sprite in enumerate(all_sprites):
    col = idx % COLS
    row = idx // COLS
    
    cx = PAD + col * CELL_W + 10
    cy = PAD + row * CELL_H + 10
    
    # Draw top card
    draw_card(composite, cx, cy, sprite['top'], ZOOM)
    # Draw bottom card
    draw_card(composite, cx, cy + 8 * ZOOM, sprite['bot'], ZOOM)
    
    # Label
    draw.text((cx, cy + 16*ZOOM + 5), sprite['source'], fill=(180,180,200), font=font)
    draw.text((cx, cy + 16*ZOOM + 25), sprite['label'], fill=(255,255,200), font=font)

composite.save('sprites/all_characters_labeled.png')
print(f"\nSaved labeled composite: sprites/all_characters_labeled.png")
print(f"Total sprites: {len(all_sprites)}")
