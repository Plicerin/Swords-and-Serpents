#!/usr/bin/env python3
"""Pixel-level correlation: for each tile, compare GROM card bits vs jzIntv colors."""
import sys
sys.path.insert(0, '.')
from render_all_rooms import (
    load_grom, parse_backtab, extract_backtab_from_output,
    extract_gram_from_output, parse_memory_dump,
    PALETTE, PASTEL_PALETTE, DEFAULT_BG,
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

def cn(rgb):
    for d, lbl in [(PALETTE, 'PAL'), (PASTEL_PALETTE, 'PAS')]:
        for k, v in d.items():
            if v == rgb: return '%s[%d]' % (lbl, k)
    if rgb == (0,0,0): return 'BLACK'
    return str(rgb)

# For each unique BACKTAB word, sample one tile position and do pixel-level analysis
print("=" * 80)
print("PIXEL-LEVEL CORRELATION: Card bit 0 -> jz color, Card bit 1 -> jz color")
print("=" * 80)

word_info = {}
for row in range(12):
    for col in range(20):
        w = grid[row][col]
        if w in word_info:
            continue
        
        card = w & 0x7FF
        is_gram = bool(w & 0x0800)
        # Standard FG extraction
        fg_std = ((w >> 13) & 0x6) | ((w >> 12) & 0x1)
        cs_adv_std = (w >> 13) & 1
        
        # Get card bytes
        if is_gram:
            cidx = card & 0x3F
            base = 0x3800 + cidx * 8
            card_bytes = bytes(gram_mem.get(base+r, 0) & 0xFF for r in range(8))
        else:
            cidx = card & 0xFF
            base = cidx * 8
            card_bytes = grom[base:base+8] if base+8 <= len(grom) else bytes(8)
        
        # Pixel-level analysis
        bit0_colors = {}  # card bit=0 -> jz colors
        bit1_colors = {}  # card bit=1 -> jz colors
        
        for y in range(8):
            b = card_bytes[y]
            for x in range(8):
                bit = (b >> (7-x)) & 1
                jz_idx = jz_px[JLEFT + col*8 + x, JTOP + row*8 + y]
                jz_val = jz_rgb(jz_idx)
                if bit == 0:
                    bit0_colors[jz_val] = bit0_colors.get(jz_val, 0) + 1
                else:
                    bit1_colors[jz_val] = bit1_colors.get(jz_val, 0) + 1
        
        bits_set = sum(bin(b).count('1') for b in card_bytes)
        
        word_info[w] = {
            'card': card, 'cidx': cidx, 'is_gram': is_gram,
            'fg_std': fg_std, 'cs_adv_std': cs_adv_std,
            'bits_set': bits_set,
            'bit0_colors': bit0_colors, 'bit1_colors': bit1_colors,
            'card_bytes': list(card_bytes),
            'row': row, 'col': col,
        }

# Group tiles by rendering pattern
hdr0 = 'Bit=0 -> jzIntv'
hdr1 = 'Bit=1 -> jzIntv'
print("\n%6s %4s %4s %4s %3s %5s  %35s  %35s" % ('Word', 'c8', 'Gram', 'FGst', 'Adv', 'Bits', hdr0, hdr1))
print("-" * 130)

for w, info in sorted(word_info.items(), key=lambda x: (len(x[1]['bit0_colors']), len(x[1]['bit1_colors']), -x[1]['bits_set'])):
    bit0_str = ', '.join('%s:%d' % (cn(c), n) for c, n in sorted(info['bit0_colors'].items(), key=lambda x: -x[1]))
    bit1_str = ', '.join('%s:%d' % (cn(c), n) for c, n in sorted(info['bit1_colors'].items(), key=lambda x: -x[1]))
    gram_str = 'GRAM' if info['is_gram'] else 'grom'
    print("0x%04X %4d %4s %4d %3d %5d  %35s  %35s" % (w, info['cidx'], gram_str, info['fg_std'], info['cs_adv_std'], info['bits_set'], bit0_str, bit1_str))

# Summary: for tiles where card bit=0 pixels are ALL the same color...
print()
print("=" * 80)
print("TILES WITH UNIFORM BIT=0 COLOR (consistent CS bg)")
print("=" * 80)
for w, info in sorted(word_info.items(), key=lambda x: len(x[1]['bit0_colors'])):
    if len(info['bit0_colors']) == 1:
        bg_color = list(info['bit0_colors'].keys())[0]
        bg_count = list(info['bit0_colors'].values())[0]
        bit1_str = ', '.join('%s:%d' % (cn(c), n) for c, n in sorted(info['bit1_colors'].items(), key=lambda x: -x[1]))
        print("  0x%04X: c8=%3d bits=%2d/64 FGstd=%d adv_std=%d  bit0->%s:%d  bit1->%s" % (
            w, info['cidx'], info['bits_set'], info['fg_std'], info['cs_adv_std'], cn(bg_color), bg_count, bit1_str))

# Key question: for tiles where BOTH bit0 and bit1 have single colors, what are they?
print()
print("=" * 80)
print("TILES WITH UNIFORM BIT=0 AND UNIFORM BIT=1 COLORS")
print("=" * 80)
for w, info in sorted(word_info.items(), key=lambda x: len(x[1]['bit0_colors'])):
    if len(info['bit0_colors']) == 1 and len(info['bit1_colors']) == 1:
        bg_color = list(info['bit0_colors'].keys())[0]
        fg_color = list(info['bit1_colors'].keys())[0]
        print("  0x%04X: c8=%3d bits=%2d/64  CS=%s  FG_apparent=%s  FGstd=%d" % (
            w, info['cidx'], info['bits_set'], cn(bg_color), cn(fg_color), info['fg_std']))

PYEOF
