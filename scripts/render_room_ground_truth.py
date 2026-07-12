#!/usr/bin/env python3
"""
Render the first dungeon room using ACTUAL GRAM data captured from jzIntv.

KEY INSIGHT: The STIC reads GRAM as 16-bit words, using only the LOW BYTE
as each pixel row. The CPU writes 16-bit words via MVO@ with SDBD active.
So GRAM card N, row R = low byte of word at address $3800 + N*16 + R*2.
"""

from PIL import Image, ImageDraw
import os

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
# PARSE jzIntv GRAM DUMP into 64 cards × 8 rows
# ============================================================
# Each card = 8 16-bit words. STIC uses low byte of each word as pixel row.
gram_hex_dump = """3800:  0000  0028  007F  0018   002F  000D  0010  0000
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
3908:  0039  009F  00CA  00E2   00F0  00F8  003C  000F
3910:  0000  0000  0000  0000   0000  0000  0000  0000
3918:  0000  0000  0000  0000   0000  0000  0000  0000
3920:  0000  0000  0000  0000   0000  0000  0000  0000
3928:  0000  0000  0000  0000   0000  0000  0000  0000
3930:  0000  0000  0000  0000   0000  0000  0000  0000
3938:  0000  0000  0000  0000   0000  0000  0000  0000
3940:  0000  0000  0000  0000   0000  0000  0000  0000
3948:  0000  0000  0000  0000   0000  0000  0000  0000
3950:  0000  0000  0000  0000   0000  0000  0000  0000
3958:  0000  0000  0000  0000   0000  0000  0000  0000
3960:  0000  0000  0000  0000   0000  0000  0000  0000
3968:  0000  0000  0000  0000   0000  0000  0000  0000
3970:  0000  0000  0000  0000   0000  0000  0000  0000
3978:  0000  0000  0000  0000   0000  0000  0000  0000
3980:  0000  0000  0000  0000   0000  0000  0000  0000
3988:  0000  0000  0000  0000   0000  0000  0000  0000
3990:  0000  0000  0000  0000   0000  0000  0000  0000
3998:  0000  0000  0000  0000   0000  0000  0000  0000
39A0:  001E  003E  0033  007B   0079  00E8  0089  0089
39A8:  0089  008B  009A  00DA   00FE  007C  007C  001C
39B0:  0000  0000  0000  0000   0000  0006  000C  0030
39B8:  0060  00C0  0000  0000   0000  0000  0000  0000
39C0:  0081  0004  0040  0010   0000  0041  0000  0080
39C8:  0004  0000  0040  0004   0020  0000  0001  0080
39D0:  0000  0000  0000  0000   0000  0006  000C  0030
39D8:  0060  00C0  0000  0000   0000  0000  0000  0000
39E0:  0000  0000  0000  0000   0000  0000  0000  0000
39E8:  0000  0000  0000  0000   0000  0000  0000  0000
39F0:  0000  0000  0000  0000   0000  0000  0000  0000
39F8:  0000  0000  0000  0000   0000  0000  0000  0000"""

# Parse all 16-bit words into a flat list, indexed by word number (0-511 for $3800-$3FFF)
# 512 words = 64 cards × 8 words/card
words = [0] * 512
for line in gram_hex_dump.strip().split('\n'):
    parts = line.split()
    # Find base address
    base_addr = None
    cleaned_parts = []
    for p in parts:
        if p.endswith(':'):
            base_addr = int(p.replace(':', ''), 16)
        elif len(p) == 4 and all(c in '0123456789ABCDEFabcdef' for c in p):
            cleaned_parts.append(int(p, 16))
    
    if base_addr is None:
        continue
    
    for i, word_val in enumerate(cleaned_parts):
        word_addr = base_addr + i * 2
        if 0x3800 <= word_addr < 0x4000:
            word_num = (word_addr - 0x3800) // 2
            if word_num < 512:
                words[word_num] = word_val

# Extract 64 GRAM cards: card N row R = low byte of word N*8 + R
NUM_GRAM_CARDS = 64
gram_cards = []
for card_n in range(NUM_GRAM_CARDS):
    card_rows = []
    for row in range(8):
        word_num = card_n * 8 + row
        pixel_byte = words[word_num] & 0xFF  # low byte = pixel data
        card_rows.append(pixel_byte)
    gram_cards.append(card_rows)

# Show non-empty cards
non_empty = [(i, card) for i, card in enumerate(gram_cards) if any(b != 0 for b in card)]
print(f"GRAM cards with data: {len(non_empty)} out of {NUM_GRAM_CARDS}")
print(f"\nFirst 20 non-empty GRAM cards:")
for card_idx, card in non_empty[:20]:
    print(f"\nGRAM card {card_idx}:")
    for row_byte in card:
        line = ''.join('#' if (row_byte >> (7-i)) & 1 else '.' for i in range(8))
        print(f"  ${row_byte:02X}  {line}")

# ============================================================
# PARSE BACKTAB
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

for i, word in enumerate(flat_words):
    if i >= COLS * ROWS: break
    grid[i // COLS][i % COLS] = word

# ============================================================
# DECODE BACKTAB
# ============================================================
def decode_backtab(word):
    csa  = (word >> 13) & 1
    gram = (word >> 12) & 1
    fg   = word & 0x07
    if gram:
        card = (word >> 3) & 0x1F  # 5-bit GRAM card (0-31)
    else:
        card = (word >> 3) & 0xFF  # 8-bit GROM card
    return gram, card, fg, csa

# ============================================================
# ANALYSIS
# ============================================================
print(f"\n{'='*60}")
print("BACKTAB ANALYSIS with corrected GRAM low-byte extraction")
print(f"{'='*60}")

unique_values = {}
for r in range(ROWS):
    for c in range(COLS):
        w = grid[r][c]
        if w not in unique_values:
            gram, card, fg, csa = decode_backtab(w)
            unique_values[w] = {'gram': gram, 'card': card, 'fg': fg, 'csa': csa, 'count': 0}
        unique_values[w]['count'] += 1

for w in sorted(unique_values.keys()):
    info = unique_values[w]
    gram_str = "GRAM" if info['gram'] else "GROM"
    csa_str = "CSA" if info['csa'] else "   "
    card_str = f"card={info['card']:3d}"
    if info['gram'] and info['card'] < NUM_GRAM_CARDS:
        cd = gram_cards[info['card']]
        if any(b != 0 for b in cd):
            card_str += " [data]"
        else:
            card_str += " [EMPTY]"
    print(f"  ${w:04X} : {gram_str} {card_str} FG={info['fg']} {csa_str} count={info['count']:3d}")

# ASCII preview
print(f"\n=== Dungeon Room Layout ({COLS}x{ROWS}) ===")
print("    " + "".join(f"{c:2d} " for c in range(COLS)))
for r in range(ROWS):
    print(f"R{r:2d} ", end="")
    for c in range(COLS):
        w = grid[r][c]
        gram, card, fg, csa = decode_backtab(w)
        if gram:
            cd = gram_cards[card] if card < NUM_GRAM_CARDS else None
            has = cd and any(b != 0 for b in cd)
            print(f"\033[33m{card:2d}{'+' if has else '?'}\033[0m ", end="")
        else:
            print(f"\033[36m{card:2d}\033[0m ", end="")
    print()

# ============================================================
# PIXEL RENDER
# ============================================================
ZOOM = 12
TILE_PX = 8 * ZOOM
LEGEND_W = 300
IMG_W = COLS * TILE_PX
IMG_H = ROWS * TILE_PX
TOTAL_W = IMG_W + LEGEND_W + 40
TOTAL_H = IMG_H + 60

img = Image.new('RGB', (TOTAL_W, TOTAL_H), (0, 0, 0))
pix = img.load()

ROOM_DARK = (20, 15, 5)

def draw_card(pixels, tx, ty, card_rows, fg_color, bg_color):
    for row in range(8):
        byte_val = card_rows[row]
        for col in range(8):
            px = tx + col * ZOOM
            py = ty + row * ZOOM
            if (byte_val >> (7 - col)) & 1:
                for dy in range(ZOOM):
                    for dx in range(ZOOM):
                        cx, cy = px + dx, py + dy
                        if 0 <= cx < TOTAL_W and 0 <= cy < TOTAL_H:
                            pixels[cx, cy] = INTV[fg_color if fg_color < 16 else 7]
            elif bg_color is not None:
                for dy in range(ZOOM):
                    for dx in range(ZOOM):
                        cx, cy = px + dx, py + dy
                        if 0 <= cx < TOTAL_W and 0 <= cy < TOTAL_H:
                            pixels[cx, cy] = bg_color

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
        gram, card, fg, csa = decode_backtab(w)
        tx_px = c * TILE_PX
        ty_px = r * TILE_PX
        
        if gram and card < NUM_GRAM_CARDS:
            card_data = gram_cards[card]
            if any(b != 0 for b in card_data):
                draw_card(pix, tx_px, ty_px, card_data, fg, ROOM_DARK)
            else:
                fill_tile(pix, tx_px, ty_px, ROOM_DARK)
        elif gram:
            fill_tile(pix, tx_px, ty_px, (80, 0, 0))  # OOB
        else:
            fill_tile(pix, tx_px, ty_px, INTV[fg if fg < 16 else 7])

# ============================================================
# LEGEND
# ============================================================
draw = ImageDraw.Draw(img)
lx = IMG_W + 20
ly = 20

for dy in range(10, IMG_H + 30):
    for dx in range(IMG_W + 10, TOTAL_W - 10):
        if 0 <= dx < TOTAL_W and 0 <= dy < TOTAL_H:
            pix[dx, dy] = (12, 10, 18)

draw.text((lx, ly), "SWORDS & SERPENTS", fill=(255, 215, 130))
ly += 22
draw.text((lx, ly), "First Dungeon Room", fill=(200, 180, 150))
ly += 20
draw.text((lx, ly), "(GRAM: low-byte pixel extraction)", fill=(140, 130, 160))
ly += 24
draw.text((lx, ly), f"BackTab: {COLS}x{ROWS}  Zoom: {ZOOM}x", fill=(120, 115, 140))
ly += 22

draw.text((lx, ly), "Used GRAM Cards:", fill=(180, 200, 220))
ly += 18

used_cards = set()
for r in range(ROWS):
    for c in range(COLS):
        w = grid[r][c]
        gram, card, fg, csa = decode_backtab(w)
        if gram:
            used_cards.add(card)

ref_zoom = 3
ref_tile = 8 * ref_zoom
for idx, card in enumerate(sorted(used_cards)):
    col = idx % 3
    row_idx = idx // 3
    rx = lx + col * (ref_tile + 18)
    ry = ly + row_idx * (ref_tile + 20)
    
    if card < NUM_GRAM_CARDS:
        cd = gram_cards[card]
        has_data = any(b != 0 for b in cd)
        for tr in range(8):
            byte_val = cd[tr]
            for tc in range(8):
                px = rx + tc * ref_zoom
                py = ry + tr * ref_zoom
                if (byte_val >> (7 - tc)) & 1:
                    for dy in range(ref_zoom):
                        for dx in range(ref_zoom):
                            cx, cy = px + dx, py + dy
                            if 0 <= cx < TOTAL_W and 0 <= cy < TOTAL_H:
                                pix[cx, cy] = INTV[3]
        draw.text((rx, ry + ref_tile + 2), f"#{card}" + ("" if has_data else "?"), fill=(180, 180, 200))

# ============================================================
# SAVE
# ============================================================
os.makedirs('sprites', exist_ok=True)
fname = 'sprites/dungeon_corrected.png'
img.save(fname)
print(f"\nSaved: {fname} ({TOTAL_W}x{TOTAL_H})")

# Print GRAM card 0 explicitly
print("\n=== GRAM Card 0 (Floor Tile) ===")
if len(gram_cards) > 0:
    has_data = any(b != 0 for b in gram_cards[0])
    print(f"Has data: {has_data}")
    for row_byte in gram_cards[0]:
        line = ''.join('#' if (row_byte >> (7-i)) & 1 else '.' for i in range(8))
        print(f"  ${row_byte:02X}  {line}")
