from PIL import Image
import os

ROM_PATH = r'C:\Users\vrock\Documents\Swords and Serpents\Swords and Serpents.bin'
OUT_DIR = r'C:\Users\vrock\Documents\Swords and Serpents\sprites'
os.makedirs(OUT_DIR, exist_ok=True)

with open(ROM_PATH, 'rb') as f:
    rom = bytearray(f.read())

def card_likeness(block_256):
    """Score a 256-byte (32-card) block for being sprite data."""
    cards = [block_256[i:i+8] for i in range(0, 256, 8)]
    good_cards = 0
    total_pixels = 0
    # A good card has: 0-2 all-zero rows, some pixel rows, reasonable pixel count
    for card in cards:
        zeros = sum(1 for b in card if b == 0)
        ones_total = sum(bin(b).count('1') for b in card)
        # Typical card: 2-6 non-zero rows, 5-40 pixels
        if 2 <= (8 - zeros) <= 7 and 5 <= ones_total <= 45:
            good_cards += 1
            total_pixels += ones_total
    # Good blocks have at least 15 good cards
    return good_cards if good_cards >= 10 else 0

# Search for the best 256-byte block
best_score = 0
best_offset = 0
for offset in range(0, len(rom) - 255, 8):
    block = rom[offset:offset+256]
    score = card_likeness(block)
    if score > best_score:
        best_score = score
        best_offset = offset

print(f'Best block at file offset 0x{best_offset:04X} (ROM addr 0x{0x5000 + best_offset//2:04X}), score {best_score}')

# Render the best 32-card sheet
block_data = rom[best_offset:best_offset+256]
sheet = Image.new('RGB', (8*8, 8*4), (0, 0, 0))
for i in range(32):
    card_bytes = block_data[i*8:(i+1)*8]
    card_img = Image.new('RGB', (8, 8))
    px = card_img.load()
    for y, b in enumerate(card_bytes):
        for x in range(8):
            px[x, y] = (255,255,255) if (b >> (7-x)) & 1 else (0,0,0)
    col = i % 8
    row = i // 8
    sheet.paste(card_img, (col*8, row*8))

sheet.save(os.path.join(OUT_DIR, 'gram_cards_best.png'))
print('Saved best guess to gram_cards_best.png')