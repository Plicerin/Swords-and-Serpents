"""Dump exact sprite bytes for use in TypeScript code."""
rom = open("Swords and Serpents.bin", "rb").read()

def rom_bytes(addr, count):
    off = (addr - 0x5000) * 2
    return [rom[off + 2*i + 1] for i in range(count)]

def fmt(data, cols=8):
    """Format as comma-separated hex bytes, wrapping at cols."""
    parts = []
    for i, b in enumerate(data):
        parts.append(f"0x{b:02X}")
    return ", ".join(parts)

# Player sprites at $5BCC (5 frames)
print("=== Player sprite data ($5BCC-$5C1B) ===")
for frame in range(5):
    addr = 0x5BCC + frame * 16
    data = rom_bytes(addr, 16)
    print(f"Frame {frame}: [{fmt(data)}]")

# Wizard sprites at $5C9C (2 frames)
print("\n=== Wizard sprite data ($5C9C-$5CBB) ===")
data0 = rom_bytes(0x5C9C, 16)
data1 = rom_bytes(0x5CAC, 16)
print(f"Frame 0: [{fmt(data0)}]")
print(f"Frame 1: [{fmt(data1)}]")

# Fireball sprites at $5C4E
print("\n=== Fireball data ($5C4E-$5C6D) ===")
for i in range(4):
    addr = 0x5C4E + i * 8
    data = rom_bytes(addr, 8)
    print(f"Card {i}: [{fmt(data)}]")

# Spawn effect at $5AE6
print("\n=== Spawn effect ($5AE6-$5B05) ===")
for i in range(4):
    addr = 0x5AE6 + i * 8
    data = rom_bytes(addr, 8)
    print(f"Card {i}: [{fmt(data)}]")
