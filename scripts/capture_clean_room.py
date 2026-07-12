#!/usr/bin/env python3
"""Capture a clean room trace without breaking GRAM initialization.

The GRAM init loop at $5318-$531C must run normally for custom dungeon tiles
to load. We only patch idle loops and the boot room parameters.
"""
import os
import sys
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from render_all_rooms import (
    parse_memory_dump, parse_backtab, parse_color_stack,
    extract_backtab_from_output, extract_gram_from_output,
    extract_color_stack_from_output, decode_backtab_word,
    load_grom, get_grom_card_bytes, PALETTE, PASTEL_PALETTE,
)
from PIL import Image

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROM_PATH = os.path.join(PROJECT_DIR, "Swords and Serpents.bin")
GROM_PATH = os.path.join(PROJECT_DIR, "grom.bin")
EXEC_PATH = os.path.join(PROJECT_DIR, "exec.bin")
JZINTV = os.path.join(PROJECT_DIR, "jzintv-20200712-win32-sdl2", "bin", "jzintv.exe")
TRACES_DIR = os.path.join(PROJECT_DIR, "traces", "rooms")
ROOMS_DIR = os.path.join(PROJECT_DIR, "sprites", "rooms")

SDL_ENV = os.environ.copy()
SDL_ENV["SDL_VIDEODRIVER"] = "dummy"
SDL_ENV["SDL_AUDIODRIVER"] = "dummy"

# Room parameter table at $5A17 (used by L_59FF in gameplay).
ROOM_PARAMS = [
    (0x0062, 0x000B),   # room 0
    (0x000C, 0x001A),   # room 1
    (0x001B, 0x001C),   # room 2
    (0x0062, 0x0004),   # room 3
]


def generate_clean_script(room_index, output_path):
    """Generate debugger script without GRAM-breaking patches."""
    lines = []
    lines.append(f"; Clean script for room {room_index}")
    lines.append("")

    # Only patch boot idle loops (NOT GRAM init)
    idle_patches = [
        (0x506A, 0x0034),  # NOP idle loops
        (0x506B, 0x0034),
        (0x506C, 0x0034),
        (0x506D, 0x0034),
        (0x506E, 0x0034),
        (0x56CC, 0x0034),  # NOP title screen idle check
        (0x56CD, 0x0034),
    ]
    for addr, val in idle_patches:
        lines.append(f"p {addr:04X} {val:04X}")
    lines.append("")

    # NOP CLRR + MVO G_019C at boot so we can set it ourselves
    lines.append("p 55C0 0034")
    lines.append("p 55C1 0034")
    lines.append("p 55C2 0034")
    lines.append("")

    # Patch boot room params
    g175, g176 = ROOM_PARAMS[room_index]
    lines.append(f"; Room {room_index}: G_0175=${g175:04X}, G_0176=${g176:04X}")
    lines.append("p 55CF 02B8")
    lines.append(f"p 55D0 {g175:04X}")
    lines.append("p 55D3 02B8")
    lines.append(f"p 55D4 {g176:04X}")
    lines.append("")

    # Break after X_FILL_ZERO returns ($5038)
    lines.append("b 5038")
    lines.append("r 8000000")
    lines.append("")

    # Write room index
    lines.append(f"p 019C {room_index:04X}")
    lines.append("")

    # Break after L_5EE2 room renderer returns ($55DA)
    lines.append("b 55DA")
    lines.append("r 8000000")
    lines.append("")

    # Dumps
    lines.append("m 0200 240")
    lines.append("m 3800 512")
    lines.append("m 0028 4")
    lines.append("m 0300 96")
    lines.append("q")

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    print(f"Generated: {output_path}")


def run_jzintv(script_path, output_path):
    cmd = [
        JZINTV, "-d",
        f"--script={script_path}",
        "-e", EXEC_PATH,
        "-g", GROM_PATH,
        ROM_PATH,
    ]
    print(f"Running jzIntv for {os.path.basename(script_path)} ...")

    startupinfo = None
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0

    try:
        with open(output_path, 'w', encoding='utf-8', errors='replace') as out_f:
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
                print("TIMEOUT after 300s")
                return ""

        with open(output_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception as e:
        print(f"ERROR: {e}")
        return ""


def render_room_from_trace(room_index, trace_path, out_path, zoom=8):
    with open(trace_path, 'r', encoding='utf-8', errors='replace') as f:
        raw = f.read()

    backtab_grid = parse_backtab(extract_backtab_from_output(raw))
    gram_text = extract_gram_from_output(raw)
    gram_mem = parse_memory_dump(gram_text, 0x3800, 512) if gram_text else {}
    cs_text = extract_color_stack_from_output(raw)
    color_stack = parse_color_stack(cs_text) if cs_text else None
    grom = load_grom()

    # Diagnostic: check GRAM validity
    gram_nonzero = sum(1 for v in gram_mem.values() if v != 0)
    print(f"  GRAM nonzero words: {gram_nonzero}/{len(gram_mem)}")

    # Collect card usage
    used_cards = set()
    for r in range(12):
        for c in range(20):
            card, fg, _, is_gram, _ = decode_backtab_word(backtab_grid[r][c])
            used_cards.add((card, is_gram))
    print(f"  Unique tiles: {len(used_cards)}")
    for card, is_gram in sorted(used_cards):
        src = "GRAM" if is_gram else "GROM"
        if is_gram:
            base = 0x3800 + card * 8
            nz = sum(1 for i in range(8) if gram_mem.get(base + i, 0) != 0)
            print(f"    {src} card {card:3d}: nonzero={nz}")
        else:
            b = get_grom_card_bytes(grom, card)
            nz = sum(1 for x in b if x != 0)
            print(f"    {src} card {card:3d}: nonzero={nz}")

    cols, rows = 20, 12
    tile_size = 8
    img_w = cols * tile_size * zoom
    img_h = rows * tile_size * zoom
    img = Image.new('RGB', (img_w, img_h))
    px = img.load()

    if color_stack is None or len(color_stack) < 4:
        color_stack = [PASTEL_PALETTE[3]] * 4

    cs_index = 0
    for row in range(rows):
        for col in range(cols):
            word = backtab_grid[row][col]
            card_idx, fg_color_idx, _, is_gram, _ = decode_backtab_word(word)
            advance = (word >> 13) & 1
            cs_index = (cs_index + advance) % 4
            bg = color_stack[cs_index]
            fg = PALETTE.get(fg_color_idx, (255, 0, 255))

            if is_gram:
                base = 0x3800 + card_idx * 8
                card_bytes = bytes(gram_mem.get(base + r, 0) & 0xFF for r in range(8))
            else:
                card_bytes = get_grom_card_bytes(grom, card_idx)

            for y in range(8):
                byte_val = card_bytes[y]
                for x in range(8):
                    bit = (byte_val >> (7 - x)) & 1
                    rgb = fg if bit else bg
                    for dy in range(zoom):
                        for dx in range(zoom):
                            px_x = col * tile_size * zoom + x * zoom + dx
                            px_y = row * tile_size * zoom + y * zoom + dy
                            px[px_x, px_y] = rgb

    img.save(out_path)
    print(f"Saved: {out_path} ({img.width}x{img.height})")
    return img


def main():
    if len(sys.argv) < 2:
        print("Usage: python capture_clean_room.py <room_number>")
        sys.exit(1)

    room_index = int(sys.argv[1])
    os.makedirs(TRACES_DIR, exist_ok=True)
    os.makedirs(ROOMS_DIR, exist_ok=True)

    script_path = os.path.join(TRACES_DIR, f"clean_room_{room_index}.txt")
    trace_path = os.path.join(TRACES_DIR, f"clean_room_{room_index}_out.txt")
    out_path = os.path.join(ROOMS_DIR, f"room_{room_index}.png")

    generate_clean_script(room_index, script_path)
    output = run_jzintv(script_path, trace_path)
    if not output:
        print("Failed to capture trace")
        sys.exit(1)

    # Render using render_all_rooms.render_room_image but with colored squares disabled
    import render_all_rooms as rar
    # Monkey-patch: never treat tiles as colored squares (that was causing solid bg)
    rar.is_colored_squares = lambda word: False

    with open(trace_path, 'r', encoding='utf-8', errors='replace') as f:
        raw = f.read()

    backtab_grid = rar.parse_backtab(rar.extract_backtab_from_output(raw))
    gram_text = rar.extract_gram_from_output(raw)
    gram_mem = rar.parse_memory_dump(gram_text, 0x3800, 512) if gram_text else {}
    cs_text = rar.extract_color_stack_from_output(raw)
    color_stack = rar.parse_color_stack(cs_text) if cs_text else None
    sysram_text = rar.extract_memory_section(raw, 0x0300, 0x0360)
    mobs = rar.parse_mobs(sysram_text) if sysram_text else []
    grom = rar.load_grom()

    # Diagnostics
    gram_nonzero = sum(1 for v in gram_mem.values() if v != 0)
    print(f"  GRAM nonzero words: {gram_nonzero}/{len(gram_mem)}")
    print(f"  MOBs parsed: {len(mobs)}")
    for mob in mobs:
        print(f"    MOB{mob['mob_idx']}: x={mob['x']} y={mob['y']} card={mob['card']} gram={mob['is_gram']} visible={mob['visible']}")

    room_img = rar.render_room_image(backtab_grid, gram_mem, grom,
                                     color_stack=color_stack, zoom=8, mobs=mobs)
    room_img.save(out_path)
    print(f"Saved: {out_path} ({room_img.width}x{room_img.height})")

    # Color stats
    px = room_img.load()
    colors = {}
    for y in range(room_img.height):
        for x in range(room_img.width):
            c = px[x,y]
            colors[c] = colors.get(c, 0) + 1
    print(f"  Unique colors: {len(colors)}")
    for c, cnt in sorted(colors.items(), key=lambda x: -x[1])[:10]:
        pct = 100 * cnt / (room_img.width * room_img.height)
        print(f"    RGB{c}: {cnt:,} ({pct:.1f}%)")


if __name__ == '__main__':
    main()
