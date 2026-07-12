"""Compare pipeline render of room 0 against the clean reference (built from jzIntv GIF)."""
from PIL import Image
import sys
sys.path.insert(0, '.')
from render_all_rooms import (
    decode_backtab_word, PALETTE, PASTEL_PALETTE,
    EMPIRICAL_TRANSPARENT, EMPIRICAL_FG, EMPIRICAL_BG_COLOR, EMPIRICAL_PER_PIXEL,
    load_grom, get_grom_card_bytes, parse_backtab, extract_backtab_from_output,
    parse_memory_dump, extract_gram_from_output,
)

pipeline = Image.open('sprites/rooms/dungeon_room_0_pipeline.png').convert('RGB')
clean = Image.open('sprites/rooms/dungeon_room_0.png').convert('RGB')

pp = pipeline.load()
cp = clean.load()

match = 0
total = pipeline.width * pipeline.height
mismatches = {}

for y in range(pipeline.height):
    for x in range(pipeline.width):
        pc = pp[x, y]
        cc = cp[x, y]
        if pc == cc:
            match += 1
        else:
            key = (pc, cc)
            mismatches[key] = mismatches.get(key, 0) + 1

print(f'Pipeline: {pipeline.width}x{pipeline.height}')
print(f'Clean ref: {clean.width}x{clean.height}')
print(f'Match: {match}/{total} = {100*match/total:.1f}%')
print(f'Mismatch: {total-match} px')
print(f'\nMismatch by (pipeline_color, clean_color):')
for (pc, cc), cnt in sorted(mismatches.items(), key=lambda x: -x[1]):
    pct = 100*cnt/total
    print(f'  pipeline RGB{pc} -> clean RGB{cc} : {cnt} px ({pct:.2f}%)')

# Analyze which BACKTAB tiles have mismatched pixels
# Load BACKTAB
with open('traces/rooms/render_room_0_out.txt', 'r') as f:
    output = f.read()
backtab_text = extract_backtab_from_output(output)
backtab_grid = parse_backtab(backtab_text)

BLUE = (20, 56, 247)
PASTEL_TAN = PASTEL_PALETTE[3]
PRIMARY_TAN = PALETTE[3]
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Per-tile mismatch analysis
tile_mismatches = {}
for ty in range(12):
    for tx in range(20):
        word = backtab_grid[ty][tx]
        tile_key = (ty, tx, word)
        wrong = 0
        for y in range(32):
            for x in range(32):
                px_x = tx * 32 + x
                px_y = ty * 32 + y
                if pp[px_x, px_y] != cp[px_x, px_y]:
                    wrong += 1
        if wrong > 0:
            tile_mismatches[tile_key] = wrong

print(f'\n=== Tiles with mismatches ({len(tile_mismatches)}) ===')
for (ty, tx, word), wrong in sorted(tile_mismatches.items(), key=lambda x: -x[1]):
    _, fg, _, is_gram, fg_transp = decode_backtab_word(word)
    in_fg = word in EMPIRICAL_FG
    in_transp = word in EMPIRICAL_TRANSPARENT
    in_bg = word in EMPIRICAL_BG_COLOR
    in_pp = word in EMPIRICAL_PER_PIXEL
    flags = []
    if in_fg: flags.append(f'FG={EMPIRICAL_FG[word]}')
    if in_transp: flags.append('TRANSP')
    if in_bg: flags.append(f'BG={EMPIRICAL_BG_COLOR[word]}')
    if in_pp: flags.append('PER_PIXEL')
    decoded = f'fg={fg} transp={fg_transp}'
    print(f'  [{ty:2d},{tx:2d}] ${word:04X} {decoded} | {", ".join(flags)} | {wrong}/1024 wrong')
