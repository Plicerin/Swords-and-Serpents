#!/usr/bin/env python3
"""Extract the real 20x12 BACKTAB for rooms 0-5 from the jzIntv trace files
under traces/rooms/ and write assets/rooms.json (runbook §2.2).

For each room we use the canonical capture:
  - rooms 0-3: traces/rooms/render_room_{N}_out.txt
  - rooms 4-5: traces/rooms/cap_room_{N}_out.txt

Uses parse_backtab() / extract_backtab_from_output() from render_all_rooms.py.
The output rooms.json has 6 rooms of 240 flat int words each (matches
the format expected by tools/diff_room.py and the JS port).
"""
import json
import os
import sys

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(PROJECT_DIR)  # tools/ -> project root
sys.path.insert(0, PROJECT_DIR)
os.chdir(PROJECT_DIR)

import render_all_rooms as rar

TRACE_FILES = [
    'traces/rooms/render_room_0_out.txt',   # room 0
    'traces/rooms/render_room_1_out.txt',   # room 1
    'traces/rooms/render_room_2_out.txt',   # room 2
    'traces/rooms/render_room_3_out.txt',   # room 3
    'traces/rooms/cap_room_4_out.txt',      # room 4 (alt naming)
    'traces/rooms/cap_room_5_out.txt',      # room 5 (alt naming)
]

OUT_PATH = 'assets/rooms.json'


def main():
    rooms = []
    for idx, fn in enumerate(TRACE_FILES):
        if not os.path.exists(fn):
            print(f'  room {idx}: MISSING {fn}')
            rooms.append([0] * 240)
            continue
        with open(fn, 'r', errors='replace') as f:
            text = f.read()
        bt_text = rar.extract_backtab_from_output(text)
        if not bt_text:
            print(f'  room {idx}: no BACKTAB in {fn}')
            rooms.append([0] * 240)
            continue
        grid = rar.parse_backtab(bt_text)
        flat = [w for row in grid for w in row]
        n_nonzero = sum(1 for w in flat if w != 0)
        print(f'  room {idx}: {fn}  -> {len(flat)} words, {n_nonzero} non-zero')
        rooms.append(flat)

    with open(OUT_PATH, 'w') as f:
        json.dump({'rooms': rooms}, f)
    print(f'\n  wrote {OUT_PATH}: {len(rooms)} rooms x {len(rooms[0])} words')


if __name__ == '__main__':
    main()
