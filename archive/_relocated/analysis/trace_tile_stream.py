#!/usr/bin/env python3
"""
DEFINITIVE TILE STREAM TRACER
=============================
Reads the ROM tile stream data (SDBD pointers → RLE encoded streams),
parses the format, runs L_5EC7 on each tile descriptor, and compares
with the actual BACKTAB from JZINTV.

If mismatches are found, brute-forces the correct attr/card table entries.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

rom = open('Swords and Serpents.bin', 'rb').read()

def rw(addr):
    """Read 16-bit big-endian word at CP1610 ROM address $5000-$6FFF."""
    off = (addr - 0x5000) * 2
    if off + 1 < len(rom):
        return (rom[off] << 8) | rom[off + 1]
    return 0

def rb(addr):
    """Read 8-bit byte at CP1610 ROM address."""
    off = (addr - 0x5000) * 2
    if off < len(rom):
        return rom[off]
    return 0

# =========================================================================
# SDBD pointer table
# =========================================================================
def decode_sdbd_table(base=0x65CE):
    """Decode SDBD pointer table (overlapping, 1-word stride)."""
    pointers = []
    for i in range(16):
        lo0 = rb(base + i)
        lo1 = rb(base + i + 1)
        ptr = (lo1 << 8) | lo0
        pointers.append(ptr)
    return pointers

# =========================================================================
# L_5EC7: BACKTAB word construction
# =========================================================================
def l5ec7(tile_descriptor, attr_table, card_table):
    """Compute BACKTAB word from tile descriptor using L_5EC7 algorithm."""
    group = tile_descriptor >> 5
    
    # Get attr and card for this group
    if group < len(attr_table):
        a_g = attr_table[group]
    else:
        a_g = rw(0x65B7 + group) if 0x65B7 + group <= 0x6FFF else 0
    
    if group + 1 < len(attr_table):
        a_next = attr_table[group + 1]
    else:
        a_next = rw(0x65B7 + group + 1) if 0x65B7 + group + 1 <= 0x6FFF else 0
    
    if group < len(card_table):
        c = card_table[group]
    else:
        c = rw(0x65A0 + group) if 0x65A0 + group <= 0x6FFF else 0
    
    # L_5EC7 attr processing
    r1 = a_g >> 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)  # SWAP
    r1 ^= a_next
    # SDBD ANDI #$3607: byte-wise AND
    r1 = ((r1 & 0xFF) & 0x07) | (((r1 >> 8) & 0xFF) & 0x36) << 8
    
    # Card processing
    r3 = (c << 3) & 0xFFFF
    
    bt = (r1 ^ r3) & 0xFFFF
    return bt

# =========================================================================
# ROM Tables
# =========================================================================
ATTR_BASE = 0x65B7
CARD_BASE = 0x65A0

attr_rom = [rw(ATTR_BASE + i) for i in range(32)]
card_rom = [rw(CARD_BASE + i) for i in range(32)]

print("=" * 100)
print("ROM ATTR TABLE (32 entries)")
print("=" * 100)
for i in range(32):
    print(f"  [{i:2d}] ${ATTR_BASE+i:04X}: ${attr_rom[i]:04X}")
print()

print("=" * 100)
print("ROM CARD TABLE (32 entries)")
print("=" * 100)
for i in range(32):
    print(f"  [{i:2d}] ${CARD_BASE+i:04X}: ${card_rom[i]:04X}")
print()

# =========================================================================
# SDBD Table and Tile Streams
# =========================================================================
sdbd_pointers = decode_sdbd_table()
print("=" * 100)
print("SDBD POINTER TABLE (16 overlapping entries)")
print("=" * 100)
for i, ptr in enumerate(sdbd_pointers):
    in_rom = 0x5000 <= ptr <= 0x6FFF
    print(f"  [{i:2d}] ${ptr:04X}  {'[ROM]' if in_rom else '[OUT OF RANGE]'}")
print()

# =========================================================================
# Read Tile Streams from ROM
# =========================================================================
print("=" * 100)
print("TILE STREAM DATA (from SDBD pointers)")
print("=" * 100)

def read_stream(ptr, max_words=64):
    """Read a tile stream from ROM at the given pointer."""
    if not (0x5000 <= ptr <= 0x6FFF):
        return []
    words = []
    addr = ptr
    for _ in range(max_words):
        w = rw(addr)
        words.append((addr, w))
        addr += 1
    return words

for i, ptr in enumerate(sdbd_pointers):
    if not (0x5000 <= ptr <= 0x6FFF):
        continue
    # Read up to 16 words from this stream
    stream = read_stream(ptr, 16)
    
    if not stream:
        continue
    
    print(f"\n  Stream [{i}] at ${ptr:04X}:")
    
    # Parse RLE format
    pos = 0
    col = 0
    for addr, word in stream:
        span = word & 0x1F  # low 5 bits: column span
        upper = word >> 5   # upper bits: type encoding
        bt = l5ec7(word, attr_rom, card_rom)
        
        print(f"    ${addr:04X}: ${word:04X}  span={span:2d}  type=${upper:3d}(${upper:04X})  L5EC7→${bt:04X}  " + 
              f"[{'GRAM' if bt & 0x0800 else 'GROM'} card={bt & 0x7FF:3d} FG={((bt>>13)&6)|((bt>>12)&1)}]" + 
              f"  {'WALL' if bt == 0x1603 else ''}{'DOOR' if bt in (0x081B,0x0823,0x082B) else ''}")
        
        pos += 1
        col += span
    
    # Show the 8 non-overlapping entries (even indices)
    if i % 2 == 0:
        pass  # already shown in the full list

# =========================================================================
# Analyze: what tile types exist in the tile stream?
# =========================================================================
print()
print("=" * 100)
print("UNIQUE TILE DESCRIPTORS IN ALL STREAMS")
print("=" * 100)

all_descriptors = set()
descriptor_to_streams = {}

for i, ptr in enumerate(sdbd_pointers):
    if not (0x5000 <= ptr <= 0x6FFF):
        continue
    stream = read_stream(ptr, 32)
    for addr, word in stream:
        all_descriptors.add(word)
        if word not in descriptor_to_streams:
            descriptor_to_streams[word] = []
        descriptor_to_streams[word].append(i)

print(f"  Total unique descriptors: {len(all_descriptors)}")
print()
print(f"  {'Descriptor':>8s} | {'Group':>5s} | {'span':>4s} | {'L5EC7→BT':>8s} | {'Streams':>10s}")
print(f"  {'-'*8} | {'-'*5} | {'-'*4} | {'-'*8} | {'-'*10}")

for word in sorted(all_descriptors):
    group = word >> 5
    span = word & 0x1F
    bt = l5ec7(word, attr_rom, card_rom)
    streams = descriptor_to_streams[word]
    stream_str = ",".join(str(s) for s in streams[:5])
    if len(streams) > 5:
        stream_str += f"...+{len(streams)-5}"
    print(f"  ${word:04X}     | {group:5d} | {span:4d} | ${bt:04X}    | {stream_str}")

# =========================================================================
# Compare with actual BACKTAB
# =========================================================================
print()
print("=" * 100)
print("COMPARE L5EC7 OUTPUT WITH ACTUAL BACKTAB")
print("=" * 100)

# Actual BACKTAB from room 0
BACKTAB_GRID = [
    [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1E13,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    [0x1603,0x1603,0x1603,0x1603,0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603],
    [0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x081B,0x1603,0x02BF,0x029F,0x025F,0x02B7,0x0207,0x02BF,0x0327,0x0317,0x0327,0x02BF],
    [0x020F,0x02B7,0x02A7,0x020F,0x0257,0x0287,0x02BF,0x0823,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603],
    [0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1EBB,0x0327,0x026F,0x024F,0x022F,0x021F,0x026F],
    [0x023F,0x0327,0x03AF,0x03EF,0x03E7,0x03B7,0x1603,0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603],
    [0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603,0x081B,0x1603,0x1603,0x1603,0x0E60,0x1603],
    [0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1E5B,0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603],
    [0x1603,0x1E40,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1E40,0x1603,0x1603,0x1603,0x1603,0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603],
    [0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x020F,0x0257,0x0287,0x020F,0x02B7,0x0327,0x021F,0x022F,0x024F,0x020F,0x0327],
    [0x0367,0x03AF,0x0347,0x03B7,0x0347,0x03BF,0x036F,0x0823,0x1E38,0x1603,0x1603,0x1603,0x1E02,0x082B,0x0823,0x0823,0x0823,0x0823,0x0823,0x081B],
    [0x1603,0x1603,0x0823,0x0823,0x0823,0x0823,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x081B,0x1603,0x1603,0x1603,0x1603,0x1603,0x1603,0x081B],
]

ALL_BT_SET = set(w for row in BACKTAB_GRID for w in row)
ALL_BT = sorted(ALL_BT_SET)
BT_SIM = set()

for word in all_descriptors:
    bt = l5ec7(word, attr_rom, card_rom)
    BT_SIM.add(bt)

matched = BT_SIM & ALL_BT_SET
unmatched_sim = BT_SIM - ALL_BT_SET
unmatched_actual = ALL_BT_SET - BT_SIM

print(f"  Unique L5EC7 outputs from tile descriptors: {len(BT_SIM)}")
print(f"  Matched BACKTAB words: {len(matched)}")
print(f"  Simulated but not in actual: {sorted([f'${w:04X}' for w in unmatched_sim])}")
print(f"  Actual but not simulated: {sorted([f'${w:04X}' for w in unmatched_actual])}")
print()

# For the unmatched actual words, show what descriptor+group would produce them
if unmatched_actual:
    print("=" * 100)
    print("REVERSE: What descriptor groups produce unmatched BACKTAB words?")
    print("=" * 100)
    
    for bt in sorted(unmatched_actual):
        print(f"\n  BACKTAB ${bt:04X}:")
        solutions = []
        for g in range(32):
            r1_attr = l5ec7(g << 5, attr_rom, card_rom)  # get r1_attr part
            # Actually this doesn't isolate r1_attr... 
            # Let's compute properly
            a_g = attr_rom[g] if g < len(attr_rom) else rw(ATTR_BASE + g)
            a_next = attr_rom[g+1] if g+1 < len(attr_rom) else rw(ATTR_BASE + g + 1)
            c = card_rom[g] if g < len(card_rom) else rw(CARD_BASE + g)
            
            r1 = a_g >> 2
            r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
            r1 ^= a_next
            r1 = ((r1 & 0xFF) & 0x07) | (((r1 >> 8) & 0xFF) & 0x36) << 8
            
            # We need: r1 ^ (card << 3) = bt
            # So: card = (bt ^ r1) >> 3
            needed_card = (bt ^ r1) >> 3
            if (bt ^ r1) & 0x7 == 0 and 0 <= needed_card <= 0x1FF:
                solutions.append((g, needed_card, r1))
        
        if solutions:
            for g, nc, r1a in solutions[:6]:
                print(f"    Group {g:2d}: needed_card=${nc:03X}, r1_attr=${r1a:04X}")
            if len(solutions) > 6:
                print(f"    ... and {len(solutions)-6} more")
        else:
            # Try with arbitrary card
            print(f"    NO group can produce this with any card 0-0x1FF")
            print(f"    Need r1_attr where r1_attr ^ (card<<3) = ${bt:04X}")
            for card_test in [0, 0x40, 0x80, 0xC0, 0x100]:
                needed_r1 = bt ^ ((card_test << 3) & 0xFFFF)
                print(f"      card=${card_test:03X} → need r1_attr=${needed_r1:04X}")

print()
print("=" * 100)
print("DONE")
print("=" * 100)
