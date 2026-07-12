#!/usr/bin/env python3
"""
Render the ACTUAL first dungeon room from Swords & Serpents
using the jzIntv BackTab dump and GRAM tile data from ROM.
"""

from PIL import Image, ImageDraw

# ============================================================
# TRUE INTELLIVISION 16-COLOR PALETTE
# ============================================================
INTV = [
    (0, 0, 0),          #  0: Black
    (0, 0, 255),        #  1: Blue
    (200, 40, 40),      #  2: Red
    (200, 170, 50),     #  3: Tan
    (0, 128, 0),        #  4: Dark Green
    (0, 255, 0),        #  5: Green
    (255, 255, 0),      #  6: Yellow
    (255, 255, 255),    #  7: White
    (128, 128, 128),    #  8: Grey
    (0, 255, 255),      #  9: Cyan
    (255, 150, 0),      # 10: Orange
    (150, 130, 100),    # 11: Brown
    (255, 100, 150),    # 12: Pink
    (100, 200, 255),    # 13: Light Blue
    (200, 200, 0),      # 14: Yellow-Green
    (150, 60, 200),     # 15: Purple
]

# ============================================================
# PARSE jzIntv BACKTAB DUMP
# ============================================================
dump_raw = """0200:  1603* 1603  1603  1603   1603  1603  1603  1603
0208:  1603  1603  1603  1603   1603  1603  1603  1603
0210:  1603  1603  1603  1603   1603  1603  1603  1603
0218:  1603  1603  1603  1603   1603  1603  1603  1603
0220:  1603  1603  1603  1603   1603  1603  1603  1603
0228:  1603  1603  179B  17BB   177B  1793  1723  179B
0230:  1603  1633  1603  179B   172B  1793  1783  172B
0238:  1773  17A3  179B  1603   1603  1603  1603  1603
0240:  1603  1603  1603  1603   1603  1603  1603  1603
0248:  1603  1603  1603  1603   1603  1603  1603  1603
0250:  1603  1603  1603  1603   1603  1EBB  1603  174B
0258:  176B  170B  173B  174B   171B  1603  168B  16CB
0260:  16C3  1693  1603  1603   1603  1603  1603  1603
0268:  1603  1603  1603  1603   1603  1603  1603  1603
0270:  1603  1603  1603  1603   1603  1603  1603  1603
0278:  1603  1603  1603  1603   1603  1603  1603  1603
0280:  1603  1603  1603  1603   1603  1603  1603  1603
0288:  1603  1603  1603  1603   1603  1603  1603  1603
0290:  1603  1603  1603  1603   1603  1603  1603  1603
0298:  1603  1603  1603  1603   1603  1603  1603  1603
02A0:  1603  1603  1603  1603   1603  1603  1603  1603
02A8:  1603  1603  1603  1603   1603  1603  1603  1603
02B0:  1603  1603  1603  1603   1603  1603  172B  1773
02B8:  17A3  172B  1793  1603   173B  170B  176B  172B
02C0:  1603  1643  168B  1663   1693  1663  169B  164B
02C8:  1603  1603  1603  1603   1603  1603  1603  1603
02D0:  1603  1603  1603  1603   1603  1603  1603  1603
02D8:  1603  1603  1603  1603   1603  1603  1603  1603
02E0:  1603  1603  1603  1603   1603  1603  1603  1603
02E8:  1603  1603  1603  1603   1603  1603  1603  1603"""

# Parse: 20 columns x 12 rows, each cell is a 16-bit word
COLS = 20
ROWS = 12
grid = [[0] * COLS for _ in range(ROWS)]

flat_words = []
for line in dump_raw.strip().split('\n'):
    parts = line.split()
    for p in parts:
        p = p.replace('*', '')
        if len(p) == 4 and all(c in '0123456789ABCDEFabcdef' for c in p):
            flat_words.append(int(p, 16))

# Fill grid row-major: each row = 20 consecutive words
for i, word in enumerate(flat_words):
    if i >= COLS * ROWS:
        break
    row = i // COLS
    col = i % COLS
    grid[row][col] = word

# ============================================================
# DECODE STIC COLOR STACK BACKTAB
# ============================================================
# Standard IntelliVision Color Stack mode BackTab word:
#   Bit 15-14: Unused
#   Bit 13:    Color Stack Advance
#   Bit 12:    GROM(0) / GRAM(1)
#   Bits 11-3: Card number (9 bits for GROM; 6 bits [8:3] for GRAM)
#   Bits 2-0:  Foreground color (0-7)

def decode_backtab(word):
    """Decode 16-bit BackTab word into (gram, card, fg_color, csa)."""
    csa  = (word >> 13) & 1
    gram = (word >> 12) & 1
    fg   = word & 0x07
    if gram:
        # GRAM: 5-bit card in bits 7-3 (32 cards, 0-31)
        card = (word >> 3) & 0x1F
    else:
        # GROM: 8-bit card in bits 10-3
        card = (word >> 3) & 0xFF
    return gram, card, fg, csa

# ============================================================
# LOAD GRAM TILES FROM ROM (RLE at $61E7)
# ============================================================
rom = open('Swords and Serpents.bin', 'rb').read()

def read_decle(addr):
    off = (addr - 0x5000) * 2
    if off + 1 < len(rom):
        return (rom[off] << 8) | rom[off + 1]
    return 0

# Decode RLE tiles
addr = 0x61E7
count = read_decle(addr + 1)
decoded = bytearray()
for i in range(count):
    entry = read_decle(addr + 2 + i)
    repeat = ((entry >> 8) & 0x03) + 1
    for _ in range(repeat):
        decoded.append(entry & 0xFF)

gram_cards = []
for c in range(len(decoded) // 8):
    gram_cards.append(list(decoded[c*8:(c+1)*8]))

print(f"Loaded {len(gram_cards)} GRAM cards from ROM $61E7")

# ============================================================
# ANALYZE BACKTAB GRID
# ============================================================
print(f"\n=== BackTab Analysis (20×12) ===")
print(f"GRID: COLS 0-{COLS-1}, ROWS 0-{ROWS-1}")
print()

# Collect unique BackTab values
unique_values = {}
for r in range(ROWS):
    for c in range(COLS):
        w = grid[r][c]
        if w not in unique_values:
            gram, card, fg, csa = decode_backtab(w)
            unique_values[w] = {
                'gram': gram, 'card': card, 'fg': fg, 'csa': csa,
                'count': 0, 'first': (r, c)
            }
        unique_values[w]['count'] += 1

print("Unique BackTab values:")
for w in sorted(unique_values.keys()):
    info = unique_values[w]
    gram_str = "GRAM" if info['gram'] else "GROM"
    csa_str = "CSA" if info['csa'] else "   "
    card_str = f"card={info['card']:3d}"
    if info['gram'] and info['card'] < len(gram_cards):
        card_str += " (valid)"
    elif info['gram']:
        card_str += " (OUT OF RANGE)"
    print(f"  ${w:04X} : {gram_str} {card_str} FG={info['fg']} {csa_str} count={info['count']:3d}  first at ({info['first'][0]},{info['first'][1]})")

# ============================================================
# ASCII PREVIEW
# ============================================================
print(f"\n=== Dungeon Room Layout ({COLS}×{ROWS}) ===")
print("    " + "".join(f"{c:2d} " for c in range(COLS)))
for r in range(ROWS):
    print(f"R{r:2d} ", end="")
    for c in range(COLS):
        w = grid[r][c]
        gram, card, fg, csa = decode_backtab(w)
        if w == 0x1603:
            print(" ·  ", end="")  # default floor
        elif gram:
            print(f"\033[33m{card:2d}:{fg}\033[0m ", end="")
        else:
            print(f"\033[36m{card:2d}:{fg}\033[0m ", end="")
    print()

# ============================================================
# PIXEL RENDER
# ============================================================
ZOOM = 12
TILE_PX = 8 * ZOOM
LEGEND_W = 280
IMG_W = COLS * TILE_PX
IMG_H = ROWS * TILE_PX
TOTAL_W = IMG_W + LEGEND_W + 40
TOTAL_H = IMG_H + 60

img = Image.new('RGB', (TOTAL_W, TOTAL_H), INTV[0])
pix = img.load()

def draw_card(pixels, tx_px, ty_px, card_bytes, fg_color, bg_color=None):
    """Draw 8×8 tile at pixel position with given colors."""
    for row in range(8):
        byte_val = card_bytes[row]
        for col in range(8):
            px = tx_px + col * ZOOM
            py = ty_px + row * ZOOM
            if (byte_val >> (7 - col)) & 1:
                for dy in range(ZOOM):
                    for dx in range(ZOOM):
                        if 0 <= px + dx < TOTAL_W and 0 <= py + dy < TOTAL_H:
                            pixels[px + dx, py + dy] = INTV[fg_color if fg_color < 16 else 7]
            elif bg_color is not None:
                for dy in range(ZOOM):
                    for dx in range(ZOOM):
                        if 0 <= px + dx < TOTAL_W and 0 <= py + dy < TOTAL_H:
                            pixels[px + dx, py + dy] = bg_color

# Dark room background for "empty" tiles
ROOM_DARK = (20, 15, 5)

# Render each tile
for r in range(ROWS):
    for c in range(COLS):
        w = grid[r][c]
        gram, card, fg, csa = decode_backtab(w)
        
        tx_px = c * TILE_PX
        ty_px = r * TILE_PX
        
        if w == 0x1603:
            # Default floor tile - dark room interior
            fill_tx = tx_px
            fill_ty = ty_px
            for dy in range(TILE_PX):
                for dx in range(TILE_PX):
                    if 0 <= fill_tx + dx < TOTAL_W and 0 <= fill_ty + dy < TOTAL_H:
                        pix[fill_tx + dx, fill_ty + dy] = ROOM_DARK
        elif gram and card < len(gram_cards):
            # GRAM dungeon tile - draw it!
            card_data = gram_cards[card]
            draw_card(pix, tx_px, ty_px, card_data, fg, ROOM_DARK)
        elif gram:
            # Out-of-range GRAM card - draw error marker
            for dy in range(TILE_PX):
                for dx in range(TILE_PX):
                    fill_tx = tx_px + dx
                    fill_ty = ty_px + dy
                    if 0 <= fill_tx < TOTAL_W and 0 <= fill_ty < TOTAL_H:
                        pix[fill_tx, fill_ty] = (80, 0, 0)
        else:
            # GROM card (system font/characters)
            # Draw as solid fill with FG color
            fill_color = INTV[fg] if fg < 16 else INTV[7]
            for dy in range(TILE_PX):
                for dx in range(TILE_PX):
                    fill_tx = tx_px + dx
                    fill_ty = ty_px + dy
                    if 0 <= fill_tx < TOTAL_W and 0 <= fill_ty < TOTAL_H:
                        pix[fill_tx, fill_ty] = fill_color

# ============================================================
# LEGEND
# ============================================================
draw = ImageDraw.Draw(img)
lx = IMG_W + 20
ly = 20

# Background panel
for dy in range(10, IMG_H + 30):
    for dx in range(IMG_W + 10, TOTAL_W - 10):
        if 0 <= dx < TOTAL_W and 0 <= dy < TOTAL_H:
            pix[dx, dy] = (15, 12, 20)

draw.text((lx, ly), "SWORDS & SERPENTS", fill=(255, 215, 130))
ly += 24
draw.text((lx, ly), "First Dungeon Room", fill=(200, 180, 150))
ly += 32
draw.text((lx, ly), f"BackTab: {COLS}x{ROWS}  (from jzIntv capture)", fill=(120, 115, 140))
ly += 18
draw.text((lx, ly), f"Zoom: {ZOOM}x  ({IMG_W}x{IMG_H} px)", fill=(120, 115, 140))
ly += 24

draw.text((lx, ly), "INTV Color Palette:", fill=(180, 200, 220))
ly += 20
for i, color in enumerate(INTV):
    draw.rectangle([lx, ly, lx + 14, ly + 10], fill=color, outline=(80, 80, 100))
    names = ["Black","Blue","Red","Tan","DkGreen","Green","Yellow","White",
             "Grey","Cyan","Orange","Brown","Pink","LtBlue","YlwGrn","Purple"]
    draw.text((lx + 20, ly - 1), f"{i}: {names[i]}", fill=(180, 180, 200))
    ly += 14

ly += 16
draw.text((lx, ly), "Dungeon Tiles (GRAM):", fill=(180, 200, 220))
ly += 20

# Show which GRAM cards are used
used_cards = set()
for r in range(ROWS):
    for c in range(COLS):
        w = grid[r][c]
        gram, card, fg, csa = decode_backtab(w)
        if gram and card < len(gram_cards):
            used_cards.add(card)

for card in sorted(used_cards):
    draw.text((lx, ly), f"Card {card}", fill=(200, 170, 50))
    draw.text((lx + 60, ly), f"FG={decode_backtab([w for w in unique_values if decode_backtab(w)[1]==card and decode_backtab(w)[0]==1][0] if [w for w in unique_values if decode_backtab(w)[1]==card and decode_backtab(w)[0]==1] else 3)[0] if False else '?'}", fill=(180, 180, 200))
    ly += 14

# Tile reference - render small versions of used GRAM cards
draw.text((lx, ly), "", fill=(180, 180, 200))
ly += 10

ref_zoom = 4
ref_tile = 8 * ref_zoom
for idx, card in enumerate(sorted(used_cards)):
    col = idx % 4
    row_idx = idx // 4
    rx = lx + col * (ref_tile + 14)
    ry = ly + row_idx * (ref_tile + 28)
    
    card_data = gram_cards[card]
    for tr in range(8):
        byte_val = card_data[tr]
        for tc in range(8):
            px = rx + tc * ref_zoom
            py = ry + tr * ref_zoom
            if (byte_val >> (7 - tc)) & 1:
                for dy in range(ref_zoom):
                    for dx in range(ref_zoom):
                        if 0 <= px + dx < TOTAL_W and 0 <= py + dy < TOTAL_H:
                            pix[px + dx, py + dy] = INTV[3]  # Tan
    
    draw.text((rx, ry + ref_tile + 2), f"#{card}", fill=(180, 180, 200))

# ============================================================
# SAVE
# ============================================================
import os
os.makedirs('sprites', exist_ok=True)
fname = 'sprites/dungeon_backtab_render.png'
img.save(fname)
print(f"\nSaved: {fname} ({TOTAL_W}x{TOTAL_H})")

# ============================================================
# ALSO: RAW GRAM CARD DUMP (all 31 cards)
# ============================================================
print("\n=== GRAM Card Contents (from ROM $61E7) ===")
for ci, card in enumerate(gram_cards):
    print(f"\nCard {ci}:")
    for row_byte in card:
        line = ''.join('#' if (row_byte >> (7-i)) & 1 else '.' for i in range(8))
        print(f"  {line}")
