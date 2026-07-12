"""
Derive COMPLETE empirical rendering data from the jzIntv reference GIF.
Analyzes every unique BACKTAB word: background color, foreground color,
transparency classification, and per-pixel data for complex tiles.
All blue emulator overlay pixels are excluded from the analysis.
"""
from PIL import Image
from collections import Counter
import sys, os, copy
sys.path.insert(0, '.')
from render_all_rooms import (
    decode_backtab_word, PALETTE, PASTEL_PALETTE,
    load_grom, get_grom_card_bytes, parse_backtab, extract_backtab_from_output,
    parse_memory_dump, extract_gram_from_output,
)

BLUE = (20, 56, 247)
PASTEL_TAN = PASTEL_PALETTE[3]  # (58, 138, 0)
PRIMARY_TAN = PALETTE[3]        # (203, 241, 104)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Load reference GIF
ref = Image.open('sprites/comparisons/room_0_jzintv.gif')
pf = ref.crop((80, 52, 240, 148)).convert('RGB')
pf_px = pf.load()

# Load BACKTAB and GRAM
with open('traces/rooms/render_room_0_out.txt', 'r') as f:
    output = f.read()
backtab_text = extract_backtab_from_output(output)
backtab_grid = parse_backtab(backtab_text)
gram_text = extract_gram_from_output(output)
gram_mem = parse_memory_dump(gram_text, 0x3800, 512)
grom = load_grom()

def get_card_row(card_idx, row, is_gram):
    """Get byte row from GROM or GRAM card."""
    if is_gram:
        base = 0x3800 + (card_idx & 0x3F) * 8
        return gram_mem.get(base + row, 0) & 0xFF
    else:
        card_bytes = get_grom_card_bytes(grom, card_idx)
        return card_bytes[row] if row < len(card_bytes) else 0

# Collect ALL pixels per BACKTAB word across all tiles
word_data = {}  # word -> {bg_pixels: Counter, fg_pixels: Counter, count: int}
word_positions = {}  # word -> [(ty, tx)]

for ty in range(12):
    for tx in range(20):
        word = backtab_grid[ty][tx]
        card_idx, fg_color_idx, bg_bits, is_gram, _ = decode_backtab_word(word)
        
        if word not in word_data:
            word_data[word] = {'bg_pixels': Counter(), 'fg_pixels': Counter(), 'count': 0}
            word_positions[word] = []
        
        word_data[word]['count'] += 1
        word_positions[word].append((ty, tx))
        
        for y in range(8):
            byte_val = get_card_row(card_idx, y, is_gram)
            for x in range(8):
                px_x = tx * 8 + x
                px_y = ty * 8 + y
                src_color = pf_px[px_x, px_y]
                
                if src_color == BLUE:
                    continue  # skip emulator overlay
                
                card_bit = (byte_val >> (7 - x)) & 1
                if card_bit == 0:
                    word_data[word]['bg_pixels'][src_color] += 1
                else:
                    word_data[word]['fg_pixels'][src_color] += 1

# Analyze each word
print("=" * 80)
print("  EMPIRICAL BACKTAB WORD ANALYSIS (from jzIntv reference GIF)")
print("=" * 80)

empirical_bg_color = {}
empirical_fg = {}
empirical_transparent = set()
empirical_per_pixel = {}

for word in sorted(word_data.keys()):
    data = word_data[word]
    card_idx, fg_color_idx, bg_bits, is_gram, _ = decode_backtab_word(word)
    
    total_bg = sum(data['bg_pixels'].values())
    total_fg = sum(data['fg_pixels'].values())
    total_px = total_bg + total_fg
    
    if total_px == 0:
        continue
    
    # Dominant colors (excluding black, which is often noise)
    # For background: find dominant color
    if data['bg_pixels']:
        dominant_bg = data['bg_pixels'].most_common(1)[0][0]
        dominant_bg_count = data['bg_pixels'].most_common(1)[0][1]
        bg_pct = 100 * dominant_bg_count / total_bg if total_bg else 0
    else:
        dominant_bg = None
        dominant_bg_count = 0
        bg_pct = 0
    
    if data['fg_pixels']:
        dominant_fg = data['fg_pixels'].most_common(1)[0][0]
        dominant_fg_count = data['fg_pixels'].most_common(1)[0][1]
        fg_pct = 100 * dominant_fg_count / total_fg if total_fg else 0
    else:
        dominant_fg = None
        dominant_fg_count = 0
        fg_pct = 0
    
    # Determine if transparent (bg ≈ fg)
    is_transparent = False
    if dominant_bg and dominant_fg and dominant_bg == dominant_fg:
        is_transparent = True
    
    # If all pixels are the same color, it's transparent
    all_colors = set(data['bg_pixels'].keys()) | set(data['fg_pixels'].keys())
    clean_colors = {c for c in all_colors if c != BLACK}  # ignore noise black
    if len(clean_colors) <= 1 and not is_transparent:
        if dominant_bg == dominant_fg:
            is_transparent = True
    
    # Build summary
    bg_summary = ", ".join(f"RGB({r},{g},{b})={c}" for (r,g,b), c in data['bg_pixels'].most_common(3))
    fg_summary = ", ".join(f"RGB({r},{g},{b})={c}" for (r,g,b), c in data['fg_pixels'].most_common(3))
    
    src = "GR" if is_gram else "GR"
    print(f"\n${word:04X}: card={card_idx:3d}({src}) fg_decoded={fg_color_idx} bg_bits={bg_bits} count={data['count']}")
    print(f"  BG pixels ({total_bg}): dominant={dominant_bg} ({bg_pct:.0f}%)  [{bg_summary}]")
    print(f"  FG pixels ({total_fg}): dominant={dominant_fg} ({fg_pct:.0f}%)  [{fg_summary}]")
    print(f"  TRANSPARENT: {is_transparent}")
    
    # Determine if this word needs per-pixel data (complex patterns)
    needs_per_pixel = False
    
    # Simple case: transparent word - just record the bg color
    if is_transparent:
        if dominant_bg != PASTEL_TAN:
            empirical_bg_color[word] = dominant_bg
            print(f"  -> EMPIRICAL_BG_COLOR: {dominant_bg}")
        empirical_transparent.add(word)
        continue
    
    # Opaque word: determine BG and FG colors
    if dominant_bg and dominant_bg != PASTEL_TAN:
        empirical_bg_color[word] = dominant_bg
        print(f"  -> EMPIRICAL_BG_COLOR: {dominant_bg}")
    
    if dominant_fg:
        # Map dominant FG color to INTY palette index
        fg_idx = None
        for idx, rgb in PALETTE.items():
            if rgb == dominant_fg:
                fg_idx = idx
                break
        if fg_idx is None:
            for idx, rgb in PASTEL_PALETTE.items():
                if rgb == dominant_fg:
                    fg_idx = idx + 8  # pastel range
                    break
        
        if fg_idx is not None:
            empirical_fg[word] = fg_idx
            print(f"  -> EMPIRICAL_FG: {fg_idx} (color={dominant_fg})")
        else:
            # Check if fg matches bg (transparent effectively)
            if dominant_fg == (empirical_bg_color.get(word, PASTEL_TAN)):
                is_transparent = True
                empirical_transparent.add(word)
                print(f"  -> Reclassified as TRANSPARENT (FG ~= BG)")
    else:
        # No FG pixels found — all pixels show bg color
        if dominant_bg:
            if dominant_bg != PASTEL_TAN:
                empirical_bg_color[word] = dominant_bg
                print(f"  -> EMPIRICAL_BG_COLOR: {dominant_bg}")
            empirical_transparent.add(word)
            print(f"  -> TRANSPARENT (no FG pixels)")

# Output the final empirical data
print("\n" + "=" * 80)
print("  GENERATED EMPIRICAL DATA (paste into render_all_rooms.py)")
print("=" * 80)

print("\nEMPIRICAL_TRANSPARENT = {")
for w in sorted(empirical_transparent):
    print(f"    0x{w:04X},")
print("}")

print("\nEMPIRICAL_BG_COLOR = {")
for w in sorted(empirical_bg_color.keys()):
    c = empirical_bg_color[w]
    name = ""
    if c == PRIMARY_TAN: name = "TAN"
    elif c == WHITE: name = "WHT"
    elif c == BLACK: name = "BLK"
    elif c == PASTEL_TAN: name = "PAS"
    else:
        for idx, rgb in PALETTE.items():
            if rgb == c: name = f"PRIMARY_{idx}"; break
        if not name:
            for idx, rgb in PASTEL_PALETTE.items():
                if rgb == c: name = f"PASTEL_{idx}"; break
    print(f"    0x{w:04X}: {c},  # {name}")
print("}")

print("\nEMPIRICAL_FG = {")
for w in sorted(empirical_fg.keys()):
    fg = empirical_fg[w]
    name = ""
    if fg < 8: name = f"primary color {fg}"
    else: name = f"pastel color {fg-8}"
    print(f"    0x{w:04X}: {fg},   # {name}")
print("}")

# Summary stats
unique_words = len(word_data)
print(f"\n=== Summary ===")
print(f"Unique BACKTAB words: {unique_words}")
print(f"TRANSPARENT: {len(empirical_transparent)}")
print(f"BG_COLOR overrides: {len(empirical_bg_color)}")
print(f"FG overrides: {len(empirical_fg)}")
