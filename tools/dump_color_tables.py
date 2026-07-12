import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

def rw(addr):
    off = (addr - 0x5000) * 2
    return (rom[off] << 8) | rom[off + 1] if off + 1 < len(rom) else 0

print('=== Color table at $65A0-$65B6 (background tile colors) ===')
for i in range(12):
    a = 0x65A0 + i * 2
    w = rw(a)
    # L_5EC7 uses this: SLL 3 (shift left 3), XOR with tile data
    # This means the color bits are in bits 2-0 or similar
    # Check: bits shifted left 3 -> in BACKTAB positions 11-8 (FG/BG color area)
    fg = (w >> 5) & 7   # after <<3, bits 2-0 move to 5-3
    bg = (w >> 3) & 3
    gram = (w >> 0) & 1
    print('  ${:04X}: ${:04X}  bin={:016b}  raw_bits={}'.format(a, w, w, w))

print()
print('=== Tile map at $65B7-$65DB (background tile definitions) ===')
for i in range(19):
    a = 0x65B7 + i * 2
    w = rw(a)
    print('  ${:04X}: ${:04X}  bin={:016b}'.format(a, w, w))

print()
print('=== Data at $65DC-$660F ===')
for i in range(26):
    a = 0x65DC + i * 2
    w = rw(a)
    print('  ${:04X}: ${:04X}'.format(a, w))

print()
print('=== Cross-ref: Object table cards vs BACKTAB color values ===')
print()
# Actual BACKTAB values observed in the JZINTV dump (from conversation history)
# Most objects show $16xx or $17xx prefix
# $16 = FG=1($16 >> 11 = 0001 0110 >> 11 = 0... actually)
# $16 in binary: 0001 0110
# Bits 12-11: 01 = color 1 (blue)
# $17 in binary: 0001 0111
# Bits 12-11: 01 = color 1 (blue)
# So both $16xx and $17xx use FG color 1

print('Backtab format for GROM (bit13=0):')
print('  Bit 15-14: flag')
print('  Bit 13: 0=GROM')
print('  Bit 12-11: FG color (0-7)')
print('  Bit 10: reserved')
print('  Bit 9-8: BG color (0-3)')
print('  Bit 7-0: card number')
print()
print('$1600 = FG=1(blue), BG=0(black), card=0')
print('$1700 = FG=1(blue), BG=1(grey?), card=0')
print()
print('Object table card $3E (entry 0) + $1600 = $163E')
print('Object table card $2B (entry 10) + $1700 = $172B  <- matches BACKTAB!')
print('Object table card $33 (entry ?) + $1700 = $1733')
print()
# Check: where does the $16 vs $17 choice come from?
# Looking at the type index: different type indices map to different colors

print('=== Testing type-to-color hypothesis ===')
print()
# Let me check if type index nibble values determine color
# Type index [0] $6580: nibbles [13, 12, 0, 1]
# These reference object table entries:
# Type 13 -> object[13] = $005B (card $1B)
# Type 12 -> object[12] = $0053 (card $13)  
# Type 0  -> object[0]  = $007E (card $3E)
# Type 1  -> object[1]  = $0087 (card $07)

# The room data at $64DE:
# [0] X=$14 Y=$00 -> uses type from index[0], nibble 0 = 13 -> object[13]=$005B

# But where's the color? Maybe the room data Y byte encodes color?
# Y=$00 -> BG color 0?
# Let me check: in the BACKTAB, objects have $16/$17 prefix
# If Y byte high nibble encodes FG color:
# X=$14 Y=$00 -> no extra color info
# Maybe the color is per-type, stored elsewhere

print('Room data first 4 entries with type lookup:')
for i in range(16):
    a = 0x64DE + i * 2
    w = rw(a)
    x = w & 0xFF
    y = (w >> 8) & 0xFF
    # Calculate type index
    tidx = i // 2
    nibble_pos = i % 2
    ti_a = 0x6580 + tidx * 2
    ti_w = rw(ti_a)
    # Extract nibble
    if nibble_pos == 0:
        # Lower nibble of the word
        nibble = ti_w & 0xF
    else:
        # Wait, the nibble extraction in the code is more complex
        # For now just print what we have
        nibble = '?'
    print('  [{}] ${:04X}: x=${:02X} y=${:02X}'.format(i, a, x, y))
