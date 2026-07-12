import os

ROM_PATH = r'C:\Users\vrock\Documents\Swords and Serpents\Swords and Serpents.bin'

with open(ROM_PATH, 'rb') as f:
    rom = f.read()

def rom_word(addr):
    if addr < 0x5000:
        return None
    offset = (addr - 0x5000) * 2
    if offset + 1 >= len(rom):
        return None
    return (rom[offset] << 8) | rom[offset + 1]

def render_ascii(addr, count=8):
    offset = (addr - 0x5000) * 2
    if offset < 0 or offset + count*16 > len(rom):
        return
    
    for f in range(count):
        frame_off = offset + f * 16
        print(f"  Frame {f} @ ROM {addr + f*16:04X}:")
        for c in range(2):
            for y in range(8):
                b = rom[frame_off + c*8 + y]
                # Not right, cards are 8 bytes each, but a 16x8 sprite has 2 cards side-by-side
                pass
        # Actually, let's just render the raw 16 bytes as two 8x8 cards
        for row in range(8):
            line = ""
            for c in range(2):
                b = rom[frame_off + c*8 + row]
                bits = ''.join('## ' if (b >> (7-x)) & 1 else '   ' for x in range(8))
                line += bits + " | "
            print(f"    {line}")

# Inspect tables
pointer_addrs = {
    'warrior_or_p1': 0x5B28,
    'class_2': 0x5B5E,
    'wizard_or_p2': 0x5B9A,
    'class_4': 0x5BAE,
}

for name, addr in pointer_addrs.items():
    print(f"\n=== {name} @ 0x{addr:04X} ===")
    ctrl = rom_word(addr)
    print(f"  Control/First word: 0x{ctrl:04X} ({ctrl})")
    print(f"  Hex dump of first 64 bytes:")
    
    off = (addr - 0x5000) * 2
    for i in range(0, 64, 16):
        h = ' '.join(f'{rom[off+i+j]:02X}' for j in range(16))
        print(f"    {addr+i:04X}: {h}")
    
    print(f"  ASCII art of first 4 frames (16x8 each):")
    render_ascii(addr + 2, count=4)
    
print("Done.")
