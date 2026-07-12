#!/usr/bin/env python3
"""Verify ROM byte ordering and offset shift vs jzIntv."""
import struct

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

print("=== ROM file bytes at offset 0 (first 32 bytes) ===")
for i in range(0, 32, 2):
    b0, b1 = rom[i], rom[i+1]
    be_word = b0 * 256 + b1
    le_word = b1 * 256 + b0
    print(f"  {i:04X}: {b0:02X} {b1:02X}  (BE=${be_word:04X}, LE=${le_word:04X})")

print()
print("jzIntv at $5000: 0000 0000 0000 0050 0017 0050 000F 0050")
print("                   0D00 0050 000F 0050 0080 0001 0000 0052")

print()
print("=== Testing: BE words from file offset 0 ===")
for i in range(0, 32, 2):
    be = rom[i] * 256 + rom[i+1]
    print(f"  ${0x5000 + i//2:04X}: ${be:04X}")

print()
print("=== Now compare with jzIntv $65CE dump ===")
print("jzIntv at reset: $65C8-$65D6 = 005D 005D 005D 0058 0058 0058 0098 006C")
print("                            $65D8-...  = 0011 006D 0086 006D 0013 006E")

# Read ROM as BE words at file offset (0x65CE - 0x5000) * 2
base = (0x65CE - 0x5000) * 2
print(f"\nROM BE words at file offset {base:#06X} (CPU $65CE):")
for i in range(16):
    off = base + i * 2
    if off + 1 < len(rom):
        be = rom[off] * 256 + rom[off+1]
        print(f"  ${0x65CE + i*2:04X}: ${be:04X}")

# Test with +6 offset
print(f"\nROM BE words at file offset {base+6:#06X} (CPU $65CE + 6-byte shift):")
for i in range(16):
    off = base + 6 + i * 2
    if off + 1 < len(rom):
        be = rom[off] * 256 + rom[off+1]
        print(f"  ${0x65CE + i*2:04X}: ${be:04X}")

# Test with -6 offset (header before ROM data)
print(f"\nROM BE words at file offset {base-6:#06X} (CPU $65CE - 6-byte pre-data):")
for i in range(16):
    off = base - 6 + i * 2
    if off >= 0 and off + 1 < len(rom):
        be = rom[off] * 256 + rom[off+1]
        print(f"  ${0x65CE + i*2:04X}: ${be:04X}")

# Also verify $6D86
print(f"\n=== Verify $6D86 (tile data pointer destination) ===")
base_6D86 = (0x6D86 - 0x5000) * 2
print(f"ROM BE words at file offset {base_6D86:#06X} (CPU $6D86):")
for i in range(8):
    off = base_6D86 + i * 2
    if off + 1 < len(rom):
        be = rom[off] * 256 + rom[off+1]
        print(f"  ${0x6D86 + i*2:04X}: ${be:04X}")

print(f"\nROM BE words at file offset {base_6D86+6:#06X} (CPU $6D86 + 6-byte shift):")
for i in range(8):
    off = base_6D86 + 6 + i * 2
    if off + 1 < len(rom):
        be = rom[off] * 256 + rom[off+1]
        print(f"  ${0x6D86 + i*2:04X}: ${be:04X}")

print("\nDone.")
