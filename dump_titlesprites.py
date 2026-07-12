"""Dump title screen sprites (may be the combat encounter sprites)."""
rom = open("Swords and Serpents.bin", "rb").read()

def rom_byte(addr):
    off = (addr - 0x5000) * 2
    return rom[off + 1]

def ascii_card(addr):
    lines = []
    for i in range(8):
        b = rom_byte(addr + i)
        lines.append("".join("#" if (b>>(7-c))&1 else "." for c in range(8)))
    return "\n".join(lines)

# Warrior side frame ($6300) and head ($62DE)
print("=== Title Screen Sprites ===\n")
print("--- Warrior head $62DE (1 card, 8x8) ---")
print(ascii_card(0x62DE))
print()
print("--- Warrior side $6300 (1 card, 8x8) ---")
print(ascii_card(0x6300))
print()
print("--- Wizard head $6302 ---")
print(ascii_card(0x6302))
print()
print("--- Wizard side $630A ---")
print(ascii_card(0x630A))
print()

# RLE header
def rom_word(addr):
    off = (addr - 0x5000) * 2
    return (rom[off] << 8) | rom[off + 1]

gram_off = rom_word(0x61E7)
count = rom_word(0x61E8)
print(f"--- RLE at $61E7: gram_off=${gram_off:04X}, count={count} ---")
print()

# RLE entries from $61E9
entries = []
for i in range(count):
    entry = rom_word(0x61E9 + i)
    byte_val = entry & 0xFF
    repeat = ((entry >> 8) & 0x03) + 1
    entries.extend([byte_val] * repeat)
    if i < 5:
        print(f"  Entry {i}: word=${entry:04X} byte=${byte_val:02X} repeat={repeat}")

print(f"\n  Total decompressed bytes: {len(entries)}")
print(f"  Total cards: {len(entries)//8}")

# Show RLE cards as ASCII
print("\n--- RLE cards ---")
for ci in range(len(entries)//8):
    card = entries[ci*8:(ci+1)*8]
    print(f"  Card {ci}: {' '.join(f'{b:02X}' for b in card)}")
    for r in range(8):
        row = "".join("#" if (card[r]>>(7-c))&1 else "." for c in range(8))
        print(f"    {row}")

# Also look at $5BCC-$5C00 more carefully - this is the player sprite region
print("\n=== Player sprite block ($5BCC-$5C08, 40 cards max) ===")
for ci in range(30):
    addr = 0x5BCC + ci*8
    px = sum(bin(rom_byte(addr+i)).count("1") for i in range(8))
    if px > 0:
        print(f"\nCard {ci} @ ${addr:04X} ({px} px):")
        print(ascii_card(addr))
