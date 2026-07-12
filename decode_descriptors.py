"""Decode all sprite descriptors in the $5B28-$5B68 range and examine their targets."""
rom = open("Swords and Serpents.bin", "rb").read()

def rom_byte(addr):
    off = (addr - 0x5000) * 2
    return rom[off + 1]

def rom_word(addr):
    off = (addr - 0x5000) * 2
    return (rom[off] << 8) | rom[off + 1]

def pixel_count(addr, nbytes=8):
    total = 0
    for i in range(nbytes):
        total += bin(rom_byte(addr + i)).count("1")
    return total

def ascii_card(addr):
    lines = []
    for i in range(8):
        b = rom_byte(addr + i)
        lines.append("".join("#" if (b>>(7-c))&1 else "." for c in range(8)))
    return "\n".join(lines)

# Decode descriptors at $5B28, $5B2C, $5B30, $5B34, $5B38, $5B3C, $5B40, $5B44
print("=== DESCRIPTOR TABLE $5B28-$5B44 ===")
for i in range(8):
    addr = 0x5B28 + i * 4
    w0 = rom_word(addr)
    w1 = rom_word(addr + 1)
    w2 = rom_word(addr + 2)
    w3 = rom_word(addr + 3)
    w2_target = (w2 << 3) & 0xFFFF if w2 else 0
    w3_target = (w3 << 3) & 0xFFFF if w3 else 0
    print(f"\nDescriptor ${addr:04X}: w0=${w0:04X} w1=${w1:04X} w2=${w2:04X} (-> ${w2_target:04X}) w3=${w3:04X} (-> ${w3_target:04X})")

# Now examine each target address and surrounding data
targets = set()
for i in range(8):
    addr = 0x5B28 + i * 4
    w2 = rom_word(addr + 2)
    w3 = rom_word(addr + 3)
    if w2:
        targets.add((w2 << 3) & 0xFFFF)
    if w3:
        targets.add((w3 << 3) & 0xFFFF)

print(f"\n\n=== UNIQUE DESCRIPTOR TARGETS ({len(targets)}) ===")
for t in sorted(targets):
    print(f"\n--- Target ${t:04X} ---")
    px_total = 0
    for ci in range(16):  # examine up to 16 cards
        ca = t + ci * 8
        px = pixel_count(ca, 8)
        if px == 0:
            break
        px_total += px
    print(f"  Cards from ${t:04X}: {px_total} total pixels over {ci} cards")
    
    # Show first 4 cards as ASCII
    for ci in range(min(4, ci)):
        ca = t + ci * 8
        print(f"  Card {ci} @ ${ca:04X} ({pixel_count(ca,8)} px):")
        for line in ascii_card(ca).split("\n"):
            print(f"    {line}")
