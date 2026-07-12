"""
Quick test: render room 0 with all color stack entries = green (5).
EXEC.730 at $1730 likely fills all 4 CS entries with the same color.
"""
import os, sys
sys.path.insert(0, '.')
from PIL import Image
from render_all_rooms import (
    extract_backtab_from_output, parse_backtab, extract_gram_from_output,
    parse_memory_dump, extract_memory_section, parse_mobs, load_grom,
    render_room_image, PALETTE
)

# Load room 0 capture
with open('traces/render_room_0_out.txt', 'r', errors='replace') as f:
    output = f.read()

backtab_text = extract_backtab_from_output(output)
backtab_grid = parse_backtab(backtab_text)
gram_text = extract_gram_from_output(output)
gram_mem = parse_memory_dump(gram_text, 0x3800, 512) if gram_text else {}
sysram_text = extract_memory_section(output, 0x0300, 0x0360)
mobs = parse_mobs(sysram_text) if sysram_text else []
grom = load_grom()

# Test 1: ALL CS = green
cs_all_green = [PALETTE[5]] * 4
room1 = render_room_image(backtab_grid, gram_mem, grom, color_stack=cs_all_green, zoom=2, mobs=mobs)

# Test 2: ALL CS = pastel tan (58,138,0) - what jzIntv actually shows
cs_all_pastel_tan = [(58, 138, 0)] * 4
room2 = render_room_image(backtab_grid, gram_mem, grom, color_stack=cs_all_pastel_tan, zoom=2, mobs=mobs)

# Test 3: CS0=pastel tan, rest=green
cs_mixed = [(58, 138, 0), PALETTE[5], PALETTE[5], PALETTE[5]]
room3 = render_room_image(backtab_grid, gram_mem, grom, color_stack=cs_mixed, zoom=2, mobs=mobs)

# Compare with screenshot
shot = Image.open('shot0001.gif').convert('RGB')

for label, room in [("all_green", room1), ("all_pastel_tan", room2), ("mixed", room3)]:
    room_160 = room.resize((160, 96), Image.NEAREST)
    shot_160 = shot.resize((160, 96), Image.NEAREST)
    rp = room_160.load()
    sp = shot_160.load()
    
    match = 0
    mismatch = 0
    for y in range(96):
        for x in range(160):
            if rp[x,y] == sp[x,y]:
                match += 1
            else:
                mismatch += 1
    
    total = match + mismatch
    print(f"Test '{label}': {match} matches ({100.0*match/total:.1f}%), {mismatch} mismatches")
    
    # Color distribution
    colors = {}
    for y in range(room.height):
        for x in range(room.width):
            c = room.getpixel((x,y))
            colors[c] = colors.get(c, 0) + 1
    print(f"  Dominant colors:")
    for c, n in sorted(colors.items(), key=lambda x: -x[1])[:5]:
        pct = 100.0*n/(room.width*room.height)
        print(f"    {c}: {pct:.1f}%")
    print()
