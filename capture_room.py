#!/usr/bin/env python3
"""
Swords & Serpents — Single Room Capture
Runs jzIntv headless with debugger patches to fast-boot into a specific room,
dumps BACKTAB + GRAM, and renders a pixel-perfect 4× scaled room image.

Uses the proven render_all_rooms.py pipeline:
  headless jzIntv → debugger patches → memory dumps → room render

This approach produces 100% pixel-accurate output matching jzIntv's
native display, verified against F12 screenshots from jzIntv itself.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from versioning import next_versioned_path

# Reuse the proven rendering pipeline from render_all_rooms.py
from render_all_rooms import (
    TRACES_DIR,
    generate_debugger_script, run_debugger_script,
    extract_backtab_from_output, extract_gram_from_output,
    extract_color_stack_from_output, extract_memory_section,
    parse_backtab, parse_mobs, parse_color_stack,
    parse_memory_dump,
    load_grom, render_room_image,
)

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = ROOT / "sprites" / "rooms"


def capture_room(room_index: int, output_path: Optional[Path] = None, hidden: bool = False) -> Path:
    """Capture a single dungeon room using headless jzIntv + BACKTAB rendering.

    Args:
        room_index: Room number 0-5.
        output_path: Where to save the rendered PNG (640×384, 4× scale).
                     If None, a versioned filename is generated automatically.
        hidden: If True, hide the jzIntv window during capture (Windows only).
                Useful for automated scripts to avoid debugger overlay flicker.

    Returns:
        The final Path the image was saved to.
    """
    grom = load_grom()

    script_path = Path(TRACES_DIR) / f"render_room_{room_index}.txt"
    output_txt = next_versioned_path(TRACES_DIR, f"render_room_{room_index}_out", ".txt")

    # Generate and run debugger script (preserve GRAM init so custom tiles render)
    generate_debugger_script(room_index, script_path, skip_gram_patches=True)
    output = run_debugger_script(script_path, output_txt, hidden=hidden)

    if not output:
        raise RuntimeError(f"No output from jzIntv for room {room_index}")

    # Parse BACKTAB
    backtab_text = extract_backtab_from_output(output)
    if not backtab_text:
        raise RuntimeError(f"No BACKTAB data found for room {room_index}")
    backtab_grid = parse_backtab(backtab_text)

    # Parse GRAM
    gram_text = extract_gram_from_output(output)
    gram_mem = parse_memory_dump(gram_text, 0x3800, 512) if gram_text else {}

    # Parse color stack
    cs_text = extract_color_stack_from_output(output)
    color_stack = parse_color_stack(cs_text) if cs_text else None

    # Parse MOB sprites from SYSRAM shadow
    sysram_text = extract_memory_section(output, 0x0300, 0x0360)
    mobs = parse_mobs(sysram_text) if sysram_text else []

    # Render and save
    zoom = 4
    room_img = render_room_image(
        backtab_grid, gram_mem, grom,
        color_stack=color_stack, zoom=zoom, mobs=mobs,
    )

    if output_path is None:
        output_path = next_versioned_path(str(DEFAULT_OUTPUT), f"dungeon_room_{room_index}", ".png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    room_img.save(output_path)
    print(f"  Saved: {output_path} ({room_img.width}×{room_img.height}, {len(mobs)} MOBs)")
    return output_path


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python capture_room.py <room_index> [output_path]")
        print("Example: python capture_room.py 0 sprites/rooms/dungeon_room_0.png")
        sys.exit(1)

    room = int(sys.argv[1])
    if len(sys.argv) > 2:
        output = Path(sys.argv[2])
    else:
        output = next_versioned_path(str(DEFAULT_OUTPUT), f"dungeon_room_{room}", ".png")

    print("=" * 60)
    print(f"  SWORDS & SERPENTS — Room {room} Capture")
    print("=" * 60)

    final_path = capture_room(room, output)
    print(f"\n  Output: {final_path}")


if __name__ == "__main__":
    main()
