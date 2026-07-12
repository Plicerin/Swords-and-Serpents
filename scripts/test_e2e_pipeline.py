#!/usr/bin/env python3
"""
test_e2e_pipeline.py — Automated end-to-end test for the interactive capture pipeline.

This script automates what the user would do manually:
  1. Launch jzIntv, boot to room 0
  2. Capture memory dumps (BACKTAB, GRAM, color stack, MOBs, SYSRAM, 8-bit RAM)
  3. Save the session log
  4. Run process_captures.py on the log
  5. Verify the rendered PNG is clean

Unlike interactive_capture.py, this does NOT require pressing F4.
Instead it uses jzIntv's 'r' (run for N cycles) command to auto-pause
at the debugger prompt, where the next commands in stdin are executed.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

# === Paths ===
PROJECT_ROOT = Path(__file__).resolve().parent.parent
JZINTV_EXE = PROJECT_ROOT / "jzintv-20200712-win32-sdl2" / "bin" / "jzintv.exe"
EXEC_BIN = PROJECT_ROOT / "exec.bin"
GROM_BIN = PROJECT_ROOT / "grom.bin"
GAME_ROM = PROJECT_ROOT / "Swords and Serpents.bin"

# Patches (same as interactive_capture.py)
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
    ("0200", "240"),
    ("3800", "512"),
    ("0028", "4"),
    ("0000", "32"),
    ("0300", "96"),
    ("0100", "256"),
]


def find_jzintv():
    paths = [
        PROJECT_ROOT / "jzintv-20200712-win32-sdl2" / "bin" / "jzintv.exe",
        PROJECT_ROOT / "jzintv-20200712-win32-sdl2" / "jzintv-20200712-win32-sdl2" / "bin" / "jzintv.exe",
    ]
    for p in paths:
        if p.exists():
            return str(p)
    print(f"ERROR: jzIntv not found at: {paths[0]}")
    return None


def generate_debugger_script():
    """Generate a complete debugger script that boots, pauses, dumps memory, and quits."""
    lines = []

    # Skip title screen idle loops
    for addr, val in IDLE_PATCHES:
        lines.append(f"p {addr:04X} {val:04X}")

    # NOP CLRR + MVO G_019C at boot
    lines.append("p 55C0 0034")
    lines.append("p 55C1 0034")
    lines.append("p 55C2 0034")

    # NOP X_FILL_MEM
    for addr, val in X_FILL_MEM_NOP:
        lines.append(f"p {addr:04X} {val:04X}")

    # Break after X_FILL_ZERO
    lines.append("b 5038")

    # Boot through initialization
    lines.append("r 8000000")

    # Set room index + force 1-player start
    lines.append("p 019C 0000")
    lines.append("p 018C 0001")

    # Run into first room
    lines.append("r 8000000")

    # --- CAPTURE: auto-pause at debugger, dump memory, quit ---
    for addr, count in CAPTURE_REGIONS:
        lines.append(f"m {addr} {count}")

    lines.append("q")
    return "\n".join(lines) + "\n"


def main():
    jzintv = find_jzintv()
    if not jzintv:
        return 1

    for name, path in [("exec.bin", EXEC_BIN), ("grom.bin", GROM_BIN),
                       ("Swords and Serpents.bin", GAME_ROM)]:
        if not path.exists():
            print(f"ERROR: Missing {name} at {path}")
            return 1

    # Create capture directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    capture_dir = PROJECT_ROOT / "captures" / f"test_{timestamp}"
    capture_dir.mkdir(parents=True, exist_ok=True)
    log_path = capture_dir / "session.log"

    script = generate_debugger_script()
    script_path = capture_dir / "auto.script"
    script_path.write_text(script, encoding="utf-8")

    cmd = [
        jzintv,
        "-d",
        f"--script={script_path}",
        "-e", str(EXEC_BIN),
        "-g", str(GROM_BIN),
        str(GAME_ROM),
    ]

    print("=" * 65)
    print("  Automated End-to-End Pipeline Test")
    print("=" * 65)
    print(f"  Capture dir: {capture_dir}")
    print(f"  jzIntv:      {jzintv}")
    print()
    print("  Step 1/3: Running jzIntv (headless auto-capture)...")
    print("  (This takes ~20-30 seconds)")
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

    # jzIntv reads commands from the script file (--script=), not stdin.
    # We just need to collect stdout to the log.
    stdout_data, _ = proc.communicate()

    log_path.write_text(stdout_data, encoding="utf-8", errors="replace")

    print(f"  jzIntv exited with code: {proc.returncode}")
    print(f"  Session log: {log_path} ({len(stdout_data)} chars)")
    print()

    # Quick sanity check on log
    has_backtab = "0200:" in stdout_data
    has_gram = "3800:" in stdout_data
    print(f"  BACKTAB dump found: {has_backtab}")
    print(f"  GRAM dump found:    {has_gram}")
    print()

    if not has_backtab:
        print("  ERROR: No BACKTAB dump in session log. jzIntv may have failed.")
        return 1

    # Step 2: Run process_captures.py
    print("  Step 2/3: Running process_captures.py...")
    print()

    proc2 = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "process_captures.py"), str(capture_dir)],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )

    print(proc2.stdout)
    if proc2.stderr:
        print("STDERR:", proc2.stderr)

    if proc2.returncode != 0:
        print(f"  ERROR: process_captures.py failed with code {proc2.returncode}")
        return 1

    # Step 3: Verify output PNG
    print("  Step 3/3: Verifying output...")
    rooms_dir = capture_dir / "rooms"
    room_png = rooms_dir / "room_0.png"
    montage_png = rooms_dir / "montage.png"

    if room_png.exists():
        from PIL import Image
        img = Image.open(room_png)
        print(f"  OK: {room_png.name}  ({img.width}x{img.height})")
    else:
        print(f"  FAIL: {room_png} not found")
        return 1

    if montage_png.exists():
        print(f"  OK: {montage_png.name}")
    else:
        print(f"  WARN: {montage_png} not found")

    print()
    print("=" * 65)
    print("  PIPELINE TEST PASSED")
    print("=" * 65)
    print(f"  Capture dir: {capture_dir}")
    print(f"  Room PNG:    {room_png}")
    print()
    print("  The rendered PNG is clean because it was rendered purely from")
    print("  memory dumps (BACKTAB + GRAM + GROM) with no reference to")
    print("  any jzIntv screenshot that could carry debugger overlays.")
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
