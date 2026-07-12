#!/usr/bin/env python3
"""Raw hex dump of ROM object table at $655E-$659D."""
import sys, struct
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

# ROM at $5000 in CP-1610 space = file offset 0
# offset = (addr - 0x5000) * 2
base = 0x655E
off = (base - 0x5000) * 2
print(f"Object table at ROM ${base:04X} = file offset ${off:04X}")
print()

print("=== Object table: 32 words (types 0-31) ===")
for t in range(32):
    addr = base + t * 2
    o = (addr - 0x5000) * 2
    b0 = rom[o] if o < len(rom) else 0
    b1 = rom[o+1] if o+1 < len(rom) else 0
    word = (b0 << 8) | b1
    card = word & 0xFF
    attr = (word >> 8) & 0xFF
    print(f"  Type {t:2d} @ROM ${addr:04X} (off ${o:04X}): "
          f"bytes=({b0:02X},{b1:02X}) word=${word:04X} "
          f"attr=${attr:02X} card=${card:02X}")

print()
print("=== ROM file header / first 32 bytes ===")
for i in range(0, min(32, len(rom)), 16):
    hexstr = ' '.join(f'{rom[i+j]:02X}' for j in range(16) if i+j < len(rom))
    print(f"  ${i:04X}: {hexstr}")

print(f"\nTotal ROM size: {len(rom)} bytes ({len(rom)//2} words)")
print(f"Expected 8K words (16KB) ROM: {len(rom)==16384}")

# Also dump $6580 table (type index lookup)
print()
print("=== Type index table at $6580-$659F ===")
for i in range(16):
    addr = 0x6580 + i * 2
    o = (addr - 0x5000) * 2
    b0 = rom[o] if o < len(rom) else 0
    b1 = rom[o+1] if o+1 < len(rom) else 0
    word = (b0 << 8) | b1
    print(f"  idx {i:2d} @ROM ${addr:04X}: ${word:04X}")
