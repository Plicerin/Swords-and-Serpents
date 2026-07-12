#!/usr/bin/env python3
"""Parse jzIntv dump state output, decode BackTab + GRAM, render title screen."""

import re
import struct

def read_rom_decle(rom, addr):
    """Read a 16-bit DECLE from ROM at given CP1610 address."""
    off = (addr - 0x5000) * 2
    if off + 1 < len(rom):
        return (rom[off] << 8) | rom[off + 1]
    return None

def read_word_at_offset(rom, file_offset):
    """Read big-endian 16-bit word from raw ROM bytes at file offset."""
    if file_offset + 1 < len(rom):
        return (rom[file_offset] << 8) | rom[file_offset + 1]
    return None

# ─── Parse jzIntv output ───────────────────────────────────────────────

def parse_hex_dump(text, start_addr, end_addr):
    """Parse a jzIntv 'm' command hex dump from text.
    Returns dict {address: 16-bit value}."""
    data = {}
    in_section = False
    for line in text.split('\n'):
        line = line.strip()
        # Look for the start of the dump section
        if line.startswith(f'{start_addr:04X}:'):
            in_section = True
        if not in_section:
            continue
        # Parse lines like "0200:  1603* 1603  1603  1603   1603  1603  1603  1603"
        parts = line.split()
        if not parts or ':' not in parts[0]:
            continue
        addr_str = parts[0].replace(':', '').replace('*', '')
        try:
            addr = int(addr_str, 16)
        except ValueError:
            continue
        if addr > end_addr:
            break
        for part in parts[1:]:
            part = part.replace('*', '')
            if part == '#':
                break
            try:
                val = int(part, 16)
                data[addr] = val
                addr += 1
            except ValueError:
                break
        if addr > end_addr:
            break
    return data

# ─── Color decoding ─────────────────────────────────────────────────────

# Intellivision 16-color palette (STIC primary set)
INTV_COLORS = {
    0:  (0, 0, 0),       # Black
    1:  (0, 0, 255),     # Blue
    2:  (255, 0, 0),     # Red
    3:  (210, 180, 140), # Tan
    4:  (0, 128, 0),     # Dark Green
    5:  (0, 255, 0),     # Green
    6:  (255, 255, 0),   # Yellow
    7:  (128, 128, 128), # Grey (White in some contexts)
    8:  (64, 64, 64),    # Dark Grey
    9:  (100, 100, 255), # Light Blue
    10: (255, 128, 128), # Light Red
    11: (255, 210, 160), # Light Tan
    12: (100, 255, 100), # Light Green
    13: (180, 255, 180), # Pale Green
    14: (255, 255, 128), # Light Yellow
    15: (255, 255, 255), # White
}

COLOR_NAMES = [
    "Black", "Blue", "Red", "Tan", "DarkGreen", "Green",
    "Yellow", "Grey", "DarkGrey", "LtBlue", "LtRed",
    "LtTan", "LtGreen", "PaleGreen", "LtYellow", "White"
]

# ─── BackTab decoding (Color Stack mode) ────────────────────────────────

def decode_backtab(word):
    """Decode an IntelliVision Color Stack mode BackTab word."""
    cs_advance = (word >> 14) & 3      # Color Stack advance counter
    grom_flag = (word >> 13) & 1       # 1=GROM, 0=GRAM
    pastel = (word >> 12) & 1          # Pastel color bit
    bg_color = (word >> 9) & 7         # Background color (foreground mode)
    fg_color = (word >> 6) & 7         # Foreground color
    card_num = word & 0x3F             # Card number (0-63)
    gram_flag2 = (word >> 6) & 1       # Alternate GRAM flag (bit 6 in some docs)
    # Actually GRAM card = bits 5-0, bit 6 might be something else
    return {
        'cs_advance': cs_advance,
        'grom': grom_flag,
        'pastel': pastel,
        'bg_color': bg_color,
        'fg_color': fg_color,
        'card': card_num,
        'raw': word,
    }

# ─── GRAM card pixel rendering ──────────────────────────────────────────

def gram_card_to_pixels(gram_data, card_num):
    """Convert GRAM card data to 8x8 pixel array (1=white, 0=black).
    Each card is 8 bytes (one per row), MSB-first within each byte."""
    card_offset = card_num * 8
    pixels = []
    for row in range(8):
        byte_val = gram_data[card_offset + row] if card_offset + row < len(gram_data) else 0
        row_pixels = []
        for b in range(7, -1, -1):
            row_pixels.append(1 if (byte_val >> b) & 1 else 0)
        pixels.append(row_pixels)
    return pixels

def grom_card_to_pixels(grom_data, card_num):
    """Convert GROM card data to 8x8 pixel array."""
    card_offset = card_num * 8
    pixels = []
    for row in range(8):
        byte_val = grom_data[card_offset + row] if card_offset + row < len(grom_data) else 0
        row_pixels = []
        for b in range(7, -1, -1):
            row_pixels.append(1 if (byte_val >> b) & 1 else 0)
        pixels.append(row_pixels)
    return pixels

# ─── Room data extraction from ROM ──────────────────────────────────────

def extract_room_data_table(rom):
    """Extract the room data table at $5617.
    L_55F7 reads: G_019C * 2 + $5617, then every 4 words.
    For each room: 4 words (8 bytes) of init data.
    
    Actually: SDBD; ADDI #$5617, R1 means R1 = G_019C + $5617 (word address)
    Then reads at +0, +4, +8, +12 words from that address.
    So each room entry is at $5617 + room_index*2 + 0/4/8/12
    """
    print("\n=== Room Data Table at $5617 ===")
    # Try to find how many rooms by reading through the data
    # The table is embedded in code at $5617-$5626 area
    
    # Let's look at ROM data directly
    # L_55F7 reads from G_019C + $5617
    # For room 0: read from $5617, $561B, $561F, $5623
    base = 0x5617
    for room in range(8):
        addr = base + room * 2  # word offset from base
        w1 = read_rom_decle(rom, addr)
        w2 = read_rom_decle(rom, addr + 4)
        w3 = read_rom_decle(rom, addr + 8)
        w4 = read_rom_decle(rom, addr + 12)
        print(f"  Room {room}: ${addr:04X} → "
              f"${w1:04X} ${w2:04X} ${w3:04X} ${w4:04X}")
    
    # Also check what G_0184-G_0187 ($0184-$0187) and G_02F2 ($02F2-$02F3) are used for
    # These are loaded with room-specific data
    return

# ─── Main ────────────────────────────────────────────────────────────────

def main():
    # Read ROM
    with open('Swords and Serpents.bin', 'rb') as f:
        rom = f.read()
    
    # Read GROM
    with open('grom.bin', 'rb') as f:
        grom = f.read()
    
    # Read jzIntv output
    try:
        with open('jzintv_dump_state.txt', 'r', encoding='utf-8', errors='replace') as f:
            dump_text = f.read()
    except FileNotFoundError:
        print("jzintv_dump_state.txt not found, checking jzintv_room_v2.txt...")
        with open('jzintv_room_v2.txt', 'r', encoding='utf-8', errors='replace') as f:
            dump_text = f.read()
    
    # Parse BackTab ($0200-$02EF)
    print("Parsing BackTab...")
    backtab = parse_hex_dump(dump_text, 0x0200, 0x02EF)
    print(f"  Found {len(backtab)} BackTab entries")
    
    # Parse GRAM ($3800-$39FF)
    print("Parsing GRAM...")
    gram = parse_hex_dump(dump_text, 0x3800, 0x39FF)
    print(f"  Found {len(gram)} GRAM entries")
    
    # Convert GRAM to byte array (low byte only, since GRAM is 8-bit)
    gram_bytes = bytearray(512)
    for addr, val in sorted(gram.items()):
        off = addr - 0x3800
        if off < 512:
            gram_bytes[off] = val & 0xFF
    
    # ─── Analyze BackTab ───
    print("\n=== BackTab Analysis (Title Screen) ===")
    
    # Find non-background tiles
    bg_tile = 0x1603  # The fill tile used for most of the screen
    unique_tiles = {}
    for addr in sorted(backtab.keys()):
        val = backtab[addr]
        if val != bg_tile:
            row = (addr - 0x0200) // 20
            col = (addr - 0x0200) % 20
            if val not in unique_tiles:
                unique_tiles[val] = []
            unique_tiles[val].append((row, col, addr))
            dec = decode_backtab(val)
            print(f"  ${addr:04X} (r{row:2d},c{col:2d}): ${val:04X} → "
                  f"card=${dec['card']:2d} fg={COLOR_NAMES[dec['fg_color']]} "
                  f"bg={COLOR_NAMES[dec['bg_color']]} cs_adv={dec['cs_advance']}")
    
    print(f"\n  Background tile ${bg_tile:04X}:")
    dec = decode_backtab(bg_tile)
    print(f"    card={dec['card']} fg={COLOR_NAMES[dec['fg_color']]} "
          f"bg={COLOR_NAMES[dec['bg_color']]} cs_adv={dec['cs_advance']}")
    
    # ─── Render title screen text grid ───
    print("\n=== Title Screen Grid (20×12) ===")
    for row in range(12):
        line = ''
        for col in range(20):
            addr = 0x0200 + row * 20 + col
            val = backtab.get(addr, 0)
            if val == bg_tile:
                line += '.'
            else:
                line += '#'
        print(f"  {line}")
    
    # ─── Show used GRAM cards ───
    gram_cards_used = set()
    for addr, val in backtab.items():
        dec = decode_backtab(val)
        if not dec['grom']:
            gram_cards_used.add(dec['card'])
    
    print(f"\n  GRAM cards used: {sorted(gram_cards_used)}")
    
    # Show pixel patterns for key GRAM cards
    print("\n=== Key GRAM Card Patterns ===")
    for card in sorted(gram_cards_used)[:4]:
        print(f"\n  GRAM card {card}:")
        pixels = gram_card_to_pixels(gram_bytes, card)
        for row_pixels in pixels:
            line = '  ' + ''.join('#' if p else '.' for p in row_pixels)
            print(line)
    
    # ─── Show key GROM cards ───
    print("\n=== Key GROM Card Patterns (font) ===")
    for card in [0, 1, 3, 15, 19, 27, 32, 35, 43, 51, 59, 63]:
        print(f"\n  GROM card {card}:")
        pixels = grom_card_to_pixels(grom, card)
        for row_pixels in pixels:
            line = '  ' + ''.join('#' if p else '.' for p in row_pixels)
            print(line)
    
    # ─── Render title screen as colored PNG ───
    print("\n=== Rendering title screen to PNG ===")
    try:
        from PIL import Image
        
        W = 20 * 8
        H = 12 * 8
        img = Image.new('RGB', (W, H), (0, 0, 0))
        
        for row in range(12):
            for col in range(20):
                addr = 0x0200 + row * 20 + col
                val = backtab.get(addr, bg_tile)
                dec = decode_backtab(val)
                
                fg_rgb = INTV_COLORS.get(dec['fg_color'], (128,128,128))
                bg_rgb = INTV_COLORS.get(dec['bg_color'], (0,0,0))
                
                # Get card pixels
                if dec['grom']:
                    card_pixels = grom_card_to_pixels(grom, dec['card'])
                else:
                    card_pixels = gram_card_to_pixels(gram_bytes, dec['card'])
                
                for py in range(8):
                    for px in range(8):
                        x = col * 8 + px
                        y = row * 8 + py
                        if card_pixels[py][px]:
                            img.putpixel((x, y), fg_rgb)
                        else:
                            img.putpixel((x, y), bg_rgb)
        
        img.save('title_screen_from_dump.png')
        print(f"  Saved title_screen_from_dump.png ({W}x{H})")
        
    except ImportError:
        print("  PIL not available, skipping PNG render")
    
    # ─── Extract room data from ROM ───
    extract_room_data_table(rom)
    
    # ─── Room data analysis from disassembly ───
    print("\n=== Room Data Analysis ===")
    print("L_55F7 loads 4 words per room:")
    print("  $0184-$0185: unknown params (possibly room tile set)")
    print("  $0186: unknown param")
    print("  $02F2-$02F3: unknown param (stored twice)")
    
    # Check what writes to $0184 and $02F2
    # These are in 16-bit RAM ($0100-$035F = System RAM)
    print("\nRoom data loaded into variables:")
    print("  G_0184 ($0184) - loaded from room table")
    print("  G_0185 ($0185) - loaded from room table") 
    print("  G_0186 ($0186) - loaded from room table")
    print("  G_02F2 ($02F2) - loaded from room table, stored twice")

if __name__ == '__main__':
    main()
