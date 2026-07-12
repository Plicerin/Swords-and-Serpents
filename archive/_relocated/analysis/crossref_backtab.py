#!/usr/bin/env python3
"""
Comprehensive BACKTAB Cross-Reference Analysis
Cross-references every unique BACKTAB word from runtime capture against:
1. Wall pre-fill ($1603)
2. L_5EC7 tile stream renderer (all 64 card/attr groups)
3. L_63B9 object BACKTAB table ($655E, types 0-31)
4. Identifies unmatched values for further investigation
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

rom = open('Swords and Serpents.bin', 'rb').read()

def rw(a):
    """Read 16-bit word from ROM at CP-1610 address a."""
    o = (a - 0x5000) * 2
    if o + 1 < len(rom):
        return (rom[o] << 8) | rom[o + 1]
    return 0

# ============================================================
# ACTUAL BACKTAB from runtime capture (dump_room_out.txt)
# ============================================================
actual_backtab_raw = [
    # Row 0  ($0200-$0213)
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603,
    # Row 1  ($0214-$0227)
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603,
    # Row 2  ($0228-$023B)
    0x1603, 0x1603, 0x179B, 0x17BB, 0x177B, 0x1793, 0x1723, 0x179B,
    0x1603, 0x1633, 0x1603, 0x179B, 0x172B, 0x1793, 0x1783, 0x172B,
    0x1773, 0x17A3, 0x179B, 0x1603,
    # Row 3  ($023C-$024F)
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603,
    # Row 4  ($0250-$0263)
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1EBB, 0x1603, 0x174B,
    0x176B, 0x170B, 0x173B, 0x174B, 0x171B, 0x1603, 0x168B, 0x16CB,
    0x16C3, 0x1693, 0x1603, 0x1603,
    # Row 5  ($0264-$0277)
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603,
    # Row 6  ($0278-$028B)
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603,
    # Row 7  ($028C-$029F)
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603,
    # Row 8  ($02A0-$02B3)
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603,
    # Row 9  ($02B4-$02C7)
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x172B, 0x1773,
    0x17A3, 0x172B, 0x1793, 0x1603, 0x173B, 0x170B, 0x176B, 0x172B,
    0x1603, 0x1643, 0x168B, 0x1663,
    # Row 10 ($02C8-$02DB)
    0x1693, 0x1663, 0x169B, 0x164B, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603,
    # Row 11 ($02DC-$02EF)
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603,
    0x1603, 0x1603, 0x1603, 0x1603,
]

# ============================================================
# SOURCE 1: Wall pre-fill
# ============================================================
WALL_PREFILL = 0x1603

# ============================================================
# SOURCE 2: L_5EC7 tile stream renderer
# Simulate L_5EC7 for all 64 card/attr groups
# ============================================================
def l5ec7_simulate(group_idx):
    """Simulate L_5EC7 for a given group index (0-63)."""
    # L_5EC7 loads attr from $65B7+group via SDBD pointer G_02F5
    attr_group = rw(0x65B7 + group_idx)
    attr_next = rw(0x65B7 + group_idx + 1)
    
    # Step 1: SLR attr_group by 2, then swap bytes
    shifted = (attr_group >> 2) & 0xFFFF
    r1 = ((shifted & 0xFF) << 8) | ((shifted >> 8) & 0xFF)
    
    # Step 2: XOR with next attr
    r1 ^= attr_next
    
    # Step 3: AND with $3607 mask
    r1_attr = ((r1 & 0xFF) & 0x07) | (((r1 >> 8) & 0xFF) & 0x36) << 8
    
    # Step 4: Load card and XOR
    card = rw(0x65A0 + group_idx)
    card_shifted = (card << 3) & 0xFFFF
    r1_attr ^= card_shifted
    
    return r1_attr & 0xFFFF

# Generate all L_5EC7 outputs
l5ec7_outputs = {}
for g in range(64):
    bt = l5ec7_simulate(g)
    if bt not in l5ec7_outputs:
        l5ec7_outputs[bt] = []
    l5ec7_outputs[bt].append(g)

# ============================================================
# SOURCE 3: Object BACKTAB table ($655E)
# ============================================================
object_table = {}
for t in range(32):
    bt = rw(0x655E + t * 2)
    if bt not in object_table:
        object_table[bt] = []
    object_table[bt].append(t)

# ============================================================
# CROSS-REFERENCE ANALYSIS
# ============================================================
print("=" * 70)
print("COMPREHENSIVE BACKTAB CROSS-REFERENCE ANALYSIS")
print("=" * 70)

# Get unique actual BACKTAB values
from collections import Counter
bt_counts = Counter(actual_backtab_raw)
unique_bt = sorted(bt_counts.keys())

print(f"\nTotal BACKTAB cells: {len(actual_backtab_raw)}")
print(f"Unique BACKTAB values: {len(unique_bt)}")
print(f"Wall pre-fill ($1603): {bt_counts[WALL_PREFILL]} cells ({bt_counts[WALL_PREFILL]*100/len(actual_backtab_raw):.1f}%)")

print(f"\nL_5EC7 unique outputs: {len(l5ec7_outputs)}")
print(f"Object table unique outputs: {len(object_table)}")

print("\n" + "=" * 70)
print("PER-VALUE CROSS-REFERENCE")
print("=" * 70)

matched_l5ec7 = 0
matched_object = 0
matched_wall = 0
unmatched = []

for bt in unique_bt:
    count = bt_counts[bt]
    card = bt & 0xFF
    color = (bt >> 8) & 0x07
    fg_bg = (bt >> 11) & 0x03
    
    sources = []
    if bt == WALL_PREFILL:
        sources.append("WALL_PREFILL")
        matched_wall += count
    
    if bt in l5ec7_outputs:
        sources.append(f"L_5EC7(grp={l5ec7_outputs[bt]})")
        matched_l5ec7 += count
    
    if bt in object_table:
        types = object_table[bt]
        floor_str = " [FLOOR]" if any(t <= 7 for t in types) else ""
        sources.append(f"OBJ_TABLE(types={types}){floor_str}")
        matched_object += count
    
    if not sources:
        unmatched.append(bt)
        sources.append("*** UNMATCHED ***")
    
    print(f"  ${bt:04X} (card=${card:02X} color={color} fg/bg={fg_bg}) x{count:3d}  <=  {', '.join(sources)}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"  Wall pre-fill ($1603):     {matched_wall:3d} cells")
print(f"  L_5EC7 (tile stream):      {matched_l5ec7:3d} cells (across {len([bt for bt in unique_bt if bt in l5ec7_outputs])} unique values)")
print(f"  Object table ($655E):       {matched_object:3d} cells (across {len([bt for bt in unique_bt if bt in object_table])} unique values)")
print(f"  UNMATCHED:                  {sum(bt_counts[bt] for bt in unmatched):3d} cells (across {len(unmatched)} unique values)")

if unmatched:
    print(f"\n  Unmatched values:")
    for bt in sorted(unmatched):
        card = bt & 0xFF
        color = (bt >> 8) & 0x07
        print(f"    ${bt:04X} (card=${card:02X} color={color})")

print("\n" + "=" * 70)
print("L_5EC7 FULL OUTPUT TABLE (all 64 groups)")
print("=" * 70)
for g in range(64):
    bt = l5ec7_simulate(g)
    card = bt & 0xFF
    color = (bt >> 8) & 0x07
    in_actual = "*** IN BACKTAB ***" if bt in bt_counts else ""
    print(f"  Group {g:2d}: ${bt:04X} (card=${card:02X} color={color}) {in_actual}")

print("\n" + "=" * 70)
print("OBJECT TABLE vs ACTUAL BACKTAB COMPARISON")
print("=" * 70)
for t in range(32):
    bt = rw(0x655E + t * 2)
    card = bt & 0xFF
    color = (bt >> 8) & 0x07
    in_actual = "*** IN BACKTAB ***" if bt in bt_counts else ""
    floor = " [FLOOR]" if t <= 7 else ""
    # Check if any BACKTAB value has same card but different color
    same_card = [abt for abt in unique_bt if (abt & 0xFF) == card and abt != bt]
    card_match = f"  SAME CARD as: {[f'${x:04X}' for x in same_card]}" if same_card else ""
    print(f"  Type {t:2d}: ${bt:04X} (card=${card:02X} color={color}){floor} {in_actual}{card_match}")
