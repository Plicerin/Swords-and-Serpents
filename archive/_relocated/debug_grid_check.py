from render_all_rooms import parse_backtab, extract_backtab_from_output
import os

trace_path = r"C:\Users\vrock\Documents\Swords and Serpents\traces\rooms\render_room_0_out_0001.txt"
with open(trace_path, 'r', encoding='utf-8', errors='replace') as f:
    raw = f.read()

grid = parse_backtab(extract_backtab_from_output(raw))
print(f"Grid dimensions: {len(grid)}x{len(grid[0])}")
for r in range(len(grid)):
    for c in range(len(grid[0])):
        if grid[r][c] != 0:
            print(f"Row {r}, Col {c}: {grid[r][c]}")
