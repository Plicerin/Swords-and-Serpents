#!/usr/bin/env python3
"""Analyze SDBD pointer table with byte-for-byte and word-for-word file mappings."""
import sys
sys.stdout.reconfigure(encoding='cp1252', errors='replace')

rom = open('Swords and Serpents.bin', 'rb').read()

print(f'ROM file size: {len(rom)} bytes = {hex(len(rom))}')
print()

# === Method 1: Word-for-word mapping (current) ===
# file_offset = (addr - 0x5000) * 2
# BE word = (file[off] << 8) | file[off+1]
def rw_be_word(addr):
    off = (addr - 0x5000) * 2
    return (rom[off] << 8) | rom[off + 1]

# LE word with same mapping
def rw_le_word(addr):
    off = (addr - 0x5000) * 2
    return rom[off] | (rom[off + 1] << 8)

# === Method 2: Byte-for-byte mapping ===
# file_offset = addr - 0x5000
# LE word = file[off] | (file[off+1] << 8) -- this is how CP-1610 memory works
def rw_le_byte(addr):
    off = addr - 0x5000
    return rom[off] | (rom[off + 1] << 8)

def rw_be_byte(addr):
    off = addr - 0x5000
    return (rom[off] << 8) | rom[off + 1]

# === Check known values from jzIntv ===
# From verify_mem2: $65C8 onward had known values
# Let's check what we can verify
print("=== VERIFICATION: Known jzIntv values at $65CE-$65D5 ===")
print("jzIntv confirmed: $65CE=$0098, $65CF=$006C, $65D0=$0011, $65D1=$006D")

for addr in range(0x65CE, 0x65D6):
    be_w = rw_be_word(addr)
    le_w = rw_le_word(addr)
    be_b = rw_be_byte(addr)
    le_b = rw_le_byte(addr)
    off_w = (addr - 0x5000) * 2
    off_b = addr - 0x5000
    print(f'  ${addr:04X}: raw_w[{off_w:04X}]={rom[off_w]:02X}{rom[off_w+1]:02X}  raw_b[{off_b:04X}]={rom[off_b]:02X}{rom[off_b+1]:02X}')
    print(f'           BE_w=${be_w:04X}  LE_w=${le_w:04X}  BE_b=${be_b:04X}  LE_b=${le_b:04X}')

# Known: $65CE should be $0098
print()
print("Expected at $65CE: $0098")
ce_be_w = rw_be_word(0x65CE)
ce_le_w = rw_le_word(0x65CE)
ce_be_b = rw_be_byte(0x65CE)
ce_le_b = rw_le_byte(0x65CE)
print(f"  BE_word=${ce_be_w:04X}  LE_word=${ce_le_w:04X}  BE_byte=${ce_be_b:04X}  LE_byte=${ce_le_b:04X}")

# Now: $65D2 should give R2=$6D86 after SDBD+MVI@
print()
print("=== THE KEY QUESTION: $65D2 -> $6D86 ===")
print(f"Raw bytes at $65D2 (word mapping off=0x{(0x65D2-0x5000)*2:04X}): {rom[(0x65D2-0x5000)*2]:02X} {rom[(0x65D2-0x5000)*2+1]:02X}")
print(f"Raw bytes at $65D2 (byte mapping off=0x{0x65D2-0x5000:04X}): {rom[0x65D2-0x5000]:02X} {rom[0x65D2-0x5000+1]:02X}")

# SDBD+MVI@ R4,R2 with R4=$65D2: reads 16-bit LE from byte addresses $65D2,$65D3
# In CP-1610 memory model, byte $65D2 is low, byte $65D3 is high
# If file maps byte-for-byte: file[$65D2-$5000] = byte at $65D2
d2_byte_low = rom[0x65D2 - 0x5000]
d2_byte_high = rom[0x65D2 - 0x5000 + 1]
sdbd_val_le = d2_byte_low | (d2_byte_high << 8)
print(f"SDBD LE from byte addresses $65D2,$65D3: {d2_byte_low:02X} | ({d2_byte_high:02X}<<8) = ${sdbd_val_le:04X}")

# If file maps word-for-word: file[($65D2-$5000)*2] and file[($65D2-$5000)*2+1]
# In CP-1610, word at $65D2 = BE of these two bytes
# But SDBD reads byte-level, so: same bytes?
d2_word_off = (0x65D2 - 0x5000) * 2
d2w_low = rom[d2_word_off]
d2w_high = rom[d2_word_off + 1]
print(f"SDBD LE from word-mapped bytes $65D2,$65D3: {d2w_low:02X} | ({d2w_high:02X}<<8) = ${d2w_low | (d2w_high << 8):04X}")

# === Possible base addresses ===
print()
print("=== TRYING DIFFERENT BASE+POINTER COMBINATIONS ===")
target = 0x6D86
for base_name, base in [("$65DC (G_02F4)", 0x65DC), ("$65CE (table start)", 0x65CE), 
                          ("$5000 (ROM base)", 0x5000), ("$6000", 0x6000),
                          ("$6D00", 0x6D00), ("$6800", 0x6800)]:
    needed = target - base
    if 0 <= needed < 0x2000:
        print(f"  Base {base_name}: ptr=${needed:04X} -> dest=${target:04X}")
    
# Maybe the pointer IS the full address, just stored differently
print()
print("=== ALTERNATIVE: Maybe the byte at $65D2 IS $6D and $65D3 is $86 ===")
# In byte-for-byte mapping, what if the raw byte at $65D2 is $86 and $65D3 is $6D?
# That would give SDBD LE = $86 | ($6D << 8) = $6D86
# Let's check what bytes are actually there
off_b = 0x65D2 - 0x5000
print(f"  Byte at file[{off_b:04X}] = {rom[off_b]:02X}")
print(f"  Byte at file[{off_b+1:04X}] = {rom[off_b+1]:02X}")
# But we already know these are 00 and 86...

# Maybe the SDBD table is a DIFFERENT table entirely
print()
print("=== SEARCHING ENTIRE ROM FOR $6D86 bytes ===")
# Search for the byte sequence 86 6D (LE) or 6D 86 (BE)
for i in range(len(rom) - 1):
    le_val = rom[i] | (rom[i+1] << 8)
    if le_val == 0x6D86:
        addr = i + 0x5000
        print(f"  Found LE $6D86 at file offset {i:04X} (byte addr ${addr:04X})")

# Also search for $6D86 as a 16-bit value in our standard mapping
for addr in range(0x5000, 0x7000):
    if rw_be_word(addr) == 0x6D86:
        print(f"  Found BE_word $6D86 at ROM addr ${addr:04X}")
    if rw_le_word(addr) == 0x6D86:
        print(f"  Found LE_word $6D86 at ROM addr ${addr:04X}")

# === Dump tile stream at $6D86 to verify it's plausible ===
print()
print("=== TILE STREAM AT $6D86 (if it's the actual tile data) ===")
for row in range(4):
    line = []
    for col in range(16):
        addr = 0x6D86 + row * 16 + col
        if addr < 0x7000:
            val = rw_be_word(addr)
            line.append(f"${val:04X}")
    print(f"  Row {row}: {' '.join(line)}")

# === Dump tile stream at $6674 (current decoder destination) for comparison ===
print()
print("=== TILE STREAM AT $6674 (current decoder destination) ===")
for row in range(4):
    line = []
    for col in range(16):
        addr = 0x6674 + row * 16 + col
        if addr < 0x7000:
            val = rw_be_word(addr)
            line.append(f"${val:04X}")
    print(f"  Row {row}: {' '.join(line)}")
