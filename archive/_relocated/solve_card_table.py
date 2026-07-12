#!/usr/bin/env python3
"""Empirically solve the L_5EC7 card table by reverse-engineering from known BACKTAB words."""
import sys
sys.stdout.reconfigure(encoding='cp1252', errors='replace')

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

def rw_be(addr):
    off = (addr - 0x5000) * 2
    if off + 1 >= len(rom):
        return 0
    return (rom[off] << 8) | rom[off + 1]

# Read attr table
attr = [rw_be(0x65B7 + i) for i in range(25)]
card_rom = [rw_be(0x65A0 + i) for i in range(23)]

# Known BACKTAB words from room 0 (render_room_0_out.txt)
KNOWN_BT = {
    0x1603, 0x081B, 0x1E13, 0x020F, 0x02B7, 0x02A7, 0x0257, 0x0287,
    0x02BF, 0x029F, 0x025F, 0x0207, 0x0327, 0x0317, 0x1EBB, 0x026F,
    0x024F, 0x022F, 0x021F, 0x023F, 0x03AF, 0x03EF, 0x03E7, 0x03B7,
    0x1E5B, 0x1E40, 0x0E60, 0x0823, 0x1E38, 0x1E02, 0x082B, 0x0367,
    0x0347, 0x036F, 0x03BF,
}

print("=== ATTR TABLE (ROM BE) ===")
for i in range(25):
    print(f"  attr[{i:2d}] @${0x65B7+i:04X}: ${attr[i]:04X}")

print("\n=== CARD TABLE (ROM BE) ===")
for i in range(23):
    print(f"  card[{i:2d}] @${0x65A0+i:04X}: ${card_rom[i]:04X} (<<3=${(card_rom[i]<<3)&0xFFFF:04X})")

# Compute L_5EC7 intermediate for each tile group
print("\n=== L_5EC7 ATTR INTERMEDIATE (before card XOR) ===")
intermediate = []
for idx in range(23):
    attr0 = attr[idx]
    attr1 = attr[idx + 1]
    r1 = attr0 >> 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)  # SWAP
    r1 ^= attr1
    r1 &= 0x3607
    intermediate.append(r1)
    print(f"  group {idx:2d}: attr0=${attr0:04X} attr1=${attr1:04X} -> ${r1:04X}", end="")
    if r1 in KNOWN_BT:
        print("  MATCH! (in known BT set)")
    else:
        # Decode
        card_n = r1 & 0x7FF
        gram = "GRAM" if r1 & 0x0800 else "GROM"
        fg = ((r1 >> 13) & 0x6) | ((r1 >> 12) & 0x1)
        cs = (r1 >> 13) & 1
        print(f"  (card={card_n} {gram} FG={fg} CS={cs})")

# For each tile group, find which known BACKTAB words COULD be produced
# if we used different card table values
print("\n=== SOLVING FOR CARD TABLE: what value would produce each BACKTAB word? ===")
for idx in range(23):
    im = intermediate[idx]
    print(f"\n  Group {idx}: intermediate=${im:04X}")
    
    # Find card values that would produce known BACKTAB words
    # card_val = (target ^ intermediate) >> 3
    for target in sorted(KNOWN_BT):
        needed_card = (target ^ im) >> 3
        # The card value is shifted by 3 and XORed, so we need:
        # (card << 3) = target ^ im
        xor_val = target ^ im
        if xor_val & 0x7 == 0:  # bottom 3 bits must be 0 (card is shifted left 3)
            card_val = xor_val >> 3
            print(f"    target=${target:04X} -> card=${card_val:04X} (decimal {card_val})", end="")
            if card_val == card_rom[idx]:
                print("  *** ROM MATCH! ***")
            else:
                print()

# Also: what if the ROM card table values are byte-swapped or otherwise transformed?
print("\n=== TRANSFORMATION ANALYSIS ===")
print("Testing if card_rom values are byte-swapped, or split into nibbles...")
for idx in range(5):
    cr = card_rom[idx]
    swapped = ((cr & 0xFF) << 8) | ((cr >> 8) & 0xFF)
    print(f"  card[{idx}]: ROM=${cr:04X}, byte-swapped=${swapped:04X}")

# Test: what if the card table is NOT at $65A0 but at a different address?
# Check ROM for 0-values in the card table area
print("\n=== Alternative: checking if card table is zero at runtime ===")
print("(ROM is read-only at $5000-$6FFF, so values are fixed)")
print("Testing L_5EC7 with card=0 for all groups:")
for idx in range(5):
    im = intermediate[idx]
    print(f"  group {idx}: intermediate=${im:04X} (no card XOR)", end="")
    if im in KNOWN_BT:
        print("  MATCH!")
    else:
        print()

# The key insight: $1603 is the floor tile. Let's see which groups have
# intermediate=$1603 (match without card XOR)
print("\n=== GROUPS WITH INTERMEDIATE IN KNOWN BT SET ===")
matching_groups = []
for idx in range(23):
    if intermediate[idx] in KNOWN_BT:
        matching_groups.append(idx)
        print(f"  Group {idx}: intermediate=${intermediate[idx]:04X}")
print(f"  Total: {len(matching_groups)}/{len(intermediate)} groups")

# Test the full L_5EC7 with ROM data
print("\n=== FULL L_5EC7 SIMULATION (with ROM card table) ===")
matches = 0
for idx in range(23):
    im = intermediate[idx]
    card_shifted = (card_rom[idx] << 3) & 0xFFFF
    result = im ^ card_shifted
    known = "MATCH!" if result in KNOWN_BT else ""
    if result in KNOWN_BT:
        matches += 1
    print(f"  group {idx:2d}: im=${im:04X} ^ card<<3=${card_shifted:04X} = ${result:04X}  {known}")
print(f"  Matches: {matches}/23")

# Most common BACKTAB word is $1603 (floor). Let's find which groups 
# produce $1603 and verify they should
print("\n=== $1603 ANALYSIS ===")
for idx in range(23):
    if intermediate[idx] == 0x1603 or (intermediate[idx] ^ (card_rom[idx] << 3)) == 0x1603:
        print(f"  Group {idx}: im=${intermediate[idx]:04X}, card=${card_rom[idx]:04X}, card<<3=${(card_rom[idx]<<3)&0xFFFF:04X}")
