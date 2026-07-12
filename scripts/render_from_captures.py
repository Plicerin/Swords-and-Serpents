#!/usr/bin/env python3
"""
Render all dungeon rooms from previously-captured BACKTAB+GRAM dumps.
Reads render_room_N_out.txt files and produces individual room PNGs + atlas.
"""
import os
import re
from PIL import Image, ImageDraw, ImageFont

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
GROM_PATH = os.path.join(PROJECT_DIR, "grom.bin")
TRACES_DIR = os.path.join(PROJECT_DIR, "traces")
SPRITES_DIR = os.path.join(PROJECT_DIR, "sprites")
ROOMS_DIR = os.path.join(PROJECT_DIR, "rooms")

PALETTE = {
    0:  (0, 0, 0),
    1:  (0, 45, 200),
    2:  (200, 0, 20),
    3:  (200, 170, 100),
    4:  (0, 80, 20),
    5:  (0, 140, 40),
    6:  (230, 215, 70),
    7:  (255, 255, 255),
}
DEFAULT_BG = (0, 0, 0)

# ---- Parsing ----

def parse_memory_dump(text, base_addr, count):
    """Parse jzIntv 'm <addr> <count>' output into dict {addr: value}."""
    mem = {}
    lines = text.strip().split('\n')
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
    """Decode BACKTAB word using correct Intellivision STIC Color Stack layout.

    Bits 15,14,12 -> FG color bits 2,1,0 (primary colors 0-7 only).
    Bit 13 -> Color Stack advance flag.
    Bit 11 -> GRAM/GROM select (1=GRAM, 0=GROM).
    Bits 10-0 -> Card number (masked to 0xFF for GROM, 0x3F for GRAM).
    """
    card = word & 0x7FF                   # bits 0-10
    is_gram = bool(word & 0x0800)         # bit 11
    # Foreground color: bits 15, 14, 12 -> bits 2, 1, 0
    fg = ((word >> 13) & 0x6) | ((word >> 12) & 0x1)
    return card, fg, is_gram

# ---- GROM / Card Rendering ----

def load_grom():
    with open(GROM_PATH, 'rb') as f:
        return f.read()

def get_grom_card_bytes(grom, card_index):
    base = card_index * 8
    if base + 8 <= len(grom):
        return grom[base:base+8]
    return bytes(8)

def render_card_1bpp(card_bytes, fg_color_idx, bg_color=DEFAULT_BG):
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

def render_gram_card(gram_mem, card_index, fg_color_idx, bg_color=DEFAULT_BG):
    base = 0x3800 + card_index * 8
    card_bytes = bytes(gram_mem.get(base + row, 0) & 0xFF for row in range(8))
    return render_card_1bpp(card_bytes, fg_color_idx, bg_color)

def render_grom_card(grom, card_index, fg_color_idx, bg_color=DEFAULT_BG):
    card_bytes = get_grom_card_bytes(grom, card_index)
    return render_card_1bpp(card_bytes, fg_color_idx, bg_color)

# ---- Room Rendering ----

def render_room_image(backtab_grid, gram_mem, grom, zoom=4, color_stack=None):
    """Render a single room (12x20 tiles, 8px tiles) as a PIL Image."""
    cols, rows = 20, 12
    tile_size = 8
    img = Image.new('RGB', (cols * tile_size * zoom, rows * tile_size * zoom))
    px = img.load()
    cs = color_stack if color_stack else [DEFAULT_BG] * 4
    cs_index = 0
    for row in range(rows):
        for col in range(cols):
            word = backtab_grid[row][col]
            card_idx, fg, is_gram = decode_backtab_word(word)
            # Color Stack mode: advance pointer when bit 13 is set
            advance = (word >> 13) & 1
            cs_index = (cs_index + advance) % 4
            bg = cs[cs_index % 4]
            # FG=0 is transparent in Color Stack mode (shows background)
            if fg == 0:
                # Card bit=1 pixels show the background color (color stack)
                if is_gram:
                    card_img = render_gram_card(gram_mem, card_idx, fg, bg)
                else:
                    card_img = render_grom_card(grom, card_idx, fg, bg)
                # For transparent tiles, show background everywhere
                for y in range(tile_size):
                    for x in range(tile_size):
                        r, g, b = card_img.getpixel((x, y))
                        # If card bit is 1, show background; else show background too
                        # (transparent means all pixels show color stack)
                        for dy in range(zoom):
                            for dx in range(zoom):
                                px_x = col * tile_size * zoom + x * zoom + dx
                                px_y = row * tile_size * zoom + y * zoom + dy
                                # Check if this pixel is card foreground or background
                                # In transparent mode, card bit=1 pixels show CS background
                                # (not the FG color which would be black=0)
                                px[px_x, px_y] = bg
            else:
                if is_gram:
                    card_img = render_gram_card(gram_mem, card_idx, fg, bg)
                else:
                    card_img = render_grom_card(grom, card_idx, fg, bg)
                for y in range(tile_size):
                    for x in range(tile_size):
                        r, g, b = card_img.getpixel((x, y))
                        for dy in range(zoom):
                            for dx in range(zoom):
                                px_x = col * tile_size * zoom + x * zoom + dx
                                px_y = row * tile_size * zoom + y * zoom + dy
                                px[px_x, px_y] = (r, g, b)
    return img

# ---- Extractors ----

def extract_backtab_from_output(output_text):
    lines = output_text.split('\n')
    backtab_lines = []
    in_backtab = False
    for line in lines:
        stripped = line.strip()
        if re.match(r'^0200:', stripped):
            in_backtab = True
        if in_backtab:
            m = re.match(r'^([0-9A-F]{4}):', stripped)
            if m:
                addr = int(m.group(1), 16)
                if addr < 0x0200 or addr >= 0x02F0:
                    break
            backtab_lines.append(line)
    return '\n'.join(backtab_lines)

def extract_gram_from_output(output_text):
    lines = output_text.split('\n')
    gram_lines = []
    in_gram = False
    for line in lines:
        stripped = line.strip()
        if re.match(r'^3800:', stripped):
            in_gram = True
        if in_gram:
            m = re.match(r'^([0-9A-F]{4}):', stripped)
            if m and int(m.group(1), 16) >= 0x3A00:
                break
            gram_lines.append(line)
    return '\n'.join(gram_lines)

# ---- Main ----

def main():
    os.makedirs(SPRITES_DIR, exist_ok=True)
    os.makedirs(ROOMS_DIR, exist_ok=True)

    grom = load_grom()
    print(f"GROM: {len(grom)} bytes ({len(grom)//8} cards)")
    print("=" * 70)
    print("  EXTRACTING BACKTAB + GRAM from capture files")
    print("=" * 70)

    room_data = []
    for room_idx in range(6):
        output_path = os.path.join(TRACES_DIR, f"render_room_{room_idx}_out.txt")
        if not os.path.exists(output_path):
            print(f"Room {room_idx}: MISSING output file!")
            continue

        with open(output_path, 'r', encoding='utf-8', errors='replace') as f:
            output = f.read()

        print(f"\nRoom {room_idx}: {len(output)} chars")

        backtab_text = extract_backtab_from_output(output)
        if not backtab_text.strip():
            print(f"  NO BACKTAB extracted!")
            print(f"  First 300 chars: {repr(output[:300])}")
            continue

        backtab_grid = parse_backtab(backtab_text)

        gram_text = extract_gram_from_output(output)
        gram_mem = parse_memory_dump(gram_text, 0x3800, 512) if gram_text else {}

        n_bt_lines = len(backtab_text.split('\n'))
        print(f"  BACKTAB: {n_bt_lines} lines, GRAM: {len(gram_mem)} words")

        room_data.append((backtab_grid, gram_mem))

        # Stats
        unique = set()
        for r in range(12):
            for c in range(20):
                card, fg, bg_adv, is_gram = decode_backtab_word(backtab_grid[r][c])
                unique.add((card, is_gram))
        non_floor = sum(1 for r in range(12) for c in range(20) if backtab_grid[r][c] != 0x1603)
        print(f"  Unique cards: {len(unique)}, Non-floor tiles: {non_floor}")

    print(f"\n  Total rooms with data: {len(room_data)}")

    if not room_data:
        print("ERROR: No room data to render!")
        return

    # ---- Render ----
    print()
    print("=" * 70)
    print("  RENDERING ROOMS")
    print("=" * 70)

    zoom = 4
    tile_px = 8 * zoom  # 32px per tile
    room_w = 20 * tile_px  # 640px
    room_h = 12 * tile_px  # 384px

    # Layout: 3 columns x 2 rows
    atlas_cols = 3
    atlas_rows = (len(room_data) + atlas_cols - 1) // atlas_cols
    margin = 8
    label_h = 24

    atlas_w = atlas_cols * room_w + (atlas_cols + 1) * margin
    atlas_h = atlas_rows * (room_h + label_h + margin) + margin

    atlas = Image.new('RGB', (atlas_w, atlas_h), (20, 20, 30))
    atlas_px = atlas.load()
    draw = ImageDraw.Draw(atlas)

    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except Exception:
        font = ImageFont.load_default()

    for i, (backtab_grid, gram_mem) in enumerate(room_data):
        ar = i // atlas_cols
        ac = i % atlas_cols

        xo = margin + ac * (room_w + margin)
        yo = margin + ar * (room_h + label_h + margin)

        draw.text((xo + 4, yo + 2), f"Room {i}", fill=(200, 200, 200), font=font)

        room_img = render_room_image(backtab_grid, gram_mem, grom, zoom=zoom)

        # Paste into atlas
        for y in range(room_h):
            for x in range(room_w):
                r, g, b = room_img.getpixel((x, y))
                atlas_px[xo + x, yo + label_h + y] = (r, g, b)

        # Save individual room PNG
        room_path = os.path.join(ROOMS_DIR, f"dungeon_room_{i}.png")
        room_img.save(room_path)
        print(f"  Room {i}: {room_path}")

    # Save atlas
    atlas_path = os.path.join(SPRITES_DIR, "dungeon_all_rooms.png")
    atlas.save(atlas_path)
    print(f"\n  Atlas: {atlas_path}  ({atlas_w}x{atlas_h}px)")

    # ---- Card Index Grids ----
    print()
    print("=" * 70)
    print("  CARD INDEX GRIDS")
    print("=" * 70)

    for i, (backtab_grid, _) in enumerate(room_data):
        print(f"\nRoom {i} card indices:")
        for row in range(12):
            parts = []
            for col in range(20):
                word = backtab_grid[row][col]
                card, fg, bg_adv, is_gram = decode_backtab_word(word)
                if word == 0x1603:
                    parts.append("  . ")
                else:
                    src = "G" if is_gram else "g"
                    parts.append(f"{card:2d}{src} ")
            print(f"  r{row:2d}: {''.join(parts)}")

    print()
    print("=" * 70)
    print("  DONE")
    print("=" * 70)

if __name__ == '__main__':
    main()
