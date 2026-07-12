#!/usr/bin/env python3
"""
Swords & Serpents — All Rooms Renderer
Generates jzIntv debugger scripts for rooms 0-5, runs them all,
parses BACKTAB+GRAM dumps, and renders all rooms.
"""
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from PIL import Image

# from versioning import next_versioned_path

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ROM_PATH = os.path.join(PROJECT_DIR, "Swords and Serpents.bin")
GROM_PATH = os.path.join(PROJECT_DIR, "grom.bin")
EXEC_PATH = os.path.join(PROJECT_DIR, "exec.bin")
JZINTV = os.path.join(PROJECT_DIR, "jzintv-20200712-win32-sdl2", "bin", "jzintv.exe")
TRACES_DIR = os.path.join(PROJECT_DIR, "traces", "rooms")
ROOMS_DIR = os.path.join(PROJECT_DIR, "sprites", "rooms")

NUM_ROOMS = 4  # Swords & Serpents only has 4 dungeon levels (0-3)

# IMPORTANT: G_0175 and G_0176 are hardcoded at boot ($55CF-$55D5) as 2 and 26.
# These values are correct for the initial renderer — DO NOT patch them.
# The per-room variation comes solely from G_02F4 (data pointer offset).
# The L_59FF function only runs on ROOM TRANSITIONS, not initial boot.

# Force headless SDL — critical for subprocess capture
SDL_ENV = os.environ.copy()
SDL_ENV["SDL_VIDEODRIVER"] = "dummy"
SDL_ENV["SDL_AUDIODRIVER"] = "dummy"

# -- Intellivision palette --------------------------------------------------
# Colors matched to jzIntv's actual RGB palette from screenshot comparison.
# jzIntv GIF palette indices 0-7 map to Intellivision primary colors 0-7.
PALETTE = {
    0:  (0, 0, 0),           # black
    1:  (20, 56, 247),       # blue
    2:  (227, 91, 14),       # red
    3:  (203, 241, 104),     # tan
    4:  (0, 148, 40),        # dark green
    5:  (7, 194, 0),         # green
    6:  (255, 255, 1),       # yellow
    7:  (255, 255, 255),     # white
}

# jzIntv pastel palette (indices 8-15, color idx = (8 + base_color_idx)).
# These values are DIRECTLY from jzIntv's actual output, verified by
# pixel-level analysis of the jzIntv reference GIF (room_0_jzintv.gif).
# The ECS/Hardware YUV-derived palettes found online are INCORRECT for
# jzIntv's actual rendering.
PASTEL_PALETTE = {
    0:  (200, 200, 200),     # pastel black (light gray)
    1:  (35, 206, 195),      # pastel blue (light cyan)
    2:  (253, 153, 24),       # pastel red (orange)
    3:  (58, 138, 0),         # pastel tan (dark olive green) — verified from jzIntv GIF
    4:  (240, 70, 60),        # pastel dark green (pinkish red)
    5:  (211, 131, 255),      # pastel green (lavender)
    6:  (72, 246, 1),         # pastel yellow (bright green)
    7:  (184, 17, 120),       # pastel white (magenta)
}
DEFAULT_BG = (0, 0, 0)

# -- Empirical BACKTAB rendering data --------------------------------------
# Derived from per-pixel analysis of jzIntv reference GIF (room 0 playfield).
# Each unique BACKTAB word was analyzed by sampling actual bit=0 and bit=1
# pixel colors from the jzIntv screenshot, excluding blue emulator overlay.
#
# LIMITATION: For tiles where blue overlay covers ALL foreground (card bit=1)
# pixels, the analysis cannot determine the true FG color. These tiles are
# flagged in EMPIRICAL_FG with manually verified FG values from card analysis.

# Per-word background color overrides (RGB tuples).
# For words where the background (card bit=0) pixel color in jzIntv differs
# from the default Color Stack entry (pastel tan = PAS[3]). These override the
# CS background color for ALL pixels of transparent words, and for bit=0
# pixels of opaque words.
# Empirical overrides DISABLED: they were derived from an incorrect BACKTAB
# bit decode (card = word & 0x7FF, fg = bits 15/14/12). With the corrected
# decode (card = bits 3-10, fg = bits 0-2), the same words map to different
# cards and foreground colors, making these overrides produce garbage.
# Re-derive empirically from clean jzIntv screenshots if needed.
EMPIRICAL_BG_COLOR = {}
EMPIRICAL_FG = {}
EMPIRICAL_TRANSPARENT = {}

# Per-pixel color tables for complex tiles that don't follow simple 1bpp.
# These words bypass the normal Color Stack + card bitmap pipeline.
EMPIRICAL_PER_PIXEL = {}


# -- MOB foreground color (derived from cartridge border extension) ---------
# The STIC border color register ($002C) controls both the screen border
# color AND the MOB foreground color. Bits 0-2 = color index, bit 3 = pastel.
# The EXEC ROM sets the initial border color from the border extension byte
# at cartridge header $500D during boot. Swords & Serpents never overrides
# STIC.BORD during gameplay, so the EXEC default applies throughout.

# Read border extension from ROM $500D.
# Swords and Serpents.bin has 0x00 padding at every even byte position.
# We must de-interleave by extracting odd-positioned bytes.
def _read_border_extension():
    try:
        with open(ROM_PATH, 'rb') as f:
            data = f.read()
        # De-interleave: odd-positioned bytes (1, 3, 5, ...) contain real ROM data
        rom = bytes(data[i] for i in range(1, len(data), 2))
        if len(rom) > 0x0D:
            return rom[0x0D]
    except Exception:
        pass
    return 0x0F  # default: pastel white

_BORDER_EXT = _read_border_extension()
_MOB_COLOR_IDX = _BORDER_EXT & 0x7
_MOB_IS_PASTEL = (_BORDER_EXT & 0x8) != 0

# Empirically verified via jzIntv screenshot (shot0001.gif):
# MOB pixels appear as jzIntv palette index 7 = RGB(255,255,255) = plain white.
# The border extension byte at ROM $500D is $0F (color 7 + pastel bit),
# but jzIntv renders MOBs as primary white, not pastel white (200,200,200).
# This is because the STIC applies MOB foreground color as the border color
# WITHOUT the pastel bit in hardware (pastel only affects the border display).
MOB_FG_COLOR = PALETTE.get(_MOB_COLOR_IDX, (255, 255, 255))



# -- Idle loop patches (speed through title/boot) --------------------------
IDLE_PATCHES = [
    (0x506A, 0x0034),  # NOP idle loops
    (0x506B, 0x0034),
    (0x506C, 0x0034),
    (0x506D, 0x0034),
    (0x506E, 0x0034),
    (0x5318, 0x0034),  # GRAM init loop patches
    (0x5319, 0x0034),
    (0x531A, 0x0034),
    (0x531B, 0x02B8),
    (0x531C, 0x0001),
    (0x56CC, 0x0034),  # NOP title screen idle check (BEQ at $56CC)
    (0x56CD, 0x0034),
]

# BREAKPOINT at $55DA captures BACKTAB immediately after L_5EE2
# (the room renderer) returns, BEFORE the title screen code at L_55DB
# wipes it with X_FILL_MEM. This yields the clean pre-title-screen
# dungeon render — no need to NOP the wipe or spoof G_018C.
X_FILL_MEM_NOP = []


def generate_debugger_script(room_index, output_path, include_vs=False, skip_gram_patches=False):
    """
    Generate a jzIntv debugger script that:
    1. Patches idle loops for speed
    2. Breaks after X_FILL_ZERO at $5038, writes G_019C=room_index
    3. Sets a breakpoint at $55DA (right after JSR R5, L_5EE2 returns)
    4. Runs until $55DA and dumps BACKTAB + GRAM

    STRATEGY: L_5EE2 at $5EE2 is the actual room renderer. At boot, the
    game calls it via JSR at $55D7. It reads room data and writes 240 words
    to BACKTAB. Immediately after it returns to $55DA, the title screen
    code (L_55DB) wipes BACKTAB with X_FILL_MEM. We break EXACTLY at
    $55DA — after the dungeon is fully rendered but before the wipe —
    capturing perfectly clean room data without any title screen remnants.

    Args:
        include_vs: If True, append a 'vs' command after hitting the
                    breakpoint to capture a clean framebuffer screenshot
                    before the memory dumps.
        skip_gram_patches: If True, do NOT patch the GRAM init loop at
                    $5318-$531C.  This makes boot ~1s slower but leaves
                    GRAM properly initialized so the pure BACKTAB renderer
                    can draw custom wall/floor tiles instead of blank cards.
    """
    lines = []
    lines.append(f"; Auto-generated script for room {room_index}")
    lines.append(f";   Strategy: break at $55DA after L_5EE2 room renderer")
    if skip_gram_patches:
        lines.append(";   GRAM init preserved (custom tiles will render)")
    else:
        lines.append(";   GRAM init skipped for speed (boot ~1s faster)")
    lines.append("")

    # Idle patches
    for addr, val in IDLE_PATCHES:
        if skip_gram_patches and 0x5318 <= addr <= 0x531C:
            continue
        lines.append(f"p {addr:04X} {val:04X}")
    lines.append("")

    # NOP the CLRR R0 + MVO R0, G_019C at boot ($55C0-$55C2).
    lines.append("; NOP CLRR + MVO G_019C at boot")
    lines.append("p 55C0 0034")
    lines.append("p 55C1 0034")
    lines.append("p 55C2 0034")
    lines.append("")

    # Patch the boot hardcoded G_0175/G_0176 values ($55CF-$55D6).
    # The game hardcodes G_0175=2, G_0176=$1A for the title screen.
    # We patch these to the room-specific values so L_5EE2 renders
    # the actual dungeon room instead of the title screen background.
    # Room parameter table at $5A17 (used by L_59FF in gameplay).
    # The table only contains 4 valid room-type entries; indices >= 4
    # read into the code stream at $5A1F (not real room data).
    #   Room 0: index 0,1  -> G_0175=$0062, G_0176=$000B
    #   Room 1: index 4,5  -> G_0175=$000C, G_0176=$001A
    #   Room 2: index 8,9  -> G_0175=$001B, G_0176=$001C
    #   Room 3: index 12,13-> G_0175=$0062, G_0176=$0004
    # For rooms 4-5 we recycle rooms 0-1 (the game may only have 4 room types).
    ROOM_PARAMS = [
        (0x0062, 0x000B),   # room 0
        (0x000C, 0x001A),   # room 1
        (0x001B, 0x001C),   # room 2
        (0x0062, 0x0004),   # room 3
        (0x0062, 0x000B),   # room 4  (recycle room 0)
        (0x000C, 0x001A),   # room 5  (recycle room 1)
    ]
    g175, g176 = ROOM_PARAMS[room_index]
    lines.append(f"; Patch boot room params for room {room_index}")
    lines.append(f";   G_0175=${g175:04X}, G_0176=${g176:04X}")
    # $55CF: MVII #$0002, R0  -> MVII #$XXXX, R0
    lines.append("p 55CF 02B8")
    lines.append(f"p 55D0 {g175:04X}")
    # $55D3: MVII #$001A, R0  -> MVII #$XXXX, R0
    lines.append("p 55D3 02B8")
    lines.append(f"p 55D4 {g176:04X}")
    lines.append("")

    # Break after X_FILL_ZERO at $5035-$5036 returns to $5038.
    lines.append("; Break after X_FILL_ZERO")
    lines.append("b 5038")
    lines.append("")

    # Run through boot up to the X_FILL_ZERO return point
    lines.append("; Run through boot + X_FILL_ZERO")
    lines.append("r 8000000")
    lines.append("")

    # Also write G_019C so the game state is consistent if we ever
    # reach the main loop (not expected at this capture point).
    lines.append(f"; Write G_019C={room_index} (room index for consistency)")
    lines.append(f"p 019C {room_index:04X}")
    lines.append("")

    # Break EXACTLY after L_5EE2 returns ($55DA), before title screen wipes BACKTAB.
    # $55D7: JSR R5, L_5EE2  → room renderer runs, writes 240 words to BACKTAB
    # $55DA: PULR R7         ← BREAK HERE: dungeon fully rendered, title screen not yet run
    # $55DB: L_55DB          → title screen code starts, would wipe BACKTAB
    lines.append("; Break after L_5EE2 room renderer returns (before title screen)")
    lines.append("b 55DA")
    lines.append("")

    # Run until we hit $55DA — L_5EE2 will execute and render the room
    lines.append("; Run until room renderer finishes")
    lines.append("r 8000000")
    lines.append("")

    if include_vs:
        lines.append("; Capture clean framebuffer screenshot (before title screen wipes it)")
        lines.append("vs")
        lines.append("")

    # Dump BACKTAB ($0200-$02EF = 240 words)
    lines.append("; Dump BACKTAB")
    lines.append("m 0200 240")
    lines.append("")

    # Dump GRAM ($3800-$39FF = 512 words)
    lines.append("; Dump GRAM")
    lines.append("m 3800 512")
    lines.append("")

    # Dump STIC color stack ($0028-$002B = 4 words)
    lines.append("; Dump STIC color stack")
    lines.append("m 0028 4")
    lines.append("")

    # Dump STIC MOB registers ($0000-$001F = 32 words)
    lines.append("; Dump STIC MOB registers")
    lines.append("m 0000 32")
    lines.append("")

    # Dump SYSRAM shadow data ($0300-$035F = 96 words)
    lines.append("; Dump SYSRAM MOB shadow")
    lines.append("m 0300 96")
    lines.append("")

    # Dump 8-bit RAM ($0100-$01FF = 256 bytes)
    lines.append("; Dump 8-bit RAM (game state)")
    lines.append("m 0100 256")
    lines.append("")

    # Quit
    lines.append("q")

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    print(f"  Generated: {output_path}")


def run_debugger_script(script_path, output_path, hidden=False):
    """Run jzIntv with a debugger script and capture output via file redirection.

    Args:
        hidden: If True, hide the jzIntv window on Windows (no debugger overlay
                visible to the user). Uses STARTUPINFO with wShowWindow=SW_HIDE.
    """
    cmd = [
        JZINTV, "-d",
        f"--script={script_path}",
        "-e", EXEC_PATH,
        "-g", GROM_PATH,
        ROM_PATH,
    ]
    print(f"  Running: jzintv with script={os.path.basename(script_path)} ...")

    # On Windows, hide the emulator window so the debugger overlay never appears
    startupinfo = None
    if hidden and sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # SW_HIDE

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
                proc.wait(timeout=300)  # 5 minutes max
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                print(f"  TIMEOUT after 300s — partial output captured")

        # Read back the output file
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8', errors='replace') as f:
                output = f.read()
            size = os.path.getsize(output_path)
            print(f"  Output saved: {output_path}  ({size} bytes)")
            return output
        else:
            print(f"  WARNING: Output file not created")
            return ""
    except FileNotFoundError:
        print(f"  ERROR: jzIntv not found at {JZINTV}")
        return ""
    except Exception as e:
        print(f"  ERROR: {e}")
        return ""


def parse_memory_dump(text, base_addr, count):
    """Parse jzIntv 'm <addr> <count>' output into dict {addr: value}."""
    mem = {}
    lines = text.strip().split('\n')
    current_addr = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        m = re.match(r'^([0-9A-F]{4}):\s+(.*)', line)
        if m:
            current_addr = int(m.group(1), 16)
            values_str = m.group(2)
        elif re.match(r'^[0-9A-F]{4}\s', line):
            current_addr = int(line[:4], 16)
            values_str = line[5:]
        else:
            continue
        
        words = re.findall(r'([0-9A-F]{4})\*?', values_str)
        for w in words:
            if current_addr is not None:
                if current_addr < base_addr + count:
                    mem[current_addr] = int(w, 16)
                current_addr += 1
    return mem


def parse_backtab(text):
    """Parse BACKTAB dump into 12x20 grid."""
    grid = [[0] * 20 for _ in range(12)]
    mem = parse_memory_dump(text, 0x0200, 240)
    for addr, val in mem.items():
        if 0x0200 <= addr < 0x02F0:
            offset = addr - 0x0200
            row = offset // 20
            col = offset % 20
            if row < 12 and col < 20:
                grid[row][col] = val
    return grid


def decode_backtab_word(word):
    """Decode BACKTAB word: (card_index, fg_color, bg_bits, is_gram, fg_transp).
    
    Standard Intellivision STIC Color Stack BACKTAB format
    (per jzIntv doc/programming/stic.txt):
      Bits 0-2:   Foreground color (primary 0-7; bit 3 comes from bit 12)
      Bits 3-10:  Card number (0-255 for GROM, 0-63 for GRAM)
      Bit 11:     GRAM/GROM select (0=GROM, 1=GRAM)
      Bit 12:     Foreground color bit 3 (pastel enable for GRAM cards)
                  OR Colored Squares mode select for GROM cards
      Bit 13:     Color Stack advance flag
      Bits 14-15: IGNORED by STIC (available for program use)
    
    In Color Stack mode, card bit=0 pixels show the color stack background,
    and card bit=1 pixels show the foreground color.
    
    fg_transp is always False for Color Stack mode (FG=0 is black, not
    transparent). It is provided for backward compatibility with
    render_room.py and build_clean_room0.py which expect 5 return values.
    """
    card = (word >> 3) & 0xFF             # bits 3-10 (8 bits, 0-255)
    is_gram = bool((word >> 11) & 1)      # bit 11
    # Foreground color: bits 0-2 (primary colors 0-7)
    # For GRAM cards, bit 12 provides the pastel bit (colors 8-15)
    fg = word & 0x7                       # bits 0-2
    if is_gram:
        fg |= ((word >> 9) & 0x8)         # bit 12 = pastel flag for GRAM
        card = card & 0x3F                # GRAM only has 64 cards
    bg_bits = word & 0x7                  # kept for FGBG compat; in CS mode this is FG bits
    fg_transp = False                     # CS mode: FG=0 is black, never transparent
    return card, fg, bg_bits, is_gram, fg_transp


def is_colored_squares(word):
    """Return True if BACKTAB word uses Colored Squares mode (bit 12=1, bit 11=0).
    
    In Color Stack mode, setting bit 12 to 1 and bit 11 to 0 causes the STIC
    to render the card as four 4×4 quadrants, each filled with a color decoded
    from the word itself rather than from a GROM/GRAM bitmap.
    """
    return ((word >> 12) & 1) == 1 and ((word >> 11) & 1) == 0


def decode_colored_squares(word, color_stack_top):
    """Decode a Colored Squares BACKTAB word into 4 quadrant RGB colors.

    The 8×8 card is divided into four 4×4 quadrants:
      [0] top-left, [1] top-right, [2] bottom-left, [3] bottom-right.

    Color indices (per STIC docs):
      Pixel 0 (top-left):     bits 0-2
      Pixel 1 (top-right):    bits 3-5
      Pixel 2 (bottom-left):  bits 6-8
      Pixel 3 (bottom-right): bits 9, 10, 13  (bit 13 is MSB)

    Colors 0-6 map to the primary palette. Color 7 shows the current
    color-stack top entry (provided as color_stack_top).

    Returns (colors, is_off) where:
      colors: list of 4 RGB tuples
      is_off: list of 4 bools (True for color-7 quadrants, which are "off"
               for MOB collision and should let behind-MOBs show through)
    """
    p0 = word & 0x7
    p1 = (word >> 3) & 0x7
    p2 = (word >> 6) & 0x7
    p3 = ((word >> 13) & 1) << 2 | ((word >> 10) & 1) << 1 | ((word >> 9) & 1)

    colors = []
    is_off = []
    for c in [p0, p1, p2, p3]:
        if c == 7:
            colors.append(color_stack_top)
            is_off.append(True)
        else:
            colors.append(PALETTE.get(c, DEFAULT_BG))
            is_off.append(False)
    return colors, is_off


# -- Authoritative jzIntv palette -------------------------------------------
# The 16 STIC colors exactly as defined in jzIntv's renderer
# (vendor/jzintv-src/gfx/gfx.c, gfx_stic_palette). Use this for FG/BG-mode
# dungeon rendering. (The PALETTE/PASTEL_PALETTE dicts above were sampled from
# a reference GIF whose palette does NOT match this build; kept for the
# color-stack code paths and backward compatibility.)
JZINTV_PALETTE = [
    (0x00, 0x00, 0x00),  # 0  black
    (0x00, 0x2D, 0xFF),  # 1  blue
    (0xFF, 0x3D, 0x10),  # 2  red
    (0xC9, 0xCF, 0xAB),  # 3  tan
    (0x38, 0x6B, 0x3F),  # 4  dark green
    (0x00, 0xA7, 0x56),  # 5  green
    (0xFA, 0xEA, 0x50),  # 6  yellow
    (0xFF, 0xFC, 0xFF),  # 7  white
    (0xBD, 0xAC, 0xC8),  # 8  grey
    (0x24, 0xB8, 0xFF),  # 9  cyan
    (0xFF, 0xB4, 0x1F),  # 10 orange
    (0x54, 0x6E, 0x00),  # 11 brown / olive
    (0xFF, 0x4E, 0x57),  # 12 pink
    (0xA4, 0x96, 0xFF),  # 13 light blue
    (0x75, 0xCC, 0x80),  # 14 yellow-green
    (0xB5, 0x1A, 0x58),  # 15 purple
]


def decode_fgbg_word(word):
    """Decode a BACKTAB word in STIC Foreground/Background mode.

    Faithful to jzIntv's stic_draw_fgbg (vendor/jzintv-src/stic/stic.c):
        gr_idx = card & 0x9F8                 # card#<<3 in bits 3-8, GRAM in bit 11
        fg     = card & 7                     # bits 0-2 (primary 0-7)
        bg     = ((card>>9)&0xB) | ((card>>11)&0x4)   # bits 12,13,10,9 (0-15)

    Swords & Serpents runs the dungeon in FG/BG mode (the screen-setup routine
    at $53B5 WRITES $0021, which selects FG/BG mode, then skips the $0021 read
    via INCR R7). In FG/BG mode the bit-12/bit-11 "Colored Squares" rule does
    NOT apply; each tile instead carries its own 4-bit background color, which
    is why dungeon walls sit on black while the floor is olive green.

    Returns (card_index 0-63, is_gram, fg_color 0-7, bg_color 0-15).
    """
    gr_idx = word & 0x9F8
    card = (gr_idx >> 3) & 0x3F
    is_gram = bool(gr_idx & 0x800)
    fg = word & 0x7
    bg = ((word >> 9) & 0xB) | ((word >> 11) & 0x4)
    return card, is_gram, fg, bg


def render_room_fgbg(backtab_grid, gram_mem, grom, zoom=4, palette=JZINTV_PALETTE,
                     mobs=None):
    """Render a room in FG/BG mode (the mode Swords & Serpents uses for dungeons).

    Each 8x8 tile: card bit=1 -> foreground color, card bit=0 -> per-tile
    background color, both from `palette`. GRAM cards (bit 11) are read from
    `gram_mem`; GROM cards from `grom`.

    `mobs` (optional): a list of MOB dicts from parse_room_mobs(). Each is drawn
    on top of the BACKTAB at its (x, y) pixel position in its own color. If the
    MOB's GRAM card is loaded, its bitmap is drawn; otherwise a small filled
    marker is drawn so the sprite's position is still visible (the sprite card
    is only populated after character-select — see parse_room_mobs).
    """
    cols, rows, ts = 20, 12, 8
    W, H = cols * ts * zoom, rows * ts * zoom
    img = Image.new('RGB', (W, H))
    px = img.load()
    for row in range(rows):
        for col in range(cols):
            word = backtab_grid[row][col]
            card, is_gram, fg_i, bg_i = decode_fgbg_word(word)
            fg = palette[fg_i & 0xF]
            bg = palette[bg_i & 0xF]
            if is_gram:
                cb = [gram_mem.get(0x3800 + card * 8 + r, 0) & 0xFF for r in range(8)]
            else:
                cb = grom[card * 8:card * 8 + 8]
            x0, y0 = col * ts * zoom, row * ts * zoom
            for y in range(ts):
                byte = cb[y] if y < len(cb) else 0
                for x in range(ts):
                    c = fg if (byte >> (7 - x)) & 1 else bg
                    for dy in range(zoom):
                        for dx in range(zoom):
                            px[x0 + x * zoom + dx, y0 + y * zoom + dy] = c

    # -- MOB (hardware sprite) overlay -------------------------------------
    # The player (Prince/Warrior) is an 8x16 top-down figure — two stacked cards
    # (N = top, N+1 = bottom), confirmed against the manual's centre-screen
    # prince. Rows 0-7 come from card N, rows 8-15 from card N+1.
    for m in (mobs or []):
        color = palette[m['color'] & 0xF]

        def _cb(cn):
            if m['is_gram']:
                return [gram_mem.get(0x3800 + (cn & 0x3F) * 8 + r, 0) & 0xFF
                        for r in range(8)]
            return list(grom[(cn & 0xFF) * 8:(cn & 0xFF) * 8 + 8])

        rows = _cb(m['card']) + _cb(m['card'] + 1)
        loaded = any(rows)
        if not loaded:
            rows = [0xFF] * 8                       # marker = solid 8x8 box
        # MOBs render at DOUBLE vertical resolution (jzIntv stic.c: the MOB
        # plane is 2x the BACKTAB height, y_pos = (y_reg & 0x7F) * 2). So the
        # 16-row sprite occupies the height of 8 BACKTAB pixels (one tile), not
        # two. Horizontal pixels are full size; vertical pixels are half.
        vz = max(1, zoom // 2)
        px0 = (m['x'] - 8) * zoom
        py0 = m['y'] * zoom
        for y, byte in enumerate(rows):
            for x in range(8):
                if not ((byte >> (7 - x)) & 1):
                    continue
                for dy in range(vz):
                    for dx in range(zoom):
                        ix, iy = px0 + x * zoom + dx, py0 + y * vz + dy
                        if 0 <= ix < W and 0 <= iy < H:
                            px[ix, iy] = color
    return img


def load_grom():
    """Load GROM character ROM (256 cards × 8 bytes)."""
    with open(GROM_PATH, 'rb') as f:
        return f.read()


def _read_rom_decle(rom, addr):
    """Read a 16-bit DECLE from the cartridge ROM at CP-1610 address `addr`.

    The .bin stores each DECLE as 2 big-endian bytes; CP address $5000 is
    file offset 0.
    """
    off = (addr - 0x5000) * 2
    if off + 1 < len(rom):
        return (rom[off] << 8) | rom[off + 1]
    return 0


def reconstruct_dungeon_gram(rom_path=ROM_PATH, rle_addr=0x61E7):
    """Rebuild the dungeon GRAM tileset directly from the cartridge ROM.

    The captured debugger traces break at $55DA (title-screen boot), where
    GRAM still holds the IMAGIC logo, not dungeon tiles — so rooms rendered
    from those dumps have blank walls/pillars. This function instead replays
    the game's own RLE tile loader (routine L_53EA at $53EA) against the RLE
    block at $61E7, producing the GRAM contents the game would have loaded
    when entering a dungeon, with no emulator run required.

    Faithful replication of L_53EA:
        R5 = DECLE[$61E7]            ; starting GRAM byte offset
        R5 += $3800                  ; -> GRAM address
        R0 = DECLE[$61E8]            ; entry count
        for each of R0 entries:
            w   = next DECLE
            rep = ((w >> 8) & 3) + 1  ; SWAP + ANDI #3 -> 1..4 repeats
            byte = w & 0xFF
            write `byte` `rep` times to GRAM, advancing R5

    Returns a dict {address: byte} compatible with the gram_mem argument of
    render_room_image (keys are $3800-based GRAM byte addresses). Covers the
    31 dungeon/dragon cards (cards 3-33); cards 0-2 are not in this block.
    """
    with open(rom_path, 'rb') as f:
        rom = f.read()
    a = rle_addr
    start_off = _read_rom_decle(rom, a); a += 1
    count = _read_rom_decle(rom, a); a += 1
    gram_mem = {}
    addr = 0x3800 + start_off
    for _ in range(count):
        w = _read_rom_decle(rom, a); a += 1
        rep = ((w >> 8) & 3) + 1
        byte = w & 0xFF
        for _r in range(rep):
            gram_mem[addr] = byte
            addr += 1
    return gram_mem


# Warrior rotation frames (top-down) -> DECLE card pair at $5BCE.
# Frame 0 is the opening position; frames advance counter-clockwise; frame 4
# faces north. Each frame is an 8x16 figure (two stacked cards).
WARRIOR_FRAMES = 5


def reconstruct_mob_sprite_gram(rom_path=ROM_PATH, sprite_base=0x5BCE,
                                target_card=48, frame=0):
    """Load a character sprite frame from the ROM's DECLE block into GRAM,
    replicating the sprite loader (routine at $5216, GRAM target from the $5555
    table -> card 48 for MOB0).

    Headless captures that force PC past the title/menu never run character-
    select, so the player sprite cards (48+) stay blank. The Warrior/Prince
    sprites live at $5BCE as consecutive 8x16 figures (two 8-byte cards each):
    `frame` 0 = opening position, 1-4 = counter-clockwise rotation, 4 = facing
    north. This loads the chosen frame's two cards into `target_card` and
    `target_card+1` so the MOB overlay can draw the figure.

    Returns a dict {gram_address: byte} to merge into a gram_mem map.
    """
    with open(rom_path, 'rb') as f:
        rom = f.read()
    a = sprite_base + (frame % WARRIOR_FRAMES) * 16   # 16 bytes (2 cards) per frame
    base = 0x3800 + target_card * 8
    return {base + i: _read_rom_decle(rom, a + i) & 0xFF for i in range(16)}


def parse_room_mobs(output_text):
    """Decode the 8 hardware sprites (MOBs) from a captured SYSRAM dump.

    The STIC X/Y registers are write-only (jzIntv reads return bus garbage), so
    the game's SYSRAM shadow is used: X at $0325-$032C, Y at $032D-$0334,
    attribute (A register) at $0335-$033C. The A-register shadow is in raw STIC
    format (verified: it equals STIC $0010-$0017 byte-for-byte), decoded per
    jzIntv stic.c:

        fg_color = ((a >> 9) & 0x08) | (a & 0x07)     # 0-15
        gr_idx   = a & 0xFF8                           # card<<3 (+GRAM bit 11)
        card     = (gr_idx >> 3) & 0x3F (GRAM) / 0xFF (GROM)
        is_gram  = a & 0x800

    Position: x = X-shadow low byte; y = Y-shadow low byte. Per stic.c the STIC
    Y is (y & 0x7F) * 2 in a 192-line field, i.e. (y & 0x7F) BACKTAB rows. The
    shadow high bytes hold the game's own flags (not STIC bits), so size/flip
    are taken from the A register's neighbours only when meaningful.

    Returns a list of dicts {idx,x,y,card,color,is_gram} for slots that are on
    the playfield. NOTE: a sprite only shows real graphics if its GRAM card is
    loaded — which happens during character-select. A headless capture that
    bypasses the menu leaves those cards blank (the renderer then draws a
    marker).
    """
    sysram = parse_memory_dump(extract_memory_section(output_text, 0x0300, 0x0360),
                               0x0300, 96)
    mobs = []
    for i in range(8):
        x = sysram.get(0x0325 + i, 0) & 0xFF
        y_raw = sysram.get(0x032D + i, 0) & 0xFF
        a = sysram.get(0x0335 + i, 0)
        if a == 0 or (x == 0 and y_raw == 0):
            continue                       # empty/off-screen slot
        y = y_raw & 0x7F                    # BACKTAB-row position (0-95)
        color = ((a >> 9) & 0x08) | (a & 0x07)
        is_gram = bool(a & 0x800)
        gr_idx = a & 0xFF8
        card = (gr_idx >> 3) & (0x3F if is_gram else 0xFF)
        if x == 0 or x >= 167 or y >= 96:
            continue
        mobs.append({'idx': i, 'x': x, 'y': y, 'card': card,
                     'color': color, 'is_gram': is_gram})
    return mobs


def get_grom_card_bytes(grom, card_index):
    """Return 8 bytes for GROM card 0-255."""
    card_index = card_index & 0xFF  # GROM has 256 cards (8-bit index)
    base = card_index * 8
    if base + 8 <= len(grom):
        return grom[base:base+8]
    return bytes(8)


def _fg_color_for_index(fg_color_idx):
    """Map FG color index to RGB using PALETTE (0-7) and PASTEL_PALETTE (8-15).
    
    In standard Color Stack mode, FG is always PRIMARY (0-7) from bits 15/14/12.
    The 8-15 range is a fallback for non-standard decodings or FG/BG mode.
    """
    if fg_color_idx >= 8:
        return PASTEL_PALETTE.get(fg_color_idx - 8, (255, 0, 255))
    return PALETTE.get(fg_color_idx, (255, 0, 255))


def render_card_1bpp_with_bitmap(card_bytes, fg_color_idx, bg_color=DEFAULT_BG):
    """Render an 8×8 card AND return a per-pixel bitmap of which pixels
    are card background (bit=0, showing color stack) vs foreground (bit=1).
    
    Returns (Image, bitmap) where bitmap[row][col] is True for background pixels.
    """
    fg = _fg_color_for_index(fg_color_idx)
    img = Image.new('RGB', (8, 8))
    px = img.load()
    bitmap = [[False] * 8 for _ in range(8)]
    for row in range(min(8, len(card_bytes))):
        byte_val = card_bytes[row]
        for col in range(8):
            bit = (byte_val >> (7 - col)) & 1
            is_bg = (bit == 0)
            bitmap[row][col] = is_bg
            px[col, row] = fg if bit else bg_color
    return img, bitmap


def render_card_1bpp(card_bytes, fg_color_idx, bg_color=DEFAULT_BG):
    """Render an 8×8 card in 1bpp Color Stack mode.
    
    In Color Stack mode, FG=0 is BLACK (palette entry 0), not transparent.
    The background color comes from the color stack, not from the FG field.
    """
    img, _ = render_card_1bpp_with_bitmap(card_bytes, fg_color_idx, bg_color)
    return img


def render_gram_card(gram_mem, card_index, fg_color_idx, bg_color=DEFAULT_BG):
    """Render a GRAM card (lo byte only, 1bpp)."""
    base = 0x3800 + card_index * 8
    card_bytes = bytes(gram_mem.get(base + row, 0) & 0xFF for row in range(8))
    return render_card_1bpp(card_bytes, fg_color_idx, bg_color)


def render_gram_card_with_bitmap(gram_mem, card_index, fg_color_idx, bg_color=DEFAULT_BG):
    """Render a GRAM card AND return background pixel bitmap."""
    base = 0x3800 + card_index * 8
    card_bytes = bytes(gram_mem.get(base + row, 0) & 0xFF for row in range(8))
    return render_card_1bpp_with_bitmap(card_bytes, fg_color_idx, bg_color)


def render_grom_card(grom, card_index, fg_color_idx, bg_color=DEFAULT_BG):
    """Render a GROM card from grom.bin."""
    card_bytes = get_grom_card_bytes(grom, card_index)
    return render_card_1bpp(card_bytes, fg_color_idx, bg_color)


def render_grom_card_with_bitmap(grom, card_index, fg_color_idx, bg_color=DEFAULT_BG):
    """Render a GROM card AND return background pixel bitmap."""
    card_bytes = get_grom_card_bytes(grom, card_index)
    return render_card_1bpp_with_bitmap(card_bytes, fg_color_idx, bg_color)


def render_room_image(backtab_grid, gram_mem, grom, color_stack=None, zoom=4, mobs=None, use_fgbg=False):
    """Render a single room (12x20 tiles) as a PIL Image.
    
    Swords & Serpents uses COLOR STACK mode (verified via per-tile screenshot
    analysis: same bg_adv value produces different backgrounds at different
    tile positions, proving the color stack pointer advances per tile).
    
    In Color Stack mode:
      - advance (bit 13) steps the color stack pointer by 1 when set
      - Card dot=0 pixels show the current color stack entry
      - Card dot=1 pixels show the FG color (bits 0-2, plus bit 12 for GRAM pastel)
      - EXEC.730 writes the same value to all 4 CS registers
    
    The alternative FG/BG mode is also supported via use_fgbg=True.
    
    Args:
        color_stack: List of 4 RGB tuples for CS0-CS3. If None, defaults to
                     [pastel tan] * 4 (as set by game via EXEC.730).
        mobs: Optional list of MOB dicts to overlay as hardware sprites.
        use_fgbg: If True, use FG/BG mode instead of Color Stack mode.
    """
    cols, rows = 20, 12
    tile_size = 8
    img_w = cols * tile_size * zoom
    img_h = rows * tile_size * zoom
    img = Image.new('RGB', (img_w, img_h))
    px = img.load()
    
    # Default color stack: Swords & Serpents uses all pastel tan entries.
    # The ROM header (de-interleaved) shows 0x00/0x50 which decode to black,
    # but jzIntv renders the background as pastel tan (verified empirically
    # from reference GIF and used throughout the project's test scripts).
    # jzIntv cannot read STIC write-only registers; dumps return $3FFx garbage.
    if color_stack is None or len(color_stack) < 4:
        color_stack = [PASTEL_PALETTE[3]] * 4  # all pastel tan — verified correct

    # Track per-pixel card bit: True if this pixel's card bit is 0
    # (background shows through). Behind MOBs should only
    # render over these background pixels, not over card foreground.
    is_card_bg = [[True] * img_w for _ in range(img_h)]
    
    cs_index = 0  # color stack pointer
    for row in range(rows):
        for col in range(cols):
            word = backtab_grid[row][col]
            card_idx, fg_color_idx, bg_bits, is_gram, _ = decode_backtab_word(word)

            if use_fgbg:
                # FG/BG mode: bits 0-2 encode per-tile background color index (0-7).
                # Bit 3 is the pastel flag for the background.
                bg_color_idx = bg_bits & 0x7
                bg_is_pastel = (word >> 3) & 1
                if bg_is_pastel:
                    bg = PASTEL_PALETTE.get(bg_color_idx, DEFAULT_BG)
                else:
                    bg = PALETTE.get(bg_color_idx, DEFAULT_BG)
            else:
                # Color Stack mode: advance by 1 when bit 13 is set.
                # Per STIC docs: "The STIC advances the color stack immediately,
                # so that the card which sets this bit gets the new background color."
                advance = (word >> 13) & 1
                cs_index = (cs_index + advance) % 4
                bg = color_stack[cs_index]

            # Colored Squares mode: jzIntv renders these as solid color-stack
            # background color, ignoring the card bitmap and quadrant colors.
            # Empirically verified: solid color-stack gives 56.91% match vs 20%
            # for primary-palette quadrants and 35% for pastel-palette quadrants.
            if is_colored_squares(word):
                for y in range(tile_size):
                    for x in range(tile_size):
                        for dy in range(zoom):
                            for dx in range(zoom):
                                px_x = col * tile_size * zoom + x * zoom + dx
                                px_y = row * tile_size * zoom + y * zoom + dy
                                px[px_x, px_y] = bg
                                is_card_bg[px_y][px_x] = True
                continue

            # Empirical BG overrides disabled (derived from wrong decode)
            # if word in EMPIRICAL_BG_COLOR:
            #     bg = EMPIRICAL_BG_COLOR[word]

            # Empirical overrides disabled (derived from wrong decode)
            effective_fg = fg_color_idx

            # Check for per-pixel empirical color override (exact jzIntv pixel colors)
            if word in EMPIRICAL_PER_PIXEL:
                pixel_table = EMPIRICAL_PER_PIXEL[word]
                for y in range(tile_size):
                    row_colors = pixel_table[y]
                    for x in range(tile_size):
                        draw_rgb = row_colors[x]
                        for dy in range(zoom):
                            for dx in range(zoom):
                                px_x = col * tile_size * zoom + x * zoom + dx
                                px_y = row * tile_size * zoom + y * zoom + dy
                                px[px_x, px_y] = draw_rgb
                                is_card_bg[px_y][px_x] = False
                continue

            if is_gram:
                card_img, card_bitmap = render_gram_card_with_bitmap(gram_mem, card_idx, effective_fg, bg)
            else:
                card_img, card_bitmap = render_grom_card_with_bitmap(grom, card_idx, effective_fg, bg)

            for y in range(tile_size):
                for x in range(tile_size):
                    r, g, b = card_img.getpixel((x, y))
                    is_bg = card_bitmap[y][x]  # True if card bit=0
                    if is_bg:
                        # Card bit=0: show color stack background
                        draw_rgb = bg
                    else:
                        # Card bit=1: show foreground color (card was rendered with effective_fg)
                        draw_rgb = (r, g, b)
                    for dy in range(zoom):
                        for dx in range(zoom):
                            px_x = col * tile_size * zoom + x * zoom + dx
                            px_y = row * tile_size * zoom + y * zoom + dy
                            px[px_x, px_y] = draw_rgb
                            is_card_bg[px_y][px_x] = is_bg

    # Overlay MOB sprites
    if mobs:
        behind_mobs = [m for m in mobs if m.get('behind')]
        front_mobs = [m for m in mobs if not m.get('behind')]

        # Render behind-MOBs: they appear BEHIND card foreground pixels
        # (bit=1) but IN FRONT of color stack background (bit=0).
        # Only render where is_card_bg is True.
        for mob in behind_mobs:
            mob_img, mx, my = render_mob_to_overlay(mob, gram_mem, grom, zoom)
            mob_px = mob_img.load()
            for py in range(mob_img.height):
                for pxx in range(mob_img.width):
                    r, g, b, a = mob_px[pxx, py]
                    if a == 0:
                        continue
                    img_x = mx + pxx
                    img_y = my + py
                    if 0 <= img_x < img_w and 0 <= img_y < img_h:
                        if is_card_bg[img_y][img_x]:
                            px[img_x, img_y] = (r, g, b)

        # Render foreground MOBs normally on top of everything
        for mob in front_mobs:
            mob_img, mx, my = render_mob_to_overlay(mob, gram_mem, grom, zoom)
            img.paste(mob_img, (mx, my), mob_img)

    return img


def extract_backtab_from_output(output_text):
    """Extract BACKTAB dump section from jzIntv output."""
    lines = output_text.split('\n')
    backtab_lines = []
    in_backtab = False
    for line in lines:
        stripped = line.strip()
        if re.match(r'^0200:', stripped):
            in_backtab = True
        if in_backtab:
            # Stop when we hit the GRAM dump
            if re.match(r'^3800:', stripped):
                break
            # Stop if address is outside BACKTAB range (before or after)
            m = re.match(r'^([0-9A-F]{4}):', stripped)
            if m:
                addr = int(m.group(1), 16)
                if addr < 0x0200 or addr >= 0x02F0:
                    break
            backtab_lines.append(line)
    return '\n'.join(backtab_lines)


def extract_gram_from_output(output_text):
    """Extract GRAM dump section from jzIntv output."""
    lines = output_text.split('\n')
    gram_lines = []
    in_gram = False
    for line in lines:
        stripped = line.strip()
        if re.match(r'^3800:', stripped):
            in_gram = True
        if in_gram:
            # Stop when we hit content past GRAM range
            m = re.match(r'^([0-9A-F]{4}):', stripped)
            if m and int(m.group(1), 16) >= 0x3A00:
                break
            gram_lines.append(line)
    return '\n'.join(gram_lines)


def extract_color_stack_from_output(output_text):
    """Extract STIC color stack dump ($0028-$002B) from jzIntv output."""
    lines = output_text.split('\n')
    cs_lines = []
    in_cs = False
    for line in lines:
        stripped = line.strip()
        if re.match(r'^0028:', stripped):
            in_cs = True
        if in_cs:
            # Stop when we hit content past color stack range
            m = re.match(r'^([0-9A-F]{4}):', stripped)
            if m and int(m.group(1), 16) >= 0x002C:
                break
            cs_lines.append(line)
    return '\n'.join(cs_lines)


def parse_color_stack(text):
    """Parse STIC color stack registers into list of 4 RGB tuples.
    
    In Color Stack mode (which Swords & Serpents uses), EXEC.730 writes
    the same value (pastel tan) to all 4 CS registers at boot. The per-tile
    bg_bits advance a pointer through this circular stack.
    
    jzIntv CANNOT read STIC registers (they return $3FFF). When garbage
    is detected, returns None so render_room_image() uses its correct default.
    """
    mem = parse_memory_dump(text, 0x0028, 4)
    colors = []
    for addr in range(0x0028, 0x002C):
        val = mem.get(addr, 0)
        color_idx = val & 0x7
        is_pastel = (val & 0x8) != 0
        base = PALETTE.get(color_idx, DEFAULT_BG)
        if is_pastel:
            colors.append(PASTEL_PALETTE.get(color_idx, DEFAULT_BG))
        else:
            colors.append(base)
    
    # jzIntv CANNOT read STIC registers — they are write-only hardware.
    # Reads return data bus pull-up values in range $3FF0-$3FFF.
    # Detect STIC readback garbage: if any parsed value has high bits
    # matching $3FFx, the read is invalid. Return None so render_room_image
    # uses its correct default (all-pastel-tan, matching EXEC.730).
    def _is_stic_garbage(val):
        """STIC write-only registers return $3FFx on read."""
        return (val & 0xFFF0) == 0x3FF0
    stic_garbage = all(
        _is_stic_garbage(mem.get(addr, 0)) or mem.get(addr, 0) == 0
        for addr in range(0x0028, 0x002C)
    )
    if not mem or len(colors) < 4 or stic_garbage:
        return None  # let render_room_image use its default
    return colors


def extract_memory_section(output_text, start_addr, end_addr):
    """Extract a memory dump section from jzIntv output by address range.

    start_addr and end_addr may be integers or hex strings (e.g. '0x0300').
    """
    # Normalize addresses to integers
    if isinstance(start_addr, str):
        start_addr = int(start_addr, 0)
    if isinstance(end_addr, str):
        end_addr = int(end_addr, 0)
    lines = output_text.split('\n')
    section_lines = []
    in_section = False
    for line in lines:
        stripped = line.strip()
        m = re.match(r'^([0-9A-F]{4}):', stripped)
        if m:
            addr = int(m.group(1), 16)
            if start_addr <= addr < end_addr:
                in_section = True
            elif in_section:
                break
            else:
                in_section = False
        if in_section:
            section_lines.append(line)
    return '\n'.join(section_lines)


def parse_mobs(sysram_text):
    """Parse SYSRAM MOB shadow data into a list of active mob dicts.

    STIC X/Y registers are WRITE-ONLY in jzIntv (return $3FFx garbage on read).
    Instead, we read the SYSRAM shadow data that the game's VBlank ISR
    copies to STIC registers every frame.

    SYSRAM MOB shadow layout (traced from disassembly at $5059, $52C2, $52D7):
      $0325-$032C: MOB0-MOB7 X positions (low byte = 8-bit X, high byte = flags)
      $032D-$0334: MOB0-MOB7 Y positions (low byte = 8-bit Y, high byte = flags)
      $0335-$033C: MOB0-MOB7 Attributes (same format as STIC MOB attribute):
        bits 0-7:   Card number (0-63 for GRAM, 0-255 for GROM)
        bit 8:      X-size (0=8px wide, 1=16px wide)
        bit 9:      X-flip (horizontal mirror)
        bit 10:     Y-flip (vertical mirror)
        bit 11:     GRAM flag (1=GRAM, 0=GROM)
        bit 12:     Priority (1=behind background colors 1-7)
        bit 13:     Collision enable
        bit 14:     Visible (1=invisible, 0=visible)
        bit 15:     Y-size (0=8px tall, 1=16px tall)

    Returns list of dicts: {mob_idx, x, y, card, xsize, ysize, xflip, yflip, is_gram, visible, behind}
    """
    sysram = parse_memory_dump(sysram_text, 0x0300, 96)
    mobs = []
    for mob_idx in range(8):
        x_word = sysram.get(0x0325 + mob_idx, 0)
        y_word = sysram.get(0x032D + mob_idx, 0)
        attr = sysram.get(0x0335 + mob_idx, 0)

        # X and Y are stored in LOW bytes of their respective words.
        # The STIC hardware registers at $0000-$0007 (X) and $0008-$000F (Y)
        # are 8-bit write-only registers. jzIntv 16-bit reads of these
        # registers return actual 8-bit value in low byte + bus noise in high.
        # Comparing STIC registers against SYSRAM shadow confirms:
        #   STIC $0000 (X) low byte = SYSRAM $0325 low byte (both 0x58=88)
        #   STIC $0008 (Y) low byte = SYSRAM $032D low byte (both 0xB8=184)
        # The high bytes of SYSRAM X/Y words are NOT STIC positions.
        x = x_word & 0xFF
        y = y_word & 0xFF

        # Filter dead slots: both X=0 and Y=0 means uninitialized.
        # A real MOB at (0,0) is extremely unlikely in a dungeon crawler
        # (it would be a wall corner). Even if real, it's invisible there.
        if x == 0 and y == 0:
            continue

        card = attr & 0xFF
        xsize = (attr >> 8) & 1   # 0=8px, 1=16px
        xflip = (attr >> 9) & 1
        yflip = (attr >> 10) & 1
        is_gram = (attr >> 11) & 1
        behind = (attr >> 12) & 1
        visible = ((attr >> 14) & 1) == 0  # 0=visible, 1=hidden
        ysize = (attr >> 15) & 1  # 0=8px, 1=16px

        if is_gram:
            card = card & 0x3F  # GRAM has 64 cards

        if visible and x < 168 and y < 104:  # on-screen check (allows partial off-screen)
            mobs.append({
                'mob_idx': mob_idx,
                'x': x,
                'y': y,
                'card': card,
                'xsize': xsize,
                'ysize': ysize,
                'xflip': xflip,
                'yflip': yflip,
                'is_gram': is_gram,
                'behind': behind,
                'visible': visible,
            })
    return mobs


def render_mob_to_overlay(mob, gram_mem, grom, zoom=4):
    """Render a single MOB sprite to an RGBA PIL Image (with transparency).

    Returns (Image, x_offset, y_offset) positioned in zoomed room coordinates.
    The image has transparency for the background (color 0 = transparent for MOBs).
    MOB foreground color is derived from the cartridge border extension byte
    at ROM $500D (read at module load). The EXEC ROM sets STIC.BORD from this
    byte at boot, and Swords & Serpents never overrides it during gameplay.
    """
    card = mob['card']
    width = 16 if mob['xsize'] == 1 else 8
    height = 16 if mob['ysize'] == 1 else 8

    fg = MOB_FG_COLOR  # from cartridge border extension ($500D)

    img = Image.new('RGBA', (width * zoom, height * zoom), (0, 0, 0, 0))
    px = img.load()

    # Read card bytes for this sprite
    def get_card_row(c, r):
        """Get byte row r from card c (GRAM or GROM).
        Card numbers wrap: GRAM at 64, GROM at 256."""
        if mob['is_gram']:
            base = 0x3800 + (c & 0x3F) * 8
            return gram_mem.get(base + r, 0) & 0xFF
        else:
            return get_grom_card_bytes(grom, c & 0xFF)[r] if r < 8 else 0

    for row in range(height):
        # Y-flip: read source row in reverse order
        src_row = (height - 1 - row) if mob['yflip'] else row

        # Determine which card(s) this row belongs to (for 16-tall sprites)
        # 16×16 sprites use a 2×2 grid: card (TL), card+1 (TR),
        # card+2 (BL), card+3 (BR)
        if height == 16:
            if src_row < 8:
                card_num = card
            else:
                card_num = ((card + 2) & 0x3F) if mob['is_gram'] else ((card + 2) & 0xFF)
            byte_off = src_row & 0x7
        else:
            card_num = card
            byte_off = src_row

        # For 16-wide sprites, get the right-card byte too
        byte_val = get_card_row(card_num, byte_off)
        right_card = ((card_num + 1) & 0x3F) if mob['is_gram'] else ((card_num + 1) & 0xFF)
        byte_val2 = get_card_row(right_card, byte_off) if width == 16 else 0

        for col in range(width):
            # Determine which byte and bit
            if col < 8:
                b = byte_val
                bit_col = col
            else:
                b = byte_val2
                bit_col = col - 8

            # X-flip: read source column in reverse order
            src_col = 7 - bit_col if mob['xflip'] else bit_col
            bit = (b >> src_col) & 1

            if bit:
                for dy in range(zoom):
                    for dx in range(zoom):
                        px_x = col * zoom + dx
                        px_y = row * zoom + dy
                        px[px_x, px_y] = fg + (255,)

    x_offset = mob['x'] * zoom
    y_offset = mob['y'] * zoom
    return img, x_offset, y_offset


def main():
    os.makedirs(TRACES_DIR, exist_ok=True)
    os.makedirs(ROOMS_DIR, exist_ok=True)

    print("=" * 70)
    print("  SWORDS & SERPENTS — ALL ROOMS RENDERER")
    print("=" * 70)
    print(f"  MOB color: border_ext=${_BORDER_EXT:02X} -> color={_MOB_COLOR_IDX} pastel={_MOB_IS_PASTEL} -> {MOB_FG_COLOR}")
    print(f"  Project: {PROJECT_DIR}")
    print(f"  Rooms:   0-{NUM_ROOMS - 1}")
    print()

    # Load GROM
    grom = load_grom()
    print(f"  GROM loaded: {len(grom)} bytes ({len(grom) // 8} cards)")
    print()

    # Phase 1: Generate and run debugger scripts for all rooms
    print("-" * 70)
    print("  PHASE 1: Capture BACKTAB for all rooms")
    print("-" * 70)

    room_data = []  # list of (backtab_grid, gram_mem, color_stack, mobs)

    for room_idx in range(NUM_ROOMS):
        print(f"\n  Room {room_idx}:")

        script_path = os.path.join(TRACES_DIR, f"render_room_{room_idx}.txt")
        output_path = str(next_versioned_path(TRACES_DIR, f"render_room_{room_idx}_out", ".txt"))

        generate_debugger_script(room_idx, script_path)
        output = run_debugger_script(script_path, output_path)

        if not output:
            print(f"  WARNING: No output for room {room_idx}, skipping")
            continue

        # Parse BACKTAB
        backtab_text = extract_backtab_from_output(output)
        if not backtab_text:
            print(f"  WARNING: No BACKTAB data found for room {room_idx}")
            # Show first 500 chars of output for debugging
            print(f"  Output preview: {output[:500]}")
            continue

        backtab_grid = parse_backtab(backtab_text)

        # Parse GRAM
        gram_text = extract_gram_from_output(output)
        gram_mem = parse_memory_dump(gram_text, 0x3800, 512) if gram_text else {}

        # Parse color stack
        cs_text = extract_color_stack_from_output(output)
        color_stack = parse_color_stack(cs_text) if cs_text else None

        # Parse SYSRAM MOB shadow data ($0300-$035F)
        # STIC X/Y registers are WRITE-ONLY in jzIntv, so we must use
        # the SYSRAM shadow that the game maintains for the VBlank ISR.
        # $0325-$032C: X positions, $032D-$0334: Y positions,
        # $0335-$033C: Attributes (card, size, flips, GRAM flag)
        sysram_text = extract_memory_section(output, 0x0300, 0x0360)
        mobs = parse_mobs(sysram_text) if sysram_text else []

        room_data.append((backtab_grid, gram_mem, color_stack, mobs))

        # Quick stats
        unique_cards = set()
        for row in range(12):
            for col in range(20):
                card, fg, bg_bits, is_gram, _ = decode_backtab_word(backtab_grid[row][col])
                unique_cards.add((card, is_gram))
        non_floor = sum(1 for r in range(12) for c in range(20) if backtab_grid[r][c] != 0x1603)
        print(f"  BACKTAB: {len(unique_cards)} unique cards, {non_floor} non-floor tiles")
        print(f"  MOBs: {len(mobs)} active sprites")
        # Also show color stack info
        cs_str = ', '.join(str(c) for c in (color_stack or []))
        print(f"  Color stack: [{cs_str}]")

    print(f"\n  Captured {len(room_data)}/{NUM_ROOMS} rooms")
    print()

    # Phase 2: Render all rooms
    print("-" * 70)
    print("  PHASE 2: Render rooms")
    print("-" * 70)

    if not room_data:
        print("  ERROR: No room data captured!")
        sys.exit(1)

    zoom = 4
    tile_px = 8 * zoom  # 32px

    # Layout: 3 columns × 2 rows of rooms
    atlas_cols = 3
    atlas_rows = (len(room_data) + atlas_cols - 1) // atlas_cols

    room_w = 20 * tile_px  # 640px
    room_h = 12 * tile_px  # 384px

    # Margin between rooms
    margin = 2 * zoom  # 8px
    label_h = 24  # pixels for room label

    atlas_w = atlas_cols * room_w + (atlas_cols + 1) * margin
    atlas_h = atlas_rows * (room_h + label_h + margin) + margin

    atlas = Image.new('RGB', (atlas_w, atlas_h), (20, 20, 30))
    atlas_px = atlas.load()

    # Simple font for labels (5x7 pixel characters)
    # We'll use PIL's default font via text drawing
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(atlas)
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()

    for i, (backtab_grid, gram_mem, color_stack, mobs) in enumerate(room_data):
        atlas_row = i // atlas_cols
        atlas_col = i % atlas_cols

        x_offset = margin + atlas_col * (room_w + margin)
        y_offset = margin + atlas_row * (room_h + label_h + margin)

        # Draw room label
        draw.text((x_offset + 4, y_offset + 2), f"Room {i}", fill=(200, 200, 200), font=font)

        # Render room with MOBs overlaid
        room_img = render_room_image(backtab_grid, gram_mem, grom, color_stack=color_stack, zoom=zoom, mobs=mobs)

        # Paste into atlas
        for y in range(room_h):
            for x in range(room_w):
                r, g, b = room_img.getpixel((x, y))
                atlas_px[x_offset + x, y_offset + label_h + y] = (r, g, b)

        # Save individual room (versioned)
        room_path = next_versioned_path(ROOMS_DIR, f"dungeon_room_{i}", ".png")
        room_img.save(room_path)
        print(f"  Room {i}: saved {room_path}")

    # Save atlas (versioned)
    atlas_path = next_versioned_path(ROOMS_DIR, "dungeon_all_rooms", ".png")
    atlas.save(atlas_path)
    print(f"\n  Atlas: saved {atlas_path}  ({atlas_w}×{atlas_h}px)")

    # Phase 3: Print card grids for each room
    print()
    print("-" * 70)
    print("  PHASE 3: Card index grids")
    print("-" * 70)

    for i, (backtab_grid, _, _, _) in enumerate(room_data):
        print(f"\n  Room {i} card indices:")
        for row in range(12):
            line = ""
            for col in range(20):
                word = backtab_grid[row][col]
                card, fg, bg_bits, is_gram, _ = decode_backtab_word(word)
                if word == 0x1603:
                    line += "  · "
                else:
                    src = "G" if is_gram else "g"
                    line += f"{card:2d}{src} "
            print(f"    row {row:2d}: {line}")

    print()
    print("=" * 70)
    print("  DONE")
    print("=" * 70)


if __name__ == '__main__':
    main()
