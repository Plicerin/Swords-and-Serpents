#!/usr/bin/env python3
"""Compare ROM file data (both BE and LE) against confirmed jzIntv memory values."""
import sys
sys.stdout.reconfigure(encoding='cp1252', errors='replace')

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

# jzIntv confirmed values from verify_mem2_out.txt
JZINTV = {
    0x65C8: 0x005D, 0x65C9: 0x005D, 0x65CA: 0x005D, 0x65CB: 0x0058,
    0x65CC: 0x0058, 0x65CD: 0x0058, 0x65CE: 0x0098, 0x65CF: 0x006C,
    0x65D0: 0x0011, 0x65D1: 0x006D, 0x65D2: 0x0086, 0x65D3: 0x006D,
    0x65D4: 0x0013, 0x65D5: 0x006E, 0x65D6: 0x009E, 0x65D7: 0x006E,
    0x65D8: 0x0020, 0x65D9: 0x006F, 0x65DA: 0x009E, 0x65DB: 0x006F,
    0x65DC: 0x0042, 0x65DD: 0x006A, 0x65DE: 0x0084, 0x65DF: 0x0020,
    0x65E0: 0x0006, 0x65E1: 0x00A6, 0x65E2: 0x00AA, 0x65E3: 0x0002,
    0x65E4: 0x0080, 0x65E5: 0x0040, 0x65E6: 0x002A, 0x65E7: 0x0086,
}

def rw_be(addr):
    off = (addr - 0x5000) * 2
    if off + 1 >= len(rom):
        return None
    return (rom[off] << 8) | rom[off + 1]

def rw_le(addr):
    off = (addr - 0x5000) * 2
    if off + 1 >= len(rom):
        return None
    return rom[off] | (rom[off + 1] << 8)

print("=== COMPARING ROM vs jzIntv ACTUAL MEMORY ===")
print()
print(f"{'Addr':>6}  {'jzIntv':>6}  {'ROM BE':>6}  {'BE OK?':>6}  {'ROM LE':>6}  {'LE OK?':>6}")
print("-" * 60)
be_ok = le_ok = 0
for addr in sorted(JZINTV.keys()):
    jz = JZINTV[addr]
    be = rw_be(addr)
    le = rw_le(addr)
    be_match = "YES" if be == jz else "NO"
    le_match = "YES" if le == jz else "NO"
    if be == jz: be_ok += 1
    if le == jz: le_ok += 1
    be_str = f"${be:04X}" if be is not None else "???"
    le_str = f"${le:04X}" if le is not None else "???"
    print(f"  ${addr:04X}  ${jz:04X}    {be_str}    {be_match:5s}   {le_str}    {le_match:5s}")

print(f"\n  BE matches: {be_ok}/{len(JZINTV)}")
print(f"  LE matches: {le_ok}/{len(JZINTV)}")

# Now dump the critical $65A0-$65B6 range (card table + attr table start)
print()
print("=== ROM DATA AT $65A0-$65B6 (card table region, 23 words) ===")
print("  Both BE and LE shown. Compare with what jzIntv shows.")
for i in range(23):
    addr = 0x65A0 + i
    be = rw_be(addr)
    le = rw_le(addr)
    print(f"  ${addr:04X}: BE=${be:04X} ({be:5d})  LE=${le:04X} ({le:5d})")

print()
print("=== ROM DATA AT $65B7-$65CF (attr table region, 25 words) ===")
for i in range(25):
    addr = 0x65B7 + i
    be = rw_be(addr)
    le = rw_le(addr)
    print(f"  ${addr:04X}: BE=${be:04X} ({be:5d})  LE=${le:04X} ({le:5d})")

# Also search: where in ROM does $005D $005D $005D $0058 $0058 $0058 appear?
print()
print("=== Searching ROM for jzIntv sequence at $65C8: 005D 005D 005D 0058 0058 0058 ===")
# jzIntv values are LE in memory. So we search for byte patterns.
# As bytes: 5D 00 5D 00 5D 00 58 00 58 00 58 00
pat = bytes([0x5D, 0x00, 0x5D, 0x00, 0x5D, 0x00, 0x58, 0x00, 0x58, 0x00, 0x58, 0x00])
idx = rom.find(pat)
if idx >= 0:
    print(f"  Found LE pattern at file offset {idx:04X}")
    # Map back: if at file offset X, then CPU addr = (X/2) + 0x5000
    cpu_addr = idx // 2 + 0x5000
    print(f"  Corresponds to CPU address ${cpu_addr:04X}")
    print(f"  Expected at $65C8 -> file offset {(0x65C8-0x5000)*2:04X}")
else:
    # Try BE pattern: 00 5D 00 5D 00 5D 00 58 00 58 00 58
    pat_be = bytes([0x00, 0x5D, 0x00, 0x5D, 0x00, 0x5D, 0x00, 0x58, 0x00, 0x58, 0x00, 0x58])
    idx2 = rom.find(pat_be)
    if idx2 >= 0:
        print(f"  Found BE pattern at file offset {idx2:04X}")

# Alternative: search for 0098 sequence (SDBD table start)
print()
print("=== Searching ROM for $0098 $006C (SDBD table start at $65CE) ===")
# LE: 98 00 6C 00
pat_le = bytes([0x98, 0x00, 0x6C, 0x00])
idx_le = rom.find(pat_le)
if idx_le >= 0:
    cpu_addr_le = idx_le // 2 + 0x5000
    print(f"  LE found at file {idx_le:04X} -> CPU ${cpu_addr_le:04X}")
    
# BE: 00 98 00 6C
pat_be = bytes([0x00, 0x98, 0x00, 0x6C])
idx_be = rom.find(pat_be)
if idx_be >= 0:
    cpu_addr_be = idx_be // 2 + 0x5000
    print(f"  BE found at file {idx_be:04X} -> CPU ${cpu_addr_be:04X}")

print(f"\n  Expected at: file {(0x65CE-0x5000)*2:04X} -> CPU $65CE")
