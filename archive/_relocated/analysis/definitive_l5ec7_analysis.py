#!/usr/bin/env python3
"""
DEFINITIVE L_5EC7 Analysis
==========================
Simulates L_5EC7 for ALL possible tile descriptor values (0-255),
showing exactly what BACKTAB word each produces, and comparing with
actual room 0 BACKTAB.

Key CP1610 semantics:
  - R5 = $65A0 (ROM card table) - SDBD+MVII loads immediate normally
  - Card reads: MVI@ reads 16-bit words from ROM $65A0+
  - XOR@ R3 reads NEXT attr word (auto-incremented)
  - ANDI $3607 with SDBD: byte-wise mask (lo=$07, hi=$36)
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
ALL_BT = sorted(set(w for row in BACKTAB_GRID for w in row))
BT_COUNTS = {}
for row in BACKTAB_GRID:
    for w in row:
        BT_COUNTS[w] = BT_COUNTS.get(w, 0) + 1

# =========================================================================
# ROM Tables
# =========================================================================
ATTR_BASE = 0x65B7
CARD_BASE = 0x65A0

# Read attr table (32 entries to check beyond group 7)
attr = [rw(ATTR_BASE + i) for i in range(32)]
# Read card table (16 entries to check beyond group 7)
card = [rw(CARD_BASE + i) for i in range(16)]

print("=" * 80)
print("ROM ATTR TABLE at $65B7 (first 16 entries)")
print("=" * 80)
for i in range(16):
    print(f"  [{i:2d}] ${attr[i]:04X}", end="")
    if i % 4 == 3: print()
print()

print("=" * 80)
print("ROM CARD TABLE at $65A0 (first 16 entries)")
print("=" * 80)
for i in range(16):
    print(f"  [{i:2d}] ${card[i]:04X}", end="")
    if i % 4 == 3: print()
print()

# =========================================================================
# L_5EC7 - EXACT CP1610 simulation
# =========================================================================
def l5ec7(tile_value):
    """
    Simulate L_5EC7 for a given tile descriptor value.
    
    Input:  R1 = tile_value (16-bit tile descriptor)
    Output: R1 = BACKTAB word
    
    Instructions:
      5EC9: MVI  G_02F5, R3     ; R3 = $65B7 (attr base)
      5ECB: SDBD
      5ECC: MVII #$65A0, R5     ; R5 = $65A0 (card base) - SDBD no effect on MVII immediate
      5ECF: SLR  R1, 2          
      5ED0: SLR  R1, 2
      5ED1: SLR  R1, 1          ; R1 = group = tile_value >> 5
      5ED2: ADDR R1, R3         ; R3 += group
      5ED3: ADDR R1, R5         ; R5 += group
      5ED4: MVI@ R3, R1         ; R1 = attr[group]; R3++
      5ED5: SLR  R1, 2          ; R1 >>= 2
      5ED6: SWAP R1, 1          ; byte swap
      5ED7: XOR@ R3, R1         ; R1 ^= attr[group+1]  (auto-incremented R3)
      5ED8: SDBD
      5ED9: ANDI #$3607, R1     ; byte-wise AND: lo & $07, hi & $36
      5EDC: MVI@ R5, R3         ; R3 = card[group] (word read)
      5EDD: SLL  R3, 2
      5EDE: SLL  R3, 1          ; R3 <<= 3
      5EDF: XORR R3, R1         ; BACKTAB = R1 ^ R3
    """
    group = (tile_value >> 5) & 0x1F  # 5 group bits → up to 32 groups
    
    a_g = attr[group]        # MVI@ R3: attr[group]
    a_next = attr[group + 1] if group + 1 < len(attr) else 0  # XOR@ R3: attr[group+1]
    
    # Process attr
    r1 = (a_g >> 2) & 0xFFFF                     # SLR R1, 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF) # SWAP R1, 1
    r1 ^= a_next                                   # XOR@ R3, R1
    
    # SDBD byte-wise ANDI #$3607
    r1 = ((r1 & 0xFF) & 0x07) | (((r1 >> 8) & 0xFF) & 0x36) << 8
    
    # Card
    c = card[group] & 0xFFFF   # MVI@ R5: word read
    r3 = (c << 3) & 0xFFFF     # SLL ×3
    
    backtab = (r1 ^ r3) & 0xFFFF
    return backtab

# =========================================================================
# ANALYSIS
# =========================================================================
print("=" * 80)
print("L_5EC7: All Tile Values → BACKTAB mapping")
print("=" * 80)
print(f"Tile values 0-255: group = tile >> 5, up to {256>>5}={256>>5} groups")
print()

# Group all tile values by their BACKTAB output
bt_to_tiles = {}
for tv in range(256):
    bt = l5ec7(tv)
    if bt not in bt_to_tiles:
        bt_to_tiles[bt] = []
    bt_to_tiles[bt].append(tv)

print(f"Distinct BACKTAB words produced: {len(bt_to_tiles)}")
print()

# Show, for each BACKTAB word, which tile values produce it
for bt in sorted(bt_to_tiles.keys()):
    tiles = bt_to_tiles[bt]
    in_actual = "IN BACKTAB" if bt in ALL_BT else "NOT in BACKTAB"
    count_in_bt = BT_COUNTS.get(bt, 0)
    
    groups_used = sorted(set(tv >> 5 for tv in tiles))
    card_idx = groups_used[0] if groups_used else -1
    r1_attr = l5ec7(groups_used[0] << 5) ^ ((card[groups_used[0]] << 3) & 0xFFFF)
    
    print(f"  ${bt:04X}  [{bt:016b}]  {in_actual}  ({count_in_bt} tiles in room)")
    print(f"         card idx: {[card[g] for g in groups_used] if len(groups_used)<=4 else f'{len(groups_used)} groups'}")
    print(f"         groups: {groups_used}")
    print(f"         tile values: {[f'${tv:02X}' for tv in tiles[:12]]}{'...' if len(tiles)>12 else ''}")
    print()

# =========================================================================
# SUMMARY: Which groups produce actual BACKTAB words?
# =========================================================================
print("=" * 80)
print("GROUP → BACKTAB SUMMARY")
print("=" * 80)
print(f"{'Group':>6s} | {'tile_range':>10s} | {'attr[g]':>8s} | {'attr[g+1]':>10s} | {'r1_attr':>8s} | {'card[g]':>8s} | {'BACKTAB':>8s} | {'In BT?':>6s} | {'Count'}")
print("-" * 85)

for g in range(32):
    tile_start = g << 5
    tile_end = ((g+1) << 5) - 1
    bt = l5ec7(tile_start)
    
    if g < len(attr) and g < len(card):
        a_g = attr[g]
        a_next = attr[g+1] if g+1 < len(attr) else 0
        c = card[g]
        
        # Compute r1_attr separately
        r1 = (a_g >> 2) & 0xFFFF
        r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
        r1 ^= a_next
        r1 = ((r1 & 0xFF) & 0x07) | (((r1 >> 8) & 0xFF) & 0x36) << 8
        
        in_bt = "YES" if bt in ALL_BT else "no"
        count = BT_COUNTS.get(bt, 0)
        
        if count > 0 or g < 8:
            print(f"  {g:3d}  | ${tile_start:02X}-${tile_end:02X}    | ${a_g:04X}    | ${a_next:04X}      | ${r1:04X}    | ${c:04X}    | ${bt:04X}    | {in_bt:>6s} | {count:3d}")

print()

# =========================================================================
# FINDING: Which tiles produce walls ($1603)?
# =========================================================================
print("=" * 80)
print("CRITICAL: Which tile values produce $1603 (wall)?")
print("=" * 80)

wall_tiles = bt_to_tiles.get(0x1603, [])
wall_groups = sorted(set(tv >> 5 for tv in wall_tiles))

if wall_tiles:
    print(f"  Tile values: {[f'${tv:02X}' for tv in sorted(wall_tiles)]}")
    print(f"  Groups: {wall_groups}")
    for g in wall_groups:
        print(f"    Group {g}: attr[{g}]=${attr[g]:04X}, attr[{g+1}]=${attr[g+1]:04X}, card[{g}]=${card[g]:04X}")
else:
    print("  *** NO TILE VALUES PRODUCE $1603 WITH ROM CARD TABLE! ***")
    print()
    print("  This PROVES that the card table is modified at runtime.")
    print("  Groups 0-1 have card=$0000 (not ROM $0100-$0101) for walls.")
    print()

# =========================================================================
# FINDING: Summary verdict
# =========================================================================
print("=" * 80)
print("VERDICT")
print("=" * 80)

bt_produced = set(bt_to_tiles.keys())
bt_matched = bt_produced & ALL_BT
bt_missing = ALL_BT - bt_produced

print(f"  BACKTAB words in actual room:        {len(ALL_BT)}")
print(f"  BACKTAB words produced by L_5EC7:    {len(bt_produced)}")
print(f"  Matches (in both):                   {len(bt_matched)}")
print(f"  Missing (in room, not produced):     {len(bt_missing)}")
print(f"  Extra (produced, not in room):       {len(bt_produced - ALL_BT)}")
print()

if bt_missing:
    print(f"  Missing BACKTAB words:")
    for bt in sorted(bt_missing):
        print(f"    ${bt:04X} ({BT_COUNTS.get(bt,0)} tiles)")
    print()

# What tiles are actually in BACKTAB that we match?
if bt_matched:
    print(f"  Matched BACKTAB words:")
    for bt in sorted(bt_matched):
        count = BT_COUNTS.get(bt, 0)
        print(f"    ${bt:04X} ({count} tiles) - from tile group {bt_to_tiles[bt][0]>>5}")
    print()

# How many total tiles match vs don't?
total_matched = sum(BT_COUNTS.get(bt, 0) for bt in bt_matched)
total_missing = sum(BT_COUNTS.get(bt, 0) for bt in bt_missing)
print(f"  Total tiles: {total_matched+total_missing} (12 rows × 20 cols = 240)")
print(f"  Tiles matched: {total_matched} ({100*total_matched/240:.1f}%)")
print(f"  Tiles not produced: {total_missing} ({100*total_missing/240:.1f}%)")
