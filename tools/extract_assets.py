#!/usr/bin/env python3
"""
Swords & Serpents — Asset Extractor for JS Port

Extracts game assets from ROM and trace files for use in the JavaScript port:
- palette.json: 16-color Intellivision palette as [R,G,B] triples
- grom.bin: Copy of GROM character ROM
- gram_tiles.json: GRAM tiles reconstructed from ROM RLE data
- rooms.json: BACKTAB data for rooms 0-5 from trace files
"""
import json
import os
import re
import shutil

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
GROM_PATH = os.path.join(PROJECT_ROOT, "grom.bin")
ROM_PATH = os.path.join(PROJECT_ROOT, "Swords and Serpents.bin")
TRACES_DIR = os.path.join(PROJECT_ROOT, "traces", "rooms")

# Trace file paths for rooms 0-5
# Trace files for rooms 0-5
# NOTE: cap_room_4/5 traces have debug text overlay that needs cleaning.
# Per DUNGEON_MAP_DOCUMENTATION.md, rooms 4/5 use same templates as 0/1.
ROOM_TRACE_FILES = [
    os.path.join(TRACES_DIR, "render_room_0_out.txt"),
    os.path.join(TRACES_DIR, "render_room_1_out.txt"),
    os.path.join(TRACES_DIR, "render_room_2_out.txt"),
    os.path.join(TRACES_DIR, "render_room_3_out.txt"),
    os.path.join(TRACES_DIR, "clean_ref_room_4_out_0001.txt"),  # Clean trace, room 0 template
    os.path.join(TRACES_DIR, "clean_ref_room_5_out_0001.txt"),  # Clean trace, room 1 template
]

# Rows/columns that contain debug text overlay (need cleaning)
# Debug text uses GROM cards (is_gram=0) - replace with floor tile 0x1603
# Row indices are 0-based (row N = BACKTAB addresses 0x0200 + N*20)
DEBUG_TEXT_REGIONS = {
    4: [(5, range(8, 20)), (6, range(8, 20)), (7, range(8, 14)),
        (10, range(8, 20)), (11, range(8, 20)), (12, range(8, 14))],
    # clean_ref_room_5_out_0001.txt debug text cleaning:
    5: [(2, range(0, 20)), (4, range(0, 20)), (9, range(0, 20))],
}

# -- Authoritative jzIntv palette -------------------------------------------
# The 16 STIC colors exactly as defined in jzIntv's renderer
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


def extract_palette():
    """Export the 16-color jzIntv palette as JSON array of [R,G,B] triples."""
    palette = [list(rgb) for rgb in JZINTV_PALETTE]
    output_path = os.path.join(ASSETS_DIR, "palette.json")
    with open(output_path, "w") as f:
        json.dump(palette, f, indent=2)
    print(f"Created: {output_path} ({len(palette)} colors)")
    return output_path


def extract_grom():
    """Copy grom.bin to assets directory."""
    output_path = os.path.join(ASSETS_DIR, "grom.bin")
    shutil.copy(GROM_PATH, output_path)
    size = os.path.getsize(output_path)
    print(f"Created: {output_path} ({size} bytes)")
    return output_path


def extract_gram_tiles():
    """Extract GRAM tiles from ROM RLE data as flat array of 512 bytes."""
    gram_mem = reconstruct_dungeon_gram()
    
    # Convert dict {addr: byte} to flat array of 512 bytes
    # GRAM has 64 cards × 8 bytes = 512 bytes
    # Addresses are 0x3800-based
    gram_array = [0] * 512
    for addr, byte in gram_mem.items():
        index = addr - 0x3800
        if 0 <= index < 512:
            gram_array[index] = byte
    
    output_path = os.path.join(ASSETS_DIR, "gram_tiles.json")
    with open(output_path, "w") as f:
        json.dump(gram_array, f)
    
    # Count non-zero cards
    non_zero_cards = sum(1 for i in range(64) if any(gram_array[i*8:(i+1)*8]))
    print(f"Created: {output_path} ({len(gram_array)} bytes, {non_zero_cards} non-zero cards)")
    return output_path


def extract_backtab_from_trace(trace_text):
    """Extract BACKTAB memory section from trace file text.
    
    BACKTAB is at 0x0200-0x02EF (240 words = 20 cols × 12 rows).
    """
    # Find the BACKTAB dump section (starts with "0200:")
    lines = trace_text.split('\n')
    backtab_lines = []
    in_backtab = False
    
    for line in lines:
        stripped = line.strip()
        if re.match(r'^0200:', stripped):
            in_backtab = True
        if in_backtab:
            # Stop when we hit addresses outside BACKTAB range
            m = re.match(r'^([0-9A-F]{4}):', stripped)
            if m:
                addr = int(m.group(1), 16)
                if addr >= 0x02F0:
                    break
            backtab_lines.append(line)
    
    return '\n'.join(backtab_lines)


def clean_debug_text(room_data, room_index):
    """Clean debug text overlay from BACKTAB data.
    
    Debug text uses GROM cards (bit 11 = 0) for text characters.
    Replace with floor tile 0x1603.
    """
    if room_index not in DEBUG_TEXT_REGIONS:
        return room_data
    
    cleaned = room_data.copy()
    floor_tile = 0x1603
    
    for row, cols in DEBUG_TEXT_REGIONS[room_index]:
        for col in cols:
            idx = row * 20 + col
            if idx < len(cleaned):
                word = cleaned[idx]
                is_gram = (word >> 11) & 1
                # If it's a GROM card (not GRAM) and not already floor, replace it
                if not is_gram and word != floor_tile:
                    cleaned[idx] = floor_tile
    
    return cleaned


def extract_rooms():
    """Extract BACKTAB data for rooms 0-5 from trace files."""
    rooms = []
    
    for i, trace_path in enumerate(ROOM_TRACE_FILES):
        if not os.path.exists(trace_path):
            print(f"  WARNING: Trace file not found: {trace_path}")
            rooms.append([0] * 240)
            continue
        
        with open(trace_path, 'r', encoding='utf-8', errors='replace') as f:
            trace_text = f.read()
        
        # Extract BACKTAB section
        backtab_text = extract_backtab_from_trace(trace_text)
        if not backtab_text:
            print(f"  WARNING: No BACKTAB data in {trace_path}")
            rooms.append([0] * 240)
            continue
        
        # Parse into memory dict
        mem = parse_memory_dump(backtab_text, 0x0200, 240)
        
        # Convert to flat array of 240 words
        room_data = []
        for addr in range(0x0200, 0x02F0):
            room_data.append(mem.get(addr, 0))
        
        # Clean debug text overlay if needed
        if i in DEBUG_TEXT_REGIONS:
            room_data = clean_debug_text(room_data, i)
            print(f"  Room {i}: {len(room_data)} words from {os.path.basename(trace_path)} (debug text cleaned)")
        else:
            print(f"  Room {i}: {len(room_data)} words from {os.path.basename(trace_path)}")
        
        rooms.append(room_data)
    
    output_path = os.path.join(ASSETS_DIR, "rooms.json")
    with open(output_path, "w") as f:
        json.dump({"rooms": rooms}, f)
    
    print(f"Created: {output_path} ({len(rooms)} rooms)")
    return output_path


def main():
    print("=" * 60)
    print("  SWORDS & SERPENTS — ASSET EXTRACTOR")
    print("=" * 60)
    print()
    
    # Create assets directory
    os.makedirs(ASSETS_DIR, exist_ok=True)
    print(f"Output directory: {ASSETS_DIR}")
    print()
    
    # Extract all assets
    print("Extracting assets...")
    print("-" * 40)
    
    extract_palette()
    extract_grom()
    extract_gram_tiles()
    
    print()
    print("Extracting room data...")
    print("-" * 40)
    extract_rooms()
    
    print()
    print("=" * 60)
    print("  DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()
