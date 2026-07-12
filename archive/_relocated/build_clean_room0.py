"""
Swords & Serpents — Clean Room 0 Builder

Builds a clean room 0 render from the jzIntv reference GIF.
Replaces blue, white, and black emulator overlay artifacts with
colors computed from the BACKTAB card bitmap.
"""
from PIL import Image
import sys
from pathlib import Path

sys.path.insert(0, '.')
from versioning import next_versioned_path
from render_all_rooms import (
    decode_backtab_word, PALETTE,
    EMPIRICAL_FG, EMPIRICAL_BG_COLOR,
    load_grom, get_grom_card_bytes, parse_backtab, extract_backtab_from_output,
    parse_memory_dump, extract_gram_from_output,
)
from room_renderer import (
    BLUE, BLACK, resolve_artifact_pixel, is_whiteish, PASTEL_TAN, ARTIFACT_ROW_LIMIT,
)

# Load reference GIF → crop to playfield → convert to RGB
ref = Image.open('sprites/comparisons/room_0_jzintv.gif')
pf = ref.crop((80, 52, 240, 148)).convert('RGB')
pf_px = pf.load()
print(f"Playfield: {pf.width}x{pf.height}")

# Load BACKTAB
with open('traces/rooms/render_room_0_out.txt', 'r') as f:
    output = f.read()
backtab_text = extract_backtab_from_output(output)
backtab_grid = parse_backtab(backtab_text)

# Load GRAM
gram_text = extract_gram_from_output(output)
gram_mem = parse_memory_dump(gram_text, 0x3800, 512)

# Load GROM
grom = load_grom()

def get_card_row(card_idx, row, is_gram):
    """Get byte row from GROM or GRAM card."""
    if is_gram:
        base = 0x3800 + (card_idx & 0x3F) * 8
        return gram_mem.get(base + row, 0) & 0xFF
    else:
        card_bytes = get_grom_card_bytes(grom, card_idx)
        return card_bytes[row] if row < len(card_bytes) else 0

def resolve_fg_color(word, fg_color_idx):
    """Get the actual FG color for a BACKTAB word."""
    if word in EMPIRICAL_FG:
        fg_idx = EMPIRICAL_FG[word]
        return PALETTE.get(fg_idx, BLACK)
    if fg_color_idx == 0:
        return BLACK  # FG=0 is black in Color Stack mode
    return PALETTE.get(fg_color_idx, BLACK)

def resolve_bg_color(word):
    """Get the actual background (Color Stack) color for a BACKTAB word."""
    if word in EMPIRICAL_BG_COLOR:
        return EMPIRICAL_BG_COLOR[word]
    return PASTEL_TAN  # default CS entry

# Build clean output
clean = Image.new('RGB', (160, 96))
clean_px = clean.load()

artifact_counts = {"blue": 0, "white": 0, "black": 0}

for ty in range(12):
    for tx in range(20):
        word = backtab_grid[ty][tx]
        card_idx, fg_color_idx, bg_bits, is_gram, fg_transp = decode_backtab_word(word)

        fg_color = resolve_fg_color(word, fg_color_idx)
        bg_color = resolve_bg_color(word)

        for y in range(8):
            byte_val = get_card_row(card_idx, y, is_gram)
            for x in range(8):
                px_x = tx * 8 + x
                px_y = ty * 8 + y
                src_color = pf_px[px_x, px_y]

                # Compute expected card color for this pixel
                card_bit = (byte_val >> (7 - x)) & 1
                if card_bit == 0 or fg_transp:
                    expected = bg_color
                else:
                    expected = fg_color

                resolved, art_type = resolve_artifact_pixel(src_color, expected, ty)
                if art_type:
                    artifact_counts[art_type] += 1
                clean_px[px_x, px_y] = resolved

print(f"Replaced {artifact_counts['blue']} blue pixels")
print(f"Removed {artifact_counts['white']} white text pixels")
print(f"Removed {artifact_counts['black']} black outline pixels")

# Scale up 4x
zoom = 4
scaled = clean.resize((160 * zoom, 96 * zoom), Image.NEAREST)

# Save (versioned)
out_path = next_versioned_path('sprites/rooms', 'dungeon_room_0', '.png')
scaled.save(out_path)
print(f"Saved: {out_path} ({scaled.width}x{scaled.height})")

# Verify: count blue, white-ish, and black pixels
blue_check = sum(1 for y in range(scaled.height) for x in range(scaled.width)
                 if scaled.getpixel((x, y)) == BLUE)
white_check = sum(1 for y in range(scaled.height) for x in range(scaled.width)
                   if is_whiteish(scaled.getpixel((x, y))))
black_check = sum(1 for y in range(scaled.height) for x in range(scaled.width)
                   if scaled.getpixel((x, y)) == BLACK)
print(f"Blue pixels in output: {blue_check}")
print(f"White-ish pixels in output: {white_check}")
print(f"Black pixels in output: {black_check}")

# Top-row verification: ensure zero artifacts in rows below ARTIFACT_ROW_LIMIT
top_rows_h = ARTIFACT_ROW_LIMIT * 8 * zoom
top_blue = sum(1 for y in range(top_rows_h) for x in range(scaled.width)
               if scaled.getpixel((x, y)) == BLUE)
top_white = sum(1 for y in range(top_rows_h) for x in range(scaled.width)
                if is_whiteish(scaled.getpixel((x, y))))
top_black = sum(1 for y in range(top_rows_h) for x in range(scaled.width)
                if scaled.getpixel((x, y)) == BLACK)
print(f"Top-row blue artifacts: {top_blue}")
print(f"Top-row white artifacts: {top_white}")
print(f"Top-row black artifacts: {top_black}")

# Color stats
color_counts = {}
px = scaled.load()
for y in range(0, scaled.height, 2):
    for x in range(0, scaled.width, 2):
        c = px[x, y]
        color_counts[c] = color_counts.get(c, 0) + 1
print(f"\nColor distribution ({len(color_counts)} unique):")
for rgb, cnt in sorted(color_counts.items(), key=lambda x: -x[1]):
    pct = 100 * cnt / (scaled.width * scaled.height / 4)
    label = ""
    if rgb == PASTEL_TAN: label = " (pastel tan - CS bg)"
    if rgb == BLACK: label = " (black)"
    if rgb == (203,241,104): label = " (primary tan)"
    if rgb == (255,255,255): label = " (white)"
    if rgb == (0,148,40): label = " (dark green)"
    print(f"  RGB({rgb[0]:3d},{rgb[1]:3d},{rgb[2]:3d}) {cnt:>7d} ({pct:5.1f}%){label}")
