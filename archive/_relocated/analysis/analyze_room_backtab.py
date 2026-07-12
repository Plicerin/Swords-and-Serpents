#!/usr/bin/env python3
"""
Comprehensive room BACKTAB analysis:
1. Read room object data from ROM $64DE
2. Decode each object's position using L_6394/L_63B9 logic
3. Read object table at $655E and type index at $6580
4. Cross-reference with actual BACKTAB from JZINTV capture
5. Determine where $16/$17 color prefix comes from
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

def rw(a):
    """Read 16-bit word from ROM at CP-1610 address a."""
    o = (a - 0x5000) * 2
    if o + 1 < len(rom):
        return (rom[o] << 8) | rom[o + 1]
    return 0

# ============================================================
# ACTUAL BACKTAB from JZINTV capture (dump_room_out.txt)
# ============================================================
# 20 columns x 12 rows = 240 cells at $0200-$02EF
actual_bt = {}
bt_raw = [
    # Row 0 ($0200-$0213)
    0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,
    # Row 1 ($0214-$0227) 
    0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,
    # Row 2 ($0228-$023B)
    0x1603,0x1603,0x179B,0x17BB,0x177B,0x1793,0x1723,0x179B,0x1603,0x1633,0x1603,0x179B,0x172B,0x1793,0x1783,0x172B,0x1773,0x17A3,0x179B,0x1603,
    # Row 3 ($023C-$024F)
    0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,
    # Row 4 ($0250-$0263)
    0x1603,0x1603,0x1603,0x1603,0x1603,0x1EBB,0x1603,0x174B,0x176B,0x170B,0x173B,0x174B,0x171B,0x1603,0x168B,0x16CB,0x16C3,0x1693,0x1603,0x1603,
    # Row 5 ($0264-$0277)
    0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,
    # Row 6 ($0278-$028B)
    0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,
    # Row 7 ($028C-$029F)
    0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,
    # Row 8 ($02A0-$02B3)
    0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,
    # Row 9 ($02B4-$02C7)
    0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x172B,0x1773,0x17A3,0x172B,0x1793,0x1603,0x173B,0x170B,0x176B,0x172B,0x1603,0x1643,0x168B,0x1663,
    # Row 10 ($02C8-$02DB)
    0x1693,0x1663,0x169B,0x164B,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,
    # Row 11 ($02DC-$02EF)
    0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,
]
for row in range(12):
    for col in range(20):
        addr = 0x0200 + row * 20 + col
        actual_bt[addr] = bt_raw[row * 20 + col]

# ============================================================
# CONSTANTS from L_55BF (room init)
# ============================================================
G_0175 = 2     # column offset
G_0176 = 26    # row offset (0x1A)
G_019C_init = 0  # current floor index

# ============================================================
# ROOM OBJECT DATA at $64DE
# Format: 16 pairs of words
#   Word 0: col (low 5 bits), row bits in upper
#   Word 1: type index selector (used with table at $6580)
# ============================================================
print("=" * 80)
print("ROOM OBJECTS DECODED FROM ROM $64DE")
print("=" * 80)

objects = []
for idx in range(16):
    addr = 0x64DE + idx * 4
    w0 = rw(addr)
    w1 = rw(addr + 2)
    
    # Decode raw position from room data
    room_col = w0 & 0x1F
    room_row = (w0 >> 5) & 0x0F
    
    # L_6394 transform: subtract offsets and clamp
    screen_col = room_col - G_0175
    screen_row = room_row - G_0176
    
    # L_6394 checks and clamps
    if screen_col < -105:  # $FF97 signed check
        screen_col &= 0x1F
    if screen_row < -50:   # $FFCE
        screen_row &= 0x0F
    
    # Bounds check (L_639E-L_63B6)
    valid = (0 <= screen_col <= 19) and (0 <= screen_row <= 11)
    
    # Get type from type index table at $6580
    # L_63C3-L_63D7: index = (addr - $64DE) >> 2, then lookup in $6580
    data_offset = addr - 0x64DE  # 0, 4, 8, ...
    type_idx = data_offset >> 2   # 0, 1, 2, ..., 15
    raw_type = rw(0x6580 + type_idx * 2)  # type info word
    
    # L_63D7: type_code = raw_type & 0x1F (after RRC/shift logic)
    # Actually from L_63CA-L_63D7:
    #   RRC R1,2; RLC R0,2; SDBD; ADDI #$6580,R1; MVI@ R1,R2
    #   RRC R0,2; BNC L_63D7
    #   SLR R2,2; SLR R2,2; SLR R2,1  (shift by 5 total)
    # L_63D7: ANDI #$001F, R2
    # So: if carry from RRC, shift right by 5; then AND with $1F
    
    # The type_index from $6580 table needs RRC/shift processing
    # R1 = data_offset >> 2 (integer division by 4)
    # RRC R1,2 shifts R1 right by 2, LSB goes to carry
    # RLC R0,2 shifts R0 left by 2, carry goes to LSB
    # After SDBD+ADDI: R1 = $6580 + type_idx*2
    # R2 = ROM[$6580 + type_idx*2]
    # RRC R0,2: check if bit 1 of original offset was set
    # If YES: SLR R2 by 5
    
    # Simplify: data_offset is 0,4,8,...,60. In binary:
    # 0: 000000, 4: 000100, 8: 001000, 12: 001100, ...
    # RRC R1,2: R1 = data_offset/4 = type_idx, shifted right by 2
    # Then RLC R0,2 loads the carry (bit 1 of R1) into R0 bit 0
    # RRC R0,2 checks if R0 bit 0 was set
    # This happens when bit 1 of type_idx = 1 (i.e., type_idx & 2 != 0)
    # If so, shift right by 5
    
    obj_type = raw_type & 0x1F
    if (type_idx & 2):
        obj_type = (raw_type >> 5) & 0x1F
    
    # Read object table at $655E for this type
    obj_table_entry = rw(0x655E + obj_type * 2)
    obj_card = obj_table_entry & 0xFF
    obj_attr = (obj_table_entry >> 8) & 0xFF
    
    # Compute BACKTAB address
    bt_addr = None
    if valid:
        bt_addr = 0x0200 + screen_row * 20 + screen_col
    
    # Get actual BACKTAB value at that position
    actual_val = actual_bt.get(bt_addr) if bt_addr else None
    actual_card = actual_val & 0xFF if actual_val else None
    actual_attr = (actual_val >> 8) & 0xFF if actual_val else None
    
    # Check if same card
    same_card = (actual_card == obj_card) if actual_val and obj_table_entry else False
    
    objects.append({
        'idx': idx,
        'addr': addr,
        'w0': w0, 'w1': w1,
        'room_col': room_col, 'room_row': room_row,
        'screen_col': screen_col, 'screen_row': screen_row,
        'valid': valid,
        'type_idx': type_idx,
        'raw_type': raw_type,
        'obj_type': obj_type,
        'obj_table': obj_table_entry,
        'obj_card': obj_card,
        'obj_attr': obj_attr,
        'bt_addr': bt_addr,
        'actual_bt': actual_val,
        'actual_card': actual_card,
        'actual_attr': actual_attr,
        'same_card': same_card,
    })
    
    status = "VALID" if valid else "INVALID"
    card_match = " *** SAME CARD ***" if same_card else ""
    print(f"  Obj {idx:2d} (${addr:04X}): "
          f"w0=${w0:04X} w1=${w1:04X}  "
          f"room=({room_col:2d},{room_row:2d}) screen=({screen_col:2d},{screen_row:2d}) "
          f"type={obj_type:2d}  "
          f"obj_tbl=${obj_table_entry:04X}  "
          f"BT=${bt_addr and f'${bt_addr:04X}:${actual_val:04X}' or 'N/A'}  "
          f"{status}{card_match}")

# ============================================================
# ANALYSIS: Color attribution pattern
# ============================================================
print()
print("=" * 80)
print("COLOR ATTRIBUTION ANALYSIS")
print("=" * 80)

for obj in objects:
    if obj['valid'] and obj['actual_bt']:
        bt = obj['actual_bt']
        card = bt & 0xFF
        attr = (bt >> 8) & 0xFF
        obj_card = obj['obj_card']
        obj_attr = obj['obj_attr']
        
        # Check if object table card matches actual card
        if card == obj_card:
            print(f"  Obj {obj['idx']:2d} (type={obj['obj_type']:2d}): "
                  f"CARD MATCH! obj_tbl_card=${obj_card:02X}, actual=${bt:04X} "
                  f"(attr=${attr:02X} vs obj_tbl_attr=${obj_attr:02X}) "
                  f"at screen ({obj['screen_col']:2d},{obj['screen_row']:2d})")
        else:
            print(f"  Obj {obj['idx']:2d} (type={obj['obj_type']:2d}): "
                  f"CARD MISMATCH obj_tbl=${obj['obj_table']:04X} actual=${bt:04X} "
                  f"(obj_card=${obj_card:02X} vs actual_card=${card:02X}) "
                  f"at screen ({obj['screen_col']:2d},{obj['screen_row']:2d})")

# ============================================================
# HYPOTHESIS: Compare object table upper bytes with actual colors
# ============================================================
print()
print("=" * 80)
print("OBJECT TABLE vs ACTUAL BACKTAB - ALL TYPES")
print("=" * 80)
print(f"{'Type':>4} {'ObjTbl':>8} {'Card':>6} {'Attr':>6} {'ActualCs':>10} {'Seen?':>6}")
print("-" * 50)

# Map which BACKTAB addresses have which object types (from room data)
type_to_positions = {}
for obj in objects:
    if obj['valid'] and obj['actual_bt']:
        t = obj['obj_type']
        if t not in type_to_positions:
            type_to_positions[t] = []
        type_to_positions[t].append(obj)

for t in range(32):
    ot = rw(0x655E + t * 2)
    card = ot & 0xFF
    attr = (ot >> 8) & 0xFF
    
    # Find actual BACKTAB values that have same card
    matching_positions = type_to_positions.get(t, [])
    actual_values = set()
    for obj in matching_positions:
        actual_values.add(obj['actual_bt'])
    
    seen_str = ", ".join(f"${v:04X}" for v in sorted(actual_values)) if actual_values else ""
    floor_mark = " [FLOOR]" if t <= 7 else ""
    
    print(f"  {t:2d}  ${ot:04X}  ${card:02X}    ${attr:02X}    {seen_str:10s}  {floor_mark}")

# ============================================================
# KEY INSIGHT: Compare object table vs actual BACKTAB entries
# ============================================================
print()
print("=" * 80)
print("PATTERN ANALYSIS: Object table entries vs actual BACKTAB")
print("=" * 80)

# For each valid object with same card:
# actual_attr = X, obj_attr = Y. What produces X from Y?
for obj in objects:
    if obj['valid'] and obj['same_card']:
        actual = obj['actual_bt']
        obj_tbl = obj['obj_table']
        actual_attr = (actual >> 8) & 0xFF
        obj_attr = (obj_tbl >> 8) & 0xFF
        
        # In Intelivision BACKTAB (CP-1610 16-bit word):
        # High byte -> STIC even addr (attribute in some views)
        # Low byte -> STIC odd addr (card in some views)
        # 
        # BUT: the object table stores card in low byte!
        # The actual BACKTAB also stores card in low byte.
        # Difference is in the HIGH byte (attr).
        #
        # $16 = 0001 0110
        # $17 = 0001 0111
        # $1E = 0001 1110
        
        # Check if actual_attr = obj_attr | $16 or | $17
        or16 = obj_attr | 0x16
        or17 = obj_attr | 0x17
        
        print(f"  Obj {obj['idx']:2d} type={obj['obj_type']:2d}: "
              f"obj_tbl=${obj_tbl:04X} actual=${actual:04X} "
              f"[obj_attr=${obj_attr:02X}] [actual_attr=${actual_attr:02X}] "
              f"obj_attr|0x16=${or16:02X} obj_attr|0x17=${or17:02X}")

# ============================================================
# ALTERNATIVE HYPOTHESIS: Maybe it's not the object table at all
# Maybe L_63B9 uses a DIFFERENT table or formula
# ============================================================
print()
print("=" * 80)
print("ALTERNATIVE: What if L_63B9 reads from $655E+type*2 BUT the values")
print("in ROM are DIFFERENT from what we read? Let's check byte order.")
print("=" * 80)

# Maybe the object table stores values differently
# In the 8-bit world: card at $655E (even), color at $655F (odd)
# In CP-1610 16-bit: word at $655E = (byte_at_655E << 8) | byte_at_655F
# So: high_byte = byte_at_655E, low_byte = byte_at_655F

# Let me try reading the object table as 8-bit pairs in reverse order
print("\nObject table read as PAIRS of 8-bit values at EVEN addresses:")
for t in range(32):
    base = 0x655E + t * 2
    o = (base - 0x5000) * 2
    b0 = rom[o]     # high byte of 16-bit word = byte at $655E+0
    b1 = rom[o+1]   # low byte of 16-bit word = byte at $655E+1
    word = (b0 << 8) | b1
    
    # What if the table stores two 8-bit values:
    # Byte 0 ($655E+0): card number (0-63 GROM)
    # Byte 1 ($655E+1): attribute byte
    card_from_pair = b1  # low byte
    attr_from_pair = b0  # high byte
    
    floor = " [FLOOR]" if t <= 7 else ""
    print(f"  Type {t:2d}: raw=({b0:02X},{b1:02X}) word=${word:04X} "
          f"card=${card_from_pair:02X} attr=${attr_from_pair:02X}{floor}")
