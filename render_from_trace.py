import numpy as np
from PIL import Image
import os

# --- Constants ---
COLORS = {
    'BG_TAN': (210, 180, 140),
    'WALL_DARK': (60, 60, 60),
    'FLOOR_LIGHT': (180, 160, 130),
    'DOOR_GOLD': (218, 165, 32),
    'WATER_BLUE': (0, 105, 148),
    'TEXT_WHITE': (255, 255, 255),
    'VOID': (0, 0, 0)
}

def get_tile_type(word):
    if word == '1603': return 'FLOOR'
    if word == '081B': return 'WALL'
    if word == '082B': return 'WALL_EDGE'
    if word == '0823': return 'WALL_CORNER'
    if word == '0833': return 'WALL_INNER'
    if word == '1E38': return 'FEATURE_1'
    if word == '1E0B': return 'FEATURE_2'
    if word == '1E40': return 'FEATURE_3'
    if word == '1E13': return 'FEATURE_4'
    if word == '5E5B': return 'DOOR'
    if word == '0980': return 'WATER'
    if word == '0990': return 'WATER'
    if word == '09A0': return 'WATER'
    if word == '09B0': return 'WATER'
    if word == '09C0': return 'WATER'
    if word == '09D0': return 'WATER'
    if word == '09E0': return 'WATER'
    if word == '09F0': return 'WATER'
    if word == '5014': return 'PLAYER_START'
    if word == '106C': return 'NPC_START'
    if word == '500C': return 'EXIT'
    if word == '1E7D': return 'TREASURE'
    if word == '65DC': return 'STAIR_UP'
    if word == '65B7': return 'STAIR_DOWN'
    if word == '0000': return 'VOID'
    return 'UNKNOWN'

def render_from_trace(trace_file):
    img = Image.new('RGB', (256, 256), COLORS['VOID'])
    pixels = img.load()

    with open(trace_file, 'r') as f:
        lines = f.readlines()

    start_idx = -1
    for i, line in enumerate(lines):
        if "Dump BACKTAB" in line:
            start_idx = i + 1
            break
    
    if start_idx == -1:
        print("Could not find BACKTAB dump.")
        return

    # We are looking for the block starting at 0200
    # The dump shows 8 words per line.
    # If 0200 is the start of a 16-byte row (8 words),
    # then 0210 would be the next row. 0208 is a 4-word partial row.
    
    # We will map each row to a 32x32 tile in the 256x256 image.
    # There are 8 columns per row.
    # Max width = 8 * 32 = 256.
    
    # We'll use a dictionary to store the 0200 block
    # key: address, value: list of words
    data_block = {}
    
    for i in range(start_idx, len(lines)):
        line = lines[i].strip()
        if not line or ">" in line or "Dump" in line or "GRAM" in line:
            continue
        
        parts = line.split(':')
        if len(parts) < 2: continue
        
        addr_part = parts[0].strip()
        words_part = parts[1].split('#')[0].strip()
        words = words_part.split()
        
        try:
            addr = int(addr_part, 16)
            if 0x0200 <= addr <= 0x035F:
                data_block[addr] = words
        except:
            continue

    # Sort addresses to ensure we draw in order
    sorted_addrs = sorted(data_block.keys())
    
    # The rows are every 16 bytes (0200, 0210, 0220...)
    # Let's map these specifically.
    for addr in sorted_addrs:
        # Calculate row index: (addr - 0x0200) / 16
        row_idx = (addr - 0x0200) // 16
        words = data_block[addr]
        
        # If the row has 8 words, it's a full row
        if len(words) == 8:
            for col_idx, word in enumerate(words):
                tile_type = get_tile_type(word)
                if tile_type == 'VOID': continue
                
                # Draw 32x32 blocks
                img_x = col_idx * 32
                img_y = row_idx * 32
                
                if img_x < 256 and img_y < 256:
                    color = COLORS.get(tile_type, COLORS['FLOOR_LIGHT'])
                    if 'WALL' in tile_type:
                        color = COLORS['WALL_DARK']
                    elif 'WATER' in tile_type:
                        color = COLORS['WATER_BLUE']
                    elif 'DOOR' in tile_type:
                        color = COLORS['DOOR_GOLD']
                    elif 'TREASURE' in tile_type:
                        color = COLORS['DOOR_GOLD']
                    
                    for dy in range(32):
                        for dx in range(32):
                            if img_x + dx < 256 and img_y + dy < 256:
                                pixels[img_x + dx, img_y + dy] = color

    img.save(r"C:\Users\vrock\Documents\Swords and Serpents\trace_render_test.png")
    print(f"Rendered {len(sorted_addrs)} address blocks to trace_render_test.png")

render_from_trace("C:/Users/vrock/Documents/Swords and Serpents/traces/rooms/render_room_0_out_0001.txt")

