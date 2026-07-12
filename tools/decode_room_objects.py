#!/usr/bin/env python3
"""Decode room object placement data from ROM at $64DE-$655D."""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

rom = open('Swords and Serpents.bin', 'rb').read()

def rw(a):
    o = (a - 0x5000) * 2
    if o + 1 < len(rom):
        return (rom[o] << 8) | rom[o + 1]
    return 0

print("=" * 70)
print("ROOM OBJECT PLACEMENT DATA at ROM $64DE-$655D")
print("Each object is a pair of 16-bit words: [row/col info, type info]")
print("Used by L_6377: reads 16 objects (R3=16), processes via L_6394→L_63B9")
print("=" * 70)

# The data at $64DE is organized as pairs
# First word: column in low 5 bits, row in next bits
# Second word: type index mixed with other info
# We read 16 pairs (R3=16 at L_6383)

for idx in range(16):
    addr = 0x64DE + idx * 4
    w0 = rw(addr)
    w1 = rw(addr + 2) if addr + 2 < 0x6560 else 0
    
    # Try different decoding schemes
    # Scheme A: column=low 5 bits, row=bits 5-8
    col_a = w0 & 0x1F
    row_a = (w0 >> 5) & 0x0F
    
    # Scheme B: full decode as per L_6394 (subtract G_0175, G_0176)
    # G_0175 = 2, G_0176 = 26 (0x1A) per L_55BF init
    
    print(f"  Obj {idx:2d} (${addr:04X}): "
          f"w0=${w0:04X} (col={col_a:2d} row={row_a:2d})  "
          f"w1=${w1:04X}")

print()
print("=" * 70)
print("OBJECT TYPE MAPPING")
print("Types 0-7: Floor tiles (conditional on bitmask at $0180+)")
print("Types 8-31: Wall/door/object tiles (always drawn)")
print("=" * 70)
for t in range(32):
    bt = rw(0x655E + t * 2)
    card = bt & 0xFF
    color = (bt >> 8) & 0x07
    fg_bg = (bt >> 11) & 0x03
    label = ""
    if t <= 7:
        label = " [FLOOR - conditional]"
    print(f"  Type {t:2d}: BACKTAB=${bt:04X}  card=${card:02X} color={color} fg/bg={fg_bg}{label}")
