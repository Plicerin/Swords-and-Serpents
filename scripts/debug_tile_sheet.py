#!/usr/bin/env python3
"""Debug tile sheet — render every unique card used in rooms 0,1,2."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image
from render_all_rooms import (
    load_grom, get_grom_card_bytes,
    parse_memory_dump, parse_backtab,
    extract_backtab_from_output,
    decode_backtab_word,
    PALETTE, PASTEL_PALETTE, DEFAULT_BG,
)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _fg_color_for_index(fg_color_idx):
    if fg_color_idx >= 8:
        return PASTEL_PALETTE.get(fg_color_idx - 8, (255, 0, 255))
    return PALETTE.get(fg_color_idx, (255, 0, 255))

def render_tile(card_bytes, fg_color_idx, bg_color, zoom=8):
    fg = _fg_color_for_index(fg_color_idx)
    img = Image.new('RGB', (8 * zoom, 8 * zoom))
    px = img.load()
    for row in range(min(8, len(card_bytes))):
        byte_val = card_bytes[row]
        for col in range(8):
            bit = (byte_val >> (7 - col)) & 1
            rgb = bg_color if bit == 0 else fg
            for dy in range(zoom):
                for dx in range(zoom):
                    px[col * zoom + dx, row * zoom + dy] = rgb
    return img

def main():
    grom = load_grom()
    print(f"grom.bin size: {len(grom)} bytes ({len(grom)//8} cards)")

    # Load gram_boot.bin as the GRAM source
    gram_path = os.path.join(PROJECT_DIR, 'sprites', 'decoded_boot', 'gram_boot.bin')
    with open(gram_path, 'rb') as f:
        gram_data = f.read()
    print(f"gram_boot.bin size: {len(gram_data)} bytes ({len(gram_data)//8} cards)")

    # Collect unique (card, is_gram, fg) from rooms 0,1,2
    unique_tiles = set()
    for i in [0, 1, 2]:
        dump_path = os.path.join(PROJECT_DIR, 'traces', 'rooms', f'render_room_{i}_out.txt')
        with open(dump_path, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
        grid = parse_backtab(extract_backtab_from_output(text))
        for r in range(12):
            for c in range(20):
                word = grid[r][c]
                card, fg, _, is_gram, _ = decode_backtab_word(word)
                unique_tiles.add((card, is_gram, fg, word))

    print(f"\nUnique tiles across rooms 0,1,2: {len(unique_tiles)}")

    # Build a sprite sheet
    zoom = 16
    tile_size = 8 * zoom
    cols = 8
    rows = (len(unique_tiles) + cols - 1) // cols

    sheet = Image.new('RGB', (cols * (tile_size + 4) + 4, rows * (tile_size + 24) + 4), (20, 20, 20))
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except Exception:
        font = ImageFont.load_default()

    for idx, (card, is_gram, fg, word) in enumerate(sorted(unique_tiles)):
        if is_gram:
            off = card * 8
            if off + 8 <= len(gram_data):
                card_bytes = gram_data[off:off+8]
            else:
                card_bytes = bytes(8)
            src = 'GRAM'
        else:
            card_bytes = get_grom_card_bytes(grom, card)
            src = 'GROM'

        # Use a neutral background for the tile sheet
        tile_img = render_tile(card_bytes, fg, (58, 138, 0), zoom=zoom)

        col = idx % cols
        row = idx // cols
        x = 4 + col * (tile_size + 4)
        y = 4 + row * (tile_size + 24)

        sheet.paste(tile_img, (x, y))
        label = f"{src[0]}{card} fg={fg} ${word:04X}"
        draw.text((x, y + tile_size + 2), label, fill=(220, 220, 220), font=font)

        # Also print to console
        nz = sum(1 for b in card_bytes if b != 0)
        print(f"  {src} card {card:3d} fg={fg} word=${word:04X} nonzero={nz} bytes={card_bytes.hex()}")

    out_path = os.path.join(PROJECT_DIR, 'sprites', 'debug_tile_sheet.png')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    sheet.save(out_path)
    print(f"\nSaved tile sheet: {out_path} ({sheet.width}x{sheet.height})")

if __name__ == '__main__':
    main()
