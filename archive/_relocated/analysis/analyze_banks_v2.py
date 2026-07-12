#!/usr/bin/env python3
"""Complete analysis: ROM bank mapping, SDBD table decoding, pointer tracing."""
import struct, sys

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

print(f"ROM size: {len(rom)} bytes = ${len(rom):X} ({len(rom)//1024}KB)")
print(f"Bank 0: file $0000-$1FFF -> CPU $5000-$6FFF")
print(f"Bank 1: file $2000-$3FFF -> CPU $5000-$6FFF (if bankswitched)")
print()

def rw(file_offset):
    """Read 16-bit LE word from ROM at file offset."""
    return struct.unpack_from('<H', rom, file_offset)[0] if file_offset + 1 < len(rom) else 0

# ============================================================
# jzIntv runtime memory at $65CE (32 words, from verify_mem2_out.txt)
# ============================================================
jzintv_words = [
    # Words $65C8-$65CF (prefix)
    None, None, None, None,          # $65C8-$65CE (none shown in dump)
    0x005D, 0x005D, 0x005D, 0x0058,  # $65CE-$65D4 (from $65C8+: 005D 005D 005D 0058)
    # Actually the dump shows: 65C8: 005D 005D 005D 0058 0058 0058 0098 006C
    0x0058, 0x0058, 0x0098, 0x006C,  # $65D6-$65DC
    0x0011, 0x006D, 0x0086, 0x006D,  # $65DE-$65E4 (wait, these don't align right)
]

# Let me reparse the memory dump properly
# 65C8:  005D  005D  005D  0058   0058  0058  0098* 006C
# 65D0:  0011  006D  0086  006D   0013  006E  009E  006E
# 65D8:  0020  006F  009E  006F   0042  006A  0084  0020
# 65E0:  0006  00A6  00AA  0002   0080  0040  002A  0086
# 65E8:  00A2  0004  0026  006A   0004  008A  0086  0024
# 65F0:  004A  00A8  0060  0024   0068  0046  000A  002C
# 65F8:  00A2  0048  0008  0060   0275  0093  0004  0160

jzintv_65C8_to_6600 = [
    0x005D, 0x005D, 0x005D, 0x0058, 0x0058, 0x0058, 0x0098, 0x006C,
    0x0011, 0x006D, 0x0086, 0x006D, 0x0013, 0x006E, 0x009E, 0x006E,
    0x0020, 0x006F, 0x009E, 0x006F, 0x0042, 0x006A, 0x0084, 0x0020,
    0x0006, 0x00A6, 0x00AA, 0x0002, 0x0080, 0x0040, 0x002A, 0x0086,
    0x00A2, 0x0004, 0x0026, 0x006A, 0x0004, 0x008A, 0x0086, 0x0024,
    0x004A, 0x00A8, 0x0060, 0x0024, 0x0068, 0x0046, 0x000A, 0x002C,
    0x00A2, 0x0048, 0x0008, 0x0060, 0x0275, 0x0093, 0x0004, 0x0160,
]

# Index into words: word $65C8 is at index 0
# Word $65CE is at index (0x65CE - 0x65C8)/2 = 3
# So jzintv_65C8_to_6600[3] = 0x0058 ... wait that doesn't match
# Let me recount: $65C8 = index 0, $65CA = 1, $65CC = 2, $65CE = 3
# But the dump shows 005D at $65C8 position. Let me align properly.

# Memory dump format: 65C8: aaaa bbbb cccc dddd eeee ffff gggg* hhhh
# * marks the address given
# aaaa = $65C8, bbbb = $65CA, cccc = $65CC, dddd = $65CE
# eeee = $65D0, ffff = $65D2, gggg = $65D4, hhhh = $65D6
# BUT the * is on gggg = $0098, which is at $65D4

# Re-reading: "65C8:  005D  005D  005D  0058   0058  0058  0098* 006C"
# The * is at position gggg (0x0098), marking address $65D4
# So: $65C8=005D, $65CA=005D, $65CC=005D, $65CE=0058
#     $65D0=0058, $65D2=0058, $65D4=0098*, $65D6=006C

jzintv_words = {
    0x65C8: 0x005D, 0x65CA: 0x005D, 0x65CC: 0x005D, 0x65CE: 0x0058,
    0x65D0: 0x0058, 0x65D2: 0x0058, 0x65D4: 0x0098, 0x65D6: 0x006C,
    0x65D8: 0x0011, 0x65DA: 0x006D, 0x65DC: 0x0086, 0x65DE: 0x006D,
    0x65E0: 0x0013, 0x65E2: 0x006E, 0x65E4: 0x009E, 0x65E6: 0x006E,
    0x65E8: 0x0020, 0x65EA: 0x006F, 0x65EC: 0x009E, 0x65EE: 0x006F,
    0x65F0: 0x0042, 0x65F2: 0x006A, 0x65F4: 0x0084, 0x65F6: 0x0020,
    0x65F8: 0x0006, 0x65FA: 0x00A6, 0x65FC: 0x00AA, 0x65FE: 0x0002,
    0x6600: 0x0080, 0x6602: 0x0040, 0x6604: 0x002A, 0x6606: 0x0086,
}

# ============================================================
# PART 1: Compare ROM file vs jzIntv runtime
# ============================================================
print("=" * 70)
print("PART 1: ROM FILE vs jzIntv RUNTIME at $65CE")
print("=" * 70)

for bank_name, addr_offset, file_base in [
    ("Bank 0 ($5000-$6FFF)", 0x5000, 0x0000),
    ("Bank 1 ($5000-$6FFF)", 0x5000, 0x2000),
]:
    matches = 0
    mismatches = 0
    print(f"\n--- {bank_name} (file offset {file_base:#06X}) ---")
    for addr in range(0x65C8, 0x6608, 2):
        if addr not in jzintv_words:
            continue
        jz_val = jzintv_words[addr]
        file_off = file_base + (addr - addr_offset)
        file_val = rw(file_off)
        match = "MATCH" if file_val == jz_val else "MISMATCH"
        if file_val == jz_val:
            matches += 1
        else:
            mismatches += 1
        print(f"  ${addr:04X}: jzintv=${jz_val:04X}  ROM=${file_val:04X}  [{match}]")
    print(f"  Results: {matches} matches, {mismatches} mismatches")

# ============================================================
# PART 2: SDBD pointer table decoding (properly)
# ============================================================
print("\n" + "=" * 70)
print("PART 2: SDBD POINTER TABLE DECODING")
print("=" * 70)
print("SDBD at byte address N reads: lo(word[N]) as low byte, lo(word[N+1]) as high byte")
print("The table base is $65CE; index i reads from byte $65CE+i")
print()

def sdbd_read(byte_addr):
    """Simulate SDBD read: reads lo bytes of consecutive words."""
    lo_word_addr = (byte_addr // 2) * 2  # word containing byte_addr
    lo_byte = jzintv_words.get(lo_word_addr, 0xFFFF) & 0xFF
    hi_byte = jzintv_words.get(lo_word_addr + 2, 0xFFFF) & 0xFF
    return (hi_byte << 8) | lo_byte

print("Full SDBD pointer table (16 entries, base=$65CE):")
print(f"{'Index':>5}  {'ByteAddr':>8}  {'Word[Lo]':>8}  {'Word[Hi]':>8}  {'Lo':>4}  {'Hi':>4}  {'Pointer':>8}  {'In ROM?'}")
print("-" * 80)

for idx in range(16):
    byte_addr = 0x65CE + idx
    lo_word_addr = (byte_addr // 2) * 2
    lo_word = jzintv_words.get(lo_word_addr, 0xFFFF)
    hi_word = jzintv_words.get(lo_word_addr + 2, 0xFFFF)
    lo = lo_word & 0xFF
    hi = hi_word & 0xFF
    ptr = (hi << 8) | lo
    in_rom = "Yes" if 0x5000 <= ptr <= 0x6FFF else ("EXEC" if 0x1000 <= ptr <= 0x1FFF else ("GRAM" if 0x3000 <= ptr <= 0x3FFF else "RAM/Other"))
    marker = " <-- R2=$6D86" if idx == 4 else ""
    print(f"  {idx:2d}   ${byte_addr:04X}     ${lo_word_addr:04X}=${lo_word:04X}  ${lo_word_addr+2:04X}=${hi_word:04X}   ${lo:02X}   ${hi:02X}   ${ptr:04X}      {in_rom}{marker}")

# ============================================================
# PART 3: Pointer destinations - compare ROM with jzIntv
# ============================================================
print("\n" + "=" * 70)
print("PART 3: POINTER DESTINATION DATA")
print("=" * 70)

# From dump_pointers_out.txt (jzIntv runtime):
# $6D86: 0061 0126 0061 0128 0061 0127 000A 0122 0061 0125 0061 0126 ...
# $136D: 0043 01A3 0343 0116 022E 0148 0343 0117 ...
# $6E9E: 0061 0126 0061 0128 0061 0127 000A 0122 ...

jzintv_6D86 = [0x0126, 0x0061, 0x0128, 0x0061, 0x0127, 0x000A, 0x0122, 0x0061]
jzintv_136D = [0x01A3, 0x0343, 0x0116, 0x022E, 0x0148, 0x0343, 0x0117, 0x0225]
jzintv_6E9E = [0x0126, 0x0061, 0x0128, 0x0061, 0x0127, 0x000A, 0x0122, 0x0061]

# Re-read from the actual dump more carefully:
# 6D80:  0061  0126  0061  0128   0061  0127  000A* 0122
# So $6D86 (* position) = 0122? No, let me re-read...
# The * marks the address given: $6D86. The data at starred position = $000A
# So $6D86 = 0x000A
# Wait: 6D80: 0061 0126 0061 0128 0061 0127 000A* 0122
# This is word addresses: $6D80, $6D82, $6D84, $6D86*, $6D88, $6D8A, $6D8C, $6D8E
# So $6D86 = 0x000A (starred position, word 3)

# Let me reparse properly
# 6D80:  [0]=0061  [1]=0126  [2]=0061  [3]=0128   [4]=0061  [5]=0127  [6]=000A* [7]=0122
# $6D80=0061, $6D82=0126, $6D84=0061, $6D86=0128, $6D88=0061, $6D8A=0127, $6D8C=000A*, $6D8E=0122
# Hmm, the * position in jzIntv debugger is the ADDRESS, not the value
# "000A*" means this word is at the address $6D8C (or wherever * is)
# Let me look at: 6D80:  0061  0126  0061  0128   0061  0127  000A* 0122
# jzintv format: ADDR: w0 w1 w2 w3 w4 w5 w6* w7  (8 words shown)
# Star on w6 means it's at $6D80 + 6*2 = $6D8C
# So w0=$6D80=0061, w1=$6D82=0126, w2=$6D84=0061, w3=$6D86=0128,
#    w4=$6D88=0061, w5=$6D8A=0127, w6=$6D8C=000A, w7=$6D8E=0122

# Actually I'm overcomplicating this. The * in jzintv output marks the requested address.
# "m 6D86 32" starts at $6D86. The * should be on the first shown value.
# But looking at the dump: "6D80:  0061  0126  0061  0128   0061  0127  000A* 0122"
# The dump starts BEFORE the requested address (6D80 is aligned to 8-word boundary)
# The * marks which word is $6D86, which is the 4th word in the line (index 3 from 0)
# Wait: $6D80 + 3*2 = $6D86. So w3 = $0128 is at $6D86.
# But the * is on $000A which is w6 = $6D80 + 6*2 = $6D8C
# That doesn't match!

# Actually, looking at other dumps:
# 1368:  0043  01A3  0343  0116   022E  0148* 0343  0117
# $1368 + 5*2 = $1372. Hmm. But "m 136D" was requested, so 
# $136D - $1368 = 5, which is a byte offset of 5, not word offset!
# This means jzIntv aligns to 8-word boundaries for display, and the * marks
# where the requested byte address falls within the displayed range.

# Wait, jzIntv memory display shows word addresses. The "m" command takes a 
# byte address in SDBD mode? No, "m" takes a word address normally.

# Actually, looking more carefully: "m 136D 32" - 136D is an odd address!
# CP-1610 addresses are 16-bit word addresses normally. $136D as a word address
# would be odd, which doesn't make sense.
# But as a BYTE address, $136D maps to... 

# I think jzIntv's "m" command uses word addresses. $136D is an odd value 
# that jzIntv rounds down to the nearest 8-word boundary for display.

# Let me just use the data as printed. The * in "0148*" at $1368 row means
# $136D is at that position. $1368 + offset_to_star*2 = ?
# $1368 is 8 words displayed. The star is on the 5th value (0-indexed: 4).
# $1368 + 4*2 = $1368 + 8 = $1370. That still doesn't give $136D!

# OK I think jzIntv displays with a mix of word and byte addressing in the "m" command.
# Let me just move forward with what we know from the step trace: R2=$6D86 is correct.

# Re-examining $6D86 data from the dump:
# We know $6D86 is the pointer. The dump at $6D86 has data starting around there.
# Let me just use the data as-is from the dump, aligning to $6D86 as the start.

jzintv_6D86_data = [0x0128, 0x0061, 0x0127, 0x000A, 0x0122, 0x0061, 0x0125, 0x0061]
jzintv_6E9E_data = [0x0128, 0x0061, 0x0127, 0x000A, 0x0122, 0x0061, 0x0125, 0x0061]

print("\nPointer $6D86 (tile index 4) - first 8 words at runtime:")
print("  jzIntv: " + " ".join(f"${w:04X}" for w in jzintv_6D86_data))
for bank_name, file_base in [("Bank 0", 0x0000), ("Bank 1", 0x2000)]:
    file_off = file_base + (0x6D86 - 0x5000)
    rom_data = [rw(file_off + i*2) for i in range(8)]
    matches = sum(1 for a, b in zip(jzintv_6D86_data, rom_data) if a == b)
    print(f"  {bank_name} (file ${file_off:X}): " + " ".join(f"${w:04X}" for w in rom_data) + f"  [{matches}/8 match]")

print("\nPointer $6E9E (tile index 8) - first 8 words at runtime:")
print("  jzIntv: " + " ".join(f"${w:04X}" for w in jzintv_6E9E_data))
for bank_name, file_base in [("Bank 0", 0x0000), ("Bank 1", 0x2000)]:
    file_off = file_base + (0x6E9E - 0x5000)
    rom_data = [rw(file_off + i*2) for i in range(8)]
    matches = sum(1 for a, b in zip(jzintv_6E9E_data, rom_data) if a == b)
    print(f"  {bank_name} (file ${file_off:X}): " + " ".join(f"${w:04X}" for w in rom_data) + f"  [{matches}/8 match]")

# ============================================================
# PART 4: Check if THIS is actually the tile/graphics data format
# ============================================================
print("\n" + "=" * 70)
print("PART 4: DATA FORMAT ANALYSIS at $6D86")
print("=" * 70)
print("The tile data at $6D86 appears to be run-length encoded or coordinate-based.")
print("Pattern: $0061 = 'a' (possibly GROM card 97='a'), $0126 = GROM card 294")
print("GROM card $61 (97) is... let me check: standard GROM includes alphanumeric")
print()
print("$0061 bits: BG=01 (blue), card=$61 (97='a')")
print("  GROM card 97 = lowercase 'a'")
print("  This makes sense: game uses GROM text cards for room rendering")
print("$0126 bits: BG=01 (blue), card=$26 (38)")
print("  GROM card 38 = ... need to check")
print()
print("The room data uses BACKTAB word format: [BG color:3][card:9][FG color:3][GRAM:1]")
print("  $0128 = 0000 0001 0010 1000 = BG=0, card=$128 (296)? Or BG=1, card=$28?")
print("  Actually: $0128 = BG=$01 (blue=1), card=$28 (40)")

print("\nDone.")
