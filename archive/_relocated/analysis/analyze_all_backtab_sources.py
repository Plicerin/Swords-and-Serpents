import sys
sys.stdout.reconfigure(encoding='cp1252', errors='replace')

rom = open('Swords and Serpents.bin', 'rb').read()

def rw_be(addr):
    off = (addr - 0x5000) * 2
    if off + 1 >= len(rom):
        return 0
    return (rom[off] << 8) | rom[off + 1]

# ============================================================
# 1. Read ALL entries in the $655E BACKTAB word table
#    L_63EC: ADDI #$655E, R4, then MVI@ R4, R0, then MVO@ R0, R5
#    R4 starts at index*2 offset from $655E
# ============================================================
print("=== $655E BACKTAB WORD TABLE (128 words to be safe) ===")
bt_table = {}
for i in range(128):
    addr = 0x655E + i
    w = rw_be(addr)
    card = (w >> 3) & 0x1FF
    gram = (w >> 11) & 1
    fg = w & 7
    cs = (w >> 13) & 1
    src = 'GRAM' if gram else 'GROM'
    bt_table[i] = w
    if w != 0xFFFF and w != 0x0000:
        print(f"  [{i:3d}] ${addr:04X}: ${w:04X}  card={card:3d} {src:4s} FG={fg} CS={cs}")

# ============================================================
# 2. Read $6580 card index table (used by L_63B9/L_6394)
#    Each entry is a byte with a 5-bit index into $655E table
# ============================================================
print("\n=== $6580 CARD INDEX TABLE (64 bytes to be safe) ===")
for i in range(64):
    addr = 0x6580 + i
    w = rw_be(addr)
    # Low nibble or full byte?
    idx5 = w & 0x1F
    hi = (w >> 5) & 0x1F
    if w != 0xFFFF and w != 0x0000:
        print(f"  [{i:3d}] ${addr:04X}: ${w:04X}  lo5={idx5} hi5={hi}")

# ============================================================
# 3. Read $64DE object table (16 objects × 2 words each = Y, X)
# ============================================================
print("\n=== $64DE OBJECT TABLE ===")
objects = []
for i in range(16):
    addr = 0x64DE + i * 2
    y = rw_be(addr)
    x = rw_be(addr + 1)
    objects.append((y, x))
    print(f"  [{i:2d}] ${addr:04X}: Y=${y:04X} ({y}), X=${x:04X} ({x})")

# ============================================================
# 4. L_5EC7 analysis: what tile groups produce what BACKTAB words
# ============================================================
print("\n=== L_5EC7 TILE GROUP → BACKTAB WORD SIMULATION ===")

# Read attribute table at $65B7 (23 entries, indexed 0-22)
# But first let's check what data L_5EC7 actually uses
# L_5EC7: MVI G_02F5, R3  -- G_02F5 was set to $65B7
#         MVII #$65A0, R5 -- card table base
#         SLR R1, 2; SLR R1, 2; SLR R1, 1  -- R1 = tile_group >> 5
#         MVI@ R3, R0  -- read attr[group]
#         SDBD; ADD@ R5, R0  -- add card_table[attr >> 10] or similar

# Actually, let me re-read the L_5EC7 code path more carefully
# R1 = raw tile value (read from tile stream)
# R1 >>= 5  (SLR x2 then SLR x1, but that's 5 shifts: SLR 2, SLR 2, SLR 1 = 5)
# So group = R1 >> 5 = R1 / 32
# Then attr[group] is read from G_02F5 ($65B7)

# Read attr table (24 entries)
print("Attr table at $65B7:")
attr = []
for i in range(24):
    a = rw_be(0x65B7 + i)
    attr.append(a)
    print(f"  [{i:2d}] ${a:04X} (raw), bits: {a:016b}")

# Card table at $65A0
print("\nCard table at $65A0:")
card_tbl = []
for i in range(24):
    c = rw_be(0x65A0 + i)
    card_tbl.append(c)
    print(f"  [{i:2d}] ${c:04X} (raw)")

# ============================================================
# 5. Cross-reference: room 0 BACKTAB words
# ============================================================
print("\n=== ROOM 0 BACKTAB CROSS-REFERENCE ===")

# Read room 0 from the dump
room0 = []
try:
    with open('traces/rooms/render_room_0_out.txt') as f:
        in_bt = False
        for line in f:
            if '0200:' in line:
                in_bt = True
            if in_bt and line.strip() and len(line) > 5:
                parts = line.split()
                for p in parts[1:]:
                    p = p.rstrip('*')
                    if len(p) == 4:
                        try:
                            room0.append(int(p, 16))
                        except:
                            pass
                if line.startswith('02F0:'):
                    break
        if len(room0) > 240:
            room0 = room0[:240]
except:
    print("Could not read room 0 dump")

print(f"Room 0 tiles: {len(room0)}")

# Identify non-floor tiles
non_floor = {}
for i, bt in enumerate(room0[:240]):
    card = (bt >> 3) & 0x1FF
    if card != 0:  # non-floor
        row = i // 20
        col = i % 20
        if bt not in non_floor:
            non_floor[bt] = []
        non_floor[bt].append((row, col))

print(f"\nNon-floor BACKTAB words ({len(non_floor)} unique):")
for bt in sorted(non_floor.keys()):
    positions = non_floor[bt]
    card = (bt >> 3) & 0x1FF
    gram = (bt >> 11) & 1
    fg = bt & 7
    cs = (bt >> 13) & 1
    src = 'GRAM' if gram else 'GROM'
    print(f"  ${bt:04X}: card={card:3d} {src:4s} FG={fg} CS={cs} at {positions[:5]}{'...' if len(positions) > 5 else ''}")

# ============================================================
# 6. Check which non-floor words appear in $655E table
# ============================================================
print("\n=== MATCHING ROOM 0 WORDS AGAINST $655E TABLE ===")
bt_table_values = set(bt_table.values())
matched_in_table = []
unmatched_in_table = []
for bt in sorted(non_floor.keys()):
    if bt in bt_table_values:
        matched_in_table.append(bt)
    else:
        unmatched_in_table.append(bt)

print(f"Matched in $655E: {len(matched_in_table)}")
for bt in matched_in_table:
    positions = non_floor[bt]
    card = (bt >> 3) & 0x1FF
    fg = bt & 7
    print(f"  ${bt:04X}: card={card:3d} FG={fg} at {positions}")

print(f"\nNOT in $655E: {len(unmatched_in_table)}")
for bt in unmatched_in_table:
    positions = non_floor[bt]
    card = (bt >> 3) & 0x1FF
    gram = (bt >> 11) & 1
    fg = bt & 7
    cs = (bt >> 13) & 1
    src = 'GRAM' if gram else 'GROM'
    print(f"  ${bt:04X}: card={card:3d} {src:4s} FG={fg} CS={cs} at {positions[:5]}{'...' if len(positions) > 5 else ''}")

# ============================================================
# 7. NEW HYPOTHESIS: Could the unmatched words be placed
#    by a completely separate rendering pass? E.g., wall/barrier
#    data that's pre-computed in the ROM?
# ============================================================
print("\n=== SPATIAL ANALYSIS OF UNMATCHED WORDS ===")
for bt in unmatched_in_table[:10]:
    positions = non_floor[bt]
    rows = sorted(set(p[0] for p in positions))
    cols = sorted(set(p[1] for p in positions))
    print(f"  ${bt:04X}: rows={rows}, cols={cols}")

# ============================================================
# 8. Check: are the unmatched words simple GROM card writes?
#    i.e., bt = (card_num * 8) | FG_bits | CS_bit
# ============================================================
print("\n=== PATTERN CHECK: Are unmatched words simple (card*8)+FG? ===")
simple_count = 0
complex_count = 0
for bt in unmatched_in_table:
    card = (bt >> 3) & 0x1FF
    reconstructed = (card << 3) | (bt & 7) | ((bt >> 13) & 1) << 13
    if reconstructed == bt and (bt & 0x0800) == 0:
        simple_count += 1
    else:
        complex_count += 1
        gram = (bt >> 11) & 1
        print(f"  COMPLEX: ${bt:04X} card={card} GRAM={gram} rec=${reconstructed:04X}")

print(f"Simple GROM writes: {simple_count}, Complex/GRAM: {complex_count}")

# ============================================================
# 9. Check if unmatched words have card numbers that could come
#    from a pre-computed "wall" data stream
# ============================================================
print("\n=== ROOM DATA AT $6D00 (room 0 data) ===")
# L_55BF sets up room rendering:
# - G_02F4 = $65DC (some pointer)
# - G_02F5 = $65B7 (attr table) 
# - G_0175 = 2, G_0176 = $1A (26)
# then calls L_5EE2 to render

# $65DC might be the room data pointer
# Let's see what's there
print("Room pointer at $65DC:")
ptr = rw_be(0x65DC)
print(f"  ${ptr:04X}")
# Room 0 might be pointed to by $65DC + room_index
# For room 0, maybe $65DC itself is the data pointer

# The tile stream for room 0 is at $6D98 (from previous analysis)
# Let's read it
print("\nRoom 0 tile stream at $6D98:")
for i in range(48):
    addr = 0x6D98 + i
    b = rw_be(addr)
    if b != 0xFFFF:
        print(f"  [+{i:2d}] ${addr:04X}: ${b:04X} ({b})")
