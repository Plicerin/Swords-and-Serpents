#!/usr/bin/env python3
"""Empirically determine BACKTAB word format by testing ALL interpretations."""
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
grom = load_grom()

scr = Image.open('sprites/room_0_jzintv.gif')
jz_pal = scr.getpalette()
jz_px = scr.load()

def jz_rgb(idx):
    if idx * 3 + 2 < len(jz_pal):
        return (jz_pal[idx*3], jz_pal[idx*3+1], jz_pal[idx*3+2])
    return (0, 0, 0)

JLEFT, JTOP = 80, 52

# Get all unique BACKTAB words with a sample tile position
samples = {}
for row in range(12):
    for col in range(20):
        w = grid[row][col]
        if w not in samples:
            samples[w] = (row, col)

print("=" * 90)
print("EMPIRICAL BACKTAB FORMAT DETERMINATION")
print("=" * 90)

# For each unique word, test different interpretations and score them
# against jzIntv pixel colors

# Define interpretation functions
# Each returns: (card, is_gram, fg_color, bg_color, transparent_flag) or None if invalid

def cs_standard(word):
    """Standard Color Stack: bits 0-10=card, 11=G/G, 12=FG0, 13=CSadv, 14=FG1, 15=FG2"""
    card = word & 0x7FF
    is_gram = bool(word & 0x0800)
    fg_idx = ((word >> 13) & 0x6) | ((word >> 12) & 0x1)
    if is_gram:
        card &= 0x3F
    else:
        card &= 0xFF
    fg = PALETTE.get(fg_idx, (255,0,255))
    return card, is_gram, fg, None, False  # bg=None means use CS

def cs_fg0_transparent(word):
    """Color Stack with FG=0 transparent: bits 0-10=card, 11=G/G, 12=FG0, 13=CSadv, 14=FG1, 15=FG2
    FG=0 means transparent (show CS bg), FG>0 means opaque"""
    card = word & 0x7FF
    is_gram = bool(word & 0x0800)
    fg_idx = ((word >> 13) & 0x6) | ((word >> 12) & 0x1)
    if is_gram:
        card &= 0x3F
    else:
        card &= 0xFF
    fg = PALETTE.get(fg_idx, (255,0,255))
    transparent = (fg_idx == 0)
    return card, is_gram, fg, None, transparent

def fgbg_standard(word):
    """Standard FG/BG: bits 0-2=BG color, 3=BGpastel, 4-10=card, 11=G/G, 12-14=FG"""
    bg_idx = word & 0x7
    bg_pastel = bool(word & 0x8)
    card = (word >> 4) & 0x7F
    is_gram = bool(word & 0x0800)
    fg_idx = (word >> 12) & 0x7
    
    if is_gram:
        card &= 0x3F
    else:
        card |= (word & 0x0800) >> 3  # bit 11 becomes card bit 7 for GROM
        card &= 0xFF
    
    bg = PASTEL_PALETTE.get(bg_idx, DEFAULT_BG) if bg_pastel else PALETTE.get(bg_idx, DEFAULT_BG)
    fg = PALETTE.get(fg_idx, (255,0,255))
    return card, is_gram, fg, bg, False

def fgbg_alt(word):
    """FG/BG alternative: bits 0-2=BG, 3=pastel, 4-11=card, 12-14=FG, 15=unused"""
    bg_idx = word & 0x7
    bg_pastel = bool(word & 0x8)
    card = (word >> 4) & 0xFF  # 8 bits for card
    is_gram = bool(word & 0x0800)
    fg_idx = (word >> 12) & 0x7
    
    if is_gram:
        card &= 0x3F
    
    bg = PASTEL_PALETTE.get(bg_idx, DEFAULT_BG) if bg_pastel else PALETTE.get(bg_idx, DEFAULT_BG)
    fg = PALETTE.get(fg_idx, (255,0,255))
    return card, is_gram, fg, bg, False

def fgbg_custom_encoding(word):
    """FG/BG mode but with game's custom bit layout (from ANDI #$3607):
    bits 0-2: BG color, bit 12: FG color bit 0, bit 13+10+9+2+1+0: card encoding
    The card is packed into bits 13,10,9,2,1,0 which gives 6 bits = 64 possible GROM cards
    But bit 11 (GROM/GRAM) might come from the second table XOR"""
    bg_idx = word & 0x7
    bg_pastel = bool(word & 0x8)
    
    # Card is packed: bits 13,10,9,2,1,0
    card = ((word >> 13) & 0x01) << 5  # bit 13 -> bit 5
    card |= ((word >> 9) & 0x03) << 3  # bits 10,9 -> bits 4,3
    card |= word & 0x7                  # bits 2,1,0 -> bits 2,1,0
    # card is 6 bits (0-63)
    
    is_gram = bool(word & 0x0800)  # bit 11 from table XOR
    
    # FG color: bit 12 only (from ANDI, could be combined with others from table XOR)
    fg_idx = (word >> 12) & 0x1  # only 0 or 1
    
    bg = PASTEL_PALETTE.get(bg_idx, DEFAULT_BG) if bg_pastel else PALETTE.get(bg_idx, DEFAULT_BG)
    fg = PALETTE.get(fg_idx, (255,0,255))
    
    return card, is_gram, fg, bg, False


# Test all formats
formats = [
    ('CS_standard', cs_standard, None),
    ('CS_FG0_transparent', cs_fg0_transparent, [PASTEL_PALETTE[3]]*4),
    ('FGBG_standard', fgbg_standard, None),
    ('FGBG_alt', fgbg_alt, None),
    ('FGBG_custom_encoding', fgbg_custom_encoding, None),
]

print()
for name, decode_fn, default_cs in formats:
    total = 0
    match = 0
    tile_correct = 0
    tile_total = 0
    
    for w, (row, col) in samples.items():
        result = decode_fn(w)
        if result is None:
            continue
        card, is_gram, fg, bg, transparent = result
        
        # Get card bytes
        if is_gram:
            cidx = card & 0x3F
            card_bytes = bytes(8)  # GRAM not loaded for this test
        else:
            cidx = card & 0xFF
            base = cidx * 8
            card_bytes = grom[base:base+8] if base+8 <= len(grom) else bytes(8)
        
        if bg is None:
            # Use color stack default
            bg = PASTEL_PALETTE[3]
        
        tile_match = True
        tile_pixels = 0
        
        for y in range(8):
            b = card_bytes[y]
            for x in range(8):
                bit = (b >> (7-x)) & 1
                jx = JLEFT + col*8 + x
                jy = JTOP + row*8 + y
                if jx >= scr.width or jy >= scr.height:
                    continue
                
                actual = jz_rgb(jz_px[jx, jy])
                
                if transparent:
                    expected = bg  # CS background for all pixels
                else:
                    expected = fg if bit else bg
                
                total += 1
                tile_pixels += 1
                if expected == actual:
                    match += 1
                else:
                    tile_match = False
        
        tile_total += 1
        if tile_match:
            tile_correct += 1
    
    acc = match / total * 100 if total > 0 else 0
    tile_acc = tile_correct / tile_total * 100 if tile_total > 0 else 0
    print(f"{name:30s}: pixel {acc:.1f}% ({match}/{total})  tile {tile_acc:.1f}% ({tile_correct}/{tile_total})")

# Now: per-tile breakdown for the best format
print()
print("=" * 90)
print("PER-TILE BREAKDOWN (CS_FG0_transparent + CS default PAS[3])")
print("=" * 90)
print(f"{'Word':>6s} {'Card':>4s} {'GRAM':>4s} {'FG':>3s} {'FGidx':>6s} {'b0Real':>30s} {'b1Real':>30s} {'b0Exp':>30s} {'b1Exp':>30s}")
print("-" * 130)

for w, (row, col) in sorted(samples.items()):
    card, is_gram, fg_rgb, _, transparent = cs_fg0_transparent(w)
    
    # Get card bytes
    if is_gram:
        cidx = card & 0x3F
        card_bytes = bytes(8)
    else:
        cidx = card & 0xFF
        base = cidx * 8
        card_bytes = grom[base:base+8] if base+8 <= len(grom) else bytes(8)
    
    fg_idx = ((w >> 13) & 0x6) | ((w >> 12) & 0x1)
    bg = PASTEL_PALETTE[3]  # Color Stack default
    
    # Collect real jzIntv colors
    bit0_real = {}
    bit1_real = {}
    for y in range(8):
        b = card_bytes[y]
        for x in range(8):
            bit = (b >> (7-x)) & 1
            jx = JLEFT + col*8 + x
            jy = JTOP + row*8 + y
            if jx < scr.width and jy < scr.height:
                rgb = jz_rgb(jz_px[jx, jy])
                if bit == 0:
                    bit0_real[rgb] = bit0_real.get(rgb, 0) + 1
                else:
                    bit1_real[rgb] = bit1_real.get(rgb, 0) + 1
    
    def cn(rgb):
        for d, lbl in [(PALETTE, 'PAL'), (PASTEL_PALETTE, 'PAS')]:
            for k, v in d.items():
                if v == rgb: return '%s[%d]' % (lbl, k)
        if rgb == (0,0,0): return 'BLACK'
        return 'RGB'+str(rgb)
    
    b0_str = ', '.join('%s:%d' % (cn(c), n) for c, n in sorted(bit0_real.items(), key=lambda x: -x[1]) or [(None,0)])
    b1_str = ', '.join('%s:%d' % (cn(c), n) for c, n in sorted(bit1_real.items(), key=lambda x: -x[1]) or [(None,0)])
    
    # Expected colors
    if transparent:
        b0_exp = cn(bg)
        b1_exp = cn(bg)
    else:
        b0_exp = cn(bg)
        b1_exp = cn(fg_rgb)
    
    gram = 'GRAM' if is_gram else 'grom'
    print(f"0x{w:04X} {cidx:4d} {gram:4s} {cn(fg_rgb):3s} {fg_idx:4d}   {b0_str:30s} {b1_str:30s} {b0_exp:30s} {b1_exp:30s}")

# Check: which tiles have FG != 0?
print()
print("=" * 90)
print("TILES WITH NON-ZERO FG COLOR (FGidx > 0)")
print("=" * 90)
for w, (row, col) in sorted(samples.items()):
    fg_idx = ((w >> 13) & 0x6) | ((w >> 12) & 0x1)
    if fg_idx > 0:
        print(f"  0x{w:04X}: FGidx={fg_idx} card={w & 0x7FF & (0x3F if (w & 0x0800) else 0xFF)}")
