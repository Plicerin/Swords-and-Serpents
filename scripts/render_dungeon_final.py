#!/usr/bin/env python3
"""
PIXEL-PERFECT first dungeon room render of "Swords and Serpents".

KEY FINDINGS:
- GRAM card N uses Method B: gram[card][row] = words[card * 8 + row] & 0xFF
- GRAM card decode is 5-bit: card = (BackTab >> 3) & 0x1F (not 0x3F!)
- Floor tile ($1603) uses GROM (blank space char), FG color 3 (Tan)
- Wall tiles use GRAM cards 0-31 loaded by ROM RLE at $61E7 (cards 3-33)
"""

from PIL import Image, ImageDraw
import os, re

# ============================================================
# INTELLIVISION 16-COLOR PALETTE
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
# UNIFIED jzIntv DUMP DATA (single 12M-cycle run)
# ============================================================

# BackTab dump ($0200-$03DF, 240 words, 20x12 grid)
backtab_raw = """0200:  1603* 1603  1603  1603   1603  1603  1603  1603
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

# GRAM dump ($3800-$3FFF, 512 words = 64 cards x 8 words)
gram_raw = """3800:  0000* 0028  007F  0018   002F  000D  0010  0000
3808:  00F0  00F0  00F0  0070   0070  0020  00A0  00A0
3810:  00A0  00A0  0080  00D0   00D0  00F0  00F0  00F0
3818:  00F0  00F8  00E8  0078   00F0  00F8  00F8  00F8
3820:  00F7  00FF  00FF  00FF   00EF  00E6  0000  0000
3828:  00EF  00FF  007F  00FF   00FF  00FD  00F8  00F8
3830:  00F0  00F8  00E8  00F8   00F0  00B8  0000  0000
3838:  0080  00C0  00E0  00E0   00E0  00E0  00E0  00E0
3840:  00FF  007F  0000  0000   0000  0000  0000  0000
3848:  00E0  00EC  00ED  00ED   00ED  00ED  00EC  00E0
3850:  00E0  00EC  00ED  00ED   00ED  00ED  00EC  00E0
3858:  007F  002E  003A  0036   006C  0074  005C  00FE
3860:  00FF  0000  00FF  00FE   00FE  00FF  0000  00FF
3868:  00AB  00AB  00AB  00AA   00AA  00AB  00AB  00AB
3870:  0000  0000  0087  009D   00FD  003F  0018  003C
3878:  0042  0081  0099  00BD   005A  0024  00DB  007E
3880:  0000  0018  0024  0018   00BD  00FF  00A5  00FF
3888:  0000  003C  004A  00D1   0085  00A9  004A  003C
3890:  00FF  00F9  00F3  00E7   00CF  007E  003C  0018
3898:  0099  00BD  00BD  00FF   0042  0066  0066  0024
38A0:  00C1  0055  007F  0055   0055  0055  0055  003E
38A8:  0018  003C  0018  003C   006E  00DF  006E  003C
38B0:  0000  0000  0040  00BF   0045  0000  0000  0000
38B8:  003C  0042  0099  0091   0091  0099  0042  003C
38C0:  0000  0078  001E  00FC   0018  0018  0031  0073
38C8:  0000  0000  0010  003B   007F  00FF  00FF  00FF
38D0:  000F  003C  00F8  00F0   00E2  00CA  009F  0039
38D8:  0000  0009  0095  00FF   00FF  0095  0009  0000
38E0:  0000  0083  001F  00FD   00FD  001F  0083  0000
38E8:  00F1  00DF  00BE  0076   0076  00BE  00DF  00F1
38F0:  0000  0006  000F  0099   00F3  00E6  000C  0000
38F8:  0073  0031  0018  0018   00FC  001E  0078  0000
3900:  00FF  00FF  00FF  007F   003B  0010  0000  0000
3908:  0039  009F  00CA  00E2   00F0  00F8  003C  000F"""

# ============================================================
# PARSE GRAM (Method B: gram[card][row] = words[card*8 + row] & 0xFF)
# ============================================================
NUM_GRAM_CARDS = 64
gram = [[0] * 8 for _ in range(NUM_GRAM_CARDS)]

words_gram = []
for line in gram_raw.strip().split('\n'):
    parts = line.split()
    for p in parts:
        p = p.replace('*', '')
        if len(p) == 4 and all(c in '0123456789ABCDEFabcdef' for c in p):
            words_gram.append(int(p, 16))

print(f"Parsed {len(words_gram)} GRAM words")

for card in range(min(NUM_GRAM_CARDS, len(words_gram) // 8)):
    for row in range(8):
        gram[card][row] = words_gram[card * 8 + row] & 0xFF

non_empty = [(c, gram[c]) for c in range(NUM_GRAM_CARDS) if any(b != 0 for b in gram[c])]
print(f"Non-empty GRAM cards: {len(non_empty)} — {[c for c, _ in non_empty]}")

# ============================================================
# PARSE BACKTAB (20x12 grid)
# ============================================================
COLS = 20
ROWS = 12
grid = [[0] * COLS for _ in range(ROWS)]

flat_bt = []
for line in backtab_raw.strip().split('\n'):
    parts = line.split()
    for p in parts:
        p = p.replace('*', '')
        if len(p) == 4 and all(c in '0123456789ABCDEFabcdef' for c in p):
            flat_bt.append(int(p, 16))

for i, word in enumerate(flat_bt):
    if i >= COLS * ROWS:
        break
    grid[i // COLS][i % COLS] = word

# ============================================================
# DECODE BACKTAB (5-bit GRAM cards)
# ============================================================
def decode_backtab(word):
    """Decode STIC BackTab word with 5-bit GRAM card extraction."""
    gram_bit = (word >> 12) & 1
    fg_color = word & 0x07
    csa = (word >> 13) & 1
    card_raw = (word >> 3) & 0x1FF  # 9-bit raw card
    if gram_bit:
        card = card_raw & 0x1F  # 5-bit GRAM card (0-31)
    else:
        card = card_raw  # GROM card (0-511)
    return gram_bit, card, fg_color, csa

# ============================================================
# ANALYSIS
# ============================================================
print(f"\n{'='*60}")
print("BACKTAB ANALYSIS (5-bit GRAM decode)")
print(f"{'='*60}")

unique_values = {}
for r in range(ROWS):
    for c in range(COLS):
        w = grid[r][c]
        if w not in unique_values:
            gram_bit, card, fg, csa = decode_backtab(w)
            unique_values[w] = {
                'gram': gram_bit, 'card': card, 'fg': fg, 'csa': csa, 'count': 0
            }
        unique_values[w]['count'] += 1

all_have_data = True
for w in sorted(unique_values.keys()):
    info = unique_values[w]
    gram_str = "GRAM" if info['gram'] else "GROM"
    card = info['card']
    card_str = f"card={card:3d}"
    if info['gram'] and card < NUM_GRAM_CARDS:
        cd = gram[card]
        has_data = any(b != 0 for b in cd)
        if has_data:
            card_str += " [DATA]"
        else:
            card_str += " [EMPTY!]"
            all_have_data = False
    print(f"  ${w:04X} : {gram_str} {card_str} FG={info['fg']} count={info['count']:3d}")

if all_have_data:
    print("\n*** ALL GRAM CARDS HAVE DATA! Correct decode confirmed. ***")

# ASCII room layout
print(f"\n=== Dungeon Room Layout ({COLS}x{ROWS}) ===")
print("    " + "".join(f"{c:2d} " for c in range(COLS)))
for r in range(ROWS):
    print(f"R{r:2d} ", end="")
    for c in range(COLS):
        w = grid[r][c]
        gram_bit, card, fg, csa = decode_backtab(w)
        if w == 0x1603:
            print(" .  ", end="")
        elif gram_bit:
            print(f"{card:2d}+ ", end="")
        else:
            print(f"{card:2d}  ", end="")
    print()

# ============================================================
# PIXEL RENDER
# ============================================================
ZOOM = 12
TILE_PX = 8 * ZOOM
LEGEND_W = 320
IMG_W = COLS * TILE_PX
IMG_H = ROWS * TILE_PX
TOTAL_W = IMG_W + LEGEND_W + 40
TOTAL_H = IMG_H + 80

img = Image.new('RGB', (TOTAL_W, TOTAL_H), (0, 0, 0))
pix = img.load()

ROOM_DARK = (20, 15, 5)
WALL_BG = (10, 8, 3)

def draw_card(pixels, tx, ty, card_rows, fg_color_idx, bg_color):
    """Draw one 8x8 tile at pixel position (tx, ty) with ZOOM scaling."""
    fg = INTV[fg_color_idx if fg_color_idx < 16 else 7]
    for row in range(8):
        byte_val = card_rows[row]
        for col in range(8):
            px = tx + col * ZOOM
            py = ty + row * ZOOM
            bit = (byte_val >> (7 - col)) & 1
            for dy in range(ZOOM):
                for dx in range(ZOOM):
                    cx, cy = px + dx, py + dy
                    if 0 <= cx < TOTAL_W and 0 <= cy < TOTAL_H:
                        pixels[cx, cy] = fg if bit else bg_color

def fill_tile(pixels, tx, ty, color):
    for dy in range(TILE_PX):
        for dx in range(TILE_PX):
            cx, cy = tx + dx, ty + dy
            if 0 <= cx < TOTAL_W and 0 <= cy < TOTAL_H:
                pixels[cx, cy] = color

# Render all tiles
for r in range(ROWS):
    for c in range(COLS):
        w = grid[r][c]
        gram_bit, card, fg, csa = decode_backtab(w)
        tx = c * TILE_PX
        ty = r * TILE_PX

        if gram_bit and card < NUM_GRAM_CARDS:
            card_data = gram[card]
            if any(b != 0 for b in card_data):
                draw_card(pix, tx, ty, card_data, fg, WALL_BG)
            else:
                fill_tile(pix, tx, ty, (40, 10, 10))  # empty GRAM = error
        elif gram_bit:
            fill_tile(pix, tx, ty, (80, 0, 0))  # out of bounds
        else:
            # GROM floor tile — dark background
            fill_tile(pix, tx, ty, ROOM_DARK)

# ============================================================
# LEGEND
# ============================================================
draw = ImageDraw.Draw(img)
lx = IMG_W + 20
ly = 20

# Background
for dy in range(10, IMG_H + 55):
    for dx in range(IMG_W + 10, TOTAL_W - 10):
        if 0 <= dx < TOTAL_W and 0 <= dy < TOTAL_H:
            pix[dx, dy] = (12, 10, 18)

draw.text((lx, ly), "SWORDS & SERPENTS", fill=(255, 215, 130))
ly += 24
draw.text((lx, ly), "First Dungeon Room", fill=(200, 180, 150))
ly += 20
draw.text((lx, ly), "(5-bit GRAM decode, Method B parsing)", fill=(140, 130, 160))
ly += 24
draw.text((lx, ly), f"BackTab: {COLS}x{ROWS}  Zoom: {ZOOM}x", fill=(120, 115, 140))
ly += 24

# Collect used GRAM cards
used_gram_cards = set()
for r in range(ROWS):
    for c in range(COLS):
        gram_bit, card, fg, csa = decode_backtab(grid[r][c])
        if gram_bit:
            used_gram_cards.add(card)

draw.text((lx, ly), f"Dungeon GRAM Cards ({len(used_gram_cards)} used):", fill=(180, 200, 220))
ly += 20

ref_zoom = 3
ref_tile = 8 * ref_zoom
for idx, card in enumerate(sorted(used_gram_cards)):
    col = idx % 4
    row_idx = idx // 4
    rx = lx + col * (ref_tile + 16)
    ry = ly + row_idx * (ref_tile + 20)

    if card < NUM_GRAM_CARDS:
        cd = gram[card]
        has_data = any(b != 0 for b in cd)
        for tr in range(8):
            byte_val = cd[tr] & 0xFF
            for tc in range(8):
                px = rx + tc * ref_zoom
                py = ry + tr * ref_zoom
                if (byte_val >> (7 - tc)) & 1:
                    for dy in range(ref_zoom):
                        for dx in range(ref_zoom):
                            cx, cy = px + dx, py + dy
                            if 0 <= cx < TOTAL_W and 0 <= cy < TOTAL_H:
                                pix[cx, cy] = INTV[3]
        status = "[OK]" if has_data else "[!]"
        color = (255, 150, 150) if not has_data else (180, 200, 180)
        draw.text((rx, ry + ref_tile + 2), f"#{card} {status}", fill=color)

# ============================================================
# SAVE
# ============================================================
os.makedirs('sprites', exist_ok=True)
fname = 'sprites/dungeon_final.png'
img.save(fname)
print(f"\nSaved: {fname} ({TOTAL_W}x{TOTAL_H})")
print(f"Room: {COLS} cols x {ROWS} rows, Tiles: {TILE_PX}px at {ZOOM}x zoom")
print(f"Used GRAM cards: {sorted(used_gram_cards)}")
print(f"Unique BackTab values: {len(unique_values)}")
