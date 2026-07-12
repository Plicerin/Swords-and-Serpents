#!/usr/bin/env python3
"""Capture a single room trace with GRAM properly initialized."""
import os
import sys
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from render_all_rooms import (
    generate_debugger_script, run_debugger_script, extract_gram_from_output,
    parse_memory_dump, extract_backtab_from_output, parse_backtab,
    ROOMS_DIR, TRACES_DIR,
)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JZINTV = os.path.join(PROJECT_DIR, "jzintv-20200712-win32-sdl2", "bin", "jzintv.exe")
EXEC_PATH = os.path.join(PROJECT_DIR, "exec.bin")
GROM_PATH = os.path.join(PROJECT_DIR, "grom.bin")
ROM_PATH = os.path.join(PROJECT_DIR, "Swords and Serpents.bin")

ROOM_PARAMS = [
    (0x0062, 0x000B),   # room 0
    (0x000C, 0x001A),   # room 1
    (0x001B, 0x001C),   # room 2
    (0x0062, 0x0004),   # room 3
]

def generate_script_no_gram_patch(room_idx, output_path):
    """Generate a debugger script that does NOT patch the GRAM init loop."""
    # Start from the standard script
    standard_script = os.path.join(TRACES_DIR, f"render_room_{room_idx}.txt")
    if not os.path.exists(standard_script):
        generate_debugger_script(room_idx, standard_script)

    with open(standard_script, 'r') as f:
        lines = f.read().split('\n')

    # Remove any patch lines that target $5318-$531C (GRAM init)
    filtered = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('p 531'):
            print(f"  Skipping GRAM patch: {stripped}")
            continue
        filtered.append(line)

    with open(output_path, 'w') as f:
        f.write('\n'.join(filtered))
    print(f"Generated: {output_path}")


def main():
    room_idx = 0
    os.makedirs(TRACES_DIR, exist_ok=True)

    script_path = os.path.join(TRACES_DIR, f"room_{room_idx}_gram_script.txt")
    output_path = os.path.join(TRACES_DIR, f"room_{room_idx}_gram_out.txt")

    generate_script_no_gram_patch(room_idx, script_path)

    # Run jzIntv
    cmd = [
        JZINTV, "-d",
        f"--script={script_path}",
        "-e", EXEC_PATH,
        "-g", GROM_PATH,
        ROM_PATH,
    ]
    print(f"Running jzIntv for room {room_idx} ...")
    env = os.environ.copy()
    env["SDL_VIDEODRIVER"] = "dummy"
    env["SDL_AUDIODRIVER"] = "dummy"

    try:
        with open(output_path, 'w', encoding='utf-8', errors='replace') as out_f:
            proc = subprocess.Popen(cmd, stdout=out_f, stderr=subprocess.STDOUT, env=env, cwd=PROJECT_DIR)
            try:
                proc.wait(timeout=300)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                print("TIMEOUT after 300s")
    except FileNotFoundError:
        print(f"jzIntv not found at {JZINTV}")
        return

    # Parse output
    with open(output_path, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    gram_text = extract_gram_from_output(text)
    gram_mem = parse_memory_dump(gram_text, 0x3800, 512) if gram_text else {}
    print(f"GRAM entries parsed: {len(gram_mem)}")

    # Check card 3, 4, 5, 10
    for card in [3, 4, 5, 10, 192]:
        base = 0x3800 + card * 8
        nz = sum(1 for r in range(8) if gram_mem.get(base + r, 0) != 0)
        print(f"  GRAM card {card}: {nz}/8 nonzero bytes")

    # BACKTAB stats
    bt = parse_backtab(extract_backtab_from_output(text))
    unique = set()
    for r in range(12):
        for c in range(20):
            word = bt[r][c]
            card = (word >> 3) & 0xFF
            is_gram = bool((word >> 11) & 1)
            unique.add((card, is_gram))
    print(f"BACKTAB unique cards: {len(unique)}")
    for card, is_gram in sorted(unique):
        print(f"  {'GRAM' if is_gram else 'GROM'} {card}")


if __name__ == '__main__':
    main()
