#!/usr/bin/env python3
"""Test each proposed rendering fix independently and measure impact."""

import sys, os
sys.path.insert(0, '.')
from render_all_rooms import (
    extract_backtab_from_output, parse_backtab, decode_backtab_word,
    extract_gram_from_output, parse_memory_dump,
    extract_memory_section, parse_mobs,
    render_room_image, load_grom,
    render_grom_card_with_bitmap, render_gram_card_with_bitmap,
    PALETTE, PASTEL_PALETTE
)
from PIL import Image

# ---------------------------------------------------------------------------
# Candidate fix: render_room_image but with corrected decode
# ---------------------------------------------------------------------------

def decode_fixed_bug1(word):
    """Fix 1: Card = bits 0-10 (word & 0x7FF)"""
    card = word & 0x7FF
    is_gram = bool(word & 0x0800)
    fg = (word >> 12) & 0x7
    bg_bits = word & 0x7  # unchanged
    return card, fg, bg_bits, is_gram

def decode_fixed_bug2(word):
    """Fix 2: FG = bits 9-12 (word >> 9) & 0xF"""
    card = (word >> 3) & 0xFF
    is_gram = bool(word & 0x0800)
    fg = (word >> 9) & 0xF
    bg_bits = word & 0x7
    return card, fg, bg_bits, is_gram

def decode_fixed_bug1_2(word):
    """Fix 1+2: Card = bits 0-10, FG = bits 9-12"""
    card = word & 0x7FF
    is_gram = bool(word & 0x0800)
    fg = (word >> 9) & 0xF
    bg_bits = word & 0x7
    return card, fg, bg_bits, is_gram

def make_fg_lookup(palette_dict, pastel_dict):
    """Fix 3: FG colors 0-15 map to PALETTE[0-7] and PASTEL_PALETTE[8-15]"""
    lut = {}
    for i in range(8):
        lut[i] = palette_dict.get(i, (255,0,255))
    for i in range(8, 16):
        lut[i] = pastel_dict.get(i - 8, (255,0,255))
    return lut

def render_card_1bpp_fixed(card_data, fg_color_idx, bg_color, fg_lut):
    """Fixed card renderer using fg_lut for 0-15 colors."""
    img = Image.new('RGB', (8, 8), bg_color)
    for row in range(min(8, len(card_data))):
        byte_val = card_data[row]
        for col in range(8):
            if byte_val & (0x80 >> col):
                img.putpixel((col, row), fg_lut.get(fg_color_idx, bg_color))
    return img

def cs_advance_fixed(word):
    """Fix 4: CS advance = bit 13 (0 or 1), not bits 0-2 (0-7)"""
    return (word >> 13) & 1

# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

def load_room_data():
    with open('traces/_cmp_room_0_out.txt', 'r', errors='replace') as f:
        output = f.read()
    backtab_grid = parse_backtab(extract_backtab_from_output(output))
    gram_mem = parse_memory_dump(extract_gram_from_output(output), 0x3800, 512)
    sysram_text = extract_memory_section(output, 0x0300, 0x0360)
    mobs = parse_mobs(sysram_text) if sysram_text else []
    grom = load_grom()
    return backtab_grid, gram_mem, grom, mobs

def load_jzintv():
    scr_path = 'sprites/room_0_jzintv.gif'
    jz_full = Image.open(scr_path)
    jz_pal = jz_full.getpalette()
    scr_px = jz_full.load()
    left = None
    for x in range(jz_full.width):
        for y in range(jz_full.height):
            if scr_px[x, y] != 0:
                left = x; break
        if left is not None: break
    top = None
    for y in range(jz_full.height):
        for x in range(jz_full.width):
            if scr_px[x, y] != 0:
                top = y; break
        if top is not None: break
    if left is None or top is None:
        left, top = 80, 52
    crop_w = min(160, jz_full.width - left)
    crop_h = min(96, jz_full.height - top)
    jz_dungeon = jz_full.crop((left, top, left + crop_w, top + crop_h))
    return jz_dungeon, jz_pal

def jz_rgb(jz_pal, idx):
    if jz_pal and idx * 3 + 2 < len(jz_pal):
        return (jz_pal[idx * 3], jz_pal[idx * 3 + 1], jz_pal[idx * 3 + 2])
    return (0, 0, 0)

def compare(img_4x, jz_dungeon, jz_pal):
    native = Image.new('RGB', (160, 96))
    for y in range(96):
        for x in range(160):
            native.putpixel((x, y), img_4x.getpixel((x * 4, y * 4)))
    match = 0
    total = 0
    for y in range(min(96, jz_dungeon.height)):
        for x in range(min(160, jz_dungeon.width)):
            if native.getpixel((x, y)) == jz_rgb(jz_pal, jz_dungeon.getpixel((x, y))):
                match += 1
            total += 1
    return 100.0 * match / total if total > 0 else 0

# ---------------------------------------------------------------------------
# Custom render with specific fixes
# ---------------------------------------------------------------------------

PAS3 = PASTEL_PALETTE[3]

def render_with_decode(backtab_grid, gram_mem, grom, decode_fn, use_cs_advance_fix=False, use_fg_lut_fix=False):
    """Render a room using a custom BACKTAB decode function."""
    color_stack = [PAS3, PAS3, PAS3, PAS3]
    zoom = 4
    img = Image.new('RGB', (20 * 8 * zoom, 12 * 8 * zoom), (0, 0, 0))
    cs_index = 0
    fg_lut = make_fg_lookup(PALETTE, PASTEL_PALETTE) if use_fg_lut_fix else None

    for row in range(12):
        for col in range(20):
            word = backtab_grid[row][col]
            card, fg, bg_bits, is_gram = decode_fn(word)

            # CS advance
            if use_cs_advance_fix:
                advance = cs_advance_fixed(word)
            else:
                advance = bg_bits
            cs_index = (cs_index + advance) % 4
            bg_color = color_stack[cs_index]

            # Card data
            if is_gram:
                gram_addr = (card & 0x3F) * 8
                card_data = [gram_mem.get(0x3800 + gram_addr + r, 0) for r in range(8)]
            else:
                grom_addr = (card & 0xFF) * 8
                card_data = [grom[grom_addr + r] if grom_addr + r < len(grom) else 0 for r in range(8)]

            # Render card pixels
            base_x = col * 8
            base_y = row * 8
            for cr in range(8):
                if cr >= len(card_data):
                    break
                byte_val = card_data[cr]
                for cc in range(8):
                    is_bg = not (byte_val & (0x80 >> cc))
                    px = (base_x + cc, base_y + cr)
                    if is_bg:
                        # Use color stack background for the CURRENT tile (already advanced)
                        color = color_stack[cs_index]
                    else:
                        if use_fg_lut_fix:
                            color = fg_lut.get(fg, (255, 0, 255))
                        else:
                            color = PALETTE.get(fg & 0x7, (255, 0, 255))
                    # Scale up
                    for dy in range(zoom):
                        for dx in range(zoom):
                            img.putpixel((px[0] * zoom + dx, px[1] * zoom + dy), color)

    return img

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

backtab_grid, gram_mem, grom, mobs = load_room_data()
jz_dungeon, jz_pal = load_jzintv()

print("Room 0 - Testing Gemini-proposed fixes independently")
print("=" * 60)

# Baseline (current code)
baseline = render_room_image(backtab_grid, gram_mem, grom, color_stack=None, zoom=4, mobs=mobs)
base_pct = compare(baseline, jz_dungeon, jz_pal)
print(f"  Baseline (current code):     {base_pct:5.1f}%")

# Fix 1: Card = bits 0-10
img1 = render_with_decode(backtab_grid, gram_mem, grom, decode_fixed_bug1)
pct1 = compare(img1, jz_dungeon, jz_pal)
print(f"  Fix 1 (card=bits 0-10):      {pct1:5.1f}%  delta: {pct1-base_pct:+.1f}%")

# Fix 2: FG = bits 9-12
img2 = render_with_decode(backtab_grid, gram_mem, grom, decode_fixed_bug2)
pct2 = compare(img2, jz_dungeon, jz_pal)
print(f"  Fix 2 (fg=bits 9-12):        {pct2:5.1f}%  delta: {pct2-base_pct:+.1f}%")

# Fix 1+2 combined
img12 = render_with_decode(backtab_grid, gram_mem, grom, decode_fixed_bug1_2)
pct12 = compare(img12, jz_dungeon, jz_pal)
print(f"  Fix 1+2 (both card+fg):      {pct12:5.1f}%  delta: {pct12-base_pct:+.1f}%")

# Fix 3: FG LUT with pastel
img3 = render_with_decode(backtab_grid, gram_mem, grom, decode_backtab_word, use_fg_lut_fix=True)
pct3 = compare(img3, jz_dungeon, jz_pal)
print(f"  Fix 3 (fg LUT 0-15):         {pct3:5.1f}%  delta: {pct3-base_pct:+.1f}%")

# Fix 4: CS advance = bit 13
img4 = render_with_decode(backtab_grid, gram_mem, grom, decode_backtab_word, use_cs_advance_fix=True)
pct4 = compare(img4, jz_dungeon, jz_pal)
print(f"  Fix 4 (cs_advance=bit 13):   {pct4:5.1f}%  delta: {pct4-base_pct:+.1f}%")

# Fix 1+2+3+4 combined
img_all = render_with_decode(backtab_grid, gram_mem, grom, decode_fixed_bug1_2, use_cs_advance_fix=True, use_fg_lut_fix=True)
pct_all = compare(img_all, jz_dungeon, jz_pal)
print(f"  ALL FIXES combined:          {pct_all:5.1f}%  delta: {pct_all-base_pct:+.1f}%")

# Fix 3+4 (fg LUT + CS advance)
img34 = render_with_decode(backtab_grid, gram_mem, grom, decode_backtab_word, use_cs_advance_fix=True, use_fg_lut_fix=True)
pct34 = compare(img34, jz_dungeon, jz_pal)
print(f"  Fix 3+4 (fgLUT + cs_adv):    {pct34:5.1f}%  delta: {pct34-base_pct:+.1f}%")

print()
print("Summary: only apply fixes that show positive deltas")
