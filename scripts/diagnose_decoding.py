#!/usr/bin/env python3
"""Diagnose BACKTAB decoding by testing hypotheses against jzIntv pixel data."""
import sys
sys.path.insert(0, '.')
from render_all_rooms import (
    load_grom, parse_backtab, extract_backtab_from_output,
    extract_gram_from_output, parse_memory_dump,
    PALETTE, PASTEL_PALETTE, DEFAULT_BG,
)
from PIL import Image

# Load data
with open('traces/_cmp_room_0_out.txt', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
grid = parse_backtab(extract_backtab_from_output(content))
gram_text = extract_gram_from_output(content)
gram_mem = parse_memory_dump(gram_text, 0x3800, 512) if gram_text else {}
grom = load_grom()

scr = Image.open('sprites/room_0_jzintv.gif')
jz_pal = scr.getpalette()
jz_px = scr.load()

def jz_rgb(idx):
    if idx * 3 + 2 < len(jz_pal):
        return (jz_pal[idx*3], jz_pal[idx*3+1], jz_pal[idx*3+2])
    return (0, 0, 0)

def cn(rgb):
    for d, lbl in [(PALETTE, 'PAL'), (PASTEL_PALETTE, 'PAS')]:
        for k, v in d.items():
            if v == rgb: return '%s[%d]' % (lbl, k)
    if rgb == (0,0,0): return 'BLACK'
    return str(rgb)

JLEFT, JTOP = 80, 52

def get_jz_pixels(row, col):
    """Get jzIntv pixels for tile at (row,col). Returns {color_rgb: count}."""
    colors = {}
    for y in range(8):
        for x in range(8):
            idx = jz_px[JLEFT + col*8 + x, JTOP + row*8 + y]
            rgb = jz_rgb(idx)
            colors[rgb] = colors.get(rgb, 0) + 1
    return colors

# ============================================================
# Hypothesis testing
# ============================================================

print("=" * 90)
print("BACKTAB DECODING HYPOTHESIS TESTS")
print("=" * 90)

# Get all unique words with their tile positions
tile_samples = {}
for row in range(12):
    for col in range(20):
        w = grid[row][col]
        if w not in tile_samples:
            tile_samples[w] = (row, col, [])

# Add all positions
for row in range(12):
    for col in range(20):
        w = grid[row][col]
        if w in tile_samples:
            tile_samples[w][2].append((row, col))

print(f"\nUnique BACKTAB words: {len(tile_samples)}")
print()

# For each word, try different decoding hypotheses
for w, (sample_row, sample_col, all_positions) in sorted(tile_samples.items()):
    # Get jzIntv pixel colors for this tile
    jz_colors = get_jz_pixels(sample_row, sample_col)
    
    # Get card bytes
    is_gram = bool(w & 0x0800)
    card_idx = w & 0xFF
    if is_gram:
        cidx = card_idx & 0x3F
        base = 0x3800 + cidx * 8
        card_bytes = bytes(gram_mem.get(base+r, 0) & 0xFF for r in range(8))
    else:
        cidx = card_idx & 0xFF
        base = cidx * 8
        card_bytes = grom[base:base+8] if base+8 <= len(grom) else bytes(8)
    
    # Count bits
    bits_set = sum(bin(b).count('1') for b in card_bytes)
    
    # Standard CS decode
    fg_std = ((w >> 13) & 0x6) | ((w >> 12) & 0x1)
    cs_adv = (w >> 13) & 1
    
    # Alternative decodings
    # Hyp A: FG = bit 12 only (from ANDI $3607)
    fg_a = (w >> 12) & 1
    
    # Hyp B: FG = bits 15,14,12 (standard CS but mapped differently)
    fg_b = ((w >> 13) & 0x6) | ((w >> 12) & 0x1)
    
    # Hyp C: FG = bits 14,13,12
    fg_c = (w >> 12) & 0x7
    
    # Hyp D: What if the word format is actually FG/BG mode bits?
    # FG/BG: bits 12-14 = FG color, bit 13 is NOT CS advance
    fg_d = (w >> 12) & 0x7
    bg_idx = w & 0x7
    bg_pastel = (w >> 3) & 1
    
    # What jzIntv colors actually appear?
    jz_color_list = ', '.join('%s:%d' % (cn(c), n) for c, n in sorted(jz_colors.items(), key=lambda x: -x[1]))
    
    # For bit=0 and bit=1 separately
    bit0_colors = {}
    bit1_colors = {}
    for y in range(8):
        b = card_bytes[y]
        for x in range(8):
            bit = (b >> (7-x)) & 1
            idx = jz_px[JLEFT + sample_col*8 + x, JTOP + sample_row*8 + y]
            rgb = jz_rgb(idx)
            if bit == 0:
                bit0_colors[rgb] = bit0_colors.get(rgb, 0) + 1
            else:
                bit1_colors[rgb] = bit1_colors.get(rgb, 0) + 1
    
    bit0_str = ', '.join('%s:%d' % (cn(c), n) for c, n in sorted(bit0_colors.items(), key=lambda x: -x[1]))
    bit1_str = ', '.join('%s:%d' % (cn(c), n) for c, n in sorted(bit1_colors.items(), key=lambda x: -x[1]))
    
    # Determine: does FG=0 mean transparent?
    has_multiple_jz_colors = len(jz_colors) > 1
    
    src = 'GRAM' if is_gram else 'grom'
    
    # Try to predict what FG color jzIntv should show
    # For bit=1 pixels (foreground):
    if bits_set > 0 and bit1_colors:
        dominant_fg = max(bit1_colors.items(), key=lambda x: x[1])[0]
        fg_jz = cn(dominant_fg)
    else:
        fg_jz = 'N/A'
    
    # For bit=0 pixels (background/CS):
    if 64 - bits_set > 0 and bit0_colors:
        dominant_bg = max(bit0_colors.items(), key=lambda x: x[1])[0]
        bg_jz = cn(dominant_bg)
    else:
        bg_jz = 'N/A'
    
    # Summary line
    marker = ''
    if len(jz_colors) > 1 and bits_set > 0:
        marker = ' **MULTI**'
    elif len(jz_colors) == 1 and bits_set > 0 and 64 - bits_set > 0:
        marker = ' **SAME**'  # both bits show same color
    
    print(f"0x{w:04X} card={cidx:3d} {src:4s} bits={bits_set:2d}/64 "
          f"FGstd={fg_std} FGbit12={fg_a} "
          f"bit0->{bit0_str:30s} bit1->{bit1_str:30s}{marker}")
    
    # For SAME tiles: both bit0 and bit1 show same color → transparent FG or single-color card
    # For DIFFERENT tiles: bit0 ≠ bit1 colors → opaque FG

print()
print("=" * 90)
print("SUMMARY")
print("=" * 90)

# Count patterns
same_count = 0
diff_count = 0
no_bg_count = 0
no_fg_count = 0
for w, (sample_row, sample_col, _) in tile_samples.items():
    is_gram = bool(w & 0x0800)
    card_idx = w & 0xFF
    if is_gram:
        cidx = card_idx & 0x3F
        base = 0x3800 + cidx * 8
        card_bytes = bytes(gram_mem.get(base+r, 0) & 0xFF for r in range(8))
    else:
        cidx = card_idx & 0xFF
        base = cidx * 8
        card_bytes = grom[base:base+8] if base+8 <= len(grom) else bytes(8)
    bits_set = sum(bin(b).count('1') for b in card_bytes)
    
    bit0_colors = {}
    bit1_colors = {}
    for y in range(8):
        b = card_bytes[y]
        for x in range(8):
            bit = (b >> (7-x)) & 1
            idx = jz_px[JLEFT + sample_col*8 + x, JTOP + sample_row*8 + y]
            rgb = jz_rgb(idx)
            if bit == 0:
                bit0_colors[rgb] = bit0_colors.get(rgb, 0) + 1
            else:
                bit1_colors[rgb] = bit1_colors.get(rgb, 0) + 1
    
    bit0_unique = set(bit0_colors.keys())
    bit1_unique = set(bit1_colors.keys())
    
    if bits_set == 0:
        no_fg_count += 1
        continue
    if bits_set == 64:
        no_bg_count += 1
        continue
    
    # Check if bit0 and bit1 share colors
    if bit0_unique == bit1_unique:
        same_count += 1
    else:
        diff_count += 1

print(f"Tiles with bit0==bit1 colors (transparent FG): {same_count}")
print(f"Tiles with bit0!=bit1 colors (opaque FG):     {diff_count}")
print(f"Tiles with no bit=0 pixels (all FG):          {no_bg_count}")
print(f"Tiles with no bit=1 pixels (all BG):          {no_fg_count}")

# Check: when FGstd=0, does bit1 show black or CS background?
print()
print("=" * 90)
print("FG=0 TILES: does bit1 show BLACK or CS background?")
print("=" * 90)
for w, (sample_row, sample_col, _) in sorted(tile_samples.items()):
    fg_std = ((w >> 13) & 0x6) | ((w >> 12) & 0x1)
    if fg_std != 0:
        continue
    is_gram = bool(w & 0x0800)
    card_idx = w & 0xFF
    if is_gram:
        cidx = card_idx & 0x3F
        base = 0x3800 + cidx * 8
        card_bytes = bytes(gram_mem.get(base+r, 0) & 0xFF for r in range(8))
    else:
        cidx = card_idx & 0xFF
        base = cidx * 8
        card_bytes = grom[base:base+8] if base+8 <= len(grom) else bytes(8)
    bits_set = sum(bin(b).count('1') for b in card_bytes)
    
    if bits_set == 0:
        continue
    
    bit1_colors = {}
    for y in range(8):
        b = card_bytes[y]
        for x in range(8):
            bit = (b >> (7-x)) & 1
            if bit:
                idx = jz_px[JLEFT + sample_col*8 + x, JTOP + sample_row*8 + y]
                rgb = jz_rgb(idx)
                bit1_colors[rgb] = bit1_colors.get(rgb, 0) + 1
    
    bit1_str = ', '.join('%s:%d' % (cn(c), n) for c, n in sorted(bit1_colors.items(), key=lambda x: -x[1]))
    black_count = bit1_colors.get((0,0,0), 0)
    pas3_count = bit1_colors.get(PASTEL_PALETTE[3], 0)
    pal1_count = bit1_colors.get(PALETTE[1], 0)
    
    print(f"  0x{w:04X} card={cidx:3d} bits={bits_set:2d} bit1->{bit1_str}")
    
    if black_count == bits_set:
        print(f"    --> ALL BLACK - FG=0 renders as black (opaque FG)")
    elif pas3_count == bits_set:
        print(f"    --> ALL PAS[3] - FG=0 renders as transparent (show CS bg)")
    elif pal1_count == bits_set:
        print(f"    --> ALL PAL[1] - FG=0 still shows blue somehow")
    else:
        print(f"    --> MIXED")

print()
print("=" * 90)
print("COLOR STACK BACKGROUND ANALYSIS")
print("=" * 90)
print("What color does the Color Stack background show for tiles where bit=0 pixels exist?")
for w, (sample_row, sample_col, _) in sorted(tile_samples.items()):
    is_gram = bool(w & 0x0800)
    card_idx = w & 0xFF
    if is_gram:
        cidx = card_idx & 0x3F
        base = 0x3800 + cidx * 8
        card_bytes = bytes(gram_mem.get(base+r, 0) & 0xFF for r in range(8))
    else:
        cidx = card_idx & 0xFF
        base = cidx * 8
        card_bytes = grom[base:base+8] if base+8 <= len(grom) else bytes(8)
    
    bit0_pixels = 64 - sum(bin(b).count('1') for b in card_bytes)
    if bit0_pixels == 0:
        continue
    
    bit0_colors = {}
    for y in range(8):
        b = card_bytes[y]
        for x in range(8):
            bit = (b >> (7-x)) & 1
            if bit == 0:
                idx = jz_px[JLEFT + sample_col*8 + x, JTOP + sample_row*8 + y]
                rgb = jz_rgb(idx)
                bit0_colors[rgb] = bit0_colors.get(rgb, 0) + 1
    
    cs_adv = (w >> 13) & 1
    bit0_str = ', '.join('%s:%d' % (cn(c), n) for c, n in sorted(bit0_colors.items(), key=lambda x: -x[1]))
    print(f"  0x{w:04X} cs_adv={cs_adv} bit0_px={bit0_pixels:2d} -> {bit0_str}")

PYEOF
