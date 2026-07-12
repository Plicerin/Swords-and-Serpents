#!/usr/bin/env python3
"""
Validate the TypeScript renderer output against authoritative PNGs.

Renders rooms using the same logic as src/platform/stic.ts and compares
to room_{N}_authoritative.png.
"""

import json
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("PIL not found. Install with: pip install Pillow")
    sys.exit(1)

# 16-color Intellivision palette (must match src/platform/stic.ts)
PALETTE = [
    (0x00, 0x00, 0x00),  # 0  black
    (0x00, 0x2D, 0xFF),  # 1  blue
    (0xFF, 0x3D, 0x10),  # 2  red
    (0xC9, 0xCF, 0xAB),  # 3  tan
    (0x38, 0x6B, 0x3F),  # 4  dark green
    (0x00, 0xA7, 0x56),  # 5  green
    (0xFA, 0xEA, 0x50),  # 6  yellow
    (0xFF, 0xFC, 0xFF),  # 7  white
    (0xBD, 0xAC, 0xC8),  # 8  grey
    (0x24, 0xB8, 0xFF),  # 9  cyan
    (0xFF, 0xB4, 0x1F),  # 10 orange
    (0x54, 0x6E, 0x00),  # 11 brown / olive (floor)
    (0xFF, 0x4E, 0x57),  # 12 pink
    (0xA4, 0x96, 0xFF),  # 13 light blue
    (0x75, 0xCC, 0x80),  # 14 yellow-green
    (0xB5, 0x1A, 0x58),  # 15 purple
]

COLS, ROWS, TS = 20, 12, 8
WIDTH, HEIGHT = COLS * TS, ROWS * TS  # 160x96


def decode_fgbg_word(word):
    """Decode BACKTAB word in FG/BG mode (matches stic.ts)."""
    gr_idx = word & 0x9F8
    card = (gr_idx >> 3) & 0x3F
    is_gram = (gr_idx & 0x800) != 0
    fg = word & 0x7
    bg = ((word >> 9) & 0xB) | ((word >> 11) & 0x4)
    return card, is_gram, fg, bg


def render_room(backtab, gram, grom):
    """Render room to PIL Image at native 160x96."""
    img = Image.new('RGB', (WIDTH, HEIGHT))
    px = img.load()
    
    for row in range(ROWS):
        for col in range(COLS):
            word = backtab[row * COLS + col]
            card, is_gram, fg, bg = decode_fgbg_word(word)
            
            card_base = card * 8
            card_bytes = gram[card_base:card_base + 8] if is_gram else grom[card_base:card_base + 8]
            
            fg_color = PALETTE[fg & 0xF]
            bg_color = PALETTE[bg & 0xF]
            
            x0, y0 = col * TS, row * TS
            for y in range(TS):
                byte = card_bytes[y] if y < len(card_bytes) else 0
                for x in range(TS):
                    bit = (byte >> (7 - x)) & 1
                    px[x0 + x, y0 + y] = fg_color if bit else bg_color
    
    return img


def compare_images(img1, img2):
    """Compare two images, return (match_ratio, diff_count, total_pixels)."""
    if img1.size != img2.size:
        return 0.0, -1, -1
    
    px1 = img1.load()
    px2 = img2.load()
    w, h = img1.size
    total = w * h
    diff = 0
    
    for y in range(h):
        for x in range(w):
            if px1[x, y] != px2[x, y]:
                diff += 1
    
    return (total - diff) / total, diff, total


def main():
    root = Path(__file__).parent.parent
    assets = root / 'assets'
    
    # Load assets
    with open(assets / 'gram_tiles.json') as f:
        gram = bytes(json.load(f))
    
    with open(assets / 'grom.bin', 'rb') as f:
        grom = f.read()
    
    with open(assets / 'rooms.json') as f:
        rooms = json.load(f)['rooms']
    
    print(f"Loaded {len(rooms)} rooms, GRAM: {len(gram)} bytes, GROM: {len(grom)} bytes\n")
    
    all_pass = True
    
    for i, backtab in enumerate(rooms):
        auth_path = root / f'room_{i}_authoritative.png'
        if not auth_path.exists():
            print(f"Room {i}: SKIP (no authoritative PNG)")
            continue
        
        # Render our version
        rendered = render_room(backtab, gram, grom)
        
        # Load authoritative (may be scaled with aspect correction)
        auth = Image.open(auth_path).convert('RGB')
        
        # Authoritative PNGs are 640x480 (4x scale, 1.25x aspect)
        # Downscale to 160x96 for comparison
        if auth.size != (WIDTH, HEIGHT):
            auth_downscaled = auth.resize((WIDTH, HEIGHT), Image.NEAREST)
        else:
            auth_downscaled = auth
        
        ratio, diff, total = compare_images(rendered, auth_downscaled)
        
        if ratio == 1.0:
            print(f"Room {i}: PASS (100% match)")
        else:
            print(f"Room {i}: DIFF ({ratio*100:.2f}% match, {diff}/{total} pixels differ)")
            # Save diff for inspection
            rendered.save(root / f'room_{i}_rendered.png')
            all_pass = False
    
    print()
    if all_pass:
        print("PASS: All rooms match authoritative PNGs!")
        return 0
    else:
        print("FAIL: Some rooms have differences. Check room_N_rendered.png files.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
