#!/usr/bin/env python3
"""
Capture jzIntv screenshots for rooms 0-5, re-render rooms,
and compare pixel-by-pixel to validate rendering accuracy.

Uses VBlank ISR breakpoint (b 5F5A) to ensure screenshots are
captured after a frame has been fully rendered by the STIC.
"""

import os
import re
import shutil
import subprocess
import sys

from PIL import Image

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_DIR)
sys.path.insert(0, '.')

from render_all_rooms import (
    decode_backtab_word,
    extract_backtab_from_output,
    extract_gram_from_output,
    extract_memory_section,
    load_grom,
    PASTEL_PALETTE,
    PALETTE,
    parse_backtab,
    parse_memory_dump,
    parse_mobs,
    render_room_image,
    SDL_ENV,
    JZINTV,
    ROM_PATH,
    GROM_PATH,
    EXEC_PATH,
)

NUM_ROOMS = 6

# -- Idle loop patches (same as render_all_rooms.py) --------------------------
IDLE_PATCHES = [
    (0x506A, 0x0034),
    (0x506B, 0x0034),
    (0x506C, 0x0034),
    (0x506D, 0x0034),
    (0x506E, 0x0034),
    (0x5318, 0x0034),
    (0x5319, 0x0034),
    (0x531A, 0x0034),
    (0x531B, 0x02B8),
    (0x531C, 0x0001),
    (0x56CC, 0x0034),
    (0x56CD, 0x0034),
]

X_FILL_MEM_NOP = [
    (0x5638, 0x0034),  # NOP the JSR R5 opcode
    (0x5639, 0x0034),  # NOP the X_FILL_MEM address
]

SPRITES_DIR = os.path.join(PROJECT_DIR, "sprites")
TRACES_DIR = os.path.join(PROJECT_DIR, "traces")


def capture_room(room_idx):
    """Run jzIntv with VBlank breakpoint, capture screenshot and memory dump.

    Returns (output_text, screenshot_path_on_disk).
    """
    # Build debugger script
    lines = []
    for addr, val in IDLE_PATCHES:
        lines.append(f"p {addr:04X} {val:04X}")
    for addr, val in X_FILL_MEM_NOP:
        lines.append(f"p {addr:04X} {val:04X}")
    # NOP the CLRR R0 + MVO R0, G_019C at boot ($55C0-$55C2) so
    # the room index isn't forced to 0.  We write the correct index below.
    # NOTE: Do NOT patch G_02F4! The game uses G_02F4 as the BASE pointer
    # ($65DC) and adds G_019C*8 internally. Patching G_02F4 causes
    # double-offset: G_02F4 + G_019C*8 = ($65DC+room*8) + room*8 → wrong data!
    lines.append("p 55C0 0034")
    lines.append("p 55C1 0034")
    lines.append("p 55C2 0034")
    # Break after X_FILL_ZERO at $5035-$5036 returns to $5038.
    # X_FILL_ZERO zeros $0102-$01EF which INCLUDES G_019C and G_018C.
    # We MUST write them AFTER the zero-fill, not before boot.
    lines.append("b 5038")          # break at SDBD right after JSR returns
    lines.append("r 8000000")       # run through boot + X_FILL_ZERO
    # Now write G_019C (room index) and G_018C (force 1-player start)
    # NOTE: 'p' (patch) writes memory; 'w' sets watchpoints — they're different!
    lines.append(f"p 019C {room_idx:04X}")
    lines.append("p 018C 0001")
    lines.append("b 5F5A")          # break at end of L_5F43 (VBlank render complete)
    lines.append("r 8000000")       # run until breakpoint fires
    lines.append("vs")              # take screenshot AFTER frame rendered
    lines.append("m 0200 240")      # dump BACKTAB
    lines.append("m 3800 512")      # dump GRAM
    lines.append("m 0300 96")       # dump SYSRAM MOB shadow
    lines.append("q")

    script_path = os.path.join(TRACES_DIR, f"_cmp_room_{room_idx}.txt")
    with open(script_path, 'w') as f:
        f.write('\n'.join(lines))

    output_path = os.path.join(TRACES_DIR, f"_cmp_room_{room_idx}_out.txt")

    # Record existing screenshot files BEFORE running jzIntv
    before = set(
        name for name in os.listdir(PROJECT_DIR)
        if name.startswith('shot') and name.endswith('.gif')
    )

    print(f"    Running jzintv (headless) for room {room_idx} ...", end='', flush=True)
    with open(output_path, 'w', encoding='utf-8', errors='replace') as out_f:
        proc = subprocess.Popen(
            [JZINTV, '-d', f'--script={script_path}',
             '-e', EXEC_PATH, '-g', GROM_PATH, ROM_PATH],
            stdout=out_f,
            stderr=subprocess.STDOUT,
            env=SDL_ENV,
            cwd=PROJECT_DIR,
        )
        try:
            proc.wait(timeout=300)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            print(" TIMEOUT", flush=True)
        else:
            print(" done", flush=True)

    # Find NEW screenshot by differencing before/after file listings.
    # This avoids grabbing a stale file from a previous failed cleanup.
    import time
    screenshot_path = None
    for _ in range(20):  # retry for up to 10 seconds
        after = set(
            name for name in os.listdir(PROJECT_DIR)
            if name.startswith('shot') and name.endswith('.gif')
        )
        new_files = after - before
        if new_files:
            new_name = new_files.pop()
            src = os.path.join(PROJECT_DIR, new_name)
            dest = os.path.join(SPRITES_DIR, f"room_{room_idx}_jzintv.gif")
            try:
                shutil.move(src, dest)
                screenshot_path = dest
            except (PermissionError, OSError):
                time.sleep(0.5)
                continue
            break
        time.sleep(0.5)

    if screenshot_path is None:
        print(f"    WARNING: No new screenshot for room {room_idx}")

    with open(output_path, 'r', encoding='utf-8', errors='replace') as f:
        output = f.read()

    return output, screenshot_path


def downsample_to_native(img, zoom=4):
    """Downsample a zoomed render to native STIC resolution (160x96).

    Takes top-left pixel of each zoom block (nearest-neighbor equivalent).
    """
    native_w = img.width // zoom
    native_h = img.height // zoom
    result = Image.new('RGB', (native_w, native_h))
    for y in range(native_h):
        for x in range(native_w):
            result.putpixel((x, y), img.getpixel((x * zoom, y * zoom)))
    return result


def extract_dungeon_from_screenshot(scr_path):
    """Extract the 160x96 STIC display area from a 320x200 jzIntv screenshot.

    jzIntv centers the STIC output in the window.  We scan for the edges
    of non-black pixels to find the exact bounds, with sane fallbacks.
    """
    scr = Image.open(scr_path)
    scr_px = scr.load()

    # Find left edge: first column that has non-zero palette indices
    left = None
    for x in range(scr.width):
        for y in range(scr.height):
            if scr_px[x, y] != 0:
                left = x
                break
        if left is not None:
            break

    # Find top edge
    top = None
    for y in range(scr.height):
        for x in range(scr.width):
            if scr_px[x, y] != 0:
                top = y
                break
        if top is not None:
            break

    if left is None or top is None:
        # Empirical defaults for standard jzIntv 320x200 window
        left, top = 80, 52

    # Clamp crop bounds
    crop_w = min(160, scr.width - left)
    crop_h = min(96, scr.height - top)
    dungeon = scr.crop((left, top, left + crop_w, top + crop_h))
    return dungeon, scr, left, top


def compare_pixels(our_native, jz_dungeon, jz_pal):
    """Pixel-by-pixel RGB comparison.

    Returns (match_count, total, our_colors_dict, jz_colors_dict, mismatch_dict).
    """
    # Pre-build jzIntv RGB lookup from GIF palette
    def jz_rgb(idx):
        if jz_pal and idx * 3 + 2 < len(jz_pal):
            return (jz_pal[idx * 3], jz_pal[idx * 3 + 1], jz_pal[idx * 3 + 2])
        return (0, 0, 0)

    total = 0
    match = 0
    our_colors = {}
    jz_colors = {}
    mismatches = {}

    max_y = min(our_native.height, jz_dungeon.height)
    max_x = min(our_native.width, jz_dungeon.width)

    for y in range(max_y):
        for x in range(max_x):
            our_rgb = our_native.getpixel((x, y))
            jz_rgb_val = jz_rgb(jz_dungeon.getpixel((x, y)))

            our_colors[our_rgb] = our_colors.get(our_rgb, 0) + 1
            jz_colors[jz_rgb_val] = jz_colors.get(jz_rgb_val, 0) + 1

            if our_rgb == jz_rgb_val:
                match += 1
            else:
                key = (our_rgb, jz_rgb_val)
                mismatches[key] = mismatches.get(key, 0) + 1

            total += 1

    return match, total, our_colors, jz_colors, mismatches


def color_name(rgb):
    """Return a human-readable name for a palette colour."""
    for d, label in [(PALETTE, "PAL"), (PASTEL_PALETTE, "PAS")]:
        for k, v in d.items():
            if v == rgb:
                return f"{label}[{k}]"
    if rgb == (0, 0, 0):
        return "black"
    return ""


def main():
    os.makedirs(TRACES_DIR, exist_ok=True)
    os.makedirs(SPRITES_DIR, exist_ok=True)

    grom = load_grom()
    print(f"GROM loaded: {len(grom)} bytes")

    results = []

    for room_idx in range(NUM_ROOMS):
        print(f"\n{'=' * 60}")
        print(f"  ROOM {room_idx}")
        print(f"{'=' * 60}")

        # 1 - Capture screenshot + memory dump -------------------------
        output, scr_path = capture_room(room_idx)

        if not scr_path:
            print(f"  SKIP: no screenshot captured")
            continue

        # 2 - Parse memory data -----------------------------------------
        backtab_text = extract_backtab_from_output(output)
        if not backtab_text:
            print(f"  SKIP: no BACKTAB in output")
            continue

        backtab_grid = parse_backtab(backtab_text)
        gram_text = extract_gram_from_output(output)
        gram_mem = parse_memory_dump(gram_text, 0x3800, 512) if gram_text else {}
        sysram_text = extract_memory_section(output, 0x0300, 0x0360)
        mobs = parse_mobs(sysram_text) if sysram_text else []

        # Quick stats
        unique_cards = set()
        for row in range(12):
            for col in range(20):
                card, fg, bg_bits, is_gram, fg_transparent = decode_backtab_word(backtab_grid[row][col])
                unique_cards.add((card, is_gram))
        print(f"    BACKTAB: {len(unique_cards)} unique cards, MOBs: {len(mobs)}")

        # 3 - Render with our engine -----------------------------------
        # The game uses standard Color Stack mode. Proof: pastel backgrounds
        # appear in jzIntv screenshots, and FG/BG mode cannot produce
        # pastel-colored backgrounds (BG is limited to primary 0-7).
        # All 4 CS registers are set to pastel tan by EXEC.730 at boot.
        # FG colors are from bits 15/14/12 (primary only 0-7 in CS mode).
        room_img = render_room_image(
            backtab_grid, gram_mem, grom,
            color_stack=None,  # defaults to [pastel tan] * 4
            zoom=4,
            mobs=mobs,
            use_fgbg=False,  # standard Color Stack mode
        )
        room_path = os.path.join(SPRITES_DIR, f"dungeon_room_{room_idx}.png")
        room_img.save(room_path)

        # 4 - Extract dungeon from screenshot ---------------------------
        jz_dungeon, jz_full, dungeon_left, dungeon_top = extract_dungeon_from_screenshot(scr_path)
        jz_pal = jz_full.getpalette()

        print(f"    jzIntv screenshot: {jz_full.size[0]}x{jz_full.size[1]}")
        print(f"    Dungeon bounds: ({dungeon_left},{dungeon_top}) -> "
              f"({dungeon_left + jz_dungeon.width},{dungeon_top + jz_dungeon.height})")

        # 5 - Compare pixel-by-pixel -----------------------------------
        our_native = downsample_to_native(room_img)
        match, total, our_cols, jz_cols, mismatches = compare_pixels(
            our_native, jz_dungeon, jz_pal
        )

        pct = 100.0 * match / total if total > 0 else 0.0

        print(f"\n    --- Pixel Comparison ---")
        print(f"    Match: {match:,} / {total:,} = {pct:.1f}%")

        print(f"\n    Our color distribution:")
        for c, n in sorted(our_cols.items(), key=lambda x: -x[1])[:6]:
            name = color_name(c)
            pct_str = f"({100*n/total:.1f}%)"
            print(f"      {str(c):20s} {name:12s} {n:6d}  {pct_str}")

        print(f"\n    jzIntv color distribution:")
        for c, n in sorted(jz_cols.items(), key=lambda x: -x[1])[:6]:
            name = color_name(c)
            pct_str = f"({100*n/total:.1f}%)"
            print(f"      {str(c):20s} {name:12s} {n:6d}  {pct_str}")

        print(f"\n    Top 5 mismatches (our RGB -> jzIntv RGB):")
        for (our, jz), n in sorted(mismatches.items(), key=lambda x: -x[1])[:5]:
            our_n = color_name(our)
            jz_n = color_name(jz)
            print(f"      {str(our):20s} {our_n:12s} -> {str(jz):20s} {jz_n:12s}  {n:5d} px")

        # Screenshot already saved by capture_room() as _room_N_jzintv.gif
        # Copy to final reference path
        ref_path = os.path.join(SPRITES_DIR, f"room_{room_idx}_jzintv.gif")
        try:
            shutil.copy(scr_path, ref_path)
        except (OSError, PermissionError):
            pass

        results.append((room_idx, pct, match, total, our_cols, jz_cols))

    # -- Summary -------------------------------------------------------
    print(f"\n{'=' * 60}")
    print(f"  SUMMARY")
    print(f"{'=' * 60}")
    for room_idx, pct, match, total, _, _ in results:
        bar = '#' * int(pct / 5) + '.' * (20 - int(pct / 5))
        print(f"  Room {room_idx}: {pct:5.1f}%  {bar}  ({match}/{total})")

    if results:
        avg = sum(r[1] for r in results) / len(results)
        print(f"\n  Average: {avg:.1f}% across {len(results)} rooms")
        if avg >= 90:
            print(f"  Verdict: Excellent match!")
        elif avg >= 75:
            print(f"  Verdict: Good match # minor discrepancies remain")
        elif avg >= 50:
            print(f"  Verdict: Partial match # significant differences")
        else:
            print(f"  Verdict: Poor match # fundamental issues remain")

    print()


if __name__ == '__main__':
    main()
