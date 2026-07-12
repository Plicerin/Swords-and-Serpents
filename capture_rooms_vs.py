#!/usr/bin/env python3
"""
Swords & Serpents — Clean Room Screenshot Capture
Uses jzIntv's 'vs' command for pixel-perfect screenshots without
any debugger overlay.  Bypasses the title screen via G_018C=1.
"""
import os
import re
import subprocess
import sys
from pathlib import Path
from PIL import Image
from collections import Counter

from versioning import next_versioned_path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ROM_PATH    = os.path.join(PROJECT_DIR, "Swords and Serpents.bin")
GROM_PATH   = os.path.join(PROJECT_DIR, "grom.bin")
EXEC_PATH   = os.path.join(PROJECT_DIR, "exec.bin")
JZINTV      = os.path.join(PROJECT_DIR, "jzintv-20200712-win32-sdl2", "bin", "jzintv.exe")
TRACES_DIR  = os.path.join(PROJECT_DIR, "traces", "rooms")
ROOMS_DIR   = os.path.join(PROJECT_DIR, "sprites", "rooms")

# Force headless SDL so no window pops up
SDL_ENV = os.environ.copy()
# NOTE: we do NOT set SDL_VIDEODRIVER=dummy because jzIntv's
# 'vs' command needs a real framebuffer.  The window is hidden
# via STARTUPINFO instead.
SDL_ENV["SDL_AUDIODRIVER"]  = "dummy"

# ---------------------------------------------------------------------------
# Idle / title-screen bypass patches
# ---------------------------------------------------------------------------
IDLE_PATCHES = [
    (0x506A, 0x0034), (0x506B, 0x0034), (0x506C, 0x0034),
    (0x506D, 0x0034), (0x506E, 0x0034),
    (0x5318, 0x0034), (0x5319, 0x0034), (0x531A, 0x0034),
    (0x531B, 0x02B8), (0x531C, 0x0001),
    (0x56CC, 0x0034), (0x56CD, 0x0034),   # BEQ L_56F8  (title-screen wait)
    (0x5638, 0x0034), (0x5639, 0x0034),   # NOP X_FILL_MEM wipe
]

# ---------------------------------------------------------------------------
# Script generation
# ---------------------------------------------------------------------------
def generate_script(room_index, cycles_after_setup=15_000_000):
    lines = []
    lines.append(f"; Auto-generated script for room {room_index}")
    lines.append("; Strategy: break after X_FILL_ZERO, write G_019C+G_018C,")
    lines.append(";           run long enough to get past title into gameplay,")
    lines.append(";           then take a clean 'vs' screenshot.")
    lines.append("")

    # Patches
    for addr, val in IDLE_PATCHES:
        lines.append(f"p {addr:04X} {val:04X}")
    lines.append("")

    # NOP boot CLRR + MVO G_019C  (so X_FILL_ZERO leaves it 0)
    lines.append("p 55C0 0034")
    lines.append("p 55C1 0034")
    lines.append("p 55C2 0034")
    lines.append("")

    # Break after X_FILL_ZERO returns to $5038
    lines.append("b 5038")
    lines.append("r 8000000")
    lines.append("")

    # Force room index and skip title-screen wait
    lines.append(f"; Room index = {room_index}, force past title screen")
    lines.append(f"p 019C {room_index:04X}")
    lines.append("p 018C 0001")
    lines.append("")

    # Run long enough to get past the title screen into gameplay
    lines.append(f"; Run {cycles_after_setup} cycles to let game settle")
    lines.append(f"r {cycles_after_setup}")
    lines.append("")

    # Clean screenshot (no debugger overlay)
    lines.append("; Capture frame-buffer screenshot")
    lines.append("vs")
    lines.append("")

    # Memory dumps for sanity-check / backup rendering
    lines.append("; Dump BACKTAB + GRAM for verification")
    lines.append("m 0200 240")
    lines.append("m 3800 512")
    lines.append("q")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Run jzIntv and handle shot files
# ---------------------------------------------------------------------------
def run_capture(room_index, cycles=15_000_000):
    script_path = os.path.join(TRACES_DIR, f"cap_room_{room_index}.txt")
    output_path = str(next_versioned_path(TRACES_DIR, f"cap_room_{room_index}_out", ".txt"))

    os.makedirs(TRACES_DIR, exist_ok=True)
    os.makedirs(ROOMS_DIR, exist_ok=True)

    # Write debugger script
    with open(script_path, "w") as f:
        f.write(generate_script(room_index, cycles))

    # Remove any old shot files in the project root so jzIntv
    # always produces shot0001.gif (predictable name)
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

    # Hide window on Windows
    startupinfo = None
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # SW_HIDE

    print(f"  Room {room_index}: running jzIntv (cycles={cycles:,}) ...")
    try:
        with open(output_path, "w", encoding="utf-8", errors="replace") as out_f:
            kwargs = {
                "stdout": out_f,
                "stderr": subprocess.STDOUT,
                "env": SDL_ENV,
                "cwd": PROJECT_DIR,
            }
            if startupinfo:
                kwargs["startupinfo"] = startupinfo
            proc = subprocess.Popen(cmd, **kwargs)
            try:
                proc.wait(timeout=300)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                print(f"  Room {room_index}: TIMEOUT")
    except FileNotFoundError:
        print(f"  ERROR: jzIntv not found at {JZINTV}")
        return None, None

    # Locate the produced screenshot
    shot_files = [f for f in os.listdir(PROJECT_DIR)
                  if f.startswith("shot") and f.endswith(".gif")]
    if not shot_files:
        print(f"  Room {room_index}: no screenshot produced")
        return None, output_path

    shot_src = os.path.join(PROJECT_DIR, sorted(shot_files)[0])
    shot_dst = next_versioned_path(ROOMS_DIR, f"room_{room_index}_jzintv", ".gif")

    # Convert to RGB and save cleanly
    img = Image.open(shot_src).convert("RGB")
    img.save(shot_dst)
    print(f"  Room {room_index}: screenshot saved -> {shot_dst}")

    return shot_dst, output_path


# ---------------------------------------------------------------------------
# Simple BACKTAB parser (borrowed from render_all_rooms.py)
# ---------------------------------------------------------------------------
def parse_backtab(text):
    grid = [[0] * 20 for _ in range(12)]
    current_addr = None
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r'^([0-9A-F]{4}):\s+(.*)', line)
        if m:
            current_addr = int(m.group(1), 16)
            rest = m.group(2)
        elif re.match(r'^[0-9A-F]{4}\s', line):
            current_addr = int(line[:4], 16)
            rest = line[5:]
        else:
            continue
        words = re.findall(r'([0-9A-F]{4})\*?', rest)
        for w in words:
            if current_addr is not None and 0x0200 <= current_addr < 0x02F0:
                offset = current_addr - 0x0200
                row = offset // 20
                col = offset % 20
                if row < 12 and col < 20:
                    grid[row][col] = int(w, 16)
            if current_addr is not None:
                current_addr += 1
    return grid


def extract_backtab(output_text):
    lines = output_text.split('\n')
    backtab_lines = []
    in_backtab = False
    for line in lines:
        stripped = line.strip()
        if re.match(r'^0200:', stripped):
            in_backtab = True
        if in_backtab:
            if re.match(r'^3800:', stripped):
                break
            m = re.match(r'^([0-9A-F]{4}):', stripped)
            if m and int(m.group(1), 16) >= 0x02F0:
                break
            backtab_lines.append(line)
    return '\n'.join(backtab_lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("  Swords & Serpents — Clean Room Capture (vs screenshots)")
    print("=" * 60)

    results = []
    for room in range(6):
        print(f"\n--- Room {room} ---")
        shot_path, out_path = run_capture(room, cycles=15_000_000)
        results.append((room, shot_path, out_path))

    # Analyse results
    print("\n" + "=" * 60)
    print("  Analysis")
    print("=" * 60)

    screenshots = {}
    for room, shot_path, out_path in results:
        if not shot_path or not os.path.exists(shot_path):
            print(f"Room {room}: NO SCREENSHOT")
            continue
        img = Image.open(shot_path).convert("RGB")
        colors = Counter(img.getdata())
        screenshots[room] = img
        print(f"Room {room}: {img.size}, {len(colors)} colors")
        print(f"         top: {colors.most_common(5)}")

    # Pairwise comparison
    print("\n--- Pairwise pixel match ---")
    for i in range(6):
        for j in range(i + 1, 6):
            if i not in screenshots or j not in screenshots:
                continue
            a = screenshots[i]
            b = screenshots[j]
            match = 0
            total = 0
            for y in range(a.height):
                for x in range(a.width):
                    if a.getpixel((x, y)) == b.getpixel((x, y)):
                        match += 1
                    total += 1
            print(f"Room {i} vs {j}: {100 * match / total:.1f}%")

    # Also print BACKTAB stats for each room
    print("\n--- BACKTAB stats ---")
    for room, _, out_path in results:
        if not out_path or not os.path.exists(out_path):
            continue
        with open(out_path, "r", encoding="utf-8", errors="replace") as f:
            output = f.read()
        bt_text = extract_backtab(output)
        if not bt_text.strip():
            print(f"Room {room}: no BACKTAB data")
            continue
        bt = parse_backtab(bt_text)
        words = Counter()
        for r in range(12):
            for c in range(20):
                words[bt[r][c]] += 1
        print(f"Room {room}: {len(words)} unique words, "
              f"{sum(1 for r in range(12) for c in range(20) if bt[r][c] != 0x1603)} non-floor")

    print("\n" + "=" * 60)
    print("  DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()
