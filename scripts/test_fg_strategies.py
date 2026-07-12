#!/usr/bin/env python3
"""Test multiple FG color extraction strategies against jzIntv room 0 screenshot."""

import os, sys
sys.path.insert(0, '.')
from render_all_rooms import (
    load_grom, parse_backtab, extract_backtab_from_output,
    extract_gram_from_output, parse_memory_dump, decode_backtab_word,
    render_card_1bpp_with_bitmap, render_gram_card_with_bitmap,
    render_grom_card_with_bitmap,
    get_grom_card_bytes,
    PALETTE, PASTEL_PALETTE, DEFAULT_BG,
)
from PIL import Image

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Load room 0 data
with open('traces/_cmp_room_0_out.txt', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

grid = parse_backtab(extract_backtab_from_output(content))
gram_text = extract_gram_from_output(content)
gram_mem = parse_memory_dump(gram_text, 0x3800, 512) if gram_text else {}
grom = load_grom()

# Load jzIntv screenshot
scr = Image.open('sprites/room_0_jzintv.gif')
jz_pal = scr.getpalette()
jz_px = scr.load()

# Find dungeon bounds
left = None
for x in range(scr.width):
    for y in range(scr.height):
        if jz_px[x, y] != 0:
            left = x
            break
    if left is not None:
        break
top = None
for y in range(scr.height):
    for x in range(scr.width):
        if jz_px[x, y] != 0:
            top = y
            break
    if top is not None:
        break

if left is None or top is None:
    left, top = 80, 52

jz_dungeon = scr.crop((left, top, left + 160, top + 96))

def jz_rgb(idx):
    if idx * 3 + 2 < len(jz_pal):
        return (jz_pal[idx*3], jz_pal[idx*3+1], jz_pal[idx*3+2])
    return (0, 0, 0)


def _fg_color_for_index(fg_idx):
    """Standard palette lookup."""
    if fg_idx >= 8:
        return PASTEL_PALETTE.get(fg_idx - 8, (255, 0, 255))
    return PALETTE.get(fg_idx, (255, 0, 255))


def render_with_strategy(name, decode_fn, color_stack=None):
    """Render room 0 with a custom BACKTAB decode function.
    
    decode_fn(word) -> (card, fg, bg_bits, is_gram, fg_transparent)
    fg_transparent: if True, card bit=1 pixels show CS background instead of FG color.
    """
    if color_stack is None:
        color_stack = [PASTEL_PALETTE[3]] * 4
    
    cols, rows = 20, 12
    tile_size = 8
    img = Image.new('RGB', (cols * tile_size, rows * tile_size))
    px = img.load()
    cs_index = 0
    
    for row in range(rows):
        for col in range(cols):
            word = grid[row][col]
            result = decode_fn(word)
            if len(result) == 5:
                card_idx, fg_color_idx, bg_bits, is_gram, fg_transparent = result
            else:
                card_idx, fg_color_idx, bg_bits, is_gram = result
                fg_transparent = False
            
            # CS advance: standard bit 13
            advance = (word >> 13) & 1
            cs_index = (cs_index + advance) % 4
            bg = color_stack[cs_index]
            
            if is_gram:
                card_img, card_bitmap = render_gram_card_with_bitmap(
                    gram_mem, card_idx, fg_color_idx, bg)
            else:
                card_img, card_bitmap = render_grom_card_with_bitmap(
                    grom, card_idx, fg_color_idx, bg)
            
            for y in range(tile_size):
                for x in range(tile_size):
                    r, g, b = card_img.getpixel((x, y))
                    is_bg = card_bitmap[y][x]
                    if is_bg:
                        # Card bit=0: show CS background
                        px[col*8+x, row*8+y] = bg
                    elif fg_transparent:
                        # Card bit=1 but FG is "transparent": show CS background
                        px[col*8+x, row*8+y] = bg
                    else:
                        # Card bit=1: show FG color
                        px[col*8+x, row*8+y] = (r, g, b)
    
    return img


def compare_native(our_img):
    """Compare our native (1x zoom) render against jzIntv dungeon crop."""
    match = 0
    total = 0
    mismatches = {}
    our_colors = {}
    jz_colors = {}
    
    for y in range(min(96, our_img.height)):
        for x in range(min(160, our_img.width)):
            our_rgb = our_img.getpixel((x, y))
            jz_idx = jz_dungeon.getpixel((x, y))
            jz_rgb_val = jz_rgb(jz_idx)
            
            our_colors[our_rgb] = our_colors.get(our_rgb, 0) + 1
            jz_colors[jz_rgb_val] = jz_colors.get(jz_rgb_val, 0) + 1
            
            if our_rgb == jz_rgb_val:
                match += 1
            else:
                key = (our_rgb, jz_rgb_val)
                mismatches[key] = mismatches.get(key, 0) + 1
            total += 1
    
    return match, total, mismatches, our_colors, jz_colors


def color_name(rgb):
    for d, label in [(PALETTE, "PAL"), (PASTEL_PALETTE, "PAS")]:
        for k, v in d.items():
            if v == rgb:
                return f"{label}[{k}]"
    if rgb == (0, 0, 0):
        return "black"
    return ""


# ============================================================
# Strategy definitions
# ============================================================

# Strategy A: Current — FG from bits 15/14/12 (primary only)
def decode_current(word):
    card = word & 0x7FF
    is_gram = bool(word & 0x0800)
    fg = ((word >> 13) & 0x6) | ((word >> 12) & 0x1)
    return card, fg, word & 0x7, is_gram

# Strategy B: FG from bits 13/14/15 (sequential)
def decode_fg_13_15(word):
    card = word & 0x7FF
    is_gram = bool(word & 0x0800)
    fg = (word >> 13) & 0x7
    return card, fg, word & 0x7, is_gram

# Strategy C: FG from bits 9-11 (the old extraction)
def decode_fg_9_11(word):
    card = word & 0x7FF
    is_gram = bool(word & 0x0800)
    fg = (word >> 9) & 0x7
    return card, fg, word & 0x7, is_gram

# Strategy D: FG from bits 10-12
def decode_fg_10_12(word):
    card = word & 0x7FF
    is_gram = bool(word & 0x0800)
    fg = (word >> 10) & 0x7
    return card, fg, word & 0x7, is_gram

# Strategy E: FG=0 is transparent (use CS background for ALL pixels)
def decode_fg0_transparent(word):
    card = word & 0x7FF
    is_gram = bool(word & 0x0800)
    fg = ((word >> 13) & 0x6) | ((word >> 12) & 0x1)
    fg_transparent = (fg == 0)
    return card, fg, word & 0x7, is_gram, fg_transparent

# Strategy F: FG/BG mode (bits 3-11 = card, bits 0-3 = bg color, bits 12-15 = fg)
def decode_fgbg(word):
    bg_idx = word & 0x7
    bg_pastel = (word >> 3) & 1
    card = (word >> 3) & 0x1FF  # bits 3-11
    fg_color = (word >> 12) & 0x7
    fg_pastel = (word >> 15) & 1
    fg = fg_color + (8 if fg_pastel else 0)
    is_gram = bool(word & 0x0800)  # bit 11 = GRAM flag (same position as CS mode)
    
    # In FG/BG mode, background is per-tile, not from CS
    bg = PASTEL_PALETTE.get(bg_idx, DEFAULT_BG) if bg_pastel else PALETTE.get(bg_idx, DEFAULT_BG)
    return card, fg, bg_idx, is_gram

# Strategy G: FG/BG mode with transparent FG=0
def decode_fgbg_fg0transparent(word):
    bg_idx = word & 0x7
    bg_pastel = (word >> 3) & 1
    card = (word >> 3) & 0x1FF
    fg_color = (word >> 12) & 0x7
    fg_pastel = (word >> 15) & 1
    fg = fg_color + (8 if fg_pastel else 0)
    is_gram = bool(word & 0x0800)
    fg_transparent = (fg_color == 0 and not fg_pastel)
    bg = PASTEL_PALETTE.get(bg_idx, DEFAULT_BG) if bg_pastel else PALETTE.get(bg_idx, DEFAULT_BG)
    return card, fg, bg_idx, is_gram, fg_transparent

# Strategy H: Variable CS advance from bits 0-2 instead of bit 13
def decode_var_cs_advance(word):
    """FG from bits 15/14/12, but CS advances by (word & 0x7) positions, not bit 13."""
    card = word & 0x7FF
    is_gram = bool(word & 0x0800)
    fg = ((word >> 13) & 0x6) | ((word >> 12) & 0x1)
    return card, fg, word & 0x7, is_gram

# ============================================================
# Run all strategies
# ============================================================

strategies = [
    ("A: Current (FG=15/14/12, CS bit13)", decode_current, False, False),
    ("B: FG=13/14/15 (sequential bits)", decode_fg_13_15, False, False),
    ("C: FG=9-11 (old extraction)", decode_fg_9_11, False, False),
    ("D: FG=10-12", decode_fg_10_12, False, False),
    ("E: FG=15/14/12, FG=0 transparent", decode_fg0_transparent, False, False),
]

print("=" * 70)
print("  FG STRATEGY COMPARISON — Room 0")
print("=" * 70)
print()

for label, decode_fn, use_fgbg, cs_advance_var in strategies:
    if use_fgbg:
        # FG/BG mode rendering (per-tile bg)
        img = render_with_strategy(label, decode_fn)
    elif cs_advance_var:
        # Variable CS advance from bits 0-2
        color_stack = [PASTEL_PALETTE[3]] * 4
        cols, rows = 20, 12
        tile_size = 8
        img = Image.new('RGB', (cols * tile_size, rows * tile_size))
        px = img.load()
        cs_index = 0
        for row in range(rows):
            for col in range(cols):
                word = grid[row][col]
                result = decode_fn(word)
                card_idx, fg_color_idx, bg_bits, is_gram = result[:4]
                fg_transparent = result[4] if len(result) >= 5 else False
                
                # CS advance from bits 0-2
                advance = word & 0x7
                cs_index = (cs_index + advance) % 4
                bg = color_stack[cs_index]
                
                if is_gram:
                    card_img, card_bitmap = render_gram_card_with_bitmap(
                        gram_mem, card_idx, fg_color_idx, bg)
                else:
                    card_img, card_bitmap = render_grom_card_with_bitmap(
                        grom, card_idx, fg_color_idx, bg)
                
                for y in range(tile_size):
                    for x in range(tile_size):
                        r, g, b = card_img.getpixel((x, y))
                        is_bg = card_bitmap[y][x]
                        if is_bg or fg_transparent:
                            px[col*8+x, row*8+y] = bg
                        else:
                            px[col*8+x, row*8+y] = (r, g, b)
    else:
        img = render_with_strategy(label, decode_fn)
    
    match, total, mismatches, our_cols, jz_cols = compare_native(img)
    pct = 100.0 * match / total
    
    print(f"\n--- {label} ---")
    print(f"  Match: {match:,}/{total:,} = {pct:.1f}%")
    
    # Show top 5 mismatches
    print(f"  Top 5 mismatches:")
    for (our, jz), n in sorted(mismatches.items(), key=lambda x: -x[1])[:5]:
        our_n = color_name(our)
        jz_n = color_name(jz)
        print(f"    {our_n:12s} -> {jz_n:12s}  {n:5d} px")
    
    # Show our top colors
    print(f"  Our top colors:")
    for c, n in sorted(our_cols.items(), key=lambda x: -x[1])[:5]:
        name = color_name(c)
        print(f"    {name:12s} {n:6d} ({100*n/total:.1f}%)")
    
    # Show jzIntv top colors  
    print(f"  jzIntv top colors:")
    for c, n in sorted(jz_cols.items(), key=lambda x: -x[1])[:5]:
        name = color_name(c)
        print(f"    {name:12s} {n:6d} ({100*n/total:.1f}%)")

# Also test FG/BG mode separately (different rendering approach)
print()
print("=" * 70)
print("  FG/BG MODE TESTS")
print("=" * 70)

for label, decode_fn in [
    ("F: FG/BG mode (card=bits3-11)", decode_fgbg),
    ("G: FG/BG + FG=0 transparent", decode_fgbg_fg0transparent),
]:
    cols, rows = 20, 12
    tile_size = 8
    img = Image.new('RGB', (cols * tile_size, rows * tile_size))
    px = img.load()
    
    for row in range(rows):
        for col in range(cols):
            word = grid[row][col]
            result = decode_fn(word)
            card_idx = result[0]
            fg_color_idx = result[1]
            bg_idx = result[2]
            is_gram = result[3]
            fg_transparent = result[4] if len(result) >= 5 else False
            
            # FG/BG mode: per-tile background
            bg_pastel = (word >> 3) & 1
            bg = PASTEL_PALETTE.get(bg_idx, DEFAULT_BG) if bg_pastel else PALETTE.get(bg_idx, DEFAULT_BG)
            
            if is_gram:
                card_img, card_bitmap = render_gram_card_with_bitmap(
                    gram_mem, card_idx, fg_color_idx, bg)
            else:
                card_img, card_bitmap = render_grom_card_with_bitmap(
                    grom, card_idx, fg_color_idx, bg)
            
            for y in range(tile_size):
                for x in range(tile_size):
                    r, g, b = card_img.getpixel((x, y))
                    is_bg = card_bitmap[y][x]
                    if is_bg or fg_transparent:
                        px[col*8+x, row*8+y] = bg
                    else:
                        px[col*8+x, row*8+y] = (r, g, b)
    
    match, total, mismatches, our_cols, jz_cols = compare_native(img)
    pct = 100.0 * match / total
    
    print(f"\n--- {label} ---")
    print(f"  Match: {match:,}/{total:,} = {pct:.1f}%")
    print(f"  Top 5 mismatches:")
    for (our, jz), n in sorted(mismatches.items(), key=lambda x: -x[1])[:5]:
        our_n = color_name(our)
        jz_n = color_name(jz)
        print(f"    {our_n:12s} -> {jz_n:12s}  {n:5d} px")
    print(f"  Our top colors:")
    for c, n in sorted(our_cols.items(), key=lambda x: -x[1])[:5]:
        name = color_name(c)
        print(f"    {name:12s} {n:6d} ({100*n/total:.1f}%)")

# Strategy H: Variable CS advance
print()
print("=" * 70)
print("  VARIABLE CS ADVANCE TEST")
print("=" * 70)

color_stack = [PASTEL_PALETTE[3]] * 4
cols, rows = 20, 12
tile_size = 8
img = Image.new('RGB', (cols * tile_size, rows * tile_size))
px = img.load()
cs_index = 0

for row in range(rows):
    for col in range(cols):
        word = grid[row][col]
        card = word & 0x7FF
        is_gram = bool(word & 0x0800)
        fg = ((word >> 13) & 0x6) | ((word >> 12) & 0x1)
        
        # Variable CS advance from bits 0-2
        advance = word & 0x7
        cs_index = (cs_index + advance) % 4
        bg = color_stack[cs_index]
        
        if is_gram:
            card_img, card_bitmap = render_gram_card_with_bitmap(
                gram_mem, card, fg, bg)
        else:
            card_img, card_bitmap = render_grom_card_with_bitmap(
                grom, card, fg, bg)
        
        for y in range(tile_size):
            for x in range(tile_size):
                r, g, b = card_img.getpixel((x, y))
                is_bg = card_bitmap[y][x]
                if is_bg:
                    px[col*8+x, row*8+y] = bg
                else:
                    px[col*8+x, row*8+y] = (r, g, b)

match, total, mismatches, our_cols, jz_cols = compare_native(img)
pct = 100.0 * match / total

print(f"\n--- H: Variable CS advance (bits 0-2) + FG=15/14/12 ---")
print(f"  Match: {match:,}/{total:,} = {pct:.1f}%")
print(f"  Top 5 mismatches:")
for (our, jz), n in sorted(mismatches.items(), key=lambda x: -x[1])[:5]:
    our_n = color_name(our)
    jz_n = color_name(jz)
    print(f"    {our_n:12s} -> {jz_n:12s}  {n:5d} px")
print(f"  Our top colors:")
for c, n in sorted(our_cols.items(), key=lambda x: -x[1])[:5]:
    name = color_name(c)
    print(f"    {name:12s} {n:6d} ({100*n/total:.1f}%)")

print()
print("Done.")
