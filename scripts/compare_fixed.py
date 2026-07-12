"""
Re-render room 0 with fixed palette + color stack, compare with jzIntv screenshot.
"""
import os, sys
sys.path.insert(0, '.')
from PIL import Image

from render_all_rooms import (
    extract_backtab_from_output, parse_backtab, extract_gram_from_output,
    parse_memory_dump, extract_color_stack_from_output, parse_color_stack,
    extract_memory_section, parse_mobs, load_grom, render_room_image,
    PALETTE, PASTEL_PALETTE, MOB_FG_COLOR
)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Load existing room 0 capture
with open('traces/render_room_0_out.txt', 'r', errors='replace') as f:
    output = f.read()

backtab_text = extract_backtab_from_output(output)
backtab_grid = parse_backtab(backtab_text)
gram_text = extract_gram_from_output(output)
gram_mem = parse_memory_dump(gram_text, 0x3800, 512) if gram_text else {}
cs_text = extract_color_stack_from_output(output)
color_stack = parse_color_stack(cs_text) if cs_text else None
sysram_text = extract_memory_section(output, 0x0300, 0x0360)
mobs = parse_mobs(sysram_text) if sysram_text else []
grom = load_grom()

print("=== Rendering room 0 with FIXED palette + color stack ===")
print(f"  CS0: {color_stack[0] if color_stack else 'N/A'}")
print(f"  CS1: {color_stack[1] if color_stack and len(color_stack) > 1 else 'N/A'}")
print(f"  MOB_FG_COLOR: {MOB_FG_COLOR}")
print(f"  MOBs: {len(mobs)}")
for m in mobs:
    print(f"    MOB{m['mob_idx']}: x={m['x']} y={m['y']} card={m['card']} {'GRAM' if m['is_gram'] else 'GROM'} {'BEHIND' if m['behind'] else 'FRONT'} {16 if m['xsize'] else 8}x{16 if m['ysize'] else 8}")

# Render
room_img = render_room_image(backtab_grid, gram_mem, grom, color_stack=color_stack, zoom=2, mobs=mobs)
room_img.save('sprites/dungeon_room_0_fixed.png')
print(f"\n  Saved: sprites/dungeon_room_0_fixed.png ({room_img.size[0]}x{room_img.size[1]})")

# Load jzIntv screenshot
shot = Image.open('shot0001.gif')
shot_rgb = shot.convert('RGB')

# Downscale both to 160x96 for comparison
our_160 = room_img.resize((160, 96), Image.NEAREST)
shot_160 = shot_rgb.resize((160, 96), Image.NEAREST)

our_px = our_160.load()
shot_px = shot_160.load()

print(f"\n=== Pixel-by-pixel comparison at 160x96 ===")
match_count = 0
mismatch_count = 0
mismatch_details = {}

for y in range(96):
    for x in range(160):
        o_rgb = our_px[x,y]
        s_rgb = shot_px[x,y]
        if o_rgb == s_rgb:
            match_count += 1
        else:
            mismatch_count += 1
            key = (s_rgb, o_rgb)
            mismatch_details[key] = mismatch_details.get(key, 0) + 1

total = match_count + mismatch_count
print(f"  Exact RGB matches: {match_count} ({100.0*match_count/total:.1f}%)")
print(f"  Mismatches: {mismatch_count} ({100.0*mismatch_count/total:.1f}%)")

# Also try neighborhood matching (allow 1-off per channel)
near_match = 0
far_mismatch = 0
for y in range(96):
    for x in range(160):
        o_rgb = our_px[x,y]
        s_rgb = shot_px[x,y]
        if all(abs(o_rgb[i] - s_rgb[i]) <= 1 for i in range(3)):
            near_match += 1
        else:
            far_mismatch += 1

print(f"  Near matches (within 1 per channel): {near_match} ({100.0*near_match/total:.1f}%)")
print(f"  Far mismatches: {far_mismatch} ({100.0*far_mismatch/total:.1f}%)")

# Top mismatch breakdown
if mismatch_details:
    print(f"\n  Top mismatches (screenshot->ours):")
    for (s, o), n in sorted(mismatch_details.items(), key=lambda x: -x[1])[:12]:
        print(f"    {s} -> {o}: {n} px")

# Color distribution comparison
print(f"\n=== Our render color distribution ===")
our_colors = {}
for y in range(room_img.height):
    for x in range(room_img.width):
        c = room_img.getpixel((x,y))
        our_colors[c] = our_colors.get(c, 0) + 1
for c, n in sorted(our_colors.items(), key=lambda x: -x[1]):
    pct = 100.0 * n / (room_img.width * room_img.height)
    print(f"  {c}: {n:6d} px ({pct:5.1f}%)")

print(f"\n=== Screenshot color distribution ===")
shot_colors = {}
for y in range(shot_rgb.height):
    for x in range(shot_rgb.width):
        c = shot_rgb.getpixel((x,y))
        shot_colors[c] = shot_colors.get(c, 0) + 1
for c, n in sorted(shot_colors.items(), key=lambda x: -x[1]):
    pct = 100.0 * n / (shot_rgb.width * shot_rgb.height)
    print(f"  {c}: {n:6d} px ({pct:5.1f}%)")
