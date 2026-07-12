#!/usr/bin/env python3
"""
process_captures.py — Render captured dungeon rooms from interactive session logs

Reads a capture session log (debugger output with memory dumps) and renders
each captured room to a PNG. Also produces a montage atlas.

Usage:
    python scripts/process_captures.py <capture_directory>

Example:
    python scripts/process_captures.py captures/20250726_143052
"""

import sys
import re
from pathlib import Path

# Add project root to path so we can import render_all_rooms
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from PIL import Image, ImageDraw, ImageFont

from render_all_rooms import (
    load_grom,
    parse_backtab,
    parse_memory_dump,
    extract_backtab_from_output,
    extract_gram_from_output,
    extract_color_stack_from_output,
    parse_color_stack,
    render_room_image,
)

ZOOM = 8
ROOM_W = 20 * 8 * ZOOM   # 1280
ROOM_H = 12 * 8 * ZOOM   # 768


def split_log_into_captures(log_text):
    """Split session log into individual capture chunks.

    Each capture starts with a BACKTAB dump at address 0200:.
    The initial setup script also dumps BACKTAB, so capture 0 is the
    auto-captured first room, and captures 1+ are user-triggered.
    """
    captures = []
    current_lines = []
    in_capture = False

    for line in log_text.split('\n'):
        stripped = line.strip()

        # A new capture starts with a BACKTAB dump at 0200:
        if re.match(r'^0200:', stripped):
            if current_lines:
                captures.append('\n'.join(current_lines))
            current_lines = [line]
            in_capture = True
        elif in_capture:
            current_lines.append(line)
        else:
            # Lines before first 0200: (boot output) — skip
            pass

    if current_lines:
        captures.append('\n'.join(current_lines))

    return captures


def render_capture(capture_text, grom):
    """Render a single capture into a clean PIL Image (no reference GIF needed)."""
    # Extract BACKTAB
    backtab_text = extract_backtab_from_output(capture_text)
    if not backtab_text.strip():
        return None

    backtab_grid = parse_backtab(backtab_text)

    # Extract GRAM
    gram_text = extract_gram_from_output(capture_text)
    gram_mem = parse_memory_dump(gram_text, 0x3800, 512) if gram_text else {}

    # Extract Color Stack (captured at $0028)
    cs_text = extract_color_stack_from_output(capture_text)
    color_stack = parse_color_stack(cs_text) if cs_text else None

    # Render purely from BACKTAB + GRAM + GROM (no reference GIF, no debugger overlay)
    img = render_room_image(
        backtab_grid, gram_mem, grom, zoom=ZOOM, color_stack=color_stack
    )

    return img


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/process_captures.py <capture_directory>")
        print()
        print("Example:")
        print("  python scripts/process_captures.py captures/20250726_143052")
        sys.exit(1)

    capture_dir = Path(sys.argv[1])
    if not capture_dir.exists():
        print(f"ERROR: Capture directory not found: {capture_dir}")
        sys.exit(1)

    log_path = capture_dir / "session.log"
    if not log_path.exists():
        print(f"ERROR: Session log not found: {log_path}")
        sys.exit(1)

    print("=" * 65)
    print("  Processing Captures")
    print("=" * 65)
    print(f"  Directory: {capture_dir}")
    print()

    # Read log
    with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
        log_text = f.read()

    # Split into captures
    captures = split_log_into_captures(log_text)
    print(f"  Found {len(captures)} capture(s) in session log")

    if not captures:
        print("  ERROR: No captures found. Did you queue any captures?")
        sys.exit(1)

    # Load GROM
    grom = load_grom()
    print(f"  GROM: {len(grom)} bytes ({len(grom) // 8} cards)")
    print()

    # (No screenshots — rooms are rendered purely from memory dumps)
    print()

    # Render each capture
    rooms_dir = capture_dir / "rooms"
    rooms_dir.mkdir(exist_ok=True)

    rendered = []
    for i, capture_text in enumerate(captures):
        print(f"  Capture {i}:")

        backtab_text = extract_backtab_from_output(capture_text)
        if not backtab_text.strip():
            print(f"    SKIP: No BACKTAB found")
            continue

        bt_lines = len([l for l in backtab_text.split('\n') if l.strip()])
        print(f"    BACKTAB lines: {bt_lines}")

        img = render_capture(capture_text, grom)
        if img is None:
            print(f"    ERROR: Render failed")
            continue

        out_path = rooms_dir / f"room_{i}.png"
        img.save(out_path)
        print(f"    Saved: {out_path.name} ({img.width}x{img.height})")
        rendered.append((i, img))

    if not rendered:
        print("  ERROR: No rooms rendered successfully.")
        sys.exit(1)

    # Build montage
    print()
    print("  Building montage...")

    margin = 16
    label_h = 32
    cols = min(3, len(rendered))
    rows = (len(rendered) + cols - 1) // cols

    atlas_w = cols * ROOM_W + (cols + 1) * margin
    atlas_h = rows * (ROOM_H + label_h + margin) + margin

    atlas = Image.new('RGB', (atlas_w, atlas_h), (15, 15, 25))
    draw = ImageDraw.Draw(atlas)

    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except Exception:
        font = ImageFont.load_default()

    for idx, (cap_idx, img) in enumerate(rendered):
        ar = idx // cols
        ac = idx % cols

        xo = margin + ac * (ROOM_W + margin)
        yo = margin + ar * (ROOM_H + label_h + margin)

        label = f"Room {cap_idx}"
        draw.text((xo + 4, yo + 4), label, fill=(220, 220, 220), font=font)
        atlas.paste(img, (xo, yo + label_h))

    montage_path = rooms_dir / "montage.png"
    atlas.save(montage_path)
    print(f"  Saved: {montage_path.name} ({atlas_w}x{atlas_h})")

    print()
    print("=" * 65)
    print("  DONE")
    print("=" * 65)
    print(f"  Rooms:   {rooms_dir}")
    print(f"  Montage: {montage_path}")


if __name__ == '__main__':
    main()
