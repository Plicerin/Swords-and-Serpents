#!/usr/bin/env python3
"""Test specific BACKTAB decode strategies and create comparison images."""
import sys
sys.path.insert(0, '.')
from render_all_rooms import (
    load_grom, parse_backtab, extract_backtab_from_output,
    extract_gram_from_output, parse_memory_dump,
    PALETTE, PASTEL_PALETTE, DEFAULT_BG,
    render_grom_card_with_bitmap, render_gram_card_with_bitmap,
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

JLEFT, JTOP = 80, 52
CS_DEFAULT = [PASTEL_PALETTE[3]] * 4

def render_with_decode(word, decode_fn, grom, gram_mem, bg):
    """Render single tile with a decode function. Returns (img, bitmap)."""
    card, fg, is_gram, fg_transparent, cs_adv = decode_fn(word)
    
    if fg >= 8:
        fg_rgb = PASTEL_PALETTE.get(fg - 8, (255,0,255))
    else:
        fg_rgb = PALETTE.get(fg, (255,0,255))
    
    if is_gram:
        return render_gram_card_with_bitmap(gram_mem, card, fg, bg)
    else:
        return render_grom_card_with_bitmap(grom, card, fg, bg)

# Strategy 1: bit12 = transparent flag, FG=0 always
def decode_v1(word):
    is_gram = bool(word & 0x0800)
    card = word & 0xFF
    if is_gram:
        card = card & 0x3F
    fg_transparent = bool((word >> 12) & 1)
    fg = 0
    cs_adv = (word >> 13) & 1
    return card, fg, is_gram, fg_transparent, cs_adv

# Strategy 2: bit12 = transparent flag, FG = bit 9
def decode_v2(word):
    is_gram = bool(word & 0x0800)
    card = word & 0xFF
    if is_gram:
        card = card & 0x3F
    fg_transparent = bool((word >> 12) & 1)
    fg = ((word >> 9) & 0x7)  # bits 11,10,9
    cs_adv = (word >> 13) & 1
    return card, fg, is_gram, fg_transparent, cs_adv

# Strategy 3: bit12 transparent, FG from palette lookup
def decode_v3(word):
    is_gram = bool(word & 0x0800)
    card = word & 0xFF
    if is_gram:
        card = card & 0x3F
    fg_transparent = bool((word >> 12) & 1)
    # FG color = whatever the card's high nybble implies
    # In INTY, different wall types have different FG colors
    # Map card ranges to colors
    fg = 1  # blue for walls
    cs_adv = (word >> 13) & 1
    return card, fg, is_gram, fg_transparent, cs_adv

# Strategy 4: bit12 transparent, FG=blue, CS advances per bit13
# (This matches the data best: transparent tiles show PAS[3], opaque show blue/white)
def decode_v4(word):
    is_gram = bool(word & 0x0800)
    card = word & 0xFF
    if is_gram:
        card = card & 0x3F
    fg_transparent = bool((word >> 12) & 1)
    fg = 1  # blue
    cs_adv = (word >> 13) & 1
    return card, fg, is_gram, fg_transparent, cs_adv

# Compare each strategy
strategies = {
    'v1_transp_fg0': decode_v1,
    'v2_transp_fg_bits9': decode_v2,
    'v3_transp_fg_blue': decode_v3,
    'v4_transp_fg_blue2': decode_v4,
}

print("Testing decode strategies...")
print()

for name, decode_fn in strategies.items():
    match = 0
    total = 0
    cs = 0
    
    for row in range(12):
        for col in range(20):
            word = grid[row][col]
            card, fg, is_gram, fg_transparent, cs_adv = decode_fn(word)
            
            cs = (cs + cs_adv) % 4
            bg = CS_DEFAULT[cs]
            
            if fg_transparent:
                # Both bits show CS background
                for y in range(8):
                    for x in range(8):
                        jx = JLEFT + col*8 + x
                        jy = JTOP + row*8 + y
                        if jx < scr.width and jy < scr.height:
                            expected = bg
                            actual = jz_rgb(jz_px[jx, jy])
                            total += 1
                            if expected == actual:
                                match += 1
            else:
                # Get card and compare pixel by pixel
                if is_gram:
                    cidx = card & 0x3F
                    baddr = 0x3800 + cidx * 8
                    card_bytes = bytes(gram_mem.get(baddr+ry, 0) & 0xFF for ry in range(8))
                else:
                    cidx = card & 0xFF
                    baddr = cidx * 8
                    card_bytes = grom[baddr:baddr+8] if baddr+8 <= len(grom) else bytes(8)
                
                fg_rgb = PALETTE.get(fg, (255,0,255))
                
                for y in range(8):
                    by = card_bytes[y]
                    for x in range(8):
                        bit = (by >> (7-x)) & 1
                        jx = JLEFT + col*8 + x
                        jy = JTOP + row*8 + y
                        if jx < scr.width and jy < scr.height:
                            total += 1
                            if bit == 0:
                                expected = bg
                            else:
                                expected = fg_rgb
                            actual = jz_rgb(jz_px[jx, jy])
                            if expected == actual:
                                match += 1
    
    acc = match / total * 100 if total > 0 else 0
    print(f"{name:30s}: {acc:.1f}% accuracy ({match}/{total} pixels)")

# Now also just dump what some key tiles SHOULD look like
print()
print("=" * 70)
print("TILE COLOR ANALYSIS (what jzIntv actually shows)")
print("=" * 70)

for w, (r, c, _) in sorted({w: (r,c,[]) for r in range(12) for c in range(20) for w in [grid[r][c]]}.items()):
    if w == 0x1603:
        continue  # skip floor, already know it's all PAS[3]
    
    card = w & 0xFF
    is_gram = bool(w & 0x0800)
    if is_gram:
        cidx = card & 0x3F
        baddr = 0x3800 + cidx * 8
        card_bytes = bytes(gram_mem.get(baddr+ry, 0) & 0xFF for ry in range(8))
    else:
        cidx = card & 0xFF
        baddr = cidx * 8
        card_bytes = grom[baddr:baddr+8] if baddr+8 <= len(grom) else bytes(8)
    
    bits_set = sum(bin(b).count('1') for b in card_bytes)
    if bits_set == 0 or bits_set == 64:
        continue
    
    # Sample pixel colors from jzIntv
    bit0_colors = {}
    bit1_colors = {}
    for y in range(8):
        by = card_bytes[y]
        for x in range(8):
            bit = (by >> (7-x)) & 1
            jx = JLEFT + c*8 + x
            jy = JTOP + r*8 + y
            if jx < scr.width and jy < scr.height:
                rgb_val = jz_rgb(jz_px[jx, jy])
                if bit == 0:
                    bit0_colors[rgb_val] = bit0_colors.get(rgb_val, 0) + 1
                else:
                    bit1_colors[rgb_val] = bit1_colors.get(rgb_val, 0) + 1
    
    bit0_dom = max(bit0_colors.items(), key=lambda kv: kv[1]) if bit0_colors else (None, 0)
    bit1_dom = max(bit1_colors.items(), key=lambda kv: kv[1]) if bit1_colors else (None, 0)
    
    def cn(rgb):
        if rgb is None: return 'N/A'
        for d, lbl in [(PALETTE, 'PAL'), (PASTEL_PALETTE, 'PAS')]:
            for k, v in d.items():
                if v == rgb: return '%s[%d]' % (lbl, k)
        return str(rgb)
    
    bit12 = (w >> 12) & 1
    bit13 = (w >> 13) & 1
    bit9 = (w >> 9) & 1
    bit10 = (w >> 10) & 1
    src = 'GRAM' if is_gram else 'grom'
    
    print(f"0x{w:04X} {src:4s} card={cidx:3d} bits={bits_set:2d}/64 "
          f"b12={bit12} b13={bit13} b10,9={bit10}{bit9} "
          f"bit0={cn(bit0_dom[0])} bit1={cn(bit1_dom[0])}")
