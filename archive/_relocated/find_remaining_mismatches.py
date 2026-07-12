"""Find remaining misclassified tiles by comparing render vs reference tile-by-tile."""
from PIL import Image
from render_all_rooms import (
    decode_backtab_word, EMPIRICAL_TRANSPARENT, EMPIRICAL_FG,
    EMPIRICAL_BG_COLOR, EMPIRICAL_PER_PIXEL,
    parse_memory_dump, extract_backtab_from_output
)

# Load jzIntv output
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

# Load reference and rendered
ref = Image.open('sprites/comparisons/room_0_jzintv.gif').convert('RGB')
rendered = Image.open('sprites/rooms/dungeon_room_0.png').convert('RGB')
rp = ref.load()
np = rendered.load()
BLUE = (20, 56, 247)

# For each tile, check what colors appear in reference vs render
bad_tiles = {}
for tr in range(12):
    for tc in range(20):
        word = grid[tr][tc]
        card, fg, bg_bits, is_gram, fg_transparent = decode_backtab_word(word)
        
        # Sample reference and rendered colors for this tile
        ref_colors = {}
        our_colors = {}
        x0 = 80 + tc * 8
        y0 = 52 + tr * 8
        for y in range(y0, y0+8):
            for x in range(x0, x0+8):
                rc = rp[x,y]
                if rc != BLUE:
                    ref_colors[rc] = ref_colors.get(rc, 0) + 1
                # In rendered, tile at 4x zoom
                for dy in range(4):
                    for dx in range(4):
                        nc = np[tc*32 + (x-x0)*4 + dx, tr*32 + (y-y0)*4 + dy]
                        our_colors[nc] = our_colors.get(nc, 0) + 1
        
        # Check if tile is mismatched
        ref_dominant = max(ref_colors.items(), key=lambda x: x[1]) if ref_colors else ((0,0,0), 0)
        our_dominant = max(our_colors.items(), key=lambda x: x[1]) if our_colors else ((0,0,0), 0)
        
        if ref_dominant[0] != our_dominant[0] and ref_dominant[1] > 4:
            key = (word, ref_dominant[0], our_dominant[0])
            if key not in bad_tiles:
                bad_tiles[key] = []
            bad_tiles[key].append((tr, tc))

def rgb_name(c):
    if c == (58, 138, 0): return 'PASTEL_TAN'
    if c == (203, 241, 104): return 'PRIMARY_TAN'
    if c == (0, 0, 0): return 'BLACK'
    if c == (255, 255, 255): return 'WHITE'
    if c == (0, 148, 40): return 'DARK_GREEN'
    if c == (7, 194, 0): return 'GREEN'
    return f'RGB({c[0]},{c[1]},{c[2]})'

print("Tiles where our dominant color differs from reference:")
for (word, ref_col, our_col), positions in sorted(bad_tiles.items(), key=lambda x: -len(x[1])):
    card, fg, bg_bits, is_gram, fg_transparent = decode_backtab_word(word)
    in_fg = word in EMPIRICAL_FG
    in_bg = word in EMPIRICAL_BG_COLOR
    in_trans = word in EMPIRICAL_TRANSPARENT
    in_pp = word in EMPIRICAL_PER_PIXEL
    
    flags = []
    if in_pp: flags.append('PP')
    if in_fg: flags.append(f'FG={EMPIRICAL_FG.get(word)}')
    if in_bg: flags.append('BG')
    if in_trans: flags.append('TRANSP')
    flag_str = ','.join(flags) if flags else '-'
    
    print(f'\n  ${word:04X}: card={card:3d} fg_decoded={fg} [{flag_str}] {len(positions)} tiles')
    print(f'    ref={rgb_name(ref_col)} our={rgb_name(our_col)}')
    print(f'    positions: {positions[:5]}')
