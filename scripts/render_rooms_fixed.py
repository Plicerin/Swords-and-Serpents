#!/usr/bin/env python3
"""Render rooms 0, 1, 2 using corrected BACKTAB tile rendering.

Fix: render_all_rooms.py incorrectly treats ~80% of tiles as "Colored Squares"
and renders them as solid background. Swords & Serpents uses normal card
bitmap rendering for all tiles in Color Stack mode.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image

from render_all_rooms import (
    load_grom,
    get_grom_card_bytes,
    parse_memory_dump,
    parse_backtab,
    extract_backtab_from_output,
    extract_gram_from_output,
    extract_color_stack_from_output,
    parse_color_stack,
    decode_backtab_word,
    PALETTE,
    PASTEL_PALETTE,
    DEFAULT_BG,
)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOMS_DIR = os.path.join(PROJECT_DIR, "sprites", "rooms")
ZOOM = 8


def _fg_color_for_index(fg_color_idx):
    """Map FG color index to RGB."""
    if fg_color_idx >= 8:
        return PASTEL_PALETTE.get(fg_color_idx - 8, (255, 0, 255))
    return PALETTE.get(fg_color_idx, (255, 0, 255))


def render_tile(card_bytes, fg_color_idx, bg_color):
    """Render an 8x8 tile as a PIL Image."""
    fg = _fg_color_for_index(fg_color_idx)
    img = Image.new('RGB', (8, 8))
    px = img.load()
    for row in range(min(8, len(card_bytes))):
        byte_val = card_bytes[row]
        for col in range(8):
            bit = (byte_val >> (7 - col)) & 1
            px[col, row] = bg_color if bit == 0 else fg
    return img


def render_room_fixed(backtab_grid, gram_mem, grom, color_stack=None, zoom=8):
    """Render a room (12x20 tiles) purely from BACKTAB + GROM/GRAM.

    All tiles are rendered as normal card bitmaps. No colored-squares shortcut.
    """
    cols, rows = 20, 12
    tile_size = 8
    img_w = cols * tile_size * zoom
    img_h = rows * tile_size * zoom
    img = Image.new('RGB', (img_w, img_h))
    px = img.load()

    if color_stack is None or len(color_stack) < 4:
        # Swords & Serpents uses pastel tan for all CS entries
        color_stack = [PASTEL_PALETTE[3]] * 4

    cs_index = 0
    for row in range(rows):
        for col in range(cols):
            word = backtab_grid[row][col]
            card_idx, fg_color_idx, _, is_gram, _ = decode_backtab_word(word)

            # Color Stack advance
            advance = (word >> 13) & 1
            cs_index = (cs_index + advance) % 4
            bg = color_stack[cs_index]

            if is_gram:
                base = 0x3800 + card_idx * 8
                card_bytes = bytes(gram_mem.get(base + r, 0) & 0xFF for r in range(8))
            else:
                card_bytes = get_grom_card_bytes(grom, card_idx)

            tile_img = render_tile(card_bytes, fg_color_idx, bg)

            for y in range(tile_size):
                for x in range(tile_size):
                    rgb = tile_img.getpixel((x, y))
                    for dy in range(zoom):
                        for dx in range(zoom):
                            px_x = col * tile_size * zoom + x * zoom + dx
                            px_y = row * tile_size * zoom + y * zoom + dy
                            px[px_x, px_y] = rgb

    return img


def render_room_to_png(room_num, out_path=None):
    dump_path = os.path.join(PROJECT_DIR, 'traces', 'rooms', f'render_room_{room_num}_out.txt')
    if out_path is None:
        out_path = os.path.join(ROOMS_DIR, f'room_{room_num}.png')

    with open(dump_path, 'r', encoding='utf-8', errors='replace') as f:
        raw = f.read()

    backtab_grid = parse_backtab(extract_backtab_from_output(raw))
    gram_text = extract_gram_from_output(raw)
    gram_mem = parse_memory_dump(gram_text, 0x3800, 512) if gram_text else {}
    cs_text = extract_color_stack_from_output(raw)
    color_stack = parse_color_stack(cs_text) if cs_text else None
    grom = load_grom()

    room_img = render_room_fixed(backtab_grid, gram_mem, grom,
                                  color_stack=color_stack, zoom=ZOOM)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    room_img.save(out_path)
    print(f"Saved: {out_path} ({room_img.width}×{room_img.height})")
    return room_img, out_path


def build_montage(out_path=None):
    if out_path is None:
        out_path = os.path.join(PROJECT_DIR, 'rooms_0_1_2.png')

    room_paths = [os.path.join(ROOMS_DIR, f'room_{i}.png') for i in [0, 1, 2]]
    images = [Image.open(p) for p in room_paths]

    gap = 8
    label_h = 40
    border = 12
    room_w = images[0].width
    room_h = images[0].height

    total_w = border * 2 + 3 * room_w + 2 * gap
    total_h = border * 2 + label_h + room_h

    montage = Image.new('RGB', (total_w, total_h), (20, 20, 30))
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(montage)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except Exception:
        font = ImageFont.load_default()

    for idx, img in enumerate(images):
        x = border + idx * (room_w + gap)
        y = border + label_h
        montage.paste(img, (x, y))
        label = f"Room {idx}"
        bbox = draw.textbbox((0, 0), label, font=font)
        tw = bbox[2] - bbox[0]
        draw.text((x + (room_w - tw) // 2, border + 8), label, fill=(220, 220, 220), font=font)

    montage.save(out_path)
    print(f"Montage saved: {out_path} ({montage.width}×{montage.height})")
    return out_path


if __name__ == '__main__':
    for i in [0, 1, 2]:
        render_room_to_png(i)
    build_montage()
