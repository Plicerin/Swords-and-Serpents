"""
BACKTAB Construction Pipeline Simulator
Traces L_5EC7 (background tiles) and L_63B9 (room objects)
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

def rw(addr):
    """Read big-endian 16-bit word at CP-1610 address"""
    off = (addr - 0x5000) * 2
    return (rom[off] << 8) | rom[off + 1] if off + 1 < len(rom) else 0

# ============================================================
# SIMULATE L_5EC7: Background tile rendering
# Input: tile_index (R1), returns BACKTAB word
# ============================================================
def L_5EC7(tile_index):
    """Simulate L_5EC7 - combine tile map + color table"""
    # G_02F5 = $65B7 (tile map base)
    tile_map_base = 0x65B7
    color_table_base = 0x65A0
    
    # SLR R1,2; SLR R1,2; SLR R1,1 => R1 / 32
    idx = tile_index >> 5
    
    r3 = tile_map_base + idx
    r5_ptr = color_table_base + idx
    
    # MVI@ R3, R1 => read tile map entry
    tile_entry = rw(r3)
    
    # SLR R1, 2; SWAP R1, 1; XOR@ R3, R1
    # This extracts specific bits from the tile entry
    temp = tile_entry >> 2
    temp = ((temp & 0xFF) << 8) | ((temp >> 8) & 0xFF)  # SWAP
    temp ^= tile_entry  # XOR with original
    
    # SDBD; ANDI #$3607, R1
    # Mask: $3607 = bits 13,12,10,9, 2,1,0
    r1 = temp & 0x3607
    
    # MVI@ R5, R3 => read color value
    color_val = rw(r5_ptr)
    
    # SLL R3, 2; SLL R3, 1 => *8
    color_shifted = (color_val << 3) & 0xFFFF
    
    # XORR R3, R1
    backtab_word = r1 ^ color_shifted
    
    return backtab_word

# ============================================================
# SIMULATE L_63B9: Object rendering to BACKTAB
# Input: room_data_ptr (R4), column (R0), row (R1)
# ============================================================
def L_63B9(room_data_offset, col, row):
    """Simulate L_63B9 - render room object to BACKTAB"""
    # R5 = $0200 + col + row*20 (BACKTAB address)
    backtab_addr = 0x0200 + col + row * 20
    
    # R4 = room_data_offset
    # SDBD; SUBI #$64E0, R4 => R4 = offset - 2 (since R4 was incremented by 2 reads)
    # Actually R4 has been incremented by MVI@ twice, so R4 = room_data_base + offset + 2
    # SUBI #$64E0 => R4 = (base + offset + 2) - $64E0 = offset (since base=$64DE, base+2=$64E0)
    adjusted_offset = room_data_offset  # already adjusted for the 2 reads
    
    # RRC R1, 2 => R1 = offset >> 2
    nibble_index = adjusted_offset >> 2
    
    # RLC R0, 2 => R0 = offset & 3
    nibble_sel = adjusted_offset & 3
    
    # ADDI #$6580, R1 => R1 = $6580 + nibble_index
    type_idx_addr = 0x6580 + nibble_index
    type_word = rw(type_idx_addr)
    
    # MVI@ R1, R2 => R2 = type_index[nibble_index]
    # RRC R0, 2 => check bit 1 of nibble_sel
    if nibble_sel & 2:  # bit 1 set = lower nibbles
        # SLR R2,2; SLR R2,2; SLR R2,1 => shift right 5
        raw_type = (type_word >> 5) & 0x1F
    else:
        # ANDI #$001F, R2
        # But for the no-shift case, we want a different nibble based on bit 0
        if nibble_sel & 1:
            raw_type = (type_word >> 4) & 0xF  # second nibble
        else:
            raw_type = type_word & 0xF  # first nibble
    
    # Actually, let me re-derive the nibble extraction from the code
    # The code uses RRC/RLC tricks that extract nibbles differently
    # Let me trace the exact bit operations
    
    # offset bits: ... b2 b1 b0
    # RRC R1,2: R1 = offset >> 2, carry = bit 1 of offset
    # RLC R0,2: R0 = (0 << 2) | bit_1_of_offset | (carry_from_shift)
    #   Actually: RLC rotates through carry. R0 starts at 0.
    #   After RLC R0,2: R0 bit0 = O_flag (from RRC = bit 0 of offset)
    #                   R0 bit1 = C_flag (from RRC = bit 1 of offset)
    # So R0 = (offset & 3)
    
    r0 = nibble_sel  # bits 1:0 of offset
    
    # RRC R0, 2: shift right 2 through carry
    # C = bit 1 of R0, R0 >>= 2
    carry = (r0 >> 1) & 1  # bit 1 goes to carry
    
    if carry:
        # Extract from upper bits (shift right 5)
        raw_type = (type_word >> 5) & 0x1F
    else:
        # No shift case - but which nibble?
        # If bit 0 of r0 determines which of the two nibbles
        if r0 & 1:
            # Second nibble (bits 4-7)
            raw_type = (type_word >> 4) & 0xF
        else:
            # First nibble (bits 0-3)
            raw_type = type_word & 0xF
    
    # SLL R2, 1 => R2 = type * 2
    # ADDI #$655E, R4 => R4 = $655E + type*2
    type_val = raw_type & 0x1F
    obj_addr = 0x655E + type_val * 2
    
    # SDBD; MVI@ R4, R0 => read object table
    obj_word = rw(obj_addr)
    
    # MVO@ R0, R5 => write to BACKTAB
    return backtab_addr, obj_word, type_val

# ============================================================
# FIXED NIBBLE EXTRACTION (matching the actual code flow)
# ============================================================
def extract_type_from_index(adjusted_offset):
    """Extract type number from type index table, matching L_63B9 logic"""
    nibble_index = adjusted_offset >> 2
    nibble_sel = adjusted_offset & 3
    
    type_word = rw(0x6580 + nibble_index)
    
    # R0 = nibble_sel
    # RRC R0, 2: C = bit 1 of R0
    if nibble_sel & 2:  # bit 1 set
        return (type_word >> 5) & 0x1F
    else:
        if nibble_sel & 1:
            return (type_word >> 4) & 0xF
        else:
            return type_word & 0xF

# ============================================================
# MAIN SIMULATION
# ============================================================

print("=" * 70)
print("BACKTAB CONSTRUCTION PIPELINE SIMULATION")
print("=" * 70)

# Part 1: Show background tiles (L_5EC7)
print("\n=== Part 1: Background Tiles (L_5EC7) ===")
print("Color table + tile map combine to form BACKTAB words")
print()
print("Color table ($65A0) values and their shifted effect:")
for i in range(12):
    addr = 0x65A0 + i * 2
    val = rw(addr)
    shifted = (val << 3) & 0xFFFF
    # What BACKTAB bits does this set?
    bits_set = []
    for b in range(16):
        if shifted & (1 << b):
            bits_set.append(str(b))
    print("  [{:2d}] ${:04X}: ${:04X} -> <<3 = ${:04X} (bits: {})".format(
        i, addr, val, shifted, ','.join(bits_set) if bits_set else 'none'))

print()
print("Tile map ($65B7) entries:")
for i in range(19):
    addr = 0x65B7 + i * 2
    val = rw(addr)
    print("  [{:2d}] ${:04X}: ${:04X}".format(i, addr, val))

print()
print("Sample L_5EC7 outputs (tile_index -> BACKTAB word):")
for tile_idx in [0, 1, 2, 3, 8, 9, 10]:
    bt = L_5EC7(tile_idx)
    card = bt & 0xFF
    fg = (bt >> 11) & 7
    bg = (bt >> 9) & 3
    gram = (bt >> 13) & 1
    print("  tile[{}] -> ${:04X} (card=${:02X}, FG={}, BG={}, GRAM={})".format(
        tile_idx, bt, card, fg, bg, gram))

# Part 2: Show room objects (L_63B9)
print("\n=== Part 2: Room Objects (L_63B9) ===")
print("Type index -> Object table -> BACKTAB")

print()
print("Type Index Table ($6580-$659F):")
for i in range(16):
    addr = 0x6580 + i * 2
    word = rw(addr)
    # Extract 4 nibbles
    n0 = word & 0xF
    n1 = (word >> 4) & 0xF
    n2 = (word >> 8) & 0xF
    n3 = (word >> 12) & 0xF
    print("  [{:2d}] ${:04X}: ${:04X}  nibbles=[{},{},{},{}]".format(i, addr, word, n0, n1, n2, n3))

print()
print("Object Table ($655E-$659D) with cards:")
for i in range(32):
    addr = 0x655E + i * 2
    word = rw(addr)
    # The object table stores just the card number in bits 7-0
    card_full = word & 0xFF
    card_6bit = card_full & 0x3F
    print("  [{:2d}] ${:04X}: ${:04X}  card=${:02X}({})  6bit=${:02X}({})".format(
        i, addr, word, card_full, card_full, card_6bit, card_6bit))

# Part 3: Simulate room rendering
print()
print("=== Part 3: Room Data -> BACKTAB Mapping ===")
print("Room data entries and their BACKTAB results:")
print()

for entry_idx in range(16):
    room_addr = 0x64DE + entry_idx * 2
    room_word = rw(room_addr)
    x = room_word & 0xFF
    y = (room_word >> 8) & 0xFF
    
    # Calculate the adjusted offset (after reading 2 words)
    # Each entry is 2 bytes. After reading X and Y, R4 = room_addr + 2
    # adjusted_offset = (room_addr + 2) - 0x64DE = entry_idx * 2
    adjusted_offset = entry_idx * 2
    
    type_num = extract_type_from_index(adjusted_offset)
    obj_addr = 0x655E + type_num * 2
    obj_word = rw(obj_addr)
    
    bt_addr, bt_word, _ = L_63B9(adjusted_offset, x, y)
    
    # Calculate expected BACKTAB position
    expected_bt_addr = 0x0200 + x + y * 20
    
    card_full = obj_word & 0xFF
    card_6bit = card_full & 0x3F
    
    print("  Entry[{}] room=${:04X} x=${:02X} y=${:02X} type={} obj=${:04X} card=${:02X} BACKTAB=${:04X}".format(
        entry_idx, room_addr, x, y, type_num, obj_word, card_6bit, expected_bt_addr))

# Part 4: Known BACKTAB values from runtime
print()
print("=== Part 4: Cross-Reference with Known Runtime BACKTAB ===")
print()
print("Known BACKTAB values (from JZINTV dump):")
known_bt = [
    0x1703, 0x1633, 0x179B, 0x172B, 0x1793, 0x1783, 0x172B,
    0x1773, 0x17A3, 0x179B,
    0x1EBB, 0x174B, 0x176B, 0x170B, 0x173B, 0x174B, 0x171B, 0x168B, 0x16CB,
    0x16C3, 0x1693, 0x172B, 0x1773, 0x17A3, 0x172B, 0x1793, 0x173B,
    0x170B, 0x176B, 0x172B, 0x1643, 0x168B, 0x1663, 0x1693, 0x1663,
    0x169B, 0x164B
]

print()
print("Extracting card numbers from known BACKTAB values:")
unique_cards = set()
for bt in known_bt:
    card = bt & 0x3F
    fg = (bt >> 11) & 7
    bg = (bt >> 9) & 3
    prefix = bt & 0xFF00
    unique_cards.add(card)
    print("  ${:04X} -> card=${:02X} FG={} BG={} prefix=${:04X}".format(bt, card, fg, bg, prefix))

print()
print("Cross-referencing known cards with object table:")
for card in sorted(unique_cards):
    matches = []
    for i in range(32):
        obj_word = rw(0x655E + i * 2)
        obj_card = (obj_word & 0xFF) & 0x3F
        if obj_card == card:
            matches.append((i, obj_word))
    if matches:
        matches_str = ', '.join('obj[{}]=${:04X}'.format(m[0], m[1]) for m in matches)
        print("  card=${:02X} matches: {}".format(card, matches_str))
    else:
        print("  card=${:02X} NO MATCH in object table".format(card))

# Part 5: Analyze where $16/$17 prefix comes from
print()
print("=== Part 5: Color Prefix Analysis ===")
print()
print("Known BACKTAB prefixes:")
prefixes = set()
for bt in known_bt:
    prefix = bt & 0xFF00
    prefixes.add(prefix)
for p in sorted(prefixes):
    fg = (p >> 11) & 7
    bg = (p >> 9) & 3
    gram = (p >> 13) & 1
    print("  ${:04X}: FG={} BG={} GRAM={}".format(p, fg, bg, gram))

print()
print("The object table stores cards WITHOUT color bits.")
print("The color ($16/$17/$1E prefix) must be added elsewhere.")
print()
print("Checking L_6445 color injection:")
print("  MWII #$0016; SWAP => $1600 written to BACKTAB-1")
print("  This is for SPECIFIC type 7 objects (doors/chests)")
print()
print("Checking if room data Y byte encodes color:")
for entry_idx in range(16):
    room_word = rw(0x64DE + entry_idx * 2)
    y = (room_word >> 8) & 0xFF
    type_num = extract_type_from_index(entry_idx * 2)
    print("  Entry[{}]: Y=${:02X} type={}".format(entry_idx, y, type_num))
