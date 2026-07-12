#!/usr/bin/env python3
"""
Brute-force ALL interpretations of L_5EC7 against actual room 0 BACKTAB.
Tests all combinations of:
- SDBD effects on MVII, MVI@, ANDI
- Byte vs word reads from attr/card tables
- Different card table locations (ROM $65A0, scratchpad copies)
- Different ANDI mask interpretations
"""

import sys
sys.stdout.reconfigure(encoding='ascii', errors='replace')

rom = open('Swords and Serpents.bin', 'rb').read()

def rw(addr):
    off = (addr - 0x5000) * 2
    if off < 0 or off + 1 >= len(rom): return 0
    return (rom[off] << 8) | rom[off + 1]

def rb(addr):
    """Read low byte of 16-bit word at ROM address"""
    off = (addr - 0x5000) * 2
    if off < 0 or off + 1 >= len(rom): return 0
    return rom[off + 1]

def rh(addr):
    """Read high byte of 16-bit word at ROM address"""
    off = (addr - 0x5000) * 2
    if off < 0 or off + 1 >= len(rom): return 0
    return rom[off]

# ============================================================
# ACTUAL BACKTAB (from JZINTV render_room_0_out.txt)
# ============================================================
actual_backtab_raw = """
0200:  1603 1603 1603 1603   1603 1603 081B 1603
0208:  1603 1603 1603 1603   1603 1E13 1603 1603
0210:  1603 1603 1603 1603   1603 1603 1603 1603
0218:  1603 1603 081B 1603   1603 1603 1603 1603
0220:  1603 081B 1603 1603   1603 1603 1603 1603
0228:  081B 1603 02BF 029F   025F 02B7 0207 02BF
0230:  0327 0317 0327 02BF   020F 02B7 02A7 020F
0238:  0257 0287 02BF 0823   081B 1603 1603 1603
0240:  1603 1603 081B 1603   1603 1603 1603 1603
0248:  1603 081B 1603 1603   1603 1603 1603 1603
0250:  081B 1603 1603 1603   1603 1EBB 0327 026F
0258:  024F 022F 021F 026F   023F 0327 03AF 03EF
0260:  03E7 03B7 1603 1603   081B 1603 1603 1603
0268:  1603 1603 081B 1603   1603 1603 1603 1603
0270:  1603 081B 1603 1603   1603 1603 1603 1603
0278:  081B 1603 1603 1603   1603 1603 081B 1603
0280:  1603 1603 0E60 1603   1603 081B 1603 1603
0288:  1603 1603 1E5B 1603   081B 1603 1603 1603
0290:  1603 1603 081B 1603   1603 1603 1603 1603
0298:  1603 1E40 1603 1603   1603 1603 1603 1603
02A0:  1E40 1603 1603 1603   1603 1603 081B 1603
02A8:  1603 1603 1603 1603   1603 1603 1603 1603
02B0:  1603 1603 1603 1603   1603 1603 020F 0257
02B8:  0287 020F 02B7 0327   021F 022F 024F 020F
02C0:  0327 0367 03AF 0347   03B7 0347 03BF 036F
02C8:  0823 1E38 1603 1603   1603 1E02 082B 0823
02D0:  0823 0823 0823 0823   0823 081B 1603 1603
02D8:  0823 0823 0823 0823   1603 1603 1603 1603
02E0:  1603 1603 081B 1603   1603 1603 1603 1603
02E8:  1603 081B 1603 1603   1603 1603 1603 1603
"""

actual = {}
for line in actual_backtab_raw.strip().split('\n'):
    parts = line.split()
    addr = int(parts[0].rstrip(':'), 16)
    for i, h in enumerate(parts[1:]):
        if len(h) == 4:
            actual[addr + i] = int(h, 16)

actual_grid = [[actual.get(0x0200 + r*20 + c, 0) for c in range(20)] for r in range(12)]

# ============================================================
# ROM TABLE DATA
# ============================================================

# $65B7: attr table (full 32 groups, but we check beyond)
attr_full = [rw(0x65B7 + i) for i in range(128)]

# $65A0: card table in ROM (48 bytes)
card_rom_bytes = [rb(0x65A0 + i) for i in range(48)]

# $65DC: the "word table" - possibly contains card data as bytes
word_tbl = [rw(0x65DC + i) for i in range(0, 256, 2)]

# $65CE: linked list byte table
link_bytes = [rb(0x65CE + i) for i in range(32)]

print("=== ROM TABLE SUMMARY ===")
print(f"Attr table $65B7: first 32 words:")
for g in range(16):
    print(f"  [{g:2d}] ${attr_full[g]:04X}", end="")
    if g % 8 == 7: print()
print()

print(f"Card table $65A0 (ROM bytes):")
for g in range(48):
    print(f"  [{g:2d}] ${card_rom_bytes[g]:02X}", end="")
    if g % 8 == 7: print()
print()

print(f"Word table $65DC (first 64 as bytes):")
for i in range(0, 128, 16):
    line = f"  +{i:3d}:"
    for j in range(16):
        b = rb(0x65DC + i + j)
        line += f" ${b:02X}"
    print(line)
print()

print(f"Word table $65DC (high bytes):")
for i in range(0, 128, 16):
    line = f"  +{i:3d}:"
    for j in range(16):
        b = rh(0x65DC + i + j)
        line += f" ${b:02X}"
    print(line)
print()

# ============================================================
# INTERPRETATION 1: Standard CP1610 (no SDBD on MVII, word reads)
# ============================================================
# R5 = $65A0 (MVII immediate unaffected)
# MVI@ R3, R1 → word read from $65B7+group (attr[group])
# MVI@ R5, R3 → word read from $65A0+group (card word)

def interp1(tile_idx):
    """Standard interpretation: no SDBD effect on MVII, word reads"""
    group = tile_idx >> 5
    # R3 = G_02F5 = $65B7
    r3 = 0x65B7 + group  # but ADDR R1, R5: R1=group, R5=$65A0+group
    r5 = 0x65A0 + group
    
    # MVI@ R3, R1 → word from ROM
    r1 = rw(r3)  # attr[group]
    # SLR R1, 2
    r1 >>= 2
    # SWAP R1, 1
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    # XOR@ R3, R1 → r1 ^= attr[group+1]
    r1 ^= rw(r3 + 1)
    # ANDI #$3607, R1
    r1 &= 0x3607
    # MVI@ R5, R3 → word from ROM
    r3 = rw(r5)  # card[group]
    # SLL R3, 2; SLL R3, 1 → <<= 3
    r3 <<= 3
    # XORR R3, R1
    return r1 ^ r3

# INTERPRETATION 2: SDBD makes MVII load low byte only
def interp2(tile_idx):
    """SDBD: MVII → R5=$00A0. Card table in scratchpad (unknown location)"""
    group = tile_idx >> 5
    # R3 = G_02F5 = $65B7, word read
    r3_addr = 0x65B7 + group
    r1 = rw(r3_addr)
    r1 >>= 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    r1 ^= rw(r3_addr + 1)
    r1 &= 0x3607
    # R5 = $00A0 (scratchpad byte address) + group
    # But scratchpad is 8-bit, at $0100-$01EF in JZINTV memory map
    # $00A0 might alias to $01A0? Or we read from $00A0 directly
    # For now, we don't know what's there
    return None  # needs scratchpad data

# INTERPRETATION 3: SDBD affects MVI@ making it byte read
def interp3(tile_idx):
    """SDBD persists through the function, making MVI@ do byte reads"""
    group = tile_idx >> 5
    # SDBD is active for MVI@ R3, R1
    r3_addr = 0x65B7 + group
    # Byte read: get low byte of the pair
    r1_lo = rb(r3_addr)      # byte 0
    r1_hi = rb(r3_addr + 1)  # byte 1
    r1 = (r1_hi << 8) | r1_lo  # word from two bytes
    r1 >>= 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    # XOR with next byte pair
    r1_lo2 = rb(r3_addr + 2)
    r1_hi2 = rb(r3_addr + 3)
    r1 ^= (r1_hi2 << 8) | r1_lo2
    r1 &= 0x3607
    # Card: byte read from $65A0
    r5 = 0x65A0 + group
    card = rb(r5)  # byte
    card <<= 3
    return r1 ^ card

# INTERPRETATION 4: SDBD affects MVII (R5=$00A0), MVI@ still word
def interp4(tile_idx):
    """R5=$00A0 (scratchpad), word read from scratchpad"""
    group = tile_idx >> 5
    # Attr from ROM as words
    r1 = rw(0x65B7 + group)
    r1 >>= 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    r1 ^= rw(0x65B7 + group + 1)
    r1 &= 0x3607
    # Card from scratchpad - we need to capture this
    return None

# INTERPRETATION 5: ANDI #$3607 is two separate byte ANDs
def interp5(tile_idx):
    """ANDI is byte-wise: lo &= $07, hi &= $36"""
    group = tile_idx >> 5
    r1 = rw(0x65B7 + group)
    r1 >>= 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    r1 ^= rw(0x65B7 + group + 1)
    # Byte-wise AND: lo & 0x07, hi & 0x36
    r1_lo = (r1 & 0xFF) & 0x07
    r1_hi = ((r1 >> 8) & 0xFF) & 0x36
    r1 = (r1_hi << 8) | r1_lo
    # Card from ROM
    r3 = rw(0x65A0 + group)
    r3 <<= 3
    return r1 ^ r3

# INTERPRETATION 6: Card table is at $65DC (the word table), each word = card number
def interp6(tile_idx):
    """Card table at $65DC, word reads, no SDBD effect"""
    group = tile_idx >> 5
    r1 = rw(0x65B7 + group)
    r1 >>= 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    r1 ^= rw(0x65B7 + group + 1)
    r1 &= 0x3607
    # Card from $65DC word table
    card = rw(0x65DC + group)
    card <<= 3  # SLL x3
    # But card might be the high byte of the word (GROM card #)
    return r1 ^ (card & 0xFF)  # use low byte only

# INTERPRETATION 7: Card table uses HIGH bytes of $65DC table
def interp7(tile_idx):
    """Card from $65DC high bytes"""
    group = tile_idx >> 5
    r1 = rw(0x65B7 + group)
    r1 >>= 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    r1 ^= rw(0x65B7 + group + 1)
    r1 &= 0x3607
    card = rh(0x65DC + group)  # high byte
    card <<= 3
    return r1 ^ card

# INTERPRETATION 8: SDBD on ANDI makes mask be byte-wise
def interp8(tile_idx):
    """SDBD makes ANDI #$3607 byte-wise: ANDI #$07 on low byte, ANDI #$36 on high byte"""
    group = tile_idx >> 5
    r1 = rw(0x65B7 + group)
    r1 >>= 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    r1 ^= rw(0x65B7 + group + 1)
    # With SDBD, ANDI #$3607 → AND #$07 on low byte, #$36 on high byte
    r1 = (r1 & 0xFF00) | (r1 & 0x07)  # low byte masked with $07
    r1 = (r1 & 0x00FF) | (((r1 >> 8) & 0x36) << 8)  # high byte masked with $36
    # Wait that's the same as interp5 essentially
    r3 = rw(0x65A0 + group)
    r3 <<= 3
    return r1 ^ r3

# INTERPRETATION 9: Different order - XOR BEFORE SWAP, or no SWAP
def interp9(tile_idx):
    """No SWAP after SLR, just ANDI"""
    group = tile_idx >> 5
    r1 = rw(0x65B7 + group)
    r1 >>= 2
    # NO SWAP
    r1 ^= rw(0x65B7 + group + 1)
    r1 &= 0x3607
    r3 = rw(0x65A0 + group)
    r3 <<= 3
    return r1 ^ r3

def interp10(tile_idx):
    """XOR before SLR"""
    group = tile_idx >> 5
    r1 = rw(0x65B7 + group)
    r1 ^= rw(0x65B7 + group + 1)
    r1 >>= 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    r1 &= 0x3607
    r3 = rw(0x65A0 + group)
    r3 <<= 3
    return r1 ^ r3

# ============================================================
# Now: what if the attr table values in ROM are NOT the actual
# values used at render time? What if they're modified at load?
# Let me try to reverse-engineer what attr values PRODUCE the
# observed BACKTAB words.
# ============================================================

print("=== WORKING BACKWARDS: What attr values produce actual BACKTAB? ===")
print()

# For each distinct BACKTAB value in the actual data, figure out
# what attr pair would produce it (assuming card=some_value).

# Known: for wall $1603, card=3 (brick). $1603 - card_bits... 
# $1603 ^ (3 << 3) = $1603 ^ $0018 = $161B
# Hmm that doesn't help directly.

# Let me try: for each possible card number 0-255, compute what
# attr value ANDI'd with $3607 would produce each BACKTAB word.

actual_distinct = sorted(set(actual.values()))
print(f"Distinct BACKTAB values in room 0: {len(actual_distinct)}")
print(f"Values: {[f'${v:04X}' for v in actual_distinct]}")
print()

# Decompose BACKTAB words into card and attr parts
print("=== BACKTAB DECOMPOSITION ===")
print(f"{'BTAB':>6} {'card#':>6} {'card_hex':>9} {'attr_val':>9} {'FG':>3} {'BG':>2} {'GROM':>5} {'pastel':>7}")
print("-"*65)

for bt in actual_distinct:
    card = bt & 0xFF
    attr = bt & 0xFF00
    fg = (bt >> 9) & 7
    bg = (bt >> 13) & 1
    grom = (bt >> 8) & 1  # GROM/GRAM select
    pastel = (bt >> 12) & 1
    dbl_y = (bt >> 11) & 1  # double vertical resolution
    print(f"${bt:04X}  {card:6d}  ${card:02X}       ${attr:04X}       {fg:3d}  {bg:2d}   {grom:5d}   {pastel:7d}")

print()
print("Note: card=3 (brick), card=27 (door top), card=35 (door side), card=43 (door bottom)")
print("      FG=6 pastel brown for walls, FG=0 for doors, FG=0-3 for details")
print()

# Let me now test all interpretations against all 256 possible tile indices
# and see how many distinct BACKTAB values each produces

print("=== TESTING ALL INTERPRETATIONS ===")
print()

interpretations = [
    ("I1: standard word reads, ROM card", interp1),
    ("I3: SDBD byte reads from ROM, ROM card byte", interp3),
    ("I5: byte-wise ANDI", interp5),
    ("I6: card from $65DC low bytes", interp6),
    ("I7: card from $65DC high bytes", interp7),
    ("I9: no SWAP", interp9),
    ("I10: XOR before SLR", interp10),
]

for name, fn in interpretations:
    outputs = {}
    for tile in range(256):
        bt = fn(tile)
        outputs[tile] = bt
    
    distinct_out = set(outputs.values())
    match_count = sum(1 for bt in distinct_out if bt in actual_distinct)
    
    print(f"{name}:")
    print(f"  Distinct outputs: {len(distinct_out)}")
    print(f"  Matching actual BACKTAB values: {match_count}/{len(actual_distinct)}")
    
    # Show first few distinct outputs
    sorted_out = sorted(set(outputs.values()))
    print(f"  Outputs: {[f'${v:04X}' for v in sorted_out[:20]]}")
    print()

# ============================================================
# KEY INSIGHT: What if BACKTAB is constructed differently?
# Maybe L_5EC7 doesn't produce the FINAL BACKTAB but an intermediate?
# Or maybe the card table is loaded from an entirely DIFFERENT ROM address?
# ============================================================

print("=== CHECKING ALTERNATE CARD TABLE LOCATIONS ===")
print()

# Check: what if card table is at a different ROM address?
# The SYSRAM dump shows: $02F4=$65DC, $02F5=$65B7
# But $02F4 changes when rooms switch. Maybe different rooms
# have different card tables.

# Let me check what other data tables exist in ROM around $6000-$7000
print("Checking ROM $6800 area (room 1+ data?):")
for i in range(0, 256, 8):
    vals = [rw(0x6800 + i + j) for j in range(8)]
    print(f"  ${0x6800+i:04X}: " + " ".join(f"${v:04X}" for v in vals))

print()
print("Checking ROM $6700 area:")
for i in range(0, 128, 8):
    vals = [rw(0x6700 + i + j) for j in range(8)]
    print(f"  ${0x6700+i:04X}: " + " ".join(f"${v:04X}" for v in vals))

# ============================================================
# WHAT IF: the attr table at $65B7 is COMPRESSED or ENCODED?
# ============================================================

print()
print("=== CHECKING ATTR TABLE PATTERNS ===")
# The attr table for group 0 is $0000 $0000.
# Is this because the actual attr data is elsewhere?
# Or because group 0 really maps to all walls?

# Let me check what happens if we XOR all attr pairs:
print("Attr pairs (word[g] ^ word[g+1]):")
for g in range(0, 32, 2):
    a0 = rw(0x65B7 + g)
    a1 = rw(0x65B7 + g + 1)
    xor = a0 ^ a1
    print(f"  group [{g:2d},{g+1:2d}]: ${a0:04X} ^ ${a1:04X} = ${xor:04X}")

# ============================================================
# CRUCIAL TEST: What if L_5EC7 card table is from GRAM itself?
# The GRAM dump shows card bitmap data. Maybe the card table
# indexes into GRAM patterns.
# ============================================================

print()
print("=== GRAM ANALYSIS ===")
# From the render_room_0 GRAM dump:
# $3800: blank, $3808: font chars, $3848: brick pattern, etc.
# Card #3 (brick) would be at GRAM $3800 + 3*8 = $3818

# The brick pattern at $3800+3*8 = $3818:
print("GRAM card #3 (brick wall) at $3818:")
gram_brick = [0x00E0, 0x00EC, 0x00ED, 0x00ED, 0x00ED, 0x00ED, 0x00EC, 0x00E0]
print(f"  {[f'${b:04X}' for b in gram_brick]}")

# Card #27 (door top) at $3800+27*8 = $3800 + 216 = $38D8:
print("GRAM card #27 (door top) at $38D8:")
gram_door_top = [0x0009, 0x0095, 0x00FF, 0x00FF, 0x0095, 0x0009, 0x0000, 0x0000]
print(f"  {[f'${b:04X}' for b in gram_door_top]}")

print()
print("=== FINAL SUMMARY ===")
print("The L_5EC7 interpretation giving best match will be identified above.")
print("If no interpretation matches well, the attr/card tables are likely")
print("loaded from ROM to scratchpad with modifications during boot.")
