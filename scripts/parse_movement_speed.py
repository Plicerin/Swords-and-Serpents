#!/usr/bin/env python3
"""Parse movement_speed_probe output and compute MOVE_SPEED.

Usage:
    .\jzintv\jzintv-20200712-win32-sdl2\bin\jzintv.exe -d --script=scripts/movement_speed_probe.txt \
        -e exec.bin -g grom.bin "Swords and Serpents.bin" > traces\movement_speed_out.txt
    python scripts\parse_movement_speed.py traces\movement_speed_out.txt
"""

import re
import sys


def parse_dump_line(line):
    """Parse 'ADDR: XXXX   # ...' → (addr_int, value_int) or None."""
    m = re.match(r'\s*\*?([0-9A-Fa-f]{4}):\s+([0-9A-Fa-f]+)', line)
    if m:
        return int(m.group(1), 16), int(m.group(2), 16)
    return None


def extract_xy(lines):
    """Extract (X, Y) pairs in order from the dump output.

    Returns list of (x_raw, y_raw) tuples in the order they appear.
    x_raw = $0325 word, y_raw = $032D word.
    Pixel coords: x_px = (x_raw & 0xFF) - 8, y_px = (y_raw & 0x7F) - 8.
    """
    results = []
    i = 0
    while i < len(lines):
        p = parse_dump_line(lines[i])
        if p and p[0] == 0x0325:
            x_raw = p[1]
            # look ahead for the Y dump on the next non-empty line
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                q = parse_dump_line(lines[j])
                if q and q[0] == 0x032D:
                    y_raw = q[1]
                    results.append((x_raw, y_raw))
                    i = j + 1
                    continue
        i += 1
    return results


def px(raw, axis):
    if axis == 'x':
        return (raw & 0xFF) - 8
    else:  # y
        return (raw & 0x7F) - 8


def main():
    if len(sys.argv) < 2:
        print("Usage: parse_movement_speed.py <jzintv_output.txt>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        lines = f.readlines()

    pairs = extract_xy(lines)
    if not pairs:
        print("ERROR: no X/Y pairs found — check that probe ran correctly")
        sys.exit(1)

    print(f"Found {len(pairs)} X/Y pairs\n")

    # Expected layout: 3 baseline + 8 north + 3 stop + 8 east + 2 stop + 8 south
    # indices (0-based):
    #   0-2   baseline idle
    #   3-10  north movement
    #   11-13 stop idle
    #   14-21 east movement
    #   22-23 stop idle
    #   24-31 south movement

    SECTIONS = [
        ("baseline", 0, 3),
        ("NORTH", 3, 11),
        ("stop_1", 11, 14),
        ("EAST", 14, 22),
        ("stop_2", 22, 24),
        ("SOUTH", 24, 32),
    ]

    for name, start, end in SECTIONS:
        chunk = pairs[start:end]
        if not chunk:
            print(f"  [{name}] no data (probe may have ended early)")
            continue
        xs = [px(r, 'x') for r, _ in chunk]
        ys = [px(r, 'y') for r, _ in chunk]
        print(f"[{name}] frames {start}-{end-1}:")
        for i, (xv, yv) in enumerate(zip(xs, ys)):
            dx = (xs[i] - xs[i-1]) if i > 0 else 0
            dy = (ys[i] - ys[i-1]) if i > 0 else 0
            marker = f"  Δx={dx:+d} Δy={dy:+d}" if i > 0 else "  (first)"
            print(f"  frame {start+i}: x={xv} y={yv}{marker}")

        if len(chunk) > 1:
            dx_vals = [xs[i]-xs[i-1] for i in range(1, len(xs))]
            dy_vals = [ys[i]-ys[i-1] for i in range(1, len(ys))]
            print(f"  → avg Δx = {sum(dx_vals)/len(dx_vals):.2f}  "
                  f"avg Δy = {sum(dy_vals)/len(dy_vals):.2f}")
        print()

    print("=" * 50)
    if len(pairs) >= 32:
        north_dy = [px(pairs[i][1], 'y') - px(pairs[i-1][1], 'y') for i in range(4, 11)]
        east_dx  = [px(pairs[i][0], 'x') - px(pairs[i-1][0], 'x') for i in range(15, 22)]
        south_dy = [px(pairs[i][1], 'y') - px(pairs[i-1][1], 'y') for i in range(25, 32)]

        n_dy = sum(north_dy) / len(north_dy) if north_dy else 0
        e_dx = sum(east_dx)  / len(east_dx)  if east_dx  else 0
        s_dy = sum(south_dy) / len(south_dy) if south_dy else 0

        print(f"MOVE_SPEED estimate:")
        print(f"  North: Δy = {n_dy:.2f} px/frame  → MOVE_SPEED_Y = {abs(n_dy):.2f}")
        print(f"  East:  Δx = {e_dx:.2f} px/frame  → MOVE_SPEED_X = {abs(e_dx):.2f}")
        print(f"  South: Δy = {s_dy:.2f} px/frame  → MOVE_SPEED_Y = {abs(s_dy):.2f}")
        print()
        best = abs(n_dy) if n_dy else abs(e_dx)
        print(f"  → Recommended MOVE_SPEED = {best:.0f} (round to nearest integer)")
    else:
        print(f"Not enough data ({len(pairs)} pairs, need 32)")


if __name__ == "__main__":
    main()
