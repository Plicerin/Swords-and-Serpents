"""Analyze BACKTAB words in room 0 vs jzIntv reference to diagnose misclassifications."""
from PIL import Image
from render_all_rooms import (
    decode_backtab_word, EMPIRICAL_TRANSPARENT, EMPIRICAL_FG,
    EMPIRICAL_BG_COLOR, EMPIRICAL_PER_PIXEL, PASTEL_PALETTE, PALETTE,
    parse_memory_dump, extract_backtab_from_output
)

# Load the jzIntv output from room 0
with open('traces/rooms/render_room_0_out.txt', 'r') as f:
    output = f.read()

backtab_text = extract_backtab_from_output(output)
grid = [[0]*20 for _ in range(12)]
mem = parse_memory_dump(backtab_text, 0x0200, 240)
for addr, val in mem.items():
    if 0x0200 <= addr < 0x02F0:
        offset = addr - 0x0200
        row = offset // 20
        col = offset % 20
        if row < 12 and col < 20:
            grid[row][col] = val

# Analyze each unique BACKTAB word
unique_words = {}
for row in range(12):
    for col in range(20):
        w = grid[row][col]
        if w not in unique_words:
            unique_words[w] = {'count': 0, 'positions': []}
        unique_words[w]['count'] += 1
        unique_words[w]['positions'].append((row, col))

print(f'Room 0 BACKTAB: {len(unique_words)} unique words')
print()

# Also load reference to check jzIntv colors at tile centers
ref = Image.open('sprites/comparisons/room_0_jzintv.gif').convert('RGB')
rp = ref.load()

def jzintv_tile_colors(tile_row, tile_col):
    """Get per-pixel color counts from jzIntv for a tile (8x8 at native res)."""
    x0 = 80 + tile_col * 8
    y0 = 52 + tile_row * 8
    colors = {}
    for y in range(y0, y0+8):
        for x in range(x0, x0+8):
            c = rp[x,y]
            colors[c] = colors.get(c, 0) + 1
    return sorted(colors.items(), key=lambda x: -x[1])

def rgb_name(c):
    r,g,b = c
    if c == (58, 138, 0): return 'PASTEL_TAN'
    if c == (203, 241, 104): return 'PRIMARY_TAN'
    if c == (20, 56, 247): return 'BLUE'
    if c == (0, 0, 0): return 'BLACK'
    if c == (255, 255, 255): return 'WHITE'
    if c == (0, 148, 40): return 'DARK_GREEN'
    if c == (7, 194, 0): return 'GREEN'
    if c == (227, 91, 14): return 'RED'
    return f'RGB({r},{g},{b})'

for word, info in sorted(unique_words.items(), key=lambda x: -x[1]['count']):
    card, fg, bg_bits, is_gram, fg_transparent = decode_backtab_word(word)
    in_pp = word in EMPIRICAL_PER_PIXEL
    in_fg = word in EMPIRICAL_FG
    in_bg = word in EMPIRICAL_BG_COLOR
    in_trans = word in EMPIRICAL_TRANSPARENT
    
    # Get jzIntv colors at this tile's position
    r, c = info['positions'][0]
    jz_colors = jzintv_tile_colors(r, c)
    jz_summary = ' + '.join(f'{cnt}*{rgb_name(clr)}' for clr, cnt in jz_colors[:4])
    
    src = 'GRAM' if is_gram else 'GROM'
    flags = []
    if in_pp: flags.append('PER_PIXEL')
    if in_fg: flags.append('FG')
    if in_bg: flags.append('BG')
    if in_trans: flags.append('TRANSP')
    flag_str = ','.join(flags) if flags else '-'
    
    print(f'  ${word:04X}: card={card:3d} ({src}) fg={fg} trans={fg_transparent:5} '
          f'[{flag_str}] count={info["count"]:2d}')
    print(f'       jzIntv: {jz_summary}')
    
    # Calculate what fraction is "overlay" (blue) vs actual card content
    blue_px = sum(cnt for clr, cnt in jz_colors if clr == (20, 56, 247))
    total_px = sum(cnt for _, cnt in jz_colors)
    non_blue_pct = 100 * (total_px - blue_px) / total_px if total_px > 0 else 0
    print(f'       non-blue: {non_blue_pct:.0f}%  (blue={blue_px}px)')
    
    # What would this tile look like WITHOUT blue?
    if blue_px > 0:
        non_blue = [(clr, cnt) for clr, cnt in jz_colors if clr != (20, 56, 247)]
        real_summary = ' + '.join(f'{cnt}*{rgb_name(clr)}' for clr, cnt in non_blue[:3])
        print(f'       w/o blue:  {real_summary}')
    print()
