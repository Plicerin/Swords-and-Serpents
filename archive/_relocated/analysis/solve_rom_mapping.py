#!/usr/bin/env python3
"""Empirically determine correct ROM mapping for $65A0/$65B7 tables
by testing all byte orders and alignments against known jzIntv BACKTAB words.
"""
import sys
sys.stdout.reconfigure(encoding='cp1252', errors='replace')

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

# Known jzIntv BACKTAB words from room 0 rendering
KNOWN_BT = {
    0x1603, 0x081B, 0x1E13, 0x020F, 0x02B7, 0x02A7, 0x0257, 0x0287,
    0x02BF, 0x029F, 0x025F, 0x0207, 0x0327, 0x0317, 0x1EBB, 0x026F,
    0x024F, 0x022F, 0x021F, 0x023F, 0x03AF, 0x03EF, 0x03E7, 0x03B7,
    0x1E5B, 0x1E40, 0x0E60, 0x0823, 0x1E38, 0x1E02, 0x082B, 0x0367,
    0x0347, 0x036F, 0x03BF,
}

# Tile values from the stream data at $6D86 (jzIntv trace)
STREAM_TILES = [0x000A, 0x0122, 0x0061, 0x0125, 0x0061, 0x0126,
                0x0061, 0x0128, 0x0061, 0x0127, 0x000B, 0x0121]

# Stream tile >>5 indices: [0, 9, 3, 9, 3, 9, 3, 9, 3, 9, 0, 9]

def read_word(rom, file_offset, byte_order='be'):
    """Read 16-bit word from ROM file."""
    if file_offset + 1 >= len(rom):
        return 0
    if byte_order == 'be':
        return (rom[file_offset] << 8) | rom[file_offset + 1]
    else:  # le
        return rom[file_offset] | (rom[file_offset + 1] << 8)

def l5ec7(tile_val, attr_table, card_table):
    """Exact L_5EC7 algorithm."""
    idx = tile_val >> 5
    if idx + 1 >= len(attr_table) or idx >= len(card_table):
        return 0
    attr0 = attr_table[idx]
    attr1 = attr_table[idx + 1]
    card = card_table[idx]
    
    r1 = attr0 >> 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)  # SWAP
    r1 ^= attr1
    r1 &= 0x3607
    r3 = (card << 3) & 0xFFFF
    r1 ^= r3
    return r1

def test_interpretation(rom, attr_offset, card_offset, byte_order, align_shift=0):
    """Test a specific ROM interpretation."""
    # Read 23 attr table words (indices 0-22, but we need idx+1 so 24)
    # Actually, for tile>>5 up to say 10, we need indices 0-11
    # Let's read 32 words for safety
    attr = []
    for i in range(32):
        o = attr_offset + i * 2 + align_shift
        attr.append(read_word(rom, o, byte_order))
    
    card = []
    for i in range(32):
        o = card_offset + i * 2 + align_shift
        card.append(read_word(rom, o, byte_order))
    
    # Test: for each stream tile, produce BACKTAB and check against known set
    produced = set()
    for tv in range(256):
        bt = l5ec7(tv, attr, card)
        produced.add(bt)
    
    # Count matches with known BACKTAB words
    hits = produced & KNOWN_BT
    return len(hits), produced, attr, card

# Test all combinations
print("=== TESTING ALL ROM INTERPRETATIONS ===\n")

# Base offsets for $65A0 and $65B7
# BE: $65A0 -> (0x65A0-0x5000)*2 = 0x2B40
# BE: $65B7 -> (0x65B7-0x5000)*2 = 0x2B6E

best_hits = 0
best_config = None

for byte_order in ['be', 'le']:
    for card_base in [0x2B40, 0x2B3E, 0x2B42, 0x2B44, 0x2B46, 0x2B48]:
        for attr_base in [0x2B6E, 0x2B6C, 0x2B70, 0x2B72]:
            for align in [0]:
                hits, produced, attr, card = test_interpretation(
                    rom, attr_base, card_base, byte_order, align)
                
                marker = ""
                if hits > best_hits:
                    best_hits = hits
                    best_config = (byte_order, card_base, attr_base, align, hits, attr, card)
                    marker = " *** NEW BEST ***"
                
                if hits >= 2:  # Only show interesting results
                    print(f"  {byte_order.upper()} card@{card_base:04X} attr@{attr_base:04X}: "
                          f"{hits}/{len(KNOWN_BT)} matches{marker}")

print(f"\n=== BEST CONFIGURATION: {best_hits}/{len(KNOWN_BT)} matches ===")
if best_config:
    bo, cb, ab, al, hits, attr, card = best_config
    print(f"  Byte order: {bo.upper()}")
    print(f"  Card table: file offset {cb:04X} (RAM ${0x5000 + cb//2:04X})")
    print(f"  Attr table: file offset {ab:04X} (RAM ${0x5000 + ab//2:04X})")
    
    print(f"\n  Card table (first 16 entries):")
    for i in range(16):
        print(f"    [{i:2d}] ${0x65A0+i:04X}: ${card[i]:04X}  (card={card[i]&0x7FF}, GRAM={bool(card[i]&0x0800)})")
    
    print(f"\n  Attr table (first 16 entries):")
    for i in range(16):
        print(f"    [{i:2d}] ${0x65B7+i:04X}: ${attr[i]:04X}")
    
    print(f"\n  L_5EC7 for stream tiles:")
    for tv in STREAM_TILES[:12]:
        bt = l5ec7(tv, attr, card)
        card_num = bt & 0x7FF
        gram = "G" if bt & 0x0800 else "g"
        fg = ((bt >> 13) & 0x6) | ((bt >> 12) & 0x1)
        cs = (bt >> 13) & 1
        print(f"    tile=${tv:04X} (>>5={tv>>5:2d}) -> BT=${bt:04X}  card={card_num:3d} {gram} FG={fg} CS={cs}")
    
    print(f"\n  All BACKTAB words produced by tiles 0-255:")
    all_bt = set()
    for tv in range(256):
        all_bt.add(l5ec7(tv, attr, card))
    for bt in sorted(all_bt):
        card_num = bt & 0x7FF
        gram = "G" if bt & 0x0800 else "g"
        fg = ((bt >> 13) & 0x6) | ((bt >> 12) & 0x1)
        cs = (bt >> 13) & 1
        in_known = " (*)" if bt in KNOWN_BT else ""
        print(f"    BT=${bt:04X}  card={card_num:3d} {gram} FG={fg} CS={cs}{in_known}")
