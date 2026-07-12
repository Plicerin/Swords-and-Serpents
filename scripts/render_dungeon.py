#!/usr/bin/env python3
"""
Swords & Serpents — Dungeon Room Renderer
Parses jzIntv debugger dumps of BACKTAB ($0200-$02EF) and GRAM ($3800-$39FF)
plus grom.bin for GROM-based tiles, to render the dungeon room as a PNG.
"""

import os
import re
from PIL import Image

# ── Load GROM (character ROM) ──────────────────────────────────────────────
_GROM_PATH = os.path.join(os.path.dirname(__file__), 'grom.bin')
_grom_data = None

def _load_grom():
    global _grom_data
    if _grom_data is None:
        _grom_data = open(_GROM_PATH, 'rb').read()
    return _grom_data

def get_grom_card_bytes(card_index):
    """Return 8 bytes for GROM card 0-255."""
    grom = _load_grom()
    base = card_index * 8
    if base + 8 <= len(grom):
        return grom[base:base+8]
    return bytes(8)

# ── Intellivision Color Palette (primary 8 + extended 8) ────────────────────
PALETTE = {
    0:  (0, 0, 0),        # Black
    1:  (0, 45, 200),     # Blue
    2:  (200, 0, 20),     # Red
    3:  (200, 170, 100),  # Tan
    4:  (0, 80, 20),      # Dark Green
    5:  (0, 140, 40),     # Green
    6:  (230, 215, 70),   # Yellow
    7:  (255, 255, 255),  # White
    8:  (100, 100, 100),  # Grey
    9:  (0, 200, 200),    # Cyan
    10: (255, 140, 40),   # Orange
    11: (140, 80, 20),    # Brown
    12: (255, 120, 180),  # Pink
    13: (120, 180, 255),  # Light Blue
    14: (180, 255, 100),  # Yellow-Green
    15: (200, 80, 255),   # Purple
}

# ── Parse jzIntv debugger memory dump ───────────────────────────────────────

def parse_memory_dump(text, base_addr, count):
    """Parse jzIntv 'm <addr> <count>' output into dict {addr: value}."""
    mem = {}
    lines = text.strip().split('\n')

    current_addr = None
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Match address line: "3800:  0000* 0028  007F  ..."
        m = re.match(r'^([0-9A-F]{4}):\s+(.*)', line)
        if m:
            current_addr = int(m.group(1), 16)
            values_str = m.group(2)
        elif re.match(r'^[0-9A-F]{4}\s', line):
            # Continuation line without colon
            current_addr = int(line[:4], 16)
            values_str = line[5:]
        else:
            continue

        # Extract hex words
        words = re.findall(r'([0-9A-F]{4})\*?', values_str)
        for w in words:
            if current_addr is not None:
                mem[current_addr] = int(w, 16)
                current_addr += 1

    return mem


# ── Card Rendering ────────────────────────────────────────────────────────

def render_card_1bpp(card_bytes, fg_color_idx, bg_color=(0, 0, 0)):
    """
    Render a single 8×8 card from raw 8-byte data in 1bpp Color Stack mode.
    bit=1 → foreground color, bit=0 → background/transparent color.
    In STIC Color Stack mode, FG color 0 means transparent (show BG).
    """
    if fg_color_idx == 0:
        fg = bg_color
    else:
        fg = PALETTE.get(fg_color_idx, (255, 0, 255))

    img = Image.new('RGB', (8, 8))
    px = img.load()

    for row in range(min(8, len(card_bytes))):
        byte_val = card_bytes[row]
        for col in range(8):
            bit = (byte_val >> (7 - col)) & 1
            px[col, row] = fg if bit else bg_color

    return img


def render_gram_card_1bpp(gram_mem, card_index, fg_color_idx, bg_color=(0, 0, 0)):
    """Render a GRAM card by extracting lo bytes from GRAM memory dump."""
    base = 0x3800 + card_index * 8
    card_bytes = bytes(gram_mem.get(base + row, 0) & 0xFF for row in range(8))
    return render_card_1bpp(card_bytes, fg_color_idx, bg_color)


def render_grom_card_1bpp(card_index, fg_color_idx, bg_color=(0, 0, 0)):
    """Render a GROM card from grom.bin."""
    card_bytes = get_grom_card_bytes(card_index)
    return render_card_1bpp(card_bytes, fg_color_idx, bg_color)


# ── BACKTAB Parsing ────────────────────────────────────────────────────────

def parse_backtab(text):
    """Parse BACKTAB dump into 12×20 grid of word values."""
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
    """
    Decode a BACKTAB word into its components.
    Color Stack mode:
    - Bit 15: 0 = CS mode
    - Bits 14-12: Foreground color (0-7)
    - Bit 11: GRAM/GROM (0=GROM, 1=GRAM) — but we ignore this
    - Bits 10-3: Card number
    - Bits 2-0: Color Stack advance
    Returns: (card_index, fg_color, bg_advance, is_gram)
    """
    fg = (word >> 12) & 0x7
    is_gram = (word >> 11) & 1
    card = (word >> 3) & 0xFF  # full 8-bit card number
    if is_gram:
        card = card & 0x3F  # GRAM: 0-63
    bg = word & 0x7
    return card, fg, bg, is_gram


# ── Main Renderer ──────────────────────────────────────────────────────────

def render_room(backtab_text, gram_text, color_stack_text="", zoom=4):
    """Render the room from BACKTAB + GRAM debugger dumps + grom.bin."""
    backtab = parse_backtab(backtab_text)
    gram_mem = parse_memory_dump(gram_text, 0x3800, 512)

    # Parse color stack if provided
    color_stack = [PALETTE[0]] * 4  # default: black
    if color_stack_text:
        cs_mem = parse_memory_dump(color_stack_text, 0x0028, 4)
        for i in range(4):
            val = cs_mem.get(0x0028 + i, 0)
            cs_color = val & 0xF
            color_stack[i] = PALETTE.get(cs_color, PALETTE[0])

    # Room: 20 columns × 12 rows, each tile 8×8 pixels
    cols, rows = 20, 12
    tile_size = 8

    img = Image.new('RGB', (cols * tile_size * zoom, rows * tile_size * zoom))
    px = img.load()

    # Count unique cards used
    grom_cards = set()
    gram_cards = set()

    # Track color stack
    cs_index = 0

    for row in range(rows):
        for col in range(cols):
            word = backtab[row][col]
            card_idx, fg, bg_adv, is_gram = decode_backtab_word(word)

            if is_gram:
                gram_cards.add(card_idx)
            else:
                grom_cards.add(card_idx)

            # Get current background color from color stack
            bg = color_stack[cs_index % 4]

            # Advance color stack for next card
            cs_index = (cs_index + bg_adv) % 4

            # Render from appropriate source
            if is_gram:
                card_img = render_gram_card_1bpp(gram_mem, card_idx, fg, bg)
            else:
                card_img = render_grom_card_1bpp(card_idx, fg, bg)

            # Place into the main image with zoom
            for y in range(tile_size):
                for x in range(tile_size):
                    r, g, b = card_img.getpixel((x, y))
                    for dy in range(zoom):
                        for dx in range(zoom):
                            px_x = col * tile_size * zoom + x * zoom + dx
                            px_y = row * tile_size * zoom + y * zoom + dy
                            px[px_x, px_y] = (r, g, b)

    print(f"Room rendered: {cols}×{rows} tiles")
    print(f"  GROM cards used ({len(grom_cards)}): {sorted(grom_cards)}")
    print(f"  GRAM cards used ({len(gram_cards)}): {sorted(gram_cards)}")
    return img


# ── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    # ── BACKTAB data (from jzIntv: m 0200 240) ─────────────────────────
    BACKTAB_DUMP = """
0200:  1603* 1603  1603  1603   1603  1603  1603  1603
0208:  1603  1603  1603  1603   1603  1603  1603  1603
0210:  1603  1603  1603  1603   1603  1603  1603  1603
0218:  1603  1603  1603  1603   1603  1603  1603  1603
0220:  1603  1603  1603  1603   1603  1603  1603  1603
0228:  1603  1603  179B  17BB   177B  1793  1723  179B
0230:  1603  1633  1603  179B   172B  1793  1783  172B
0238:  1773  17A3  179B  1603   1603  1603  1603  1603
0240:  1603  1603  1603  1603   1603  1603  1603  1603
0248:  1603  1603  1603  1603   1603  1603  1603  1603
0250:  1603  1603  1603  1603   1603  1EBB  1603  174B
0258:  176B  170B  173B  174B   171B  1603  168B  16CB
0260:  16C3  1693  1603  1603   1603  1603  1603  1603
0268:  1603  1603  1603  1603   1603  1603  1603  1603
0270:  1603  1603  1603  1603   1603  1603  1603  1603
0278:  1603  1603  1603  1603   1603  1603  1603  1603
0280:  1603  1603  1603  1603   1603  1603  1603  1603
0288:  1603  1603  1603  1603   1603  1603  1603  1603
0290:  1603  1603  1603  1603   1603  1603  1603  1603
0298:  1603  1603  1603  1603   1603  1603  1603  1603
02A0:  1603  1603  1603  1603   1603  1603  1603  1603
02A8:  1603  1603  1603  1603   1603  1603  1603  1603
02B0:  1603  1603  1603  1603   1603  1603  172B  1773
02B8:  17A3  172B  1793  1603   173B  170B  176B  172B
02C0:  1603  1643  168B  1663   1693  1663  169B  164B
02C8:  1603  1603  1603  1603   1603  1603  1603  1603
02D0:  1603  1603  1603  1603   1603  1603  1603  1603
02D8:  1603  1603  1603  1603   1603  1603  1603  1603
02E0:  1603  1603  1603  1603   1603  1603  1603  1603
02E8:  1603  1603  1603  1603   1603  1603  1603  1603
"""

    # ── GRAM data (from jzIntv: m 3800 512) ────────────────────────────
    GRAM_DUMP = """
3800:  0000* 0028  007F  0018   002F  000D  0010  0000
3808:  00F0  00F0  00F0  0070   0070  0020  00A0  00A0
3810:  00A0  00A0  0080  00D0   00D0  00F0  00F0  00F0
3818:  00F0  00F8  00E8  0078   00F0  00F8  00F8  00F8
3820:  00F7  00FF  00FF  00FF   00EF  00E6  0000  0000
3828:  00EF  00FF  007F  00FF   00FF  00FD  00F8  00F8
3830:  00F0  00F8  00E8  00F8   00F0  00B8  0000  0000
3838:  0080  00C0  00E0  00E0   00E0  00E0  00E0  00E0
3840:  00FF  007F  0000  0000   0000  0000  0000  0000
3848:  00E0  00EC  00ED  00ED   00ED  00ED  00EC  00E0
3850:  00E0  00EC  00ED  00ED   00ED  00ED  00EC  00E0
3858:  007F  002E  003A  0036   006C  0074  005C  00FE
3860:  00FF  0000  00FF  00FE   00FE  00FF  0000  00FF
3868:  00AB  00AB  00AB  00AA   00AA  00AB  00AB  00AB
3870:  0000  0000  0087  009D   00FD  003F  0018  003C
3878:  0042  0081  0099  00BD   005A  0024  00DB  007E
3880:  0000  0018  0024  0018   00BD  00FF  00A5  00FF
3888:  0000  003C  004A  00D1   0085  00A9  004A  003C
3890:  00FF  00F9  00F3  00E7   00CF  007E  003C  0018
3898:  0099  00BD  00BD  00FF   0042  0066  0066  0024
38A0:  00C1  0055  007F  0055   0055  0055  0055  003E
38A8:  0018  003C  0018  003C   006E  00DF  006E  003C
38B0:  0000  0000  0040  00BF   0045  0000  0000  0000
38B8:  003C  0042  0099  0091   0091  0099  0042  003C
38C0:  0000  0078  001E  00FC   0018  0018  0031  0073
38C8:  0000  0000  0010  003B   007F  00FF  00FF  00FF
38D0:  000F  003C  00F8  00F0   00E2  00CA  009F  0039
38D8:  0000  0009  0095  00FF   00FF  0095  0009  0000
38E0:  0000  0083  001F  00FD   00FD  001F  0083  0000
38E8:  00F1  00DF  00BE  0076   0076  00BE  00DF  00F1
38F0:  0000  0006  000F  0099   00F3  00E6  000C  0000
38F8:  0073  0031  0018  0018   00FC  001E  0078  0000
3900:  00FF  00FF  00FF  007F   003B  0010  0000  0000
3908:  0039  009F  00CA  00E2   00F0  00F8  003C  000F
3910:  0000  0000  0000  0000   0000  0000  0000  0000
3918:  0000  0000  0000  0000   0000  0000  0000  0000
3920:  0000  0000  0000  0000   0000  0000  0000  0000
3928:  0000  0000  0000  0000   0000  0000  0000  0000
3930:  0000  0000  0000  0000   0000  0000  0000  0000
3938:  0000  0000  0000  0000   0000  0000  0000  0000
3940:  0000  0000  0000  0000   0000  0000  0000  0000
3948:  0000  0000  0000  0000   0000  0000  0000  0000
3950:  0000  0000  0000  0000   0000  0000  0000  0000
3958:  0000  0000  0000  0000   0000  0000  0000  0000
3960:  0000  0000  0000  0000   0000  0000  0000  0000
3968:  0000  0000  0000  0000   0000  0000  0000  0000
3970:  0000  0000  0000  0000   0000  0000  0000  0000
3978:  0000  0000  0000  0000   0000  0000  0000  0000
3980:  0000  0000  0000  0000   0000  0000  0000  0000
3988:  0000  0000  0000  0000   0000  0000  0000  0000
3990:  0000  0000  0000  0000   0000  0000  0000  0000
3998:  0000  0000  0000  0000   0000  0000  0000  0000
39A0:  001E  003E  0033  007B   0079  00E8  0089  0089
39A8:  0089  008B  009A  00DA   00FE  007C  007C  001C
39B0:  0000  0000  0000  0000   0000  0006  000C  0030
39B8:  0060  00C0  0000  0000   0000  0000  0000  0000
39C0:  0081  0004  0040  0010   0000  0041  0000  0080
39C8:  0004  0000  0040  0004   0020  0000  0001  0080
39D0:  0000  0000  0000  0000   0000  0006  000C  0030
39D8:  0060  00C0  0000  0000   0000  0000  0000  0000
39E0:  0000  0000  0000  0000   0000  0000  0000  0000
39E8:  0000  0000  0000  0000   0000  0000  0000  0000
39F0:  0000  0000  0000  0000   0000  0000  0000  0000
39F8:  0000  0000  0000  0000   0000  0000  0000  0000
"""

    # Color stack dump (from jzIntv: m 0028 4)
    COLOR_STACK_DUMP = """
0028:  3FF0  3FF3  3FF0  3FF0
"""

    # Render
    print("=" * 60)
    print("  SWORDS & SERPENTS — DUNGEON ROOM RENDERER")
    print("=" * 60)

    img = render_room(BACKTAB_DUMP, GRAM_DUMP, COLOR_STACK_DUMP, zoom=4)

    out_path = "sprites/dungeon_room.png"
    img.save(out_path)
    print(f"\nSaved: {out_path}  ({img.size[0]}×{img.size[1]} pixels)")

    # Also render a version showing just the card indices as text overlay
    backtab = parse_backtab(BACKTAB_DUMP)
    print("\n=== BACKTAB Card Index Grid (row × col) ===")
    for row in range(12):
        line = ""
        for col in range(20):
            word = backtab[row][col]
            card, fg, bg, is_gram = decode_backtab_word(word)
            if word == 0x1603:
                line += "  · "
            else:
                line += f"{card:3d}"
        print(f"  row {row:2d}: {line}")

    # Print FG color grid
    print("\n=== FG Color Grid ===")
    for row in range(12):
        line = ""
        for col in range(20):
            word = backtab[row][col]
            _, fg, _, _ = decode_backtab_word(word)
            if word == 0x1603:
                line += " · "
            else:
                line += f"{fg:2d} "
        print(f"  row {row:2d}: {line}")
