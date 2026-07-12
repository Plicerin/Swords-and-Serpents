#!/usr/bin/env python3
"""Dump and verify the $65A0 and $65B7 tables from ROM"""
import struct, os

rom_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Swords and Serpents.bin")
with open(rom_path, 'rb') as f:
    rom = f.read()

def rw_be(addr):
    """Read 16-bit big-endian word at CPU address"""
    off = (addr - 0x5000) * 2
    return (rom[off] << 8) | rom[off + 1]

print("=== Raw bytes at $65A0 (Card table, 8 words) ===")
for i in range(8):
    addr = 0x65A0 + i
    w = rw_be(addr)
    print(f"  ${addr:04X}: ${w:04X}  (bin: {w:016b})")

print()
print("=== Raw bytes at $65B7 (Attribute table, 8 words) ===")
for i in range(8):
    addr = 0x65B7 + i
    w = rw_be(addr)
    print(f"  ${addr:04X}: ${w:04X}  (bin: {w:016b})")

print()
print("=== Manual L_5EC7 trace for tile index 0 ===")
print("Using attr[0]=$%04X and attr[1]=$%04X" % (rw_be(0x65B7), rw_be(0x65B8)))
print("Using card[0]=$%04X" % rw_be(0x65A0))

attr0 = rw_be(0x65B7)
attr1 = rw_be(0x65B8)
card0 = rw_be(0x65A0)

# Step through L_5EC7
r1 = attr0 >> 2
print(f"  SLR R1,2:  R1 = ${r1:04X} ({r1:016b})")
r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)  # SWAP
print(f"  SWAP R1,1: R1 = ${r1:04X} ({r1:016b})")
r1 = r1 ^ attr1
print(f"  XOR@ R3,R1: R1 = ${r1:04X} ({r1:016b})  (XOR with ${attr1:04X})")
r1 = r1 & 0x3607
print(f"  ANDI #$3607: R1 = ${r1:04X} ({r1:016b})")

r3 = card0 << 3
print(f"  SLL R3,3:  R3 = ${r3:04X} ({r3:016b})")
r1 = r1 ^ r3
print(f"  XORR R3,R1: R1 = ${r1:04X} ({r1:016b})")

print()
print("BACKTAB decode:")
card = r1 & 0x7FF
is_gram = bool(r1 & 0x0800)
fg = ((r1 >> 13) & 0x6) | ((r1 >> 12) & 0x1)
cs = (r1 >> 13) & 1
print(f"  Card={card}, GRAM={is_gram}, FG={fg}, CS_advance={cs}")
print(f"  Expected from jzIntv: $1603 (card=3, GRAM=True, FG=1, CS=0)")

print()
print("=== jzIntv BACKTAB values seen in room 0 ===")
# Unique BACKTAB values from jzIntv dump
seen = {0x1603, 0x081B, 0x1E13, 0x020F, 0x02B7, 0x02A7, 0x0257, 0x0287, 
        0x02BF, 0x029F, 0x025F, 0x0207, 0x0327, 0x0317, 0x1EBB, 0x026F,
        0x024F, 0x022F, 0x021F, 0x023F, 0x03AF, 0x03EF, 0x03E7, 0x03B7,
        0x1E5B, 0x1E40, 0x0E60, 0x0823, 0x1E38, 0x1E02, 0x082B, 0x0367,
        0x0347, 0x036F, 0x03BF}
for w in sorted(seen):
    card = w & 0x7FF
    gram = "G" if w & 0x0800 else "g"
    fg = ((w >> 13) & 0x6) | ((w >> 12) & 0x1)
    cs = (w >> 13) & 1
    print(f"  ${w:04X}: card={card:4d} {gram} FG={fg} CS={cs}")
