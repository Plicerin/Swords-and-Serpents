#!/usr/bin/env python3
"""
Corrected L_5EC7 Simulation
===========================
Implements the EXACT CP1610 instruction sequence from disassembly with
proper SDBD semantics, XOR target, and card table handling.

Key corrections vs. decode_full_pipeline.py:
  1. XOR@ R3 reads the NEXT attr word (R3 was auto-incremented by MVI@)
  2. SDBD+ANDI does byte-wise AND (mask per byte)
  3. Card table loaded into scratchpad 8-bit RAM at $00A0
"""

import sys
sys.stdout.reconfigure(encoding='ascii', errors='replace')

rom = open('Swords and Serpents.bin', 'rb').read()

def rw(addr):
    """Read 16-bit big-endian word at CP1610 address."""
    if addr < 0x5000 or addr > 0x6FFF:
        return 0
    off = (addr - 0x5000) * 2
    if off + 1 < len(rom):
        return (rom[off] << 8) | rom[off + 1]
    return 0

def rb(addr):
    """Read low byte of 16-bit word at CP1610 address."""
    off = (addr - 0x5000) * 2
    if off + 1 < len(rom):
        return rom[off + 1]
    return 0

# ====================================================================
# ACTUAL ROOM 0 BACKTAB
# ====================================================================
actual_raw = """
0200: 1603 1603 1603 1603 1603 1603 081B 1603
0208: 1603 1603 1603 1603 1603 1E13 1603 1603
0210: 1603 1603 1603 1603 1603 1603 1603 1603
0218: 1603 1603 081B 1603 1603 1603 1603 1603
0220: 1603 081B 1603 1603 1603 1603 1603 1603
0228: 081B 1603 02BF 029F 025F 02B7 0207 02BF
0230: 0327 0317 0327 02BF 020F 02B7 02A7 020F
0238: 0257 0287 02BF 0823 081B 1603 1603 1603
0240: 1603 1603 081B 1603 1603 1603 1603 1603
0248: 1603 081B 1603 1603 1603 1603 1603 1603
0250: 081B 1603 1603 1603 1603 1EBB 0327 026F
0258: 024F 022F 021F 026F 023F 0327 03AF 03EF
0260: 03E7 03B7 1603 1603 081B 1603 1603 1603
0268: 1603 1603 081B 1603 1603 1603 1603 1603
0270: 1603 081B 1603 1603 1603 1603 1603 1603
0278: 081B 1603 1603 1603 1603 1603 081B 1603
0280: 1603 1603 0E60 1603 1603 081B 1603 1603
0288: 1603 1603 1E5B 1603 081B 1603 1603 1603
0290: 1603 1603 081B 1603 1603 1603 1603 1603
0298: 1603 1E40 1603 1603 1603 1603 1603 1603
02A0: 1E40 1603 1603 1603 1603 1603 081B 1603
02A8: 1603 1603 1603 1603 1603 1603 1603 1603
02B0: 1603 1603 1603 1603 1603 1603 020F 0257
02B8: 0287 020F 02B7 0327 021F 022F 024F 020F
02C0: 0327 0367 03AF 0347 03B7 0347 03BF 036F
02C8: 0823 1E38 1603 1603 1603 1E02 082B 0823
02D0: 0823 0823 0823 0823 0823 081B 1603 1603
02D8: 0823 0823 0823 0823 1603 1603 1603 1603
02E0: 1603 1603 081B 1603 1603 1603 1603 1603
02E8: 1603 081B 1603 1603 1603 1603 1603 1603
"""

actual_backtab = {}
for line in actual_raw.strip().split('\n'):
    parts = line.split()
    if not parts or not parts[0].endswith(':'): continue
    addr = int(parts[0].rstrip(':'), 16)
    for i, h in enumerate(parts[1:]):
        if len(h) == 4:
            actual_backtab[addr + i] = int(h, 16)

unique_bt = sorted(set(actual_backtab.values()))
print(f"Actual BACKTAB: {len(actual_backtab)} tiles, {len(unique_bt)} distinct values")
print(f"Distinct: {[f'${v:04X}' for v in unique_bt]}")
print()

# ====================================================================
# CORRECTED L_5EC7 SIMULATION
# ====================================================================

def l5ec7_corrected(attr_table, card_bytes, group):
    """
    EXACT L_5EC7 algorithm from CP1610 disassembly.
    
    Input state:
      R1 = tile_descriptor (passed from caller, group = R1 >> 5)
      G_02F5 = attr_table base ($65B7)
      R5 = card_table base ($00A0, from SDBD+MVII #$65A0)
    
    Instructions:
      5EC9: MVI  G_02F5, R3          ; R3 = attr_base
      5ECB: SDBD
      5ECC: MVII #$65A0, R5          ; R5 = $00A0 (byte from SDBD)
      5ECF: SLR  R1, 2
      5ED0: SLR  R1, 2
      5ED1: SLR  R1, 1               ; R1 = group = tile >> 5
      5ED2: ADDR R1, R3              ; R3 = attr_base + group
      5ED3: ADDR R1, R5              ; R5 = card_base + group
      5ED4: MVI@ R3, R1              ; R1 = attr[group], R3++
      5ED5: SLR  R1, 2               ; R1 >>= 2
      5ED6: SWAP R1, 1               ; byte swap
      5ED7: XOR@ R3, R1              ; R1 ^= attr[group+1] (R3 auto-incremented)
      5ED8: SDBD
      5ED9: ANDI #$3607, R1          ; Byte-wise AND with $36, $07
      5EDC: MVI@ R5, R3              ; R3 = card[group] (word read from scratchpad)
      5EDD: SLL  R3, 2               ; R3 <<= 2
      5EDE: SLL  R3, 1               ; R3 <<= 1 (total <<3)
      5EDF: XORR R3, R1              ; R1 ^= R3
    Returns: R1 (BACKTAB word)
    """
    # attr_table is indexed by group (word address)
    a0 = attr_table[group]          # MVI@ R3: read attr[group], R3 becomes group+1
    a1 = attr_table[group + 1] if group + 1 < len(attr_table) else 0  # XOR@ R3: read attr[group+1]
    
    # Process attr
    r1 = a0 >> 2                    # SLR R1, 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)  # SWAP R1, 1
    
    r1 ^= a1                        # XOR@ R3, R1
    
    # SDBD + ANDI #$3607: byte-wise AND
    # SDBD makes ANDI operate on bytes: lo & $07, hi & $36
    r1_lo = (r1 & 0xFF) & 0x07
    r1_hi = ((r1 >> 8) & 0xFF) & 0x36
    r1 = (r1_hi << 8) | r1_lo
    
    # Card: word read from scratchpad at $00A0 + group
    # In 8-bit RAM, a word read concatenates two consecutive bytes
    # card_word = bytes[group*2] | (bytes[group*2+1] << 8)
    card_word = card_bytes[group * 2] | (card_bytes[group * 2 + 1] << 8)
    
    r3 = (card_word << 3) & 0xFFFF   # SLL R3, 2; SLL R3, 1
    
    backtab = r1 ^ r3
    
    return backtab & 0xFFFF


def decode_bt(bt):
    """Decode BACKTAB word."""
    card = bt & 0x7FF
    is_gram = bool(bt & 0x0800)
    fg = ((bt >> 13) & 0x6) | ((bt >> 12) & 0x1)
    cs = (bt >> 13) & 1
    return f"${bt:04X} card={card:3d} {'GRAM' if is_gram else 'GROM'} fg={fg} cs={cs}"


# ====================================================================
# READ ROM ATTR TABLE
# ====================================================================
print("=" * 75)
print("ROM ATTR TABLE at $65B7 (word reads, 1-word stride)")
print("=" * 75)

attr_table = []
for i in range(32):
    w = rw(0x65B7 + i)
    attr_table.append(w)

for g in range(8):
    print(f"  group {g}: attr[{g}]=${attr_table[g]:04X}  attr[{g+1}]=${attr_table[g+1]:04X}")

print()

# ====================================================================
# TEST 1: ROM card table as-is (assuming loaded to scratchpad verbatim)
# ====================================================================
print("=" * 75)
print("TEST 1: Card table loaded from ROM $65A0 to scratchpad $00A0")
print("  Each ROM word copied to 2 consecutive bytes in 8-bit RAM")
print("=" * 75)

# Simulate ROM card table copied to scratchpad 8-bit RAM
rom_card_bytes = []
for i in range(8):
    w = rw(0x65A0 + i)  # Read words at $65A0, $65A1, ...
    rom_card_bytes.append(w & 0xFF)    # Low byte
    rom_card_bytes.append((w >> 8) & 0xFF)  # High byte

print(f"  Scratchpad bytes at $00A0: ", end="")
for i, b in enumerate(rom_card_bytes):
    print(f"${b:02X}", end=" ")
print()
print()

matches = 0
total = 0
outputs = {}
for g in range(8):
    bt = l5ec7_corrected(attr_table, rom_card_bytes, g)
    outputs[g] = bt
    in_actual = "✓" if bt in unique_bt else "✗"
    if bt in unique_bt:
        matches += 1
    print(f"  group {g}: {decode_bt(bt)}  {in_actual}")
    total += 1

print(f"\n  Matches: {matches}/{total}")
print()

# ====================================================================
# REVERSE ENGINEER: What card bytes would produce each BACKTAB value?
# ====================================================================
print("=" * 75)
print("REVERSE-ENGINEER: Find card bytes that produce each BACKTAB value")
print("=" * 75)

# For each group, find which BACKTAB values can be produced and with what card
for g in range(8):
    processed_attr = l5ec7_corrected(attr_table, [0]*16, g)  # card=0 gives just attr portion
    
    matching = []
    for bt_val in unique_bt:
        # bt_val = processed_attr ^ (card_word << 3)
        needed = bt_val ^ processed_attr
        # card_word = needed >> 3, but need needed to be cleanly divisible
        if (needed & 0x7) == 0:
            card_word = needed >> 3
            if 0 <= card_word <= 0xFFFF:
                card_lo = card_word & 0xFF
                card_hi = (card_word >> 8) & 0xFF
                matching.append((bt_val, card_word, card_lo, card_hi))
    
    if matching:
        print(f"\n  Group {g}: processed_attr={decode_bt(processed_attr)}")
        print(f"    Can produce {len(matching)} BACKTAB values:")
        for bt, cw, clo, chi in matching[:25]:
            marker = " ← WALL" if bt == 0x1603 else " ← DOOR" if bt in (0x081B, 0x0823, 0x082B) else ""
            floor = " ← FLOOR" if (bt >> 10) & 7 == 0 else ""
            print(f"    ${bt:04X} needs card_word=${cw:04X} (bytes lo=${clo:02X} hi={chi:02X}){marker}{floor}")

print()

# ====================================================================
# FIND: What scratchpad bytes would maximize matches?
# ====================================================================
print("=" * 75)
print("BRUTE FORCE: Find optimal scratchpad card bytes (8 groups × 2 bytes)")
print("=" * 75)

# For each group, find the card_word that produces the most unique BACKTAB values
# Then check if a consistent set of bytes works for all groups

# Strategy: scan card_word for groups that appear most in actual BACKTAB
for g in range(8):
    processed_attr = l5ec7_corrected(attr_table, [0]*16, g)
    
    # Count how many actual tiles each card_word could produce
    best_cards = []
    for cw in range(0, 0x10000):  # reasonable range
        bt = (processed_attr ^ (cw << 3)) & 0xFFFF
        if bt in unique_bt:
            count = sum(1 for v in actual_backtab.values() if v == bt)
            best_cards.append((cw, bt, count, (cw & 0xFF), ((cw >> 8) & 0xFF)))
    
    best_cards.sort(key=lambda x: x[2], reverse=True)
    if best_cards:
        print(f"\n  Group {g}: processed_attr=${processed_attr:04X}")
        for cw, bt, count, clo, chi in best_cards[:8]:
            label = "WALL" if bt == 0x1603 else "DOOR" if bt in (0x081B, 0x0823, 0x082B) else ""
            print(f"    card_word=${cw:04X} (${clo:02X},${chi:02X}) → ${bt:04X} ({count} tiles) {label}")

print()

# ====================================================================
# DEDUCTION: The card table must vary per room
# ====================================================================
print("=" * 75)
print("KEY INSIGHT: Card values deduced from first 8 groups")
print("=" * 75)

# For group 0 (wall): processed_attr = $1603. To get $1603, card_word must be 0.
# For group 3 (door): processed_attr = $0003. To get $081B, card_word must be $0103.
# For group 4 (door): processed_attr = $0003. To get $0823, card_word must be $0104.
# For group 5 (door): processed_attr = $0003. To get $082B, card_word must be $0105.

# So the card table bytes should be:
# Group 0: card_word=$0000 → bytes (0x00, 0x00)
# Group 1: card_word=$???? → unknowns
# Group 2: card_word=$???? → unknowns
# Group 3: card_word=$0103 → bytes (0x03, 0x01)
# Group 4: card_word=$0104 → bytes (0x04, 0x01)
# Group 5: card_word=$0105 → bytes (0x05, 0x01)

# For groups 0-2, the processed_attr is $1603 (wall), so card_word must be 0
# But this means all groups 0-2 produce the SAME wall tile.

# For the floor groups (6,7), processed_attr varies, and we can derive from BACKTAB

print("\n  Group 0: needs card_word=$0000 → $(00,00)")
print("  Group 1: needs card_word=$0000 → $(00,00)")  
print("  Group 2: needs card_word=$0000 → $(00,00)")
print("  Group 3: needs card_word=$0103 → $(03,01)")
print("  Group 4: needs card_word=$0104 → $(04,01)")
print("  Group 5: needs card_word=$0105 → $(05,01)")

# Groups 6-7: processed_attr for group 7
g6 = l5ec7_corrected(attr_table, [0]*16, 6)
g7 = l5ec7_corrected(attr_table, [0]*16, 7)
print(f"\n  Group 6: processed_attr=${g6:04X}")
print(f"  Group 7: processed_attr=${g7:04X}")

print()
print("CONCLUSION: ROM card table at $65A0 ($0100, $0101, ...) gets MODIFIED")
print("  at runtime. Groups 0-2 have card=0 (walls), groups 3-5 have card=$01xx (doors).")
print("  Need to find where this substitution happens, or capture actual scratchpad.")
