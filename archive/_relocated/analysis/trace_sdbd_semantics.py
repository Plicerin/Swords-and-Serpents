#!/usr/bin/env python3
"""
Proper CP1610 instruction trace of L_5EC7 with SDBD semantics.
Key questions:
1. Does SDBD before MVII (immediate) consume the SDBD or pass it through?
2. Does SDBD before ANDI (also immediate) affect it?
3. Are attr reads byte or word?

According to CP1610 docs: SDBD is consumed by the next instruction that
references memory. MVII and ANDI are immediate (no memory ref), so SDBD
PASSES THROUGH them to the next memory-referencing instruction.
"""

import sys
sys.stdout.reconfigure(encoding='ascii', errors='replace')

rom = open('Swords and Serpents.bin', 'rb').read()

def rw(addr):
    """Read 16-bit word at ROM address"""
    off = (addr - 0x5000) * 2
    if off < 0 or off + 1 >= len(rom): return 0
    return (rom[off] << 8) | rom[off + 1]

def rb(addr):
    """Read low byte of 16-bit word at ROM address"""
    off = (addr - 0x5000) * 2
    if off < 0 or off + 1 >= len(rom): return 0
    return rom[off + 1]

# Actual BACKTAB values from render_room_0
actual_vals = {0x1603, 0x081B, 0x0823, 0x082B, 0x1E13, 0x1EBB, 0x1E5B, 0x1E40, 0x1E38, 0x1E02,
               0x02BF, 0x029F, 0x025F, 0x02B7, 0x0207, 0x020F, 0x021F, 0x022F, 0x023F, 0x024F,
               0x0257, 0x026F, 0x0287, 0x02A7, 0x0317, 0x0327, 0x0347, 0x0367, 0x036F, 0x03AF,
               0x03B7, 0x03BF, 0x03E7, 0x03EF, 0x0E60}

# ============================================================
# THEORY A: SDBD passes through MVII, consumed by MVI@ R3, R1
#   → MVI@ R3, R1 reads a BYTE, R3 advances by 1
#   → XOR@ R3, R1 reads a WORD at byte address R3
#   → SDBD passes through ANDI (no memory ref), consumed by MVI@ R5, R3
#   → MVI@ R5, R3 reads a BYTE, R5 advances by 1
# ============================================================

def theory_A(tile_idx):
    """SDBD flows through immediate ops to the next memory op"""
    group = tile_idx >> 5
    
    # R3 = G_02F5 = $65B7 (stored in SYSRAM $02F5)
    # ADDR R1, R3 → R3 = $65B7 + group
    r3 = 0x65B7 + group  # this is a ROM address
    
    # ADDR R1, R5 → R5 = $65A0 + group (SDBD CONSUMED by previous MVI@)
    r5 = 0x65A0 + group
    
    # MVI@ R3, R1 → SDBD active: BYTE read
    r1 = rb(r3)  # byte
    r3 += 1  # advance by 1 in byte mode
    
    # SLR R1, 2
    r1 >>= 2
    # SWAP R1, 1
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    
    # XOR@ R3, R1 → no SDBD: WORD read at R3 (byte address!)
    r1 ^= rw(r3)  # word at byte-address R3
    r3 += 1  # advance by 1 in word mode (but only 1??)
    
    # SDBD; ANDI #$3607, R1 → SDBD passes through ANDI?
    # Actually SDBD before ANDI: if ANDI is immediate, SDBD passes through
    # to MVI@ R5, R3. And ANDI itself... does SDBD affect it?
    # CP1610: SDBD makes ANDI do byte-wise AND
    # Let me assume SDBD makes ANDI byte-wise:
    r1_lo = (r1 & 0xFF) & 0x07
    r1_hi = ((r1 >> 8) & 0xFF) & 0x36
    r1 = (r1_hi << 8) | r1_lo
    
    # MVI@ R5, R3 → SDBD active: BYTE read
    r3_card = rb(r5)
    r5 += 1
    
    # SLL R3, 2; SLL R3, 1 → <<= 3
    r3_card <<= 3
    
    # XORR R3, R1
    return r1 ^ r3_card

# THEORY B: SDBD is consumed by MVII (immediate eats it), second SDBD affects ANDI
def theory_B(tile_idx):
    """SDBD consumed by MVII, second SDBD makes ANDI byte-wise"""
    group = tile_idx >> 5
    
    r3 = 0x65B7 + group
    r5 = 0x65A0 + group
    
    # MVI@ R3, R1 → WORD read (SDBD already consumed)
    r1 = rw(r3)
    r3 += 2  # word mode: advance by 2 bytes (= 1 word address)
    
    r1 >>= 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    
    # XOR@ R3, R1 → WORD read
    r1 ^= rw(r3)
    
    # Second SDBD at $5ED8: ANDI byte-wise
    r1_lo = (r1 & 0xFF) & 0x07
    r1_hi = ((r1 >> 8) & 0xFF) & 0x36
    r1 = (r1_hi << 8) | r1_lo
    
    # MVI@ R5, R3 → WORD read (no SDBD)
    r3_card = rw(r5)
    r3_card <<= 3
    
    return r1 ^ r3_card

# THEORY C: Both SDBDs create byte reads at MVI@ (passing through immediates)
# ANDI is also affected by second SDBD
def theory_C(tile_idx):
    """Full SDBD effects: byte reads for both MVI@, byte-wise ANDI"""
    group = tile_idx >> 5
    
    r3 = 0x65B7 + group
    r5 = 0x65A0 + group
    
    # SDBD #1 active → MVI@ R3, R1: byte read
    r1 = rb(r3)
    r3_byt = r3 + 1
    r3 += 2  # Assume word operations still use word addresses? No...
    # Actually, after SDBD byte read, R3 increments by 1 (byte mode)
    # But the next memory op is XOR@ without SDBD → word read at byte addr
    
    # Hmm, this is the crux. After SDBD MVI@, R3 = byte_addr + 1.
    # If R3 = $65B7 + group + 1 (byte address), then XOR@ R3 reads
    # a WORD from that byte address. But ROM addresses are word-based!
    # rd(r3) where r3 is a byte address would be wrong.
    # 
    # Let me assume the CP1610 handles the conversion: 
    # For word read at byte address A, it reads the word at floor(A/2)*2
    # Actually no, in SDBD mode the address IS a byte address.
    # For word read without SDBD, the address is a word address.
    # 
    # This mixing is the problem. Let me try a different approach.
    
    # THEORY C variant: SDBD MVI@ reads byte, R3 increments to next WORD boundary
    r1 = rb(r3)
    # After byte read, for the NEXT instruction (word read), R3 should be
    # at the next word boundary. In CP1610, mixing SDBD/non-SDBD is unspecified.
    # Let me assume R3 = original_R3 + 2 (skip to next word)
    
    # Actually, let me look at how ADDR R1, R3 works. R1 = group (from tile_idx>>5).
    # R3 = $65B7 + group. R1=group. ADDR R1, R3: R3 += group.
    # So R3 = $65B7 + 2*group. But that means each group takes 2 words in the attr table.
    
    # Wait wait wait. ADDR R1, R3 adds R1 to R3. But R1 = group. R3 = $65B7.
    # So R3 = $65B7 + group. But group ranges from 0 to 7 (3-bit shift).
    
    # Hmm actually the SLR chain: SLR R1,2; SLR R1,2; SLR R1,1 → R1 >>= 5
    # So group = tile_idx >> 5. For 256 tile indices, group ranges 0-7.
    # R3 = $65B7 + group. Each group has 1 word of attr data? Or 2?
    
    # With ADDR R1, R3, R3 advances by group (1 word per group). Then:
    # MVI@ reads word at R3, and XOR@ reads word at R3+1 (auto-incremented).
    # So each group uses 2 consecutive words.
    
    # OK let me simplify. Let me just try all combinations brute-force.
    return theory_A(tile_idx)  # placeholder

# THEORY D: Like theory A but rw is replaced with reading two bytes for XOR@
def theory_D(tile_idx):
    """SDBD byte read for MVI@, then XOR@ also reads bytes (SDBD persists?)"""
    group = tile_idx >> 5
    
    r3 = 0x65B7 + group
    
    # MVI@ R3, R1: BYTE
    r1 = rb(r3)
    r3 += 1
    
    r1 >>= 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    
    # XOR@ R3: read next byte, combine with next
    byte2 = rb(r3)
    byte3 = rb(r3 + 1)
    xor_val = (byte3 << 8) | byte2
    r1 ^= xor_val
    
    # ANDI byte-wise
    r1_lo = (r1 & 0xFF) & 0x07
    r1_hi = ((r1 >> 8) & 0xFF) & 0x36
    r1 = (r1_hi << 8) | r1_lo
    
    # Card: byte read
    r5 = 0x65A0 + group
    card = rb(r5)
    card <<= 3
    
    return r1 ^ card

# ============================================================
# THEORY E: The RESULT - I found that group 0 attrs ($5A, $5B) with byte-wise ANDI
# give exactly $1603. Let me verify and extend.
# Actually, I discovered this: $5A>>2 = $16, swapped = $1600, XOR $005B = $165B.
# Byte-wise ANDI: 5B & 07 = 03, 16 & 36 = 16 → $1603. CORRECT!
# But this uses $(WORD) for the XOR, not byte.
# The question is: what is the correct SDBD interpretation?
# ============================================================

# Let's trace with the CP1610 behavior where SDBD affects only the NEXT
# memory-referencing instruction, and intermediate register ops don't consume it.

def theory_E(tile_idx):
    """
    SDBD at $5ECB is consumed by MVI@ R3,R1 at $5ED4 (byte read).
    XOR@ R3,R1 at $5ED7 is a WORD read (SDBD already consumed).
    SDBD at $5ED8 is consumed by MVI@ R5,R3 at $5EDC (byte read).
    ANDI at $5ED9 is NOT affected (SDBD at $5ED8 skips it and goes to next memory op).
    
    Wait, no. SDBD is consumed by the NEXT memory-referencing instruction.
    After SDBD at $5ED8, the next instructions are:
    - ANDI #$3607, R1 → immediate, doesn't consume SDBD
    - MVI@ R5, R3 → MEMORY reference! Consumes SDBD → byte read
    
    So actually ANDI is NOT affected by SDBD. SDBD skips over ANDI.
    """
    group = tile_idx >> 5
    
    r3 = 0x65B7 + group
    
    # SDBD #1: MVI@ R3, R1 → byte read
    r1 = rb(r3)
    r3 += 1  # R3 = $65B7 + group + 1 (byte address)
    
    r1 >>= 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    
    # XOR@ R3, R1 → WORD read at byte address R3
    # rw() expects a word address, but R3 is a byte address.
    # CP1610 likely uses the word at floor(R3/2) or R3 directly.
    # Let me try: read word at R3 (as byte address)
    # rw(R3) with R3 = byte address... let's try matching word boundary
    r1 ^= rw(r3)
    r3 += 1  # word mode: +1 word address
    
    # ANDI #$3607, R1 → standard word ANDI (SDBD skips it)
    r1 &= 0x3607
    
    # SDBD #2: MVI@ R5, R3 → byte read
    r5 = 0x65A0 + group
    r3_card = rb(r5)
    r5 += 1
    
    r3_card <<= 3
    
    return r1 ^ r3_card

# ============================================================
# Now let me just brute-force ALL combinations and see which produces
# the most matching BACKTAB values.
# ============================================================

print("=== BRUTE FORCE: ALL SDBD INTERPRETATIONS ===")
print()

# All possible SDBD effect combinations
results = {}

# For attr_read: 'word' or 'byte'
# For xor_read: 'word' or 'byte'  
# For andi: 'word' or 'byte_split'
# For card_read: 'word' or 'byte'

for attr_r in ['word', 'byte']:
    for xor_r in ['word', 'byte']:
        for andi_m in ['word', 'byte_split']:
            for card_r in ['word', 'byte']:
                outputs = {}
                for tile in range(256):
                    group = tile >> 5
                    r3 = 0x65B7 + group
                    r5 = 0x65A0 + group
                    
                    # Attr read
                    if attr_r == 'byte':
                        r1 = rb(r3)
                        r3 += 1
                    else:
                        r1 = rw(r3)
                        r3 += 1  # CP1610 auto-increment = +1 word address
                    
                    r1 >>= 2
                    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
                    
                    # XOR read
                    if xor_r == 'byte':
                        # Read two bytes and combine
                        b2 = rb(r3)
                        b3 = rb(r3 + 1)
                        r1 ^= (b3 << 8) | b2
                    else:
                        r1 ^= rw(r3)
                    
                    # ANDI
                    if andi_m == 'byte_split':
                        r1_lo = (r1 & 0xFF) & 0x07
                        r1_hi = ((r1 >> 8) & 0xFF) & 0x36
                        r1 = (r1_hi << 8) | r1_lo
                    else:
                        r1 &= 0x3607
                    
                    # Card read
                    if card_r == 'byte':
                        card = rb(r5)
                    else:
                        card = rw(r5) & 0xFF  # low byte only
                    
                    card <<= 3
                    outputs[tile] = r1 ^ card
                
                distinct = set(outputs.values())
                matches = sum(1 for v in distinct if v in actual_vals)
                label = f"attr={attr_r[0]} xor={xor_r[0]} andi={andi_m[:4]} card={card_r[0]}"
                results[label] = (len(distinct), matches, sorted(distinct))
                
                if matches >= 4:  # Only show promising results
                    print(f"[{label}] distinct={len(distinct)} matches={matches}")
                    print(f"  outputs: {[f'${v:04X}' for v in sorted(distinct)]}")
                    print()

# ============================================================
# BEST RESULT ANALYSIS
# ============================================================
print("=== TOP RESULTS ===")
sorted_results = sorted(results.items(), key=lambda x: x[1][1], reverse=True)
for label, (dist, matches, outs) in sorted_results[:8]:
    print(f"  {label}: {dist} distinct, {matches}/{len(actual_vals)} matches")
    print(f"    Outputs: {[f'${v:04X}' for v in outs]}")

# ============================================================
# KEY INSIGHT: What if the attr table values in ROM are actually
# 8-bit values, not 16-bit? The table at $65B7 stores one byte
# per group (low byte of each word), and the group indexing
# is different?
# ============================================================

print()
print("=== CHECKING: Attr table as 8-bit values (1 byte per group) ===")
print("Bytes at $65B7-$65D6:")
for i in range(32):
    b = rb(0x65B7 + i)
    print(f"  [{i:2d}] ${b:02X}", end="")
    if i % 8 == 7: print()
print()

# What if ADDR R1,R3 uses R1=group but R3 is advanced by 1 BYTE per group?
# With SDBD mode, R3 advances in bytes. So R3 = $65B7 + group.
# MVI@ reads BYTE from that address. This gives us the attr table as bytes!

# Let me check: group 0 attr byte = $5A, group 1 = $5B, group 2 = $5B, group 3 = $03...
# These would be attr[group]. What about attr[group+1]? After MVI@ byte read,
# R3 increments to $65B7+group+1. XOR@ reads WORD (or BYTE) from there.

# For group 0: attr byte = $5A, next bytes = $5B $00 (word=$005B)
#   r1 = $5A >> 2 = $16, swap = $1600
#   XOR word $005B: $1600 ^ $005B = $165B
#   ANDI word $3607: $165B & $3607 = $1603 ← WALL!

print()
print("=== DETAILED TRACE: Group 0 byte attrs → $1603 ===")
b0 = rb(0x65B7)  # $5A
w1 = rw(0x65B8)  # $005B
r1 = b0 >> 2
print(f"  attr[0] byte=${b0:02X}, >>2 = ${r1:02X}")
r1_swap = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
print(f"  SWAP → ${r1_swap:04X}")
r1_xor = r1_swap ^ w1
print(f"  XOR word at $65B8 (${w1:04X}) → ${r1_xor:04X}")
r1_word_andi = r1_xor & 0x3607
r1_byte_andi_lo = (r1_xor & 0xFF) & 0x07
r1_byte_andi_hi = ((r1_xor >> 8) & 0xFF) & 0x36
r1_byte_andi = (r1_byte_andi_hi << 8) | r1_byte_andi_lo
print(f"  ANDI word $3607: ${r1_word_andi:04X}")
print(f"  ANDI byte-split: ${r1_byte_andi:04X}")
print()

# Now trace ALL 32 groups with byte attr reads
print("=== ALL 32 GROUPS: attr byte + xor word + andi word, card byte ===")
for group in range(32):
    r3 = 0x65B7 + group
    r5 = 0x65A0 + group
    
    # Byte attr read
    r1 = rb(r3)
    r3 += 1
    
    r1 >>= 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    
    # Word XOR read at byte address
    r1 ^= rw(r3)
    
    # Word ANDI
    r1 &= 0x3607
    
    # Byte card read
    card = rb(r5)
    card <<= 3
    
    backtab = r1 ^ card
    card_num = backtab & 0xFF
    fg = (backtab >> 9) & 7
    bg = (backtab >> 13) & 1
    pastel = (backtab >> 12) & 1
    grom = (backtab >> 8) & 1
    
    marker = " ← IN BACKTAB!" if backtab in actual_vals else ""
    
    print(f"  grp[{group:2d}]: attr=${rb(0x65B7+group):02X} xor_w=${rw(0x65B7+group+1):04X} card_b=${rb(0x65A0+group):02X} → ${backtab:04X} (c={card_num:3d} FG={fg} BG={bg} P={pastel} G={grom}){marker}")

# Count matches
matches = 0
for group in range(32):
    r1 = rb(0x65B7 + group)
    r1 >>= 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    r1 ^= rw(0x65B7 + group + 1)
    r1 &= 0x3607
    card = rb(0x65A0 + group) << 3
    bt = r1 ^ card
    if bt in actual_vals:
        matches += 1

print(f"\nTotal matches: {matches}/32 groups")
