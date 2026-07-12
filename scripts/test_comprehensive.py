#!/usr/bin/env python3
"""Comprehensive empirical test: determine correct BACKTAB word format
by testing all decoding hypotheses against jzIntv pixel data (clean tiles only)."""
import sys
sys.path.insert(0, '.')
from render_all_rooms import (
    load_grom, parse_backtab, extract_backtab_from_output,
    extract_gram_from_output, parse_memory_dump,
    extract_memory_section, parse_mobs,
    PALETTE, PASTEL_PALETTE, DEFAULT_BG,
)
from PIL import Image

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
    if rgb == (0,0,0): return 'BLACK'
    return 'RGB'+str(rgb)

JLEFT, JTOP = 80, 52
CS_DEFAULT = [PASTEL_PALETTE[3]] * 4

# ============================================================
# Step 1: Build MOB coverage, identify clean tiles
# ============================================================
mob_pixels = [[False]*scr_w for _ in range(scr_h)]
for mob in mobs:
    mx = mob['x']
    my = mob['y']
    w = 16 if mob['xsize'] == 1 else 8
    h = 16 if mob['ysize'] == 1 else 8
    for y in range(h):
        py = my + y
        if py < 0 or py >= scr_h: continue
        for x in range(w):
            px = mx + x
            if px < 0 or px >= scr_w: continue
            mob_pixels[py][px] = True

clean_tiles = []
for row in range(12):
    for col in range(20):
        mob_px_count = 0
        ty = JTOP + row * 8
        tx = JLEFT + col * 8
        for y in range(8):
            py = ty + y
            if py >= scr_h: continue
            for x in range(8):
                px = tx + x
                if px >= scr_w: continue
                if mob_pixels[py][px]:
                    mob_px_count += 1
        if mob_px_count == 0:
            clean_tiles.append((row, col))

print(f"Clean tiles: {len(clean_tiles)}/{240}")

# ============================================================
# Step 2: Test ALL decode hypotheses against clean tiles
# ============================================================

# Hypothesis 1: Standard Color Stack (FG=bits 15,14,12; CS advance=bit13)
def h1_standard_cs(word):
    card = word & 0x7FF
    is_gram = bool(word & 0x0800)
    fg_idx = ((word >> 13) & 0x6) | ((word >> 12) & 0x1)  # bits 15,14,12 → bits 2,1,0
    cs_adv = (word >> 13) & 1
    transparent = (fg_idx == 0)
    if is_gram: card &= 0x3F
    else: card &= 0xFF
    return card, is_gram, fg_idx, cs_adv, transparent

# Hypothesis 2: FG=0 transparent, rest standard CS
def h2_fg0_transparent(word):
    card = word & 0x7FF
    is_gram = bool(word & 0x0800)
    fg_idx = ((word >> 13) & 0x6) | ((word >> 12) & 0x1)
    cs_adv = (word >> 13) & 1
    transparent = (fg_idx == 0)
    if is_gram: card &= 0x3F
    else: card &= 0xFF
    return card, is_gram, fg_idx, cs_adv, transparent

# Hypothesis 3: Card is just bits 0-7, no shifting
def h3_card_low8(word):
    card = word & 0xFF
    is_gram = bool(word & 0x0800)
    fg_idx = ((word >> 13) & 0x6) | ((word >> 12) & 0x1)
    cs_adv = (word >> 13) & 1
    transparent = (fg_idx == 0)
    if is_gram: card &= 0x3F
    return card, is_gram, fg_idx, cs_adv, transparent

# Hypothesis 4: bit12 is transparent flag, FG=white (7) when opaque
def h4_bit12_transparent_fg7(word):
    card = word & 0xFF
    is_gram = bool(word & 0x0800)
    fg_idx = 7 if (word & 0x1000) else 0  # bit12=1 → FG=7 (white)
    cs_adv = (word >> 13) & 1
    transparent = not bool(word & 0x1000)  # bit12=0 → transparent
    if is_gram: card &= 0x3F
    return card, is_gram, fg_idx, cs_adv, transparent

# Hypothesis 5: bit12 is transparent flag, FG=blue (1) when opaque
def h5_bit12_transparent_fg1(word):
    card = word & 0xFF
    is_gram = bool(word & 0x0800)
    fg_idx = 1 if (word & 0x1000) else 0  # bit12=1 → FG=1 (blue)
    cs_adv = (word >> 13) & 1
    transparent = not bool(word & 0x1000)
    if is_gram: card &= 0x3F
    return card, is_gram, fg_idx, cs_adv, transparent

# Hypothesis 6: FG/BG mode interpretation
def h6_fgbg(word):
    bg_idx = word & 0x7
    bg_pastel = bool(word & 0x8)
    card = (word >> 4) & 0x7F
    is_gram = bool(word & 0x0800)
    fg_idx = (word >> 12) & 0x7
    if is_gram: card &= 0x3F
    else: card |= (word & 0x0800) >> 3
    cs_adv = 0
    transparent = False
    # Return bg color directly
    return card, is_gram, fg_idx, cs_adv, transparent, (bg_idx, bg_pastel)

# Hypothesis 7: bit12 controls transparency, FG = bits extracted from table
def h7_bit12_transparent_fg_from_room(word):
    card = word & 0xFF
    is_gram = bool(word & 0x0800)
    # FG color bits might be in bits 10,9 (extracted BEFORE AND mask)
    fg_idx = ((word >> 9) & 0x3)  # bits 10,9 → FG color bits 1,0
    cs_adv = (word >> 13) & 1
    transparent = not bool(word & 0x1000)
    if is_gram: card &= 0x3F
    return card, is_gram, fg_idx, cs_adv, transparent

hypotheses = [
    ('H1_standard_CS', h1_standard_cs),
    ('H2_FG0_transparent', h2_fg0_transparent),
    ('H3_card_low8', h3_card_low8),
    ('H4_b12transp_FG7', h4_bit12_transparent_fg7),
    ('H5_b12transp_FG1', h5_bit12_transparent_fg1),
    ('H7_b12transp_FGbits9_10', h7_bit12_transparent_fg_from_room),
]

print()
print("=" * 100)
print("HYPOTHESIS TESTING (clean tiles only, CS=pas3 default)")
print("=" * 100)

for name, decode_fn in hypotheses:
    match = 0
    total = 0
    cs = 0  # color stack pointer
    
    for row, col in clean_tiles:
        word = grid[row][col]
        result = decode_fn(word)
        
        if len(result) == 6:
            card, is_gram, fg_idx, cs_adv, transparent, bg_extra = result
            bg_idx, bg_pastel = bg_extra
            bg = PASTEL_PALETTE.get(bg_idx, DEFAULT_BG) if bg_pastel else PALETTE.get(bg_idx, DEFAULT_BG)
        else:
            card, is_gram, fg_idx, cs_adv, transparent = result
        
        cs = (cs + cs_adv) % 4
        bg = CS_DEFAULT[cs]
        
        # Get card bytes
        if is_gram:
            cidx = card & 0x3F
            baddr = 0x3800 + cidx * 8
            card_bytes = bytes(gram_mem.get(baddr + ry, 0) & 0xFF for ry in range(8))
        else:
            cidx = card & 0xFF
            baddr = cidx * 8
            card_bytes = grom[baddr:baddr+8] if baddr+8 <= len(grom) else bytes(8)
        
        fg_rgb = PALETTE.get(fg_idx, (255,0,255))
        
        for y in range(8):
            by = card_bytes[y]
            for x in range(8):
                bit = (by >> (7-x)) & 1
                jx = JLEFT + col*8 + x
                jy = JTOP + row*8 + y
                if jx >= scr_w or jy >= scr_h:
                    continue
                
                actual = jz_rgb(jz_px[jx, jy])
                
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
    print(f"  {name:30s}: {acc:5.1f}%  ({match:6d}/{total:6d} pixels)")

# ============================================================
# Step 3: Per-tile detailed analysis for best hypotheses
# ============================================================
print()
print("=" * 100)
print("PER-TILE BREAKDOWN (H4: bit12=transparent, FG=7 when opaque)")
print("=" * 100)

# Group unique words
unique_words = {}
for row, col in clean_tiles:
    w = grid[row][col]
    if w not in unique_words:
        unique_words[w] = []
    unique_words[w].append((row, col))

print(f"{'Word':>6s} {'Card':>5s} {'Src':>4s} {'b12':>3s} {'b13':>3s} {'bits':>4s} {'bit0color':>14s} {'bit1color':>14s} {'expected':>14s} {'match':>5s}")
print("-" * 100)

for w, positions in sorted(unique_words.items()):
    row, col = positions[0]
    card, is_gram, fg_idx, cs_adv, transparent = h4_bit12_transparent_fg7(w)
    
    if is_gram:
        cidx = card & 0x3F
        baddr = 0x3800 + cidx * 8
        card_bytes = bytes(gram_mem.get(baddr + ry, 0) & 0xFF for ry in range(8))
        src = 'GRAM'
    else:
        cidx = card & 0xFF
        baddr = cidx * 8
        card_bytes = grom[baddr:baddr+8] if baddr+8 <= len(grom) else bytes(8)
        src = 'grom'
    
    bits_set = sum(bin(b).count('1') for b in card_bytes)
    
    # Get actual colors from jzIntv
    bit0_colors = {}
    bit1_colors = {}
    for y in range(8):
        by = card_bytes[y]
        for x in range(8):
            bit = (by >> (7-x)) & 1
            jx = JLEFT + col*8 + x
            jy = JTOP + row*8 + y
            if jx < scr_w and jy < scr_h:
                rgb = jz_rgb(jz_px[jx, jy])
                if bit == 0:
                    bit0_colors[rgb] = bit0_colors.get(rgb, 0) + 1
                else:
                    bit1_colors[rgb] = bit1_colors.get(rgb, 0) + 1
    
    bit0_dom = max(bit0_colors.items(), key=lambda x: x[1]) if bit0_colors else (None, 0)
    bit1_dom = max(bit1_colors.items(), key=lambda x: x[1]) if bit1_colors else (None, 0)
    
    # What would H4 predict?
    if transparent:
        expected = cn(CS_DEFAULT[0])  # CS pos 0 = PAS[3]
        pred_match = (bit0_dom[0] == CS_DEFAULT[0]) if bit0_dom[0] else True
    else:
        expected = cn(PALETTE[7])  # FG=white
        # For opaque tiles: bit0 should be CS bg, bit1 should be FG
        if bits_set > 0 and 64 - bits_set > 0:
            pred_match = (bit0_dom[0] == CS_DEFAULT[0] and bit1_dom[0] == PALETTE[7])
        else:
            pred_match = True
    
    print(f"0x{w:04X} {cidx:5d} {src:4s} {(w>>12)&1:3d} {(w>>13)&1:3d} {bits_set:4d} "
          f"{cn(bit0_dom[0]):14s} {cn(bit1_dom[0]):14s} {expected:14s} {'OK' if pred_match else 'X'}")

# ============================================================
# Step 4: Focus on DIFFERENT tiles - what FG colors do they show?
# ============================================================
print()
print("=" * 100)
print("TILES WHERE bit0 != bit1 IN jzIntv (these have opaque FG)")
print("=" * 100)

for w, positions in sorted(unique_words.items()):
    row, col = positions[0]
    card_idx = w & 0xFF
    is_gram = bool(w & 0x0800)
    
    if is_gram:
        cidx = card_idx & 0x3F
        baddr = 0x3800 + cidx * 8
        card_bytes = bytes(gram_mem.get(baddr + ry, 0) & 0xFF for ry in range(8))
        src = 'GRAM'
    else:
        cidx = card_idx & 0xFF
        baddr = cidx * 8
        card_bytes = grom[baddr:baddr+8] if baddr+8 <= len(grom) else bytes(8)
        src = 'grom'
    
    bits_set = sum(bin(b).count('1') for b in card_bytes)
    if bits_set == 0 or bits_set == 64:
        continue
    
    bit0_colors = {}
    bit1_colors = {}
    for y in range(8):
        by = card_bytes[y]
        for x in range(8):
            bit = (by >> (7-x)) & 1
            jx = JLEFT + col*8 + x
            jy = JTOP + row*8 + y
            if jx < scr_w and jy < scr_h:
                rgb = jz_rgb(jz_px[jx, jy])
                if bit == 0:
                    bit0_colors[rgb] = bit0_colors.get(rgb, 0) + 1
                else:
                    bit1_colors[rgb] = bit1_colors.get(rgb, 0) + 1
    
    bit0_dom = max(bit0_colors.items(), key=lambda x: x[1]) if bit0_colors else (None, 0)
    bit1_dom = max(bit1_colors.items(), key=lambda x: x[1]) if bit1_colors else (None, 0)
    
    if bit0_dom[0] != bit1_dom[0]:
        print(f"  0x{w:04X} {src} card={cidx:3d} bits={bits_set} b12={(w>>12)&1} b13={(w>>13)&1}")
        print(f"    bit0 (bg): {', '.join('%s:%d' % (cn(c), n) for c, n in sorted(bit0_colors.items(), key=lambda x: -x[1]))}")
        print(f"    bit1 (fg): {', '.join('%s:%d' % (cn(c), n) for c, n in sorted(bit1_colors.items(), key=lambda x: -x[1]))}")

# ============================================================
# Step 5: Check GRAM card contents
# ============================================================
print()
print("=" * 100)
print("GRAM CARDS WITH NON-ZERO CONTENT")
print("=" * 100)
for cidx in range(64):
    baddr = 0x3800 + cidx * 8
    card_bytes = bytes(gram_mem.get(baddr + ry, 0) & 0xFF for ry in range(8))
    bits_set = sum(bin(b).count('1') for b in card_bytes)
    if bits_set > 0:
        hex_str = ' '.join(f'{b:02X}' for b in card_bytes)
        print(f"  GRAM {cidx:2d} (0x{baddr:04X}): bits={bits_set:2d}  {hex_str}")
