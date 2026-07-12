from render_all_rooms import parse_backtab, extract_backtab_from_output, decode_backtab_word, JZINTV_PALETTE
import os

trace_path = r"C:\Users\vrock\Documents\Swords and Serpents\traces\rooms\render_room_0_out_0001.txt"
with open(trace_path, 'r', encoding='utf-8', errors='replace') as f:
    raw = f.read()

grid = parse_backtab(extract_backtab_from_output(raw))
print(f"Grid dimensions: {len(grid)}x{len(grid[0])}")

# Check for any word that results in a "blue" background or white foreground.
# Blue is (0, 45, 255) or similar.
for r in range(len(grid)):
    for c in range(len(grid[0])):
        word = grid[r][c]
        if word == 0: continue
        
        card, fg_i, bg_i, is_gram, _ = decode_backtab_word(word)
        fg = JZINTV_PALETTE[fg_i & 0xF]
        bg = JZINTV_PALETTE[bg_i & 0xF]
        
        # Check if it's blue (index 1)
        if bg == JZINTV_PALETTE[1] or fg == JZINTV_PALETTE[1]:
            print(f"Row {r}, Col {c}: word={word}, fg={fg}, bg={bg}")
