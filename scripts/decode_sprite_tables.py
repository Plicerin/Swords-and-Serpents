import struct

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

print(f'ROM size: {len(rom)} bytes')

def rom_word(addr):
    """Read a 16-bit big-endian word from ROM at logical Intellivision address."""
    off = (addr - 0x5000) * 2
    if off + 1 < len(rom):
        return (rom[off] << 8) | rom[off + 1]
    return 0

def rom_bytes(addr, count):
    """Read count bytes from ROM at logical address.
    Each ROM DECLE stores 8-bit data in the lo byte."""
    off = (addr - 0x5000) * 2
    result = []
    for i in range(count):
        pos = off + 2*i + 1  # lo byte of each 16-bit word
        if pos < len(rom):
            result.append(rom[pos])
        else:
            result.append(0)
    return result

print('\n=== Table at $5555 (MOB attribute init, XOR $0800 before stored to $0335) ===')
for i in range(8):
    word = rom_word(0x5555 + i)
    print(f'  $5555+{i}: ${word:04X}  -> XOR $0800 = ${word ^ 0x0800:04X}')

for addr, label in [(0x5B28, '$5B28'), (0x5B5E, '$5B5E'), (0x5B9A, '$5B9A'), (0x5BAE, '$5BAE')]:
    print(f'\n=== Code at {label} (first 8 words) ===')
    for i in range(8):
        word = rom_word(addr + i)
        print(f'  {label}+{i}: ${word:04X}')

for addr, label in [(0x62DE, '$62DE'), (0x6300, '$6300'), (0x6302, '$6302'), (0x630A, '$630A')]:
    print(f'\n=== Sprite data at {label} (16 words as lo-byte rows) ===')
    for i in range(16):
        word = rom_word(addr + i)
        lo = word & 0xFF
        hi = (word >> 8) & 0xFF
        bits = ''.join('#' if (lo >> (7-c)) & 1 else '.' for c in range(8))
        print(f'  {label}+{i}: ${word:04X}  lo=${lo:02X}  {bits}')

# Read the RLE data at $61E7
print('\n=== RLE data at $61E7 (first 16 words) ===')
for i in range(16):
    word = rom_word(0x61E7 + i)
    lo = word & 0xFF
    repeat = ((word >> 8) & 0x03) + 1
    print(f'  $61E7+{i}: ${word:04X}  byte=${lo:02X}  repeat={repeat}')

# Read the sprite pointer table at $5C4C (used at boot $5039)
print('\n=== Sprite pointer table at $5C4C (first 8 words) ===')
for i in range(8):
    word = rom_word(0x5C4C + i)
    print(f'  $5C4C+{i}: ${word:04X}')

# Decode the full RLE block
print('\n=== Full RLE decode ===')
gram_off = rom_word(0x61E7)
count = rom_word(0x61E8)
print(f'  GRAM offset: ${gram_off:04X} (card {gram_off // 8})')
print(f'  Entry count: {count}')
rle_bytes = []
for i in range(count):
    entry = rom_word(0x61E9 + i)
    byte_val = entry & 0xFF
    repeat = ((entry >> 8) & 0x03) + 1
    rle_bytes.extend([byte_val] * repeat)
print(f'  Decompressed: {len(rle_bytes)} bytes = {len(rle_bytes) // 8} cards')
for ci in range(min(8, len(rle_bytes) // 8)):
    card = rle_bytes[ci*8:(ci+1)*8]
    bits = [''.join('#' if (b >> (7-c)) & 1 else '.' for c in range(8)) for b in card]
    print(f'  Card {ci}: {" ".join(f"${b:02X}" for b in card)}')
    for line in bits:
        print(f'    {line}')
