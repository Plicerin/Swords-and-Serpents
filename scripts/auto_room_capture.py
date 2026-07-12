#!/usr/bin/env python3
"""
auto_room_capture.py — Automated dungeon room capture for Swords & Serpents

Launches jzIntv with a visible SDL window, boots to room 0, then cycles
through rooms 1-5 by patching the room index in memory. For each room it
captures a jzIntv screenshot plus memory dumps (BACKTAB, GRAM, MOB data).

Usage:
    python scripts/auto_room_capture.py

Post-processing:
    python scripts/process_captures.py captures/YYYYMMDD_HHMMSS
"""

import subprocess
import threading
import time
import sys
from pathlib import Path
from datetime import datetime

# === Paths ===
PROJECT_ROOT = Path(__file__).resolve().parent.parent
JZINTV_EXE = PROJECT_ROOT / "jzintv-20200712-win32-sdl2" / "bin" / "jzintv.exe"
EXEC_BIN = PROJECT_ROOT / "exec.bin"
GROM_BIN = PROJECT_ROOT / "grom.bin"
GAME_ROM = PROJECT_ROOT / "Swords and Serpents.bin"

# Boot patches (same as render_all_rooms.py)
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

CAPTURE_REGIONS = [
    ("0200", "240"),   # BACKTAB
    ("3800", "512"),   # GRAM
    ("0028", "4"),     # Color stack
    ("0000", "32"),    # MOB registers
    ("0300", "96"),    # SYSRAM shadow
    ("0100", "256"),   # 8-bit RAM
]

ROOM_NAMES = [
    "First Room",
    "Room 1 (right)",
    "Room 2 (down)",
    "Room 3 (left)",
    "Room 4 (up)",
    "Final Room",
]


def find_jzintv():
    paths = [
        PROJECT_ROOT / "jzintv-20200712-win32-sdl2" / "bin" / "jzintv.exe",
        PROJECT_ROOT / "jzintv-20200712-win32-sdl2" / "jzintv-20200712-win32-sdl2" / "bin" / "jzintv.exe",
    ]
    for p in paths:
        if p.exists():
            return str(p)
    print(f"ERROR: jzIntv not found")
    return None


def create_boot_script(capture_dir):
    lines = ["; Auto-generated boot script", ""]
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
    lines.append("p 019C 0000")
    lines.append("p 018C 0001")
    lines.append("r 8000000")
    lines.append("c")
    lines.append("")

    script_path = capture_dir / "boot.script"
    script_path.write_text("\n".join(lines), encoding="utf-8")
    return str(script_path)


def drain_stdout(proc, log_path):
    with open(log_path, 'w', encoding='utf-8', errors='replace') as f:
        try:
            for line in proc.stdout:
                f.write(line)
                f.flush()
        except Exception as e:
            f.write(f"\n[STDOUT DRAIN ERROR: {e}]\n")


def send_room_capture(proc, room_idx):
    print(f"  Capturing room {room_idx}: {ROOM_NAMES[room_idx]}")
    try:
        proc.stdin.write(f"p 019C {room_idx:04X}\n")
        proc.stdin.flush()
        time.sleep(1.5)  # let game render new room

        proc.stdin.write("vs\n")
        proc.stdin.flush()

        for addr, count in CAPTURE_REGIONS:
            proc.stdin.write(f"m {addr} {count}\n")
            proc.stdin.flush()

        proc.stdin.write("c\n")
        proc.stdin.flush()
    except (BrokenPipeError, OSError) as e:
        print(f"  ERROR: jzIntv pipe broken ({e})")
        return False
    return True


def main():
    jzintv = find_jzintv()
    if not jzintv:
        return 1

    for name, path in [("exec.bin", EXEC_BIN), ("grom.bin", GROM_BIN),
                       ("Swords and Serpents.bin", GAME_ROM)]:
        if not path.exists():
            print(f"ERROR: Missing {name}")
            return 1

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    capture_dir = PROJECT_ROOT / "captures" / timestamp
    capture_dir.mkdir(parents=True, exist_ok=True)

    # Clean old screenshots
    old_shots = list(PROJECT_ROOT.glob("shot*.gif"))
    if old_shots:
        for old in old_shots:
            old.unlink()
        print(f"Removed {len(old_shots)} old screenshot(s)")

    print("=" * 65)
    print("  Swords & Serpents — Automated Room Capture")
    print("=" * 65)
    print()
    print(f"  Capture directory: {capture_dir}")
    print("  The emulator window will open and cycle through rooms 0-5.")
    print("  No interaction needed — just watch!")
    print()

    boot_script = create_boot_script(capture_dir)

    cmd = [
        jzintv, "-d",
        f"--script={boot_script}",
        "-e", str(EXEC_BIN),
        "-g", str(GROM_BIN),
        str(GAME_ROM),
    ]

    print(f"  Launching: {' '.join(cmd)}")
    print()

    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=str(PROJECT_ROOT),
    )

    log_path = capture_dir / "session.log"
    drain_thread = threading.Thread(target=drain_stdout, args=(proc, log_path), daemon=True)
    drain_thread.start()

    # Wait for boot (visible mode = real-time, ~18 s for 16M cycles)
    print("  Waiting for game to boot...")
    time.sleep(20)

    if proc.poll() is not None:
        print(f"  ERROR: jzIntv exited early (code {proc.returncode})")
        return 1

    print("  Game running! Starting room capture cycle...")
    print()

    captured = 0
    for room_idx in range(6):
        if proc.poll() is not None:
            print(f"  ERROR: jzIntv exited before room {room_idx}")
            break
        if send_room_capture(proc, room_idx):
            captured += 1
            time.sleep(2)  # pause between rooms so you can watch

    print()
    print(f"  Captured {captured}/6 rooms")
    print("  Shutting down jzIntv...")

    try:
        proc.stdin.write("q\n")
        proc.stdin.flush()
        time.sleep(2)
    except Exception:
        pass

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()

    # Collect screenshots
    shots = sorted(PROJECT_ROOT.glob("shot*.gif"))
    if shots:
        shots_dir = capture_dir / "screenshots"
        shots_dir.mkdir(exist_ok=True)
        for shot in shots:
            dest = shots_dir / shot.name
            shot.rename(dest)
        print(f"  Moved {len(shots)} screenshot(s) to {shots_dir}")

    print()
    print("=" * 65)
    print("  CAPTURE COMPLETE")
    print("=" * 65)
    print(f"  Session log:   {log_path}")
    print(f"  Captures dir:  {capture_dir}")
    print()
    print("  Next step: process captures into room PNGs")
    print(f"    python scripts/process_captures.py {capture_dir}")
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
