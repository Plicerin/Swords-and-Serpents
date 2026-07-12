"""
Work backward from captured BACKTAB to deduce L_5EC7 attr/card tables.
Uses the actual room 0 BACKTAB from render_room_0_out.txt.
"""
import sys
sys.stdout.reconfigure(encoding='ascii', errors='replace')

rom = open('Swords and Serpents.bin', 'rb').read()

def rw(addr):
    """Read 16-bit word at ROM address"""
    off = (addr - 0x5000) * 2
    if off < 0 or off + 1 >= len(rom):
        return 0
    return (rom[off] << 8) | rom[off + 1]

def rb(addr):
    """Read low byte of 16-bit word at ROM address"""
    off = (addr - 0x5000) * 2
    if off < 0 or off + 1 >= len(rom):
        return 0
    return rom[off + 1]

# Actual BACKTAB from the capture (row-major, 20x12=240 tiles)
backtab_raw = [
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1E13, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x081B, 0x1603, 0x02BF, 0x029F, 0x025F, 0x02B7,
    0x0207, 0x02BF, 0x0327, 0x0317,
    0x0327, 0x02BF, 0x020F, 0x02B7, 0x02A7, 0x020F, 0x0257, 0x0287,
    0x02BF, 0x0823, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x081B, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1EBB,
    0x0327, 0x026F, 0x024F, 0x022F, 0x021F, 0x026F, 0x023F, 0x0327,
    0x03AF, 0x03EF, 0x03E7, 0x03B7, 0x1603, 0x1603, 0x081B, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B,
    0x1603, 0x1603, 0x1603, 0x1603,
    0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603,
    0x1603, 0x1603, 0x0E60, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1E5B, 0x1603,
    0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1E40, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1E40, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x020F, 0x0257,
    0x0287, 0x020F, 0x02B7, 0x0327, 0x021F, 0x022F, 0x024F, 0x020F,
    0x0327, 0x0367, 0x03AF, 0x0347,
    0x03B7, 0x0347, 0x03BF, 0x036F, 0x0823, 0x1E38, 0x1603, 0x1603,
    0x1603, 0x1E02, 0x082B, 0x0823, 0x0823, 0x0823, 0x0823, 0x0823,
    0x0823, 0x081B, 0x1603, 0x1603,
    0x0823, 0x0823, 0x0823, 0x0823, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x081B, 0x1603, 0x1603,
]

# Get distinct BACKTAB values
distinct = sorted(set(backtab_raw))
print(f"=== {len(distinct)} distinct BACKTAB values ===")

# Decompose each BACKTAB word
print("\nBACKTAB decomposition (FG, BG, G/C, Card):")
for bt in distinct:
    fg = (bt >> 13) & 0x7
    bg = ((bt >> 10) & 0x7)  # bits 12-10
    gc = (bt >> 9) & 0x1   # 0=GRAM, 1=GROM
    card = bt & 0x1FF
    gtype = "GROM" if gc else "GRAM"
    count = backtab_raw.count(bt)
    print(f"  ${bt:04X}: FG={fg} BG={bg} {gtype} card={card:3d} (${card:02X})  x{count}")

# Now reverse-engineer L_5EC7
# L_5EC7 formula: R1 = ((attr_byte << 8) ^ attr_word) & 0x3607) ^ (card_byte << 3)
# 
# Given BACKTAB word BT, we need to find attr_word, card_byte such that:
# BT = ((A_lo << 8) ^ A) & 0x3607) ^ (C << 3)
# where A = attr_word, A_lo = A & 0xFF, C = card_byte
#
# Let X = ((A_lo << 8) ^ A) & 0x3607
# Then BT = X ^ (C << 3)
# So C = ((BT ^ X) >> 3) & 0xFF

# The L_5EC7 uses the SAME attr_word for all tiles in a group (indexed by R1>>5).
# Each group has ONE attr_word and ONE card_byte.
# But we have 35 distinct BACKTAB values. If we have up to 32 groups (R1>>5 gives 0-31),
# and each group can produce only one BACKTAB value...

# UNLESS: the tile descriptor R1 ALSO contributes to the card value.
# Maybe R1's lower 5 bits are added to the card value somehow.

# Let me look at the code again:
# R1_in is the tile descriptor from the stream.
# L_5EC7 uses R1_in >> 5 = group index
# Then it reads ONE attr_byte and ONE card_byte for that group.
# But there's nothing in L_5EC7 that uses R1_in's lower bits!

# Wait... maybe the card_byte isn't from the table. Let me re-read L_5EC7:

# SDBD
# MVII #$65A0, R5       ; R5 = $65A0 (base of card table in ROM)
# ...
# ADDR R1, R5            ; R5 = $65A0 + group_index  (word address!)
# ...
# SDBD
# ANDI #$3607, R1        ; masks upper attr bits
# MVI@ R5, R3            ; R3 = byte at (card_table + group_index) [SDBD]
# SLL R3, 2; SLL R3, 1   ; R3 <<= 3
# XORR R3, R1            ; R1 ^= (card << 3)

# So R1_out depends ONLY on group_index, not on the original R1 value!
# That means all tiles in the same group produce the same BACKTAB value.
# With only 32 possible groups (0-31 from R1>>5), there can be at most 32 distinct
# BACKTAB values per room.

# But we have 35 distinct values! That means the 32-group theory is wrong,
# OR some groups index beyond the table, OR the card table is modified during rendering.

# Let me check: could R1>>5 produce more than 32 values?
# R1 is a 16-bit value. R1>>5 gives an 11-bit value (0-2047). That's way more than 32.

# But if group_index goes beyond the 32-entry tables, it would read garbage.
# Unless the tables are larger than 32 entries...

# Let me reconsider: maybe the card table IS NOT indexed by group.
# Let me re-examine the ADDR R1, R5 instruction.
# R5 = $65A0 (card table base)
# ADDR R1, R5: R5 = R5 + R1
# If R1 is the FULL tile descriptor (not just group_index), then R5 = $65A0 + R1.
# This would index directly into a card table using the tile descriptor as an offset.

# But R1 was modified by the attr processing! Let me trace again:

# R1 = MVI@ R2 (tile descriptor from stream)
# JSR R5, L_5EC7
# In L_5EC7:
#   R3 = G_02F5  (attr table base)
#   SDBD
#   R5 = $65A0   (card table base)
#   SLR R1,2; SLR R1,2; SLR R1,1   -> R1 >>= 5 (R1 is now group_index)
#   ADDR R1, R3   -> R3 = attr_table + group_index
#   ADDR R1, R5   -> R5 = card_table + group_index
#   MVI@ R3, R1   -> R1 = byte at attr_table[group_index]  [SDBD]
#   SLR R1,2      -> R1 >>= 2
#   SWAP R1,1     -> R1 = (R1_lo << 8) | R1_hi  (swap bytes)
#   XOR@ R3, R1   -> R1 ^= word at attr_table[group_index]  [no SDBD]
#   SDBD
#   ANDI #$3607, R1 -> R1 &= $3607
#   MVI@ R5, R3   -> R3 = byte at card_table[group_index]  [SDBD]
#   SLL R3,2; SLL R3,1 -> R3 <<= 3
#   XORR R3, R1   -> R1 ^= R3

# So yes, both attr and card are indexed ONLY by group_index (R1>>5).
# R1's lower 5 bits are LOST during the SLR chain.

# Unless... the SDBD before ANDI changes things. Let me check:
# Does ANDI with immediate consume SDBD?

# If ANDI #$3607, R1 does NOT consume SDBD, then MVI@ R5, R3 uses SDBD.
# But what if ANDI DOES consume SDBD? Then MVI@ R5 reads a full word.

# Let me test both interpretations:
# Interpretation A: ANDI does NOT consume SDBD -> card_byte from SDBD read
# Interpretation B: ANDI DOES consume SDBD -> card_word from full read

# For interpretation B: card_word = rw(card_table + group_index)
#   R3 = full word. R3 <<= 3 would shift a 16-bit word, potentially producing
#   values in bits 15-3, which after XOR with R1 would set bits beyond the ANDI mask.

# Actually, for interpretation B with group 0 and ROM card data:
# card_word = rw($65A0) 
# Let me compute this.

print("\n\n=== ROM Card Table at $65A0 (words, first 32) ===")
for i in range(32):
    w = rw(0x65A0 + i)
    print(f"  [{i:2d}] ${w:04X}  (lo=${w&0xFF:02X})")

print("\n=== ROM Attr Table at $65B7 (words, first 32) ===")
for i in range(32):
    w = rw(0x65B7 + i)
    lo = w & 0xFF
    hi = (w >> 8) & 0xFF
    print(f"  [{i:2d}] ${w:04X}  lo=${lo:02X} hi=${hi:02X}")

# Now test L_5EC7 with BOTH SDBD interpretations
print("\n\n=== L_5EC7 output for groups 0-31 with ROM tables ===")

for group in range(32):
    attr_word = rw(0x65B7 + group)
    attr_byte = attr_word & 0xFF
    
    # attr processing (same for both interpretations):
    # R1 = SDBD read of attr: attr_byte
    r1 = attr_byte
    r1 >>= 2                            # SLR 2
    r1 = ((r1 & 0xFF) << 8) | (r1 >> 8) # SWAP 1 (byte swap on CP1610)
    r1 ^= attr_word                     # XOR@ R3, R1
    r1 &= 0x3607                        # ANDI
    
    # Interpretation A: SDBD byte read of card
    card_byte = rb(0x65A0 + group)
    r1_a = r1 ^ (card_byte << 3)
    
    # Interpretation B: full word read of card
    card_word = rw(0x65A0 + group)
    r1_b = r1 ^ ((card_word & 0xFF) << 3)  # only low byte matters for <<3 anyway
    
    if r1_a != 0 or r1_b != 0:
        match_a = "MATCH!" if r1_a in backtab_raw else ""
        match_b = "MATCH!" if r1_b in backtab_raw else ""
        print(f"  Group {group:2d}: A=${r1_a:04X} {match_a:6s}  B=${r1_b:04X} {match_b:6s}")
