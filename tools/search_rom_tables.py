#!/usr/bin/env python3
"""Search ROM for $65A0/$65B7 data with different byte interpretations."""
import sys
sys.stdout.reconfigure(encoding='cp1252', errors='replace')

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

print(f'ROM size: {len(rom)} bytes = {hex(len(rom))}')

# The raw bytes at known offsets
print('\n=== $65A0 region (LE interpretation) ===')
o2 = 0x2B40
for i in range(23):
    o = o2 + i * 2
    le = rom[o] | (rom[o+1] << 8)
    print(f'  ${0x65A0+i:04X} -> LE={le:04X}')

print('\n=== $65B7 region (LE interpretation) ===')
o3 = 0x2B6E
for i in range(23):
    o = o3 + i * 2
    le = rom[o] | (rom[o+1] << 8)
    print(f'  ${0x65B7+i:04X} -> LE={le:04X}')

# Search for patterns that look like table data
print('\n=== Searching for 0000 pattern (potential table gaps) ===')
pattern = bytes([0x00, 0x00, 0x00, 0x00])
pos = 0
found = 0
while found < 20:
    idx = rom.find(pattern, pos)
    if idx == -1: break
    if idx >= 0x2B40 and idx <= 0x2C00:  # Only show $65A0 region
        print(f'  0000 at file offset {idx:04X} (CPU ~${0x5000+idx//2:04X})')
        start = max(0, idx-6)
        end = min(len(rom), idx+20)
        hex_str = ' '.join(f'{rom[i]:02X}' for i in range(start, end))
        print(f'    [{start:04X}]: {hex_str}')
        found += 1
    pos = idx + 1

# Byte-swapped test
print('\n=== Byte-swapped interpretation (high byte from odd offset) ===')
for i in range(16):
    o = 0x2B40 + i * 2
    swapped = (rom[o+1] << 8) | rom[o]
    be = (rom[o] << 8) | rom[o+1]
    print(f'  file[{o:04X}]: raw={rom[o]:02X} {rom[o+1]:02X}  BE={be:04X}  swapped={swapped:04X}')
