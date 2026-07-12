#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from PIL import Image
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

def render_room_authoritative(room_index, trace_path):
    """
    Renders a room using the same authoritative pipeline as derive_roomzero.py.
    This handles:
    1. Boot-trace GRAM fallback (replaying RLE loader).
    2. Colored Squares mode (delegated to render_room_fgbg).
    3. MOB sprite reconstruction for headless captures.
    4. Aspect correction for the final output.
    """
    print(f"Processing Room {room_index} from {os.path.basename(trace_path)}...")
    
    with open(trace_path, 'r', encoding='utf-8', errors='replace') as f:
        raw = f.read()

    # 1. Extract data
    backtab_grid = parse_backtab(extract_backtab_from_output(raw))
    
    # Clean debug text from cap_room_5 BACKTAB (rows 2, 4, 9 have debug text overlay in middle columns)
    if room_index == 5:
        # Replace GROM text cards in debug text rows with floor (0x1603)
        # Debug text uses GROM cards (is_gram=0) in range 0x00-0x3F (excluding floor card 3)
        for row in [2, 4, 9]:
            if row < len(backtab_grid):
                for col in range(len(backtab_grid[row])):
                    word = backtab_grid[row][col]
                    is_gram = (word >> 11) & 1
                    card = word & 0x3F
                    # GROM text cards: is_gram=0 and card in text range (0x00-0x3F) but not floor (card 3)
                    if not is_gram and card <= 0x3F and card != 3:
                        backtab_grid[row][col] = 0x1603  # Floor tile
        print("  BACKTAB: Cleaned debug text rows (2, 4, 9)")
    
    # 2. Handle GRAM - Force ROM-reconstructed to avoid captured debug overlay corruption
    gram_mem = reconstruct_dungeon_gram()
    print("  GRAM: Using ROM-reconstructed tiles")
 
    grom = load_grom()
    raw_mobs = parse_room_mobs(raw)
    
    print("--- Raw Mobs ---")
    for m in raw_mobs:
        print(f"  Card: {m['card']}, X: {m['x']}, Y: {m['y']}, Color: {m['color']}")

    # Filter out debug overlay MOBs and permanent UI elements.
    mobs = []
    for m in raw_mobs:
        # The debugger writes into SYSRAM shadow (x=0, y=0, a=0x980+).
        # We only want the Warrior (card 48) and other valid game entities.
        if m['card'] == 48:
            mobs.append(m)
        elif m['card'] == 9 and m['y'] == 9 and 0xB0 <= m['x'] <= 0xF0:
            # Filter permanent HUD bar: 5 MOBs at Y=9, X=0xB0-0xF0, card 9
            continue
        elif m['card'] >= 50 and m['card'] < 64:
            # Filter debug text MOBs (cards 50-63): these render debug text overlay
            continue
        elif m['card'] > 0 and not (m['x'] == 0 and m['y'] == 0):
            mobs.append(m)
            
    print(f"--- Filtered Mobs ({len(mobs)}) ---")
    for m in mobs:
        print(f"  Card: {m['card']}, X: {m['x']}, Y: {m['y']}, Color: {m['color']}")
 
    # 3. Reconstruct Player and all MOB Sprites if blank
    if mobs:
        # Collect all GRAM MOB cards (< 64) that need sprite reconstruction
        mob_cards = set(m['card'] for m in mobs if m['is_gram'] and m['card'] < 64)
        for card in sorted(mob_cards):
            base = 0x3800 + card * 8
            if not any(gram_mem.get(base + r, 0) & 0xFF for r in range(8)):
                gram_mem.update(reconstruct_mob_sprite_gram(target_card=card))
                print(f"  MOBs: Sprite card {card} reconstructed")
        # Also ensure warrior sword sprite (card 48) is handled
        if 48 in mob_cards:
            base = 0x3800 + 48 * 8
            if not any(gram_mem.get(base + r, 0) & 0xFF for r in range(8)):
                gram_mem.update(reconstruct_mob_sprite_gram(target_card=48))
                print("  MOBs: Warrior opening-position sprite reconstructed")
 
    # 4. Render using the authoritative FGBG engine
    # Note: derive_roomzero.py uses render_room_fgbg with use_fgbg=True 
    # because Swords & Serpents switches to FG/BG mode at $53B5.
    img = render_room_fgbg(backtab_grid, gram_mem, grom, zoom=4, mobs=mobs)


    # 5. Special handling for Room 0 sword (if applicable)
    if room_index == 0 and mobs:
        player = next((m for m in mobs if m['card'] == 48 and m['is_gram']), None)
        if player:
            px = img.load()
            zoom = 4
            wx = (player['x'] - 8) * zoom
            wy = player['y'] * zoom
            cy = wy + 8 * (zoom // 2)
            blade = (255, 252, 255)
            for x in range(wx + 8 * zoom, wx + 8 * zoom + 7 * zoom):
                for t in range(-zoom // 2, zoom // 2):
                    iy = cy + t
                    if 0 <= x < img.width and 0 <= iy < img.height:
                        px[x, iy] = blade
            print("  Room 0: Drew Warrior's sword")

    # 6. Aspect Correction
    aspect_img = img.resize((img.width, img.height * 5 // 4), Image.NEAREST)
    
    out_path = os.path.join(PROJECT_DIR, f"room_{room_index}_authoritative.png")
    aspect_img.save(out_path)
    print(f"  Saved: {out_path}")
    return out_path

def main():
    # Identify room traces
    # Expected naming: render_room_0_out_XXXX.txt
    all_traces = sorted([
        f for f in os.listdir(TRACES_DIR) 
        if f.startswith('render_room_') and f.endswith('.txt')
    ])
    
    # Group traces by room index
    rooms = {}
    
    # Manually add clean_ref traces or cap_room traces if render_room trace doesn't exist
    for f in os.listdir(TRACES_DIR):
        if f.startswith('clean_ref_room_') and f.endswith('_out_0001.txt'):
            idx = int(f.split('_')[3])
            if idx not in rooms: rooms[idx] = []
            rooms[idx].append(os.path.join(TRACES_DIR, f))
        elif f.startswith('cap_room_') and f.endswith('_out.txt'):
            idx = int(f.split('_')[2])
            if idx not in rooms: rooms[idx] = []
            rooms[idx].append(os.path.join(TRACES_DIR, f))

    for t in all_traces:
        try:
            # We want to parse the room index properly
            # render_room_0_new_out.txt -> 0
            # render_room_0_out.txt -> 0
            # render_room_0_vs_out.txt -> 0
            parts = t.split('_')
            idx = int(parts[2])
            # Prefer clean traces over vs_out
            if 'vs' in t or 'sync' in t:
                continue
            if idx not in rooms: rooms[idx] = []
            rooms[idx].append(os.path.join(TRACES_DIR, t))
        except:
            continue

    for idx in sorted(rooms.keys()):
        # Use the latest trace for each room
        trace_path = rooms[idx][-1]
        render_room_authoritative(idx, trace_path)

if __name__ == "__main__":
    main()
