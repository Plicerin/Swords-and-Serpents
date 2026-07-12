#!/usr/bin/env python3
"""Test different GROM address mapping schemes to find the correct one."""
import sys
sys.path.insert(0, '.')
from render_all_rooms import (
    load_grom, parse_backtab, extract_backtab_from_output,
    extract_gram_from_output, parse_memory_dump,
    PALETTE, PASTEL_PALETTE,
)
from PIL import Image

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

# FG: standard 15/14/12, csadv=13
def decode_std(word):
    card = word & 0x7FF
    is_gram = bool(word & 0x0800)
    fg = ((word >> 13) & 0x6) | ((word >> 12) & 0x1)
    fg_transparent = (fg == 0)
    cs_advance = (word >> 13) & 1
    return card, fg, is_gram, fg_transparent, cs_advance

# Different GROM mapping strategies
def get_grom_mask8(card_idx, grom):
    """Strategy A: mask to 8 bits (current)"""
    idx = card_idx & 0xFF
    base = idx * 8
    return grom[base:base+8] if base+8 <= len(grom) else bytes(8)

def get_grom_mask10(card_idx, grom):
    """Strategy B: mask to 10 bits, then 8 bits"""
    idx = (card_idx & 0x3FF) & 0xFF
    base = idx * 8
    return grom[base:base+8] if base+8 <= len(grom) else bytes(8)

def get_grom_stic14(card_idx, grom):
    """Strategy C: STIC 14-bit address wrapping"""
    addr = (0x3000 + card_idx * 8) & 0x3FFF
    if 0x3000 <= addr <= 0x37F8:
        offset = addr - 0x3000
        if offset + 8 <= len(grom):
            return grom[offset:offset+8]
    return bytes(8)

def get_grom_hole(card_idx, grom):
    """Strategy D: cards 256+ return zeros (GROM hole)"""
    if card_idx >= 256:
        return bytes(8)
    base = (card_idx & 0xFF) * 8
    return grom[base:base+8] if base+8 <= len(grom) else bytes(8)

def get_grom_stic_full(card_idx, grom):
    """Strategy E: STIC 14-bit wrapping, GROM responds to all 0x3000-0x3FFF"""
    addr = (0x3000 + card_idx * 8) & 0x3FFF
    if 0x3000 <= addr <= 0x3FFF:
        offset = addr - 0x3000
        grom_idx = offset // 8
        if grom_idx < 256:
            return grom[grom_idx*8:grom_idx*8+8]
    return bytes(8)

def render_and_compare(get_grom_fn, cs, fg0_trans):
    img = Image.new('RGB', (160, 96))
    px = img.load()
    cs_idx = 0
    for row in range(12):
        for col in range(20):
            w = grid[row][col]
            card, fg, is_gram, fg_trans, cs_adv = decode_std(w)
            cs_idx = (cs_idx + cs_adv) % 4
            bg = cs[cs_idx]
            fg_rgb = PALETTE.get(fg, (255,0,255))
            
            if is_gram:
                cidx = card & 0x3F
                base = 0x3800 + cidx * 8
                card_bytes = bytes(gram_mem.get(base+r, 0) & 0xFF for r in range(8))
            else:
                card_bytes = get_grom_fn(card, grom)
            
            eff_trans = fg_trans if fg0_trans else False
            for y in range(8):
                b = card_bytes[y]
                for x in range(8):
                    bit = (b >> (7-x)) & 1
                    if bit == 0 or eff_trans:
                        px[col*8+x, row*8+y] = bg
                    else:
                        px[col*8+x, row*8+y] = fg_rgb
    
    match = 0; total = 0; mm = {}
    for y in range(96):
        for x in range(160):
            our = img.getpixel((x, y))
            jz = jz_rgb(jz_px[JLEFT+x, JTOP+y])
            if our == jz: match += 1
            else:
                mm[(our, jz)] = mm.get((our, jz), 0) + 1
            total += 1
    return match, total, mm

def cn(rgb):
    for d, lbl in [(PALETTE, 'PAL'), (PASTEL_PALETTE, 'PAS')]:
        for k, v in d.items():
            if v == rgb: return f'{lbl}[{k}]'
    if rgb == (0,0,0): return 'BLACK'
    return str(rgb)

strategies = [
    ('A: mask8 (current)', get_grom_mask8),
    ('B: mask10->8', get_grom_mask10),
    ('C: STIC 14-bit wrap', get_grom_stic14),
    ('D: cards>=256->zero', get_grom_hole),
    ('E: STIC wrap GROM=all 0x3000-0x3FFF', get_grom_stic_full),
]

cs = [PASTEL_PALETTE[3]] * 4

print('=== GROM address mapping strategies ===')
print(f'CS=all PASTEL[3], fg0_trans=True')
print()
for name, fn in strategies:
    match, total, mm = render_and_compare(fn, cs, True)
    pct = 100.0 * match / total
    top = sorted(mm.items(), key=lambda x: -x[1])[:3]
    print(f'{name}: {pct:.1f}%')
    for (our, jz), n in top:
        print(f'  {cn(our):>10s} -> {cn(jz):>10s}: {n} px')
    print()

# Now try strategy D with different CS values
print('=== Strategy D (cards>=256->zero) with different CS ===')
for cs_name, cs_val in [
    ('all PASTEL[3]', [PASTEL_PALETTE[3]]*4),
    ('all PASTEL[5]', [PASTEL_PALETTE[5]]*4),
    ('all PAL[3]', [PALETTE[3]]*4),
    ('all PAL[1]', [PALETTE[1]]*4),
]:
    match, total, mm = render_and_compare(get_grom_hole, cs_val, True)
    pct = 100.0 * match / total
    top = sorted(mm.items(), key=lambda x: -x[1])[:3]
    print(f'  CS={cs_name}: {pct:.1f}%')
    for (our, jz), n in top:
        print(f'    {cn(our):>10s} -> {cn(jz):>10s}: {n} px')
