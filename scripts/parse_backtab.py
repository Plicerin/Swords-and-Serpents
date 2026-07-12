#!/usr/bin/env python3
"""Parse jzIntv BackTab hex dump and decode dungeon room layout."""

# Raw jzIntv "m 0200 f0" output
dump_raw = """0200:  1603* 1603  1603  1603   1603  1603  1603  1603
0208:  1603  1603  1603  1603   1603  1603  1603  1603
0210:  1603  1603  1603  1603   1603  1603  1603  1603
0218:  1603  1603  1603  1603   1603  1603  1603  1603
0220:  1603  1603  1603  1603   1603  1603  1603  1603
0228:  1603  1603  179B  17BB   177B  1793  1723  179B
0230:  1603  1633  1603  179B   172B  1793  1783  172B
0238:  1773  17A3  179B  1603   1603  1603  1603  1603
0240:  1603  1603  1603  1603   1603  1603  1603  1603
0248:  1603  1603  1603  1603   1603  1603  1603  1603
0250:  1603  1603  1603  1603   1603  1EBB  1603  174B
0258:  176B  170B  173B  174B   171B  1603  168B  16CB
0260:  16C3  1693  1603  1603   1603  1603  1603  1603
0268:  1603  1603  1603  1603   1603  1603  1603  1603
0270:  1603  1603  1603  1603   1603  1603  1603  1603
0278:  1603  1603  1603  1603   1603  1603  1603  1603
0280:  1603  1603  1603  1603   1603  1603  1603  1603
0288:  1603  1603  1603  1603   1603  1603  1603  1603
0290:  1603  1603  1603  1603   1603  1603  1603  1603
0298:  1603  1603  1603  1603   1603  1603  1603  1603
02A0:  1603  1603  1603  1603   1603  1603  1603  1603
02A8:  1603  1603  1603  1603   1603  1603  1603  1603
02B0:  1603  1603  1603  1603   1603  1603  172B  1773
02B8:  17A3  172B  1793  1603   173B  170B  176B  172B
02C0:  1603  1643  168B  1663   1693  1663  169B  164B
02C8:  1603  1603  1603  1603   1603  1603  1603  1603
02D0:  1603  1603  1603  1603   1603  1603  1603  1603
02D8:  1603  1603  1603  1603   1603  1603  1603  1603
02E0:  1603  1603  1603  1603   1603  1603  1603  1603
02E8:  1603  1603  1603  1603   1603  1603  1603  1603"""

# Parse: each line has start address then 8 hex values
# Each hex value = 16-bit word = 2 bytes (big-endian)
# Bytes are arranged sequentially in memory
all_bytes = []
for line in dump_raw.strip().split('\n'):
    parts = line.split()
    # Extract 4-character hex values (skip address like "0200:")
    hex_vals = []
    for p in parts:
        p = p.replace('*', '')  # remove jzIntv marker
        if len(p) == 4 and all(c in '0123456789ABCDEFabcdef' for c in p):
            hex_vals.append(p)
    
    for hv in hex_vals:
        val = int(hv, 16)
        hi = (val >> 8) & 0xFF
        lo = val & 0xFF
        all_bytes.append(hi)
        all_bytes.append(lo)

print(f"Parsed {len(all_bytes)} bytes total")
print(f"Expecting 240 bytes for 20x12 BackTab")

# Trim or warn
if len(all_bytes) > 240:
    print(f"WARNING: {len(all_bytes)} bytes, trimming to 240")
    all_bytes = all_bytes[:240]
elif len(all_bytes) < 240:
    print(f"WARNING: only {len(all_bytes)} bytes")

# Arrange as 20 columns x 12 rows
# BackTab is row-major: row 0 = $0200-$0213 (20 bytes), row 1 = $0214-$0227, etc.
COLS = 20
ROWS = 12
grid = [[0]*COLS for _ in range(ROWS)]
for i, b in enumerate(all_bytes):
    if i >= COLS * ROWS:
        break
    row = i // COLS
    col = i % COLS
    grid[row][col] = b

# Decode STIC 8-bit BACKTAB format:
# Bit 7: GRAM/GROM (0=GROM cards 0-63, 1=GRAM cards 0-63)
# Bit 6: Color Stack Advance
# Bits 5-2: Card number (4 bits for COLOR STACK mode, combined with bit 7)
# Bits 1-0: Foreground color? NO...
#
# Actually standard STIC BACKTAB byte format (Color Stack mode):
# Bit 7: 1 = advance color stack
# Bit 6: 0 = GROM, 1 = GRAM
# Bits 5-3: Card number upper
# Bits 2-0: Foreground color
# BUT this depends on mode.
#
# For FOREGROUND/BACKGROUND mode:
# Bit 7: GRAM/GROM
# Bit 6: (unused or part of card)
# Bits 5-3: Card number (3 bits)
# Bits 2-0: FG Color (3 bits)
# Total: card = bit7*8 + bits5-3 = 0-15 (GROM) or 16-31 (GRAM)
#
# Let me use this interpretation:
# Card (5 bits, 0-31): (byte >> 3) & 0x1F
# FG Color (3 bits, 0-7): byte & 0x07
# GRAM flag: (byte >> 7) & 1 (1=GRAM, 0=GROM)

print("\n=== 20×12 BackTab Grid ===")
print("    " + "".join(f"{c:2d} " for c in range(COLS)))
for r in range(ROWS):
    print(f"R{r:2d}: ", end="")
    for c in range(COLS):
        b = grid[r][c]
        card = (b >> 3) & 0x1F
        fg = b & 0x07
        gram = (b >> 7) & 1
        
        # Color coding
        if gram:
            # GRAM card - dungeon tile!
            print(f"\033[1;33m{card:2d}:{fg}\033[0m ", end="")
        elif card == 2 and fg == 6:
            # GROM card 2, FG Yellow - default?
            print(f"\033[2m{card:2d}:{fg}\033[0m ", end="")
        elif card == 0 and fg == 3:
            # GROM card 0, FG Tan
            print(f"\033[2m{card:2d}:{fg}\033[0m ", end="")
        else:
            print(f"{card:2d}:{fg} ", end="")
    print()

# Show unique bytes and their decoded values
print("\n=== Unique BackTab values ===")
seen = {}
for r in range(ROWS):
    for c in range(COLS):
        b = grid[r][c]
        if b not in seen:
            card = (b >> 3) & 0x1F
            fg = b & 0x07
            gram = (b >> 7) & 1
            csa = (b >> 6) & 1
            seen[b] = {
                'hex': f"${b:02X}",
                'gram': gram,
                'csa': csa,
                'card': card,
                'fg': fg,
                'count': 0,
                'positions': []
            }
        seen[b]['count'] += 1
        seen[b]['positions'].append((r, c))

for b, info in sorted(seen.items()):
    gram_str = "GRAM" if info['gram'] else "GROM"
    csa_str = "CSA" if info['csa'] else "   "
    print(f"  {info['hex']} ({b:3d}) → {gram_str} card={info['card']:2d} FG={info['fg']} {csa_str} count={info['count']:3d}")

# Show the dungeon room as ASCII art
print("\n=== Dungeon Room (ASCII) ===")
# Group by card type for the legend
card_chars = {}
char_idx = 0
char_palette = '#*+@%$&!=~^'
for r in range(ROWS):
    line = ""
    for c in range(COLS):
        b = grid[r][c]
        card = (b >> 3) & 0x1F
        gram = (b >> 7) & 1
        if gram:
            key = f"G{card}"
        else:
            key = f"g{card}"
        if key not in card_chars:
            card_chars[key] = char_palette[char_idx % len(char_palette)]
            char_idx += 1
        line += card_chars[key]
    print(f"  {line}")

print("\n=== Legend ===")
for key, ch in sorted(card_chars.items()):
    gram = key[0] == 'G'
    card = int(key[1:])
    gram_str = "GRAM" if gram else "GROM"
    print(f"  {ch} = {gram_str} card {card}")
