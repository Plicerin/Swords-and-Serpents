#!/usr/bin/env python3
"""Comprehensive L_5EC7 analysis: all 64 groups against actual BACKTAB."""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

rom = open('Swords and Serpents.bin', 'rb').read()
def rw(addr):
    off = (addr - 0x5000) * 2
    if off + 1 < len(rom):
        return (rom[off] << 8) | rom[off + 1]
    return 0

ATTR_BASE = 0x65B7
CARD_BASE = 0x65A0

# Actual BACKTAB words from room 0 (with counts)
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

print("=" * 100)
print("L_5EC7: ALL 64 GROUPS WITH ROM TABLES")
print("=" * 100)
print()
print(f"{'Grp':>4s} | {'attr[g]':>8s} | {'attr[g+1]':>10s} | {'card[g]':>8s} | {'r1_attr':>8s} | {'BACKTAB':>8s} | Match | Count")
print("-" * 100)

matches = {}
all_produced = {}
for g in range(64):
    a_g = rw(ATTR_BASE + g)
    a_next = rw(ATTR_BASE + g + 1)
    c = rw(CARD_BASE + g)
    
    r1 = (a_g >> 2) & 0xFFFF
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    r1 ^= a_next
    r1 = ((r1 & 0xFF) & 0x07) | (((r1 >> 8) & 0xFF) & 0x36) << 8
    r3 = (c << 3) & 0xFFFF
    bt = (r1 ^ r3) & 0xFFFF
    
    all_produced[g] = (bt, r1, c)
    
    match = "YES" if bt in ALL_BT_SET else ""
    cnt = BT_COUNTS.get(bt, 0)
    if bt in ALL_BT:
        matches[g] = bt
    
    print(f"  {g:3d} | ${a_g:04X}    | ${a_next:04X}      | ${c:04X}    | ${r1:04X}    | ${bt:04X}    | {match:5s} | {cnt:3d}")

print()
print(f"Groups matching actual BACKTAB: {len(matches)}")
for g, bt in sorted(matches.items()):
    print(f"  Group {g:2d}: ${bt:04X} ({BT_COUNTS[bt]} tiles)")

covered = set(matches.values())
missing = sorted(ALL_BT_SET - covered, key=lambda w: -BT_COUNTS[w])
print(f"\nBACKTAB words covered: {len(covered)}/{len(ALL_BT)}")
print(f"Missing ({len(missing)}):")
for w in missing:
    print(f"  ${w:04X} ({BT_COUNTS[w]:3d} tiles)")

# REVERSE: for each missing word, what r1_attr + card would produce it?
print()
print("=" * 100)
print("REVERSE ENGINEERING: What r1_attr is needed per missing BACKTAB word?")
print("=" * 100)

for bt in missing:
    print(f"\n  BACKTAB ${bt:04X} ({BT_COUNTS[bt]} tiles):")
    # For this BACKTAB to be produced: bt = r1_attr ^ (card << 3)
    # With card in range 0-0x1FF: bt ^ (card << 3) gives possible r1_attr values
    solutions = []
    for card in range(0x200):
        r1_needed = bt ^ ((card << 3) & 0xFFFF)
        # Check if any group's ROM r1_attr matches this
        for g in range(64):
            _, r1_actual, _ = all_produced[g]
            if r1_needed == r1_actual:
                solutions.append((g, card, r1_needed))
    if solutions:
        for g, card, r1a in solutions[:8]:
            print(f"    Group {g:2d}: r1_attr=${r1a:04X}, card=${card:03X} ({'GROM' if card < 256 else 'GRAM'})")
        if len(solutions) > 8:
            print(f"    ... and {len(solutions)-8} more solutions")
    else:
        print(f"    No group produces this r1_attr with any card 0-0x1FF")
        # Show what r1_attr values would work
        print(f"    Need r1_attr where: r1_attr ^ (card<<3) = ${bt:04X}")
        for card in [0, 1, 2, 3, 4, 5, 6, 7]:
            r1_needed = bt ^ ((card << 3) & 0xFFFF)
            print(f"      card=${card:03X} -> r1_attr=${r1_needed:04X}")

print()
print("=" * 100)
print("DONE")
print("=" * 100)
