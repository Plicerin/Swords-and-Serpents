#!/usr/bin/env python3
"""Verify ROM table byte values and test L_5EC7 formula exhaustively."""

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

# ============================================================
# ACTUAL BACKTAB from room 0
# ============================================================
actual_vals = {0x1603, 0x081B, 0x0823, 0x082B, 0x1E13, 0x1EBB, 0x1E5B, 0x1E40, 0x1E38, 0x1E02,
               0x02BF, 0x029F, 0x025F, 0x02B7, 0x0207, 0x020F, 0x021F, 0x022F, 0x023F, 0x024F,
               0x0257, 0x026F, 0x0287, 0x02A7, 0x0317, 0x0327, 0x0347, 0x0367, 0x036F, 0x03AF,
               0x03B7, 0x03BF, 0x03E7, 0x03EF, 0x0E60}

print("=== DIRECT ROM BYTE DUMP ===")
print()
print("$65B7 ATTR TABLE (bytes 0-63):")
for i in range(64):
    b = rb(0x65B7 + i)
    print(f"${b:02X} ", end="")
    if i % 16 == 15: print()
print()

print("$65B7 ATTR TABLE (as 16-bit words, 32 entries):")
for i in range(0, 64, 2):
    lo = rb(0x65B7 + i)
    hi = rb(0x65B7 + i + 1)
    w = rw(0x65B7 + i)
    print(f"  [{i//2:2d}] ${0x65B7+i:04X}: lo=${lo:02X} hi=${hi:02X} word=${w:04X}")

print()
print("$65A0 CARD TABLE (bytes 0-63):")
for i in range(64):
    b = rb(0x65A0 + i)
    print(f"${b:02X} ", end="")
    if i % 16 == 15: print()
print()

print("$65CE LINK TABLE (bytes 0-31):")
for i in range(32):
    b = rb(0x65CE + i)
    print(f"${b:02X} ", end="")
    if i % 16 == 15: print()
print()

print("$65DC TILE DATA (high bytes 0-63):")
for i in range(64):
    b = rh(0x65DC + i)
    print(f"${b:02X} ", end="")
    if i % 16 == 15: print()
print()

# ============================================================
# REVERSE-ENGINEER: For each BACKTAB value, find (attr_byte, xor_word, card_byte)
# that produces it under the byte-attr word-xor word-andi byte-card formula.
# ============================================================
print()
print("=== REVERSE ENGINEERING: what (a0, xor_w, card) produces each BACKTAB? ===")
print()

for bt in sorted(actual_vals):
    solutions = []
    # Card byte 0-255
    for card in range(256):
        card_bits = card << 3
        needed = bt ^ card_bits  # what processed_attr must equal
        # processed_attr = (a0>>2 swapped ^ xor_w) & 0x3607
        # So: (a0>>2 swapped ^ xor_w) must match needed in bits 0x3607
        # For each possible a0 (0-255):
        for a0 in range(256):
            r1 = a0 >> 2
            r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
            # We need: (r1 ^ xor_w) & 0x3607 == needed
            # So: xor_w = r1 ^ (needed | dontcare)
            # The "dontcare" bits are ~0x3607 = 0xC9F8
            # Any xor_w in {r1 ^ (needed | X) for X in 0..0xC9F8} works
            # But xor_w must be 16-bit. Let me just try a few values.
            pass  # Too many combinations, approach differently

    # Better approach: for each (a0, xor_w) from the actual ROM table
    for a0 in range(256):
        r1 = a0 >> 2
        r1_swap = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
        for xor_w_lo in range(0, 256, 4):  # sample
            for xor_w_hi in range(0, 64, 4):
                xor_w = (xor_w_hi << 8) | xor_w_lo
                processed = (r1_swap ^ xor_w) & 0x3607
                for card in range(256):
                    if (processed ^ (card << 3)) == bt:
                        solutions.append((a0, xor_w, card))
                        if len(solutions) >= 3:
                            break
                    if len(solutions) >= 3:
                        break
                if len(solutions) >= 3:
                    break
            if len(solutions) >= 3:
                break
        if len(solutions) >= 3:
            break

    if solutions:
        a0, xw, c = solutions[0]
        print(f"  ${bt:04X}: a0=${a0:02X} xor_w=${xw:04X} card=${c:02X}")
    else:
        print(f"  ${bt:04X}: [no solution found]")

# ============================================================
# KEY TEST: What if the card table is NOT at $65A0 but derived differently?
# Looking at the actual BACKTAB, card numbers are:
#   0x03 = brick, 0x1B = door top, 0x23 = door side, 0x2B = door bottom
#   0x13 = special detail, 0xBF/9F/5F/B7/07/etc = various interior tiles
# ============================================================

print()
print("=== CARD NUMBER ANALYSIS FROM ACTUAL BACKTAB ===")
card_set = set()
for bt in actual_vals:
    card = bt & 0xFF
    card_set.add(card)
    fg = (bt >> 9) & 7
    bg = (bt >> 13) & 1
    pastel = (bt >> 12) & 1
    grom = (bt >> 8) & 1
    print(f"  ${bt:04X}: card=${card:3d} (${card:02X}) FG={fg} BG={bg} pastel={pastel} grom={grom}")

print(f"\nDistinct card numbers in BACKTAB: {sorted(card_set)}")

# ============================================================
# KEY INSIGHT: Looking at $65A0 card table bytes:
#   [0]=$00 [1]=$01 [2]=$02 [3]=$03 [4]=$04 [5]=$05 [6]=$06 [7]=$07
#   These are SEQUENTIAL! 
# And the attr bytes at $65B7:
#   [0]=$5A [1]=$5B [2]=$5B [3]=$03 [4]=$03 [5]=$03 [6]=$03 [7]=$58
# For group 0: a0=$5A → >>2 = $16 → swap = $1600 → xor $005B = $165B → ANDI $3607 = $1603
# With card=$00: $1603 ^ ($00<<3) = $1603. MATCHES wall!
#
# For group 3: a0=$03 → >>2 = $00 → swap = $0000 → xor $0003 = $0003 → ANDI $3607 = $0003
# With card=$03: $0003 ^ ($03<<3) = $0003 ^ $0018 = $001B. That's door top card 27!
# But actual door top in BACKTAB is $081B not $001B.
# $081B = GROM=1, pastel=0, FG=0, card=27
# $001B = GROM=0, pastel=0, FG=0, card=27
# The attr part ($0800 vs $0000) differs.
#
# So: the XOR word needs to produce bit 11 (GROM bit = $0800) for door tiles.
# Let's check: group 3 has xor_w = $0003. 
# If we need $081B, then processed_attr must be ($081B ^ card_bits).
# card_bits = $03 << 3 = $0018
# processed_attr = $081B ^ $0018 = $0803
# But we got $0003 from the formula. Missing GROM bit!
#
# The GROM bit (bit 11 in BACKTAB, which is bit 3 of high byte = $08 in high byte)
# must come from the attr processing. With ANDI $3607, bit 3 of high byte is:
# $3607 high byte = $36 = 0011 0110. Bit 3 is NOT in the mask!
# So bit 3 (GROM select in BACKTAB) MUST come from the CARD table's high bits.
# card[group] << 3 shifts the card byte left by 3. If card byte = $03, <<3 = $0018.
# That puts bits in positions 3-10 of the word. Bit 3 is where GROM select goes!
# So if card byte = $03, <<3 = $00011000 = bit 3 = 0, bit 4 = 1 (GROM select = 0)
# Wait, BACKTAB bit assignments:
# Bit 0-7: card number
# Bit 8-10: foreground color  
# Bit 11: GROM/GRAM select (GROM=1=bit11)
# Bit 12: pastel
# Bit 13: background color
#
# Wait, I need to be more careful about the bit layout. The GROM/GRAM select is
# actually encoded differently in BACKTAB. Let me think about this...
# 
# In $081B: 
# Low byte = $1B = card number 27
# High byte = $08 = bit 11 set (GROM/GRAM)
# $081B in binary: 0000 1000 0001 1011
# Bit 11 is GROM (bit 3 of high byte)
#
# In $1603:
# Low byte = $03 = card number 3
# High byte = $16 = bits 8-15: 0001 0110
# Bit 12 (pastel) = 1, bit 8-10 = 110 = FG color 6
# 
# Now, L_5EC7 with card << 3:
# card[$00] = $00 → <<3 = $0000 → no bits set
# But the wall is $1603, and $1603 ^ $0000 = $1603. 
# So processed_attr MUST produce $1603 directly for walls.
# Group 0 does: $165B & $3607 = $1603. That works.
#
# For doors, card[$03] = $03 → <<3 = $0018 = bit 3 and 4 set.
# $03 << 3 = 00011 << 3 = 00011000 = bits 3 and 4 = $18
# In BACKTAB: bit 3 is part of card number ($18 in low byte of card = card 24? No...)
# Actually card[$03] means card byte = $03 = 3. <<3 = $18.
# The card NUMBER in BACKTAB would be $18 = 24? No, card 27 = $1B.
# $1B = 27. But $03 << 3 = $18 = 24. They don't match!
#
# So the card byte is NOT the card number. It's something else that gets XORed.
# The card number comes from... where?
#
# Wait, let me re-examine. I said:
# card_bits = card[group] << 3
# bt = processed_attr ^ card_bits
#
# For wall: processed_attr = $1603, card_bits = $00<<3 = $00, bt = $1603 ✓
# For door top: processed_attr = $0003 (from group 3), card_bits = $03<<3 = $18
#   bt = $0003 ^ $0018 = $001B (card 27). But actual is $081B.
#   The issue is $0003 vs $0803. Missing GROM bit.
#
# Hmm, so for the PROCESSED_ATTR to produce $081B:
# ($081B ^ ($03<<3)) = $081B ^ $0018 = $0803
# processed_attr must be $0803 & $3607 = $0003. What? No.
# $0803 & $3607: $08 & $36 = $00, $03 & $07 = $03. So $0003.
# But we NEED $0803 to survive ANDI $3607? No, $0803 & $3607 = $0003.
# So processed_attr CAN'T produce $081B with ANDI $3607 masking away the GROM bit!
#
# This means the GROM bit must come from somewhere else, or the ANDI mask is wrong.
#
# Looking at ANDI #$3607:
# $3607 = 0011 0110 0000 0111
# This preserves:
# - High byte bits: 5,4,2,1 (no bit 3, no bit 6, no bit 7)
# - Low byte bits: 2,1,0 (no bit 3,4,5,6,7)
#
# For BACKTAB: bit 3 of high byte = GROM select = not preserved by ANDI!
# This means GROM must come from CARD << 3!
#
# card << 3: if card byte has bit 0 = GROM select...
# After <<3, bit 3 of result = original bit 0 of card byte!
# So: card byte bit 0 = GROM select (after <<3 becomes BACKTAB bit 3 of high byte)
# card byte bits 1-7 = card number high bits (after <<3 become bits 4-10)
# Low 3 bits of card number come from processed_attr (ANDI preserves 3 low bits of attr)
#
# Let me test this theory:
# Wall: card 3 = $03. <<3 = $18 = bit 3=1 (GROM), bit 4=1 (card bit 3), rest 0.
# processed_attr = $1603. ANDI $3607 preserves: $1603 → high=$16 & $36 = $16, low=$03 & $07 = $03
# bt = $1603 ^ $0018 = $161B? No! That's card 27, not 3!
#
# Hmm, that doesn't work either. Let me think differently.
# 
# Actually, the XOR with card<<3 happens AFTER ANDI $3607. So:
# bt = (processed_attr & $3607) ^ (card << 3)
# For wall group 0: processed_attr = $165B, ANDI = $1603, card <<3 = $00, bt = $1603 ✓
# For door group 3: processed_attr = $0003, ANDI = $0003, card <<3 = $18, bt = $001B
#   But actual door is $081B, not $001B.
#
# So the OR logic should be: GROM bit comes from CARD <<3 when card byte has bit 0 set.
# For door at $081B: card byte must give GROM=1 AND card=27.
# $081B: card=27 ($1B), GROM=1.
# card << 3 = bits 3-10 would encode card number. 
# $081B: card number = $1B = 27.
# card << 3 = $1B << 3 = $D8 = bit 3=1 (GROM=1), bits 4-10 = 11011 = 27!
# YES! $1B << 3 = $D8. $D8 XOR $0003 = $DB? No... 
# Actually: if card byte = $1B = 27, then card << 3 = $D8.
# $D8 ^ $0003 = $DB = 219, which is not $1B.
# 
# Wait, I'm confusing card byte with card number. The CARD BYTE is read from the 
# card table, not the card number. The card byte gets shifted left by 3 and XORed.
# The RESULTING low byte is the card number in BACKTAB.
#
# For wall: card_byte = $00. $00 << 3 = $00. ANDI attr = $1603. $1603 ^ $00 = $1603.
#   card number in BACKTAB = $03. Where did $03 come from? From attr ANDI!
#   attr low byte before ANDI: $165B low = $5B. $5B & $07 = $03. That's card number!
#
# OH! The card number's LOW 3 BITS come from attr, and HIGH bits come from card<<3!
# That's brilliant. card << 3 provides bits 3+, attr low bits provide bits 0-2.
#
# For door: card_byte = ?. door card number = $1B = 27.
# attr low 3 bits must provide the low 3 bits of card number.
# $1B & $07 = $03. So attr low 3 bits = 3 for doors too!
# Group 3: a0=$03, xor_w=$0003 → $0003 & $07 = $03. ✓
# card_byte << 3 provides bits 3-10: $1B >> 3 = $03. So card_byte = $03!
# $03 << 3 = $18. GROM bit check: $18 bit 3 = 1! GROM=1 ✓
# 
# But $0003 ^ $0018 = $001B. That's card 27, GROM=0 (bit 3 of $001B = 0).
# $001B in binary: 0000 0000 0001 1011. Bit 3 (GROM) = 0!
# We need $081B: 0000 1000 0001 1011. Bit 3 = 1.
# 
# $18 = 00011000. Bit 3 = 1. $03 = 00000011.
# $03 ^ $18 = $1B = 00011011. Bit 3 = 1! 
# $001B: low byte = $1B (00011011), high byte = $00.
# Bit 11 = bit 3 of high byte = 0. 
# But bit 3 of low byte = 1!
# 
# Wait, I need to double-check bit numbering.
# 16-bit word: bits 0-15. Bit 0 = LSB.
# Low byte = bits 0-7, high byte = bits 8-15.
# BACKTAB: bit 11 = GROM/GRAM. Bit 11 is bit 3 of HIGH byte.
# So we need bit 11 = 1 → high byte bit 3 = 1.
#
# card << 3: $18 = 00000000 00011000. Bit 3 of result = 00011000 bit 3 = 1.
# But bit 3 is in the LOW byte (bit 3 of low byte), not the high byte!
# We need bit 11 (high byte bit 3) to be 1.
# 
# card << 3 shifts by 3 bits. So card byte bits 0-7 become result bits 3-10.
# For GROM=1, we need result bit 11 set = card byte bit 8. But card byte is only 8 bits!
# 
# So: card << 3 can't set bit 11 (only up to bit 10). The GROM bit must come from
# the attr processing (via XOR word and ANDI).
#
# Let me re-examine. For wall $1603: processed_attr gives $1603. Bit 12 (pastel) = 1.
# $16 = 00010110. Bit 4 of high byte = 1 = bit 12 of word = pastel. ✓
# Bit 3 of high byte ($08) = 0. GROM/GRAM = 0. That means wall uses GRAM.
# And looking at GRAM dump, card 3 at $3818 has brick pattern. Makes sense!
#
# For door $081B: high byte = $08 = 00001000. Bit 3 = 1 = GROM.
# Card 27 ($1B) in GROM would be the door top character.
# So door uses GROM (bit 11 = 1), wall uses GRAM (bit 11 = 0).
#
# So the GROM/GRAM select comes from the attr processing, not card<<3.
# Group 0 (wall): no GROM. Group 3 (door): GROM.
#
# Let me check: group 3's processed_attr before ANDI.
# a0 = $03 (from $65B7+3), xor_w = rw($65B7+4) = rw($65BB) 
# $65BB = bytes $00 $03... wait let me recalculate.
# $65B7 bytes: [0]=$5A [1]=$5B [2]=$5B [3]=$03 [4]=$03 [5]=$03 [6]=$03 [7]=$58
# For group 3: a0 = byte at $65B7+3 = $03
#   R3 = $65B7+3. After byte read, R3 = $65B7+4 = $65BB.
#   XOR@ reads word at $65BB = rw($65BB)
#   $65BB bytes: [4]=$03 [5]=$03 → word = ($03<<8) | $03 = $0303
#   So xor_w = $0303.
#   a0 >> 2 = $00. Swap = $0000. XOR $0303 = $0303.
#   ANDI $3607: $0303 & $3607 = $0303 & ($3607) = $0003.
#   card byte = rb($65A0+3) = $03. <<3 = $18.
#   bt = $0003 ^ $0018 = $001B.
#
# That gives $001B (card=27), not $081B (card=27, GROM=1).
# The GROM bit ($0800) is missing. 
#
# The $0800 bit is bit 11. $3607 mask: bit 11 check:
# $3607 = 0011 0110 0000 0111
# Bit 11 = bit 3 of high byte = 0 in mask. So ANDI $3607 clears bit 11!
#
# So GROM must come from CARD << 3 somehow. But card << 3 only gives bits 0-10.
# Unless... card byte has more than 8 bits? No, it's a byte read via SDBD.
#
# WAIT. Maybe the ANDI mask is WRONG. Let me look at the disassembly again.
# 
# Line 2659: ANDI #$3607, R1 → 5ED9 03B9 0007 0036
#
# In CP1610, ANDI is a two-word instruction. The encoding:
# 03B9 = ANDI opcode
# 0007 = first data word
# 0036 = second data word
#
# These are STORED as 0007 0036 in ROM, but when executed:
# Does CP1610 read them as a 16-bit value $3607? Or as two 8-bit values?
#
# Actually, ANDI #$xxxx, Rn: the 16-bit immediate is $3607 = 0011011000000111.
# That's the standard interpretation.
#
# Hmm. But the mask doesn't have bit 11. So GROM comes from elsewhere.
#
# Let me look at the full BACKTAB word layout more carefully:
# $081B = 0000 1000 0001 1011
# Card number = bits 0-7 = $1B = 27 ✓
# 
# Actually wait, maybe I have the GROM/GRAM bit wrong. Let me check:
# BACKTAB format (from Intellivision docs):
# Bits 0-8: Card number (0-255) - wait, that's 9 bits?
# No: bits 0-7: Card number (0-255)
# Bit 8-10: Foreground color (0-7)
# Bit 11: GROM/GRAM (0=GRAM, 1=GROM)  
# Bit 12: Pastel
# Bit 13: Background color (0-1)
#
# So for $1603: card=$03, FG=6, GROM/GRAM=0, pastel=1, BG=0
# For $081B: card=$1B, FG=0, GROM/GRAM=1, pastel=0, BG=0
#
# $081B: high byte $08 = 00001000. Bit 3 = 1 = GROM set. ✓
# $1603: high byte $16 = 00010110. Bit 3 = 0 = GRAM. ✓
#
# Now the ANDI mask $3607:
# $3607 = 0011 0110 0000 0111
# Bits preserved:
# Bit 1,2,4,5 of high byte (bits 9,10,12,13)
# Bit 0,1,2 of low byte (bits 0,1,2)
# NOT preserved: bit 3 of high byte (bit 11 = GROM!)
#
# So GROM bit (11) is NOT preserved by ANDI. It's zeroed out.
# GROM must come from CARD << 3.
#
# card << 3: card byte bits go to result bits 3-10.
# But GROM is bit 11, which is outside card<<3 range (only bits 3-10).
# Unless... the card byte actually has its own high bits that get shifted further.
# 
# Wait, what if card is read as a WORD (no SDBD on card read)?
# Then card = rw($65A0+group). The high byte of the word could have GROM bit.
# After <<3: low byte bits + carry into high byte.
# 
# For example, if card word = $0003: <<3 = $0018. No GROM.
# If card word = $0103: <<3 = $0818. GROM=1! Card number would be $18 ^ attr_bits.
# $0818 ^ $0003 = $081B! That's the door top!
#
# YES! If the card table is read as WORDS (not bytes), then:
# card_word = rw($65A0+group)  -- high byte has GROM and other control bits
# card_word << 3 → shifts the whole 16-bit value left by 3
# Bit 11 (GROM) comes from bit 8 of card_word (which becomes bit 11 after <<3)
#
# Wait, but the SDBD at $5ED8 makes MVI@ R5, R3 a byte read, doesn't it?
# Unless the SDBD is consumed by ANDI...
# 
# From CP1610: SDBD is consumed by the next memory-referencing instruction.
# After SDBD at $5ED8, the sequence is:
# 1. ANDI #$3607, R1 - immediate, no memory ref, SDBD passes through
# 2. MVI@ R5, R3 - memory ref! SDBD consumed → byte read
#
# So card IS read as byte. But then GROM must come from elsewhere.
# Maybe the ANDI mask is different, or there's no ANDI at all?
# 
# Let me re-check the disassembly at $5ED9:
# ANDI #$3607, R1 → 5ED9   03B9 0007 0036
# 
# Actually, what if with SDBD, the ANDI constant is interpreted differently?
# No, ANDI uses an immediate, SDBD doesn't affect immediate operands.
#
# Hmm OK, let me try yet another approach. Let me compute:
# For door $081B, processed_attr (after ANDI) = X
# card << 3 = Y
# X ^ Y = $081B
#
# If card byte = $03: Y = $18. X = $081B ^ $18 = $081B ^ $0018 = $0803.
# But $0803 & $3607 = $0003. X can't be $0803 after ANDI.
# 
# If card byte = $1B: Y = $D8. X = $081B ^ $D8 = $08C3.
# $08C3 & $3607 = $0803 ^ $3607... $08 & $36 = $00, $C3 & $07 = $03 → $0003.
# 
# No matter what, ANDI $3607 kills the $08 high byte bit.
# This means my understanding is WRONG somewhere.
#
# KEY REALIZATION: What if group 3 isn't used for door tiles at all?
# What if door tiles use a DIFFERENT group where the ANDI result GIVES $08xx?
#
# Looking at the trace_sdbd_semantics output for all 32 groups:
# Group 0 gives $1603 ← wall ✓
# Group 3 gives $001B ← card 27, no GROM
# Group 4 gives $0023 ← card 35, no GROM  
# Group 5 gives $002B ← card 43, no GROM
#
# None of them produce $08xx values! The $08xx need GROM bit set.
#
# What if the Backtab writing routine ORs in a GROM bit separately?
# Or what if the card table at $65A0 has DIFFERENT values at runtime?
#
# Let me look at the $65A0 table again:
# [0]=$00 [1]=$01 [2]=$02 [3]=$03 [4]=$04 [5]=$05 [6]=$06 [7]=$07
# These are sequential - each group adds 1 to the card number.
# 
# For wall: group 0, card_byte=0 ⇒ card <<3 = 0. Wall uses GRAM (bit11=0).
# Most likely correct.
#
# What if the actual BACKTAB $08xx values are built by adding $0800 after L_5EC7?
# Looking at the BACKTAB, doors are $081B, $0823, $082B.
# These are $001B+$0800, $0023+$0800, $002B+$0800.
# Which are exactly group 3 ($001B), group 4 ($0023), group 5 ($002B) with $0800 added!
# 
# So there might be a separate OR step that adds the GROM bit!
#
# Let me check: L_5EE2/L_5EF4 writes R1 to BACKTAB. Is there an OR with R2 or R0?
# After L_5EC7 returns, the code does:
# Line 2686: MVO@ R1, R4  ; Write R1 to BACKTAB (R4 = BACKTAB addr)
#
# No OR step. So L_5EC7 must produce the final value including GROM.
#
# What if GROM comes from attr XOR word? For group 3: xor_w = $0303
# After ANDI: $03 & $36 = $02? No: $03 & $36 = $02. Hmm that's not $08.
#
# Wait: $03 (0000 0011) & $36 (0011 0110) = $02 (0000 0010). That doesn't give GROM.
#
# I'm stuck. Let me just approach this differently: 
# JZINTV trace L_5EC7 at runtime to capture register values.

print()
print("=== APPROACH: Need JZINTV trace of L_5EC7 registers ===")
print("The ROM tables alone don't explain all BACKTAB values.")
print("Must capture R1, R3, R5 at L_5EC7 entry and exit to verify formula.")
