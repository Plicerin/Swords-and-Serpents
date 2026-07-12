#!/usr/bin/env python3
"""Dump all object-related ROM tables for BACKTAB reverse engineering."""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

rom = open('Swords and Serpents.bin', 'rb').read()

def rw(a):
    """Read 16-bit word from ROM at CP-1610 address a."""
    o = (a - 0x5000) * 2
    if o + 1 < len(rom):
        return (rom[o] << 8) | rom[o + 1]
    return 0

print("=" * 70)
print("OBJECT BACKTAB TABLE at ROM $655E-$659D (32 entries, 2 bytes each)")
print("Used by L_63EC: MVI@ R4, R0; MVO@ R0, R5  (R4 = $655E + type*2)")
print("=" * 70)
for i in range(32):
    addr = 0x655E + i * 2
    val = rw(addr)
    # Decode BACKTAB: bits 15-11=f.g/b, 10-8=color, 7-0=card
    card = val & 0xFF
    color = (val >> 8) & 0x07
    fg_bg = (val >> 11) & 0x1F
    grom_char = card & 0x3F  # lower 6 bits = GROM char
    print(f"  Type {i:2d} (ROM ${addr:04X}): BACKTAB=${val:04X}  "
          f"card=${card:02X}(${card:3d}) color={color} fg/bg=${fg_bg:02X}  GROM={grom_char:02X}")

print()
print("=" * 70)
print("OBJECT TYPE INDEX TABLE at ROM $6580-$659F (16 entries)")
print("Used by L_63B9: ADDI #$6580, R1; MVI@ R1, R2")
print("Each entry indexes into the BACKTAB table above (via RRC/RLC extraction)")
print("=" * 70)
for i in range(16):
    addr = 0x6580 + i * 2
    val = rw(addr)
    # Extract type index: the value is rotated/manipulated
    low5 = val & 0x1F
    print(f"  Index {i:2d} (ROM ${addr:04X}): ${val:04X}  low5={low5:2d}  "
          f"bin={val:016b}")

print()
print("=" * 70)
print("ROOM OBJECT DATA at ROM $64E0-$655D")
print("Used by L_6377: MVII #$64DE, R4; ...")
print("Pairs of words describe objects placed in the room")
print("=" * 70)
for i in range(0x64E0, 0x655E, 4):  # step by 4 (two 16-bit words)
    w0 = rw(i)
    w1 = rw(i + 2) if i + 2 < 0x655E else 0
    if w0 == 0 and w1 == 0:
        continue  # skip empty entries
    print(f"  ${i:04X}: ${w0:04X}  ${w1:04X}  "
          f"(row/col/pair: {w0&0x1F},{w0>>5}  {w1&0x1F},{w1>>5})")

print()
print("=" * 70)
print("CROSS-REFERENCE: Compare with actual BACKTAB from runtime capture")
print("=" * 70)
# Known actual BACKTAB words from earlier capture
actual_bt = {
    0x0200: 0x1603, 0x0201: 0x1603, 0x0202: 0x1603, 0x0203: 0x1603,
    0x0204: 0x1603, 0x0205: 0x1603, 0x0206: 0x1603, 0x0207: 0x0207,
    # etc. - will be populated from capture
}
# List all unique BACKTAB values from the object table
unique_bt = set()
for i in range(32):
    unique_bt.add(rw(0x655E + i * 2))
print(f"Unique BACKTAB values in object table: {len(unique_bt)}")
for bt in sorted(unique_bt):
    print(f"  ${bt:04X}")
