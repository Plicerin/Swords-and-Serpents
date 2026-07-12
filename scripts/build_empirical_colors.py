#!/usr/bin/env python3
"""Build empirical per-word color map from jzIntv screenshot, then
determine optimal Color Stack entries and FG mapping."""

import sys
sys.path.insert(0, '.')
from render_all_rooms import (
    load_grom, parse_backtab, extract_backtab_from_output,
    extract_gram_from_output, parse_memory_dump,
    extract_memory_section, parse_mobs,
    PALETTE, PASTEL_PALETTE, DEFAULT_BG,
)
from PIL import Image
from collections import defaultdict, Counter

# Load data
with open('traces/_cmp_room_0_out.txt', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

grid = parse_backtab(extract_backtab_from_output(content))
gram_text = extract_gram_from_output(content)
gram_mem = parse_memory_dump(gram_text, 0x3800, 512) if gram_text else {}
sysram_text = extract_memory_section(content, 0x0300, 0x0360)
mobs = parse_mobs(sysram_text) if sysram_text else []
grom = load_grom()

scr = Image.open('sprites/room_0_jzintv.gif')
scr_w, scr_h = scr.size
jz_pal = scr.getpalette()
jz_px = scr.load()

def jz_rgb(idx):
    if idx * 3 + 2 < len(jz_pal):
        return (jz_pal[idx*3], jz_pal[idx*3+1], jz_pal[idx*3+2])
    return (0,0,0)

def cn(rgb):
    for d, lbl in [(PALETTE, 'PAL'), (PASTEL_PALETTE, 'PAS')]:
        for k, v in d.items():
            if v == rgb: return '%s[%d]' % (lbl, k)
    if rgb == (0,0,0): return 'BLK'
    return 'RGB'+str(rgb)

JLEFT, JTOP = 80, 52

# ======================================================================
# Step 1: For each tile, extract dominant bit0 and bit1 colors from jzIntv
# ======================================================================
print("=" * 90)
print("STEP 1: Extract per-tile empirical colors")
print("=" * 90)

tile_colors = {}  # (row, col) -> (bit0_dom_rgb, bit1_dom_rgb, is_transparent)

for row in range(12):
    for col in range(20):
        word = grid[row][col]
        card_idx = word & 0xFF
        is_gram = bool(word & 0x0800)

        if is_gram:
            baddr = 0x3800 + (card_idx & 0x3F) * 8
            card_bytes = bytes(gram_mem.get(baddr + ry, 0) & 0xFF for ry in range(8))
        else:
            baddr = card_idx * 8
            card_bytes = grom[baddr:baddr+8] if baddr+8 <= len(grom) else bytes(8)

        bit0_colors = Counter()
        bit1_colors = Counter()
        for y in range(8):
            by = card_bytes[y]
            for x in range(8):
                bit = (by >> (7-x)) & 1
                jx = JLEFT + col*8 + x
                jy = JTOP + row*8 + y
                if jx < scr_w and jy < scr_h:
                    rgb = jz_rgb(jz_px[jx, jy])
                    if bit == 0:
                        bit0_colors[rgb] += 1
                    else:
                        bit1_colors[rgb] += 1

        bit0_dom = bit0_colors.most_common(1)[0] if bit0_colors else (None, 0)
        bit1_dom = bit1_colors.most_common(1)[0] if bit1_colors else (None, 0)
        is_transparent = (bit0_dom[0] == bit1_dom[0])

        tile_colors[(row, col)] = (bit0_dom[0], bit1_dom[0], is_transparent)

# ======================================================================
# Step 2: Group by BACKTAB word - what's the consensus?
# ======================================================================
print()
print("=" * 90)
print("STEP 2: Per-word empirical color map")
print("=" * 90)

word_data = defaultdict(list)
for (row, col), (b0, b1, transp) in tile_colors.items():
    word = grid[row][col]
    word_data[word].append((row, col, b0, b1, transp))

print(f"{'Word':>6s} {'Card':>5s} {'G?':>3s} {'b12':>3s} {'b13':>3s} {'N':>3s} {'Transp%':>7s} {'bit0_dom':>14s} {'bit1_dom':>14s}")
print("-" * 90)

word_map = {}  # word -> (fg_rgb, bg_behavior, is_transparent_consensus)

for word, instances in sorted(word_data.items()):
    n = len(instances)
    transp_count = sum(1 for _, _, _, _, t in instances if t)
    transp_pct = transp_count / n * 100

    # Most common bit0 and bit1 colors across all instances
    b0_colors = Counter(b0 for _, _, b0, _, _ in instances if b0 is not None)
    b1_colors = Counter(b1 for _, _, _, b1, _ in instances if b1 is not None)
    b0_dom = b0_colors.most_common(1)[0][0] if b0_colors else None
    b1_dom = b1_colors.most_common(1)[0][0] if b1_colors else None

    card = word & 0xFF
    is_gram = bool(word & 0x0800)
    b12 = (word >> 12) & 1
    b13 = (word >> 13) & 1

    print(f"0x{word:04X} {card:5d} {'Y' if is_gram else 'N':>3s} {b12:3d} {b13:3d} {n:3d} {transp_pct:6.1f}% {cn(b0_dom):>14s} {cn(b1_dom):>14s}")

    # Determine consensus
    if transp_pct >= 80:
        behavior = 'transparent'
    elif transp_pct <= 20:
        behavior = 'opaque'
    else:
        behavior = 'mixed'

    word_map[word] = {
        'card': card,
        'is_gram': is_gram,
        'b12': b12,
        'b13': b13,
        'bit0_dom': b0_dom,
        'bit1_dom': b1_dom,
        'behavior': behavior,
        'transp_pct': transp_pct,
        'n': n,
    }

# ======================================================================
# Step 3: Determine optimal Color Stack entries
# ======================================================================
print()
print("=" * 90)
print("STEP 3: Determine optimal CS entries by simulating CS advance")
print("=" * 90)

# For transparent tiles: all pixels = CS background color
# For opaque tiles: bit0 = CS background, bit1 = FG color
# CS advances on b13=1

# Collect background colors from transparent tiles
# Group by CS position (counting b13=1 advances before each tile)
cs_bg_samples = defaultdict(list)  # cs_pos -> [rgb_colors]

cs = 0
for row in range(12):
    for col in range(20):
        word = grid[row][col]
        b13 = (word >> 13) & 1
        b0, b1, transp = tile_colors[(row, col)]

        if transp and b0 is not None:
            cs_bg_samples[cs].append(b0)

        if b13:
            cs = (cs + 1) % 4

print("Background color samples per CS position:")
for cs_pos in range(4):
    samples = cs_bg_samples.get(cs_pos, [])
    color_counts = Counter(samples)
    print(f"  CS[{cs_pos}]: {len(samples)} samples")
    for rgb, count in color_counts.most_common(5):
        print(f"    {cn(rgb)}: {count} ({count/len(samples)*100:.0f}%)" if samples else f"    (no samples)")

# Build optimal CS
optimal_cs = []
for cs_pos in range(4):
    samples = cs_bg_samples.get(cs_pos, [])
    if samples:
        optimal_cs.append(Counter(samples).most_common(1)[0][0])
    else:
        optimal_cs.append(PASTEL_PALETTE[3])  # default

print()
print("Optimal CS entries:")
for i, rgb in enumerate(optimal_cs):
    print(f"  CS[{i}] = {cn(rgb)}")

# ======================================================================
# Step 4: Determine FG color for opaque tiles
# ======================================================================
print()
print("=" * 90)
print("STEP 4: FG colors for opaque tiles")
print("=" * 90)

fg_by_word = {}
for word, info in word_map.items():
    if info['behavior'] == 'opaque':
        # For opaque tiles, bit1 = FG color
        b13 = info['b13']
        b12 = info['b12']
        fg = info['bit1_dom']
        fg_by_word[word] = fg
        print(f"  0x{word:04X} (b12={b12}, b13={b13}): FG = {cn(fg)}")

# ======================================================================
# Step 5: Accuracy test with optimal CS + empirical FG
# ======================================================================
print()
print("=" * 90)
print("STEP 5: Accuracy test with optimal CS + empirical FG")
print("=" * 90)

match = 0
total = 0
cs = 0

for row in range(12):
    for col in range(20):
        word = grid[row][col]
        b13 = (word >> 13) & 1
        b12 = (word >> 12) & 1
        b0, b1, transp = tile_colors[(row, col)]

        info = word_map.get(word, {})
        behavior = info.get('behavior', 'unknown')
        
        # Determine expected colors
        if behavior == 'transparent':
            exp_b0 = optimal_cs[cs]
            exp_b1 = optimal_cs[cs]
        elif behavior == 'opaque':
            exp_b0 = optimal_cs[cs]
            exp_b1 = fg_by_word.get(word, PALETTE[7])
        else:
            # Mixed - use CS for bg, empirical for fg
            exp_b0 = optimal_cs[cs]
            exp_b1 = b1 if b1 is not None else optimal_cs[cs]

        # Advance CS for next tile (after rendering current)
        if b13:
            cs = (cs + 1) % 4

        # Count pixel matches
        card_idx = word & 0xFF
        is_gram = bool(word & 0x0800)
        if is_gram:
            baddr = 0x3800 + (card_idx & 0x3F) * 8
            card_bytes = bytes(gram_mem.get(baddr + ry, 0) & 0xFF for ry in range(8))
        else:
            baddr = card_idx * 8
            card_bytes = grom[baddr:baddr+8] if baddr+8 <= len(grom) else bytes(8)

        for y in range(8):
            by = card_bytes[y]
            for x in range(8):
                bit = (by >> (7-x)) & 1
                expected = exp_b1 if bit else exp_b0

                jx = JLEFT + col*8 + x
                jy = JTOP + row*8 + y
                if jx < scr_w and jy < scr_h:
                    actual = jz_rgb(jz_px[jx, jy])
                    total += 1
                    if expected == actual:
                        match += 1

acc = match / total * 100 if total > 0 else 0
print(f"  Accuracy: {acc:.1f}%  ({match}/{total} pixels)")

# ======================================================================
# Step 6: Print Python code for render_all_rooms.py
# ======================================================================
print()
print("=" * 90)
print("STEP 6: Code for render_all_rooms.py")
print("=" * 90)

cs_rgb = [optimal_cs[i] for i in range(4)]

print()
print("# Paste this into render_all_rooms.py:")
print(f"EMPIRICAL_CS = [")
for i, rgb in enumerate(cs_rgb):
    # Find which palette entry
    for name, pal in [('PALETTE', PALETTE), ('PASTEL_PALETTE', PASTEL_PALETTE)]:
        for k, v in pal.items():
            if v == rgb:
                print(f"    {name}[{k}],  # CS[{i}] = {cn(rgb)}")
                break
        else:
            continue
        break
    else:
        print(f"    ({rgb[0]}, {rgb[1]}, {rgb[2]}),  # CS[{i}] = custom")
print(f"]")

print()
print("# Empirical FG color map for opaque tiles:")
print("EMPIRICAL_FG = {")
for word, fg_rgb in sorted(fg_by_word.items()):
    if fg_rgb is None:
        print(f"    0x{word:04X}: None,  # no empirical FG (all pixels same)")
        continue
    found = False
    for name, pal in [('PALETTE', PALETTE), ('PASTEL_PALETTE', PASTEL_PALETTE)]:
        for k, v in pal.items():
            if v == fg_rgb:
                print(f"    0x{word:04X}: {name}[{k}],  # {cn(fg_rgb)}")
                found = True
                break
        if found:
            break
    if not found:
        print(f"    0x{word:04X}: ({fg_rgb[0]}, {fg_rgb[1]}, {fg_rgb[2]}),  # custom")
print("}")

print()
print("# Transparent words (all pixels = CS background):")
transparent_words = sorted(w for w, i in word_map.items() if i['behavior'] == 'transparent')
print(f"TRANSPARENT_WORDS = {{")
for w in transparent_words:
    print(f"    0x{w:04X},")
print(f"}}")
