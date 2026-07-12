#!/usr/bin/env python3
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
"""
Definitive L_5EC7 Reverse Engineering
=====================================
Works backward from actual BACKTAB data to determine:
  1. What card value each group MUST use to produce each BACKTAB word
  2. Whether a single consistent card table can produce all 35 words
  3. The exact L_5EC7 formula with verified semantics
"""
import os

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ROM_PATH = os.path.join(PROJECT_DIR, "Swords and Serpents.bin")

# =========================================================================
# ROM Access
# =========================================================================
def load_rom():
    with open(ROM_PATH, 'rb') as f:
        return f.read()

def rw_be(rom, addr):
    if addr < 0x5000 or addr > 0x6FFF:
        return 0
    offset = (addr - 0x5000) * 2
    if offset + 1 < len(rom):
        return (rom[offset] << 8) | rom[offset + 1]
    return 0

# =========================================================================
# Actual BACKTAB from JZINTV capture (room 0)
# =========================================================================
BACKTAB_GRID = [
    [0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1E13, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603],
    [0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603],
    [0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603, 0x02BF, 0x029F, 0x025F, 0x02B7, 0x0207, 0x02BF, 0x0327, 0x0317, 0x0327, 0x02BF],
    [0x020F, 0x02B7, 0x02A7, 0x020F, 0x0257, 0x0287, 0x02BF, 0x0823, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603],
    [0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1EBB, 0x0327, 0x026F, 0x024F, 0x022F, 0x021F, 0x026F],
    [0x023F, 0x0327, 0x03AF, 0x03EF, 0x03E7, 0x03B7, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603],
    [0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x0E60, 0x1603],
    [0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1E5B, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603],
    [0x1603, 0x1E40, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1E40, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603],
    [0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x020F, 0x0257, 0x0287, 0x020F, 0x02B7, 0x0327, 0x021F, 0x022F, 0x024F, 0x020F, 0x0327],
    [0x0367, 0x03AF, 0x0347, 0x03B7, 0x0347, 0x03BF, 0x036F, 0x0823, 0x1E38, 0x1603, 0x1603, 0x1603, 0x1E02, 0x082B, 0x0823, 0x0823, 0x0823, 0x0823, 0x0823, 0x081B],
    [0x1603, 0x1603, 0x0823, 0x0823, 0x0823, 0x0823, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B],
]

ALL_DISTINCT = sorted(set(w for row in BACKTAB_GRID for w in row))

# =========================================================================
# L_5EC7 formula — Correct CP1610 semantics
# =========================================================================

def l5ec7_r1_attr(attr_table, group_idx):
    """
    Compute the attribute contribution R1 (before card XOR).
    
    ASM:
        MVI G_02F5, R3        ; R3 = $65B7 (attr base)
        <R1 = group>
        ADDR R1, R3           ; R3 = $65B7 + group
        MVI@ R3, R1           ; R1 = attr[group]; R3 -> group+1
        SLR R1, 2
        SWAP R1, 1
        XOR@ R3, R1           ; R1 ^= attr[group+1] (reads NEXT word)
        SDBD
        ANDI #$3607, R1       ; byte-wise AND with mask
    
    Key: XOR@ R3 reads the NEXT word (R3 was auto-incremented by MVI@).
    SDBD+ANDI: the mask $3607 is byte-wise: lo=$07, hi=$36.
    """
    if group_idx >= len(attr_table):
        return 0
    
    attr_word = attr_table[group_idx]
    
    # R1 = attr_word >> 2
    r1 = (attr_word >> 2) & 0xFFFF
    
    # SWAP R1 (byte swap)
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    
    # XOR with attr[group+1] (auto-incremented pointer)
    if group_idx + 1 < len(attr_table):
        r1 ^= attr_table[group_idx + 1]
    else:
        r1 ^= attr_word  # wrap back (or any behavior — doesn't matter for group 7)
    
    # SDBD byte-wise ANDI #$3607
    # With SDBD, ANDI reads mask bytes from consecutive addresses
    # lo mask = lo(3607) = $07, hi mask = lo(next_word)
    # The next word after $3607 in ROM makes the hi mask.
    # For now, test both interpretations: word ANDI vs byte ANDI
    mask_lo = 0x07
    mask_hi = 0x36
    r1_byte = ((r1 & 0xFF) & mask_lo) | (((r1 >> 8) & 0xFF) & mask_hi) << 8
    
    # Also compute without SDBD (word ANDI)
    r1_word = r1 & 0x3607
    
    return r1_byte, r1_word


def l5ec7_full(attr_table, card_val, group_idx, use_sdbd_andi=True):
    """
    Full L_5EC7: compute BACKTAB word from attr table and card value.
    card_val can be a word ($0103) or byte ($03) — we handle both.
    """
    r1_byte, r1_word = l5ec7_r1_attr(attr_table, group_idx)
    r1 = r1_byte if use_sdbd_andi else r1_word
    
    # Card: shift left 3
    r3 = (card_val << 3) & 0xFFFF
    
    return (r1 ^ r3) & 0xFFFF


# =========================================================================
# Load ROM tables
# =========================================================================

rom = load_rom()
print(f"ROM loaded: {len(rom)} bytes")

ATTR_BASE = 0x65B7
attr_rom = [rw_be(rom, ATTR_BASE + i) for i in range(8)]

CARD_BASE = 0x65A0
card_rom_words = [rw_be(rom, CARD_BASE + i) for i in range(8)]
card_rom_bytes = [rw_be(rom, CARD_BASE + i) & 0xFF for i in range(8)]

print(f"\nAttr table @ ${ATTR_BASE:04X}:")
for i, a in enumerate(attr_rom):
    print(f"  [{i}] ${a:04X}")

print(f"\nCard table @ ${CARD_BASE:04X} (words):")
for i, c in enumerate(card_rom_words):
    print(f"  [{i}] ${c:04X}")

print(f"\nCard table @ ${CARD_BASE:04X} (bytes):")
for i, c in enumerate(card_rom_bytes):
    print(f"  [{i}] ${c:02X}")

# =========================================================================
# Part 1: Compute R1 attr contribution for each group
# =========================================================================

print("\n" + "=" * 80)
print("PART 1: R1 Attribute Contribution per Group")
print("=" * 80)

print(f"\n{'Group':>6s} | {'attr[g]':>8s} | {'attr[g+1]':>8s} | {'R1 (byte ANDI)':>14s} | {'R1 (word ANDI)':>14s} | Notes")
print(f"{'-'*6} | {'-'*8} | {'-'*8} | {'-'*14} | {'-'*14} | {'-'*20}")

for g in range(8):
    r1_byte, r1_word = l5ec7_r1_attr(attr_rom, g)
    a_g = attr_rom[g]
    a_next = attr_rom[g+1] if g+1 < 8 else 0
    note = ""
    if g <= 2:
        note = "(walls: GROM card 3 + features)"
    elif g <= 5:
        note = "(doors: GRAM cards 27, 35, 43)"
    else:
        note = "(features: GRAM cards 56, 64...)"
    print(f"  {g:3d}  | ${a_g:04X}    | ${a_next:04X}    | ${r1_byte:04X}          | ${r1_word:04X}          | {note}")


# =========================================================================
# Part 2: For each actual BACKTAB word, compute required card value for each group
# =========================================================================

print("\n" + "=" * 80)
print("PART 2: Reverse-Engineer Card Values per BACKTAB Word per Group")
print("=" * 80)

# For each group, the BACKTAB = r1_attr ^ (card << 3)
# So card_needed = ((BACKTAB ^ r1_attr) >> 3) & 0x1FFF

# For each group and SDBD interpretation, find which BACKTAB words match
for use_sdbd in [True, False]:
    label = "SDBD byte ANDI" if use_sdbd else "word ANDI"
    print(f"\n--- Using {label} ---")
    
    r1_cache = {}
    for g in range(8):
        r1_byte, r1_word = l5ec7_r1_attr(attr_rom, g)
        r1_cache[g] = r1_byte if use_sdbd else r1_word
    
    for g in range(8):
        r1 = r1_cache[g]
        matches = []
        for bt in ALL_DISTINCT:
            needed = ((bt ^ r1) >> 3) & 0x1FFF
            # Verify
            recomputed = (r1 ^ ((needed << 3) & 0xFFFF)) & 0xFFFF
            if recomputed == bt:
                is_gram = (needed & 0x100) != 0
                matches.append((bt, needed, is_gram))
        
        if matches:
            print(f"\n  Group {g} (r1=${r1:04X}): {len(matches)} matches")
            for bt, card, is_gram in sorted(matches):
                card_display = f"${card:04X}" if is_gram else f"${card & 0xFF:02X}"
                print(f"    ${bt:04X}  <- card={card_display} {'(GRAM)' if is_gram else '(GROM)'}")


# =========================================================================
# Part 3: Find the minimal card table that produces ALL distinct BACKTAB words
# =========================================================================

print("\n" + "=" * 80)
print("PART 3: Find Optimal Card Table")
print("=" * 80)

# We need: for each group g, a SINGLE card value card[g] such that
# L_5EC7(attr_rom, card[g], g) produces the right BACKTAB words for tiles of that group.
#
# Problem: one group produces MULTIPLE BACKTAB words (e.g., group 0 produces both
# $1603 walls and $1E13 features). But L_5EC7 is called with a single tile descriptor 
# that maps to a single group — so the tile stream must provide different tile indices
# for walls vs features within the same group.
#
# Wait — that's the key insight! The tile descriptor (4 bits) encodes group + variant.
# L_5EE2 calls L_5EC7 with the full tile descriptor (R1), which gets divided by 32 (>>5)
# to get the group index. So tiles $00-$1F all map to group 0, $20-$3F to group 1, etc.
#
# But within a group, different tile indices exist... and they all produce the SAME
# BACKTAB word since they map to the same attr[g] and card[g]!
#
# This means: each group maps to EXACTLY ONE BACKTAB word type via L_5EC7.
# The variation within a group must come from the TILE STREAM (L_5E48-L_5E76),
# which provides per-tile data that overrides or supplements the group-based lookup.

print("\nKey insight: Each L_5EC7 call produces ONE BACKTAB word per group.")
print("The tile stream (L_5E76) provides per-tile data that supplements the group lookup.")
print()

# Let's find the most common BACKTAB word per group by matching
for use_sdbd in [True, False]:
    label = "SDBD byte ANDI" if use_sdbd else "word ANDI"
    print(f"\n--- Best-fit card per group ({label}) ---")
    
    r1_cache = {}
    for g in range(8):
        r1_byte, r1_word = l5ec7_r1_attr(attr_rom, g)
        r1_cache[g] = r1_byte if use_sdbd else r1_word
    
    for g in range(8):
        r1 = r1_cache[g]
        # Try different card sources
        candidates = []
        
        # ROM word
        bt = l5ec7_full(attr_rom, card_rom_words[g], g, use_sdbd)
        candidates.append(("ROM word", card_rom_words[g], bt))
        
        # ROM byte (low byte only)
        bt = l5ec7_full(attr_rom, card_rom_bytes[g], g, use_sdbd)
        candidates.append(("ROM byte", card_rom_bytes[g], bt))
        
        # Try card=0 (walls for groups 0-2)
        bt = l5ec7_full(attr_rom, 0, g, use_sdbd)
        candidates.append(("card=$0000", 0, bt))
        
        print(f"  Group {g} (r1=${r1:04X}):")
        for label_c, card_val, bt in candidates:
            in_backtab = "YES" if bt in ALL_DISTINCT else "NO"
            if in_backtab == "YES":
                print(f"    {label_c}: card=${card_val:04X} -> BACKTAB=${bt:04X}  *** MATCH ***")
            else:
                print(f"    {label_c}: card=${card_val:04X} -> BACKTAB=${bt:04X}")


# =========================================================================
# Part 4: Summary of findings
# =========================================================================

print("\n" + "=" * 80)
print("PART 4: SUMMARY")
print("=" * 80)

print("""
FINDINGS:
1. With SDBD byte-wise ANDI ($3607 -> lo=$07 hi=$36):
   - Groups 0-2 (attr $005A/$005B): r1_attr = $1603
     This produces $1603 (GROM wall, card 3) with card=0.
     The ROM card word $0100 produces $1E03 (GRAM) — NOT matching actual $1603.
   
2. With word ANDI ($3607):
   - Groups 0-2: r1_attr also = $1603 (same result, ANDI works either way for this value)

3. ROM card words ($0100-$0107) for groups 3-5 produce doors ($081B, $0823, $082B)
   because card=$0103 -> <<3 = $0818, XOR with attr=$0003 -> $081B.

4. The card table MUST be runtime-modified: groups 0-2 need card=0, not ROM $0100-$0102.

5. GRAM features ($1E13, $1EBB, $1E40, etc.) come from groups 6-7 with specific card values
   that differ from the ROM values ($0106-$0107).
""")
