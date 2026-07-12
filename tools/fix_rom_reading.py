#!/usr/bin/env python3
"""Read ROM with correct mapping (LE + 6-byte header) and verify L_5EC7."""
import struct, sys, os

sys.stdout.reconfigure(encoding='cp1252', errors='replace')

ROM_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Swords and Serpents.bin")
with open(ROM_PATH, 'rb') as f:
    rom = f.read()

def rw_le(addr):
    """Read 16-bit word at CPU address from ROM (LE, 6-byte header)."""
    if addr < 0x5000 or addr > 0x6FFF:
        return 0
    offset = (addr - 0x5000) + 6
    if offset + 1 < len(rom):
        return struct.unpack_from('<H', rom, offset)[0]
    return 0

# ============================================================
# Part 1: Read and display lookup tables
# ============================================================
print("=" * 70)
print("ROM DATA (LE + 6-byte header)")
print("=" * 70)

# Card table ($65A0 area, up to SDBD table at $65CE)
print("\n--- Card Table area ($65A0-$65B6) ---")
card_vals = []
for i in range(23):
    addr = 0x65A0 + i
    w = rw_le(addr)
    card_vals.append(w)
    print(f"  ${addr:04X}: ${w:04X}  (idx {i})")

# Attribute table ($65B7 area)
print("\n--- Attribute Table area ($65B7-$65CD) ---")
attr_vals = []
for i in range(23):
    addr = 0x65B7 + i
    w = rw_le(addr)
    attr_vals.append(w)
    print(f"  ${addr:04X}: ${w:04X}  (idx {i})")

# SDBD pointer table
print("\n--- SDBD Pointer Table ($65CE+) ---")
for i in range(16):
    addr = 0x65CE + i
    lo_byte = rw_le(addr) & 0xFF
    hi_byte = rw_le(addr + 1) & 0xFF
    ptr = (hi_byte << 8) | lo_byte
    in_range = "ROM" if 0x5000 <= ptr <= 0x6FFF else "OUT"
    print(f"  ${addr:04X}: lo=${lo_byte:02X} + ${addr+1:04X}: hi=${hi_byte:02X}  ->  ${'$'}${ptr:04X}  [{in_range}]")

# ============================================================
# Part 2: Simulate L_5EC7 (correct algorithm from disassembly)
# ============================================================
print("\n" + "=" * 70)
print("L_5EC7 BACKTAB SIMULATION (correct tables)")
print("=" * 70)

def l5ec7(tile_val, attr_table, card_table):
    """Exact L_5EC7 algorithm from disassembly $5EC7-$5EE1."""
    idx = tile_val >> 5  # SLR x3 = >>5
    if idx >= len(attr_table) - 1 or idx >= len(card_table):
        return 0
    
    attr0 = attr_table[idx]
    attr1 = attr_table[idx + 1]  # MVI@ R3,R1 increments R3, then XOR@ R3,R1
    card = card_table[idx]       # MVI@ R5,R3 reads from card table
    
    # Attribute processing
    r1 = attr0 >> 2              # SLR R1, 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)  # SWAP R1, 1
    r1 ^= attr1                  # XOR@ R3, R1
    r1 &= 0x3607                 # ANDI #$3607
    
    # Card processing  
    r3 = (card << 3) & 0xFFFF    # SLL R3,2; SLL R3,1
    r1 ^= r3                     # XORR R3, R1
    
    return r1

def decode_bt(w):
    return {
        'card': w & 0x7FF,
        'gram': bool(w & 0x0800),
        'fg': ((w >> 13) & 0x6) | ((w >> 12) & 0x1),
        'cs': (w >> 13) & 1,
    }

# Test with tile values from the trace
print("\nTile values from data stream at $6D86:")
stream_data = [0x000A, 0x0122, 0x0061, 0x0125, 0x0061, 0x0126, 
               0x0061, 0x0128, 0x0061, 0x0127, 0x000B, 0x0121]

for tv in stream_data:
    bt = l5ec7(tv, attr_vals, card_vals)
    d = decode_bt(bt)
    print(f"  tile=${tv:04X} (>>5={tv>>5:2d})  ->  BT=${bt:04X}  card={d['card']:3d}  {'GRAM' if d['gram'] else 'GROM'}  FG={d['fg']}  CS={d['cs']}")

# Test with floor tile (should be $1603 based on jzIntv BACKTAB)
print("\nBrute-force search: which tile values produce BACKTAB=$1603?")
for tv in range(256):
    bt = l5ec7(tv, attr_vals, card_vals)
    if bt == 0x1603:
        d = decode_bt(bt)
        print(f"  tile=${tv:04X} (>>5={tv>>5:2d}) -> BT=${bt:04X}")

# Test with ALL unique BACKTAB values seen in room 0 from jzIntv
print("\nMapping tile values to known jzIntv BACKTAB words (room 0):")
jz_bt_words = sorted(set([
    0x1603, 0x081B, 0x1E13, 0x020F, 0x02B7, 0x02A7, 0x0257, 0x0287,
    0x02BF, 0x029F, 0x025F, 0x0207, 0x0327, 0x0317, 0x1EBB, 0x026F,
    0x024F, 0x022F, 0x021F, 0x023F, 0x03AF, 0x03EF, 0x03E7, 0x03B7,
    0x1E5B, 0x1E40, 0x0E60, 0x0823, 0x1E38, 0x1E02, 0x082B, 0x0367,
    0x0347, 0x036F, 0x03BF
]))

# For each BACKTAB word seen on screen, find which tile values could produce it
bt_to_tiles = {}
for tv in range(256):
    bt = l5ec7(tv, attr_vals, card_vals)
    if bt not in bt_to_tiles:
        bt_to_tiles[bt] = []
    bt_to_tiles[bt].append(tv)

for bt in jz_bt_words:
    tiles = bt_to_tiles.get(bt, [])
    d = decode_bt(bt)
    print(f"  BT=${bt:04X}  card={d['card']:3d} {'G' if d['gram'] else 'g'} FG={d['fg']} CS={d['cs']}  <-  tiles: {[f'${t:02X}' for t in tiles[:6]]}{'...' if len(tiles)>6 else ''}")

# ============================================================
# Part 3: Compare with jzIntv memory dump (expected)
# ============================================================
print("\n" + "=" * 70)
print("VALIDATION: Check if ROM data should match jzIntv")
print("=" * 70)
print("Expected jzIntv first few words at $65CE area:")
print("  $65CE: $0098  $65CF: $006C  $65D0: $0011  $65D1: $006D")
print()
print("ROM reads at same addresses:")
for addr in range(0x65CE, 0x65D2):
    w = rw_le(addr)
    print(f"  ${addr:04X}: ${w:04X}  {'MATCH' if addr==0x65CE and w==0x0098 else ''}{'MATCH' if addr==0x65CF and w==0x006C else ''}{'MATCH' if addr==0x65D0 and w==0x0011 else ''}{'MATCH' if addr==0x65D1 and w==0x006D else ''}")

print("\nDone.")
