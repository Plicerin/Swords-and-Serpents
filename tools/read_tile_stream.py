#!/usr/bin/env python3
"""Read tile stream data at SDBD pointers and decode RLE format."""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

rom = open('Swords and Serpents.bin', 'rb').read()

def rw(addr):
    off = (addr - 0x5000) * 2
    if off + 1 < len(rom):
        return (rom[off] << 8) | rom[off + 1]
    return 0

def l5ec7(word):
    """Compute BACKTAB via L_5EC7 on tile descriptor word."""
    group = word >> 5
    a_g = rw(0x65B7 + group)
    a_next = rw(0x65B7 + group + 1)
    c = rw(0x65A0 + group)
    
    r1 = (a_g >> 2) & 0xFFFF
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    r1 ^= a_next
    r1 = ((r1 & 0xFF) & 0x07) | (((r1 >> 8) & 0xFF) & 0x36) << 8
    bt = r1 ^ ((c << 3) & 0xFFFF)
    return bt, group, r1, c

# SDBD pointers (even entries from decoded table)
SDBD_PTRS = {0: 0x6C98, 2: 0x6D11, 4: 0x6D86, 6: 0x6E13,
             8: 0x6E9E, 10: 0x6F20, 12: 0x6F9E, 14: 0x6A42}

# Actual BACKTAB
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
ALL_BT = set(w for row in BACKTAB_GRID for w in row)

print("=" * 100)
print("TILE STREAM DATA AT SDBD POINTERS")
print("=" * 100)

for sdbd_idx, ptr in sorted(SDBD_PTRS.items()):
    print(f"\n{'='*100}")
    print(f"SDBD[{sdbd_idx}] → ROM ${ptr:04X}")
    print(f"{'='*100}")
    
    # Read up to 32 words from this pointer
    total_span = 0
    bt_found = set()
    
    print(f"  {'Addr':>8s} | {'Word':>6s} | {'span':>4s} | {'group':>5s} | {'r1_attr':>8s} | {'card':>6s} | {'BACKTAB':>8s} | {'Match':>5s} | {'cum_col':>7s}")
    print(f"  {'-'*8} | {'-'*6} | {'-'*4} | {'-'*5} | {'-'*8} | {'-'*6} | {'-'*8} | {'-'*5} | {'-'*7}")
    
    for i in range(32):
        addr = ptr + i
        w = rw(addr)
        span = w & 0x1F
        group = w >> 5
        bt, g, r1a, card = l5ec7(w)
        
        match = "YES" if bt in ALL_BT else ""
        if bt in ALL_BT:
            bt_found.add(bt)
        
        total_span += span
        
        print(f"  ${addr:04X}   | ${w:04X}  | {span:4d} | {group:5d} | ${r1a:04X}    | ${card:04X}  | ${bt:04X}    | {match:5s} | {total_span:7d}")
        
        if total_span >= 20:
            break
    
    print(f"\n  BACKTAB words produced by this stream: {sorted(['${0:04X}'.format(b) for b in bt_found])}")

print()
print("=" * 100)
print("ANALYSIS: Room data table at $65DC")
print("=" * 100)

# Read sub-table pointers at $65DC (at offsets 0, 2, 4, 6 — the even entries after >>3)
print("  Sub-table pointers (from G_02F4 = $65DC):")
for i in range(8):
    w = rw(0x65DC + i)
    print(f"    [${i}] ${w:04X}   ", end="")
    if i % 4 == 3:
        print()

print()
print("  Sub-table entries (row groups 0-7 and 8-11):")
# Follow the first sub-table pointer
ptr0 = rw(0x65DC)
for i in range(8):
    w = rw(ptr0 + i)
    print(f"    [${i}] at ${ptr0+i:04X}: ${w:04X}")

print()
print("=" * 100)
print("SUMMARY: All BACKTAB words producible from SDBD-referenced tile streams")
print("=" * 100)

all_bt_from_streams = set()
all_groups_used = set()
for sdbd_idx, ptr in sorted(SDBD_PTRS.items()):
    for i in range(64):
        w = rw(ptr + i)
        span = w & 0x1F
        if span == 0 or span > 20:
            break
        bt, g, r1a, card = l5ec7(w)
        all_bt_from_streams.add(bt)
        all_groups_used.add(g)

print(f"  Total unique BACKTAB words: {len(all_bt_from_streams)}")
print(f"  Words: {sorted(['${0:04X}'.format(b) for b in all_bt_from_streams])}")
print(f"  Groups used: {sorted(all_groups_used)}")
print()
matched = all_bt_from_streams & ALL_BT
print(f"  Matched with actual BACKTAB: {len(matched)}")
print(f"  Matched: {sorted(['${0:04X}'.format(b) for b in matched])}")
print()
missing = ALL_BT - all_bt_from_streams
print(f"  Missing ({len(missing)}): {sorted(['${0:04X}({1})'.format(w, sum(row.count(w) for row in BACKTAB_GRID)) for w in missing])}")

print()
print("=" * 100)
print("DONE")
print("=" * 100)
