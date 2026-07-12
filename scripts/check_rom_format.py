rom = open('Swords and Serpents.bin', 'rb').read()
print(f'ROM file size: {len(rom)} bytes')

# Test: read at offset corresponding to $5A17
off = (0x5A17 - 0x5000) * 2
print(f'Offset for $5A17: {off} (0x{off:04X})')
print(f'  bytes: {rom[off]:02X} {rom[off+1]:02X}')
print(f'  big-endian word: {(rom[off] << 8) | rom[off+1]:04X}')
print(f'  little-endian word: {(rom[off+1] << 8) | rom[off]:04X}')

# Disassembly says: DECLE $0062, $000B, $000C, $001A at $5A17
# So $5A17 should be 0x0062
print()
print('Expected from disassembly:')
print('  $5A17 = 0x0062')
print('  $5A18 = 0x000B')
print('  $5A19 = 0x000C')
print('  $5A1A = 0x001A')

# Now read from odd bytes (de-interleaved)
rom_odd = bytes(rom[i] for i in range(1, len(rom), 2))
off2 = 0x5A17 - 0x5000
print()
print(f'Odd-byte offset: {off2}')
print(f'  bytes: {rom_odd[off2]:02X} {rom_odd[off2+1]:02X}')
print(f'  big-endian word: {(rom_odd[off2] << 8) | rom_odd[off2+1]:04X}')
