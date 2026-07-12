#!/usr/bin/env python3
"""Analyze the $655E BACKTAB word table and $6580 card index table used by L_63B9."""
import sys
sys.stdout.reconfigure(encoding='cp1252', errors='replace')

rom = open('Swords and Serpents.bin', 'rb').read()

def rw_be(addr):
    off = (addr - 0x5000) * 2
    if off + 1 >= len(rom):
        return 0
    return (rom[off] << 8) | rom[off + 1]

# BACKTAB word table at $655E (used by L_63B9 for index > 7)
# Each entry is a 16-bit BACKTAB word
print("=" * 70)
print("BACKTAB WORD TABLE at $655E")
print("=" * 70)
print("Used by L_63B9: R4 = $655E + index*2, then MVI@ R4,R0 writes to BACKTAB")
print()
bt_table = {}
for i in range(32):
    addr = 0x655E + i * 2
    w = rw_be(addr)
    bt_table[i] = w
    
    # Decode
    card = (w >> 3) & 0xFF
    gram = 'GRAM' if w & 0x0800 else 'GROM'
    fg = ((w >> 13) & 0x6) | ((w >> 12) & 1) | (w & 7)
    cs = (w >> 13) & 1
    print(f"  [{i:2d}] ${addr:04X}: ${w:04X}  card={card:3d} {gram:4s} FG={fg} CS={cs}")

# Card index table at $6580
# Each entry maps an object type to a card index (0-31)
print()
print("=" * 70)
print("CARD INDEX TABLE at $6580")
print("=" * 70)
for i in range(32):
    addr = 0x6580 + i
    v = rw_be(addr)
    if v & 0xFF00:
        # Maybe a complex entry
        print(f"  [{i:2d}] ${addr:04X}: ${v:04X} ({v})  [complex]")
    else:
        idx = v & 0x1F
        if idx in bt_table:
            bt = bt_table[idx]
            card = (bt >> 3) & 0xFF
            gram = 'GRAM' if bt & 0x0800 else 'GROM'
            fg = bt & 7
            print(f"  [{i:2d}] ${addr:04X}: ${v:04X} -> idx={idx} -> BT=${bt:04X} card={card} {gram} FG={fg}")
        else:
            print(f"  [{i:2d}] ${addr:04X}: ${v:04X} -> idx={idx}")

# Object table at $64DE (16 entries, each 2 words)
# First word = encoded Y, second = encoded X?
print()
print("=" * 70)
print("OBJECT TABLE at $64DE (16 entries)")
print("=" * 70)
for i in range(16):
    addr = 0x64DE + i * 2
    w0 = rw_be(addr)
    w1 = rw_be(addr + 1)
    print(f"  [{i:2d}] ${addr:04X}: Y=${w0:04X} ({w0:3d}), X=${w1:04X} ({w1:3d})")

# Now cross-reference: which BACKTAB words from $655E table appear in room 0?
print()
print("=" * 70)
print("CROSS-REFERENCE: $655E WORDS IN ROOM 0 BACKTAB")
print("=" * 70)

# Read room 0 BACKTAB
room0_grid = []
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
                        room0_grid.append(int(p, 16))
                    except:
                        pass
            if line.startswith('02F0:'):
                break

room0_set = set(room0_grid)

bt_table_set = set(bt_table.values())
in_room0 = bt_table_set & room0_set
not_in_room0 = bt_table_set - room0_set

print(f"BT table has {len(bt_table_set)} unique words")
print(f"Room 0 uses {len(in_room0)} of them")
print()
print("Words in both BT table and room 0:")
for w in sorted(in_room0):
    card = (w >> 3) & 0xFF
    gram = 'GRAM' if w & 0x0800 else 'GROM'
    fg = ((w >> 13) & 0x6) | ((w >> 12) & 1) | (w & 7)
    # Find which positions
    positions = [(r, c) for r in range(12) for c in range(20) if r*20+c < len(room0_grid) and room0_grid[r*20+c] == w]
    print(f"  ${w:04X} card={card:3d} {gram} FG={fg}  at positions: {positions}")

print()
print("Words in BT table but NOT in room 0:")
for w in sorted(not_in_room0):
    card = (w >> 3) & 0xFF
    gram = 'GRAM' if w & 0x0800 else 'GROM'
    fg = ((w >> 13) & 0x6) | ((w >> 12) & 1) | (w & 7)
    # Find which table indices produce this
    indices = [i for i, v in bt_table.items() if v == w]
    print(f"  ${w:04X} card={card:3d} {gram} FG={fg}  (indices: {indices})")

# KEY QUESTION: Do the unmatched room 0 words all appear in this BT table?
l5ec7_outputs = set()
def swap_byte(val):
    return ((val & 0xFF) << 8) | ((val >> 8) & 0xFF)
card_t = [rw_be(0x65A0 + i) for i in range(23)]
attr_t = [rw_be(0x65B7 + i) for i in range(24)]
for idx in range(23):
    attr0 = attr_t[idx]
    attr1 = attr_t[idx + 1]
    r1 = attr0 >> 2
    r1 = swap_byte(r1)
    r1 ^= attr1
    r1 &= 0x3607
    card_s3 = (card_t[idx] << 3) & 0xFFFF
    l5ec7_outputs.add(r1 ^ card_s3)

unmatched = room0_set - l5ec7_outputs - {0x1603}
explained = unmatched & bt_table_set
unexplained = unmatched - bt_table_set

print()
print(f"Room 0 words not from L_5EC7: {len(unmatched)}")
print(f"  Explained by $655E BT table: {len(explained)}")
print(f"  Still unexplained: {len(unexplained)}")
if explained:
    print(f"  Explained words:")
    for w in sorted(explained):
        card = (w >> 3) & 0xFF
        gram = 'GRAM' if w & 0x0800 else 'GROM'
        fg = ((w >> 13) & 0x6) | ((w >> 12) & 1) | (w & 7)
        positions = [(r, c) for r in range(12) for c in range(20) if r*20+c < len(room0_grid) and room0_grid[r*20+c] == w]
        print(f"    ${w:04X} card={card:3d} {gram} FG={fg}  at {positions}")
if unexplained:
    print(f"  Unexplained words:")
    for w in sorted(unexplained):
        card = (w >> 3) & 0xFF
        gram = 'GRAM' if w & 0x0800 else 'GROM'
        fg = ((w >> 13) & 0x6) | ((w >> 12) & 1) | (w & 7)
        positions = [(r, c) for r in range(12) for c in range(20) if r*20+c < len(room0_grid) and room0_grid[r*20+c] == w]
        print(f"    ${w:04X} card={card:3d} {gram} FG={fg}  at {positions}")
