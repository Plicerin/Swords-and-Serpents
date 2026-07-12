#!/usr/bin/env python3
"""Map ROM file to jzIntv memory by binary search for matching data."""
import struct

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

def be_word(offset):
    """Read big-endian 16-bit word at file offset."""
    return rom[offset] * 256 + rom[offset+1]

def find_data_in_rom(target_words, max_offset=None):
    """Search ROM file for a sequence of big-endian words."""
    if max_offset is None:
        max_offset = len(rom) - len(target_words) * 2
    for off in range(0, min(max_offset, len(rom) - len(target_words)*2), 2):
        match = True
        for i, tw in enumerate(target_words):
            if be_word(off + i*2) != tw:
                match = False
                break
        if match:
            return off
    return None

# jzIntv data sequences we know
jzintv_65CE = [0x0058, 0x0058, 0x0058, 0x0098, 0x006C, 0x0011, 0x006D, 0x0086,
               0x006D, 0x0013, 0x006E, 0x009E, 0x006E, 0x0020, 0x006F, 0x009E]

jzintv_5000 = [0x0000, 0x0000, 0x0000, 0x0050, 0x0017, 0x0050, 0x000F, 0x0050]

jzintv_6D86 = [0x0128, 0x0061, 0x0127, 0x000A, 0x0122, 0x0061, 0x0125, 0x0061]

print("=== Searching ROM for known jzIntv data sequences ===")
print()

for name, data, expected_cpu in [
    ("$5000 init vectors", jzintv_5000, 0x5000),
    ("$65CE SDBD table", jzintv_65CE, 0x65CE),
    ("$6D86 tile data", jzintv_6D86, 0x6D86),
]:
    offset = find_data_in_rom(data)
    if offset is not None:
        expected_off = (expected_cpu - 0x5000) * 2
        delta = offset - expected_off
        print(f"{name}:")
        print(f"  Found at file offset ${offset:06X}")
        print(f"  Expected file offset: ${expected_off:06X} (CPU ${expected_cpu:04X})")
        print(f"  Delta: {delta:+d} bytes ({delta//2:+d} words)")
        print(f"  Implied CPU addr: ${0x5000 + offset//2:04X}")
    else:
        print(f"{name}: NOT FOUND in ROM file!")
    print()

# Also do a full correlation: for each 2-byte offset in ROM, compute a "signature"
# and find the offset that gives maximum matches with jzIntv data
print("=== Full correlation: finding best offset match for $65CE data ===")
best_offset = 0
best_matches = 0
for off in range(0, len(rom) - len(jzintv_65CE)*2, 2):
    matches = 0
    for i, expected in enumerate(jzintv_65CE):
        if be_word(off + i*2) == expected:
            matches += 1
    if matches > best_matches:
        best_matches = matches
        best_offset = off

print(f"Best match at file offset ${best_offset:06X}")
print(f"Matches: {best_matches}/{len(jzintv_65CE)}")
print(f"Implied CPU addr: ${0x5000 + best_offset//2:04X}")
expected_off = (0x65CE - 0x5000) * 2
delta = best_offset - expected_off
print(f"Delta from expected: {delta:+d} bytes ({delta//2:+d} words)")
print()

# Show the matching data
print("Expected (jzIntv): " + " ".join(f"${w:04X}" for w in jzintv_65CE))
print("Found at ROM:      " + " ".join(f"${be_word(best_offset+i*2):04X}" for i in range(len(jzintv_65CE))))

print("\nDone.")
