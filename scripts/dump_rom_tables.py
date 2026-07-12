"""Dump ROM tables for room BACKTAB reverse-engineering."""
rom = open('Swords and Serpents.bin', 'rb').read()

def read_word(addr):
    off = (addr - 0x5000) * 2
    if off + 1 < len(rom):
        return (rom[off] << 8) | rom[off + 1]
    return None

def read_byte(addr):
    off = (addr - 0x5000) * 2
    if off < len(rom):
        return rom[off]
    return None

print("=== Header check ===")
for a in [0x5000, 0x5002, 0x5004, 0x5006, 0x5008, 0x500A, 0x500C]:
    print(f"  {a:04X}: {read_word(a):04X}")

print("\n=== Table at $65A0 (64 words) ===")
for i in range(64):
    val = read_word(0x65A0 + i)
    print(f"  {0x65A0+i:04X}: {val:04X}")

print("\n=== Data at $65B7 (64 words) ===")
for i in range(64):
    val = read_word(0x65B7 + i)
    print(f"  {0x65B7+i:04X}: {val:04X}")

print("\n=== Data at $65DC (64 words) ===")
for i in range(64):
    val = read_word(0x65DC + i)
    print(f"  {0x65DC+i:04X}: {val:04X}")

print("\n=== Room param table at $5A17 (32 words) ===")
for i in range(32):
    val = read_word(0x5A17 + i)
    print(f"  {0x5A17+i:04X}: {val:04X}")

print("\n=== Room param table at $5A40 (32 words) ===")
for i in range(32):
    val = read_word(0x5A40 + i)
    print(f"  {0x5A40+i:04X}: {val:04X}")

print("\n=== Data at $5A5B (32 words) ===")
for i in range(32):
    val = read_word(0x5A5B + i)
    print(f"  {0x5A5B+i:04X}: {val:04X}")

print("\n=== Scratchpad $00CE area (as words) ===")
for i in range(16):
    val = read_word(0x00CE + i)
    print(f"  {0x00CE+i:04X}: {val:04X}")
