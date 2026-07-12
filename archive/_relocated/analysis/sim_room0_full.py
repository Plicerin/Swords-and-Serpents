#!/usr/bin/env python3
"""Full room 0 BACKTAB simulation tracing L_5EE2 -> L_5EC7."""

import sys
sys.stdout.reconfigure(encoding='cp1252', errors='replace')

rom = open('Swords and Serpents.bin', 'rb').read()

def rw(addr):
    """Read 16-bit big-endian word from ROM at 16-bit word address."""
    off = (addr - 0x5000) * 2
    if off + 1 >= len(rom):
        return 0
    return (rom[off] << 8) | rom[off + 1]

def rw_sdbd(addr):
    """Read SDBD-style 8-bit from ROM — lower byte of 16-bit word."""
    off = (addr - 0x5000) * 2
    if off + 1 >= len(rom):
        return 0
    return rom[off + 1]  # lower byte in big-endian

# ============================================================
# L_55BF sets up:
#   G_02F4 = $65DC  (room data pointer table base)
#   G_02F5 = $65B7  (attr table base)
#   G_0175 = 2
#   G_0176 = 26 ($1A)
# ============================================================

g_02f4 = 0x65DC  # pointer to table
g_02f5 = 0x65B7  # attr table
g_0175 = 2
g_0176 = 26  # $1A

# ============================================================
# L_5E48: reads data from stream pointed to by G_02F4
# Returns R2 (tile stream byte pointer), R1 (count/control)
# ============================================================

# Actually, let me trace the full L_5EE2 loop:

# L_5EE2:
#   MVI G_0175, R2   → R2 = 2
#   MVI G_0176, R0   → R0 = 26
#   MVO R0, G_0178   → G_0178 = 26
#   MVII #$0200, R4  → R4 = $0200 (BACKTAB pointer)

r2 = g_0175  # = 2
g_0178 = g_0176  # = 26
r4 = 0x0200  # BACKTAB base

backtab = {}  # address -> value

# L_5E48 reads the data stream:
#   MVI G_02F4, R4   → R4 = $65DC
#   SDBD; MVI@ R4, R2 → R2 = byte at ROM[$65DC]
#   INCR R4          → R4 = $65DD
#   SDBD; MVI@ R4, R1 → R1 = byte at ROM[$65DD]
#   INCR R4
#   ; Then processes R1 (attr table index?) and R2 (card table index?)

# Let me read what's actually at these ROM locations
print("=== Data at G_02F4 pointer ($65DC) ===")
w0 = rw(0x65DC)
b0_lo = rw_sdbd(0x65DC)  # SDBD read
print(f"  $65DC: word=${w0:04X}, SDBD byte=${b0_lo:02X}")

# But wait - L_5E48 uses INCR on R4, so it's incrementing the ADDRESS
# R4 = $65DC → increment → R4 = $65DD
w1 = rw(0x65DD)
b1_lo = rw_sdbd(0x65DD)
print(f"  $65DD: word=${w1:04X}, SDBD byte=${b1_lo:02X}")

w2 = rw(0x65DE)
b2_lo = rw_sdbd(0x65DE)
print(f"  $65DE: word=${w2:04X}, SDBD byte=${b2_lo:02X}")

# ============================================================
# Let me trace L_5E48 more carefully from the disassembly
# ============================================================

# Read L_5E48 full code:
print("\n=== Tracing L_5E48 full routine ===")

# L_5E48:
#   MVI G_02F4, R4    → R4 = 0x65DC
#   SDBD
#   MVI@ R4, R2       → R2 = byte at ROM[0x65DC] = 0x00 (?)
#   INCR R4           → R4 = 0x65DD
#   SDBD               
#   MVI@ R4, R1       → R1 = byte at ROM[0x65DD] = 0x42 (?)
#   INCR R4           → R4 = 0x65DE
#   ; ... then some processing
#   ; ... returns with R2 pointing into tile stream

# Actually, let me look at what follows L_5E48:
# After first SDBD read, there's processing:
#   MOVR R2, R0
#   ANDI #$001F, R0   
#   CMPI #$001F, R0
# etc.

# Let me just dump the relevant ROM data
print("\n=== Dumping first 32 words from $65DC (room pointer table) ===")
for i in range(32):
    w = rw(0x65DC + i)
    b = rw_sdbd(0x65DC + i)
    marker = ""
    if b != 0:
        marker = f" * byte={b:02X}"
    print(f"  ${0x65DC+i:04X}: ${w:04X}{marker}")

print("\n=== Dumping first 32 words from $65B7 (attr table) ===")
for i in range(32):
    w = rw(0x65B7 + i)
    print(f"  ${0x65B7+i:04X}: ${w:04X}", end="")
    if (i+1) % 4 == 0:
        print()

print("\n=== Object table at $64DE (room 0, 16 entries x 2 words) ===")
for i in range(16):
    w0 = rw(0x64DE + i*2)
    w1 = rw(0x64DE + i*2 + 1)
    print(f"  [{i:2d}] ${0x64DE+i*2:04X}: Y=${w0:04X}, X=${w1:04X}")

print("\n=== GROM card table at $655E (first 64 entries) ===")
for i in range(64):
    w = rw(0x655E + i)
    if w != 0:
        card = w >> 3
        fg = w & 7
        print(f"  [{i:2d}] ${0x655E+i:04X}: ${w:04X} (card={card:3d}, FG={fg})")

# Now let's also dump the $6580 table
print("\n=== Card index table at $6580 (first 32 entries) ===")
for i in range(32):
    w = rw(0x6580 + i)
    if w != 0:
        print(f"  [{i:2d}] ${0x6580+i:04X}: ${w:04X}")
