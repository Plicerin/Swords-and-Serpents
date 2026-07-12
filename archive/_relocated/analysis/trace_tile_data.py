#!/usr/bin/env python3
"""Trace the complete room-drawing pipeline: $00CE pointers -> tile data -> BACKTAB."""
import struct, sys
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

# $00CE table
ce_table = [rw(0x00CE + i*2) for i in range(16)]

# Color/card tables
color_table = [rw(0x65B7 + i*2) for i in range(64)]
card_table = [rw(0x65A0 + i*2) for i in range(64)]

print("=== $00CE lookup table (16 entries) ===")
for i, ptr in enumerate(ce_table):
    print(f"  tile_idx={i}: ptr=${ptr:04X}")

# Trace: what data is at the pointers?
print("\n=== Data at tile_idx=6 pointer ($1601) ===")
ptr6 = ce_table[6]
print(f"  Pointer: ${ptr6:04X}")
for i in range(16):
    w = rw(ptr6 + i*2)
    print(f"    +{i*2}: ${w:04X}")

print("\n=== Data at tile_idx=2 pointer ($0400) ===")
ptr2 = ce_table[2]
print(f"  Pointer: ${ptr2:04X}")
for i in range(16):
    w = rw(ptr2 + i*2)
    print(f"    +{i*2}: ${w:04X}")

# Try to decode RLE structure for tile 6 data
print("\n=== Attempt RLE decode for tile_idx=6 ===")
# The tile data structure: each "row" starts with a word = jump to next row
# Then run-length encoded words: length in low 5 bits, tile data in upper bits
r2 = ptr6
for row in range(4):  # try first 4 rows
    skip = rw(r2)
    print(f"  Row {row}: skip=${skip:04X} (at ${r2:04X})")
    r2 += 1
    # Read run-length entries for this row
    remaining = 20  # 20 columns
    entries = []
    while remaining > 0 and r2 < ptr6 + 100:
        val = rw(r2)
        length = val & 0x1F
        if length == 0:
            length = 32  # wrap-around? no, this might be the tile data
        tile_val = val & 0xFFE0
        entries.append((val, min(length, remaining)))
        remaining -= length
        r2 += 1
        if remaining <= 0:
            break
    print(f"    Entries: {entries}")

print("\nDone.")
