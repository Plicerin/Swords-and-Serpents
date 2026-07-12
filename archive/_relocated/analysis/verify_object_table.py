"""Verify the object table at ROM $655E by reading raw bytes and cross-referencing 
with the actual BACKTAB capture data."""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

print(f"ROM size: {len(rom)} bytes")
print(f"ROM word count: {len(rom)//2}")
print()

# CRITICAL: CP-1610 is big-endian. ROM is stored as 10-bit words in 16-bit halves.
# The ROM starts at $5000. To read word at address A: offset = (A - 0x5000) * 2
# High byte at offset, low byte at offset+1

def rw(addr):
    """Read 16-bit word from ROM at CP-1610 address"""
    offset = (addr - 0x5000) * 2
    if offset + 1 < len(rom):
        return (rom[offset] << 8) | rom[offset + 1]
    elif offset < len(rom):
        return rom[offset] << 8
    return 0

def rb(addr):
    """Read byte from ROM at CP-1610 address (high byte of word)"""
    offset = (addr - 0x5000) * 2
    if offset < len(rom):
        return rom[offset]
    return 0

# Verify known values from disassembly
print("=== ROM VERIFICATION ===")
print(f"  $5017 (DIS=$0003): ${rw(0x5017):04X}")
print(f"  $5018 (SDBD=$0001): ${rw(0x5018):04X}")
print(f"  $5019 (MVII #$538E,R0 = $02B8 $008E $0053): raw bytes at offset {((0x5019-0x5000)*2):04X}")
off = (0x5019-0x5000)*2
print(f"    bytes: ({rom[off]:02X} {rom[off+1]:02X} {rom[off+2]:02X} {rom[off+3]:02X} {rom[off+4]:02X} {rom[off+5]:02X})")
print()

# Object BACKTAB table at $655E-$659D (32 entries, 2 bytes each = 16-bit words)
print("=== OBJECT BACKTAB TABLE ($655E-$659D) ===")
print(f"  Offset in ROM: ${((0x655E-0x5000)*2):04X}")
print("  Type  ROM-addr  RAW-bytes    Word     Card   FG-Color  BG-Color  Mode")
print("  " + "-" * 75)

all_obj_backtab = {}
for t in range(32):
    addr = 0x655E + t * 2
    offset = (addr - 0x5000) * 2
    b0 = rom[offset] if offset < len(rom) else 0
    b1 = rom[offset+1] if offset+1 < len(rom) else 0
    word = (b0 << 8) | b1
    
    # Parse BACKTAB format (16-bit word)
    # Bits 0-2: background color (color stack mode) or lower 3 bits  
    # Bit 3: unused in colored squares
    # Bits 4-5: upper 2 bits of card number
    # Bits 6-7: foreground color lower 2 bits
    # Bit 8: GROM/GRAM select
    # Bits 9-11: foreground color upper 3 bits
    # Bit 12: colored squares mode (0) vs color stack mode (1)
    # Bit 13: pastel
    # Bit 14: unused
    # Bit 15: GRAM bit (for GRAM cards, bit 15 is used)
    
    card = word & 0x01F8  # bits 3-8 (well, card is split across bits)
    # Card number is: (word >> 3) & 0x3F | ((word >> 8) & 0xC0) ... hmm, let me just use direct extraction
    
    # Actually, in Colored Squares mode (bit 12=0):
    # Bits 0-2: foreground color lower 3 bits
    # Bits 3-8: card number (6 bits, 0-63)
    # Bits 9-11: foreground color upper 3 bits (so FG color = bits 9-11 + bits 0-2 = 0-63)
    # Bit 12: 0 = colored squares, 1 = color stack
    # Bits 13-14: background color (in colored squares mode, 4 colors)
    # Bit 15: GRAM select
    
    mode = (word >> 12) & 0x1
    card_num = (word >> 3) & 0x3F  # bits 3-8 = 6 bits
    fg_color = ((word >> 9) & 0x7) << 3 | (word & 0x7)  # upper 3 bits + lower 3 bits
    bg_color = (word >> 13) & 0x3
    gram = (word >> 15) & 0x1
    
    all_obj_backtab[t] = word
    
    mode_str = "CS" if mode == 0 else "CStack"
    gram_str = "GRAM" if gram else "GROM"
    
    print(f"  {t:3d}   ${addr:04X}    ({b0:02X} {b1:02X})     ${word:04X}    ${card_num:02X}    {fg_color:2d}        {bg_color}        {mode_str}")
    
print()

# Type index table at $6580-$659F (16 entries, resolves room object to type)
print("=== TYPE INDEX TABLE ($6580-$659F) ===")
for i in range(16):
    addr = 0x6580 + i * 2
    word = rw(addr)
    print(f"  idx {i:2d} (${addr:04X}): ${word:04X}  ({word & 0x1F:2d})")

print()

# NOW: the actual BACKTAB from the JZINTV capture
print("=== ACTUAL BACKTAB (from JZINTV capture) ===")
actual_btab = [
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x179B, 0x17BB, 0x177B, 0x1793, 0x1723, 0x179B, 0x1603, 0x1633, 0x1603, 0x179B, 0x172B, 0x1793, 0x1783, 0x172B, 0x1773, 0x17A3, 0x179B, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1EBB, 0x1603, 0x174B, 0x176B, 0x170B, 0x173B, 0x174B, 0x171B, 0x1603,
    0x168B, 0x16CB, 0x16C3, 0x1693, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x172B, 0x1773, 0x17A3, 0x172B, 0x1793, 0x1603, 0x173B, 0x170B, 0x176B, 0x172B, 0x1603, 0x1643, 0x168B, 0x1663, 0x1693, 0x1663, 0x169B, 0x164B, 0x1603,
]


# Find all unique actual BACKTAB values
unique_actual = sorted(set(actual_btab))
print(f"\nUnique BACKTAB values in actual capture: {len(unique_actual)}")
print(f"  Wall tile ($1603) cells: {actual_btab.count(0x1603)}")
print(f"  Non-wall cells: {len(actual_btab) - actual_btab.count(0x1603)}")
print()

# Cross-reference: for each unique BACKTAB value, check if it exists in object table
print("=== CROSS-REFERENCE: Actual BACKTAB vs Object Table ===")
print(f"{'BACKTAB':>6}  {'Card':>4}  {'FG':>3}  {'In Object Table?':>20}  {'Matching Type(s)':>20}")
print("-" * 70)

for btab in unique_actual:
    card = (btab >> 3) & 0x3F
    fg = ((btab >> 9) & 0x7) << 3 | (btab & 0x7)
    
    match_types = []
    for t in range(32):
        if all_obj_backtab[t] == btab:
            match_types.append(str(t))
    
    match_str = ", ".join(match_types) if match_types else "---"
    found = "YES" if match_types else "NO"
    print(f"  ${btab:04X}  ${card:02X}   {fg:2d}   {found:>20}  {match_str:>20}")

print()

# Also check: do any object table values have the same CARD number?
print("=== SAME-CARD MATCHES (object table has same card, different color) ===")
for btab in unique_actual:
    if btab == 0x1603:
        continue
    card = (btab >> 3) & 0x3F
    fg = ((btab >> 9) & 0x7) << 3 | (btab & 0x7)
    
    match_types = []
    for t in range(32):
        o_card = (all_obj_backtab[t] >> 3) & 0x3F
        if o_card == card and all_obj_backtab[t] != btab:
            match_types.append(f"type {t}: ${all_obj_backtab[t]:04X}")
    
    if match_types:
        print(f"  ${btab:04X} (card=${card:02X}, FG={fg}): same card as {', '.join(match_types)}")

print()
# Show all object table entries that share card numbers with actual BACKTAB
print("=== ALL OBJECT TABLE ENTRIES WITH SAME CARD AS ACTUAL BACKTAB ===")
actual_cards = set()
for btab in unique_actual:
    if btab != 0x1603:
        actual_cards.add((btab >> 3) & 0x3F)

for t in range(32):
    o_card = (all_obj_backtab[t] >> 3) & 0x3F
    o_fg = ((all_obj_backtab[t] >> 9) & 0x7) << 3 | (all_obj_backtab[t] & 0x7)
    if o_card in actual_cards:
        print(f"  Type {t:2d}: ${all_obj_backtab[t]:04X} (card=${o_card:02X}, FG={o_fg})")
