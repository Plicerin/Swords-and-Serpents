#!/usr/bin/env python3
"""Render rooms 0, 1, and 2 purely from BACKTAB tile data (no jzIntv GIF base)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from render_all_rooms import (
    load_grom,
    parse_memory_dump,
    parse_backtab,
    extract_backtab_from_output,
    extract_gram_from_output,
    extract_color_stack_from_output,
    parse_color_stack,
    render_room_image,
)
from PIL import Image

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOMS_DIR = os.path.join(PROJECT_DIR, "sprites", "rooms")
ZOOM = 8

def render_room_pure(room_num, out_path=None):
    dump_path = os.path.join(PROJECT_DIR, 'traces', 'rooms', f'render_room_{room_num}_out.txt')
    if out_path is None:
        out_path = os.path.join(ROOMS_DIR, f'room_{room_num}.png')

    with open(dump_path, 'r', encoding='utf-8', errors='replace') as f:
        raw = f.read()

    backtab_text = extract_backtab_from_output(raw)
    backtab_grid = parse_backtab(backtab_text)

    gram_text = extract_gram_from_output(raw)
    gram_mem = parse_memory_dump(gram_text, 0x3800, 512) if gram_text else {}

    cs_text = extract_color_stack_from_output(raw)
    color_stack = parse_color_stack(cs_text) if cs_text else None

    grom = load_grom()

    room_img = render_room_image(backtab_grid, gram_mem, grom,
                                  color_stack=color_stack, zoom=ZOOM, mobs=None)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    room_img.save(out_path)
    print(f"Saved: {out_path} ({room_img.width}×{room_img.height})")
    return room_img

if __name__ == '__main__':
    for i in [0, 1, 2]:
        render_room_pure(i)
