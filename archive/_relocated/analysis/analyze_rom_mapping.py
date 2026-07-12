#!/usr/bin/env python3
"""Compare ROM file with jzIntv memory dumps to understand memory mapping."""
import struct

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

print(f'Total ROM size: {len(rom)} bytes = ${len(rom):X}')
print()

print('=== File offset 0x0000 (would be CPU $5000 if mapped) ===')
for i in range(16):
    w = struct.unpack_from('<H', rom, i*2)[0]
    print(f'  ${0x5000+i*2:04X}: ${w:04X}')

print()
print('=== File offset 0x15CE (would be CPU $65CE if mapped linearly) ===')
for i in range(16):
    off = 0x15CE + i*2
    w = struct.unpack_from('<H', rom, off)[0]
    print(f'  ${off:04X} (CPU ${off+0x5000:04X}): ${w:04X}')

print()
print('=== File offset 0x1D86 (would be CPU $6D86) ===')
for i in range(16):
    off = 0x1D86 + i*2
    if off + 1 < len(rom):
        w = struct.unpack_from('<H', rom, off)[0]
        print(f'  ${off:04X}: ${w:04X}')

print()
print('=== File offset 0x0000 raw first 16 bytes ===')
for i in range(16):
    print(f'  +{i:04X}: {rom[i]:02X}')

print()
# Check if there's a repeat/mirror pattern
print('=== Check: does file offset 0x0000 match jzIntv $5000 dump? ===')
# jzIntv at reset showed $5000: $0000 $0000 $0000 $0050 $0017 $0050...
# As bytes: 00 00 00 00 00 50 17 50 0F 50 0D 50 0F 50 80 01
file_bytes = [rom[i] for i in range(16)]
jzintv_bytes = [0x00, 0x00, 0x00, 0x00, 0x00, 0x50, 0x17, 0x50, 
                0x0F, 0x50, 0x0D, 0x50, 0x0F, 0x50, 0x80, 0x01]
print(f'  File:    {" ".join(f"{b:02X}" for b in file_bytes)}')
print(f'  jzIntv:  {" ".join(f"{b:02X}" for b in jzintv_bytes)}')
print(f'  Match: {file_bytes == jzintv_bytes}')
