#!/usr/bin/env python3
"""
auto_room_cycle.py — Automated visible room capture for Swords & Serpents

Runs jzIntv six times (once per room 0-5) with a visible SDL window.
Each run boots the game, renders the specified room, takes a jzIntv
screenshot, dumps memory, and exits. The user can watch each room
appear in the emulator window.

Usage:
    python scripts/auto_room_cycle.py
"""

import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
JZINTV = PROJECT_ROOT / "jzintv-20200712-win32-sdl2" / "bin" / "jzintv.exe"
EXEC_BIN = PROJECT_ROOT / "exec.bin"
GROM_BIN = PROJECT_ROOT / "grom.bin"
GAME_ROM = PROJECT_ROOT / "Swords and Serpents.bin"

IDLE_PATCHES = [
    (0x506A, 0x0034), (0x506B, 0x0034), (0x506C, 0x0034),
    (0x506D, 0x0034), (0x506E, 0x0034),
    (0x5318, 0x0034), (0x5319, 0x0034), (0x531A, 0x0034),
    (0x531B, 0x02B8), (0x531C, 0x0001),
    (0x56CC, 0x0034), (0x56CD, 0x0034),
]

X_FILL_MEM_NOP = [
    (0x5638, 0x0034),
    (0x5639, 0x0034),
]

ROOM_NAMES = [
    "Room 0 — First Chamber",
    "Room 1 — East Wing",
    "Room 2 — South Hall",
    "Room 3 — West Wing",
    "Room 4 — North Tower",
    "Room 5 — Final Chamber",
]


def generate_room_script(room_idx, script_path):
    lines = [f"; Boot and capture room {room_idx}", ""]
    for addr, val in IDLE_PATCHES:
        lines.append(f"p {addr:04X} {val:04X}")
    lines.append("")
    lines.append("p 55C0 0034")
    lines.append("p 55C1 0034")
    lines.append("p 55C2 0034")
    lines.append("")
    for addr, val in X_FILL_MEM_NOP:
        lines.append(f"p {addr:04X} {val:04X}")
    lines.append("")
    lines.append("b 5038")
    lines.append("r 8000000")
    lines.append(f"p 019C {room_idx:04X}")
    lines.append("p 018C 0001")
    lines.append("r 8000000")
    lines.append("vs")
    lines.append("m 0200 240")
    lines.append("m 3800 512")
    lines.append("m 0028 4")
    lines.append("m 0000 32")
    lines.append("m 0300 96")
    lines.append("m 0100 256")
    lines.append("q")
    script_path.write_text("\n".join(lines), encoding="utf-8")


def run_jzintv_room(room_idx, capture_dir, script_path):
    cmd = [
        str(JZINTV), "-d",
        f"--script={script_path}",
        "-e", str(EXEC_BIN),
        "-g", str(GROM_BIN),
        str(GAME_ROM),
    ]

    log_path = capture_dir / f"room_{room_idx}.log"
    print(f"  Room {room_idx}: launching jzIntv...")

    try:
        with open(log_path, 'w', encoding='utf-8', errors='replace') as log_f:
            proc = subprocess.Popen(
                cmd,
                stdout=log_f,
                stderr=subprocess.STDOUT,
                cwd=str(PROJECT_ROOT),
            )
            try:
                proc.wait(timeout=60)
            except subprocess.TimeoutExpired:
                print(f"  Room {room_idx}: timeout — killing")
                proc.kill()
                proc.wait()
    except FileNotFoundError:
        print(f"  ERROR: jzIntv not found at {JZINTV}")
        return False

    return proc.returncode == 0 or proc.returncode == -9


def collect_screenshot(room_idx, capture_dir):
    shots = list(PROJECT_ROOT.glob("shot*.gif"))
    if not shots:
        return None
    # Most recent screenshot
    shot = max(shots, key=lambda p: p.stat().st_mtime)
    dest = capture_dir / f"room_{room_idx}.gif"
    shot.rename(dest)
    return dest


def main():
    if not JZINTV.exists():
        print(f"ERROR: jzIntv not found at {JZINTV}")
        return 1

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    capture_dir = PROJECT_ROOT / "captures" / timestamp
    capture_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print("  Swords & Serpents — Automated Room Capture")
    print("=" * 65)
    print("  The emulator window will open for each room.")
    print("  Watch the dungeon cycle through rooms 0-5!")
    print()

    screenshots = []
    for room_idx in range(6):
        print(f"\n  --- {ROOM_NAMES[room_idx]} ---")

        script_path = capture_dir / f"room_{room_idx}.script"
        generate_room_script(room_idx, script_path)

        success = run_jzintv_room(room_idx, capture_dir, script_path)
        if not success:
            print(f"  Room {room_idx}: jzIntv failed")
            continue

        time.sleep(0.5)
        shot = collect_screenshot(room_idx, capture_dir)
        if shot:
            print(f"  Screenshot: {shot.name}")
            screenshots.append(shot)
        else:
            print(f"  WARNING: no screenshot for room {room_idx}")

        # Small pause between rooms so user can see each one
        if room_idx < 5:
            print("  Next room in 2 seconds...")
            time.sleep(2)

    print()
    print("=" * 65)
    print("  CAPTURE COMPLETE")
    print("=" * 65)
    print(f"  Captured {len(screenshots)}/6 rooms")
    print(f"  Directory: {capture_dir}")
    print()

    if screenshots:
        print("  Screenshots:")
        for s in screenshots:
            print(f"    {s.name}")
        print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
