#!/usr/bin/env python3
"""Determine ROM bank mapping by comparing file bytes with jzIntv runtime dumps."""
import struct

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

print(f"ROM size: {len(rom)} bytes = ${len(rom):X}")
print(f"Bank 0: file offset $0000-$1FFF -> CPU $5000-$6FFF")
print(f"Bank 1: file offset $2000-$3FFF -> CPU $????(or $5000 if bankswitched)")
print()

# === The $65CE table (SDBD pointer table) ===
print("=" * 70)
print("$65CE TABLE COMPARISON")
print("=" * 70)

# jzIntv runtime words at $65CE-$65EE (from verify_mem2_out.txt)
jzintv_65CE = [
    0x0098, 0x006C, 0x0011, 0x006D, 0x0086, 0x006D, 0x0013, 0x006E,
    0x009E, 0x006E, 0x0020, 0x006F, 0x009E, 0x006F, 0x0042, 0x006A,
]
jzintv_cont = [
    0x0084, 0x0020, 0x0006, 0x00A6, 0x00AA, 0x0002, 0x0080, 0x0040,
    0x002A, 0x0086, 0x00A2, 0x0004, 0x0026, 0x006A, 0x0004, 0x008A,
]

def read_words(rom, file_offset, count):
    return [struct.unpack_from('<H', rom, file_offset + i*2)[0] for i in range(count)]

# Bank 0: file offset $15CE
bank0_65CE = read_words(rom, 0x15CE, 16)
bank0_cont = read_words(rom, 0x15CE + 32, 16)

print("\nBank 0 (file $15CE):")
for i in range(16):
    match = "✓" if bank0_65CE[i] == jzintv_65CE[i] else "✗"
    print(f"  ${0x65CE+i*2:04X}: ${bank0_65CE[i]:04X} (jzintv: ${jzintv_65CE[i]:04X}) {match}")

# Bank 1: file offset $35CE = $2000 + $15CE
bank1_65CE = read_words(rom, 0x35CE, 16)
bank1_cont = read_words(rom, 0x35CE + 32, 16)

print("\nBank 1 (file $35CE):")
for i in range(16):
    match = "✓" if bank1_65CE[i] == jzintv_65CE[i] else "✗"
    print(f"  ${0x65CE+i*2:04X}: ${bank1_65CE[i]:04X} (jzintv: ${jzintv_65CE[i]:04X}) {match}")

# === The $6D86 pointer destination ===
print("\n" + "=" * 70)
print("$6D86 POINTER DESTINATION COMPARISON (first 16 words)")
print("=" * 70)

# jzIntv runtime words at $6D86
jzintv_6D86 = [
    0x0126, 0x0061, 0x0128, 0x0061, 0x0127, 0x000A, 0x0122, 0x0061,
    0x0125, 0x0061, 0x0126, 0x0061, 0x0128, 0x0061, 0x0127, 0x000B,
]

# Bank 0: file offset $1D86
bank0_6D86 = read_words(rom, 0x1D86, 16)
print("\nBank 0 (file $1D86):")
for i in range(16):
    match = "✓" if bank0_6D86[i] == jzintv_6D86[i] else "✗"
    print(f"  ${0x6D86+i*2:04X}: ${bank0_6D86[i]:04X} (jzintv: ${jzintv_6D86[i]:04X}) {match}")

# Bank 1: file offset $3D86 = $2000 + $1D86
bank1_6D86 = read_words(rom, 0x3D86, 16)
print("\nBank 1 (file $3D86):")
for i in range(16):
    match = "✓" if bank1_6D86[i] == jzintv_6D86[i] else "✗"
    print(f"  ${0x6D86+i*2:04X}: ${bank1_6D86[i]:04X} (jzintv: ${jzintv_6D86[i]:04X}) {match}")

# === What about $136D (another pointer destination from the table)? ===
print("\n" + "=" * 70)
print("$136D POINTER DESTINATION COMPARISON")
print("=" * 70)

# jzIntv runtime words at $136D (from dump_pointers_out.txt)
jzintv_136D = [
    0x01A3, 0x0343, 0x0116, 0x022E, 0x0148, 0x0343, 0x0117, 0x0225,
]

# But $136D is below $5000. In bank 0, this would be EXEC ROM area.
# Let me check what's there in the file
# Actually $136D is in the $1000-$1FFF range which is EXEC ROM, not game ROM.
# This might be in Scratch RAM, System RAM, or GRAM.
print("\n$136D is below $5000 - checking both EXEC ROM and possible RAM mapping.")
# Check EXEC ROM area
exec_data = read_words(rom, 0, 16)  # First 16 words
print("Note: $136D is in $1000-$1FFF range (EXEC ROM) or could be RAM/GRAM")
print(f"jzIntv shows at $136D: " + " ".join(f"${w:04X}" for w in jzintv_136D))

# === Decode SDBD pointer table properly ===
print("\n" + "=" * 70)
print("DECODING SDBD POINTER TABLE FROM jzIntv RUNTIME VALUES")
print("=" * 70)

# SDBD at word address N: lo(word[N]) as low byte, lo(word[N+1]) as high byte
# Because CP-1610 SDBD treats addr as byte address, reading lo byte of each word
all_words = jzintv_65CE + jzintv_cont

print("\nAll 32 words at $65CE:")
for i, w in enumerate(all_words):
    addr = 0x65CE + i*2
    print(f"  ${addr:04X}: ${w:04X} (lo=${w&0xFF:02X}, hi=${(w>>8)&0xFF:02X})")

print("\nSDBD pointer table (16 entries, SDBD at $65CE + index):")
for idx in range(16):
    word_addr = 0x65CE + idx
    lo = all_words[idx] & 0xFF
    hi = all_words[idx + 1] & 0xFF if idx + 1 < len(all_words) else 0
    ptr = (hi << 8) | lo
    in_range = "✓" if 0x5000 <= ptr <= 0x6FFF else ("D000" if 0xD000 <= ptr <= 0xEFFF else "OTHER")
    print(f"  Index {idx:2d}: SDBD ${word_addr:04X} -> lo=${lo:02X} hi=${hi:02X} -> ${ptr:04X} [{in_range}]")

# === Check if these pointers exist in the ROM file (either bank) ===
print("\n" + "=" * 70)
print("VERIFYING POINTER DESTINATIONS IN ROM FILE")
print("=" * 70)

def check_pointer(ptr, bank_name, file_offset, length=8):
    """Read data at a pointer destination from the ROM file."""
    if file_offset + length*2 > len(rom):
        print(f"  {bank_name}: OUT OF RANGE (offset ${file_offset:X} + {length*2} > ${len(rom):X})")
        return
    words = read_words(rom, file_offset, length)
    print(f"  {bank_name} ${ptr:04X} (file ${file_offset:X}): {' '.join(f'${w:04X}' for w in words)}")

# Trace: R2=$6D86 from index 4
# In bank 0: $6D86 -> file $1D86
# In bank 1: $6D86 -> file $3D86
print("\nPointer $6D86 (index 4 in table):")
check_pointer(0x6D86, "Bank 0", 0x1D86)
check_pointer(0x6D86, "Bank 1", 0x3D86)
print("jzIntv:  0061 0126 0061 0128 0061 0127 000A 0122")

# Also check $136D (index 5)
print("\nPointer $136D (index 5 in table):")
# $136D is in the $1000-$1FFF range (EXEC ROM)
# File offset depends on mapping
print("  $136D is in EXEC ROM range ($1000-$1FFF)")
# Check if bank 1 maps to $1000 (unlikely but check)
check_pointer(0x136D, "Bank 1@$1000", 0x336D)

# Check the $6E9E pointer (index 8)
print("\nPointer $6E9E (index 8 in table):")
check_pointer(0x6E9E, "Bank 0", 0x1E9E)
check_pointer(0x6E9E, "Bank 1", 0x3E9E)

print("\nDone.")
