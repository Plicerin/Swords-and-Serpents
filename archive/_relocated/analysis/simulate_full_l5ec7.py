#!/usr/bin/env python3
"""Full L_5EC7 simulation: all tile values 0-2047, compare with jzIntv BACKTAB."""
import sys
sys.stdout.reconfigure(encoding='cp1252', errors='replace')

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

def rw_be(addr):
    """Read BE word from ROM at CPU address."""
    off = (addr - 0x5000) * 2
    if off + 1 >= len(rom):
        return 0
    return (rom[off] << 8) | rom[off + 1]

# Read tables
print("=== READING TABLES FROM ROM ===")
attr = []
for i in range(24):
    w = rw_be(0x65B7 + i)
    attr.append(w)
    print(f"  attr[{i:2d}] @${0x65B7+i:04X}: ${w:04X}")

card = []
for i in range(24):
    w = rw_be(0x65A0 + i)
    card.append(w)
    print(f"  card[{i:2d}] @${0x65A0+i:04X}: ${w:04X}  (<<3=${(w<<3)&0xFFFF:04X})")

def l5ec7(tile_val):
    """Exact L_5EC7 algorithm."""
    idx = tile_val >> 5
    if idx + 1 >= len(attr) or idx >= len(card):
        return 0
    
    attr0 = attr[idx]
    attr1 = attr[idx + 1]
    card_val = card[idx]
    
    # Attribute processing
    r1 = attr0 >> 2                    # SLR R1, 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)  # SWAP R1, 1
    r1 ^= attr1                        # XOR@ R3, R1
    r1 &= 0x3607                       # ANDI #$3607
    
    # Card modifier
    r3 = (card_val << 3) & 0xFFFF      # SLL R3, 2; SLL R3, 1
    r1 ^= r3                           # XORR R3, R1
    
    return r1

def decode_bt(w):
    """Decode BACKTAB word."""
    return {
        'card': w & 0x7FF,
        'gram': "GRAM" if w & 0x0800 else "GROM",
        'fg': ((w >> 13) & 0x6) | ((w >> 12) & 0x1),
        'cs': (w >> 13) & 1,
        'fg_bit_summary': f"b14={(w>>14)&1} b13={(w>>13)&1} b12={(w>>12)&1}"
    }

# Known jzIntv BACKTAB words from room 0
KNOWN_BT = {
    0x1603, 0x081B, 0x1E13, 0x020F, 0x02B7, 0x02A7, 0x0257, 0x0287,
    0x02BF, 0x029F, 0x025F, 0x0207, 0x0327, 0x0317, 0x1EBB, 0x026F,
    0x024F, 0x022F, 0x021F, 0x023F, 0x03AF, 0x03EF, 0x03E7, 0x03B7,
    0x1E5B, 0x1E40, 0x0E60, 0x0823, 0x1E38, 0x1E02, 0x082B, 0x0367,
    0x0347, 0x036F, 0x03BF,
}

# Simulate ALL tile values
print("\n=== L_5EC7 RESULTS FOR ALL TILE GROUPS (0-22) ===")
print(f"{'idx':>4} {'tile range':>12} {'BACKTAB':>6} {'card':>5} {'GRAM':>5} {'FG':>3} {'CS':>3} {'known?':>7}")
print("-" * 60)

all_produced = {}
for idx in range(23):
    tv = idx << 5  # lowest tile value for this group
    bt = l5ec7(tv)
    d = decode_bt(bt)
    known = "YES" if bt in KNOWN_BT else ""
    all_produced[idx] = bt
    print(f"  {idx:3d}  {tv:5d}-{tv+31:5d}  ${bt:04X}  {d['card']:4d} {d['gram']:>5}  {d['fg']:2d}  {d['cs']:2d}  {known}")

# Compare with known BACKTAB
print("\n=== MATCH ANALYSIS ===")
matched = set()
for idx, bt in all_produced.items():
    if bt in KNOWN_BT:
        matched.add(bt)

print(f"L_5EC7 produces {len(all_produced)} unique BACKTAB values (indices 0-22)")
print(f"Known jzIntv set: {len(KNOWN_BT)} values")
print(f"Matched: {len(matched)}")
print(f"Unmatched (produced but not seen): {len(all_produced.values()) - len(matched)}")
print(f"Unmatched (seen but not produced): {len(KNOWN_BT - matched)}")

if KNOWN_BT - matched:
    print(f"\nBACKTAB words seen in jzIntv but NOT produced by L_5EC7:")
    for bt in sorted(KNOWN_BT - matched):
        d = decode_bt(bt)
        print(f"  ${bt:04X}: card={d['card']:4d} {d['gram']} FG={d['fg']} CS={d['cs']}")

if set(all_produced.values()) - KNOWN_BT:
    print(f"\nBACKTAB words produced by L_5EC7 but NOT seen in jzIntv room 0:")
    for bt in sorted(set(all_produced.values()) - KNOWN_BT):
        idx = [k for k,v in all_produced.items() if v == bt][0]
        d = decode_bt(bt)
        print(f"  idx={idx:2d} -> ${bt:04X}: card={d['card']:4d} {d['gram']} FG={d['fg']} CS={d['cs']}")

# Also test tiles 0-255 to see ALL producible values
print("\n=== ALL TILES 0-255: unique BACKTAB words ===")
unique_bt = set()
for tv in range(256):
    unique_bt.add(l5ec7(tv))

print(f"Tiles 0-255 produce {len(unique_bt)} unique BACKTAB words (max 8 groups)")
# Since 0-255 / 32 = 0-7, maximum 8 unique values

# Show actual stream tile processing
STREAM = [0x000A, 0x0122, 0x0061, 0x0125, 0x0061, 0x0126,
          0x0061, 0x0128, 0x0061, 0x0127, 0x000B, 0x0121]

print("\n=== STREAM TILE PROCESSING (from $6D86) ===")
for tv in STREAM:
    bt = l5ec7(tv)
    d = decode_bt(bt)
    known = " *" if bt in KNOWN_BT else ""
    print(f"  tile=${tv:04X} (>>5={tv>>5:2d}) -> BT=${bt:04X} card={d['card']:4d} {d['gram']} FG={d['fg']} CS={d['cs']}{known}")
