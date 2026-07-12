from PIL import Image
import os

ROM_PATH = r'C:\Users\vrock\Documents\Swords and Serpents\Swords and Serpents.bin'
OUT_DIR = r'C:\Users\vrock\Documents\Swords and Serpents\sprites'
os.makedirs(OUT_DIR, exist_ok=True)

with open(ROM_PATH, 'rb') as f:
    rom = bytearray(f.read())

def render_block(data, palette=((0,0,0), (255,255,255))):
    """Render an 8-byte sequence as an 8x8 image."""
    img = Image.new('RGB', (8, 8))
    px = img.load()
    for y, b in enumerate(data):
        for x in range(8):
            c = palette[1] if (b >> (7 - x)) & 1 else palette[0]
            px[x, y] = c
    return img

def render_cards(data, w=8, h=8):
    """Render a sequence of bytes as a grid of 8x8 cards."""
    num_cards = len(data) // 8
    img = Image.new('RGB', (w * 8, h * 8))
    for i in range(min(num_cards, w * h)):
        card_data = data[i*8:(i+1)*8]
        card_img = render_block(card_data)
        x = (i % w) * 8
        y = (i // w) * 8
        img.paste(card_img, (x, y))
    return img

# --- 1. Render the entire ROM as a grid of 8x8 cards (32 cards wide) ---
print("Rendering full ROM as 8x8 cards...")
rom_cards = len(rom) // 8
cards_w = 32
cards_h = (rom_cards + cards_w - 1) // cards_w
sheet_8x8 = Image.new('RGB', (cards_w * 8, cards_h * 8))
for i in range(rom_cards):
    block = rom[i*8:(i+1)*8]
    img = render_block(block)
    x = (i % cards_w) * 8
    y = (i // cards_w) * 8
    sheet_8x8.paste(img, (x, y))
sheet_8x8.save(os.path.join(OUT_DIR, 'full_rom_8x8.png'))
print(f"  Saved full_rom_8x8.png ({cards_w}x{cards_h} cards)")

# --- 2. Render the entire ROM as 16x16 composite blocks (built from 4 8x8 cards) ---
# A 16x16 block is 4 cards = 32 bytes
print("Rendering full ROM as 16x16 composite blocks...")
block_size = 32
num_blocks = (len(rom) - block_size + 1) // block_size
blocks_w = 16
blocks_h = (num_blocks + blocks_w - 1) // blocks_w
sheet_16x16 = Image.new('RGB', (blocks_w * 16, blocks_h * 16))
scale = 1  # 1x scale for raw

for i in range(num_blocks):
    data = rom[i*block_size : (i+1)*block_size]
    # Data is 4 cards: top-left, top-right, bottom-left, bottom-right.
    # We assume standard top-left to bottom-right ordering.
    # Let's also try row-major ordering if the cards are stored top-left, bottom-left, top-right, bottom-right?
    # The default Intellivision MOB ordering for a 16x16 sprite is usually top-left, top-right, bottom-left, bottom-right.
    # But for background cards, they are just a sequence.
    # We'll just render them as 2x2:
    img = Image.new('RGB', (16, 16))
    for card_idx in range(4):
        card_data = data[card_idx*8 : (card_idx+1)*8]
        card_img = render_block(card_data)
        cx = (card_idx % 2) * 8
        cy = (card_idx // 2) * 8
        img.paste(card_img, (cx, cy))
    
    x = (i % blocks_w) * 16
    y = (i // blocks_w) * 16
    sheet_16x16.paste(img, (x, y))

sheet_16x16.save(os.path.join(OUT_DIR, 'full_rom_16x16_composites.png'))
print(f"  Saved full_rom_16x16_composites.png ({blocks_w}x{blocks_h} blocks)")

# --- 3. Also render just the non-GROM part (ROM 0x5000+) differently, maybe just more zoomed ---
# Actually, the main goal is clear visuals. Let's render the same grids but at higher scale for easier manual inspection.
print("Rendering zoomed versions for inspection...")

def scale_image(img, factor):
    return img.resize((img.width * factor, img.height * factor), Image.NEAREST)

zoom_8x8 = scale_image(sheet_8x8, 4)
zoom_8x8.save(os.path.join(OUT_DIR, 'full_rom_8x8_zoom4x.png'))
print(f"  Saved full_rom_8x8_zoom4x.png")

zoom_16x16 = scale_image(sheet_16x16, 4)
zoom_16x16.save(os.path.join(OUT_DIR, 'full_rom_16x16_composites_zoom4x.png'))
print(f"  Saved full_rom_16x16_composites_zoom4x.png")

print("Done. Please inspect the generated images to locate the 'wizard' sprite.")
