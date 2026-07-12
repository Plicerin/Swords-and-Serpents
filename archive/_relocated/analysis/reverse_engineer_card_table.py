#!/usr/bin/env python3
"""
REVERSE-ENGINEER RUNTIME CARD TABLE
====================================
For each actual BACKTAB word in room 0, compute:
  1. What R1_attr value each group produces (from attr[g], attr[g+1])
  2. What card value is needed: needed_card = (BACKTAB ^ R1_attr) >> 3
  3. Which groups can produce which BACKTAB words with consistent card values

This definitively answers what the runtime card table looks like.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# =========================================================================
# ROM Access
# =========================================================================
rom = open('Swords and Serpents.bin', 'rb').read()

def rw(addr):
    """Read 16-bit big-endian word at CP1610 ROM address $5000-$6FFF."""
    off = (addr - 0x5000) * 2
    if off + 1 < len(rom):
        return (rom[off] << 8) | rom[off + 1]
    return 0

# =========================================================================
# Actual BACKTAB from JZINTV capture (room 0)
# =========================================================================
BACKTAB_GRID = [
    [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1E13,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    [0x1603,0x1603,0x1603,0x1603,0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    [0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x081B,0x1603,0x02BF,0x029F,0x025F,0x02B7,0x0207,0x02BF,0x0327,0x0317,0x0327,0x02BF],
    [0x020F,0x02B7,0x02A7,0x020F,0x0257,0x0287,0x02BF,0x0823,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603],
    [0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1EBB,0x0327,0x026F,0x024F,0x022F,0x021F,0x026F],
    [0x023F,0x0327,0x03AF,0x03EF,0x03E7,0x03B7,0x1603,0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603],
    [0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603,0x081B,0x1603,0x1603,0x1603,0x0E60,0x1603],
    [0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1E5B,0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603],
    [0x1603,0x1E40,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1E40,0x1603,0x1603,0x1603,0x1603,0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603],
    [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x020F,0x0257,0x0287,0x020F,0x02B7,0x0327,0x021F,0x022F,0x024F,0x020F,0x0327],
    [0x0367,0x03AF,0x0347,0x03B7,0x0347,0x03BF,0x036F,0x0823,0x1E38,0x1603,0x1603,0x1603,0x1E02,0x082B,0x0823,0x0823,0x0823,0x0823,0x0823,0x081B],
    [0x1603,0x1603,0x0823,0x0823,0x0823,0x0823,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x081B],
]
ALL_BT_SET = set(w for row in BACKTAB_GRID for w in row)
ALL_BT = sorted(ALL_BT_SET)
BT_COUNTS = {}
for row in BACKTAB_GRID:
    for w in row:
        BT_COUNTS[w] = BT_COUNTS.get(w, 0) + 1

# =========================================================================
# ROM Tables (extended: read 64 entries to cover all possible groups)
# =========================================================================
ATTR_BASE = 0x65B7
CARD_BASE = 0x65A0

attr = [rw(ATTR_BASE + i) for i in range(64)]
card = [rw(CARD_BASE + i) for i in range(64)]

print("=" * 100)
print("REVERSE-ENGINEER RUNTIME CARD TABLE FROM ACTUAL BACKTAB")
print("=" * 100)
print()

# =========================================================================
# L_5EC7 attr computation (without card XOR)
# =========================================================================
def compute_r1_attr(group):
    """Compute R1 value after attr processing, before card XOR."""
    if group >= len(attr):
        return 0
    a_g = attr[group]
    a_next = attr[group + 1] if group + 1 < len(attr) else 0
    
    r1 = (a_g >> 2) & 0xFFFF
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)   # SWAP
    r1 ^= a_next
    # SDBD byte-wise ANDI #$3607
    r1 = ((r1 & 0xFF) & 0x07) | (((r1 >> 8) & 0xFF) & 0x36) << 8
    return r1

# For each BACKTAB word, find which groups can produce it with a valid card
print("PER-BACKTAB-WORD ANALYSIS")
print("-" * 100)
print(f"{'BACKTAB':>8s} | {'Count':>5s} | Groups that can produce it (g: needed_card)")
print("-" * 100)

word_to_groups = {}
for bt in ALL_BT:
    producing_groups = []
    for g in range(32):
        r1_attr = compute_r1_attr(g)
        needed_card = (bt ^ r1_attr) >> 3
        # Card must be 0-0x1FF (10-bit card number), multiple of 8 after <<3
        if (bt ^ r1_attr) & 0x7 == 0 and 0 <= needed_card <= 0x1FF:
            producing_groups.append((g, needed_card))
    
    word_to_groups[bt] = producing_groups
    group_str = ", ".join(f"g{g}:${needed_card:03X}" for g, needed_card in producing_groups[:6])
    if len(producing_groups) > 6:
        group_str += f" ... (+{len(producing_groups)-6} more)"
    if not producing_groups:
        group_str = "*** NO GROUP CAN PRODUCE THIS ***"
    print(f"  ${bt:04X}  | {BT_COUNTS[bt]:>5d} | {group_str}")

print()

# =========================================================================
# Find the most consistent card table
# =========================================================================
print("=" * 100)
print("CARD TABLE INFERENCE: most frequent needed_card per group")
print("=" * 100)
print()

# For each group, collect all needed_card values from words it can produce
from collections import Counter

for g in range(32):
    r1_attr = compute_r1_attr(g)
    needed_cards = Counter()
    word_matches = []
    
    for bt in ALL_BT_SET:
        needed_card = (bt ^ r1_attr) >> 3
        if (bt ^ r1_attr) & 0x7 == 0 and 0 <= needed_card <= 0x1FF:
            needed_cards[needed_card] += BT_COUNTS[bt]
            word_matches.append((bt, BT_COUNTS[bt], needed_card))
    
    if needed_cards:
        top3 = needed_cards.most_common(3)
        total_tiles = sum(c for _, c in needed_cards.items())
        best_card, best_count = top3[0]
        rom_card = card[g] if g < len(card) else 0
        
        # Check if ROM card value works (produces the most common BACKTAB word)
        rom_bt = r1_attr ^ ((rom_card << 3) & 0xFFFF)
        rom_in_bt = "YES" if rom_bt in ALL_BT else "no"
        
        print(f"  Group {g:2d}: best card=${best_card:03X} ({best_count}/{total_tiles} tiles, {100*best_count//total_tiles if total_tiles else 0}%)")
        print(f"          ROM card=${rom_card:04X} -> BACKTAB=${rom_bt:04X} in BT? {rom_in_bt}")
        if len(top3) > 1:
            print(f"          Alternatives: " + ", ".join(f"${c:03X}={cnt}" for c, cnt in top3))
        
        # Show which words match the best card
        best_words = [(bt, cnt) for bt, cnt, nc in word_matches if nc == best_card]
        if best_words:
            word_list = ", ".join(f"${bt:04X}({cnt})" for bt, cnt in sorted(best_words, key=lambda x: -x[1])[:8])
            print(f"          Produces: {word_list}")
        print()

# =========================================================================
# Brute-force: find the minimal card table that covers all BACKTAB words
# =========================================================================
print("=" * 100)
print("MINIMAL CARD TABLE: find card values that maximize BACKTAB coverage")
print("=" * 100)
print()

# For each group, try all card values 0-0x1FF and see how many BACKTAB words match
for g in range(32):
    r1_attr = compute_r1_attr(g)
    best_card = 0
    best_count = 0
    best_words = []
    
    for c in range(0x200):
        bt = r1_attr ^ ((c << 3) & 0xFFFF)
        if bt in ALL_BT:
            cnt = BT_COUNTS[bt]
            if cnt > best_count:
                best_count = cnt
                best_card = c
                best_words = [bt]
            elif cnt == best_count:
                best_words.append(bt)
    
    if best_count > 0:
        rom_card = card[g] if g < len(card) else 0
        rom_bt = r1_attr ^ ((rom_card << 3) & 0xFFFF)
        rom_in_bt = "YES" if rom_bt in ALL_BT else "no"
        word_list = ", ".join(f"${w:04X}({BT_COUNTS[w]})" for w in sorted(best_words))
        print(f"  Group {g:2d}: best_card=${best_card:03X} -> {word_list} ({best_count} tiles)")
        print(f"          ROM card=${rom_card:04X} -> ${rom_bt:04X} in BT? {rom_in_bt}")

print()

# =========================================================================
# KEY INSIGHT: Can ALL BACKTAB words be covered by just 8 groups?
# =========================================================================
print("=" * 100)
print("COVERAGE: assigning best_card to groups 0-7")
print("=" * 100)

# Try: for groups 0-7, pick the card value that covers the most BACKTAB tiles
best_cards = {}
for g in range(8):
    r1_attr = compute_r1_attr(g)
    best = None
    best_cnt = 0
    for c in range(0x200):
        bt = r1_attr ^ ((c << 3) & 0xFFFF)
        if bt in ALL_BT:
            cnt = BT_COUNTS[bt]
            if cnt > best_cnt:
                best_cnt = cnt
                best = c
    if best is not None:
        best_cards[g] = best

print(f"  Best-fit card table for groups 0-7:")
for g in range(8):
    c = best_cards.get(g, 0)
    r1_attr = compute_r1_attr(g)
    bt = r1_attr ^ ((c << 3) & 0xFFFF)
    in_bt = "YES" if bt in ALL_BT else "no"
    count = BT_COUNTS.get(bt, 0)
    print(f"    [{g}] card=${c:03X} -> BACKTAB=${bt:04X} {in_bt} ({count} tiles)")

print()
covered = set()
for g, c in best_cards.items():
    r1_attr = compute_r1_attr(g)
    bt = r1_attr ^ ((c << 3) & 0xFFFF)
    if bt in ALL_BT:
        covered.add(bt)

total_covered = sum(BT_COUNTS.get(bt, 0) for bt in covered)
total_tiles = sum(BT_COUNTS.values())
print(f"  Groups 0-7 cover {len(covered)}/{len(ALL_BT_SET)} BACKTAB words ({total_covered}/{total_tiles} tiles = {100*total_covered//total_tiles}%)")
print(f"  Missing words: {sorted([f'${w:04X}({BT_COUNTS[w]})' for w in (ALL_BT_SET - covered)])}")

print()

# =========================================================================
# TRUTH TABLE: For each actual BACKTAB word, show the L_5EC7 group that produces it
# =========================================================================
print("=" * 100)
print("TRUTH TABLE: BACKTAB word → producing groups (all possible)")
print("=" * 100)
print()

for bt in sorted(ALL_BT_SET, key=lambda w: -BT_COUNTS[w]):
    producing = []
    for g in range(32):
        r1_attr = compute_r1_attr(g)
        for c in range(0x200):
            if r1_attr ^ ((c << 3) & 0xFFFF) == bt:
                producing.append((g, c))
                break  # one card per group
    
    count = BT_COUNTS[bt]
    card_num = bt & 0x7FF
    is_gram = bool(bt & 0x0800)
    fg = ((bt >> 13) & 0x6) | ((bt >> 12) & 0x1)
    src = "GRAM" if is_gram else "GROM"
    
    group_str = ", ".join(f"g{g}(card=${card:03X})" for g, card in producing[:8])
    if len(producing) > 8:
        group_str += f" ... +{len(producing)-8}"
    
    print(f"  ${bt:04X} ({count:3d} tiles)  FG={fg} card={card_num:3d} {src:4s}")
    print(f"        Produced by: {group_str}")

print()
print("=" * 100)
print("DONE")
print("=" * 100)
