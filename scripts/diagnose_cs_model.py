#!/usr/bin/env python3
"""
Comprehensive Color Stack diagnostic for Swords & Serpents.
Determines the correct CS values and advance model from the jzIntv screenshot.
"""

import sys
sys.path.insert(0, '.')
from render_all_rooms import (
    load_grom, parse_backtab, extract_backtab_from_output,
    extract_memory_section, parse_mobs,
    PALETTE, PASTEL_PALETTE,
)
from PIL import Image

def cn(rgb):
    """Human-readable color name."""
    for d, lbl in [(PALETTE, 'PAL'), (PASTEL_PALETTE, 'PAS')]:
        for k, v in d.items():
            if v == rgb:
                return f'{lbl}[{k}]'
    if rgb == (0, 0, 0):
        return 'BLACK'
    return f'RGB({rgb[0]},{rgb[1]},{rgb[2]})'


def jz_rgb(jz_pal, idx):
    if idx * 3 + 2 < len(jz_pal):
        return (jz_pal[idx * 3], jz_pal[idx * 3 + 1], jz_pal[idx * 3 + 2])
    return (0, 0, 0)


# Load data
with open('traces/_cmp_room_0_out.txt', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
grid = parse_backtab(extract_backtab_from_output(content))
grom = load_grom()

scr = Image.open('sprites/room_0_jzintv.gif')
scr_w, scr_h = scr.size
jz_pal = scr.getpalette()
jz_px = scr.load()

JLEFT, JTOP = 80, 52
TILE = 8


def get_tile_pixels(row, col):
    """Get all 64 pixels for a tile as list of (r,g,b)."""
    pixels = []
    tx = JLEFT + col * TILE
    ty = JTOP + row * TILE
    for y in range(ty, ty + TILE):
        for x in range(tx, tx + TILE):
            idx = jz_px[x, y]
            pixels.append(jz_rgb(jz_pal, idx))
    return pixels


def dominant_color(pixels):
    """Most common color ignoring black (FG=0 pixels)."""
    from collections import Counter
    counts = Counter(pixels)
    # Ignore pure black as it's likely FG=1 pixels with FG=0 (which renders black)
    for c in list(counts.keys()):
        if c[0] == 0 and c[1] == 0 and c[2] == 0:
            del counts[c]
    if not counts:
        return (0, 0, 0)
    return counts.most_common(1)[0][0]


def is_floor_tile(word):
    """Floor tile is GROM card 3 with no GRAM flag."""
    return (word & 0x08FF) == 0x0003  # card 3, no GRAM, no b13/b12


print("=" * 70)
print("  DIAGNOSTIC: Extracting CS colors from floor tiles")
print("=" * 70)

# Step 1: Extract the actual CS background color from every floor tile
# Since floor tiles have FG=0 (transparent), ALL pixels show CS background
print("\n=== Floor tile background colors (from jzIntv screenshot) ===")

cs_colors_by_position = {}  # (row, col) -> bg color
floor_positions = []

for row in range(12):
    for col in range(20):
        w = grid[row][col]
        if is_floor_tile(w):
            px = get_tile_pixels(row, col)
            dom = dominant_color(px)
            cs_colors_by_position[(row, col)] = dom
            floor_positions.append((row, col))

# Show a grid of floor tile background colors
print(f"\n  Background color for each floor tile position (by col):")
for row in range(12):
    line = f"  Row {row:2d}: "
    for col in range(20):
        if (row, col) in cs_colors_by_position:
            c = cs_colors_by_position[(row, col)]
            line += f"{cn(c):>8s} "
        else:
            line += "  ----   "
    print(line)


# Step 2: Test all CS advance models
print("\n" + "=" * 70)
print("  TESTING CS ADVANCE MODELS")
print("=" * 70)

# Collect unique CS colors that appear on floor tiles
unique_bg_colors = set(cs_colors_by_position.values())
print(f"\n  Unique background colors on floor tiles: {len(unique_bg_colors)}")
for c in sorted(unique_bg_colors):
    print(f"    {cn(c)} = RGB({c[0]},{c[1]},{c[2]})")


# Step 3: For each row, determine the repeating pattern of background colors
print("\n=== Per-row CS advance pattern analysis ===")

for row in range(12):
    cols_in_row = [col for r, col in floor_positions if r == row]
    if not cols_in_row:
        continue
    
    # Get the actual CS advance values from BACKTAB bits 0-2 for floor tiles
    advances = []
    for col in range(20):
        w = grid[row][col]
        if is_floor_tile(w):
            advances.append(w & 0x7)
    
    # Get the actual background colors for floor tiles in this row
    actual_colors = []
    for col in cols_in_row:
        actual_colors.append(cs_colors_by_position[(row, col)])
    
    print(f"\n  Row {row}:")
    print(f"    Position colors: {' → '.join(cn(c) for c in actual_colors)}")
    print(f"    BACKTAB advances: {advances}")
    
    # Test model: advance by bits 0-2 AFTER rendering, CS resets at row start
    # Try to find the CS values that work
    
    # Model 1: advance AFTER rendering, CS resets each row
    # If advance=3 every tile and CS=[A,B,C,D]:
    #   col0: A, col1: D, col2: C, col3: B, col4: A, ...
    
    # Model 2: advance BEFORE rendering 
    #   col0: A, col1: D, col2: C, ...
    
    # Both give same assignment just shifted
    
    # The pattern is 4-tile repeating: pos 0, pos 3, pos 2, pos 1, pos 0, ...
    # (with advance 3, modulo 4)
    
    # For advance=3, every floor tile in a row should show one of 4 colors
    # in the repeating pattern CS[0], CS[3], CS[2], CS[1], CS[0], ...
    
    # Verify: at col positions: 0→CS[0], 1→CS[3], 2→CS[2], 3→CS[1], 4→CS[0], ...
    # This maps col%4 to CS index:
    #   col%4=0 → CS[0]
    #   col%4=1 → CS[3]
    #   col%4=2 → CS[2]
    #   col%4=3 → CS[1]
    
    expected_map_adv3 = {0: 0, 1: 3, 2: 2, 3: 1}
    
    for col in cols_in_row:
        cs_idx = expected_map_adv3[col % 4]
        actual = cs_colors_by_position[(row, col)]
        print(f"    Col {col:2d}: CS[{cs_idx}] = {cn(actual)}")


# Step 4: Determine the 4 CS values from ALL rows
print("\n" + "=" * 70)
print("  DETERMINING CS REGISTER VALUES")
print("=" * 70)

# Group by expected CS index based on advance=3 model
cs_index_colors = {0: [], 1: [], 2: [], 3: []}

for row in range(12):
    for col in range(20):
        w = grid[row][col]
        if is_floor_tile(w):
            actual = cs_colors_by_position[(row, col)]
            cs_idx = (col * 3) % 4  # advance 3 per tile from col 0, AFTER rendering
            # Actually: starting at CS[0], advancing 3 per tile
            # After col 0: pointer goes from 0→3
            # After col 1: pointer goes from 3→2
            # After col 2: pointer goes from 2→1
            # After col 3: pointer goes from 1→0
            # So:
            # col 0 uses CS[0]
            # col 1 uses CS[3]
            # col 2 uses CS[2]
            # col 3 uses CS[1]
            idx = (0 - 3 * col) % 4
            # col 0: (0-0)%4=0 ✓
            # col 1: (0-3)%4=1... but should be CS[3]
            # Let me compute the other way
            # After n advances of 3: pointer = (0 + 3*n) % 4
            # Tile at col n uses CS[pointer_before_advance] = CS[(3*(n-1))%4]
            # Hmm, let me just map empirically:
            # col 0 → CS[0], col 1 → CS[3], col 2 → CS[2], col 3 → CS[1]
            cs_idx = {0: 0, 1: 3, 2: 2, 3: 1}[col % 4]
            cs_index_colors[cs_idx].append(actual)

print("\n  Inferred CS register colors:")
for idx in range(4):
    colors = cs_index_colors[idx]
    if colors:
        from collections import Counter
        c = Counter(colors).most_common(1)[0][0]
        print(f"    CS[{idx}] = {cn(c)} = RGB({c[0]},{c[1]},{c[2]})  (from {len(colors)} samples)")
    else:
        print(f"    CS[{idx}] = ??? (no floor tiles at this position)")


# Step 5: Get definitive CS values and test the full model
print("\n" + "=" * 70)
print("  TESTING FULL CS MODEL")
print("=" * 70)

# CS values inferred from floor tiles
inferred_cs = {}
for idx in range(4):
    colors = cs_index_colors[idx]
    if colors:
        from collections import Counter
        inferred_cs[idx] = Counter(colors).most_common(1)[0][0]
    else:
        inferred_cs[idx] = (0, 0, 0)

cs_values = [inferred_cs[0], inferred_cs[1], inferred_cs[2], inferred_cs[3]]

print(f"\n  Using CS = [{cn(cs_values[0])}, {cn(cs_values[1])}, {cn(cs_values[2])}, {cn(cs_values[3])}]")
print(f"  CS = [RGB({cs_values[0][0]},{cs_values[0][1]},{cs_values[0][2]}),")
print(f"        RGB({cs_values[1][0]},{cs_values[1][1]},{cs_values[1][2]}),")
print(f"        RGB({cs_values[2][0]},{cs_values[2][1]},{cs_values[2][2]}),")
print(f"        RGB({cs_values[3][0]},{cs_values[3][1]},{cs_values[3][2]})]")

# Test all tiles with this CS model
total_pixels = 0
matching_pixels = 0

for row in range(12):
    cs_index = 0  # reset at start of each row
    for col in range(20):
        w = grid[row][col]
        card_idx = w & 0x7FF
        is_gram = bool(w & 0x0800)
        # FG color: bits 15,14,12 for standard CS mode
        fg_color = ((w >> 13) & 0x6) | ((w >> 12) & 0x1)
        fg_transparent = (fg_color == 0)
        
        # CS advance: bits 0-2
        advance = w & 0x7
        
        # Get card bytes
        if is_gram:
            # Skip GRAM tiles for now (need GRAM memory dump)
            cs_index = (cs_index + advance) % 4
            continue
        else:
            card_bytes = load_grom()[card_idx * 8 : card_idx * 8 + 8]
        
        bg = cs_values[cs_index % 4]
        
        # Get actual screenshot pixels
        actual_px = get_tile_pixels(row, col)
        
        # Render our prediction
        px_idx = 0
        for cy in range(8):
            b = card_bytes[cy]
            for cx in range(8):
                bit = (b >> (7 - cx)) & 1
                actual = actual_px[px_idx]
                
                if fg_transparent or bit == 0:
                    predicted = bg
                else:
                    # FG color
                    if fg_color == 0:
                        predicted = (0, 0, 0)  # FG=0 is black
                    else:
                        predicted = PALETTE.get(fg_color, (0, 0, 0))
                
                total_pixels += 1
                if actual == predicted:
                    matching_pixels += 1
                
                px_idx += 1
        
        # Advance CS after rendering
        cs_index = (cs_index + advance) % 4

pct = 100.0 * matching_pixels / total_pixels if total_pixels else 0
print(f"\n  GROM tiles accuracy: {matching_pixels}/{total_pixels} = {pct:.1f}%")


# Step 6: Also test uniform CS (same value in all 4 registers)
print("\n=== Testing uniform CS (all same value) ===")

# Try all 16 color combinations
best_uniform = (None, 0)
for color_idx in range(16):
    if color_idx < 8:
        cs_color = PALETTE[color_idx]
    else:
        cs_color = PASTEL_PALETTE[color_idx - 8]
    
    uniform_cs = [cs_color] * 4
    matches = 0
    total = 0
    
    for row in range(12):
        cs_index = 0
        for col in range(20):
            w = grid[row][col]
            card_idx = w & 0x7FF
            is_gram = bool(w & 0x0800)
            fg_color = ((w >> 13) & 0x6) | ((w >> 12) & 0x1)
            fg_transparent = (fg_color == 0)
            advance = w & 0x7
            
            if is_gram:
                cs_index = (cs_index + advance) % 4
                continue
            
            card_bytes = load_grom()[card_idx * 8 : card_idx * 8 + 8]
            bg = uniform_cs[cs_index % 4]
            actual_px = get_tile_pixels(row, col)
            
            px_idx = 0
            for cy in range(8):
                b = card_bytes[cy]
                for cx in range(8):
                    bit = (b >> (7 - cx)) & 1
                    actual = actual_px[px_idx]
                    
                    if fg_transparent or bit == 0:
                        predicted = bg
                    else:
                        if fg_color == 0:
                            predicted = (0, 0, 0)
                        else:
                            predicted = PALETTE.get(fg_color, (0, 0, 0))
                    
                    total += 1
                    if actual == predicted:
                        matches += 1
                    px_idx += 1
            
            cs_index = (cs_index + advance) % 4
    
    pct = 100.0 * matches / total if total else 0
    if pct > best_uniform[1]:
        best_uniform = (cn(cs_color), pct)

print(f"  Best uniform CS: {best_uniform[0]} at {best_uniform[1]:.1f}%")


# Step 7: Brute force ALL 16^4 = 65536 CS combinations (primary only)
print("\n=== Brute-force ALL primary CS combinations ===")

best_combo = (None, 0)

# We only test primary palette (0-7) for speed
# 8^4 = 4096 combinations, manageable
for cs0 in range(8):
    for cs1 in range(8):
        for cs2 in range(8):
            for cs3 in range(8):
                cs = [PALETTE[cs0], PALETTE[cs1], PALETTE[cs2], PALETTE[cs3]]
                matches = 0
                total = 0
                
                for row in range(12):
                    cs_index = 0
                    for col in range(20):
                        w = grid[row][col]
                        card_idx = w & 0x7FF
                        is_gram = bool(w & 0x0800)
                        fg_color = ((w >> 13) & 0x6) | ((w >> 12) & 0x1)
                        fg_transparent = (fg_color == 0)
                        advance = w & 0x7
                        
                        if is_gram:
                            cs_index = (cs_index + advance) % 4
                            continue
                        
                        card_bytes = load_grom()[card_idx * 8 : card_idx * 8 + 8]
                        bg = cs[cs_index % 4]
                        actual_px = get_tile_pixels(row, col)
                        
                        px_idx = 0
                        for cy in range(8):
                            b = card_bytes[cy]
                            for cx in range(8):
                                bit = (b >> (7 - cx)) & 1
                                actual = actual_px[px_idx]
                                
                                if fg_transparent or bit == 0:
                                    predicted = bg
                                else:
                                    if fg_color == 0:
                                        predicted = (0, 0, 0)
                                    else:
                                        predicted = PALETTE.get(fg_color, (0, 0, 0))
                                
                                total += 1
                                if actual == predicted:
                                    matches += 1
                                px_idx += 1
                        
                        cs_index = (cs_index + advance) % 4
                
                pct = 100.0 * matches / total if total else 0
                if pct > best_combo[1]:
                    best_combo = (f"CS=[PAL[{cs0}],PAL[{cs1}],PAL[{cs2}],PAL[{cs3}]]", pct)

print(f"  Best primary CS: {best_combo[0]} at {best_combo[1]:.1f}%")


print("\n" + "=" * 70)
print("  DONE")
print("=" * 70)
