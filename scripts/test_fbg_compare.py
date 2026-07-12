#!/usr/bin/env python3
"""Fresh capture + render + compare test for FG/BG mode."""
import subprocess, os, sys, time
from PIL import Image

PROJECT_DIR = "C:/Users/vrock/Documents/Swords and Serpents"
os.chdir(PROJECT_DIR)

sys.path.insert(0, '.')
from render_all_rooms import (
    extract_backtab_from_output, parse_backtab, decode_backtab_word,
    extract_gram_from_output, parse_memory_dump,
    extract_memory_section, parse_mobs,
    render_room_image, load_grom,
    PALETTE, PASTEL_PALETTE, DEFAULT_BG,
    SDL_ENV, JZINTV, ROM_PATH, GROM_PATH, EXEC_PATH,
    IDLE_PATCHES, X_FILL_MEM_NOP
)

# Remove old screenshots
for f in ['shot0001.gif', 'shot0002.gif']:
    if os.path.exists(f):
        os.remove(f)

# Generate debugger script that captures BACKTAB AND takes screenshot
script = """\
; Speed patches
p 506A 0034
p 506B 0034
p 506C 0034
p 506D 0034
p 506E 0034
p 5318 0034
p 5319 0034
p 531A 0034
p 531B 02B8
p 531C 0001
p 56CC 0034
p 56CD 0034
; NOP X_FILL_MEM
p 5638 0034
p 5639 0034
; Force past title screen
w 018C 0001
; Run to gameplay
r 8000000
; Take screenshot FIRST (before dumps might affect state)
vs
; Dump BACKTAB
m 0200 240
; Dump GRAM
m 3800 512
; Dump STIC color stack
m 0028 4
; Dump MOB registers
m 0000 32
; Dump SYSRAM MOB shadow
m 0300 96
; Dump 8-bit RAM
m 0100 256
q
"""

with open('_fresh_test.txt', 'w') as f:
    f.write(script)

print("Running jzIntv with fresh capture...")
cmd = [
    JZINTV, "-d",
    "--script=_fresh_test.txt",
    "-e", EXEC_PATH,
    "-g", GROM_PATH,
    ROM_PATH,
]

with open('_fresh_out.txt', 'w', encoding='utf-8', errors='replace') as out_f:
    proc = subprocess.Popen(
        cmd, stdout=out_f, stderr=subprocess.STDOUT,
        env=SDL_ENV, cwd=PROJECT_DIR,
    )
    try:
        proc.wait(timeout=300)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()

with open('_fresh_out.txt', 'r', encoding='utf-8', errors='replace') as f:
    output = f.read()

print(f"Output size: {len(output)} bytes")

# Parse
backtab_text = extract_backtab_from_output(output)
backtab_grid = parse_backtab(backtab_text)
gram_text = extract_gram_from_output(output)
gram_mem = parse_memory_dump(gram_text, 0x3800, 512) if gram_text else {}
sysram_text = extract_memory_section(output, 0x0300, 0x0360)
mobs = parse_mobs(sysram_text) if sysram_text else []
grom = load_grom()

print(f"\nBACKTAB: {len(backtab_grid)}x{len(backtab_grid[0]) if backtab_grid else 0}")
print(f"GRAM: {len(gram_mem)} words")
print(f"MOBs: {len(mobs)}")

# Analyze bg_adv distribution
print(f"\n=== BACKTAB bg_adv analysis ===")
bg_counts = {}
for row in range(12):
    for col in range(20):
        word = backtab_grid[row][col]
        card, fg, bg_adv, is_gram, _ = decode_backtab_word(word)
        bg_counts[bg_adv] = bg_counts.get(bg_adv, 0) + 1

print("bg_adv distribution:")
for ba in sorted(bg_counts.keys()):
    pct = 100*bg_counts[ba]/240
    color_idx = ba & 0x3
    is_pastel = (ba & 0x4) != 0
    mode = "PASTEL" if is_pastel else "primary"
    pal = PASTEL_PALETTE if is_pastel else PALETTE
    color_name = {0:"black",1:"blue",2:"red",3:"tan"}.get(color_idx, "??")
    rgb = pal.get(color_idx, (0,0,0))
    print(f"  bg_adv={ba} ({ba:03b}): {bg_counts[ba]:3d} tiles ({pct:.1f}%) -> {mode} {color_name} {rgb}")

# Render
print(f"\n=== Rendering with FG/BG mode ===")
room_img = render_room_image(backtab_grid, gram_mem, grom, color_stack=None, zoom=4, mobs=mobs)
room_img.save('sprites/dungeon_room_0.png')

our_px = room_img.load()
our_colors = {}
for y in range(room_img.height):
    for x in range(room_img.width):
        c = our_px[x,y]
        our_colors[c] = our_colors.get(c, 0) + 1

print("Our render color distribution:")
for c, n in sorted(our_colors.items(), key=lambda x: -x[1]):
    pct = 100*n/(room_img.width*room_img.height)
    print(f"  {c}: {n:5d} px ({pct:.1f}%)")

# Check screenshot
scr_path = None
for f in ['shot0001.gif', 'shot0002.gif']:
    if os.path.exists(f):
        scr_path = f
        break

if scr_path:
    scr = Image.open(scr_path)
    scr_pal = scr.getpalette()
    scr_px = scr.load()
    
    print(f"\nScreenshot: {scr.size[0]}x{scr.size[1]}")
    
    # Full screenshot palette
    print("jzIntv GIF palette:")
    for i in range(16):
        if scr_pal and i*3+2 < len(scr_pal):
            r, g, b = scr_pal[i*3], scr_pal[i*3+1], scr_pal[i*3+2]
            mode = "PASTEL" if i >= 8 else "primary"
            print(f"  idx {i:2d}: RGB({r:3d},{g:3d},{b:3d}) => INTY {i&7} {mode}")
    
    scr_colors = {}
    for y in range(scr.height):
        for x in range(scr.width):
            idx = scr_px[x,y]
            if scr_pal and idx*3+2 < len(scr_pal):
                c = (scr_pal[idx*3], scr_pal[idx*3+1], scr_pal[idx*3+2])
                scr_colors[c] = scr_colors.get(c, 0) + 1
    
    print("\njzIntv screenshot color distribution:")
    for c, n in sorted(scr_colors.items(), key=lambda x: -x[1]):
        pct = 100*n/(scr.width*scr.height)
        print(f"  {c}: {n:5d} px ({pct:.1f}%)")
    
    # Find dungeon bounds in screenshot
    # Look for the rectangle of non-black pixels
    # Scan from edges inward
    def find_left_edge():
        for x in range(scr.width):
            colored = sum(1 for y in range(scr.height) if scr_px[x,y] != 0)
            if colored > 20:  # need significant non-black pixels
                return x
        return 0
    def find_right_edge():
        for x in range(scr.width-1, -1, -1):
            colored = sum(1 for y in range(scr.height) if scr_px[x,y] != 0)
            if colored > 20:
                return x
        return scr.width-1
    def find_top_edge():
        for y in range(scr.height):
            colored = sum(1 for x in range(scr.width) if scr_px[x,y] != 0)
            if colored > 20:
                return y
        return 0
    def find_bottom_edge():
        for y in range(scr.height-1, -1, -1):
            colored = sum(1 for x in range(scr.width) if scr_px[x,y] != 0)
            if colored > 20:
                return y
        return scr.height-1
    
    l, r, t, b = find_left_edge(), find_right_edge(), find_top_edge(), find_bottom_edge()
    print(f"\nDungeon bounds: x=[{l},{r}] y=[{t},{b}]")
    
    # The dungeon should be exactly 160x96 pixels (20x12 tiles at 8px)
    # jzIntv might render at 1x, 2x, or other zoom
    dungeon_w = r - l + 1
    dungeon_h = b - t + 1
    # Sometimes right edge has 1px black border, so allow some tolerance
    print(f"Dungeon size in screenshot: {dungeon_w}x{dungeon_h}")
    
    if dungeon_w >= 300:
        zoom_factor = 2  # 320x192 (2x zoom)
    else:
        zoom_factor = 1  # 160x96 (1x zoom)
    
    # Now compare pixel by pixel at 1x resolution
    # Our render is always 4x zoom (640x384)
    # Screenshot may be 1x or 2x zoom
    # Map screenshot coordinates to our render coordinates
    
    # First, figure out exact mapping
    # Our tile grid: 20 cols × 12 rows, each tile is 8px at 1x, 32px at 4x
    # Screenshot: 160x96 (1x) or 320x192 (2x) dungeon area
    
    # For comparison, downsample our render to match screenshot zoom
    our_zoom = 4
    scr_zoom = zoom_factor
    
    matches = 0
    total = 0
    
    for tile_row in range(12):
        for tile_col in range(20):
            for y in range(8):  # 8px per tile at 1x
                for x in range(8):
                    # Our render coords at 4x
                    our_x = tile_col * 8 * our_zoom + x * our_zoom
                    our_y = tile_row * 8 * our_zoom + y * our_zoom
                    our_rgb = our_px[our_x, our_y]
                    
                    # Screenshot coords
                    scr_x = l + tile_col * 8 * scr_zoom + x * scr_zoom
                    scr_y = t + tile_row * 8 * scr_zoom + y * scr_zoom
                    
                    if 0 <= scr_x < scr.width and 0 <= scr_y < scr.height:
                        scr_idx = scr_px[scr_x, scr_y]
                        if scr_pal and scr_idx*3+2 < len(scr_pal):
                            scr_rgb = (scr_pal[scr_idx*3], scr_pal[scr_idx*3+1], scr_pal[scr_idx*3+2])
                        else:
                            continue
                        
                        total += 1
                        if our_rgb == scr_rgb:
                            matches += 1
    
    print(f"\n=== PIXEL COMPARISON ===")
    print(f"Total pixels: {total}")
    print(f"Exact matches: {matches} ({100*matches/total:.1f}%)" if total else "N/A")
    
    # Also compare color distribution percentages to see if they match
    print(f"\n=== COLOR PERCENTAGE COMPARISON ===")
    # Expected from bg_adv distribution
    our_total = room_img.width * room_img.height
    scr_total = scr.width * scr.height
    
    for c in set(list(our_colors.keys()) + list(scr_colors.keys())):
        our_pct = 100 * our_colors.get(c, 0) / our_total
        scr_pct = 100 * scr_colors.get(c, 0) / scr_total
        if our_pct > 0.1 or scr_pct > 0.1:
            match_symbol = "✓" if abs(our_pct - scr_pct) < 2 else "✗"
            print(f"  {c}: our={our_pct:.1f}%  jzIntv={scr_pct:.1f}%  {match_symbol}")

print("\nDone!")
