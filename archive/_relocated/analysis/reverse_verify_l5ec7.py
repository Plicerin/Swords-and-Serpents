#!/usr/bin/env python3
"""
Empirical Reverse Verification of L_5EC7
========================================
Works backward from known BACKTAB words to verify the algorithm.

For each BACKTAB word (excluding $1603 floor):
  For each card table entry (0-22):
    intermediate = BT ^ (card[idx] << 3)
    if intermediate has NO bits outside the $3607 mask → valid candidate
    Check if any attr pair produces this intermediate
"""

import sys
sys.stdout.reconfigure(encoding='cp1252', errors='replace')

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

def rw_be(addr):
    off = (addr - 0x5000) * 2
    if off + 1 >= len(rom):
        return 0
    return (rom[off] << 8) | rom[off + 1]

def swap_byte(val):
    return ((val & 0xFF) << 8) | ((val >> 8) & 0xFF)

def l5ec7_forward(tile_value, attr_table, card_table):
    """Original L_5EC7 simulation"""
    idx = tile_value >> 5
    if idx >= 23:
        idx = 22
    attr0 = attr_table[idx]
    r1 = attr0 >> 2
    r1 = swap_byte(r1)
    attr1 = attr_table[idx + 1]
    r1 ^= attr1
    r1 &= 0x3607
    card = card_table[idx]
    card_shifted = (card << 3) & 0xFFFF
    r1 ^= card_shifted
    return r1 & 0xFFFF

# Read tables
card_table = [rw_be(0x65A0 + i) for i in range(23)]
attr_table = [rw_be(0x65B7 + i) for i in range(24)]

# Compute all possible attr intermediates (attr0>>2, SWAP, XOR attr1, & $3607)
attr_intermediates = {}
for idx in range(23):
    attr0 = attr_table[idx]
    attr1 = attr_table[idx + 1]
    r1 = attr0 >> 2
    r1 = swap_byte(r1)
    r1 ^= attr1
    r1 &= 0x3607
    if r1 not in attr_intermediates:
        attr_intermediates[r1] = []
    attr_intermediates[r1].append(idx)

print("=" * 70)
print("REVERSE VERIFICATION OF L_5EC7")
print("=" * 70)

# Read room 0 BACKTAB dump
room0_words = {}
with open('traces/rooms/render_room_0_out.txt') as f:
    in_bt = False
    addr = 0x0200
    for line in f:
        if '0200:' in line and '1603' in line:
            in_bt = True
        if in_bt and line.startswith('02') and ':' in line:
            parts = line.split()
            addr_str = parts[0].replace(':', '')
            try:
                addr = int(addr_str, 16)
            except:
                continue
            for p in parts[1:]:
                if p.endswith('*'):
                    p = p[:-1]
                if len(p) == 4:
                    try:
                        val = int(p, 16)
                        if addr <= 0x02EF:
                            room0_words[addr] = val
                            addr += 1
                    except:
                        pass

print(f"\nRoom 0 BACKTAB: {len(room0_words)} tiles ($0200-$02EF)")

# Unique BACKTAB words
unique_bt = sorted(set(room0_words.values()))
print(f"Unique BACKTAB words: {len(unique_bt)}")

# Count $1603 floor tiles
floor_count = sum(1 for v in room0_words.values() if v == 0x1603)
print(f"Floor tiles ($1603): {floor_count}/{len(room0_words)}")

# Non-floor words
non_floor = [w for w in unique_bt if w != 0x1603]
print(f"Non-floor unique words: {len(non_floor)}")

print("\n" + "=" * 70)
print("FOR EACH NON-FLOOR BACKTAB WORD: FIND MATCHING TILE GROUP")
print("=" * 70)

# For each non-floor BACKTAB word, find which tile groups could produce it
print(f"\n{'BT Word':>8} {'CardIdx':>8} {'Card':>6} {'<<3':>6} {'Intermed':>8} {'MaskOK':>7} {'AttrIdx':>8} {'TileGrp':>8} {'TileVal':>8}")
print("-" * 90)

matched_words = set()
unmatched_words = set()

for bt_word in sorted(non_floor):
    found_any = False
    for idx in range(23):
        card = card_table[idx]
        card_s3 = (card << 3) & 0xFFFF
        intermediate = bt_word ^ card_s3
        
        # Check: does intermediate only have bits within $3607 mask?
        mask_ok = (intermediate & ~0x3607) == 0
        
        if mask_ok:
            # Check if this intermediate matches any attr pair
            attr_matches = attr_intermediates.get(intermediate, [])
            for attr_idx in attr_matches:
                tile_val_lo = idx << 5
                tile_val_hi = tile_val_lo + 31
                print(f" ${bt_word:04X}     {idx:2d}     ${card:04X}  ${card_s3:04X}  ${intermediate:04X}     {'YES':>5}     {attr_idx:2d}     {idx:2d}      ${tile_val_lo:04X}-${tile_val_hi:04X}")
                found_any = True
                matched_words.add(bt_word)
    
    if not found_any:
        unmatched_words.add(bt_word)
        # Show ALL card table attempts for debugging
        print(f" ${bt_word:04X}  --- NO MATCH FOUND ---")
        for idx in range(23):
            card = card_table[idx]
            card_s3 = (card << 3) & 0xFFFF
            intermediate = bt_word ^ card_s3
            mask_ok = (intermediate & ~0x3607) == 0
            if mask_ok:
                print(f"       idx={idx:2d}: card=${card:04X}<<3=${card_s3:04X} intermed=${intermediate:04X} maskOK but no attr match")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"  Matched BACKTAB words:   {len(matched_words)}/{len(non_floor)}")
print(f"  Unmatched BACKTAB words: {len(unmatched_words)}/{len(non_floor)}")

if unmatched_words:
    print(f"\n  Unmatched words:")
    for w in sorted(unmatched_words):
        # Show what card table entries WOULD produce a valid intermediate
        print(f"    ${w:04X}: ", end="")
        candidates = []
        for idx in range(23):
            card_s3 = (card_table[idx] << 3) & 0xFFFF
            intermed = w ^ card_s3
            if (intermed & ~0x3607) == 0:
                candidates.append(f"idx={idx}(im=${intermed:04X})")
        if candidates:
            print(f"mask-valid intermediates: {', '.join(candidates)}")
        else:
            print(f"NO mask-valid intermediate exists — this word CANNOT be from L_5EC7 with current tables!")

print("\n" + "=" * 70)
print("MATCHED BACKTAB WORDS WITH THEIR TILE GROUPS")
print("=" * 70)
for bt in sorted(matched_words):
    print(f"  ${bt:04X}: ", end="")
    groups = []
    for idx in range(23):
        card_s3 = (card_table[idx] << 3) & 0xFFFF
        intermed = bt ^ card_s3
        if (intermed & ~0x3607) == 0 and intermed in attr_intermediates:
            groups.append(idx)
    print(f"tile groups {groups}, tile values ${groups[0]<<5:04X}-${(groups[0]<<5)+31:04X}" if groups else "none")

print("\n" + "=" * 70)
print("FORWARD SIMULATION (all 23 groups)")
print("=" * 70)
for idx in range(23):
    attr0 = attr_table[idx]
    attr1 = attr_table[idx + 1]
    r1 = attr0 >> 2
    r1 = swap_byte(r1)
    r1 ^= attr1
    r1 &= 0x3607
    card_s3 = (card_table[idx] << 3) & 0xFFFF
    bt = r1 ^ card_s3
    in_room0 = "✓ IN ROOM 0" if bt in room0_words.values() else ""
    tile_lo = idx << 5
    tile_hi = tile_lo + 31
    print(f"  Group {idx:2d}: tile ${tile_lo:04X}-${tile_hi:04X} → attr={attr0:04X}/{attr1:04X} im=${r1:04X} card={card_table[idx]:04X}<<3={card_s3:04X} → BT=${bt:04X} {in_room0}")

# Count room0 matches
room0_match_count = sum(1 for idx in range(23) if l5ec7_forward(idx << 5, attr_table, card_table) in room0_words.values())
print(f"\n  {room0_match_count}/23 groups produce BACKTAB words found in room 0")
