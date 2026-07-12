#!/usr/bin/env python3
"""
Focused trace: L_5E48 tile stream decoding for room 0, row 0.
Tests the linked-list walk against actual BACKTAB.
"""

import sys
sys.stdout.reconfigure(encoding='ascii', errors='replace')

rom = open('Swords and Serpents.bin', 'rb').read()

def rw(addr):
    off = (addr - 0x5000) * 2
    if off < 0 or off + 1 >= len(rom): return 0
    return (rom[off] << 8) | rom[off + 1]

def rb(addr):
    off = (addr - 0x5000) * 2
    if off < 0 or off + 1 >= len(rom): return 0
    return rom[off + 1]

# ============================================================
# Actual BACKTAB row 0 (from JZINTV capture)
# ============================================================
actual_row0 = [
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1E13, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603
]

# ============================================================
# Simulate L_5E48 for room 0, row 0 (G_0176=26, G_0175=2, G_02F4=$65DC)
# ============================================================

print("=== L_5E48 TRACE: Room 0, Row 0 ===")
print(f"G_0176=26 ($1A), G_0175=2, G_02F4=$65DC")

R0_row = 26   # G_0176
R2_pos = 2    # G_0175
G_02F4 = 0x65DC  # value at SYSRAM $02F4

# Step 1: ANDI #$0030, R0; SLR R0, 2; SLR R0, 1
R0 = R0_row
R0 = ((R0 & 0x30) >> 2) >> 1  # = (0x10 >> 2) >> 1 = 4 >> 1 = 2
print(f"Step 1: (R0 & $30) >> 3 = {R0}")

# Step 2: ADD G_02F4, R0 → R0 += mem[G_02F4_addr]
# G_02F4_addr = $02F4, mem[$02F4] = $65DC
R0 += G_02F4  # R0 = $65DC + 2 = $65DE
print(f"Step 2: R0 += G_02F4 → R0 = ${R0:04X}")

# Step 3: ANDI #$0060, R2; SLR x3
R2 = R2_pos
R2 = ((R2 & 0x60) >> 2) >> 2 >> 1  # = (0 & 0x60) >> 5 = 0
print(f"Step 3: R2 = (pos & $60) >> 5 = {R2}")

# Step 4: MOVR R2, R3; SLR R3, 1; ADDR R0, R3
R3 = R2 >> 1  # 0
R3 = R0 + R3  # $65DE
print(f"Step 4: R3 = R0 + (R2>>1) = ${R3:04X}")

# Step 5: MVI@ R3, R0 → R0 = rom[R3], R3++
word_at = rw(R3)
print(f"Step 5: MVI@ ${R3:04X} → R0 = ${word_at:04X}")

# Step 6: RRC R2, 1; BNC L_5E60
# R2=0, RRC with no carry → BNC to L_5E60
print(f"Step 6: RRC R2(0),1 → no carry → skip SLR")

# Step 7: ANDI #$000F, R0 → R0 = nibble (0-15)
R0_nibble = word_at & 0x0F
print(f"Step 7: R0 &= $0F → {R0_nibble}")

# Step 8: MVII #$65CE, R4; ADDR R0, R4; SDBD; MVI@ R4, R2
R4 = 0x65CE + R0_nibble
link_byte = rb(R4)  # SDBD → byte read
print(f"Step 8: $65CE+{R0_nibble} = ${R4:04X}, SDBD MVI@ → R2 = ${link_byte:02X} (scratchpad addr)")
R2 = link_byte  # This is a scratchpad address ($00-$FF)

# Step 9: PULR R0 (original); ANDI #$000F, R0
R0_orig = R0_row  # original row value saved at function entry
R0_low = R0_orig & 0x0F  # = 26 & 0xF = 10 (0xA)
print(f"Step 9: Original R0={R0_orig}, low nibble = {R0_low}")

# Step 10: Linked list walk
# L_5E6C: TSTR R0; BEQ L_5E73; ADD@ R2, R2; DECR R0; B L_5E6C
# This walks the linked list: for i in range(R0_low): R2 = R2 + [R2]
# R2 starts as the scratchpad address of the first node
# [R2] contains the offset to the next node (or something similar)
# ADD@ R2, R2 means R2 += memory[R2] (add indirect)

# BUT we don't have scratchpad data! We need to capture it.
# Let me instead try to figure out the format by working backwards from BACKTAB.

print("\n=== REVERSE ENGINEERING: What tile stream produces row 0? ===")
print("Row 0 BACKTAB pattern:")
print("  6 walls ($1603), 1 door ($081B), 6 walls ($1603), 1 detail ($1E13), 6 walls ($1603)")

# Let me compute what L_5EC7 produces for various tile indices
print("\n=== L_5EC7 OUTPUTS FOR TILE INDICES 0-31 (group 0) ===")
for tile in range(32):
    group = tile >> 5  # 0
    attr_g = rw(0x65B7 + group)
    attr_g1 = rw(0x65B7 + group + 1)
    
    r1 = attr_g >> 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)  # SWAP
    r1 ^= attr_g1
    r1 &= 0x3607
    
    # Card table: card_table[group] from ROM $65A0 (but may be different in scratchpad)
    card_byte = rb(0x65A0 + group)  # = $00 for group 0
    card_bits = card_byte << 3  # SLL x3
    
    backtab = r1 ^ card_bits
    card = backtab & 0xFF
    fg = (backtab >> 9) & 7
    bg = (backtab >> 13) & 1
    
    marker = ""
    if backtab == 0x1603: marker = " ← WALL"
    elif backtab == 0x081B: marker = " ← DOOR_TOP"
    elif backtab == 0x0823: marker = " ← DOOR_SIDE"
    elif backtab == 0x082B: marker = " ← DOOR_BOT"
    elif backtab == 0x1E13: marker = " ← DETAIL?"
    
    print(f"  tile[{tile:2d}]: backtab=${backtab:04X} card={card:3d} FG={fg} BG={bg}{marker}")

# For group 0, ALL tiles 0-31 produce $1603 (same attr, same card).
# This means the tile index within group doesn't change the BACKTAB output
# when using group 0's attr and card tables.
# Different groups must have different attr/card values!

print("\n=== ALL GROUPS: L_5EC7 output for tile_idx=0 of each group ===")
for group in range(8):
    attr_g = rw(0x65B7 + group)
    attr_g1 = rw(0x65B7 + group + 1)
    
    r1 = attr_g >> 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    r1 ^= attr_g1
    r1 &= 0x3607
    
    card_byte = rb(0x65A0 + group)
    card_bits = card_byte << 3
    
    backtab = r1 ^ card_bits
    card = backtab & 0xFF
    fg = (backtab >> 9) & 7
    bg = (backtab >> 13) & 1
    
    print(f"  group {group}: tile_idx=0 → backtab=${backtab:04X} card={card:3d} FG={fg} BG={bg}")

# Hmm, group 0 gives $1603 (wall), but what about the non-wall tiles?
# For door $081B: we need group with different attr.
# Let me check: what attr pair produces $081B?

print("\n=== WHAT ATTR PAIR PRODUCES $081B? ===")
target = 0x081B
# Looking for (attr[p]>>2 swapped ^ attr[p+1]) & 0x3607 = $081B (with card=0)
# $081B & 0x3607 = $0803
# We need r1 ^ $08 = $0803, so r1 = $080B? No.
# Actually: (attr[p]>>2 swapped ^ attr[p+1]) & 0x3607 ^ (card_byte << 3) = $081B
# With card_byte = $00 (most groups), we need:
# (attr[p]>>2 swapped ^ attr[p+1]) & 0x3607 = $081B
# 
# Let me brute-force search for which group produces $081B:
for group in range(32):
    attr_g = rw(0x65B7 + group)
    attr_g1 = rw(0x65B7 + group + 1)
    
    r1 = attr_g >> 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    r1 ^= attr_g1
    r1 &= 0x3607
    
    card_byte = rb(0x65A0 + group)
    card_bits = card_byte << 3
    
    backtab = r1 ^ card_bits
    
    if backtab == 0x081B:
        print(f"  FOUND: group {group}: attr[{group}]=${attr_g:04X} attr[{group+1}]=${attr_g1:04X} card=${card_byte:02X}")
    elif backtab == 0x0823:
        print(f"  FOUND: group {group}: attr[{group}]=${attr_g:04X} attr[{group+1}]=${attr_g1:04X} card=${card_byte:02X} → $0823")
    elif backtab == 0x082B:
        print(f"  FOUND: group {group}: attr[{group}]=${attr_g:04X} attr[{group+1}]=${attr_g1:04X} card=${card_byte:02X} → $082B")
    elif backtab == 0x1E13:
        print(f"  FOUND: group {group}: attr[{group}]=${attr_g:04X} attr[{group+1}]=${attr_g1:04X} card=${card_byte:02X} → $1E13")

# Let's also check what backtab values different groups produce for different tile_idx offsets
print("\n=== CHECKING: tile_idx WITHIN group changes result ===")
# The tile_idx = group * 32 + offset. L_5EC7 only uses group = tile_idx >> 5.
# So tile_idx within group doesn't affect L_5EC7 output.
# This means each GROUP maps to exactly ONE BACKTAB word.
# 32 groups × 1 BACKTAB word each = 32 possible tile types. But we see >32 in BACKTAB.

# Actually wait - I computed the wrong thing. Let me re-check.
# The card table entry varies by group. And within a group, different tile_idx values
# give the same result because L_5EC7 only uses group = tile_idx >> 5.
# But we see many distinct BACKTAB values ($02BF, $029F, $025F, etc.)

# Let me check ALL 32 groups for ALL their outputs:
print("\n=== ALL 32 GROUPS: BACKTAB output ===")
outputs = {}
for group in range(32):
    attr_g = rw(0x65B7 + group)
    attr_g1 = rw(0x65B7 + group + 1)
    
    r1 = attr_g >> 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    r1 ^= attr_g1
    r1 &= 0x3607
    
    card_byte = rb(0x65A0 + group)
    card_bits = card_byte << 3
    
    backtab = r1 ^ card_bits
    
    outputs[group] = backtab
    if group < 8 or backtab != outputs.get(0):
        print(f"  group[{group:2d}]: attr=({rw(0x65B7+group):04X},{rw(0x65B7+group+1):04X}) card={rb(0x65A0+group):02X} → ${backtab:04X}")

# Now count distinct outputs
distinct = set(outputs.values())
print(f"\nDistinct BACKTAB outputs from 32 groups: {len(distinct)}")
print(f"Values: {[f'${v:04X}' for v in sorted(distinct)]}")

# Compare with actual BACKTAB distinct values
actual_distinct = set()
for row in range(12):
    for col in range(20):
        addr = 0x0200 + row*20 + col
        if addr in actual_row0 if row == 0 else False:
            pass
# Let me just dump all actual distinct values
actual_all = {
    0x1603, 0x081B, 0x0823, 0x082B, 0x1E13, 0x1EBB, 0x1E5B, 0x1E40, 0x1E38, 0x1E02,
    0x02BF, 0x029F, 0x025F, 0x02B7, 0x0207, 0x020F, 0x021F, 0x022F, 0x023F, 0x024F,
    0x0257, 0x026F, 0x0287, 0x02A7, 0x02AF, 0x0317, 0x0327, 0x0347, 0x0367, 0x0377,
    0x03AF, 0x03B7, 0x03BF, 0x03E7, 0x03EF, 0x0E60
}
print(f"\nActual BACKTAB distinct values (from room 0): {len(actual_all)}")
print(f"Simulated distinct values: {len(distinct)}")
print(f"Values unique to actual: {[f'${v:04X}' for v in sorted(actual_all - distinct)]}")
print(f"Values unique to simulated: {[f'${v:04X}' for v in sorted(distinct - actual_all)]}")
