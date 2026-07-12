"""
Compare jzIntv screenshot (shot0001.gif) with our rendered room 0 (sprites/dungeon_room_0.png).
Maps jzIntv's palette to our palette for fair comparison.
"""
from PIL import Image
import os

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Our PALETTE
OUR_PALETTE = {
    0:  (0, 0, 0),
    1:  (0, 45, 200),
    2:  (200, 0, 20),
    3:  (200, 170, 100),
    4:  (0, 80, 20),
    5:  (0, 140, 40),
    6:  (230, 215, 70),
    7:  (255, 255, 255),
}

# Load jzIntv screenshot
shot = Image.open(os.path.join(PROJECT_DIR, 'shot0001.gif'))
shot_pal = shot.getpalette()

print("=== jzIntv GIF Palette ===")
for i in range(16):
    r = shot_pal[i*3]
    g = shot_pal[i*3+1]
    b = shot_pal[i*3+2]
    print(f"  idx {i:2d}: RGB({r:3d},{g:3d},{b:3d})")

# Convert GIF to RGB for analysis
shot_rgb = shot.convert('RGB')
shot_px = shot_rgb.load()

# Count actual pixel colors in screenshot
shot_colors = {}
for y in range(shot_rgb.height):
    for x in range(shot_rgb.width):
        c = shot_px[x,y]
        shot_colors[c] = shot_colors.get(c, 0) + 1

print(f"\n=== Screenshot color distribution (320x200 = {320*200} px) ===")
for c, n in sorted(shot_colors.items(), key=lambda x: -x[1]):
    pct = 100.0 * n / (320*200)
    print(f"  {c}: {n:6d} px ({pct:5.1f}%)")

# Match each screenshot RGB to nearest our palette entry
def nearest_our_color(rgb):
    best_dist = 999999
    best_idx = 0
    for idx, (pr, pg, pb) in OUR_PALETTE.items():
        dist = (rgb[0]-pr)**2 + (rgb[1]-pg)**2 + (rgb[2]-pb)**2
        if dist < best_dist:
            best_dist = dist
            best_idx = idx
    return best_idx

# Count which of our palette indices each screenshot pixel maps to
our_color_counts = {}
for c, n in shot_colors.items():
    our_idx = nearest_our_color(c)
    our_color_counts[our_idx] = our_color_counts.get(our_idx, 0) + n

print(f"\n=== Screenshot mapped to OUR palette ===")
for idx in sorted(our_color_counts.keys()):
    n = our_color_counts[idx]
    pct = 100.0 * n / (320*200)
    print(f"  Our idx {idx} {OUR_PALETTE[idx]}: {n:6d} px ({pct:5.1f}%)")

# Now load our rendered room 0
our_room = Image.open(os.path.join(PROJECT_DIR, 'sprites', 'dungeon_room_0.png'))
our_px = our_room.load()

# Our render is 640x384 (4x zoom of 160x96)
# Downscale to 160x96 by taking most common color in each 4x4 block
# For comparison we'll look at 2x2 blocks (since screenshot is 2x zoom)
# Actually, our render is 4x, screenshot is 2x. Let's compare at native 1x.

print(f"\n=== Our rendered room 0 colors (640x384) ===")
our_colors = {}
for y in range(our_room.height):
    for x in range(our_room.width):
        c = our_px[x,y]
        our_colors[c] = our_colors.get(c, 0) + 1
for c, n in sorted(our_colors.items(), key=lambda x: -x[1]):
    idx = nearest_our_color(c)
    pct = 100.0 * n / (640*384)
    print(f"  {c} (our idx {idx}): {n:6d} px ({pct:5.1f}%)")

# Compare: downscale our render to 160x96 and compare with screenshot (downscaled to 160x96)
shot_160 = shot_rgb.resize((160, 96), Image.NEAREST)
shot_160_px = shot_160.load()

our_160 = our_room.resize((160, 96), Image.NEAREST)
our_160_px = our_160.load()

print(f"\n=== Pixel-by-pixel comparison at 160x96 ===")
match_count = 0
mismatch_count = 0
mismatch_details = {}

for y in range(96):
    for x in range(160):
        s_rgb = shot_160_px[x,y]
        o_rgb = our_160_px[x,y]
        s_idx = nearest_our_color(s_rgb)
        o_idx = nearest_our_color(o_rgb)
        if s_idx == o_idx:
            match_count += 1
        else:
            mismatch_count += 1
            key = (s_idx, o_idx)
            mismatch_details[key] = mismatch_details.get(key, 0) + 1

total = match_count + mismatch_count
print(f"  Matches: {match_count} ({100.0*match_count/total:.1f}%)")
print(f"  Mismatches: {mismatch_count} ({100.0*mismatch_count/total:.1f}%)")
print(f"  Mismatch breakdown (screenshot->ours):")
for (s, o), n in sorted(mismatch_details.items(), key=lambda x: -x[1]):
    print(f"    idx {s}->{o}: {n} px")
