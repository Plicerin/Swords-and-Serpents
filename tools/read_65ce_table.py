#!/usr/bin/env python3
"""Read the $65CE lookup table and trace the full room-drawing data flow."""
import struct

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

def rw(a):
    """Read 16-bit little-endian word from ROM address (CPU space $5000-$6FFF)."""
    if a < 0x5000 or a > 0x6FFF:
        return 0
    offset = a - 0x5000
    if offset + 1 >= len(rom):
        return 0
    return struct.unpack_from('<H', rom, offset)[0]

# === The actual lookup table at $65CE ===
print("=== $65CE lookup table (16 entries, tile index -> tile data pointer) ===")
table_entries = []
for i in range(16):
    w = rw(0x65CE + i * 2)
    table_entries.append(w)
    print(f"  [{i:2d}] ${0x65CE+i*2:04X}: ${w:04X}")

print()
print("=== Tracing pointers to their tile data ===")
for i, ptr in enumerate(table_entries):
    if ptr == 0:
        continue
    if ptr < 0x5000 or ptr > 0x6FFF:
        print(f"  [{i:2d}] ${ptr:04X} -> OUT OF RANGE")
        continue
    print(f"  [{i:2d}] ${ptr:04X} -> ROM offset ${ptr-0x5000:04X}:")
    # Read the first 8 words at this pointer
    for j in range(8):
        v = rw(ptr + j * 2)
        if v == 0 and j > 0:
            break
        print(f"       +{j*2:02d}: ${v:04X}")
    print()

# === Compare with tile color/card tables ===
print("=== Tile color table at $65B7 ===")
for i in range(16):
    print(f"  [{i:2d}]: ${rw(0x65B7+i*2):04X}")

print()
print("=== Tile card table at $65A0 ===")
for i in range(16):
    print(f"  [{i:2d}]: ${rw(0x65A0+i*2):04X}")

# === Also dump the raw bytes around $65CE ===
print()
print("=== Raw hex at ROM $15CE (32 bytes) ===")
base = 0x15CE
for row in range(2):
    offset = base + row * 16
    hex_str = ' '.join(f'{b:02X}' for b in rom[offset:offset+16])
    print(f"  ${offset+0x5000:04X}: {hex_str}")

# === What does MVII #$65CE actually look like in ROM? ===
print()
print("=== Instruction bytes at $5E63 ===")
off = 0x5E63 - 0x5000
for i in range(off, off + 10):
    print(f"  ${i+0x5000:04X}: {rom[i]:02X}")

print()
print("=== For comparison: MVII #$65DC, R0 at $55C4 ===")
off = 0x55C4 - 0x5000
for i in range(off, off + 6):
    print(f"  ${i+0x5000:04X}: {rom[i]:02X}")

print()
print("=== For comparison: MVII #$65B7, R0 at $55CA ===")
off = 0x55CA - 0x5000
for i in range(off, off + 6):
    print(f"  ${i+0x5000:04X}: {rom[i]:02X}")

print()
print("Done.")
