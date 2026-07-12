#!/usr/bin/env python3
"""Pixel-compare each unique BACKTAB word type against jzIntv room 0 to find which words cause the PAS[3]↔PAL[1] swap."""

import sys, os, re
sys.path.insert(0, '.')
from render_all_rooms import (
    load_grom, get_grom_card_bytes, parse_backtab, extract_backtab_from_output,
    extract_gram_from_output, parse_memory_dump, decode_backtab_word,
    render_gram_card_with_bitmap, render_grom_card_with_bitmap,
    PALETTE, PASTEL_PALETTE, DEFAULT_BG,
)
from PIL import Image
from collections import defaultdict

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

def jz_rgb(idx):
    if idx * 3 + 2 < len(jz_pal):
        return (jz_pal[idx*3], jz_pal[idx*3+1], jz_pal[idx*3+2])
    return (0, 0, 0)

# Find dungeon bounds
left = top = None
for x in range(scr.width):
    for y in range(scr.height):
        if jz_px[x, y] != 0:
            left = x; break
    if left is not None: break
for y in range(scr.height):
    for x in range(scr.width):
        if jz_px[x, y] != 0:
            top = y; break
    if top is not None: break
if left is None or top is None:
    left, top = 80, 52

def color_name(rgb):
    for d, label in [(PALETTE, "PAL"), (PASTEL_PALETTE, "PAS")]:
        for k, v in d.items():
            if v == rgb:
                return f"{label}[{k}]"
    if rgb == (0, 0, 0): return "black"
    return str(rgb)

# Use our current renderer (with FG=0 transparent) at native resolution
color_stack = [PASTEL_PALETTE[3]] * 4
cs_index = 0

# For each tile position, render it and compare to jzIntv
word_stats = defaultdict(lambda: {
    'count': 0, 'match': 0, 'total_px': 0,
    'our_pt_jz_blue': 0,  # we show pastel tan, jz shows blue (PAS[3]->PAL[1])
    'our_blue_jz_pt': 0,  # we show blue, jz shows pastel tan (PAL[1]->PAS[3])
    'our_black_jz_pt': 0,
    'our_pt_jz_white': 0,
    'our_pt_jz_ptan': 0,
    'our_blue_jz_blue': 0,
    'our_pt_jz_pt': 0,
    'other_mismatch': 0,
})

print("Rendering all tiles at native resolution and comparing to jzIntv...")
print()

for row in range(12):
    for col in range(20):
        word = grid[row][col]
        card_idx, fg_color_idx, bg_bits, is_gram, fg_transparent = decode_backtab_word(word)
        
        # CS advance
        advance = (word >> 13) & 1
        cs_index = (cs_index + advance) % 4
        bg = color_stack[cs_index]
        
        # Render this single tile
        if is_gram:
            card_img, card_bitmap = render_gram_card_with_bitmap(gram_mem, card_idx, fg_color_idx, bg)
        else:
            card_img, card_bitmap = render_grom_card_with_bitmap(grom, card_idx, fg_color_idx, bg)
        
        stats = word_stats[word]
        stats['count'] += 1
        
        for y in range(8):
            for x in range(8):
                r, g, b = card_img.getpixel((x, y))
                is_bg = card_bitmap[y][x]
                
                if is_bg or fg_transparent:
                    our_rgb = bg
                else:
                    our_rgb = (r, g, b)
                
                sx = left + col*8 + x
                sy = top + row*8 + y
                if 0 <= sx < scr.width and 0 <= sy < scr.height:
                    jz_rgb_val = jz_rgb(jz_px[sx, sy])
                else:
                    jz_rgb_val = (0, 0, 0)
                
                stats['total_px'] += 1
                
                if our_rgb == jz_rgb_val:
                    stats['match'] += 1
                elif our_rgb == PASTEL_PALETTE[3] and jz_rgb_val == PALETTE[1]:
                    stats['our_pt_jz_blue'] += 1
                elif our_rgb == PALETTE[1] and jz_rgb_val == PASTEL_PALETTE[3]:
                    stats['our_blue_jz_pt'] += 1
                elif our_rgb == (0,0,0) and jz_rgb_val == PASTEL_PALETTE[3]:
                    stats['our_black_jz_pt'] += 1
                elif our_rgb == PASTEL_PALETTE[3] and jz_rgb_val == PALETTE[7]:
                    stats['our_pt_jz_white'] += 1
                elif our_rgb == PASTEL_PALETTE[3] and jz_rgb_val == PALETTE[3]:
                    stats['our_pt_jz_ptan'] += 1
                elif our_rgb == PALETTE[1] and jz_rgb_val == PALETTE[1]:
                    stats['our_blue_jz_blue'] += 1
                elif our_rgb == PASTEL_PALETTE[3] and jz_rgb_val == PASTEL_PALETTE[3]:
                    stats['our_pt_jz_pt'] += 1
                else:
                    stats['other_mismatch'] += 1

# Show results per word
print(f"{'Word':>6} {'Tiles':>5} {'GRAM':>5} {'Card':>5} {'FG':>3} {'Trans':>5} {'Match%':>7} {'PT->Blue':>10} {'Blue->PT':>10} {'PT->White':>11} {'PT->PTan':>11} {'Other':>7}")
print("-" * 100)

for word in sorted(word_stats.keys()):
    s = word_stats[word]
    card, fg, bg_bits, is_gram, fg_transparent = decode_backtab_word(word)
    pct = 100.0 * s['match'] / s['total_px'] if s['total_px'] > 0 else 0
    
    if s['our_pt_jz_blue'] > 0 or s['our_blue_jz_pt'] > 0:
        marker = " <- MIX"
    elif s['match'] == s['total_px']:
        marker = " PERFECT"
    else:
        marker = ""
    
    print(f"0x{word:04X} {s['count']:5d} {'Y' if is_gram else 'N':>5} {card:5d} {fg:3d} {'Y' if fg_transparent else 'N':>5} {pct:6.1f}% {s['our_pt_jz_blue']:9d} {s['our_blue_jz_pt']:9d} {s['our_pt_jz_white']:10d} {s['our_pt_jz_ptan']:9d} {s['other_mismatch']:7d}{marker}")

print()
print("=== Summary ===")
total_pt_blue = sum(s['our_pt_jz_blue'] for s in word_stats.values())
total_blue_pt = sum(s['our_blue_jz_pt'] for s in word_stats.values())
total_pt_white = sum(s['our_pt_jz_white'] for s in word_stats.values())
total_pt_ptan = sum(s['our_pt_jz_ptan'] for s in word_stats.values())
total_match = sum(s['match'] for s in word_stats.values())
total_px = sum(s['total_px'] for s in word_stats.values())

print(f"Total pixels: {total_px}")
print(f"Total match: {total_match} ({100*total_match/total_px:.1f}%)")
print(f"PAS[3]->PAL[1] (our tan->jz blue): {total_pt_blue} px")
print(f"PAL[1]->PAS[3] (our blue->jz tan): {total_blue_pt} px")
print(f"PAS[3]->PAL[7] (our tan->jz white): {total_pt_white} px")
print(f"PAS[3]->PAL[3] (our tan->jz primary tan): {total_pt_ptan} px")

# For MIX words, show detailed pixel pattern
print("\n=== Detail for MIX words ===")
for word in sorted(word_stats.keys()):
    s = word_stats[word]
    if s['our_pt_jz_blue'] == 0 and s['our_blue_jz_pt'] == 0:
        continue
    
    card, fg, bg_bits, is_gram, fg_transparent = decode_backtab_word(word)
    print(f"\n--- Word 0x{word:04X} (card={card}, fg={fg}, gram={is_gram}, transparent={fg_transparent}) ---")
    print(f"  Tiles: {s['count']}, Match: {s['match']}/{s['total_px']} ({100*s['match']/s['total_px']:.1f}%)")
    print(f"  PT→Blue: {s['our_pt_jz_blue']}, Blue→PT: {s['our_blue_jz_pt']}, PT→White: {s['our_pt_jz_white']}, PT→PTan: {s['our_pt_jz_ptan']}")
    
    # Show the card data
    if is_gram:
        base = 0x3800 + (card & 0x3F) * 8
        print(f"  GRAM card {card & 0x3F}:")
        for i in range(8):
            b = gram_mem.get(base + i, 0) & 0xFF
            line = ''
            for bit in range(8):
                line += '#' if (b >> (7-bit)) & 1 else '.'
            print(f"    {b:02X} {line}")
    else:
        cbytes = get_grom_card_bytes(grom, card & 0xFF)
        print(f"  GROM card {card & 0xFF}:")
        for i in range(8):
            b = cbytes[i]
            line = ''
            for bit in range(8):
                line += '#' if (b >> (7-bit)) & 1 else '.'
            print(f"    {b:02X} {line}")
    
    # For the first tile of this word, compare pixel-by-pixel
    for row in range(12):
        for col in range(20):
            if grid[row][col] == word:
                print(f"\n  First tile at ({row},{col}): pixel comparison")
                print(f"  Legend: B=blue, T=pastel tan, W=white, t=primary tan, 0=black, .=match")
                
                our_lines = []
                jz_lines = []
                comp_lines = []
                
                for y in range(8):
                    our_line = ""
                    jz_line = ""
                    comp_line = ""
                    for x in range(8):
                        r, g, b = card_img.getpixel((x, y))
                        is_bg = card_bitmap[y][x]
                        
                        if is_bg or fg_transparent:
                            our_rgb = bg
                        else:
                            our_rgb = (r, g, b)
                        
                        sx = left + col*8 + x
                        sy = top + row*8 + y
                        jz_rgb_val = jz_rgb(jz_px[sx, sy]) if 0 <= sx < scr.width and 0 <= sy < scr.height else (0,0,0)
                        
                        # Map to short codes
                        if our_rgb == PALETTE[1]: our_ch = 'B'
                        elif our_rgb == PASTEL_PALETTE[3]: our_ch = 'T'
                        elif our_rgb == PALETTE[7]: our_ch = 'W'
                        elif our_rgb == PALETTE[3]: our_ch = 't'
                        elif our_rgb == (0,0,0): our_ch = '0'
                        else: our_ch = '?'
                        
                        if jz_rgb_val == PALETTE[1]: jz_ch = 'B'
                        elif jz_rgb_val == PASTEL_PALETTE[3]: jz_ch = 'T'
                        elif jz_rgb_val == PALETTE[7]: jz_ch = 'W'
                        elif jz_rgb_val == PALETTE[3]: jz_ch = 't'
                        elif jz_rgb_val == (0,0,0): jz_ch = '0'
                        else: jz_ch = '?'
                        
                        our_line += our_ch
                        jz_line += jz_ch
                        comp_line += '.' if our_rgb == jz_rgb_val else '!'
                    
                    our_lines.append(our_line)
                    jz_lines.append(jz_line)
                    comp_lines.append(comp_line)
                
                print("    Our:   " + "  ".join(our_lines[:4]))
                if len(our_lines) > 4:
                    print("    Our:   " + "  ".join(our_lines[4:]))
                print("    jzIntv:" + "  ".join(jz_lines[:4]))
                if len(jz_lines) > 4:
                    print("    jzIntv:" + "  ".join(jz_lines[4:]))
                print("    Diff:  " + "  ".join(comp_lines[:4]))
                if len(comp_lines) > 4:
                    print("    Diff:  " + "  ".join(comp_lines[4:]))
                
                break
        break

print()
print("Done.")
