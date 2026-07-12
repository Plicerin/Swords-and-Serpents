#!/usr/bin/env python3
"""
Complete simulation of L_5EE2 -> L_5EC7 rendering pipeline.
Corrected L_5EC7 algorithm with stateful attr table modification.

L_5EC7 algorithm:
  1. group = tile_value >> 5
  2. R3 = attr_base + group  (index into attr table)
  3. R5 = card_base + group  (index into card table)
  4. R1 = attr[group]        (read current attr)
  5. R1 >>= 2
  6. SWAP R1                 (swap bytes)
  7. R1 ^= attr[group]       (XOR with original attr)
  8. attr[group] = R1        (write back - STATE CHANGE!)
  9. R1 &= 0x3607
  10. R3 = card_table[group]
  11. R3 <<= 3
  12. R1 ^= R3
  13. Return R1 as BACKTAB word
"""

import sys
sys.stdout.reconfigure(encoding='cp1252', errors='replace')

rom = open('Swords and Serpents.bin', 'rb').read()

def rw(addr):
    off = (addr - 0x5000) * 2
    if off < 0 or off + 1 >= len(rom):
        return 0
    return (rom[off] << 8) | rom[off + 1]

def rb(addr):
    """Read low byte (SDBD style)"""
    off = (addr - 0x5000) * 2
    if off < 0 or off + 1 >= len(rom):
        return 0
    return rom[off + 1]

# ============================================================
# Read tables
# ============================================================

# Attr table at $65B7
attr_table_original = [rw(0x65B7 + i) for i in range(32)]

# Card table at $65A0
card_table = [rw(0x65A0 + i) for i in range(128)]

# $65CE index table (byte table)
tbl_65ce = [rb(0x65CE + i) for i in range(32)]

# Room pointer table at $65DC
room_ptr_tbl = [rw(0x65DC + i) for i in range(32)]

# ============================================================
# L_5EC7 simulation
# ============================================================
def sim_l5ec7(tile_val, attr_tbl, card_tbl):
    """Simulate L_5EC7 for a single tile value.
    Returns (backtab_word, new_attr_table)"""
    group = (tile_val >> 5) & 0x1F  # 0-31
    
    if group >= len(attr_tbl):
        # Out of range, return empty
        return 0
    
    a = attr_tbl[group]
    c = card_tbl[group] if group < len(card_tbl) else 0
    
    # Step 4-5: read attr, shift
    r1 = a
    r1 >>= 2
    
    # Step 6: SWAP byte halves
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    
    # Step 7: XOR with original attr
    r1 ^= a
    
    # Write back (state change!)
    attr_tbl[group] = r1 & 0xFFFF
    
    # Step 9: ANDI #$3607
    r1 &= 0x3607
    
    # Step 10-11: read card table, shift
    r3 = c
    r3 <<= 3
    r3 &= 0xFFFF
    
    # Step 12: XOR
    r1 ^= r3
    r1 &= 0xFFFF
    
    return r1

# ============================================================
# Test L_5EC7 with known tile values
# ============================================================
print("=== L_5EC7 SIMULATION (fresh attr table) ===")
print("Testing tile values 0-31 (group 0):")
test_attr = attr_table_original[:]
for t in range(8):
    bt = sim_l5ec7(t, test_attr, card_table)
    card = (bt >> 3) & 0x1FF
    gram = (bt >> 11) & 1
    fg = bt & 7
    src = 'GRAM' if gram else 'GROM'
    print(f"  tile={t:3d} (group=0, sub={t&31}) → ${bt:04X}: card={card:3d} {src} FG={fg}")
    if t == 7:
        print(f"  ... (attr[0] now = ${test_attr[0]:04X})")

# ============================================================
# Tile stream simulation
# ============================================================
# The tile stream for room 0 needs to be resolved.
# G_0175=2, G_0176=26 for room 0.
# L_5E48 uses these to index into the data.

# Let me trace L_5E48 for room 0:
# R0 = G_0176 = 26 ($1A)
# R2 = G_0175 = 2
# 
# R0 &= $30 → 26 & $30 = 16 ($10)
# R0 >>= 2 → 4
# R0 >>= 1 → 2
# R0 += G_02F4 → $65DC + 2 = $65DE
#
# R2 &= $60 → 2 & $60 = 0
# R2 >>= 2 → 0
# R2 >>= 2 → 0
# R2 >>= 1 → 0
# R3 = R2 = 0
# R3 >>= 1 → 0
# R3 += R0 → $65DE
# R0 = *R3 = word at $65DE
# R2 bit 0 = 0, so no shift
# R0 &= $F → nibble
#
# Then R4 = $65CE + R0 → index into byte table
# R2 = byte at $65CE+R0
#
# Then R0 restored, &= $F

# For room 0 first call:
# $65DE word = rw(0x65DE) = ?
w_65de = rw(0x65DE)
nibble = w_65de & 0xF
print(f"\n=== L_5E48 for room 0 ===")
print(f"  $65DE = ${w_65de:04X}, nibble = {nibble}")
byte_idx = tbl_65ce[nibble] if nibble < len(tbl_65ce) else 0
print(f"  tbl_65ce[{nibble}] = {byte_idx}")

# The byte at $65CE+nibble gives us... a tile stream offset?
# Let me check if it points to tile data
# Actually, looking at the code more carefully:
# After reading the byte, the code does:
#   PULR R0 (restore original R0 = G_0176 before ANDI)
#   ANDI #$000F, R0
#   TSTR R0
#   BEQ L_5E73  (skip if 0)
#   ADD@ R2, R2  (R2 += *R2, self-referencing!)
#   DECR R0
#   B L_5E6C
#
# This is a loop that adds offsets. R2 tracks the cumulative tile stream offset.
# The byte table at $65CE gives offsets.
# Then:
#   PULR R3
#   ANDI #$001F, R3
#   INCR R2
#   MVI@ R2, R0 (read tile stream byte)
#   ANDI #$001F, R0
#   SUBR R0, R3 → R3 -= R0 (run length check?)
#   NEGR R3
#   PULR R4; PULR R5 → return

# This is complex. Let me just try reading tile data from known ROM locations

# ============================================================
# Try to find the actual tile stream
# ============================================================
print("\n=== SEARCHING FOR TILE STREAM ===")
# The tile stream should contain run-length encoded room data
# Format: [tile_value] [run_count] ...
# Tile 0 (floor) appears most frequently

# Let me scan for plausible tile streams
# Room 0 has room_ptr_tbl[0] = $0042 (byte)
# But that's an index, not a pointer

# Let me look for the room data structure
# Previous analysis suggested data at $6D00-$6F00

# Let me try: $65CE table gives tile stream offsets
# For room 0, $65CE[nibble] might give the tile stream offset

# Actually let me take a completely different approach.
# Let me read what the room pointer table ACTUALLY contains
# and how L_5E48 uses it.

print("\n=== DECODING ROOM DATA STRUCTURE ===")
# G_02F4 = $65DC
# L_5E48 reads: byte at $65DC + (G_0176 bits 5-4)*2 + (G_0175 bits 6-5)/2
# Hmm, the indexing is complex. Let me just try all combinations.

# Actually, G_02F4 is variable. L_55BF sets it to $65DC initially.
# But L_5E48 might change it. Let me look at L_5E80...
# L_5E80 calls L_5E48 with modified R0 and R2:
# R2 = (G_0175 + 32) & $60
# R0 = G_0178

# For now, let me just try to find the tile stream empirically.
# I know room 0 BACKTAB has specific patterns.
# Let me scan ROM for byte sequences that look like run-length encoded tile data.

print("\nScanning ROM for run-length encoded tile patterns...")
# Tile 0 (floor) should be the most common
# Look for $0000 bytes followed by run length bytes
for addr in range(0x6D00, 0x7000, 0x10):
    data = [rb(addr + i) for i in range(32)]
    zeros = data.count(0)
    if zeros >= 4:
        print(f"  ${addr:04X}: {data[:16]} (zeros={zeros})")

# ============================================================
# NEW APPROACH: Use the tile stream at a known location
# Based on the basher output, $6D00 seems to have run-length data
# Format: each pair is (tile_value_byte, run_count_byte)
# ============================================================

print("\n=== PARSING TILE STREAM AT $6D00 ===")
# Read bytes as tile stream
raw_bytes = [rb(0x6D00 + i) for i in range(256)]
print(f"Raw bytes: {raw_bytes[:64]}")

# Try run-length decoding
# Tiles with value > 31 have special meaning
# Format: [tile_byte] [count_byte] for normal tiles
# For tile > 31: special handling

tiles = []
i = 0
while i < len(raw_bytes) - 1 and len(tiles) < 240:
    b = raw_bytes[i]
    if b > 0x1F:  # > 31, special
        # Could be a jump or special command
        i += 1
        continue
    count = raw_bytes[i+1] & 0x1F  # run count
    if count == 0:
        count = 32  # 0 means 32
    for _ in range(count):
        if len(tiles) < 240:
            tiles.append(b)
    i += 2

print(f"Decoded {len(tiles)} tiles")
if len(tiles) >= 20:
    print(f"First 20 tiles: {tiles[:20]}")

# ============================================================
# Now run L_5EC7 on each tile
# ============================================================
print("\n=== FULL BACKTAB CONSTRUCTION ===")
attr_state = attr_table_original[:]
backtab = []

for idx, t in enumerate(tiles[:240]):
    bt = sim_l5ec7(t, attr_state, card_table)
    backtab.append(bt)

# Show grid
print("\nSimulated BACKTAB grid (20x12):")
for row in range(12):
    line = ""
    for col in range(20):
        idx = row * 20 + col
        if idx < len(backtab):
            bt = backtab[idx]
            card = (bt >> 3) & 0x1FF
            if card == 0:
                line += ".... "
            else:
                line += f"${bt:04X} "
        else:
            line += "???? "
    print(f"  R{row:2d}: {line}")

# Count non-floor
non_floor_sim = {}
for idx, bt in enumerate(backtab[:240]):
    card = (bt >> 3) & 0x1FF
    if card != 0:
        if bt not in non_floor_sim:
            non_floor_sim[bt] = []
        non_floor_sim[bt].append(idx)

print(f"\nSimulated non-floor words ({len(non_floor_sim)} unique):")
for bt in sorted(non_floor_sim.keys()):
    pos = non_floor_sim[bt]
    card = (bt >> 3) & 0x1FF
    gram = (bt >> 11) & 1
    fg = bt & 7
    src = 'GRAM' if gram else 'GROM'
    pos_str = ', '.join(f"({p//20},{p%20})" for p in pos[:5])
    if len(pos) > 5:
        pos_str += f" +{len(pos)-5}"
    print(f"  ${bt:04X}: card={card:3d} {src:4s} FG={fg} at {pos_str}")

# ============================================================
# Compare with actual room 0
# ============================================================
print("\n=== COMPARISON WITH KNOWN ROOM 0 ===")
try:
    room0_bt = []
    with open('traces/rooms/render_room_0_out.txt') as f:
        in_bt = False
        for line in f:
            if '0200:' in line:
                in_bt = True
            if in_bt and line.strip():
                parts = line.split()
                for p in parts[1:]:
                    p = p.rstrip('*')
                    if len(p) == 4:
                        try:
                            room0_bt.append(int(p, 16))
                        except:
                            pass
                if line.startswith('02F0:'):
                    break
        if len(room0_bt) > 240:
            room0_bt = room0_bt[:240]
    
    if len(room0_bt) >= 240 and len(backtab) >= 240:
        matches = sum(1 for i in range(240) if room0_bt[i] == backtab[i])
        print(f"Matches: {matches}/240 ({matches*100//240}%)")
        
        # Show differences
        diffs = 0
        for i in range(240):
            if room0_bt[i] != backtab[i]:
                r, c = i // 20, i % 20
                if diffs < 20:
                    print(f"  [{i:3d}] ({r},{c}): actual=${room0_bt[i]:04X}  sim=${backtab[i]:04X}")
                diffs += 1
        if diffs > 20:
            print(f"  ... and {diffs-20} more differences")
    else:
        print(f"Room 0: {len(room0_bt)} tiles, Sim: {len(backtab)} tiles")
except Exception as e:
    print(f"Could not compare: {e}")

# ============================================================
# Try different tile stream sources
# ============================================================
print("\n=== TRYING ALTERNATIVE TILE STREAM SOURCES ===")
for stream_addr in [0x6D80, 0x6D98, 0x6E00, 0x6E80, 0x6F00]:
    raw_bytes = [rb(stream_addr + i) for i in range(256)]
    
    # Decode run-length
    tiles = []
    i = 0
    while i < len(raw_bytes) - 1 and len(tiles) < 240:
        b = raw_bytes[i]
        if b > 0x1F:
            i += 1
            continue
        count = raw_bytes[i+1] & 0x1F
        if count == 0:
            count = 32
        for _ in range(count):
            if len(tiles) < 240:
                tiles.append(b)
        i += 2
    
    if len(tiles) < 240:
        continue
    
    # Simulate
    attr_state = attr_table_original[:]
    backtab = []
    for t in tiles[:240]:
        bt = sim_l5ec7(t, attr_state, card_table)
        backtab.append(bt)
    
    if len(room0_bt) >= 240:
        matches = sum(1 for i in range(240) if room0_bt[i] == backtab[i])
        print(f"  Stream at ${stream_addr:04X}: {len(tiles)} tiles, {matches}/240 matches ({matches*100//240}%)")
    else:
        print(f"  Stream at ${stream_addr:04X}: {len(tiles)} tiles decoded")
