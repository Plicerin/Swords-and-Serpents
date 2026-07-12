import os
from PIL import Image

ROM_PATH = r'C:\Users\vrock\Documents\Swords and Serpents\Swords and Serpents.bin'
OUT_DIR = r'C:\Users\vrock\Documents\Swords and Serpents\sprites\decoded_boot'
os.makedirs(OUT_DIR, exist_ok=True)

with open(ROM_PATH, 'rb') as f:
    rom = f.read()

def rom_word(addr):
    off = (addr - 0x5000) * 2
    return (rom[off] << 8) | rom[off+1]

# Decode boot RLE at 0x61E7
base = 0x61E7

r4 = base
r5 = rom_word(r4)    # destination offset
r4 += 1
gram_dest = (r5 + 0x3800) & 0xFFFF
r0 = rom_word(r4)    # loop count (number of entries)
r4 += 1

print(f"RLE at ROM 0x{base:04X}:")
print(f"  Dest base word: 0x{r5:04X} -> GRAM 0x{gram_dest:04X}")
print(f"  Num entries: {r0}")

gram = bytearray(512)
gram_addr = gram_dest - 0x3800

for i in range(r0):
    word = rom_word(r4)
    r4 += 1
    count = ((word >> 8) & 0x03)
    data = word & 0x00FF
    for j in range(count + 1):
        if 0 <= gram_addr < 512:
            gram[gram_addr] = data
        gram_addr += 1

print(f"  Written {gram_addr} bytes to GRAM offset {gram_dest - 0x3800}.")

# Render first 64 cards
num_cards = 64
sheet = Image.new('RGB', (16 * 8, (num_cards // 16) * 8), (0,0,0))
for card in range(num_cards):
    for y in range(8):
        b = gram[card * 8 + y]
        for x in range(8):
            color = (255, 255, 255) if (b >> (7 - x)) & 1 else (0, 0, 0)
            px = (card % 16) * 8 + x
            py = (card // 16) * 8 + y
            sheet.putpixel((px, py), color)

sheet.save(os.path.join(OUT_DIR, 'boot_gram_sheet.png'))
print(f"  Saved to {OUT_DIR}\\boot_gram_sheet.png")

with open(os.path.join(OUT_DIR, 'gram_boot.bin'), 'wb') as f:
    f.write(gram)
