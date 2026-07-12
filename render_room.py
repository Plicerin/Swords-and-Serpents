#!/usr/bin/env python3
"""
Swords & Serpents — Room Renderer (Reference-GIF based)

Renders a single room using a jzIntv reference GIF as the base image.
Replaces blue, white, and black emulator overlay artifacts with colors
computed from the BACKTAB card bitmap.  All other pixels are kept
exactly as jzIntv renders them.

WARNING: The jzIntv reference GIFs in sprites/comparisons/ MUST be
captured WITHOUT debugger overlay.  If the reference GIF contains
jzIntv's own debug text (white/blue/black strings in the margins),
those pixels will be copied into the output because they do NOT match
the artifact colors this script removes.

For a 100% clean pipeline that does NOT depend on any reference GIF,
use capture_room.py or render_all_rooms.py instead.

Usage: python render_room.py <room_number> [--zoom N] [--out path]
"""
import os
import sys
from pathlib import Path
from PIL import Image

from versioning import next_versioned_path
from render_all_rooms import (
    decode_backtab_word, PALETTE,
    EMPIRICAL_FG, EMPIRICAL_BG_COLOR,
    load_grom, get_grom_card_bytes, parse_backtab, extract_backtab_from_output,
    parse_memory_dump, extract_gram_from_output,
    extract_color_stack_from_output, parse_color_stack,
)
from room_renderer import (
    BLUE, BLACK, resolve_artifact_pixel, is_whiteish, PASTEL_TAN, ARTIFACT_ROW_LIMIT,
)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ZOOM = 8
PLAYFIELD_CROP = (80, 52, 240, 148)  # 160x96 playfield in 320x200 GIF


def get_card_row(card_idx, row, is_gram, gram_mem, grom):
    """Get byte row from GROM or GRAM card."""
    if is_gram:
        base = 0x3800 + (card_idx & 0x3F) * 8
        return gram_mem.get(base + row, 0) & 0xFF
    else:
        card_bytes = get_grom_card_bytes(grom, card_idx)
        return card_bytes[row] if row < len(card_bytes) else 0


def resolve_fg_color(word, fg_color_idx):
    """Get the actual FG color for a BACKTAB word."""
    if word in EMPIRICAL_FG:
        fg_idx = EMPIRICAL_FG[word]
        return PALETTE.get(fg_idx, (0, 0, 0))
    if fg_color_idx == 0:
        return (0, 0, 0)
    return PALETTE.get(fg_color_idx, (0, 0, 0))


def resolve_bg_color(word, color_stack):
    """Get the actual background (Color Stack) color for a BACKTAB word."""
    if word in EMPIRICAL_BG_COLOR:
        return EMPIRICAL_BG_COLOR[word]
    # Default to the game's actual Color Stack color (pastel tan)
    if color_stack and len(color_stack) >= 4:
        return color_stack[0]
    return PASTEL_TAN


def render_room_jzintv(room_num, dump_path=None, out_path=None, zoom=ZOOM):
    """Render a single room using jzIntv reference GIF as the base.

    Filters out blue, white, and black emulator overlay artifacts in the
    top tile rows by replacing them with colors computed from the BACKTAB
    card bitmap.  All other pixels are kept exactly as jzIntv renders them.
    """

    if dump_path is None:
        dump_path = os.path.join(PROJECT_DIR, 'traces', 'rooms', f'render_room_{room_num}_out.txt')
    if out_path is None:
        out_path = next_versioned_path(
            os.path.join(PROJECT_DIR, 'sprites', 'rooms'),
            f'room_{room_num}',
            '.png'
        )
    
    ref_gif_path = os.path.join(PROJECT_DIR, 'sprites', 'comparisons', f'room_{room_num}_jzintv.gif')
    
    if not os.path.exists(dump_path):
        print(f"ERROR: Dump file not found: {dump_path}")
        return None
    if not os.path.exists(ref_gif_path):
        print(f"ERROR: jzIntv reference GIF not found: {ref_gif_path}")
        return None
    
    with open(dump_path, 'r', encoding='utf-8', errors='replace') as f:
        raw = f.read()
    
    # Load jzIntv reference GIF and crop to playfield
    try:
        ref = Image.open(ref_gif_path)
        pf = ref.crop(PLAYFIELD_CROP).convert('RGB')
    except Exception as e:
        print(f"ERROR: Failed to load reference GIF {ref_gif_path}: {e}")
        return None
    pf_px = pf.load()
    
    # Load BACKTAB
    backtab_text = extract_backtab_from_output(raw)
    backtab_grid = parse_backtab(backtab_text)
    
    # Load GRAM
    gram_text = extract_gram_from_output(raw)
    gram_mem = parse_memory_dump(gram_text, 0x3800, 512) if gram_text else {}
    
    # Load GROM
    grom = load_grom()
    
    # Load Color Stack (for fallback / blue replacement)
    cs_text = extract_color_stack_from_output(raw)
    color_stack = parse_color_stack(cs_text) if cs_text else None
    
    # Build clean output: same size as playfield (160x96 at 1x)
    clean = Image.new('RGB', (160, 96))
    clean_px = clean.load()
    
    artifact_counts = {"blue": 0, "white": 0, "black": 0}

    for ty in range(12):
        for tx in range(20):
            word = backtab_grid[ty][tx]
            card_idx, fg_color_idx, bg_bits, is_gram, fg_transp = decode_backtab_word(word)

            fg_color = resolve_fg_color(word, fg_color_idx)
            bg_color = resolve_bg_color(word, color_stack)

            for y in range(8):
                byte_val = get_card_row(card_idx, y, is_gram, gram_mem, grom)
                for x in range(8):
                    px_x = tx * 8 + x
                    px_y = ty * 8 + y
                    src_color = pf_px[px_x, px_y]

                    # Compute expected card color for this pixel
                    card_bit = (byte_val >> (7 - x)) & 1
                    if card_bit == 0 or fg_transp:
                        expected = bg_color
                    else:
                        expected = fg_color

                    resolved, art_type = resolve_artifact_pixel(src_color, expected, ty)
                    if art_type:
                        artifact_counts[art_type] += 1
                    clean_px[px_x, px_y] = resolved
    
    # Scale to desired zoom
    scaled = clean.resize((160 * zoom, 96 * zoom), Image.NEAREST)
    
    # Note: MOBs are already rendered correctly by jzIntv in the reference GIF.
    # We replace blue, white, and black emulator artifacts, so jzIntv's MOB
    # rendering is preserved. No additional MOB overlay is needed.
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    scaled.save(out_path)
    print(f"Saved: {out_path} ({scaled.width}x{scaled.height})")
    print(f"  Replaced {artifact_counts['blue']} blue overlay pixels")
    print(f"  Removed {artifact_counts['white']} white text pixels")
    print(f"  Removed {artifact_counts['black']} black outline pixels")

    # Verify: count remaining blue, white-ish, and black pixels
    blue_check = 0
    white_check = 0
    black_check = 0
    for y in range(scaled.height):
        for x in range(scaled.width):
            c = scaled.getpixel((x, y))
            if c == BLUE:
                blue_check += 1
            elif is_whiteish(c):
                white_check += 1
            elif c == BLACK:
                black_check += 1
    print(f"  Blue pixels remaining: {blue_check}")
    print(f"  White-ish pixels remaining: {white_check}")
    print(f"  Black pixels remaining: {black_check}")

    # Top-row verification: ensure zero artifacts in rows below ARTIFACT_ROW_LIMIT
    top_rows_h = ARTIFACT_ROW_LIMIT * 8 * zoom
    top_blue = sum(1 for y in range(top_rows_h) for x in range(scaled.width)
                   if scaled.getpixel((x, y)) == BLUE)
    top_white = sum(1 for y in range(top_rows_h) for x in range(scaled.width)
                    if is_whiteish(scaled.getpixel((x, y))))
    top_black = sum(1 for y in range(top_rows_h) for x in range(scaled.width)
                    if scaled.getpixel((x, y)) == BLACK)
    print(f"  Top-row blue artifacts: {top_blue}")
    print(f"  Top-row white artifacts: {top_white}")
    print(f"  Top-row black artifacts: {top_black}")
    
    # Color stats
    color_counts = {}
    px = scaled.load()
    for y in range(0, scaled.height, 2):
        for x in range(0, scaled.width, 2):
            c = px[x, y]
            color_counts[c] = color_counts.get(c, 0) + 1
    print(f"  Unique colors: {len(color_counts)}")
    for rgb, cnt in sorted(color_counts.items(), key=lambda x: -x[1])[:10]:
        pct = 100 * cnt / (scaled.width * scaled.height / 4)
        label = ""
        if rgb == PASTEL_TAN: label = " (pastel tan - CS bg)"
        elif rgb == (0, 0, 0): label = " (black)"
        elif rgb == (203, 241, 104): label = " (primary tan)"
        elif rgb == (255, 255, 255): label = " (white)"
        elif rgb == BLUE: label = " (BLUE - should be 0!)"
        print(f"    RGB({rgb[0]:3d},{rgb[1]:3d},{rgb[2]:3d}) {cnt:>7d} ({pct:5.1f}%){label}")
    
    return scaled


def find_available_rooms():
    """Return list of room numbers that have dump files available."""
    available = []
    for i in range(6):
        dump_path = os.path.join(PROJECT_DIR, 'traces', 'rooms', f'render_room_{i}_out.txt')
        gif_path = os.path.join(PROJECT_DIR, 'sprites', 'comparisons', f'room_{i}_jzintv.gif')
        if os.path.exists(dump_path) and os.path.exists(gif_path):
            available.append(i)
    return available


def render_room(room_num, dump_path=None, out_path=None, zoom=ZOOM, **kwargs):
    """Main entry point — delegates to jzIntv-based renderer."""
    return render_room_jzintv(room_num, dump_path, out_path, zoom=zoom)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Render a Swords & Serpents room')
    parser.add_argument('room_num', type=int, help='Room number to render')
    parser.add_argument('--zoom', type=int, default=ZOOM, help='Output zoom factor (default: 8)')
    parser.add_argument('--out', type=str, default=None, help='Output path override')
    args = parser.parse_args()
    if args.zoom < 1:
        parser.error('--zoom must be >= 1')
    render_room(args.room_num, out_path=args.out, zoom=args.zoom)
