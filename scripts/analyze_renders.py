#!/usr/bin/env python3
"""Deep pixel analysis of all 6 rendered dungeon rooms."""
import sys, os
sys.path.insert(0, '.')
from render_all_rooms import (
    extract_backtab_from_output, parse_backtab, decode_backtab_word,
    PALETTE, extract_memory_section, parse_mobs
)
from PIL import Image

print("=" * 70)
print("ROOM TILE & MOB ANALYSIS")
print("=" * 70)

for room in range(6):
    capture_path = f'traces/render_room_{room}_out.txt'
    image_path = f'sprites/dungeon_room_{room}.png'
    
    if not os.path.exists(capture_path):
        print(f"\nRoom {room}: NO CAPTURE FILE")
        continue
    
    with open(capture_path, 'r', errors='replace') as f:
        output = f.read()
    
    # BACKTAB analysis
    backtab_text = extract_backtab_from_output(output)
    backtab = parse_backtab(backtab_text) if backtab_text else []
    
    tile_counts = {}
    non_floor = []
    for row in range(len(backtab)):
        for col in range(len(backtab[row]) if backtab else 0):
            word = backtab[row][col]
            card, fg, bg_adv, is_gram, _ = decode_backtab_word(word)
            gram_label = "GRAM" if is_gram else "GROM"
            key = f"{gram_label}:{card}:fg{fg}"
            tile_counts[key] = tile_counts.get(key, 0) + 1
            if card != 0 or fg != 7:
                non_floor.append((row, col, card, fg, is_gram))
    
    # MOBs
    sysram_text = extract_memory_section(output, 0x0300, 0x0360)
    mobs = parse_mobs(sysram_text) if sysram_text else []
    
    print(f"\n{'='*70}")
    print(f"ROOM {room}")
    print(f"{'='*70}")
    print(f"  Backtab: {len(backtab)} rows x {len(backtab[0]) if backtab else 0} cols")
    print(f"  Unique tile types: {len(tile_counts)}")
    for t, n in sorted(tile_counts.items(), key=lambda x: -x[1])[:12]:
        print(f"    {t}: {n}x")
    print(f"  Non-floor tiles ({len(non_floor)}):")
    for r, c, card, fg, is_gram in non_floor[:20]:
        gram_label = "GRAM" if is_gram else "GROM"
        color_name = {0:"BLK",1:"BLU",2:"RED",3:"TAN",4:"DKGRN",5:"GRN",6:"YEL",7:"WHT"}.get(fg, str(fg))
        print(f"    [{r:2d},{c:2d}] card={card:3d} ({gram_label}) fg={fg} ({color_name})")
    print(f"  MOBs: {len(mobs)}")
    for m in mobs:
        w = 16 if m['xsize'] else 8
        h = 16 if m['ysize'] else 8
        behind = 'BEHIND' if m['behind'] else 'FRONT'
        print(f"    MOB{m['mob_idx']}: ({m['x']},{m['y']}) {w}x{h} card={m['card']} {'GRAM' if m['is_gram'] else 'GROM'} {behind}")
    
    # Image pixel analysis
    if os.path.exists(image_path):
        img = Image.open(image_path)
        px = img.load()
        colors = {}
        for y in range(img.height):
            for x in range(img.width):
                c = px[x, y]
                colors[c] = colors.get(c, 0) + 1
        sorted_colors = sorted(colors.items(), key=lambda x: -x[1])
        print(f"  Image: {img.size[0]}x{img.size[1]}px, {len(colors)} unique colors")
        for c, n in sorted_colors[:8]:
            label = ""
            if c == (200, 170, 100): label = " (TAN-walls)"
            elif c == (0, 45, 200): label = " (BLU-accents)"
            elif c == (0, 0, 0): label = " (BLK-ceiling)"
            elif c == (127, 127, 127): label = " (PASTEL-MOB)"
            elif c == (200, 0, 20): label = " (RED)"
            elif c == (255, 255, 255): label = " (WHT)"
            elif c == (230, 215, 70): label = " (YEL)"
            elif c == (0, 140, 40): label = " (GRN)"
            print(f"    {c}: {n:6d} px{label}")
    else:
        print(f"  Image: MISSING at {image_path}")

print(f"\n{'='*70}")
print("COMPLETE")
print(f"{'='*70}")
