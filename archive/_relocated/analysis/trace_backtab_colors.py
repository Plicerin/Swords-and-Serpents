"""Deep-dive: trace EVERY byte in the object table, and cross-reference 
with L_63B9 logic to understand the color injection mechanism."""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

def rw(addr):
    offset = (addr - 0x5000) * 2
    if offset + 1 < len(rom):
        return (rom[offset] << 8) | rom[offset + 1]
    return 0

# === DUMP ENTIRE OBJECT-RELATED ROM REGION ===
print("=== COMPLETE ROM DUMP: $64E0 - $65DF (room data + object tables) ===")
print("     Addr  Off    B0 B1   Word     Decoded")
print("     " + "-" * 75)

for addr in range(0x64E0, 0x65E0, 2):
    offset = (addr - 0x5000) * 2
    b0 = rom[offset] if offset < len(rom) else 0
    b1 = rom[offset+1] if offset+1 < len(rom) else 0
    word = (b0 << 8) | b1
    
    # Try decoding as room object (col=bits0-4, row=bits5-8, type=bits9-14)
    col = word & 0x1F
    row = (word >> 5) & 0xF
    obj_type = (word >> 9) & 0x3F
    
    # Also try as BACKTAB word
    card = (word >> 3) & 0x3F
    fg = ((word >> 9) & 0x7) << 3 | (word & 0x7)
    cs = "CS" if (word >> 12) & 1 == 0 else "STACK"
    
    if addr < 0x655E:
        label = f"col={col:2d} row={row:2d} type={obj_type:2d}"
    elif addr < 0x6580:
        label = f"BTAB=${word:04X} card=${card:02X} FG={fg:2d} {cs}"
    elif addr < 0x65A0:
        label = f"type_idx={word & 0x3F:2d}"
    else:
        label = ""
    
    section = ""
    if addr == 0x64E0: section = " <-- ROOM DATA START"
    elif addr == 0x655E: section = " <-- OBJECT BTAB TABLE"
    elif addr == 0x6580: section = " <-- TYPE INDEX TABLE"
    elif addr == 0x659E: section = " <-- END type index"
    elif addr == 0x65A0: section = " <-- CARD TABLE (L_5EC7)"
    
    print(f"     ${addr:04X} ${offset:04X}  ({b0:02X} {b1:02X})  ${word:04X}   {label}{section}")

print()

# === NOW: Trace L_63B9's math with actual room data ===
print("=== TRACING L_63B9 with first room's objects ===")
print()

# Room data at $64DE (where objects start) 
print("Room objects (from room data $64DE-$655D):")
obj_defs = []
for addr in range(0x64DE, 0x655E, 4):
    w0 = rw(addr)
    w1 = rw(addr+2)
    col0 = w0 & 0x1F
    row0 = (w0 >> 5) & 0xF
    type0 = (w0 >> 9) & 0x3F
    col1 = w1 & 0x1F
    row1 = (w1 >> 5) & 0xF
    type1 = (w1 >> 9) & 0x3F
    obj_defs.append((addr, col0, row0, type0))
    obj_defs.append((addr+2, col1, row1, type1))
    print(f"  ${addr:04X}: obj1(col={col0:2d} row={row0:2d} type={type0:2d})  obj2(col={col1:2d} row={row1:2d} type={type1:2d})")

print()

# For each object definition, simulate L_63B9
# L_63B9: R5 = $0200 + col + row*20 (BACKTAB address)
# Then it indexes into type table at $6580
# For types > 7: reads object table at $655E + type*2
print("=== SIMULATING L_63B9 for each object ===")
print(f"{'Obj#':>4} {'col':>3} {'row':>3} {'type':>4} {'R4-off':>6} {'type_idx_R1':>10} {'type_from_table':>15} {'BTAB':>6} {'card':>4} {'FG':>3}")
print("-" * 90)

type_index_base = 0x6580
obj_btab_base = 0x655E

actual_btab_positions = {}
# From the capture:
# Row 5 (Y=5): $0228-$022B: 179B 17BB 177B 1793 1723 179B 1603 1633 1603 179B 172B 1793 1783 172B 1773 17A3 179B
# Row 6 (Y=6): ??? 
# Row 10 (Y=10): $0250+: 1EBB 174B
# Row 11 (Y=11): $0258+: 176B 170B 173B 174B 171B 168B 16CB
# Row 12 (Y=12): $0260+: 16C3 1693

for i, (addr, col, row, obj_type) in enumerate(obj_defs):
    if obj_type == 0:
        continue  # skip null objects
    
    # R4 offset from $64E0
    r4_offset = addr - 0x64E0
    
    # R1 = R4 / 4 (from the RRC/ADC dance)
    type_table_index = r4_offset // 4
    
    # R1 = $6580 + type_table_index
    type_table_addr = 0x6580 + type_table_index * 2
    type_from_table = rw(type_table_addr) & 0x1F
    
    # Object BACKTAB entry
    btab_addr = 0x655E + obj_type * 2
    btab_word = rw(btab_addr)
    card = (btab_word >> 3) & 0x3F
    fg = ((btab_word >> 9) & 0x7) << 3 | (btab_word & 0x7)
    
    # BACKTAB address
    btab_dest = 0x0200 + col + row * 20
    
    print(f"  {i:3d}  {col:3d}  {row:3d}   {obj_type:2d}    ${r4_offset:04X}     ${type_table_addr:04X}      type={type_from_table:2d} (${rw(type_table_addr):04X})   ${btab_word:04X}  ${card:02X}   {fg:2d}   -> ${btab_dest:04X}")

print()

# Now show what would actually be written: the object table word directly
print("=== EXPECTED BACKTAB (if object table words are written directly) ===")
print("Grid positions 20x12:")
grid = [[0x1603] * 20 for _ in range(12)]  # default wall fill

for i, (addr, col, row, obj_type) in enumerate(obj_defs):
    if obj_type == 0:
        continue
    btab_word = rw(0x655E + obj_type * 2)
    if row < 12 and col < 20:
        grid[row][col] = btab_word

for r in range(12):
    row_str = " ".join(f"${grid[r][c]:04X}" for c in range(20))
    print(f"  Row {r:2d}: {row_str}")

print()
print("=== ACTUAL BACKTAB (from capture - non-wall cells only) ===")
print("These are at specific positions. Let me compare per-position.")
print()

# Compare expected vs actual at each non-wall position
print("=== PER-POSITION COMPARISON: expected (from object table) vs actual ===")
actual_grid = [[0x1603] * 20 for _ in range(12)]
# Fill from capture data (positions from the earlier analysis)
actual_nonwall = {
    # From row 5 (index 5)
    (5, 2): 0x179B, (5, 3): 0x17BB, (5, 4): 0x177B, (5, 5): 0x1793,
    (5, 6): 0x1723, (5, 7): 0x179B, (5, 9): 0x1633, (5, 11): 0x179B,
    (5, 12): 0x172B, (5, 13): 0x1793, (5, 14): 0x1783, (5, 15): 0x172B,
    (5, 16): 0x1773, (5, 17): 0x17A3, (5, 18): 0x179B,
    # Row 10
    (10, 6): 0x1EBB, (10, 8): 0x174B,
    # Row 11
    (11, 1): 0x176B, (11, 2): 0x170B, (11, 3): 0x173B, (11, 4): 0x174B,
    (11, 5): 0x171B, (11, 7): 0x168B, (11, 8): 0x16CB,
    # Row 12
    (12, 1): 0x16C3, (12, 2): 0x1693,
    # Row 23? Actually there are only 12 rows (0-11). Let me check capture again.
    # The capture showed rows from $0200-$02EF which is 240 words = 20*12.
    # Row 11 would be at $02DC-$02EF.
    # Actually looking at the capture more carefully, the labeled offsets are:
    # 0200,0208,0210,0218,0220,0228,0230,0238,0240,0248,0250,0258,0260,0268,0270...
    # Each is 8 words, so 0200+row*8 = row offset
    # But actually BACKTAB is 20 words per row, so each 8-word dump line shows 8 cells
    
    # Let me re-parse: the capture at $0200 shows 16 cells per line (they show 8 words but the text shows 16 hex values)
    # Actually re-reading: "0200: 1603* 1603 1603 1603 1603 1603 1603 1603" = 8 cells
    # And "0208: 1603 1603 1603 1603 1603 1603 1603 1603" = next 8 cells
    
    # So the grid is 20 columns, shown as 8+8+4 per row in the dump
    # But the dump shows 8 cells per line
    # Row 0: $0200-$0207, $0208-$020F, $0210-$0213
    # Row 1: $0214-$0217, ...
    
    # Actually wait, the dump doesn't show continuation indicators. Let me count:
    # Each line is 8 words (16 bytes). 240/8 = 30 lines.
    # Row 0: lines 0200,0208,0210(part) = cols 0-7, 8-15, 16-19
    # Row 1: line 0214 starts col 0 of row 1
    # 
    # Backtab address = $0200 + row*20 + col. Row 5 starts at $0200 + 100 = $0264
    # But the dump shows $0228, $0230, $0238...
    # $0228 = $0200 + 40 = row 2, col 8. Hmm that doesn't align.
    
    # Actually BACKTAB is $0200 + col + row*20, not $0200 + row*20 + col*8
    # Each cell is 1 word, 20 cells per row, 12 rows = 240 words = 480 bytes
    
    # The dump shows 8-word lines. Let me number the rows properly:
    # Line $0200: cols 0-7 of row 0 (addresses $0200-$0207)
    # Line $0208: cols 8-15 of row 0 (addresses $0208-$020F)
    # Line $0210: cols 16-19 of row 0 + cols 0-3 of row 1 (addresses $0210-$0217)
    # ...
    
    # Row 5 starts at $0200 + 5*20 = $0264. 
    # $0228 = col 8 of row 2 (since $0200 + 2*20 + 8 = $0248, no wait $0248 ≠ $0228)
    # Hmm: $0200 + 2*20 + 8 = $0248. But line starts at $0228. 
    # $0228 = $0200 + 2*20 + 0? No: 0x228 - 0x200 = 0x28 = 40. 40/20 = 2 rows. So $0228 = row 2 col 0.
    
    # Let me just map each line to a row:
    # Line 0200: row 0 cols 0-7
    # Line 0208: row 0 cols 8-15
    # Line 0210: row 0 cols 16-19 + row 1 cols 0-3
    # Line 0218: row 1 cols 4-11
    # Line 0220: row 1 cols 12-19
    # Line 0228: row 2 cols 0-7
    # ... and so on.
    
    # Actually let me just extract positions more carefully from the raw data.
    # The capture shows: 0200-02EF with the actual backtab values.
    # Let me just parse them properly.
}

# Let me parse the capture data properly
capture_data = {
    0x0200: [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    0x0208: [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    0x0210: [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    0x0218: [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    0x0220: [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    0x0228: [0x1603,0x1603,0x179B,0x17BB,0x177B,0x1793,0x1723,0x179B],
    0x0230: [0x1603,0x1633,0x1603,0x179B,0x172B,0x1793,0x1783,0x172B],
    0x0238: [0x1773,0x17A3,0x179B,0x1603,0x1603,0x1603,0x1603,0x1603],
    0x0240: [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    0x0248: [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    0x0250: [0x1603,0x1603,0x1603,0x1603,0x1603,0x1EBB,0x1603,0x174B],
    0x0258: [0x176B,0x170B,0x173B,0x174B,0x171B,0x1603,0x168B,0x16CB],
    0x0260: [0x16C3,0x1693,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    0x0268: [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    0x0270: [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    0x0278: [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    0x0280: [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    0x0288: [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    0x0290: [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    0x0298: [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    0x02A0: [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    0x02A8: [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    0x02B0: [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x172B,0x1773],
    0x02B8: [0x17A3,0x172B,0x1793,0x1603,0x173B,0x170B,0x176B,0x172B],
    0x02C0: [0x1603,0x1643,0x168B,0x1663,0x1693,0x1663,0x169B,0x164B],
    0x02C8: [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    0x02D0: [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    0x02D8: [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    0x02E0: [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    0x02E8: [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
}

# Build full grid
for base_addr, values in capture_data.items():
    for i, val in enumerate(values):
        addr = base_addr + i
        row = (addr - 0x0200) // 20
        col = (addr - 0x0200) % 20
        if row < 12:
            actual_grid[row][col] = val

print("ACTUAL BACKTAB grid (non-wall cells highlighted):")
for r in range(12):
    cells = []
    for c in range(20):
        v = actual_grid[r][c]
        if v != 0x1603:
            cells.append(f"\033[33m${v:04X}\033[0m")
        else:
            cells.append(f"${v:04X}")
    row_str = " ".join(cells)
    print(f"  Row {r:2d}: {row_str}")

print()

# Compare expected vs actual
print("=== COMPARISON: Expected (from object table) vs Actual ===")
print(f"{'Pos (r,c)':>10} {'Addr':>6} {'Obj#':>4} {'Type':>4} {'ObjTable':>8} {'Actual':>8} {'Match?':>7} {'SameCard?':>7}")
print("-" * 75)

for i, (addr, col, row, obj_type) in enumerate(obj_defs):
    if obj_type == 0:
        continue
    if row >= 12 or col >= 20:
        continue
    
    expected = rw(0x655E + obj_type * 2)
    actual = actual_grid[row][col]
    
    exp_card = (expected >> 3) & 0x3F
    act_card = (actual >> 3) & 0x3F
    
    match = "YES" if expected == actual else "NO"
    same_card = "YES" if exp_card == act_card else "NO"
    
    print(f"  ({row:2d},{col:2d})    ${0x200+col+row*20:04X}  {i:4d}   {obj_type:2d}    ${expected:04X}     ${actual:04X}   {match:>7}  {same_card:>7}")
