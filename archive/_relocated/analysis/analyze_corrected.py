#!/usr/bin/env python3
"""CORRECTED analysis: file_offset = (cpu_addr - 0x5000) * 2 for 16-bit ROM."""
import struct, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

def rw_cpu(cpu_addr):
    """Read 16-bit LE word at CPU address in ROM range."""
    if cpu_addr < 0x5000 or cpu_addr > 0x6FFF:
        return None
    offset = (cpu_addr - 0x5000) * 2
    if offset + 1 >= len(rom):
        return None
    return struct.unpack_from('<H', rom, offset)[0]

# ============================================================
# jzIntv runtime words (from verify_mem2_out.txt step trace)
# ============================================================
# $65CE area
jzintv_65CE_to_65F8 = {
    # Row 1: 65C8: 005D 005D 005D 0058 0058 0058 0098* 006C
    0x65C8: 0x005D, 0x65CA: 0x005D, 0x65CC: 0x005D, 0x65CE: 0x0058,
    0x65D0: 0x0058, 0x65D2: 0x0058, 0x65D4: 0x0098, 0x65D6: 0x006C,
    # Row 2: 65D0: 0011 006D 0086 006D 0013 006E 009E 006E
    0x65D8: 0x0011, 0x65DA: 0x006D, 0x65DC: 0x0086, 0x65DE: 0x006D,
    0x65E0: 0x0013, 0x65E2: 0x006E, 0x65E4: 0x009E, 0x65E6: 0x006E,
    # Row 3: 65D8: 0020 006F 009E 006F 0042 006A 0084 0020
    0x65E8: 0x0020, 0x65EA: 0x006F, 0x65EC: 0x009E, 0x65EE: 0x006F,
    0x65F0: 0x0042, 0x65F2: 0x006A, 0x65F4: 0x0084, 0x65F6: 0x0020,
    # Row 4: 65E0: 0006 00A6 00AA 0002 0080 0040 002A 0086
    0x65F8: 0x0006, 0x65FA: 0x00A6, 0x65FC: 0x00AA, 0x65FE: 0x0002,
    0x6600: 0x0080, 0x6602: 0x0040, 0x6604: 0x002A, 0x6606: 0x0086,
}

# $6D86 area (from dump_pointers_out.txt)
# 6D80: 0061 0126 0061 0128 0061 0127 000A* 0122
# The * at $000A = word at position 6 = $6D80 + 6*2 = $6D8C
# Wait, need to figure out the * position
# "$000A*" in position 6 of 8 means: word 6 = $6D8C = 0x000A
# So: $6D80=0061, $6D82=0126, $6D84=0061, $6D86=0128,
#     $6D88=0061, $6D8A=0127, $6D8C=000A*, $6D8E=0122

jzintv_6D80 = {
    0x6D80: 0x0061, 0x6D82: 0x0126, 0x6D84: 0x0061, 0x6D86: 0x0128,
    0x6D88: 0x0061, 0x6D8A: 0x0127, 0x6D8C: 0x000A, 0x6D8E: 0x0122,
}

# ============================================================
# PART 1: Compare ROM file (corrected mapping) vs jzIntv runtime
# ============================================================
print("=" * 70)
print("PART 1: ROM FILE vs jzIntv RUNTIME (CORRECTED mapping)")
print("=" * 70)
print("Mapping: file_offset = (cpu_addr - 0x5000) * 2")
print()

print("--- $65CE area comparison ---")
print(f"{'CPU Addr':>8}  {'jzIntv':>6}  {'ROM':>6}  {'Match?'}")
print("-" * 40)
matches = 0
mismatches = 0
for addr in range(0x65C8, 0x6608, 2):
    jz = jzintv_65CE_to_65F8.get(addr)
    if jz is None:
        continue
    rom_val = rw_cpu(addr)
    match = "YES" if rom_val == jz else "NO"
    if rom_val == jz:
        matches += 1
    else:
        mismatches += 1
    print(f"  ${addr:04X}    ${jz:04X}    ${rom_val or 0:04X}     {match}")
print(f"Results: {matches} matches, {mismatches} mismatches")

# ============================================================
# PART 2: Also check $6D86 area
# ============================================================
print("\n--- $6D86 area comparison ---")
print(f"{'CPU Addr':>8}  {'jzIntv':>6}  {'ROM':>6}  {'Match?'}")
print("-" * 40)
matches2 = 0
mismatches2 = 0
for addr in range(0x6D80, 0x6D90, 2):
    jz = jzintv_6D80.get(addr)
    if jz is None:
        continue
    rom_val = rw_cpu(addr)
    match = "YES" if rom_val == jz else "NO"
    if rom_val == jz:
        matches2 += 1
    else:
        mismatches2 += 1
    print(f"  ${addr:04X}    ${jz:04X}    ${rom_val or 0:04X}     {match}")
print(f"Results: {matches2} matches, {mismatches2} mismatches")

# ============================================================
# PART 3: Check basic file structure
# ============================================================
print("\n" + "=" * 70)
print("PART 3: BASIC FILE STRUCTURE")
print("=" * 70)
print(f"ROM size: {len(rom)} bytes")
print(f"First word at CPU $5000 = ${rw_cpu(0x5000):04X}")
print(f"Word at CPU $65CE = ${rw_cpu(0x65CE):04X}")
print(f"Word at CPU $6D86 = ${rw_cpu(0x6D86):04X}")
print(f"Last word at CPU $6FFF = ${rw_cpu(0x6FFF):04X}")

# Verify the step trace: SDBD at $65D2 gives $6D86
# lo(word[$65D2]) = $86, lo(word[$65D4]) = $6D
w65D2 = jzintv_65CE_to_65F8.get(0x65D2)
w65D4 = jzintv_65CE_to_65F8.get(0x65D4)
if w65D2 is not None and w65D4 is not None:
    lo_byte = w65D2 & 0xFF
    hi_byte = w65D4 & 0xFF
    sdbd_result = (hi_byte << 8) | lo_byte
    print(f"\nSDBD verification (step trace):")
    print(f"  lo(word[$65D2]) = lo(${w65D2:04X}) = ${lo_byte:02X}")
    print(f"  lo(word[$65D4]) = lo(${w65D4:04X}) = ${hi_byte:02X}")
    print(f"  Combined = ${sdbd_result:04X}")
    print(f"  Step trace shows R2 = $6D86 -> {'CORRECT!' if sdbd_result == 0x6D86 else 'WRONG'}" )

# ============================================================
# PART 4: Full SDBD pointer table with corrected ROM data
# ============================================================
print("\n" + "=" * 70)
print("PART 4: SDBD POINTER TABLE (16 entries)")
print("=" * 70)
print("SDBD at byte address N: lo(word[N]) | lo(word[N+1])")
print()

for idx in range(16):
    byte_addr = 0x65CE + idx
    # Word containing byte_addr (byte address rounds down to even word addr)
    w_lo_addr = (byte_addr // 2) * 2  # This isn't right for CP-1610...
    # Actually, CP-1610 byte address N in word memory:
    # Word for byte N = word at address (N & ~1) if using standard interpretation
    # But jzIntv might use: lo(word[byte_addr]) because byte_addr IS a word address
    # Let me try: byte N reads lo(word[N]) - this worked for $65D2 + $65D4
    lo_word = jzintv_65CE_to_65F8.get(byte_addr, 0xFFFF)
    hi_word = jzintv_65CE_to_65F8.get(byte_addr + 1, 0xFFFF)  # Next word address
    lo = lo_word & 0xFF
    hi = hi_word & 0xFF
    ptr = (hi << 8) | lo
    
    # Now verify against ROM file (corrected mapping)
    rom_lo_word = rw_cpu(byte_addr)
    rom_hi_word = rw_cpu(byte_addr + 1)
    rom_lo = (rom_lo_word or 0xFFFF) & 0xFF
    rom_hi = (rom_hi_word or 0xFFFF) & 0xFF
    rom_ptr = (rom_hi << 8) | rom_lo
    match = "Y" if rom_ptr == ptr else "N"
    
    in_range = ""
    if 0x5000 <= ptr <= 0x6FFF:
        in_range = "ROM"
    elif 0x1000 <= ptr <= 0x1FFF:
        in_range = "EXEC"
    elif 0x3000 <= ptr <= 0x3FFF:
        in_range = "GRAM"
    elif 0x0100 <= ptr <= 0x035F:
        in_range = "RAM"
    else:
        in_range = "OTHER"
    
    marker = " <-- R2=$6D86" if idx == 4 else ""
    print(f"  [{idx:2d}] byte ${byte_addr:04X}: lo(word[${byte_addr:04X}]=${lo_word:04X})={lo:02X} | "
          f"lo(word[${byte_addr+1:04X}]=${hi_word:04X})={hi:02X} -> ${ptr:04X} [{in_range}] ROM={match}{marker}")

print("\nDone.")
