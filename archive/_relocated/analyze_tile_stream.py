#!/usr/bin/env python3
"""Analyze the raw tile stream at $6D98 (room 0) and $6D86 (step trace)."""
import sys
sys.stdout.reconfigure(encoding='cp1252', errors='replace')

rom = open('Swords and Serpents.bin', 'rb').read()

def rw_be(addr):
    off = (addr - 0x5000) * 2
    if off + 1 >= len(rom):
        return 0
    return (rom[off] << 8) | rom[off + 1]

# Known BACKTAB words from room 0
room0_words = set()
with open('traces/rooms/render_room_0_out.txt') as f:
    in_bt = False
    for line in f:
        if '0200:' in line and '1603' in line:
            in_bt = True
        if in_bt and line.startswith('02') and ':' in line:
            parts = line.split()
            for p in parts[1:]:
                if p.endswith('*'):
                    p = p[:-1]
                if len(p) == 4:
                    try:
                        room0_words.add(int(p, 16))
                    except:
                        pass

# Dump the tile stream at $6D98 (room 0 SDBD entry 0)
print("=" * 70)
print("RAW TILE STREAM AT $6D98 (room 0, SDBD entry 0 with base $6D00)")
print("=" * 70)

stream_addr = 0x6D98
for offset in range(0, 128):
    addr = stream_addr + offset
    if addr >= 0x7000:
        break
    val = rw_be(addr)
    # Decode: is it a BACKTAB word? A tile index? A count?
    is_bt = val in room0_words
    is_floor = val == 0x1603
    tile_grp = val >> 5
    is_small = val <= 0x001F
    
    labels = []
    if is_bt:
        labels.append("BT_MATCH")
    if is_floor:
        labels.append("FLOOR")
    if is_small:
        labels.append("<=31")
    if not is_small and not is_bt:
        # Could be a tile index - show group
        labels.append(f"grp{tile_grp}")
    
    label_str = " ".join(labels) if labels else ""
    print(f"  [{offset:3d}] ${stream_addr+offset:04X}: ${val:04X} ({val:5d})  {label_str}")

# Dump the tile stream at $6D86 (from step trace)
print()
print("=" * 70)
print("RAW TILE STREAM AT $6D86 (step trace, SDBD entry 4)")
print("=" * 70)

stream_addr = 0x6D86
for offset in range(0, 128):
    addr = stream_addr + offset
    if addr >= 0x7000:
        break
    val = rw_be(addr)
    is_bt = val in room0_words
    is_small = val <= 0x001F
    tile_grp = val >> 5
    
    labels = []
    if is_bt:
        labels.append("BT_MATCH")
    if is_small:
        labels.append("<=31")
    if not is_small and not is_bt:
        labels.append(f"grp{tile_grp}")
    
    label_str = " ".join(labels) if labels else ""
    print(f"  [{offset:3d}] ${stream_addr+offset:04X}: ${val:04X} ({val:5d})  {label_str}")

# Now: for ALL unmatched BACKTAB words, check if they appear literally in the tile stream
print()
print("=" * 70)
print("UNMATCHED BACKTAB WORDS IN TILE STREAM?")
print("=" * 70)

# Get unmatched words
from solve_card_table import rw_be as _, attr, card_rom, intermediate, KNOWN_BT as _2
# Actually just read the tables directly
card_table = [rw_be(0x65A0 + i) for i in range(23)]
attr_table = [rw_be(0x65B7 + i) for i in range(24)]

def swap_byte(val):
    return ((val & 0xFF) << 8) | ((val >> 8) & 0xFF)

# Compute all L_5EC7 outputs
l5ec7_outputs = set()
for idx in range(23):
    attr0 = attr_table[idx]
    attr1 = attr_table[idx + 1]
    r1 = attr0 >> 2
    r1 = swap_byte(r1)
    r1 ^= attr1
    r1 &= 0x3607
    card_s3 = (card_table[idx] << 3) & 0xFFFF
    bt = r1 ^ card_s3
    l5ec7_outputs.add(bt)

unmatched = room0_words - l5ec7_outputs - {0x1603}
print(f"L_5EC7 produces {len(l5ec7_outputs)} words")
print(f"Room 0 has {len(room0_words)} unique words")
print(f"Unmatched non-floor words: {len(unmatched)}")

# Check if unmatched words appear in the tile stream
stream_addr = 0x6D98
stream_vals = set()
for offset in range(0, 256):
    addr = stream_addr + offset
    if addr >= 0x7000:
        break
    stream_vals.add(rw_be(addr))

found_in_stream = unmatched & stream_vals
print(f"\nUnmatched words found literally in $6D98 stream: {len(found_in_stream)}")
for w in sorted(found_in_stream):
    print(f"  ${w:04X}")

not_in_stream = unmatched - stream_vals
print(f"\nUnmatched words NOT in $6D98 stream: {len(not_in_stream)}")
for w in sorted(not_in_stream):
    print(f"  ${w:04X}")

# Also check: are the tile stream values in the range of L_5EC7 tile indices (0-736)?
# Since tile>>5 = group (0-22), tile range is 0-735
print()
print("=" * 70)
print("TILE STREAM VALUE DISTRIBUTION")
print("=" * 70)

stream_addr = 0x6D98
counts = {'<=31': 0, '32-255': 0, '256-735': 0, '736+': 0}
for offset in range(0, 256):
    addr = stream_addr + offset
    if addr >= 0x7000:
        break
    val = rw_be(addr)
    if val <= 31:
        counts['<=31'] += 1
    elif val <= 255:
        counts['32-255'] += 1
    elif val <= 735:  # max tile value: 22*32+31 = 735
        counts['256-735'] += 1
    else:
        counts['736+'] += 1

for k, v in counts.items():
    print(f"  {k}: {v}")
