import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

def rw(addr):
    """Read big-endian 16-bit word at CP-1610 address using Method 1"""
    offset = (addr - 0x5000) * 2
    if offset + 1 >= len(rom):
        return 0
    return (rom[offset] << 8) | rom[offset + 1]

# Check raw bytes around 655E
addr = 0x655E
offset = (addr - 0x5000) * 2
print('Address $655E -> offset {} (0x{:04X})'.format(offset, offset))
print('Bytes at offset -2: {:02X} {:02X}'.format(rom[offset-2], rom[offset-1]))
print('Bytes at offset +0: {:02X} {:02X}  -> word = ${:04X}'.format(
    rom[offset], rom[offset+1], (rom[offset]<<8)|rom[offset+1]))
print('Bytes at offset +2: {:02X} {:02X}'.format(rom[offset+2], rom[offset+3]))
print()

# FULL object table dump
print('=== Object Type Table ($655E-$659D) - 32 entries ===')
for i in range(32):
    a = 0x655E + i * 2
    w = rw(a)
    card = w & 0x3F
    fg = (w >> 11) & 7
    gram = (w >> 13) & 1
    print('  [{:2d}] ${:04X}: ${:04X}  card=${:02X}  fg=${:01X}  gram={}'.format(i, a, w, card, fg, gram))

print()
print('=== Type Index Table ($6580-$659F) ===')
for i in range(16):
    a = 0x6580 + i * 2
    w = rw(a)
    hi = (w >> 8) & 0xFF
    lo = w & 0xFF
    t0 = hi >> 4
    t1 = hi & 0x0F
    t2 = lo >> 4
    t3 = lo & 0x0F
    print('  [{:2d}] ${:04X}: ${:04X}  types=[{},{},{},{}]'.format(i, a, w, t0, t1, t2, t3))

print()
print('=== Room Data ($64DE-$655D) - First 64 words ===')
for i in range(64):
    a = 0x64DE + i * 2
    w = rw(a)
    x = w & 0xFF
    y = (w >> 8) & 0xFF
    print('  [{:2d}] ${:04X}: ${:04X}  x=${:02X}  y=${:02X}'.format(i, a, w, x, y))
