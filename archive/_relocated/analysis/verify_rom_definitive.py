#!/usr/bin/env python3
"""Definitive ROM mapping verification: BE, offset=(addr-0x5000)*2."""
import struct, sys

sys.stdout.reconfigure(encoding='cp1252', errors='replace')

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

def rw_be(addr):
    """Read BE word at CPU address."""
    if addr < 0x5000 or addr > 0x6FFF:
        return 0
    off = (addr - 0x5000) * 2
    return (rom[off] << 8) | rom[off + 1] if off + 1 < len(rom) else 0

# ============================================================
# Verify $65CE SDBD table against known jzIntv values
# ============================================================
print("=== VERIFY $65CE (jzIntv shows: $0098 $006C $0011 $006D $0086 $006D...) ===")
expected_65CE = [0x0098, 0x006C, 0x0011, 0x006D, 0x0086, 0x006D, 0x0013, 0x006E,
                 0x009E, 0x006E, 0x0020, 0x006F, 0x009E, 0x006F, 0x0042, 0x006A]
match_count = 0
for i, exp in enumerate(expected_65CE):
    addr = 0x65CE + i
    actual = rw_be(addr)
    ok = actual == exp
    if ok: match_count += 1
    print(f"  ${addr:04X}: ROM=${actual:04X} jzIntv=${exp:04X}  {'OK' if ok else 'MISMATCH!'}")
print(f"  Match: {match_count}/{len(expected_65CE)}")
print()

# ============================================================
# Verify $6D86 tile stream - what does ROM have vs jzIntv?
# ============================================================
print("=== VERIFY $6D86 (jzIntv tile stream) ===")
print("jzIntv dump at $6D86: 000A 0122 0061 0125 0061 0126 0061 0128 0061 0127")
for i in range(12):
    addr = 0x6D86 + i
    w = rw_be(addr)
    print(f"  ${addr:04X}: ${w:04X}")
print()

# ============================================================
# Dump $65A0 area fully (card table)
# ============================================================
print("=== CARD TABLE at $65A0 (23 words) ===")
card_vals = []
for i in range(23):
    addr = 0x65A0 + i
    w = rw_be(addr)
    card_vals.append(w)
    if i < 16:
        print(f"  [{i:2d}] ${addr:04X}: ${w:04X}")
    else:
        print(f"  [{i:2d}] ${addr:04X}: ${w:04X}")

# ============================================================
# Dump $65B7 area (attribute table)
# ============================================================
print("\n=== ATTR TABLE at $65B7 (23 words) ===")
attr_vals = []
for i in range(23):
    addr = 0x65B7 + i
    w = rw_be(addr)
    attr_vals.append(w)
    if i < 16:
        print(f"  [{i:2d}] ${addr:04X}: ${w:04X}")
    else:
        print(f"  [{i:2d}] ${addr:04X}: ${w:04X}")

# ============================================================
# L_5EC7 simulation with actual values
# ============================================================
print("\n=== L_5EC7 SIMULATION ===")

def l5ec7(tile_val):
    """Exact L_5EC7: tile_val>>5 indexes attr[idx], attr[idx+1], card[idx]."""
    idx = tile_val >> 5
    if idx + 1 >= len(attr_vals) or idx >= len(card_vals):
        return 0
    attr0 = attr_vals[idx]
    attr1 = attr_vals[idx + 1]   # XOR@ reads NEXT word after MVI@ increment
    card  = card_vals[idx]       # MVI@ reads from card table
    
    r1 = attr0 >> 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)  # SWAP
    r1 ^= attr1
    r1 &= 0x3607
    r3 = (card << 3) & 0xFFFF
    r1 ^= r3
    return r1

# Tile stream data from jzIntv dump at $6D86
stream_data = [0x000A, 0x0122, 0x0061, 0x0125, 0x0061, 0x0126,
               0x0061, 0x0128, 0x0061, 0x0127, 0x000B, 0x0121]

print("Stream values -> BACKTAB:")
for tv in stream_data:
    bt = l5ec7(tv)
    card = bt & 0x7FF
    gram = "G" if bt & 0x0800 else "g"
    fg = ((bt >> 13) & 0x6) | ((bt >> 12) & 0x1)
    cs = (bt >> 13) & 1
    print(f"  tile=${tv:04X} (>>5={tv>>5}) -> BT=${bt:04X}  card={card:3d} {gram} FG={fg} CS={cs}")

# ============================================================
# Known BACKTAB words from jzIntv room 0
# ============================================================
print("\n=== JZINTV BACKTAB words mapped to tile values ===")
jz_bts = sorted(set([
    0x1603, 0x081B, 0x1E13, 0x020F, 0x02B7, 0x02A7, 0x0257, 0x0287,
    0x02BF, 0x029F, 0x025F, 0x0207, 0x0327, 0x0317, 0x1EBB, 0x026F,
    0x024F, 0x022F, 0x021F, 0x023F, 0x03AF, 0x03EF, 0x03E7, 0x03B7,
    0x1E5B, 0x1E40, 0x0E60, 0x0823, 0x1E38, 0x1E02, 0x082B, 0x0367,
    0x0347, 0x036F, 0x03BF
]))

# Build reverse map
bt_to_tiles = {}
all_produced = set()
for tv in range(256):
    bt = l5ec7(tv)
    all_produced.add(bt)
    if bt not in bt_to_tiles:
        bt_to_tiles[bt] = []
    bt_to_tiles[bt].append(tv)

print(f"L_5EC7 produces {len(all_produced)} unique BACKTAB words for tiles 0-255")
print()

hits = 0
misses = 0
for bt in jz_bts:
    tiles = bt_to_tiles.get(bt, [])
    if tiles:
        hits += 1
        print(f"  BT=${bt:04X} MATCHED by tiles: {[f'${t:02X}' for t in tiles[:8]]}{'...' if len(tiles)>8 else ''}")
    else:
        misses += 1
        print(f"  BT=${bt:04X} NO MATCH - cannot be produced by L_5EC7!")

print(f"\n  Matched: {hits}/{len(jz_bts)}, Unmatched: {misses}/{len(jz_bts)}")
print(f"  Accuracy: {hits/len(jz_bts)*100:.1f}%")

# ============================================================
# Raw bytes dump at key offsets
# ============================================================
print("\n=== RAW ROM BYTES at $65A0, $65B7, $65CE, $6D86 ===")
for desc, addr in [("$65A0 card tbl", 0x65A0), ("$65B7 attr tbl", 0x65B7),
                    ("$65CE SDBD tbl", 0x65CE), ("$6D86 tile stream", 0x6D86)]:
    off = (addr - 0x5000) * 2
    print(f"\n{desc} (file offset {off:04X}):")
    for i in range(8):
        a = addr + i
        o = off + i * 2
        if o + 1 < len(rom):
            b = (rom[o] << 8) | rom[o + 1]
            print(f"  ${a:04X}: file[{o:04X}]={rom[o]:02X} {rom[o+1]:02X}  BE=${b:04X}")
