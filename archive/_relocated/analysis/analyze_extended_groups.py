#!/usr/bin/env python3
"""Analyze ALL possible groups (0-2047) through L_5EC7, find floor tile producers."""
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

# Actual BACKTAB from room 0
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
ALL_BT = set(w for row in BACKTAB_GRID for w in row)
BT_COUNTS = {}
for row in BACKTAB_GRID:
    for w in row:
        BT_COUNTS[w] = BT_COUNTS.get(w, 0) + 1

def l5ec7_r1_attr(group):
    """Compute r1_attr for a group."""
    a_g = rw(ATTR_BASE + group)
    a_next = rw(ATTR_BASE + group + 1)
    r1 = (a_g >> 2) & 0xFFFF
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    r1 ^= a_next
    r1 = ((r1 & 0xFF) & 0x07) | (((r1 >> 8) & 0xFF) & 0x36) << 8
    return r1

def l5ec7_full(group):
    """Compute BACKTAB for a group with ROM tables."""
    r1 = l5ec7_r1_attr(group)
    c = rw(CARD_BASE + group)
    bt = r1 ^ ((c << 3) & 0xFFFF)
    return bt, r1, c

print("=" * 100)
print("GROUPS 0-63: L_5EC7 outputs with ROM tables")
print("=" * 100)
print(f"{'Grp':>4s} | {'attr[g]':>8s} | {'attr[g+1]':>10s} | {'card[g]':>8s} | {'r1_attr':>8s} | {'BACKTAB':>8s} | Match | Count")
print("-" * 100)

covering = set()
for g in range(64):
    bt, r1, c = l5ec7_full(g)
    a_g = rw(ATTR_BASE + g)
    a_n = rw(ATTR_BASE + g + 1)
    match = "YES" if bt in ALL_BT else ""
    cnt = BT_COUNTS.get(bt, 0)
    if bt in ALL_BT:
        covering.add(bt)
    print(f"  {g:3d} | ${a_g:04X}    | ${a_n:04X}      | ${c:04X}    | ${r1:04X}    | ${bt:04X}    | {match:5s} | {cnt:3d}")

print()
print(f"Covered: {len(covering)}/{len(ALL_BT)} BACKTAB words")
missing = sorted(ALL_BT - covering, key=lambda w: -BT_COUNTS[w])
print(f"Missing ({len(missing)}): {', '.join('${0:04X}({1})'.format(w, BT_COUNTS[w]) for w in missing)}")

# Now search all groups 64-2047
print()
print("=" * 100)
print("SEARCHING GROUPS 64-2047 FOR FLOOR TILE PRODUCERS")
print("=" * 100)

found = {}
for g in range(64, 2048):
    bt, r1, c = l5ec7_full(g)
    if bt in ALL_BT and bt not in covering:
        if bt not in found:
            found[bt] = []
        found[bt].append((g, r1, c))

if found:
    for bt in sorted(found, key=lambda w: -BT_COUNTS[w]):
        entries = found[bt]
        print(f"\n  BACKTAB ${bt:04X} ({BT_COUNTS[bt]} tiles) - found in {len(entries)} groups:")
        for g, r1, c in entries[:5]:
            print(f"    Group {g:4d}: r1_attr=${r1:04X} card=${c:03X} ROM_card=${rw(CARD_BASE+g):04X}")
        if len(entries) > 5:
            print(f"    ... and {len(entries)-5} more")
else:
    print("  No floor tile producing groups found!")

# Check: what unique r1_attr values exist across groups 0-2047?
print()
print("=" * 100)
print("UNIQUE r1_attr VALUES ACROSS ALL GROUPS")
print("=" * 100)
unique_r1 = {}
for g in range(2048):
    r1 = l5ec7_r1_attr(g)
    if r1 not in unique_r1:
        unique_r1[r1] = []
    unique_r1[r1].append(g)

# Show r1_attr values that could help produce floor tiles
print(f"\n  Total unique r1_attr values: {len(unique_r1)}")
print(f"\n  Looking for r1_attr values that can produce floor tiles...")
print(f"  (Need r1_attr where r1_attr ^ (card<<3) = floor tile for some card 0-0x1FF)")
print()

floor_tiles = sorted(w for w in ALL_BT if (w & 0x0C00) == 0x0000)  # $0xxx-$3xxx range
print(f"  Floor tiles: {', '.join('${0:04X}'.format(w) for w in floor_tiles)}")
print()

for bt in floor_tiles:
    producing_groups = []
    for r1_val, groups in unique_r1.items():
        needed_card = (bt ^ r1_val) >> 3
        if (bt ^ r1_val) & 0x7 == 0 and 0 <= needed_card <= 0x1FF:
            producing_groups.append((r1_val, groups[:3], needed_card))
    if producing_groups:
        print(f"  ${bt:04X}: can be produced by {len(producing_groups)} r1_attr values:")
        for r1_val, groups, card in producing_groups[:5]:
            print(f"    r1_attr=${r1_val:04X} card=${card:03X} (groups: {groups})")
    else:
        print(f"  ${bt:04X}: *** NO r1_attr can produce this floor tile ***")

print()
print("=" * 100)
print("DONE")
print("=" * 100)
