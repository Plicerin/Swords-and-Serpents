from PIL import Image, ImageDraw, ImageFont
import os

ROM_PATH = r'C:\Users\vrock\Documents\Swords and Serpents\Swords and Serpents.bin'
OUT_DIR = r'C:\Users\vrock\Documents\Swords and Serpents\sprites'
os.makedirs(OUT_DIR, exist_ok=True)

with open(ROM_PATH, 'rb') as f:
    rom = bytearray(f.read())

# The best block from previous run was at file offset 0x0BB8 (ROM 0x55DC)
best_offset = 0x0BB8

# Render all cards as a labeled 8x4 grid
cell_size = 16  # scaled up
grid_w, grid_h = 8, 4
sheet = Image.new('RGB', (grid_w * cell_size, grid_h * cell_size + 20), (0,0,0))
draw = ImageDraw.Draw(sheet)

for i in range(32):
    card_bytes = rom[best_offset + i*8 : best_offset + i*8 + 8]
    card_img = Image.new('RGB', (8, 8))
    px = card_img.load()
    for y, b in enumerate(card_bytes):
        for x in range(8):
            px[x, y] = (255, 0, 0) if (b >> (7-x)) & 1 else (0, 0, 64)
    # Scale to cell_size
    scaled = card_img.resize((cell_size-2, cell_size-2), Image.NEAREST)
    col = i % grid_w
    row = i // grid_w
    sheet.paste(scaled, (col*cell_size + 1, row*cell_size + 1))
    # Draw card number
    draw.text((col*cell_size + 2, row*cell_size + cell_size - 12), str(i), fill=(255, 255, 0))

fname = os.path.join(OUT_DIR, 'gram_cards_labeled.png')
sheet.save(fname)
print(f'Saved labeled sheet to {fname}')

# Also save individual cards
for i in range(32):
    card_bytes = rom[best_offset + i*8 : best_offset + i*8 + 8]
    card_img = Image.new('RGB', (8, 8))
    px = card_img.load()
    for y, b in enumerate(card_bytes):
        for x in range(8):
            px[x, y] = (255, 255, 255) if (b >> (7-x)) & 1 else (0, 0, 0)
    scaled = card_img.resize((64, 64), Image.NEAREST)
    scaled.save(os.path.join(OUT_DIR, f'card_{i:02d}_rom_0x{0x55DC + i*4:04X}.png'))

# Also print ASCII art of all cards
print('\n=== ASCII Art of All 32 Cards ===')
for i in range(32):
    card_bytes = rom[best_offset + i*8 : best_offset + i*8 + 8]
    print(f'\nCard {i} (ROM 0x{0x55DC + i*4:04X}):')
    for b in card_bytes:
        row = ''.join('##' if (b >> (7-x)) & 1 else '..' for x in range(8))
        print(f'  {row}')