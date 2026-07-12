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
from PIL import Image

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ROM_PATH = os.path.join(PROJECT_DIR, "Swords and Serpents.bin")
GROM_PATH = os.path.join(PROJECT_DIR, "grom.bin")
EXEC_PATH = os.path.join(PROJECT_DIR, "exec.bin")
JZINTV = os.path.join(PROJECT_DIR, "jzintv-20200712-win32-sdl2", "bin", "jzintv.exe")
TRACES_DIR = os.path.join(PROJECT_DIR, "traces")
SPRITES_DIR = os.path.join(PROJECT_DIR, "sprites")

NUM_ROOMS = 6  # rooms 0-5

# G_02F4 base: $65DC for room 0, increments by 8 per room (from L_6725)
G_02F4_BASE = 0x65DC

# IMPORTANT: G_0175 and G_0176 are hardcoded at boot ($55CF-$55D5) as 2 and 26.
# These values are correct for the initial renderer — DO NOT patch them.
# The per-room variation comes solely from G_02F4 (data pointer offset).
# The L_59FF function only runs on ROOM TRANSITIONS, not initial boot.

# Force headless SDL — critical for subprocess capture
SDL_ENV = os.environ.copy()
SDL_ENV["SDL_VIDEODRIVER"] = "dummy"
SDL_ENV["SDL_AUDIODRIVER"] = "dummy"

# -- Intellivision palette --------------------------------------------------
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

# NOP X_FILL_MEM at $5638-$5639 — prevents title screen from wiping BACKTAB
# JSR R5, X_FILL_MEM is a 2-word instruction (opcode + immediate address)
X_FILL_MEM_NOP = [
    (0x5638, 0x0034),  # NOP the JSR R5 opcode
    (0x5639, 0x0034),  # NOP the X_FILL_MEM address
]


def generate_debugger_script(room_index, output_path):
    """
    Generate a jzIntv debugger script that:
    1. Patches idle loops for speed
    2. NOPs X_FILL_MEM at $5638 to prevent title screen from wiping BACKTAB
    3. Patches G_02F4 immediate with per-room pointer ($65DC + room*8)
    4. Writes G_018C=1 to force game past title screen
    5. Runs 8M cycles past boot and dumps BACKTAB + GRAM

    STRATEGY: The game boots → renders dungeon at $55DA → title screen code
    wipes BACKTAB via X_FILL_MEM at $5638. We NOP that wipe, write G_018C=1
    to skip the title screen idle loop, and the game enters gameplay where it
    re-renders the dungeon with proper per-room GRAM graphics.
    """
    g_02f4 = G_02F4_BASE + room_index * 8

    lines = []
    lines.append(f"; Auto-generated script for room {room_index}")
    lines.append(f";   G_02F4 = ${g_02f4:04X}")
    lines.append("")

    # Idle patches
    for addr, val in IDLE_PATCHES:
        lines.append(f"p {addr:04X} {val:04X}")
    lines.append("")

    # NOP X_FILL_MEM at $5638-$563A to prevent BACKTAB wipe
    lines.append("; NOP X_FILL_MEM — prevents title screen from wiping BACKTAB")
    for addr, val in X_FILL_MEM_NOP:
        lines.append(f"p {addr:04X} {val:04X}")
    lines.append("")

    # Patch G_02F4 immediate at $55C5-$55C6 (MVII #$65DC, R0 with SDBD)
    # The value is stored as two 16-bit words (lo, hi) due to SDBD
    lines.append(f"; Patch G_02F4 to ${g_02f4:04X} (was $65DC)")
    lines.append(f"p 55C5 {g_02f4 & 0xFF:04X}")
    lines.append(f"p 55C6 {(g_02f4 >> 8) & 0xFF:04X}")
    lines.append("")

    # Write G_018C = 1 in scratch RAM to force 1-player game start
    # This bypasses the title screen idle loop at $56C9 (MVI G_018C, R0; BEQ ...)
    lines.append("; Write G_018C=1 to force past title screen into gameplay")
    lines.append("w 018C 0001")
    lines.append("")

    # Run for enough cycles to get past boot, title screen, and render the room
    lines.append("; Run past boot + title screen into gameplay")
    lines.append("r 8000000")
    lines.append("")

    # Dump BACKTAB ($0200-$02EF = 240 words)
    lines.append("; Dump BACKTAB")
    lines.append("m 0200 240")
    lines.append("")

    # Dump GRAM ($3800-$39FF = 512 words)
    lines.append("; Dump GRAM")
    lines.append("m 3800 512")
    lines.append("")

    # Dump color stack registers ($0028-$002B = 4 words)
    lines.append("; Dump STIC color stack")
    lines.append("m 0028 4")
    lines.append("")

    # Quit
    lines.append("q")

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    print(f"  Generated: {output_path}")


def run_debugger_script(script_path, output_path):
    """Run jzIntv with a debugger script and capture output via file redirection."""
    cmd = [
        JZINTV, "-d",
        f"--script={script_path}",
        "-e", EXEC_PATH,
        "-g", GROM_PATH,
        ROM_PATH,
    ]
    print(f"  Running: jzintv (headless) with script={os.path.basename(script_path)} ...")
    try:
        with open(output_path, 'w', encoding='utf-8', errors='replace') as out_f:
            proc = subprocess.Popen(
                cmd,
                stdout=out_f,
                stderr=subprocess.STDOUT,
                env=SDL_ENV,
                cwd=PROJECT_DIR,
            )
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
    """Decode BACKTAB word: (card_index, fg_color, bg_advance, is_gram)."""
    fg = (word >> 12) & 0x7
    is_gram = (word >> 11) & 1
    card = (word >> 3) & 0xFF
    if is_gram:
        card = card & 0x3F
    bg_adv = word & 0x7
    return card, fg, bg_adv, is_gram


def load_grom():
    """Load GROM character ROM (256 cards × 8 bytes)."""
    with open(GROM_PATH, 'rb') as f:
        return f.read()


def get_grom_card_bytes(grom, card_index):
    """Return 8 bytes for GROM card 0-255."""
    base = card_index * 8
    if base + 8 <= len(grom):
        return grom[base:base+8]
    return bytes(8)


def render_card_1bpp(card_bytes, fg_color_idx, bg_color=DEFAULT_BG):
    """Render an 8×8 card in 1bpp Color Stack mode.
    
    In Color Stack mode, FG=0 is BLACK (palette entry 0), not transparent.
    The background color comes from the color stack, not from the FG field.
    """
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
    """Render a GRAM card (lo byte only, 1bpp)."""
    base = 0x3800 + card_index * 8
    card_bytes = bytes(gram_mem.get(base + row, 0) & 0xFF for row in range(8))
    return render_card_1bpp(card_bytes, fg_color_idx, bg_color)


def render_grom_card(grom, card_index, fg_color_idx, bg_color=DEFAULT_BG):
    """Render a GROM card from grom.bin."""
    card_bytes = get_grom_card_bytes(grom, card_index)
    return render_card_1bpp(card_bytes, fg_color_idx, bg_color)


def render_room_image(backtab_grid, gram_mem, grom, color_stack=None, zoom=4):
    """Render a single room (12×20 tiles) as a PIL Image.
    
    Args:
        color_stack: Optional list of 4 RGB tuples for the STIC color stack.
                     If None, defaults to black for all entries.
    """
    cols, rows = 20, 12
    tile_size = 8
    img = Image.new('RGB', (cols * tile_size * zoom, rows * tile_size * zoom))
    px = img.load()
    # Color stack from STIC registers $0028-$002B, or default to black
    if color_stack is None or len(color_stack) < 4:
        color_stack = [DEFAULT_BG] * 4
    cs_index = 0
    bg = color_stack[0]

    for row in range(rows):
        for col in range(cols):
            word = backtab_grid[row][col]
            card_idx, fg, bg_adv, is_gram = decode_backtab_word(word)

            # Advance color stack before rendering this tile
            # (STIC advances by bg_adv after each card)
            bg = color_stack[cs_index % 4]
            cs_index = (cs_index + bg_adv) % 4

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
    
    Each word at $0028-$002B encodes a color in the low 4 bits
    (0-7 for foreground colors, 8-15 for pastel colors).
    
    NOTE: jzIntv may not correctly emulate reading STIC registers.
    If all reads return $3FFx (power-on defaults), we fall back to
    hardcoded dungeon-appropriate colors.
    """
    mem = parse_memory_dump(text, 0x0028, 4)
    colors = []
    all_default = True
    for addr in range(0x0028, 0x002C):
        val = mem.get(addr, 0)
        # Detect STIC power-on default pattern ($3FFx)
        if (val & 0xFFF0) != 0x3FF0:
            all_default = False
        color_idx = val & 0x7  # low 3 bits = color index (same as BACKTAB FG)
        is_pastel = (val & 0x8) != 0  # bit 3: pastel/luminance flag
        base = PALETTE.get(color_idx, DEFAULT_BG)
        if is_pastel:
            colors.append(tuple(c // 2 for c in base))
        else:
            colors.append(base)
    
    # If all registers show STIC power-on defaults, or dump is missing/incomplete,
    # use hardcoded dungeon-appropriate colors
    if not mem or all_default or len(colors) < 4:
        # Dungeon color stack: black (ceiling), tan (wall bg), blue (accent), black
        # Based on the only non-zero STIC read showing color 3 (tan) at $0029
        DUNGEON_COLORS = [
            PALETTE[0],   # CS0: black — ceiling/void
            PALETTE[3],   # CS1: tan/orange — wall background
            PALETTE[1],   # CS2: blue — accent
            PALETTE[0],   # CS3: black — default
        ]
        return list(DUNGEON_COLORS)
    return colors


def main():
    os.makedirs(TRACES_DIR, exist_ok=True)
    os.makedirs(SPRITES_DIR, exist_ok=True)

    print("=" * 70)
    print("  SWORDS & SERPENTS — ALL ROOMS RENDERER")
    print("=" * 70)
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

    room_data = []  # list of (backtab_grid, gram_mem)

    for room_idx in range(NUM_ROOMS):
        print(f"\n  Room {room_idx}:")

        script_path = os.path.join(TRACES_DIR, f"render_room_{room_idx}.txt")
        output_path = os.path.join(TRACES_DIR, f"render_room_{room_idx}_out.txt")

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

        room_data.append((backtab_grid, gram_mem, color_stack))

        # Quick stats
        unique_cards = set()
        for row in range(12):
            for col in range(20):
                card, fg, bg_adv, is_gram = decode_backtab_word(backtab_grid[row][col])
                unique_cards.add((card, is_gram))
        non_floor = sum(1 for r in range(12) for c in range(20) if backtab_grid[r][c] != 0x1603)
        print(f"  BACKTAB: {len(unique_cards)} unique cards, {non_floor} non-floor tiles")

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

    for i, (backtab_grid, gram_mem, color_stack) in enumerate(room_data):
        atlas_row = i // atlas_cols
        atlas_col = i % atlas_cols

        x_offset = margin + atlas_col * (room_w + margin)
        y_offset = margin + atlas_row * (room_h + label_h + margin)

        # Draw room label
        draw.text((x_offset + 4, y_offset + 2), f"Room {i}", fill=(200, 200, 200), font=font)

        # Render room
        room_img = render_room_image(backtab_grid, gram_mem, grom, color_stack=color_stack, zoom=zoom)

        # Paste into atlas
        for y in range(room_h):
            for x in range(room_w):
                r, g, b = room_img.getpixel((x, y))
                atlas_px[x_offset + x, y_offset + label_h + y] = (r, g, b)

        # Save individual room
        room_path = os.path.join(SPRITES_DIR, f"dungeon_room_{i}.png")
        room_img.save(room_path)
        print(f"  Room {i}: saved {room_path}")

    # Save atlas
    atlas_path = os.path.join(SPRITES_DIR, "dungeon_all_rooms.png")
    atlas.save(atlas_path)
    print(f"\n  Atlas: saved {atlas_path}  ({atlas_w}×{atlas_h}px)")

    # Phase 3: Print card grids for each room
    print()
    print("-" * 70)
    print("  PHASE 3: Card index grids")
    print("-" * 70)

    for i, (backtab_grid, _, _) in enumerate(room_data):
        print(f"\n  Room {i} card indices:")
        for row in range(12):
            line = ""
            for col in range(20):
                word = backtab_grid[row][col]
                card, fg, bg_adv, is_gram = decode_backtab_word(word)
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
