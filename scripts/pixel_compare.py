#!/usr/bin/env python3
"""Pixel-level comparison: check what our render shows vs jzIntv for specific tiles."""
import sys, os
sys.path.insert(0, '.')
from render_all_rooms import (
    load_grom, get_grom_card_bytes, parse_backtab, extract_backtab_from_output,
    extract_gram_from_output, parse_memory_dump, decode_backtab_word,
    render_room_image, render_grom_card, render_gram_card,
    PALETTE, PASTEL_PALETTE
)
from PIL import Image

# Load room 0 data
with open('traces/_cmp_room_0_out.txt', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
grid = parse_backtab(extract_backtab_from_output(content))
gram_text = extract_gram_from_output(content)
gram_mem = parse_memory_dump(gram_text, 0x3800, 512) if gram_text else {}
grom = load_grom()

# Load jzIntv screenshot
scr = Image.open('sprites/room_0_jzintv.gif')
scr_px = scr.load()
jz_pal = scr.getpalette()
def jz_rgb(idx):
    if jz_pal and idx * 3 + 2 < len(jz_pal):
        return (jz_pal[idx*3], jz_pal[idx*3+1], jz_pal[idx*3+2])
    return (0,0,0)

# Find dungeon bounds
def find_dungeon_bounds(scr_img, scr_px):
    left = top = None
    for x in range(scr_img.width):
        for y in range(scr_img.height):
            if scr_px[x, y] != 0:
                left = x; break
        if left is not None: break
    for y in range(scr_img.height):
        for x in range(scr_img.width):
            if scr_px[x, y] != 0:
                top = y; break
        if top is not None: break
    return left or 80, top or 52

d_left, d_top = find_dungeon_bounds(scr, scr_px)
print(f"Dungeon bounds: ({d_left}, {d_top})")

# Render at native resolution (zoom=1)
our_img = render_room_image(grid, gram_mem, grom, color_stack=None, zoom=1, mobs=None)
our_px = our_img.load()

# Examine SPECIFIC tiles
print("\n=== Floor tile at (5,5) ===")
row, col = 5, 5
word = grid[row][col]
card, fg, bg_bits, is_gram, fg_transparent = decode_backtab_word(word)
print(f"Word: 0x{word:04X}, card={card}, fg={fg}, gram={is_gram}")

# Our render pixels
print("\nOur render (8x8):")
for y in range(8):
    line = ""
    for x in range(8):
        r, g, b = our_px[col*8 + x, row*8 + y]
        for name, val in list(PALETTE.items()) + [(f"pas{k}",v) for k,v in PASTEL_PALETTE.items()]:
            if val == (r,g,b):
                line += f"{str(name):6s} "
                break
        else:
            if (r,g,b) == (0,0,0):
                line += "BLACK  "
            else:
                line += f"({r:3d},{g:3d},{b:3d}) "
    print(f"  {line}")

# jzIntv pixels
print("\njzIntv render (8x8):")
for y in range(8):
    line = ""
    for x in range(8):
        sx = d_left + col*8 + x
        sy = d_top + row*8 + y
        if 0 <= sx < scr.width and 0 <= sy < scr.height:
            pi = scr_px[sx, sy]
            rgb = jz_rgb(pi)
        else:
            rgb = (0,0,0)
        for name, val in list(PALETTE.items()) + [(f"pas{k}",v) for k,v in PASTEL_PALETTE.items()]:
            if val == rgb:
                line += f"{str(name):6s} "
                break
        else:
            line += f"({rgb[0]:3d},{rgb[1]:3d},{rgb[2]:3d}) "
    print(f"  {line}")

# Show GROM card 3 pattern
print("\nGROM card 3 bytes:")
for i in range(8):
    b = get_grom_card_bytes(grom, 3)[i]
    line = ""
    for bit in range(8):
        line += '#' if (b >> (7-bit)) & 1 else '.'
    print(f"  {b:02X} {line}")

# Check: does jzIntv floor have 1s where we have 0s?
print("\n=== Mismatch analysis for floor tile (5,5) ===")
mismatch_count = 0
our_ones_jz_zeros = 0
our_zeros_jz_ones = 0
for y in range(8):
    for x in range(8):
        our_rgb = our_px[col*8 + x, row*8 + y]
        sx = d_left + col*8 + x
        sy = d_top + row*8 + y
        jz_rgb_val = jz_rgb(scr_px[sx, sy]) if 0 <= sx < scr.width and 0 <= sy < scr.height else (0,0,0)
        if our_rgb != jz_rgb_val:
            mismatch_count += 1
            # Determine if our pixel is a card '1' (fg color) or '0' (bg color)
            card_byte = get_grom_card_bytes(grom, 3)[y]
            bit_val = (card_byte >> (7-x)) & 1
            our_is_one = (bit_val == 1)
            jz_is_pastel_tan = (jz_rgb_val == PASTEL_PALETTE[3])
            jz_is_blue = (jz_rgb_val == PALETTE[1])
            if our_is_one and jz_is_pastel_tan:
                our_ones_jz_zeros += 1
            elif not our_is_one and jz_is_blue:
                our_zeros_jz_ones += 1
            else:
                # Other mismatch
                pass

print(f"Total mismatches: {mismatch_count}/64")
print(f"Our 1s → jz pastel tan (bg): {our_ones_jz_zeros}")
print(f"Our 0s → jz blue (fg): {our_zeros_jz_ones}")

print("\n=== Now examine a WALL tile (0x081B, GRAM card 27) ===")
# Find first wall tile with 0x081B
wall_row = wall_col = None
for r in range(12):
    for c in range(20):
        if grid[r][c] == 0x081B:
            wall_row, wall_col = r, c
            break
    if wall_row is not None:
        break

if wall_row is not None:
    print(f"Wall tile at ({wall_row}, {wall_col})")
    print("\nGRAM card 27 bytes (raw from memory dump):")
    base = 0x3800 + 27 * 8
    has_data = False
    for i in range(8):
        b = gram_mem.get(base + i, 0) & 0xFF
        if b != 0:
            has_data = True
        line = ""
        for bit in range(8):
            line += '#' if (b >> (7-bit)) & 1 else '.'
        print(f"  {b:02X} {line}")
    print(f"  Has data: {has_data}")
    
    print("\nOur render (8x8):")
    for y in range(8):
        line = ""
        for x in range(8):
            r, g, b = our_px[wall_col*8 + x, wall_row*8 + y]
            for name, val in list(PALETTE.items()) + [(f"pas{k}",v) for k,v in PASTEL_PALETTE.items()]:
                if val == (r,g,b):
                    line += f"{str(name):6s} "
                    break
            else:
                if (r,g,b) == (0,0,0):
                    line += "BLACK  "
                else:
                    line += f"??     "
        print(f"  {line}")
    
    print("\njzIntv render (8x8):")
    for y in range(8):
        line = ""
        for x in range(8):
            sx = d_left + wall_col*8 + x
            sy = d_top + wall_row*8 + y
            pi = scr_px[sx, sy] if 0 <= sx < scr.width and 0 <= sy < scr.height else 0
            rgb = jz_rgb(pi)
            for name, val in list(PALETTE.items()) + [(f"pas{k}",v) for k,v in PASTEL_PALETTE.items()]:
                if val == rgb:
                    line += f"{str(name):6s} "
                    break
            else:
                line += f"??     "
        print(f"  {line}")
