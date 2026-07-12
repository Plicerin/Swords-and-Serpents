#!/usr/bin/env python3
"""Batch-capture clean jzIntv reference GIFs for rooms 1-5.

Uses the proven $55DA breakpoint strategy from render_all_rooms.py with
an added 'vs' command.  jzIntv runs with a hidden window (STARTUPINFO)
but a REAL video driver so 'vs' has a framebuffer to capture.

The key insight: the debugger overlay only appears after long free-runs
that let the UI event loop compose text onto the SDL surface.  By breaking
at $55DA (immediately after the room renderer returns) and issuing 'vs'
*before* any long free-run, the framebuffer is captured pristine.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional
from PIL import Image

from render_all_rooms import (
    generate_debugger_script,
    TRACES_DIR, PROJECT_DIR, JZINTV, EXEC_PATH, GROM_PATH, ROM_PATH,
)
from versioning import next_versioned_path

COMPARISONS_DIR = os.path.join(PROJECT_DIR, "sprites", "comparisons")
SDL_ENV_REAL = os.environ.copy()
SDL_ENV_REAL["SDL_AUDIODRIVER"] = "dummy"
# NOTE: we do NOT set SDL_VIDEODRIVER=dummy — 'vs' needs a real framebuffer.


def run_capture_vs(room_index: int) -> Optional[Path]:
    """Capture a clean framebuffer screenshot for a single room.

    Returns the path to the cropped 160×96 playfield GIF, or None on failure.
    """
    script_path = Path(TRACES_DIR) / f"clean_ref_room_{room_index}.txt"
    out_txt = next_versioned_path(TRACES_DIR, f"clean_ref_room_{room_index}_out", ".txt")

    # Generate the $55DA-breakpoint script with 'vs' appended
    generate_debugger_script(room_index, script_path, include_vs=True)

    # Remove any old shot files so jzIntv produces shot0001.gif predictably
    for fname in os.listdir(PROJECT_DIR):
        if fname.startswith("shot") and fname.endswith(".gif"):
            os.remove(os.path.join(PROJECT_DIR, fname))

    cmd = [
        JZINTV, "-d",
        f"--script={script_path}",
        "-e", EXEC_PATH,
        "-g", GROM_PATH,
        ROM_PATH,
    ]

    # Hide window but keep real video driver
    startupinfo = None
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # SW_HIDE

    print(f"  Room {room_index}: running jzIntv (hidden window, $55DA breakpoint + vs) ...")
    try:
        with open(out_txt, "w", encoding="utf-8", errors="replace") as out_f:
            kwargs = {
                "stdout": out_f,
                "stderr": subprocess.STDOUT,
                "env": SDL_ENV_REAL,
                "cwd": PROJECT_DIR,
            }
            if startupinfo:
                kwargs["startupinfo"] = startupinfo
            proc = subprocess.Popen(cmd, **kwargs)
            try:
                proc.wait(timeout=120)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                print(f"  Room {room_index}: TIMEOUT")
                return None
    except FileNotFoundError:
        print(f"  ERROR: jzIntv not found at {JZINTV}")
        return None

    # Find the produced screenshot
    shot_files = [f for f in os.listdir(PROJECT_DIR)
                  if f.startswith("shot") and f.endswith(".gif")]
    if not shot_files:
        print(f"  Room {room_index}: no screenshot produced")
        return None

    shot_src = os.path.join(PROJECT_DIR, sorted(shot_files)[0])
    img = Image.open(shot_src).convert("RGB")
    # Crop to 160×96 playfield (same coordinates render_room.py uses)
    pf = img.crop((80, 52, 240, 148))

    # Save to canonical comparison path
    canonical = Path(COMPARISONS_DIR) / f"room_{room_index}_jzintv.gif"
    canonical.parent.mkdir(parents=True, exist_ok=True)
    pf.save(canonical)
    print(f"  Room {room_index}: saved {canonical}")

    # Quick contamination check
    white = sum(1 for c in pf.getdata() if c == (255, 255, 255))
    blue = sum(1 for c in pf.getdata() if c[2] > 200 and c[0] < 100 and c[1] < 100)
    black = sum(1 for c in pf.getdata() if c == (0, 0, 0))
    status = "CLEAN" if (white == 0 and blue == 0 and black == 0) else "CORRUPTED"
    print(f"  Room {room_index}: white={white} blue={blue} black={black} -> {status}")

    return canonical


def main():
    print("=" * 60)
    print("  Clean Reference Capture — $55DA breakpoint + vs")
    print("=" * 60)

    for room in range(1, 6):
        run_capture_vs(room)

    print("\n" + "=" * 60)
    print("  Done")
    print("=" * 60)


if __name__ == "__main__":
    main()
