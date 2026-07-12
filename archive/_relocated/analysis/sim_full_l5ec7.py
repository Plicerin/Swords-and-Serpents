#!/usr/bin/env python3
"""
Complete simulation of L_5EE2 → L_5EC7 rendering pipeline.
Corrects the SDBD alignment issue: ADDR R1, R3 adds tile group index
to attr table pointer before reading attr[group].

Raw bytes at $5EC7:
  $5EC7: PSHR R5       ($0275)
  $5EC8: PSHR R3       ($0273)
  $5EC9: MVI  G_02F5, R3  ($0283 $02F5)   → R3 = $65B7
  $5ECB: SDBD          ($0001)
  $5ECC: MVII #$65A0, R5 ($02BD $00A0 $0065)  → R5 = $65A0 (SDBD makes 3 words)
  $5ECF: SLR  R1, 2    ($0065)             → R1 >>= 2
  $5ED0: SLR  R1, 2    ($0065)             → R1 >>= 2 
  $5ED1: SLR  R1, 1    ($0061)             → R1 >>= 1 (total >>=5, group = tile/32)
  $5ED2: ADDR R1, R3   ($00CB)             → R3 += group (index into attr table!)
  $5ED3: ???           ($00CD)             → possibly ADDR R?, R?

Then:
  MVI@ R3, R0    → R0 = attr_table[group]
  SDBD; ADD@ R5, R0  → R0 += card_table[R0 >> 10]  (word access)
  ANDI #$01F8, R0 → R0 &= $01F8
  SLR R0, 2; SLR R0, 1 → R0 = (R0 & $1F8) >> 3 = card number in bits 11-3
  ADDR R?, R0    → ?
  OR some FG bits
  PULR R3; PULR R5
  MOVR R5, R7    → return
"""

import sys
sys.stdout.reconfigure(encoding='cp1252', errors='replace')

rom = open('Swords and Serpents.bin', 'rb').read()

def rw(addr):
    """Read 16-bit big-endian word from ROM at CP-1610 word address."""
    off = (addr - 0x5000) * 2
    if off < 0 or off + 1 >= len(rom):
        return 0
    return (rom[off] << 8) | rom[off + 1]

def rb(addr):
    """Read low byte of 16-bit word (SDBD-style)."""
    off = (addr - 0x5000) * 2
    if off < 0 or off + 1 >= len(rom):
        return 0
    return rom[off + 1]  # low byte

# ============================================================
# Tables
# ============================================================

# Attr table at $65B7 (G_02F5)
attr = [rw(0x65B7 + i) for i in range(24)]
print("=== ATTR TABLE ($65B7) ===")
for i, a in enumerate(attr):
    b6_5 = (a >> 5) & 3
    b4_0 = a & 0x1F
    card_idx = (a >> 8) & 0x3F
    print(f"  [{i:2d}] ${a:04X}  bits6-5={b6_5} bits4-0={b4_0:2d}  card_idx_hi={card_idx}")

# Card table at $65A0
card_tbl = [rw(0x65A0 + i) for i in range(64)]

# $655E BACKTAB word table (for object placement)
bt655e = [rw(0x655E + i) for i in range(128)]

# $6580 card index table
card_idx = [rw(0x6580 + i) for i in range(64)]

# Room pointer table at $65DC
room_ptrs = [rw(0x65DC + i) for i in range(32)]

# Tile stream data at various room locations
print("\n=== ROOM POINTER TABLE ($65DC) ===")
for i in range(8):
    w = room_ptrs[i]
    b = rb(0x65DC + i)
    print(f"  [{i}] ${0x65DC+i:04X}: word=${w:04X} byte=${b:02X}")

# ============================================================
# L_5E48: Row setup - reads tile stream pointer
# ============================================================
# L_5E48 takes:
#   R0 bits 5-4 = some index (from G_0175 shift)
#   R2 bits 6-5 = another index (from G_0175 shift)
# Returns:
#   R2 = tile stream pointer
#   R1 = count/run length?
#   R3 = ?

# Actually, let me just focus on L_5EC7 and simulate with known tile stream data

# ============================================================
# L_5EC7: BACKTAB word construction
# ============================================================
# Input: R1 = tile value (0-255)
# Output: R1 = BACKTAB word
#
# Algorithm:
#   group = (tile_value >> 5) & 7     ; tiles 0-31→group0, 32-63→group1, etc.
#   R3 = $65B7 + group               ; index into attr table
#   R0 = attr[group]                 ; read attr word
#   R5 = $65A0                       ; card table
#   R0 += card_table[(attr_value >> 10) & ?]  ; SDBD word access
#   R0 &= $01F8                      ; mask to card bits
#   R0 >>= 3                         ; now just the card number
#   R0 |= (tile_value & 7)           ; FG color from low bits of tile
#   R0 |= 0x0800                     ; GRAM flag maybe?
#   R1 = R0

def sim_l5ec7_v1(tile_val, card_tbl, attr_tbl):
    """Version 1: group-indexed attr, card table indexed by attr bits 15-10."""
    group = (tile_val >> 5) & 7
    a = attr_tbl[group]
    
    # Try: card_table index = (attr >> 10) & 0x3F
    ci = (a >> 10) & 0x3F
    card_word = card_tbl[ci] if ci < len(card_tbl) else 0
    
    r0 = a + card_word  # ADD@ R5, R0
    r0 &= 0x01F8  # ANDI #$01F8, R0
    r0 >>= 3      # SLR x2 then SLR x1
    r0 |= (tile_val & 7)  # FG color
    r0 |= 0x0800  # GRAM flag?
    return r0 & 0xFFFF

def sim_l5ec7_v2(tile_val, card_tbl, attr_tbl):
    """Version 2: card_table index from attr bits 7-5 and tile value within group."""
    group = (tile_val >> 5) & 7
    sub_tile = tile_val & 0x1F  # 0-31 within group
    a = attr_tbl[group]
    
    # The attr value might encode a base card number
    # card_num = (a & 0x1F) + sub_tile  (where a&0x1F gives base)
    card_num = (a & 0x1F) + sub_tile
    
    # But also lookup in card table
    ci = ((a >> 7) & 0x7) * 8 + (sub_tile >> 2)  # some indexing
    if ci < len(card_tbl):
        card_word = card_tbl[ci]
    else:
        card_word = 0
    
    r0 = card_num * 8  # base card << 3
    # r0 += card_word contribution? 
    r0 |= (tile_val & 7)  # FG
    r0 |= 0x0800  # GRAM
    return r0 & 0xFFFF

def sim_l5ec7_v3(tile_val, card_tbl, attr_tbl):
    """Version 3: Try direct card output from attr encoding + FG."""
    group = (tile_val >> 5) & 7
    sub = tile_val & 0x1F
    fg = tile_val & 7
    a = attr_tbl[group]
    
    # The attr table tells us which card table entry range to use
    # AND the card table entries might be pre-computed BACKTAB words
    # (i.e., they already include card<<3 | GRAM | FG)
    
    # Try: card_table entries are full BACKTAB words
    # ci = (attr >> 10) gives card table index
    ci = (a >> 10) & 0x3F
    
    # But each group uses a RANGE of card table entries
    # The sub-tile within group selects which entry
    card_idx = ci + (sub >> 2)  # every 4 sub-tiles share a card?
    if card_idx < len(card_tbl):
        bt_word = card_tbl[card_idx]
    else:
        bt_word = 0
    
    # Overlay FG
    bt_word = (bt_word & 0xFFF8) | fg
    return bt_word & 0xFFFF

def sim_l5ec7_v4(tile_val, card_tbl, attr_tbl):
    """Version 4: card_table indexed by something from attr, result is card num<<3."""
    group = (tile_val >> 5) & 7
    sub = tile_val & 0x1F
    fg = tile_val & 7
    a = attr_tbl[group]
    
    # attr[group] encodes a base card_table index
    # The sub-tile selects from a contiguous range
    base_ci = (a >> 8) & 0x3F  # bits 13-8
    
    # sub_tile 0-31 maps to backtab cards
    # Higher sub_tiles = higher card numbers
    card_num = base_ci + sub
    
    bt = (card_num << 3) | fg
    return bt & 0xFFFF

def sim_l5ec7_v5(tile_val, card_tbl, attr_tbl):
    """Version 5: The attr's low bits encode a card table index.
    The card table entries are GROM card numbers * 8.
    Then FG and GRAM flag are OR'd in."""
    group = (tile_val >> 5) & 7
    sub = tile_val & 0x1F
    fg = sub & 7
    a = attr_tbl[group]
    
    # attr low nibble selects card table entry
    ci = a & 0x1F
    
    # card_tbl[ci] might be a GROM card * 8
    # Then we also look at bits 7-5 of attr for GRAM flag
    gram_flag = ((a >> 5) & 7) << 11  # bits 15-11 include GRAM at bit 11
    
    card_offset = 0
    if ci < len(card_tbl):
        card_offset = card_tbl[ci]
    
    # card_offset is the card number << 3, or actual BACKTAB word
    bt = card_offset | fg | gram_flag
    return bt & 0xFFFF

# ============================================================
# Read the known room 0 BACKTAB
# ============================================================
print("\n=== READING ROOM 0 BACKTAB FROM DUMP ===")
room0_bt = []
try:
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
    print(f"Read {len(room0_bt)} BACKTAB tiles from dump")
except Exception as e:
    print(f"Could not read dump: {e}")

if len(room0_bt) < 240:
    print("WARNING: No room 0 dump available, using empty grid")
    room0_bt = [0] * 240

# Show non-floor tiles
non_floor = {}
for idx, bt in enumerate(room0_bt[:240]):
    card = (bt >> 3) & 0x1FF
    if card != 0:
        if bt not in non_floor:
            non_floor[bt] = []
        non_floor[bt].append(idx)

print(f"\nNon-floor BACKTAB words ({len(non_floor)} unique):")
for bt in sorted(non_floor.keys()):
    positions = non_floor[bt]
    card = (bt >> 3) & 0x1FF
    gram = (bt >> 11) & 1
    fg = bt & 7
    cs = (bt >> 13) & 1
    src = 'GRAM' if gram else 'GROM'
    pos_str = ', '.join(f"({p//20},{p%20})" for p in positions[:8])
    if len(positions) > 8:
        pos_str += f" +{len(positions)-8} more"
    print(f"  ${bt:04X}: card={card:3d} {src:4s} FG={fg} CS={cs}  at {pos_str}")

# ============================================================
# Try different L_5EC7 interpretations
# ============================================================
# First, let's try to figure out what tile values are in each group
# by looking at the actual tile stream data

# Read tile stream for room 0
# Room 0 index = 0, so use room_ptrs[0] = $0042 byte = 0x42
# But this seems wrong. Let me look at L_5E48 more carefully.

# L_5E48 reads from G_02F4 ($65DC) using SDBD
# First read: byte at $65DC → used as index into some table
# L_5E48 also uses G_0175 and G_0176

# For room 0: G_0175=2, G_0176=26
# R0 = G_0176 = 26 ($1A)
# R2 = G_0175 = 2

# L_5E48:
#   ANDI #$0030, R0    → R0 = 26 & 0x30 = 0x10 = 16
#   SLR R0, 2           → R0 = 4
#   SLR R0, 1           → R0 = 2
#   ADD G_02F4, R0      → R0 = $65DC + 2 = $65DE
#   ANDI #$0060, R2     → R2 = 2 & 0x60 = 0
#   SLR R2, 2           → R2 = 0
#   SLR R2, 2
#   SLR R2, 1
#   MOVR R2, R3         → R3 = 0
#   SLR R3, 1           → R3 = 0
#   ADDR R0, R3         → R3 = $65DE + 0 = $65DE
#   MVI@ R3, R0         → R0 = word at $65DE
#   RRC R2, 1           → R2 bit 0 was 0, C=0
#   BNC → skip SLRs
#   ANDI #$000F, R0     → R0 &= 0xF

# Then:
#   MVII #$65CE, R4     → R4 = $65CE
#   SLR R1, 2           → ? (R1 not set by L_5E48!)
#   ADDR R0, R4         → R4 = $65CE + R0
#   SDBD
#   MVI@ R4, R2         → R2 = byte at $65CE+R0
#   PULR R0 (from stack)
#   ANDI #$000F, R0

# This is getting complex. Let me try a different approach:
# Read the tile stream data directly and try all possible L_5EC7 variants.

# ============================================================
# TRY ALL VARIANTS
# ============================================================
print("\n=== TESTING L_5EC7 VARIANTS ===")

# Get the actual tile stream by reading the room data
# For room 0, the data pointer needs to be resolved through L_5E48
# But let me try just reading from some likely data addresses

# The room data might be at $6D00-$6DFF based on previous analysis
# Let me try reading tile bytes from there
print("\nPossible tile stream data:")
for addr_base in [0x6D00, 0x6D80, 0x6D98, 0x6E00, 0x6E80, 0x6F00]:
    print(f"\n  From ${addr_base:04X}:")
    tiles = [rw(addr_base + i) for i in range(64)]
    # Show first 32 non-FFFF values
    count = 0
    for i, t in enumerate(tiles):
        if t != 0xFFFF:
            print(f"    [{i:2d}] ${t:04X} ({t:3d})", end="")
            count += 1
            if count % 8 == 0:
                print()
        if count >= 40:
            break
    if count > 0:
        print()

# ============================================================
# Let me also try: simulate using tile values 0-255 directly
# to see what BACKTAB words each variant produces
# ============================================================
print("\n=== BACKTAB WORDS FROM EACH VARIANT (tile group 0: 0-31) ===")
for variant_name, sim_fn in [
    ("v1", sim_l5ec7_v1),
    ("v2", sim_l5ec7_v2),
    ("v3", sim_l5ec7_v3),
    ("v4", sim_l5ec7_v4),
    ("v5", sim_l5ec7_v5),
]:
    print(f"\n  {variant_name}:")
    words = set()
    for t in range(256):
        w = sim_fn(t, card_tbl, attr)
        words.add(w)
    for w in sorted(words):
        card = (w >> 3) & 0x1FF
        gram = (w >> 11) & 1
        fg = w & 7
        src = 'GRAM' if gram else 'GROM'
        print(f"    ${w:04X}: card={card:3d} {src} FG={fg}")

# ============================================================
# NEW APPROACH: The card table entries might BE full BACKTAB words
# ============================================================
print("\n=== CARD TABLE AS BACKTAB WORDS ===")
for i, c in enumerate(card_tbl[:32]):
    if c != 0 and c != 0xFFFF:
        card = (c >> 3) & 0x1FF
        gram = (c >> 11) & 1
        fg = c & 7
        src = 'GRAM' if gram else 'GROM'
        print(f"  card_tbl[{i:2d}] = ${c:04X}: card={card:3d} {src} FG={fg}")
