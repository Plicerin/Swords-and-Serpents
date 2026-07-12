#!/usr/bin/env python3
"""Extract all ROM/EXEC tables needed to trace the room-drawing pipeline."""
import struct, sys

# Force ASCII-safe output
sys.stdout.reconfigure(encoding='ascii', errors='replace')

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()
with open('exec.bin', 'rb') as f:
    exec_rom = f.read()

def rw(a):
    if a < 0x5000:
        if a < len(exec_rom):
            return struct.unpack_from('<H', exec_rom, a)[0]
        return 0
    offset = a - 0x5000
    if offset + 1 < len(rom):
        return struct.unpack_from('<H', rom, offset)[0]
    return 0

# 1. CS init
print("=== CS init at $554E (6 words) ===")
for i in range(6):
    w = rw(0x554E + i*2)
    print(f"  [{i}]: ${w:04X}  color={w&7}  pastel={bool(w&8)}")

# 2. $00CE lookup table
print("\n=== $00CE lookup table (first 32) ===")
ce_table = [rw(0x00CE + i*2) for i in range(128)]
for i in range(32):
    print(f"  [{i:3d}] ${0xCE+i*2:04X}: ${ce_table[i]:04X}")

# 3. Room data
print("\n=== Room data at $65DC (128 words) ===")
room_data = [rw(0x65DC + i*2) for i in range(128)]
for i in range(128):
    if i % 16 == 0:
        print(f"  +{i*2:04X}:", end="")
    print(f" ${room_data[i]:04X}", end="")
    if (i+1) % 16 == 0:
        print()
print()

# 4. Color/card tables
print("=== Tile color table at $65B7 (64 words) ===")
color_table = [rw(0x65B7 + i*2) for i in range(64)]
for i in range(32):
    print(f"  [{i:2d}]: ${color_table[i]:04X}")

print("\n=== Tile card table at $65A0 (64 words) ===")
card_table = [rw(0x65A0 + i*2) for i in range(64)]
for i in range(32):
    print(f"  [{i:2d}]: ${card_table[i]:04X}")

# 5. Room 0 tile index grid
print("\n=== Room 0 tile indices (4-bit) ===")
for y in range(26, 38):
    line = ""
    for x in range(2, 22):
        y_idx = ((y & 0x30) >> 3)
        x_idx = ((x & 0x60) >> 5)
        r3 = y_idx + (x_idx >> 1)
        room_word = rw(0x65DC + r3 * 2)
        if x & 1:
            tile_idx = (room_word >> 12) & 0xF
        else:
            tile_idx = room_word & 0xF
        line += f"{tile_idx:X} " if tile_idx else ". "
    print(f"  Y={y:2d}: {line}")

# 6. BACKTAB construction
print("\n=== Trace L_5EC7 BACKTAB construction ===")
def trace_l5ec7(tile_data_val):
    idx = tile_data_val >> 5
    cv = color_table[idx] if idx < len(color_table) else 0
    ca = card_table[idx] if idx < len(card_table) else 0
    
    r1_s = cv >> 2
    r1_sw = ((r1_s & 0xFF) << 8) | ((r1_s >> 8) & 0xFF)
    r1_x = r1_sw ^ cv
    r1_m = r1_x & 0x3607
    r3_s = (ca << 3) & 0xFFFF
    backtab = r1_m ^ r3_s
    
    card_num = backtab & 0x3F
    is_gram = bool(backtab & 0x800)
    fg = ((backtab >> 13) & 6) | ((backtab >> 12) & 1)
    
    return backtab, idx, cv, ca, card_num, is_gram, fg

for tv in [0x1603, 0x0207, 0x03E7, 0x0E60, 0x025F, 0x03B7, 0x02AF, 0x0247]:
    bt, idx, cv, ca, cn, ig, fg = trace_l5ec7(tv)
    print(f"  data=${tv:04X} idx={idx:2d} cv=${cv:04X} ca=${ca:04X} BACKTAB=${bt:04X} card={cn} {'GRAM' if ig else 'GROM'} fg={fg}")

print("\nDone.")
