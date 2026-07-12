#!/usr/bin/env python3
"""
Empirical GROM Card → jzIntv Pixel Correlation

Uses only GROM tiles (immutable card data) from room 0 to determine:
1. What jzIntv color does a card bit=0 show? (reveals Color Stack background)
2. What jzIntv color does a card bit=1 show? (reveals FG color, or transparency)
3. Which BACKTAB bits control FG vs transparency?
"""
import sys
sys.path.insert(0, '.')
from render_all_rooms import (
    load_grom, parse_backtab, extract_backtab_from_output,
    extract_memory_section, parse_mobs,
    PALETTE, PASTEL_PALETTE, DEFAULT_BG,
)
from PIL import Image

def cn(rgb):
    for d, lbl in [(PALETTE, 'PAL'), (PASTEL_PALETTE, 'PAS')]:
        for k, v in d.items():
            if v == rgb: return '%s[%d]' % (lbl, k)
    if rgb == (0,0,0): return 'BLACK'
    return 'RGB'+str(rgb)

# Load data
with open('traces/_cmp_room_0_out.txt', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

grid = parse_backtab(extract_backtab_from_output(content))
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

JLEFT, JTOP = 80, 52

# ============================================================
# Step 1: Build MOB coverage mask (conservative, expanded)
# ============================================================
# Expand MOB bounding boxes by 1px to catch edge contamination
mob_pixels = [[False]*scr_w for _ in range(scr_h)]
for mob in mobs:
    mx = mob['x'] - 1
    my = mob['y'] - 1
    w = (16 if mob['xsize'] == 1 else 8) + 2
    h = (16 if mob['ysize'] == 1 else 8) + 2
    for y in range(h):
        py = my + y
        if py < 0 or py >= scr_h: continue
        for x in range(w):
            px = mx + x
            if px < 0 or px >= scr_w: continue
            mob_pixels[py][px] = True

# ============================================================
# Step 2: For GROM-only tiles, correlate each pixel
# ============================================================
# Build per-pixel correlation: (word, grom_card_byte, bit_position) -> jzIntv color
# We need to know: for each GROM card pixel, is there a MOB on top?

print("=" * 90)
print("GROM CARD PIXEL CORRELATION")
print("=" * 90)
print()

# Collect all GROM tiles and their per-pixel jzIntv colors
grom_tiles = []
for row in range(12):
    for col in range(20):
        w = grid[row][col]
        is_gram = bool(w & 0x0800)
        if is_gram:
            continue  # skip GRAM (dynamic content)
        grom_tiles.append((row, col, w))

print(f"GROM tiles: {len(grom_tiles)}/{240}")

# For each GROM tile, correlate card bits with actual jzIntv colors
# Only use pixels NOT covered by MOBs

print()
print("Per-tile analysis (MOB-free pixels only):")
print(f"{'Row':>3s} {'Col':>3s} {'Word':>6s} {'Card':>5s} {'b12':>3s} {'b13':>3s} {'bit0_dom':>14s} {'bit1_dom':>14s} {'bit1_alt':>14s}")
print("-" * 90)

for row, col, w in grom_tiles:
    card_idx = w & 0xFF  # GROM card 0-255
    baddr = card_idx * 8
    if baddr + 8 > len(grom):
        continue
    card_bytes = grom[baddr:baddr+8]
    
    b12 = (w >> 12) & 1
    b13 = (w >> 13) & 1
    
    # Collect pixel colors, separated by bit value
    bit0_colors = {}  # card bit=0 pixels (background)
    bit1_colors = {}  # card bit=1 pixels (foreground)
    
    tx = JLEFT + col * 8
    ty = JTOP + row * 8
    
    for y in range(8):
        py = ty + y
        if py >= scr_h: continue
        byte_val = card_bytes[y]
        for x in range(8):
            px = tx + x
            if px >= scr_w: continue
            # Skip MOB-contaminated pixels
            if mob_pixels[py][px]:
                continue
            bit = (byte_val >> (7 - x)) & 1
            rgb = jz_rgb(jz_px[px, py])
            if bit == 0:
                bit0_colors[rgb] = bit0_colors.get(rgb, 0) + 1
            else:
                bit1_colors[rgb] = bit1_colors.get(rgb, 0) + 1
    
    bit0_dom = max(bit0_colors.items(), key=lambda x: x[1]) if bit0_colors else (None, 0)
    bit1_dom = max(bit1_colors.items(), key=lambda x: x[1]) if bit1_colors else (None, 0)
    
    # Also find the SECOND most common bit1 color (in case FG=7 white but some pixels are CS)
    bit1_alt = (None, 0)
    if len(bit1_colors) > 1:
        sorted_b1 = sorted(bit1_colors.items(), key=lambda x: -x[1])
        bit1_alt = sorted_b1[1] if len(sorted_b1) > 1 else (None, 0)
    
    print(f"{row:3d} {col:3d} 0x{w:04X} {card_idx:5d} {b12:3d} {b13:3d} "
          f"{cn(bit0_dom[0]):14s} {cn(bit1_dom[0]):14s} {cn(bit1_alt[0]):14s}")

# ============================================================
# Step 3: Aggregate analysis
# ============================================================
print()
print("=" * 90)
print("AGGREGATE: bit0 colors per BACKTAB word (MOB-free pixels)")
print("=" * 90)

word_bit0 = {}  # word -> {color: count} for bit=0 pixels
word_bit1 = {}  # word -> {color: count} for bit=1 pixels

for row, col, w in grom_tiles:
    card_idx = w & 0xFF
    baddr = card_idx * 8
    if baddr + 8 > len(grom):
        continue
    card_bytes = grom[baddr:baddr+8]
    
    tx = JLEFT + col * 8
    ty = JTOP + row * 8
    
    for y in range(8):
        py = ty + y
        if py >= scr_h: continue
        byte_val = card_bytes[y]
        for x in range(8):
            px = tx + x
            if px >= scr_w: continue
            if mob_pixels[py][px]:
                continue
            bit = (byte_val >> (7 - x)) & 1
            rgb = jz_rgb(jz_px[px, py])
            if bit == 0:
                wb0 = word_bit0.setdefault(w, {})
                wb0[rgb] = wb0.get(rgb, 0) + 1
            else:
                wb1 = word_bit1.setdefault(w, {})
                wb1[rgb] = wb1.get(rgb, 0) + 1

print()
print(f"{'Word':>6s} {'b12':>3s} {'b13':>3s} {'bit0_dom':>14s} {'bit0_cnt':>8s} {'bit1_dom':>14s} {'bit1_cnt':>8s} {'FG_colors':>20s}")
print("-" * 110)

for w in sorted(word_bit0.keys()):
    b12 = (w >> 12) & 1
    b13 = (w >> 13) & 1
    
    b0d = sorted(word_bit0[w].items(), key=lambda x: -x[1])
    b0_dom_color = b0d[0][0] if b0d else None
    b0_dom_count = b0d[0][1] if b0d else 0
    
    b1d = sorted(word_bit1.get(w, {}).items(), key=lambda x: -x[1])
    b1_dom_color = b1d[0][0] if b1d else None
    b1_dom_count = b1d[0][1] if b1d else 0
    
    # All FG colors seen
    fg_colors = ', '.join('%s:%d' % (cn(c), n) for c, n in b1d[:3])
    
    print(f"0x{w:04X} {b12:3d} {b13:3d} {cn(b0_dom_color):14s} {b0_dom_count:8d} "
          f"{cn(b1_dom_color):14s} {b1_dom_count:8d} {fg_colors:20s}")

# ============================================================
# Step 4: Hypothesis testing
# ============================================================
print()
print("=" * 90)
print("HYPOTHESIS: Is bit12 the FG-opaque flag?")
print("=" * 90)

# For each unique GROM BACKTAB word, compute:
# - Do bit1 pixels match bit0 pixels? (transparent FG)
# - Or are bit1 pixels different? (opaque FG)

transparent_words = []
opaque_words = []

for w in sorted(word_bit0.keys()):
    if w not in word_bit1 or not word_bit1[w]:
        transparent_words.append(w)
        continue
    
    b0d = sorted(word_bit0[w].items(), key=lambda x: -x[1])
    b1d = sorted(word_bit1[w].items(), key=lambda x: -x[1])
    
    b0_dom = b0d[0][0] if b0d else None
    b1_dom = b1d[0][0] if b1d else None
    
    if b0_dom == b1_dom:
        transparent_words.append(w)
    else:
        opaque_words.append(w)

print(f"\nTransparent tiles (bit0==bit1 dominant): {len(transparent_words)}")
print(f"Opaque tiles (bit0!=bit1 dominant): {len(opaque_words)}")

print(f"\n{'Word':>6s} {'b12':>3s} {'b13':>3s} {'Transparent?':>14s}")
print("-" * 50)
for w in transparent_words:
    b12 = (w >> 12) & 1
    b13 = (w >> 13) & 1
    print(f"0x{w:04X} {b12:3d} {b13:3d} {'YES':>14s}")

print()
for w in opaque_words:
    b12 = (w >> 12) & 1
    b13 = (w >> 13) & 1
    b1d = sorted(word_bit1[w].items(), key=lambda x: -x[1])
    fg_str = cn(b1d[0][0]) if b1d else 'NONE'
    # What FG color according to standard CS?
    std_fg = ((w >> 13) & 0x6) | ((w >> 12) & 0x1)
    print(f"0x{w:04X} {b12:3d} {b13:3d} {'NO':>14s}  FG_actual={fg_str}  std_FG={std_fg}")

# ============================================================
# Step 5: Test specific decode models
# ============================================================
print()
print("=" * 90)
print("DECODE MODEL ACCURACY (GROM only, MOB-free pixels)")
print("=" * 90)

def model_std_cs(word):
    """Standard Color Stack: FG=bits 15,14,12. FG=0 → black (not transparent)"""
    card = word & 0xFF
    fg = ((word >> 13) & 0x6) | ((word >> 12) & 0x1)
    transparent = False
    cs_adv = (word >> 13) & 1
    return card, fg, cs_adv, transparent

def model_fg0_transparent(word):
    """Standard CS but FG=0 → transparent"""
    card = word & 0xFF
    fg = ((word >> 13) & 0x6) | ((word >> 12) & 0x1)
    transparent = (fg == 0)
    cs_adv = (word >> 13) & 1
    return card, fg, cs_adv, transparent

def model_b12_opaque_flag(word):
    """bit12=0 → transparent; bit12=1 → FG=7 (white)"""
    card = word & 0xFF
    fg = 7 if (word & 0x1000) else 0
    transparent = not bool(word & 0x1000)
    cs_adv = (word >> 13) & 1
    return card, fg, cs_adv, transparent

def model_bg_bits_mode(word):
    """bits 0-2 = CS advance amount; bit12=opaque flag; FG=7"""
    card = word & 0xFF
    fg = 7 if (word & 0x1000) else 0
    transparent = not bool(word & 0x1000)
    cs_adv = word & 0x7  # bits 0-2 advance the CS
    return card, fg, cs_adv, transparent

def model_fgbg_mode(word):
    """FG/BG mode: bits 0-3 = bg color+pastel; card in bits 4-10"""
    bg_idx = word & 0x7
    bg_pastel = bool(word & 0x8)
    card = (word >> 4) & 0x7F  # bits 4-10
    fg = ((word >> 13) & 0x6) | ((word >> 12) & 0x1)
    transparent = (fg == 0)
    cs_adv = 0
    return card, fg, cs_adv, transparent, (bg_idx, bg_pastel)

CS_DEFAULT = [PASTEL_PALETTE[3]] * 4  # pastel tan

models = [
    ('std_cs', model_std_cs),
    ('fg0_transparent', model_fg0_transparent),
    ('b12_opaque_white', model_b12_opaque_flag),
    ('bg_bits_advance', model_bg_bits_mode),
]

for name, model_fn in models:
    match = 0
    total = 0
    cs = 0
    
    for row, col, w in grom_tiles:
        card_idx = w & 0xFF
        baddr = card_idx * 8
        if baddr + 8 > len(grom):
            continue
        card_bytes = grom[baddr:baddr+8]
        
        if name == 'fgbg_mode':
            result = model_fn(w)
            card, fg, cs_adv, transparent, (bg_idx, bg_pastel) = result
            if bg_pastel:
                bg = PASTEL_PALETTE.get(bg_idx, DEFAULT_BG)
            else:
                bg = PALETTE.get(bg_idx, DEFAULT_BG)
        else:
            card, fg, cs_adv, transparent = model_fn(w)
        
        cs = (cs + cs_adv) % 4
        bg = CS_DEFAULT[cs]
        fg_rgb = PALETTE.get(fg, (255, 0, 255))
        
        tx = JLEFT + col * 8
        ty = JTOP + row * 8
        
        for y in range(8):
            py = ty + y
            if py >= scr_h: continue
            byte_val = card_bytes[y]
            for x in range(8):
                px = tx + x
                if px >= scr_w: continue
                if mob_pixels[py][px]:
                    continue
                
                bit = (byte_val >> (7 - x)) & 1
                actual = jz_rgb(jz_px[px, py])
                
                if transparent:
                    expected = bg
                elif bit == 0:
                    expected = bg
                else:
                    expected = fg_rgb
                
                total += 1
                if expected == actual:
                    match += 1
    
    acc = match / total * 100 if total > 0 else 0
    print(f"  {name:25s}: {acc:5.1f}%  ({match:6d}/{total:6d} pixels)")
