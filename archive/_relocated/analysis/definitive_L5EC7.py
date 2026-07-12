#!/usr/bin/env python3
"""
Definitive L_5EC7 reverse-engineering: test ALL SDBD interpretations
against actual room 0 BACKTAB values. Find the ONE correct interpretation.
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
# ACTUAL ROOM 0 BACKTAB (from JZINTV render_room_0_out.txt)
# ============================================================
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

print(f"Loaded {len(actual_backtab)} BACKTAB words")
unique_bt = sorted(set(actual_backtab.values()))
print(f"Unique BACKTAB values: {[f'${v:04X}' for v in unique_bt]}")
print(f"Count: {len(unique_bt)}")
print()

# ============================================================
# ROM TABLE DUMP (definitive)
# ============================================================
print("=== DEFINITIVE ROM TABLE DUMP ===")
print()

print("$65B7 ATTR table: 32 words (16-bit each)")
for i in range(32):
    w = rw(0x65B7 + i*2)
    print(f"  [{i:2d}] ${w:04X}", end="")
    if i % 8 == 7: print()
print()

print("$65B7 ATTR bytes (low byte of each word):")
for i in range(32):
    b = rb(0x65B7 + i*2)
    print(f"  [{i:2d}] ${b:02X}", end="")
    if i % 16 == 15: print()
print()

print("$65A0 CARD table: 32 words (16-bit each)")
for i in range(32):
    w = rw(0x65A0 + i*2)
    print(f"  [{i:2d}] ${w:04X}", end="")
    if i % 8 == 7: print()
print()

print("$65A0 CARD bytes (low byte of each word):")
for i in range(32):
    b = rb(0x65A0 + i*2)
    print(f"  [{i:2d}] ${b:02X}", end="")
    if i % 16 == 15: print()
print()

# ============================================================
# KEY: What are the actual ROM values at $65B7 and $65A0?
# ============================================================
print("=== RAW ROM DATA AT $65B7 ===")
for i in range(32):
    addr = 0x65B7 + i*2
    b_lo = rb(addr)
    b_hi = rb(addr + 1)
    w = rw(addr)
    print(f"  [{i:2d}] ${addr:04X}: lo=${b_lo:02X} hi=${b_hi:02X} w=${w:04X}")

print()
print("=== RAW ROM DATA AT $65A0 ===")
for i in range(32):
    addr = 0x65A0 + i*2
    b_lo = rb(addr)
    b_hi = rb(addr + 1)
    w = rw(addr)
    print(f"  [{i:2d}] ${addr:04X}: lo=${b_lo:02X} hi=${b_hi:02X} w=${w:04X}")

# ============================================================
# THEORY: L_5EC7 formula
# 
# R3 = G_02F5 (SYSRAM value = $65B7)
# R5 = ? (MVII #$65A0 with possible SDBD effect)
# ADDR R1, R3 → R3 = attr_base + group (R1=group from caller)
# ADDR R1, R5 → R5 = card_base + group
# 
# SDBD #1 (at $5ECB):
#   If consumed by MVI@ R3,R1: byte read → R1 = byte[attr_base + group]
#   If passes through: word read → R1 = word[attr_base + group]
#
# XOR@ R3,R1: word read (no SDBD active)
#   R1 ^= word[attr_base + group + 1]
#
# SDBD #2 (at $5ED8):
#   If consumed by ANDI: byte-wise ANDI
#   If consumed by MVI@ R5,R3: byte card read
#   If passes through: word reads
#
# ============================================================

print()
print("=== BRUTE FORCE: ALL 16 COMBINATIONS ===")
print()

# Build attr/card tables from ROM
# Each "g" (group) indexes into the tables
# We need attr[g] (byte or word) and card[g]

# All interpretations to test
# attr: 'w'=word, 'b'=byte
# attr_xor: 'w'=word at g+1, 'b'=bytes at g+1  
# andi_sdbd: True if SDBD consumed by ANDI (byte-wise), False if passes through
# card_sdbd: True if SDBD consumed by MVI@R5 (byte read), False if word read
# card_mvii_sdbd: True if MVII is affected by SDBD (R5=scratchpad addr), False if R5=ROM

results = []
for attr_mode in ['word', 'byte']:
    for xor_mode in ['word', 'byte']:
        for andi_sdbd in [True, False]:
            for card_sdbd in [True, False]:
                for mvii_sdbd in [True, False]:
                    outputs = {}
                    distinct = set()
                    
                    for tile in range(256):
                        group = tile >> 5  # group = tile_index / 32
                        
                        # ---- ATTR READ ----
                        if attr_mode == 'byte':
                            # Read byte from attr[g]
                            a0 = rb(0x65B7 + group)  # byte
                            r3_next = 0x65B7 + group + 1  # byte address after read
                        else:
                            # Read word from attr[g]
                            # Actually, if R3 = 0x65B7 + group (word addr = group offset from base)
                            # Read word at word address
                            a0 = rw(0x65B7 + group)
                            r3_next = 0x65B7 + group + 1  # word read: R3 advances by 1 word address
                        
                        # >>2, swap
                        r1 = a0 >> 2
                        r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
                        
                        # ---- ATTR XOR READ ----
                        if xor_mode == 'byte':
                            # Read two bytes and combine
                            b1 = rb(r3_next)
                            b2 = rb(r3_next + 1)
                            xor_val = (b2 << 8) | b1
                        else:
                            xor_val = rw(r3_next)
                        
                        r1 ^= xor_val
                        
                        # ---- ANDI ----
                        if andi_sdbd:
                            # SDBD consumed by ANDI: byte-wise AND
                            r1_lo = (r1 & 0xFF) & 0x07
                            r1_hi = ((r1 >> 8) & 0xFF) & 0x36
                            r1 = (r1_hi << 8) | r1_lo
                        else:
                            # Standard word ANDI
                            r1 &= 0x3607
                        
                        # ---- CARD READ ----
                        if mvii_sdbd:
                            # MVII #$65A0 with SDBD: R5 = scratchpad address $00A0
                            card_base = 0x00A0
                        else:
                            # MVII loads full $65A0, no SDBD effect
                            card_base = 0x65A0
                        
                        if card_sdbd:
                            # MVI@ R5 reads byte
                            if card_base == 0x00A0:
                                # scratchpad: need runtime data - using placeholder
                                card = 0  # placeholder for scratchpad
                            else:
                                card = rb(card_base + group)
                        else:
                            # MVI@ R5 reads word
                            if card_base == 0x00A0:
                                # scratchpad word: placeholder
                                card = 0  # placeholder
                            else:
                                card = rw(card_base + group)
                        
                        card <<= 3
                        backtab = (r1 ^ card) & 0xFFFF
                        
                        outputs[tile] = backtab
                        distinct.add(backtab)
                    
                    matches = sum(1 for v in distinct if v in set(actual_backtab.values()))
                    
                    label = f"attr={attr_mode[0]} xor={xor_mode[0]} andi_sdbd={1 if andi_sdbd else 0} card_sdbd={1 if card_sdbd else 0} mvii_sdbd={1 if mvii_sdbd else 0}"
                    results.append((label, len(distinct), matches, distinct))
                    
                    if matches > 0:
                        print(f"[{label}] distinct={len(distinct)} matches={matches}")
                        print(f"  outputs: {[f'${v:04X}' for v in sorted(distinct)]}")
                        print()

# Sort by matches
print("=== TOP RESULTS ===")
sorted_results = sorted(results, key=lambda x: (x[2], x[1]), reverse=True)
for label, dist, matches, outputs in sorted_results[:10]:
    print(f"  {label}: {dist} distinct, {matches} matches")

print()
print("=== CARD TABLE ANALYSIS ===")
print("ROM card table at $65A0 (word reads):")
for g in range(8):
    w = rw(0x65A0 + g)
    print(f"  group {g}: ${w:04X} (<<3 = ${(w<<3)&0xFFFF:04X})")

print()
print("If card table were loaded into scratchpad $00A0 from a DIFFERENT source:")
print("Need to find the actual card values by reverse-engineering.")
print()

# ============================================================
# REVERSE ENGINEER: for each BACKTAB value, find the (attr_group, card) pair
# that produces it under the BEST interpretation found above.
# ============================================================
# From the results, the best interpretation is:
# attr=byte, xor=word, andi_sdbd=False (word ANDI), card_sdbd=True (byte)
# But this only gives 1 match with ROM tables.

# Let me try: what card values WOULD produce the correct BACKTAB
# if the processed_attr is correct from the ROM tables?

print("=== REVERSE-ENGINEER: needed card values per group ===")
print("Assuming: attr=byte, xor=word, andi=word ($3607 mask)")
print()

for g in range(32):
    # Process attr
    a0 = rb(0x65B7 + g)
    r1 = a0 >> 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    r1 ^= rw(0x65B7 + g + 1)
    processed = r1 & 0x3607
    
    # For each observed BACKTAB value, what card << 3 would produce it?
    matching_bts = []
    for bt_val in unique_bt:
        needed_card_bits = bt_val ^ processed
        card_needed = needed_card_bits >> 3
        if (card_needed << 3) == needed_card_bits and 0 <= card_needed <= 255:
            matching_bts.append((bt_val, card_needed))
    
    if matching_bts:
        print(f"  group[{g:2d}]: attr=${a0:02X} xor_w=${rw(0x65B7+g+1):04X} processed=${processed:04X}")
        for bt, card in matching_bts:
            match_str = " ← MATCH" if bt in set(actual_backtab.values()) else ""
            print(f"    BACKTAB=${bt:04X} needs card=${card:3d} (${card:02X}){match_str}")

print()
print("=== KEY QUESTION ===")
print("Groups 0-2 all have processed_attr=$1603 (wall). Need card=0 for $1603.")
print("Groups 3-5 have processed_attr=$0003. Need card=27/35/43 for $081B/$0823/$082B.")
print("But those cards need GROM bit set (cards 27,35,43 need $08xx BACKTAB).")
print("The $08 comes from bit 11 of BACKTAB, which is NOT in the ANDI $3607 mask!")
print()
print("CONCLUSION: The GROM bit must come from card << 3 having bit 11 set.")
print("If card is read as BYTE: <<3 only gives bits 0-10. Bit 11 stays 0.")
print("If card is read as WORD: high byte bits shifted into bits 8-15 could provide bit 11.")
print()
print("TEST: card_word at $65A0")
for g in range(8):
    w = rw(0x65A0 + g)
    shifted = (w << 3) & 0xFFFF
    print(f"  group {g}: card_word=${w:04X} → <<3 = ${shifted:04X}")

print()
print("For door at $081B: processed_attr=$0003, need card_bits=$0818")
print("$0818 >> 3 = $0103. So card_word should be $0103.")
print("For door at $0823: processed_attr=$0003, need card_bits=$0820")
print("$0820 >> 3 = $0104. So card_word should be $0104.")
print("For door at $082B: processed_attr=$0003, need card_bits=$0828")
print("$0828 >> 3 = $0105. So card_word should be $0105.")
print()
print("The ROM card table has $0003, $0004, $0005 for groups 3-5.")
print("We need $0103, $0104, $0105 instead - adding $0100 to each!")
print("The $0100 provides the GROM bit (bit 8 in card_word, becomes bit 11 after <<3).")
