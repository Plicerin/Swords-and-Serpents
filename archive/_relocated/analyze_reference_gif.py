"""
Extract the playfield from the jzIntv reference GIF and analyze each tile.
Maps BACKTAB words to tiles and identifies where blue overlay pixels appear.
"""
from PIL import Image
import os, sys

sys.path.insert(0, '.')
from render_all_rooms import (
    decode_backtab_word, PALETTE, PASTEL_PALETTE,
    EMPIRICAL_TRANSPARENT, EMPIRICAL_FG, EMPIRICAL_BG_COLOR, EMPIRICAL_PER_PIXEL,
    load_grom, get_grom_card_bytes, parse_backtab, extract_backtab_from_output,
    parse_memory_dump, extract_gram_from_output,
)

# Load reference GIF
ref = Image.open('sprites/comparisons/room_0_jzintv.gif')
print(f"Reference GIF: {ref.width}x{ref.height}, mode={ref.mode}")

# Crop to playfield (verified: 80,52 to 240,148 = 160x96 = 20x12 tiles at 8x8)
# MUST convert to RGB — GIF is palette-mode, px[] returns indices not RGB tuples
pf = ref.crop((80, 52, 240, 148)).convert('RGB')  # 160x96 native playfield
print(f"Playfield crop: {pf.width}x{pf.height}")
pf_px = pf.load()

# Load BACKTAB data
with open('traces/rooms/render_room_0_out.txt', 'r') as f:
    output = f.read()

backtab_text = extract_backtab_from_output(output)
backtab_grid = parse_backtab(backtab_text)

# Load GROM for card analysis
grom = load_grom()

# Map palette index to RGB
# jzIntv GIF uses palette indices 0-15 mapping to INTY colors
GIF_PALETTE = {
    0:  (0, 0, 0),           # black
    1:  (20, 56, 247),       # blue
    2:  (227, 91, 14),       # red
    3:  (203, 241, 104),     # tan
    4:  (0, 148, 40),        # dark green
    5:  (7, 194, 0),         # green
    6:  (255, 255, 1),       # yellow
    7:  (255, 255, 255),     # white
    8:  (200, 200, 200),     # pastel black
    9:  (35, 206, 195),      # pastel blue
    10: (253, 153, 24),      # pastel red
    11: (58, 138, 0),        # pastel tan
    12: (240, 70, 60),       # pastel dark green
    13: (211, 131, 255),     # pastel green
    14: (72, 246, 1),        # pastel yellow
    15: (184, 17, 120),      # pastel white
}

# Reverse map: RGB -> palette index
RGB_TO_IDX = {v: k for k, v in GIF_PALETTE.items()}

BLUE_RGB = GIF_PALETTE[1]
PASTEL_TAN = GIF_PALETTE[11]  # (58,138,0)

print(f"\n=== Per-Tile Analysis ===")
print(f"Legend: word=hex, card=GROM/GRAM#, fg=color#, bg_adv=CSadv, is_gram, fg_transp")
print(f"Colors: B=blue pix, P=pastel tan, T=primary tan, K=black, W=white, D=dark green, G=green")
print()

# Analyze each 8x8 tile
total_blue_px = 0
blue_tiles = set()
tile_data = {}  # (row,col) -> color distribution

for ty in range(12):
    for tx in range(20):
        word = backtab_grid[ty][tx]
        card, fg, bg_bits, is_gram, fg_transp = decode_backtab_word(word)
        
        # Count colors in this tile
        color_counts = {}
        blue_count = 0
        for y in range(8):
            for x in range(8):
                px_x = tx * 8 + x
                px_y = ty * 8 + y
                c = pf_px[px_x, px_y]
                color_counts[c] = color_counts.get(c, 0) + 1
                if c == BLUE_RGB:
                    blue_count += 1
        
        if blue_count > 0:
            total_blue_px += blue_count
            blue_tiles.add((ty, tx))
        
        # Build color summary string
        summary = ""
        for rgb, cnt in sorted(color_counts.items(), key=lambda x: -x[1]):
            if cnt < 2:
                break
            idx = RGB_TO_IDX.get(rgb, '?')
            if rgb == BLUE_RGB:
                summary += f"B{cnt} "
            elif rgb == PASTEL_TAN:
                summary += f"P{cnt} "
            elif rgb == GIF_PALETTE[3]:
                summary += f"T{cnt} "
            elif rgb == GIF_PALETTE[0]:
                summary += f"K{cnt} "
            elif rgb == GIF_PALETTE[7]:
                summary += f"W{cnt} "
            elif rgb == GIF_PALETTE[4]:
                summary += f"D{cnt} "
            elif rgb == GIF_PALETTE[5]:
                summary += f"G{cnt} "
            else:
                summary += f"#{idx}:{cnt} "
        
        # Decode info
        src = "G" if is_gram else "g"
        transp = "T" if fg_transp else " "
        card_str = f"{card:3d}{src}"
        adv = bg_bits & 1
        
        # Only print non-$1603 tiles (interesting ones)
        if word != 0x1603 or blue_count > 0:
            print(f"  [{ty:2d},{tx:2d}] ${word:04X} card={card_str} fg={fg} adv={adv} {transp} | {summary.strip()}")

print(f"\n=== Summary ===")
print(f"Total blue pixels in playfield: {total_blue_px}")
print(f"Tiles with blue: {len(blue_tiles)}")
print(f"Unique BACKTAB words in playfield: {len(set(backtab_grid[ty][tx] for ty in range(12) for tx in range(20)))}")

# Analyze the dominant tile $1603
print(f"\n=== $1603 (dominant wall tile) Analysis ===")
t1603_colors = {}
t1603_count = 0
for ty in range(12):
    for tx in range(20):
        if backtab_grid[ty][tx] == 0x1603:
            t1603_count += 1
            for y in range(8):
                for x in range(8):
                    c = pf_px[tx*8+x, ty*8+y]
                    t1603_colors[c] = t1603_colors.get(c, 0) + 1
print(f"  Tiles: {t1603_count}/{240}")
for rgb, cnt in sorted(t1603_colors.items(), key=lambda x: -x[1]):
    idx = RGB_TO_IDX.get(rgb, '?')
    pct = 100*cnt/(t1603_count*64)
    print(f"    GIF[{idx}] RGB{rgb} = {cnt} px ({pct:.1f}%)")

# For each tile with blue, figure out what card content should replace it
print(f"\n=== Blue Tile Analysis (what should replace blue?) ===")
for ty in range(12):
    for tx in range(20):
        word = backtab_grid[ty][tx]
        card, fg, bg_bits, is_gram, fg_transp = decode_backtab_word(word)
        
        # Count colors in this tile
        color_counts = {}
        for y in range(8):
            for x in range(8):
                c = pf_px[tx*8+x, ty*8+y]
                color_counts[c] = color_counts.get(c, 0) + 1
        
        blue_count = color_counts.get(BLUE_RGB, 0)
        if blue_count == 0:
            continue
        
        # What non-blue colors exist in this tile?
        non_blue = {c: n for c, n in color_counts.items() if c != BLUE_RGB}
        
        # What's the dominant non-blue color?
        dominant = max(non_blue.items(), key=lambda x: x[1]) if non_blue else (BLUE_RGB, 0)
        
        # Get the card bytes
        if is_gram:
            src = "GRAM"
        else:
            src = "GROM"
            card_bytes = get_grom_card_bytes(grom, card)
        
        # Show the card bitmap (which pixels are 1 = foreground)
        if not is_gram:
            bitmap = ""
            for row in range(8):
                byte_val = card_bytes[row] if row < len(card_bytes) else 0
                line = ""
                for col in range(8):
                    bit = (byte_val >> (7 - col)) & 1
                    line += "#" if bit else "."
                bitmap += f"    {line}\n"
        else:
            bitmap = "    (GRAM card - not analyzed)\n"
        
        print(f"  [{ty:2d},{tx:2d}] ${word:04X} blue={blue_count}/64")
        print(f"    Non-blue colors: {non_blue}")
        print(f"    Dominant non-blue: {dominant}")
        print(f"    Card bitmap (1=fg, 0=bg):")
        if not is_gram:
            print(bitmap.rstrip())
        else:
            print(bitmap)
        print()
