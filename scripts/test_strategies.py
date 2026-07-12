#!/usr/bin/env python3
"""Test render with different BACKTAB decode strategies and compare to jzIntv."""
import sys
sys.path.insert(0, '.')
from render_all_rooms import (
    load_grom, parse_backtab, extract_backtab_from_output,
    extract_gram_from_output, parse_memory_dump,
    PALETTE, PASTEL_PALETTE, DEFAULT_BG,
    render_grom_card, render_gram_card, render_grom_card_with_bitmap, render_gram_card_with_bitmap,
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

# Default CS background (all pastel tan as set by EXEC.730)
CS_DEFAULT = [PASTEL_PALETTE[3]] * 4

def decode_strategy(word, strategy):
    """Test different decode strategies. Returns (card, fg_color, is_gram, fg_transparent, cs_adv)."""
    is_gram = bool(word & 0x0800)
    card = word & 0xFF
    if is_gram:
        card = card & 0x3F
    
    if strategy == 'standard_cs':
        # Standard Color Stack: FG from bits 15,14,12
        fg = ((word >> 13) & 0x6) | ((word >> 12) & 0x1)
        fg_transparent = (fg == 0)
        cs_adv = (word >> 13) & 1
        return card, fg, is_gram, fg_transparent, cs_adv
    
    elif strategy == 'fg_bit12_only':
        # Only bit 12 as FG
        fg = (word >> 12) & 1
        fg_transparent = (fg == 0)
        cs_adv = (word >> 13) & 1
        return card, fg, is_gram, fg_transparent, cs_adv
    
    elif strategy == 'fg_bits_15_14_12':
        fg = ((word >> 14) & 0x3 << 1) | ((word >> 12) & 0x1)
        fg_transparent = (fg == 0)
        cs_adv = (word >> 13) & 1
        return card, fg, is_gram, fg_transparent, cs_adv
    
    elif strategy == 'fg_fgbg_mode':
        # FG/BG mode encoding
        fg = (word >> 12) & 0x7
        fg_transparent = (fg == 0)
        cs_adv = (word >> 13) & 1
        return card, fg, is_gram, fg_transparent, cs_adv
    
    elif strategy == 'never_transparent':
        # FG never transparent
        fg = ((word >> 13) & 0x6) | ((word >> 12) & 0x1)
        fg_transparent = False
        cs_adv = (word >> 13) & 1
        return card, fg, is_gram, fg_transparent, cs_adv
    
    return card, 0, is_gram, True, 0

def render_room_with_strategy(strategy, zoom=4):
    """Render room 0 with a specific decode strategy."""
    cols, rows = 20, 12
    tile_size = 8
    img_w = cols * tile_size * zoom
    img_h = rows * tile_size * zoom
    img = Image.new('RGB', (img_w, img_h))
    px = img.load()
    
    cs_index = 0
    
    for row in range(rows):
        for col in range(cols):
            word = grid[row][col]
            card, fg, is_gram, fg_transparent, cs_adv = decode_strategy(word, strategy)
            
            # CS advance
            cs_index = (cs_index + cs_adv) % 4
            bg = CS_DEFAULT[cs_index]
            
            # FG color
            if fg >= 8:
                fg_rgb = PASTEL_PALETTE.get(fg - 8, (255, 0, 255))
            else:
                fg_rgb = PALETTE.get(fg, (255, 0, 255))
            
            if is_gram:
                card_img, bitmap = render_gram_card_with_bitmap(gram_mem, card, fg, bg)
            else:
                card_img, bitmap = render_grom_card_with_bitmap(grom, card, fg, bg)
            
            for y in range(tile_size):
                for x in range(tile_size):
                    r, g, b = card_img.getpixel((x, y))
                    is_bg = bitmap[y][x]
                    
                    if is_bg or fg_transparent:
                        draw_rgb = bg
                    else:
                        draw_rgb = (r, g, b)
                    
                    for dy in range(zoom):
                        for dx in range(zoom):
                            px_x = col * tile_size * zoom + x * zoom + dx
                            px_y = row * tile_size * zoom + y * zoom + dy
                            px[px_x, px_y] = draw_rgb
    
    return img

def compare_to_jzintv(rendered_img):
    """Compare rendered image to jzIntv screenshot, return accuracy."""
    jz = scr
    match = 0
    total = 0
    for py in range(12 * 8):
        for px_x in range(20 * 8):
            # Map to jzIntv screenshot coordinates
            jx = JLEFT + px_x
            jy = JTOP + py
            
            if jx >= jz.width or jy >= jz.height:
                continue
            
            jz_idx = jz_px[jx, jy]
            jz_rgb_val = jz_rgb(jz_idx)
            
            # Get rendered pixel at 1x zoom
            r_px = rendered_img.getpixel((px_x * 4 + 2, py * 4 + 2))  # sample center
            r_px = tuple(r_px)
            
            total += 1
            if r_px == jz_rgb_val:
                match += 1
    
    return match / total * 100 if total > 0 else 0

# Test strategies
strategies = ['standard_cs', 'fg_bit12_only', 'fg_bits_15_14_12', 'fg_fgbg_mode', 'never_transparent']

print("=" * 70)
print("BACKTAB DECODE STRATEGY COMPARISON (vs jzIntv)")
print("=" * 70)
print()

for strat in strategies:
    print(f"Strategy: {strat}")
    img = render_room_with_strategy(strat)
    acc = compare_to_jzintv(img)
    print(f"  Accuracy: {acc:.1f}%")
    
    # Sample a few tiles to see colors
    # Floor at (0,0)
    word = grid[0][0]
    card, fg, is_gram, fg_transparent, cs_adv = decode_strategy(word, strat)
    print(f"  Floor (0,0) word=0x{word:04X}: card={card} fg={fg} transp={fg_transparent}")
    
    # Wall at (0,5) - find a non-floor tile
    wall_word = None
    wall_pos = None
    for r in range(12):
        for c in range(20):
            if grid[r][c] != 0x1603:
                wall_word = grid[r][c]
                wall_pos = (r, c)
                break
        if wall_word:
            break
    
    if wall_word:
        card, fg, is_gram, fg_transparent, cs_adv = decode_strategy(wall_word, strat)
        print(f"  Wall {wall_pos} word=0x{wall_word:04X}: card={card} fg={fg} transp={fg_transparent}")
    
    # Save image
    img.save(f'sprites/test_render_{strat}.png')
    print(f"  Saved: sprites/test_render_{strat}.png")
    print()

# Also check: what if we just use fg_transparent = (word >> 12) & 1 as a flag?
print("=" * 70)
print("TRANSPARENCY FLAG ANALYSIS")
print("=" * 70)
for r in range(12):
    for c in range(20):
        w = grid[r][c]
        bit12 = (w >> 12) & 1
        fg_std = ((w >> 13) & 0x6) | ((w >> 12) & 0x1)
        bit13 = (w >> 13) & 1
        is_gram = bool(w & 0x0800)
        card = w & 0xFF
        if is_gram:
            card = card & 0x3F
        
        # Check if this tile benefits from transparent FG
        if is_gram:
            cidx = card & 0x3F
            base = 0x3800 + cidx * 8
            card_bytes = bytes(gram_mem.get(base+ry, 0) & 0xFF for ry in range(8))
        else:
            cidx = card & 0xFF
            base = cidx * 8
            card_bytes = grom[base:base+8] if base+8 <= len(grom) else bytes(8)
        
        bits_set = sum(bin(b).count('1') for b in card_bytes)
        bits_clear = 64 - bits_set
        
        # If no FG pixels, transparency doesn't matter
        if bits_set == 0:
            continue
        
        # If no BG pixels, transparency doesn't change anything visually
        if bits_clear == 0:
            continue
        
        # Get jz colors for this tile
        jz_bit0 = {}
        jz_bit1 = {}
        for y in range(8):
            b = card_bytes[y]
            for x in range(8):
                bit = (b >> (7-x)) & 1
                idx = jz_px[JLEFT + c*8 + x, JTOP + r*8 + y]
                rgb_val = jz_rgb(idx)
                if bit == 0:
                    jz_bit0[rgb_val] = jz_bit0.get(rgb_val, 0) + 1
                else:
                    jz_bit1[rgb_val] = jz_bit1.get(rgb_val, 0) + 1
        
        bit0_set = set(jz_bit0.keys())
        bit1_set = set(jz_bit1.keys())
        
        if bit0_set == bit1_set:
            needs_transparent = True
        else:
            needs_transparent = False
        
        # Only print first occurrence of each word
        if (r == 0 and c < 3) or (w not in [grid[rr][cc] for rr in range(r+1) for cc in range(20) if rr < r or (rr == r and cc < c)]):
            continue  # Skip duplicates
        
PYEOF
