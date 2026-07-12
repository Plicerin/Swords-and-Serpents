#!/usr/bin/env python3
"""Dump ROM room data to understand the tile stream structure."""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

rom = open('Swords and Serpents.bin', 'rb').read()

def rw(addr):
    off = (addr - 0x5000) * 2
    if off + 1 < len(rom):
        return (rom[off] << 8) | rom[off + 1]
    return 0

print("=" * 100)
print("ROM DATA: $65DC - $6650 (Room data area)")
print("=" * 100)

# Dump as 16-bit words, organized to look for patterns
for base in range(0x65DC, 0x6650, 16):
    print(f"  ${base:04X}: ", end="")
    for i in range(16):
        w = rw(base + i)
        card_num = w & 0x7FF
        fg = ((w >> 13) & 0x6) | ((w >> 12) & 0x1)
        is_gram = bool(w & 0x0800)
        # Check if it looks like a BACKTAB word
        in_bt = "BT" if w in [0x1603,0x081B,0x0823,0x082B,0x0E60,0x1E02,0x1E13,0x1E38,0x1E40,0x1E5B,0x1EBB] else ""
        if 0x0200 <= w <= 0x03FF:
            in_bt = "FLR"
        print(f"${w:04X} ", end="")
    print()

print()
print("=" * 100)
print("ROM DATA: $6600 - $66FF (potential tile stream)")
print("=" * 100)

for base in range(0x6600, 0x6700, 16):
    print(f"  ${base:04X}: ", end="")
    for i in range(16):
        w = rw(base + i)
        span = w & 0x1F
        group = w >> 5
        print(f"${w:04X} ", end="")
    print()

print()
print("=" * 100)
print("DECODING TILE STREAM: look for RLE patterns (span in low 5 bits)")
print("=" * 100)

# Scan for potential tile stream data: words with small span values (0-19)
for base in range(0x6600, 0x6E00, 16):
    # Check if this looks like an RLE stream with valid spans
    spans = [rw(base+i) & 0x1F for i in range(16)]
    groups = [rw(base+i) >> 5 for i in range(16)]
    # A stream is valid if spans are in the range 1-20 and groups aren't all the same
    valid_spans = sum(1 for s in spans if 1 <= s <= 20)
    if valid_spans >= 8:
        print(f"\n  Potential stream at ${base:04X}:")
        print(f"  {'Addr':>8s} | {'Word':>6s} | {'span':>4s} | {'group':>5s} | {'L5EC7→BT':>8s}")
        print(f"  {'-'*8} | {'-'*6} | {'-'*4} | {'-'*5} | {'-'*8}")
        for i in range(min(16, 32)):
            w = rw(base + i)
            span = w & 0x1F
            group = w >> 5
            # Compute L5EC7
            a_g = rw(0x65B7 + group)
            a_n = rw(0x65B7 + group + 1)
            c = rw(0x65A0 + group)
            r1 = (a_g >> 2) & 0xFFFF
            r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
            r1 ^= a_n
            r1 = ((r1 & 0xFF) & 0x07) | (((r1 >> 8) & 0xFF) & 0x36) << 8
            bt = r1 ^ ((c << 3) & 0xFFFF)
            tag = ""
            if bt in [0x1603,0x081B,0x0823,0x082B,0x0E60,0x1E02,0x1E13,0x1E38,0x1E40,0x1E5B,0x1EBB]:
                tag = "BT"
            elif 0x0200 <= bt <= 0x03FF:
                tag = "FLR"
            print(f"  ${base+i:04X} | ${w:04X}  | {span:4d} | {group:5d} | ${bt:04X} {tag}")
        if base > 0x6700:
            break

print()
print("=" * 100)
print("SDBD TABLE ANALYSIS: $65CE decoded as overlapping byte pairs")
print("=" * 100)

# The SDBD table at $65CE: each SDBD+MVI@ reads two consecutive ROM words
# and extracts the low byte from each
# For address A: low_byte = (rw(A) & 0xFF), high_byte = (rw(A+1) & 0xFF)
# ptr = (high_byte << 8) | low_byte
for i in range(16):
    lo_w = rw(0x65CE + i)
    hi_w = rw(0x65CE + i + 1)
    lo_byte = lo_w & 0xFF
    hi_byte = hi_w & 0xFF
    ptr = (hi_byte << 8) | lo_byte
    in_rom = 0x5000 <= ptr <= 0x6FFF
    print(f"  [{i:2d}] lo=${lo_byte:02X} hi=${hi_byte:02X} → ptr=${ptr:04X} {'[ROM]' if in_rom else '[OUT OF RANGE]'}  (raw: ${lo_w:04X} ${hi_w:04X})")

print()
print("=" * 100)
print("DONE")
print("=" * 100)
