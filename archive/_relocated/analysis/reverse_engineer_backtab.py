#!/usr/bin/env python3
"""
Reverse-engineer the L_5EC7 formula by working backward from actual BACKTAB.
For each distinct BACKTAB word, find the attr pair + card byte that produce it.

Then check which combinations appear in the ROM tables, accounting for SDBD.
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

def rh(addr):
    off = (addr - 0x5000) * 2
    if off < 0 or off + 1 >= len(rom): return 0
    return rom[off]

# Full attr table at $65B7 (128 bytes = 64 words)
# Read as words
attr_words = [rw(0x65B7 + i) for i in range(64)]
# Read as bytes
attr_bytes = [rb(0x65B7 + i) for i in range(128)]

# Card table at $65A0 (bytes)
card_bytes = [rb(0x65A0 + i) for i in range(64)]

# Actual distinct BACKTAB values from room 0
actual_vals = sorted([
    0x1603, 0x081B, 0x0823, 0x082B, 0x1E13, 0x1EBB, 0x1E5B, 0x1E40, 0x1E38, 0x1E02,
    0x02BF, 0x029F, 0x025F, 0x02B7, 0x0207, 0x020F, 0x021F, 0x022F, 0x023F, 0x024F,
    0x0257, 0x026F, 0x0287, 0x02A7, 0x0317, 0x0327, 0x0347, 0x0367, 0x036F, 0x03AF,
    0x03B7, 0x03BF, 0x03E7, 0x03EF, 0x0E60
])

print("=== REVERSE ENGINEERING: What attr/card produce each BACKTAB? ===")
print()

# For each BACKTAB value, find ALL (attr0, attr1, card_byte) triplets that produce it
# where attr0, attr1 are single bytes (as they would be read with SDBD)

# The L_5EC7 transformation we're testing:
# R1 = attr[group] (byte or word, depending on SDBD)
# R1 >>= 2
# R1 = SWAP(R1)
# R1 ^= attr[group+1] (byte or word)
# R1 &= 0x3607 (or byte-wise)
# R3 = card[group] (byte via SDBD)
# R3 <<= 3
# BACKTAB = R1 ^ R3

# Working backward:
# BACKTAB = (processed_attr & 0x3607) ^ (card << 3)
# processed_attr & 0x3607 = BACKTAB ^ (card << 3)
# The AND 0x3607 only preserves certain bits, so multiple processed_attr values
# can map to the same BACKTAB for a given card.

# Let me try ALL possible byte pairs (attr0, attr1, card) and see which produce
# each BACKTAB value

print(f"{'BACKTAB':>6} {'card':>5} {'card<<3':>8} {'attr_part':>10} {'attr0':>6} {'attr1':>6}")
print("-" * 65)

found_matches = {}

for bt in actual_vals:
    matches = []
    for a0 in range(256):
        for a1 in range(256):
            for c in range(256):
                # Try word attr read (a0 | (a1_hi << 8), but we use byte pairs)
                # We need to test both SDBD and non-SDBD interpretations
                
                # Interpretation 1: word read (no SDBD on MVI@)
                # attr_word = (a1 << 8) | a0  -- but wait, in CP1610 reading a word
                # at address $65B7+N gives the 16-bit value at that word address
                
                # Actually, we just try byte pairs with different formulas.
                # Formula 1: R1 = (a0 << 8) | a1 (word at even address)
                r1 = (a0 << 8) | a1  # word read
                r1 >>= 2
                r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)  # SWAP
                # XOR with attr[group+1] = next word
                # But we need a2, a3 for the next word...
                # We can't enumerate all 4-byte combos easily.
                pass
    
    # Simpler approach: we know the formula, let's just compute what processed attr
    # value is needed for each card
    if not matches:
        # For each possible card (0-255), compute required attr
        for c in range(256):
            card_bits = c << 3
            required_attr = (bt ^ card_bits)
            # The attr must satisfy: processed_attr & 0x3607 == required_attr
            # processed_attr = (attr_word >> 2 swapped) ^ next_word
            # But we don't know attr_word and next_word individually.
            # However, the RESULT of the AND must match.
            matches.append((c, required_attr))

print("\n=== SYSTEMATIC APPROACH: Test attr pairs from ROM ===\n")

# The most likely interpretation: 
# - SDBD at $5ECB affects MVI@ R3,R1 → byte read 
# - XOR@ R3,R1 → word read (no SDBD)
# - SDBD at $5ED8 affects MVI@ R5,R3 → byte read of card table
# - ANDI #$3607 is word AND (SDBD passes through)
# AND: SDBD at $5ED8 affects ANDI → byte-wise AND

# Interpretation A: Byte attr read + word XOR + byte card + word ANDI
def interp_A(tile_idx):
    group = tile_idx >> 5
    # MVI@ R3,R1: SDBD byte read
    r1 = rb(0x65B7 + group)  # byte at $65B7+group
    r1 >>= 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    # R3 advanced to $65B7+group+1 (byte address)
    # XOR@ R3,R1: WORD read at that address
    # But rw() expects a WORD address. After SDBD byte read, R3 is a byte address.
    # If R3 = $65B7+group+1, rw(R3) gives the word at that address.
    # Since $65B7+group+1 is odd/even depending on group...
    r1 ^= rw(0x65B7 + group + 1)  # word at the next addr
    r1 &= 0x3607
    # MVI@ R5,R3: SDBD byte read
    r3 = rb(0x65A0 + group)
    r3 <<= 3
    return r1 ^ r3

# Interpretation B: Word attr read + word XOR + byte card + word ANDI  
# (SDBD at $5ECB is consumed/ignored, or not active for some reason)
def interp_B(tile_idx):
    group = tile_idx >> 5
    # MVI@ R3,R1: word read (no SDBD effect)
    r1 = rw(0x65B7 + group)
    r1 >>= 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    r1 ^= rw(0x65B7 + group + 1)
    r1 &= 0x3607
    # MVI@ R5,R3: SDBD byte read
    r3 = rb(0x65A0 + group)
    r3 <<= 3
    return r1 ^ r3

# Interpretation C: Word attr + word XOR + byte card + byte-wise ANDI
def interp_C(tile_idx):
    group = tile_idx >> 5
    r1 = rw(0x65B7 + group)
    r1 >>= 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    r1 ^= rw(0x65B7 + group + 1)
    # Byte-wise ANDI from SDBD
    r1_lo = (r1 & 0xFF) & 0x07
    r1_hi = ((r1 >> 8) & 0xFF) & 0x36
    r1 = (r1_hi << 8) | r1_lo
    r3 = rb(0x65A0 + group)
    r3 <<= 3
    return r1 ^ r3

# Interpretation D: Byte attr + word XOR + byte card + byte-wise ANDI
def interp_D(tile_idx):
    group = tile_idx >> 5
    r1 = rb(0x65B7 + group)
    r1 >>= 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    r1 ^= rw(0x65B7 + group + 1)
    r1_lo = (r1 & 0xFF) & 0x07
    r1_hi = ((r1 >> 8) & 0xFF) & 0x36
    r1 = (r1_hi << 8) | r1_lo
    r3 = rb(0x65A0 + group)
    r3 <<= 3
    return r1 ^ r3

# Interpretation E: Like C but byte card from scratchpad
# (Need scratchpad data for this)

# Interpretation F: What if ADDR R1,R3 advances by R1 in WORD increments? 
# R1 = tile_idx >> 5 = group. R3 = $65B7 + group (word address).
# So MVI@ reads word at $65B7 + group, then XOR@ reads word at $65B7 + group + 1.
# This is what interp_B already does.

# Interpretation G: SDBD makes MVII load only low byte → R5 = $00A0
# Card table is in scratchpad at $00A0. We need scratchpad data.
# But wait: G_02F4=$65DC changes with rooms. Maybe G_02F5 also changes.
# The SYSRAM dump shows $02F5=$65B7. So the attr table IS at $65B7.
# But the card table might be copied elsewhere.

# Let me first test interpretations A-D
print("Testing all interpretations with 32 groups (tile indices 0-31 * 8 groups = 256 tiles):")
print()

for name, fn in [("A: byte attr + word XOR + byte card + word ANDI", interp_A),
                  ("B: word attr + word XOR + byte card + word ANDI", interp_B),
                  ("C: word attr + word XOR + byte card + byte ANDI", interp_C),
                  ("D: byte attr + word XOR + byte card + byte ANDI", interp_D)]:
    outputs = set()
    for tile in range(256):
        outputs.add(fn(tile))
    
    sorted_out = sorted(outputs)
    matches = sorted_out & set(actual_vals)
    
    print(f"{name}:")
    print(f"  Distinct: {len(outputs)}, Matches actual: {len(matches)}/{len(actual_vals)}")
    print(f"  Outputs:     {[f'${v:04X}' for v in sorted_out]}")
    print(f"  Matches:     {[f'${v:04X}' for v in sorted(matches)]}")
    print(f"  Missing:     {[f'${v:04X}' for v in sorted(set(actual_vals) - matches)]}")
    print()

# ============================================================
# KEY TEST: For each BACKTAB value, what attrs are needed?
# ============================================================

print("=== REVERSE ENGINEERING: Required attr values for each BACKTAB ===")
print("Given: BACKTAB = (processed_attr & 0x3607) ^ (card_byte << 3)")
print("processed_attr = (attr[group]>>2 swapped) ^ attr[group+1]")
print()

# For each BACKTAB value, try all possible (a0, a1, card) byte triplets
# Since we're enumerating bytes (0-255), let's be smart about it.

# The processed_attr for word reads: 
#   r1 = (a0 << 8) | a1  (word at even addr)
#   r1 >>= 2 → r1 = ((a0 << 8) | a1) >> 2
#   SWAP → swap bytes
#   r1 ^= (a2 << 8) | a3   (next word)

# The SWAP after >> 2 means:
# r1 = ((a0 << 8) | a1) >> 2
# r1 = ((a0 >> 2) << 8) | ( (a0 & 3) << 6) | (a1 >> 2)
# Hmm, that's already getting complex.

# Let me just compute directly: for each (a0, a1, a2, a3, card) combo,
# what BACKTAB does interp_B produce?

print("Searching for attr/card combos that produce each BACKTAB...")
print("(Testing interp_B with byte-level enumeration)")

# Enumerate byte quadruplets (a0,a1,a2,a3) as word pairs (w0, w1)
# w0 = (a1 << 8) | a0  (ROM word at even addr)
# w0_hi = a1, w0_lo = a0
# w1 = (a3 << 8) | a2

found_for = {}
for bt in actual_vals:
    found_for[bt] = []

# Search with restricted ranges for speed
for a0 in range(0, 256, 2):  # step 2 for speed
    for a1 in range(0, 128, 2):
        w0 = (a1 << 8) | a0
        r1 = w0 >> 2
        r1_swap = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
        
        for a2 in range(0, 128, 2):
            for a3 in range(0, 128, 2):
                w1 = (a3 << 8) | a2
                r1_xor = r1_swap ^ w1
                r1_word_andi = r1_xor & 0x3607
                
                r1_lo = (r1_xor & 0xFF) & 0x07
                r1_hi = ((r1_xor >> 8) & 0xFF) & 0x36
                r1_byte_andi = (r1_hi << 8) | r1_lo
                
                for card in range(0, 64, 1):
                    card_bits = card << 3
                    
                    bt_word = r1_word_andi ^ card_bits
                    bt_byte = r1_byte_andi ^ card_bits
                    
                    if bt_word in actual_vals:
                        found_for[bt_word].append((a0, a1, a2, a3, card, "word_ANDI"))
                    if bt_byte in actual_vals:
                        found_for[bt_byte].append((a0, a1, a2, a3, card, "byte_ANDI"))
                
                # Break early if all found
                if all(len(found_for[bt]) > 0 for bt in actual_vals):
                    break
            if all(len(found_for[bt]) > 0 for bt in actual_vals):
                break
        if all(len(found_for[bt]) > 0 for bt in actual_vals):
            break
    if all(len(found_for[bt]) > 0 for bt in actual_vals):
        break

print("Results (first match for each):")
for bt in actual_vals:
    matches = found_for[bt]
    if matches:
        a0, a1, a2, a3, card, mode = matches[0]
        print(f"  ${bt:04X}: attr=({a0:02X},{a1:02X}) xor ({a2:02X},{a3:02X}) card={card:02X} [{mode}]")
    else:
        print(f"  ${bt:04X}: NO MATCH FOUND")

# ============================================================
# Now check: do these attr values appear in the ROM table?
# ============================================================
print()
print("=== CHECKING ROM ATTR TABLE FOR MATCHES ===")
print("Attr bytes at $65B7:")
for i in range(0, 128, 16):
    line = f"  +{i:3d}:"
    for j in range(16):
        line += f" ${rb(0x65B7 + i + j):02X}"
    print(line)

# The SDBD key question: when SDBD makes MVI@ read bytes,
# group 0 reads byte $65B7, group 1 reads byte $65B8, etc.
# BUT the XOR then reads words at (byte_addr + 1).
# After byte read at $65B7, R3 = $65B8 (byte addr). XOR@ reads word at $65B8.
# For group 1: byte read at $65B8, R3 = $65B9. XOR@ reads word at $65B9.

# With word reads (no SDBD):
# Group 0: MVI@ reads word at $65B7 (= bytes $65B7+$65B8), XOR@ reads word at $65B8 (= $65B8+$65B9)
# Wait, that doesn't match either. In word mode, R3 increments to $65B8 after MVI@.

# Actually, in word mode:
# MVI@ $65B7 → reads rw($65B7), R3 becomes $65B8
# XOR@ $65B8 → reads rw($65B8)

# In byte mode (SDBD):
# MVI@ $65B7 → reads rb($65B7), R3 becomes $65B7+1 (byte address)... 
# But wait, does R3 become a byte address? In CP1610, SDBD mode means
# the address register increments by 1 instead of 1 (word).
# R3 = $65B7, after byte read: R3 = $65B8.
# XOR@ R3 (no SDBD): reads WORD at $65B8.

# So: SDBD byte read at group G: reads byte at $65B7+G, R3 = $65B7+G+1
# Then word read: rw($65B7+G+1) = bytes at $65B7+G+1 and $65B7+G+2

# For group 0: byte=$65B7, word=$65B8($65B8+$65B9)
# For group 1: byte=$65B8, word=$65B9($65B9+$65BA)
# Notice: group 0's word is $65B8/$65B9, group 1's word is $65B9/$65BA
# They overlap! Group 1 uses byte $65B9 that was part of group 0's word.

# Let me actually compute interp_D for each group with this understanding:

print()
print("=== PROPER SDBD TRACE: byte attr, word XOR with overlap ===")
for group in range(16):
    # SDBD byte read
    a0 = rb(0x65B7 + group)  # attr[group] byte
    
    # R3 = $65B7 + group + 1 after byte read
    # XOR@ reads word at that address
    w1 = rw(0x65B7 + group + 1)  # attr[group+1] as word
    
    r1 = a0 >> 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)  # SWAP
    r1 ^= w1
    
    # Try both ANDI modes
    r1_word = r1 & 0x3607
    r1_lo = (r1 & 0xFF) & 0x07
    r1_hi = ((r1 >> 8) & 0xFF) & 0x36
    r1_byte = (r1_hi << 8) | r1_lo
    
    # Card: SDBD byte read from scratchpad (we don't have scratchpad data yet)
    # For now, use ROM card bytes
    card_byte = rb(0x65A0 + group)
    card_bits = card_byte << 3
    
    bt_word = r1_word ^ card_bits
    bt_byte = r1_byte ^ card_bits
    
    in_actual_w = "← IN BACKTAB" if bt_word in actual_vals else ""
    in_actual_b = "← IN BACKTAB" if bt_byte in actual_vals else ""
    
    print(f"  grp[{group:2d}]: a0=${a0:02X} xor_w=${w1:04X} card=${card_byte:02X} → word_ANDI=${bt_word:04X} {in_actual_w} | byte_ANDI=${bt_byte:04X} {in_actual_b}")

# Also test: what if SDBD is consumed by MVII (R5 = $00A0) rather than passing through?
print()
print("=== ALTERNATE: SDBD consumed by MVII, card from scratchpad (unknown) ===")
print("If R5=$00A0, then card_scratch = scratchpad[$00A0+group]")
print("We need scratchpad capture to verify.")
print()
print("=== ROM card bytes at $65A0 (might differ from scratchpad $00A0+) ===")
for i in range(0, 48, 16):
    line = f"  +{i:3d}:"
    for j in range(16):
        line += f" ${rb(0x65A0 + i + j):02X}"
    print(line)
