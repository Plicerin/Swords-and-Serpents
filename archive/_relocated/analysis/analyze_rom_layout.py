#!/usr/bin/env python3
"""Deep ROM analysis: verify $65A0-$65CD data and search for correct mapping."""
import sys
sys.stdout.reconfigure(encoding='cp1252', errors='replace')

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

print(f'ROM size: {len(rom)} bytes = {hex(len(rom))}')

# Known good: $65CE at file offset 0x2B9C (BE, offset=(addr-0x5000)*2)
# jzIntv shows at $65CE: 0098 006C 0011 006D 0086 006D 0013 006E ...

print('\n=== $65CE verification (known good) ===')
o = 0x2B9C  # (0x65CE-0x5000)*2
expected = [0x0098, 0x006C, 0x0011, 0x006D, 0x0086, 0x006D, 0x0013, 0x006E]
for i, exp in enumerate(expected):
    be = (rom[o+i*2] << 8) | rom[o+i*2+1]
    ok = 'OK' if be == exp else 'MISMATCH'
    print(f'  ${0x65CE+i:04X}: BE={be:04X} jzIntv={exp:04X}  {ok}')

print('\n=== $65A0 region (46 words, card + attr tables) ===')
o2 = 0x2B40  # (0x65A0-0x5000)*2
for i in range(46):
    be = (rom[o2+i*2] << 8) | rom[o2+i*2+1]
    print(f'  ${0x65A0+i:04X} -> file[{o2+i*2:04X}]: BE={be:04X}')

print('\n=== Raw hex dump of $65A0 region (0x2B40-0x2B9B) ===')
for row in range(12):
    o3 = 0x2B40 + row * 16
    hex_str = ' '.join(f'{rom[o3+i]:02X}' for i in range(16))
    print(f'  {o3:04X}: {hex_str}')

print('\n=== Searching for alternative $65A0 data ===')
# What if the ROM has the tables copied elsewhere?
# The game code copies data from ROM to RAM during init
# Let's check if there's data at $65A0 that looks like card table entries
# Card table would have words like: card_number, GRAM flag, FG color
# Typical BACKTAB: $1603 = card 3, GRAM, FG=1, CS=0
# Card table values should be small (0-63 for GROM, 0-255 for GRAM)

print('If card table values are small, $0100, $0101 look wrong.')
print()

# Let's try different byte interpretations
print('=== Trying LE+0 mapping (offset from file start, LE) ===')
for i in range(16):
    addr = 0x65A0 + i
    off = (addr - 0x5000) + 0  # try linear
    if off + 1 < len(rom):
        le = rom[off] | (rom[off+1] << 8)
        if le < 0x100:
            print(f'  ${addr:04X}: LE={le:04X} (*potential match - small value)')
