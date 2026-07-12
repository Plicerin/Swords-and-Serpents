import os

ROM_PATH = r'C:\Users\vrock\Documents\Swords and Serpents\Swords and Serpents.bin'
OUT_DIR = r'C:\Users\vrock\Documents\Swords and Serpents\sprites'

with open(ROM_PATH, 'rb') as f:
    rom = bytearray(f.read())

# clusters from previous run
clusters = [
    (0x126C, 17), (0x1672, 26), (0x1698, 24), (0x170A, 22),
    (0x1840, 16), (0x1860, 16), (0x1880, 17), (0x19A6, 19),
    (0x19C2, 25), (0x2420, 19), (0x24E6, 19), (0x2AB0, 20),
    (0x2AEA, 19), (0x2B7C, 24), (0x360C, 17), (0x372F, 17)
]

def to_ascii(data):
    lines = []
    for b in data:
        line = ''.join('#' if (b >> (7 - x)) & 1 else '.' for x in range(8))
        lines.append(line)
    return lines

for idx, (offset, length) in enumerate(clusters):
    print(f"=== Cluster {idx} at 0x{offset:04X}, length {length} ===")
    for i in range(min(8, length)):
        block = rom[offset + i : offset + i + 8]
        if any(b != 0 for b in block):
            print(f"  Block {i} (0x{offset+i:04X}):")
            for line in to_ascii(block):
                print(f"    {line}")
    print()
