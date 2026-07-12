#!/usr/bin/env python3
"""Analyze per-tile dominant colors from jzIntv screenshot for room 0."""
import sys
sys.path.insert(0, '.')
from render_all_rooms import (
    load_grom, parse_backtab, extract_backtab_from_output,
    PALETTE, PASTEL_PALETTE,
)
from PIL import Image
from collections import Counter, defaultdict

def cn(rgb):
    for d, lbl in [(PALETTE, 'PAL'), (PASTEL_PALETTE, 'PAS')]:
        for k, v in d.items():
            if v == rgb: return '%s[%d]' % (lbl, k)
    if rgb == (0,0,0): return 'BLK'
    return 'RGB'+str(rgb)

grom = load_grom()
with open('traces/_cmp_room_0_out.txt', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
grid = parse_backtab(extract_backtab_from_output(content))

scr = Image.open('sprites/room_0_jzintv.gif')
scr_w, scr_h = scr.size
jz_pal = scr.getpalette()
jz_px = scr.load()

def jz_rgb(idx):
    if idx * 3 + 2 < len(jz_pal):
        return (jz_pal[idx*3], jz_pal[idx*3+1], jz_pal[idx*3+2])
    return (0,0,0)

JLEFT, JTOP = 80, 52

# ============================================================
# PART 1: Per-tile dominant colors (GROM only)
# ============================================================
print('=== PER-TILE DOMINANT COLORS (GROM tiles) ===')
print(f'{"Pos":>6s} {"Word":>8s} {"Card":>5s} {"bit0_dom":>14s} {"bit1_dom":>14s} {"same?":>6s} {"b12":>4s} {"b13":>4s}')
print('-' * 90)

position_data = []  # list of (row, col, word, bit0_dom_rgb, bit1_dom_rgb, same)

for row in range(12):
    for col in range(20):
        w = grid[row][col]
        card_idx = w & 0xFF
        is_gram = bool(w & 0x0800)
        
        if is_gram:
            continue  # skip GRAM for now
        
        baddr = card_idx * 8
        if baddr + 8 > len(grom):
            continue
        card_bytes = grom[baddr:baddr+8]
        
        bit0_colors = {}
        bit1_colors = {}
        
        tx = JLEFT + col * 8
        ty = JTOP + row * 8
        
        for y in range(8):
            py = ty + y
            if py >= scr_h: continue
            byte_val = card_bytes[y]
            for x in range(8):
                px = tx + x
                if px >= scr_w: continue
                bit = (byte_val >> (7 - x)) & 1
                rgb = jz_rgb(jz_px[px, py])
                if bit == 0:
                    bit0_colors[rgb] = bit0_colors.get(rgb, 0) + 1
                else:
                    bit1_colors[rgb] = bit1_colors.get(rgb, 0) + 1
        
        b0 = sorted(bit0_colors.items(), key=lambda x: -x[1])
        b1 = sorted(bit1_colors.items(), key=lambda x: -x[1])
        b0_dom = b0[0] if b0 else (None, 0)
        b1_dom = b1[0] if b1 else (None, 0)
        same = 'YES' if b0_dom[0] == b1_dom[0] else 'NO'
        b12 = (w >> 12) & 1
        b13 = (w >> 13) & 1
        
        print(f'{row:2d},{col:<3d} 0x{w:04X} {card_idx:5d} {cn(b0_dom[0]):14s} {cn(b1_dom[0]):14s} {same:>6s} {b12:4d} {b13:4d}')
        position_data.append((row, col, w, b0_dom[0], b1_dom[0], same == 'YES'))

# ============================================================
# PART 2: Floor tiles (0x1603) by position
# ============================================================
print()
print('=== FLOOR TILES (0x1603) BY POSITION ===')
print(f'{"Pos":>6s} {"bit0_dom":>14s} {"bit1_dom":>14s} {"same?":>6s}')
floor_positions = []
for row in range(12):
    for col in range(20):
        w = grid[row][col]
        if w != 0x1603:
            continue
        card_bytes = grom[3*8:3*8+8]
        bit0_colors = {}
        bit1_colors = {}
        tx = JLEFT + col * 8
        ty = JTOP + row * 8
        for y in range(8):
            py = ty + y
            if py >= scr_h: continue
            byte_val = card_bytes[y]
            for x in range(8):
                px = tx + x
                if px >= scr_w: continue
                bit = (byte_val >> (7 - x)) & 1
                rgb = jz_rgb(jz_px[px, py])
                if bit == 0:
                    bit0_colors[rgb] = bit0_colors.get(rgb, 0) + 1
                else:
                    bit1_colors[rgb] = bit1_colors.get(rgb, 0) + 1
        b0 = sorted(bit0_colors.items(), key=lambda x: -x[1])
        b1 = sorted(bit1_colors.items(), key=lambda x: -x[1])
        b0_dom = b0[0] if b0 else (None, 0)
        b1_dom = b1[0] if b1 else (None, 0)
        same = 'YES' if b0_dom[0] == b1_dom[0] else 'NO'
        print(f'{row:2d},{col:<3d} {cn(b0_dom[0]):14s} {cn(b1_dom[0]):14s} {same:>6s}')
        floor_positions.append((row, col, b0_dom[0], b1_dom[0], same == 'YES'))

# ============================================================
# PART 3: Pattern analysis
# ============================================================
print()
print('=== PATTERN ANALYSIS ===')

# For floor tiles, what's the pattern of positions where bit0 != bit1?
differ_positions = [(r, c) for r, c, b0, b1, same in floor_positions if not same]
print(f'Floor tiles where bit0 != bit1: {differ_positions}')
print(f'Floor tiles where bit0 == bit1: {len(floor_positions) - len(differ_positions)}')

# For ALL GROM tiles, what words have bit0 != bit1?
print()
print('=== WORDS WITH bit0 != bit1 (opaque/colored FG) ===')
diff_words = defaultdict(list)
for row, col, w, b0, b1, same in position_data:
    if not same:
        diff_words[w].append((row, col, b0, b1))

for w in sorted(diff_words.keys()):
    positions = diff_words[w]
    b12 = (w >> 12) & 1
    b13 = (w >> 13) & 1
    b14 = (w >> 14) & 1
    b15 = (w >> 15) & 1
    fg_std = ((w >> 13) & 0x6) | ((w >> 12) & 0x1)
    # What's the dominant bit1 color?
    b1_colors = Counter(p[3] for p in positions)
    b1_dom = b1_colors.most_common(1)[0][0] if b1_colors else None
    b0_colors = Counter(p[2] for p in positions)
    b0_dom = b0_colors.most_common(1)[0][0] if b0_colors else None
    print(f'  0x{w:04X} card={w & 0xFF:3d} b15-12={b15}{b14}{b13}{b12} FG_std={fg_std} ')
    print(f'    bit0_dom={cn(b0_dom)} bit1_dom={cn(b1_dom)}')
    for r, c, b0, b1 in positions[:5]:
        print(f'      at ({r},{c}): bit0={cn(b0)} bit1={cn(b1)}')

# ============================================================
# PART 4: Row-by-row color summary
# ============================================================
print()
print('=== ROW-BY-ROW BACKGROUND COLOR PATTERN ===')
for row in range(12):
    # Most common bit0 color in this row (across all GROM tiles)
    row_b0 = Counter()
    row_b1 = Counter()
    for r, c, w, b0, b1, same in position_data:
        if r == row:
            if b0: row_b0[b0] += 1
            if b1: row_b1[b1] += 1
    b0_dom = row_b0.most_common(1)
    b1_dom = row_b1.most_common(1)
    b0_str = cn(b0_dom[0][0]) if b0_dom else 'N/A'
    b1_str = cn(b1_dom[0][0]) if b1_dom else 'N/A'
    print(f'  Row {row:2d}: bit0_dom={b0_str:14s} bit1_dom={b1_str:14s}')

# ============================================================
# PART 5: Build empirical per-word color map
# ============================================================
print()
print('=== EMPIRICAL PER-WORD COLOR MAP ===')
word_colors = {}
for row, col, w, b0, b1, same in position_data:
    if w not in word_colors:
        word_colors[w] = {'bit0': Counter(), 'bit1': Counter(), 'positions': []}
    if b0: word_colors[w]['bit0'][b0] += 1
    if b1: word_colors[w]['bit1'][b1] += 1
    word_colors[w]['positions'].append((row, col))

print(f'{"Word":>6s} {"card":>5s} {"bit0_dom":>14s} {"bit1_dom":>14s} {"transp?":>7s} {"positions":>10s}')
print('-' * 70)
for w in sorted(word_colors.keys()):
    d = word_colors[w]
    b0_dom = d['bit0'].most_common(1)
    b1_dom = d['bit1'].most_common(1)
    b0_rgb = b0_dom[0][0] if b0_dom else None
    b1_rgb = b1_dom[0][0] if b1_dom else None
    transparent = b0_rgb == b1_rgb
    print(f'0x{w:04X} {w & 0xFF:5d} {cn(b0_rgb):14s} {cn(b1_rgb):14s} {str(transparent):>7s} {len(d["positions"]):10d}')
