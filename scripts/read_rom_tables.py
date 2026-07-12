rom = open('Swords and Serpents.bin', 'rb').read()
print(f'ROM: {len(rom)} bytes')

def w(addr):
    off = (addr - 0x5000) * 2
    if off + 1 < len(rom):
        return (rom[off] << 8) | rom[off+1]
    return None

print('=== Table at $65A0 ===')
for i in range(16):
    val = w(0x65A0 + i)
    print(f'  {0x65A0+i:04X}: {val:04X}')

print()
print('=== Data at $5A17 (16 words) ===')
for i in range(16):
    val = w(0x5A17 + i)
    print(f'  {0x5A17+i:04X}: {val:04X}')
