"""Check ROM byte ordering by verifying known values from disassembly."""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

print(f"ROM size: {len(rom)} bytes = {len(rom)//2} words")

# Try both endianness
def rw_be(addr):
    """Big-endian: high byte first"""
    offset = (addr - 0x5000) * 2
    if offset + 1 < len(rom):
        return (rom[offset] << 8) | rom[offset + 1]
    return 0

def rw_le(addr):
    """Little-endian: low byte first"""
    offset = (addr - 0x5000) * 2
    if offset + 1 < len(rom):
        return (rom[offset + 1] << 8) | rom[offset]
    return 0

# Verify known instructions from disassembly
print("\n=== ENDIANNESS CHECK ===")
print(f"  At $5017: DIS should be $0003")
print(f"    Big-endian:  ${rw_be(0x5017):04X}")
print(f"    Little-endian: ${rw_le(0x5017):04X}")

print(f"  At $5018: SDBD should be $0001")
print(f"    Big-endian:  ${rw_be(0x5018):04X}")
print(f"    Little-endian: ${rw_le(0x5018):04X}")

print(f"  At $5019: MVII #$538E,R0 → $02B8")
print(f"    Big-endian:  ${rw_be(0x5019):04X}")
print(f"    Little-endian: ${rw_le(0x5019):04X}")

# Check which gives consistent results
print("\n=== CODE SEQUENCE AT $5017 (first 8 words) ===")
for i, addr in enumerate(range(0x5017, 0x5017+16)):
    be = rw_be(addr)
    le = rw_le(addr)
    print(f"  ${addr:04X}: BE=${be:04X}  LE=${le:04X}")

# Now verify: the object table at $655E
print("\n=== OBJECT TABLE AT $655E (both endianness) ===")
print("  Type  BE-word  LE-word")
for t in range(32):
    addr = 0x655E + t * 2
    be = rw_be(addr)
    le = rw_le(addr)
    
    # Also show raw bytes
    offset = (addr - 0x5000) * 2
    b0 = rom[offset] if offset < len(rom) else 0
    b1 = rom[offset+1] if offset+1 < len(rom) else 0
    
    print(f"  {t:3d}  ${be:04X}   ${le:04X}   raw=({b0:02X},{b1:02X})")

# Compare with actual BACKTAB values
print("\n=== TYPE INDEX TABLE AT $6580 ===")
for i in range(16):
    addr = 0x6580 + i * 2
    be = rw_be(addr)
    le = rw_le(addr)
    print(f"  idx {i:2d}: BE=${be:04X}  LE=${le:04X}")

# Let's also check: room data at $64DE in both endianness
print("\n=== ROOM DATA AT $64DE-$64FF (both endianness) ===")
for i in range(16):
    addr = 0x64DE + i * 2
    be = rw_be(addr)
    le = rw_le(addr)
    offset = (addr - 0x5000) * 2
    b0 = rom[offset] if offset < len(rom) else 0
    b1 = rom[offset+1] if offset+1 < len(rom) else 0
    print(f"  ${addr:04X}: BE=${be:04X} LE=${le:04X} raw=({b0:02X},{b1:02X})")
