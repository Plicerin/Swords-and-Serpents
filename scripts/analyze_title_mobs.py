#!/usr/bin/env python3
"""Parse STIC MOB registers + GRAM dump, render GRAM cards, identify warrior sprite."""
from PIL import Image, ImageDraw, ImageFont
import os

# ========== PARSE DATA ==========

# STIC registers ($0000-$003F) as raw byte pairs from jzintv 'm 0 40' output
# CP-1600 memory: word at addr N has low byte at N, high byte at N+1 (little-endian)
# jzintv displays 16-bit words as hex; we parse word then split into bytes.

stic_lines = {
    0x0000: [0x3B58, 0x3B60, 0x3800, 0x384A, 0x3800, 0x3800, 0x3800, 0x3800],
    0x0008: [0x30B8, 0x30B8, 0x30D2, 0x3089, 0x3000, 0x3000, 0x3000, 0x3000],
    0x0010: [0x1980, 0x2996, 0x09A7, 0x09B6, 0x09C0, 0x09D0, 0x09E0, 0x09F0],
    0x0018: [0x3C00, 0x3C00, 0x3C00, 0x3C00, 0x3C00, 0x3C00, 0x3C00, 0x3C00],
}

# Build byte array from words (little-endian: even addr = low byte, odd addr = high byte)
stic_bytes = {}
for base_addr, words in stic_lines.items():
    for i, word in enumerate(words):
        addr = base_addr + i * 2
        stic_bytes[addr] = word & 0xFF          # low byte
        stic_bytes[addr + 1] = (word >> 8) & 0xFF  # high byte

# Decode MOB registers
print("=== STIC MOB REGISTERS ===")
mobs = []
for m in range(8):
    x = stic_bytes.get(m * 4, 0)
    y = stic_bytes.get(m * 4 + 1, 0)
    a = stic_bytes.get(m * 4 + 2, 0)
    col = stic_bytes.get(m * 4 + 3, 0)
    card = a & 0x3F  # bits 0-5
    gram_flag = (a >> 6) & 1  # bit 6
    grom_flag = (a >> 7) & 1  # bit 7 (or color mode)
    mobs.append({'x': x, 'y': y, 'a': a, 'card': card, 'col': col})
    
    card_type = "GROM" if grom_flag else "GRAM"
    active = "ACTIVE" if x != 0 else "hidden"
    print(f"  MOB {m}: X={x:3d}(${x:02X}) Y={y:3d}(${y:02X}) A=${a:02X} -> card ${card:02X}({card:2d}) [{card_type}] {active}")

# ========== GRAM DUMP ==========
# From jzintv 'm 3800 200' output
gram_lines_raw = """
3800: 0040 0020 00FD 007F  003B 001E 0024 0008
3808: 00F0 00F0 0070 0020  0020 0000 0000 0000
3810: 0000 0000 0080 0080  00D0 00D0 00F0 00F0
3818: 00F0 00F8 00E8 0078  00F0 00F8 00F8 00F8
3820: 00F7 00FF 00FF 00FF  00EF 00E6 0000 0000
3828: 00EF 00FF 007F 00FF  00FF 00FD 00F8 00F8
3830: 00F0 00F8 00E8 00F8  00F0 00B8 0000 0000
3838: 0080 00C0 00E0 00E0  00E0 00E0 00E0 00E0
3840: 00FF 007F 0000 0000  0000 0000 0000 0000
3848: 00E0 00EC 00ED 00ED  00ED 00ED 00EC 00E0
3850: 00E0 00EC 00ED 00ED  00ED 00ED 00EC 00E0
3858: 007F 002E 003A 0036  006C 0074 005C 00FE
3860: 00FF 0000 00FF 00FE  00FE 00FF 0000 00FF
3868: 00AB 00AB 00AB 00AA  00AA 00AB 00AB 00AB
3870: 0000 0000 0087 009D  00FD 003F 0018 003C
3878: 0042 0081 0099 00BD  005A 0024 00DB 007E
3880: 0000 0018 0024 0018  00BD 00FF 00A5 00FF
3888: 0000 003C 004A 00D1  0085 00A9 004A 003C
3890: 00FF 00F9 00F3 00E7  00CF 007E 003C 0018
3898: 0099 00BD 00BD 00FF  0042 0066 0066 0024
38A0: 00C1 0055 007F 0055  0055 0055 0055 003E
38A8: 0018 003C 0018 003C  006E 00DF 006E 003C
38B0: 0000 0000 0040 00BF  0045 0000 0000 0000
38B8: 003C 0042 0099 0091  0091 0099 0042 003C
38C0: 0000 0078 001E 00FC  0018 0018 0031 0073
38C8: 0000 0000 0010 003B  007F 00FF 00FF 00FF
38D0: 000F 003C 00F8 00F0  00E2 00CA 009F 0039
38D8: 0000 0009 0095 00FF  00FF 0095 0009 0000
38E0: 0000 0083 001F 00FD  00FD 001F 0083 0000
38E8: 00F1 00DF 00BE 0076  0076 00BE 00DF 00F1
38F0: 0000 0006 000F 0099  00F3 00E6 000C 0000
38F8: 0073 0031 0018 0018  00FC 001E 0078 0000
3900: 00FF 00FF 00FF 007F  003B 0010 0000 0000
3908: 0039 009F 00CA 00E2  00F0 00F8 003C 000F
3910: 0000 0000 0000 0000  0000 0000 0000 0000
3918: 0000 0000 0000 0000  0000 0000 0000 0000
3920: 0000 0000 0000 0000  0000 0000 0000 0000
3928: 0000 0000 0000 0000  0000 0000 0000 0000
3930: 0000 0000 0000 0000  0000 0000 0000 0000
3938: 0000 0000 0000 0000  0000 0000 0000 0000
3940: 0000 0000 0000 0000  0000 0000 0000 0000
3948: 0000 0000 0000 0000  0000 0000 0000 0000
3950: 0000 0000 0000 0000  0000 0000 0000 0000
3958: 0000 0000 0000 0000  0000 0000 0000 0000
3960: 0000 0000 0000 0000  0000 0000 0000 0000
3968: 0000 0000 0000 0000  0000 0000 0000 0000
3970: 0000 0000 0000 0000  0000 0000 0000 0000
3978: 0000 0000 0000 0000  0000 0000 0000 0000
3980: 0018 003C 007E 0073  00F9 0099 0089 0089
3988: 0089 0089 0099 00F9  0073 007E 003C 0018
3990: 0000 0000 0000 0000  0000 0000 0000 00FF
3998: 0000 0000 0000 0000  0000 0000 0000 0000
39A0: 0000 0000 0000 0000  0018 0024 003C 0066
39A8: 0066 003C 0024 0018  0000 0000 0000 0000
39B0: 0000 0024 0011 003A  00AE 007B 006E 00FE
39B8: 007F 007C 00FE 005C  0088 0024 0000 0000
39C0: 0000 0000 0000 0000  0000 0000 0000 0000
39C8: 0000 0000 0000 0000  0000 0000 0000 0000
39D0: 0000 0000 0000 0000  0000 0000 0000 0000
39D8: 0000 0000 0000 0000  0000 0000 0000 0000
39E0: 0000 0000 0000 0000  0000 0000 0000 0000
39E8: 0000 0000 0000 0000  0000 0000 0000 0000
39F0: 0000 0000 0000 0000  0000 0000 0000 0000
39F8: 0000 0000 0000 0000  0000 0000 0000 0000
"""

# Parse GRAM
gram = {}
for line in gram_lines_raw.strip().split('\n'):
    line = line.strip()
    if not line:
        continue
    parts = line.split(':')
    if len(parts) != 2:
        continue
    try:
        addr = int(parts[0].strip(), 16)
    except:
        continue
    bytes_str = parts[1].strip().split()
    byte_vals = [int(b.strip(), 16) for b in bytes_str]
    
    # Each value is a 16-bit word; we need individual bytes
    # CP-1600 little-endian: first 2 hex digits = high byte, last 2 = low byte
    # But in GRAM, each byte IS 8 bits, stored as the low byte of a 16-bit word
    # (high byte typically 0). The jzintv dump shows the full 16-bit word.
    # For GRAM, the meaningful data is the LOW BYTE of each word.
    for i, word in enumerate(byte_vals):
        byte_addr = addr + i * 2
        gram[byte_addr] = word & 0xFF  # low byte is the GRAM data

# ========== INTELLIVISION COLOR PALETTE ==========
INTV_COLORS = [
    (0, 0, 0),        # 0: Black
    (0, 0, 255),      # 1: Blue
    (200, 40, 40),    # 2: Red
    (200, 160, 40),   # 3: Tan/Gold
    (0, 128, 0),      # 4: Dark Green
    (0, 255, 0),      # 5: Green
    (255, 255, 0),    # 6: Yellow
    (255, 255, 255),  # 7: White
    (128, 128, 128),  # 8: Gray
    (0, 255, 255),    # 9: Cyan
    (255, 128, 0),    # 10: Orange
    (128, 64, 0),     # 11: Brown
    (255, 0, 255),    # 12: Magenta
    (128, 128, 255),  # 13: Light Blue
    (255, 255, 128),  # 14: Yellow-Green
    (128, 0, 255),    # 15: Purple
]

# For sprites, typical foreground/background color pairing:
# MOB A register bit 7 selects color mode; bit 6 may be GROM/GRAM flag
# Colors 0-7 are foreground (with bit 7=0) or colors 8-15 (with bit 7=1? dep on mode)
# For title screen sprites, we'll use tan/gold (color 3) on black (color 0)

def draw_card_8x8(data, fg_color, bg_color, scale=1):
    """Draw a single 8x8 GRAM card."""
    img = Image.new('RGBA', (8, 8))
    for row in range(8):
        byte_val = data[row] if row < len(data) else 0
        for col in range(8):
            bit = (byte_val >> (7 - col)) & 1
            color = fg_color if bit else bg_color
            img.putpixel((col, row), (*color, 255))
    if scale > 1:
        img = img.resize((8 * scale, 8 * scale), Image.NEAREST)
    return img


def get_card_data(card_num):
    """Get 8 bytes for a GRAM card number."""
    base = 0x3800 + card_num * 8
    data = [gram.get(base + i, 0) for i in range(8)]
    return data


# ========== RENDER ALL 64 GRAM CARDS AS TILE SHEET ==========
TILE = 12  # pixel size per tile
GAP = 4
COLS = 8
ROWS = 8

W = COLS * (TILE + GAP) + GAP + 200  # extra space for labels
H = ROWS * (TILE + GAP) + GAP + 40

all_cards = Image.new('RGBA', (W, H), (20, 20, 30, 255))
draw = ImageDraw.Draw(all_cards)

try:
    font = ImageFont.truetype("arial.ttf", 10)
except:
    font = ImageFont.load_default()

for c in range(64):
    col = c % COLS
    row = c // COLS
    x = GAP + col * (TILE + GAP)
    y = GAP + row * (TILE + GAP)
    
    data = get_card_data(c)
    # Use color 3 (tan/gold) on black for visibility
    card_img = draw_card_8x8(data, INTV_COLORS[3], INTV_COLORS[0], 1)
    card_img = card_img.resize((TILE, TILE), Image.NEAREST)
    all_cards.paste(card_img, (x, y))
    
    # Highlight cards used by MOBs
    for m in mobs:
        if m['card'] == c:
            draw.rectangle([x-1, y-1, x+TILE, y+TILE], outline=(255, 255, 0, 200), width=1)
            draw.text((x + TILE + 2, y + TILE//2 - 5), f"M{m}", fill=(255, 255, 0, 255), font=font)

# Labels
for c in range(64):
    col = c % COLS
    row = c // COLS
    x = GAP + col * (TILE + GAP)
    y = GAP + row * (TILE + GAP) + TILE + 2
    draw.text((x, y), f"{c:02d}", fill=(150, 150, 150, 255), font=font)

# Right side: MOB info
info_x = COLS * (TILE + GAP) + GAP + 10
draw.text((info_x, 10), "MOB Assignments:", fill=(255, 255, 255, 255), font=font)
for i, m in enumerate(mobs):
    y = 30 + i * 20
    active = "ACTIVE" if m['x'] != 0 else "hidden"
    color = (0, 255, 0) if m['x'] != 0 else (100, 100, 100)
    draw.text((info_x, y), f"MOB{i}: X={m['x']:3d} Y={m['y']:3d} card={m['card']:02d} [{active}]", fill=color, font=font)

os.makedirs('sprites', exist_ok=True)
all_cards.save('sprites/all_gram_cards.png')
print(f"\nSaved: sprites/all_gram_cards.png ({W}x{H})")

# ========== RENDER SPRITE CARDS INDIVIDUALLY ==========
# Cards used by active MOBs and their neighbors for 16-wide sprites
active_cards = set()
for m in mobs:
    if m['x'] != 0:  # active
        active_cards.add(m['card'])
        active_cards.add(m['card'] + 1)  # potential paired card

print(f"\nActive MOB cards: {sorted(active_cards)}")

# Render each active card at large scale
BIG = 16
for card_num in sorted(active_cards):
    data = get_card_data(card_num)
    img = draw_card_8x8(data, INTV_COLORS[3], INTV_COLORS[0], BIG)
    
    # Add label
    labeled = Image.new('RGBA', (8*BIG + 60, 8*BIG + 20), (30, 30, 40, 255))
    labeled.paste(img, (2, 2))
    d = ImageDraw.Draw(labeled)
    d.text((2, 8*BIG + 4), f"Card ${card_num:02X} ({card_num})", fill=(255,255,200,255), font=font)
    labeled.save(f'sprites/card_{card_num:02d}.png')

# ========== RENDER 16x16 2-MOB SPRITE ==========
# Try pairing MOBs that are at similar Y positions
print("\n=== POTENTIAL MOB PAIRS (16-wide sprites) ===")
pairs = []
for i in range(0, 8, 2):
    m0 = mobs[i]
    m1 = mobs[i + 1]
    if m0['x'] != 0 or m1['x'] != 0:
        y_diff = abs(m0['y'] - m1['y'])
        print(f"  MOB{i}+MOB{i+1}: Y0={m0['y']} Y1={m1['y']} diff={y_diff} cards=({m0['card']},{m1['card']})")
        
        # Render the pair as 16-wide sprite
        left_card = get_card_data(m0['card'])
        right_card = get_card_data(m1['card'])
        
        Z = 16  # zoom
        pair_img = Image.new('RGBA', (16 * Z + 20, 8 * Z + 40), (40, 40, 50, 255))
        
        # Left MOB (card m0)
        l_img = draw_card_8x8(left_card, INTV_COLORS[3], INTV_COLORS[0], Z)
        pair_img.paste(l_img, (2, 2))
        
        # Right MOB (card m1)  
        r_img = draw_card_8x8(right_card, INTV_COLORS[3], INTV_COLORS[0], Z)
        pair_img.paste(r_img, (2 + 8*Z + 2, 2))
        
        # Divider
        d = ImageDraw.Draw(pair_img)
        d.line([(2 + 8*Z, 2), (2 + 8*Z, 2 + 8*Z)], fill=(255,255,0,128), width=1)
        d.text((4, 8*Z + 6), f"MOB{i}(c{m0['card']}) + MOB{i+1}(c{m1['card']})  Y diff={y_diff}", fill=(200,200,200,255), font=font)
        
        pair_img.save(f'sprites/pair_{i}_{i+1}.png')
        print(f"  → saved sprites/pair_{i}_{i+1}.png")

# ========== TAG MOBs on user screenshot ==========
try:
    ss = Image.open('sprites/user_screenshot.png')
    ss_w, ss_h = ss.size
    print(f"\nUser screenshot: {ss_w}x{ss_h}")
    
    # Create annotated version
    ann = ss.copy()
    d = ImageDraw.Draw(ann)
    
    # MOB positions: X is pixel position, Y is row (×2 for pixel approx?)
    # STIC Y position maps to scanline pairs? Y * 2 approx
    for i, m in enumerate(mobs):
        if m['x'] == 0:
            continue
        # Convert STIC coordinates to approximate pixel position on screenshot
        px = m['x']  # approximate - X is in pixels
        py = m['y'] * 2  # approximate - Y in card-rows, ~2 px per row
        # Scale to screenshot size
        r = 6
        d.ellipse([px-r, py-r, px+r, py+r], outline=(255, 0, 0), width=1)
        d.text((px + 8, py - 4), f"MOB{i}\nc{m['card']}", fill=(255, 255, 0), font=font)
    
    ann.save('sprites/screenshot_tagged.png')
    print("Saved: sprites/screenshot_tagged.png")
except Exception as e:
    print(f"Could not annotate screenshot: {e}")

print("\n=== DONE ===")
print("Key files:")
print("  sprites/all_gram_cards.png - All 64 GRAM cards with MOB assignments")
print("  sprites/pair_*.png - 16-wide MOB pair renders")
for c in sorted(active_cards):
    if c < 64:
        print(f"  sprites/card_{c:02d}.png - Card ${c:02X}")
