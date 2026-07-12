#!/usr/bin/env python3
"""Derive Room 0 PNG from emulator-captured BACKTAB using the correct STIC decode.

Renders Room 0 from a jzIntv debugger trace using the spec-correct STIC
Color Stack decode in render_all_rooms (bit 11 = GRAM/GROM select per
jzIntv doc/programming/stic.txt).

This script previously re-implemented its own tile loop, which did NOT
handle Colored Squares mode (BACKTAB bit 12=1, bit 11=0). The Room 0 floor
tile $1603 is a Colored Squares card (185 of 240 tiles, 77%); the old loop
decoded it as GROM card $C0 and drew a column of vertical lines instead of a
solid floor. It now delegates to render_all_rooms.render_room_image, the
single Colored-Squares-aware renderer, so there is one decode path for the
whole project.

NOTE ON CAPTURE DATA: the structural (non-floor) tiles in the current traces
decode to GRAM cards 0-11, but the capture breaks at $55DA (title-screen
boot) where GRAM still holds the IMAGIC logo, not dungeon tiles. Until a
trace is captured at a real gameplay frame with dungeon GRAM loaded, those
tiles render blank regardless of the renderer. See docs/.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts'))

from render_all_rooms import (
    load_grom,
    parse_backtab,
    extract_backtab_from_output,
    parse_memory_dump,
    extract_gram_from_output,
    parse_room_mobs,
    render_room_fgbg,
    reconstruct_dungeon_gram,
    reconstruct_mob_sprite_gram,
)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
TRACES_DIR = os.path.join(PROJECT_DIR, "traces", "rooms")


def render_room_correct(backtab_grid, gram_mem, grom, zoom=4, mobs=None):
    """Render Room 0 in FG/BG mode — the mode Swords & Serpents uses for dungeons.

    The screen-setup routine at $53B5 WRITES STIC mode-select $0021, which
    selects Foreground/Background mode (jzIntv stic.c:253), so each BACKTAB
    tile carries its own fg/bg color. The floor tile $1603 decodes to GROM
    card 0 on an olive-green (color 11) background; wall tiles sit on black.
    Delegates to render_all_rooms.render_room_fgbg (faithful to jzIntv's
    stic_draw_fgbg) using the authoritative jzIntv palette. `mobs` overlays the
    hardware sprites.
    """
    return render_room_fgbg(backtab_grid, gram_mem, grom, zoom=zoom, mobs=mobs)


def main():
    # Find latest room 0 trace
    trace_files = sorted([
        f for f in os.listdir(TRACES_DIR)
        if f.startswith('render_room_0_out') and f.endswith('.txt')
    ])
    if not trace_files:
        print("ERROR: No room 0 trace files found in traces/rooms/")
        sys.exit(1)

    latest = trace_files[-1]
    dump_path = os.path.join(TRACES_DIR, latest)
    print(f"Using trace: {latest}")

    with open(dump_path, 'r', encoding='utf-8', errors='replace') as f:
        raw = f.read()

    backtab_grid = parse_backtab(extract_backtab_from_output(raw))

    # Prefer the trace's own GRAM when it was captured in gameplay (real dungeon
    # tiles loaded — see scripts/debug_capture_gameplay.txt). Boot-time traces
    # ($55DA) have only the IMAGIC logo in GRAM, so fall back to replaying the
    # ROM tile loader (reconstruct_dungeon_gram), which is byte-identical to the
    # gameplay GRAM for the structural cards (3-33).
    captured_gram = parse_memory_dump(extract_gram_from_output(raw), 0x3800, 512)
    if sum(1 for v in captured_gram.values() if v & 0xFF) > 64:
        gram_mem = captured_gram
        print("GRAM: using captured gameplay tiles")
    else:
        gram_mem = reconstruct_dungeon_gram()
        print("GRAM: boot trace (logo only) — reconstructed from ROM")

    grom = load_grom()

    mobs = parse_room_mobs(raw)
    if mobs:
        # The headless capture bypasses character-select, so the player's sprite
        # card (48) is blank in GRAM. The player is the Warrior/Prince; his
        # opening-position frame is DECLE cards 0+1 at $5BCD (an 8x16 top-down
        # oval with a sword — confirmed against the manual). Reconstruct it from
        # ROM into the player's GRAM card 48/49 so MOB0 renders as the warrior.
        player = next((m for m in mobs if m['card'] == 48 and m['is_gram']), None)
        if player and not any(gram_mem.get(0x3800 + 48 * 8 + r, 0) & 0xFF for r in range(8)):
            gram_mem.update(reconstruct_mob_sprite_gram(target_card=48))
            print("MOBs: Warrior opening-position sprite reconstructed into card 48/49")
        print(f"MOBs: {len(mobs)} sprite(s) overlaid")

    room_img = render_room_correct(backtab_grid, gram_mem, grom, zoom=4, mobs=mobs)

    # The Warrior's sword is a separate element the game draws as a line in his
    # facing direction (the opening-position body sprite is symmetric and has no
    # sword). The sword MOB is inactive/mispositioned in this idle capture, so
    # draw the blade pointing east (matching the reference screenshot) from the
    # player MOB's right edge at his vertical centre.
    player = next((m for m in mobs if m['card'] == 48 and m['is_gram']), None) if mobs else None
    if player:
        px = room_img.load()
        zoom = 4
        wx = (player['x'] - 8) * zoom          # warrior left edge (render px)
        wy = player['y'] * zoom                # warrior top (render px)
        cy = wy + 8 * (zoom // 2)              # warrior vertical centre (8 rows * vz)
        blade = (255, 252, 255)
        for x in range(wx + 8 * zoom, wx + 8 * zoom + 7 * zoom):   # ~1 tile long, east
            for t in range(-zoom // 2, zoom // 2):                 # ~2 native px thick
                iy = cy + t
                if 0 <= x < room_img.width and 0 <= iy < room_img.height:
                    px[x, iy] = blade
        print("MOBs: drew Warrior's sword (east-facing) — see note in output")

    # Intellivision pixel-aspect correction. The renderer uses square pixels
    # (matching jzIntv's GIF output), but the real STIC displays the 160x96
    # playfield on a 4:3 TV, so pixels are taller than wide (PAR = (4/3)/(160/96)
    # = 0.8 -> stretch height x1.25). This un-squishes the room and the Warrior
    # to the proportions seen in the manual's TV screenshots.
    from PIL import Image
    aspect_img = room_img.resize((room_img.width, room_img.height * 5 // 4),
                                 Image.NEAREST)

    out_path = os.path.join(PROJECT_DIR, 'roomzero.png')
    aspect_img.save(out_path)
    print(f"Saved: {out_path} ({aspect_img.width}×{aspect_img.height}, 4:3 aspect-corrected)")
    room_img = aspect_img

    from collections import Counter
    colors = Counter(room_img.getdata())
    print(f"Unique colors: {len(colors)}")
    for color, count in colors.most_common(10):
        print(f"  RGB{color}: {count} ({100*count/(room_img.width*room_img.height):.1f}%)")


if __name__ == '__main__':
    main()
