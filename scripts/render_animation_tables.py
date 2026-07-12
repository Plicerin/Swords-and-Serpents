import os
from PIL import Image

# ROM setup
ROM_PATH = r'C:\Users\vrock\Documents\Swords and Serpents\Swords and Serpents.bin'
OUT_DIR = r'C:\Users\vrock\Documents\Swords and Serpents\sprites\animation_tables'
os.makedirs(OUT_DIR, exist_ok=True)

with open(ROM_PATH, 'rb') as f:
    rom = f.read()

def rom_word(addr):
    if addr < 0x5000:
        return None
    offset = (addr - 0x5000) * 2
    if offset + 1 >= len(rom):
        return None
    return (rom[offset] << 8) | rom[offset + 1]

def render_8x8(data, palette=((0,0,0), (255,255,255))):
    img = Image.new('RGB', (8, 8))
    px = img.load()
    for y, b in enumerate(data):
        for x in range(8):
            px[x, y] = palette[1] if (b >> (7 - x)) & 1 else palette[0]
    return img

# These are the ROM addresses found in the game code
# They seem to be class/animation tables
pointer_addrs = {
    'warrior_or_p1': 0x5B28,
    'class_2': 0x5B5E,
    'wizard_or_p2': 0x5B9A,
    'class_4': 0x5BAE,
    # Add more if found in code
}

# Read the first word at each table (control word)
for name, addr in pointer_addrs.items():
    print(f"\n=== Table {name} at ROM 0x{addr:04X} ===")
    ctrl = rom_word(addr)
    print(f"  Control word: 0x{ctrl:04X}")
    
    # Render a strip of 8 frames (16 bytes each = 2 cards per frame)
    # Usually a sprite is 2 cards (16x8 pixels) or 4 cards (16x16)
    # Let's render both possibilities
    num_frames = 16
    frame_width = 16  # 2 cards side by side = 16x8 pixels
    
    # Create a sheet: num_frames frames horizontally
    sheet = Image.new('RGB', (frame_width * num_frames, 8 + 20), (0, 0, 0))
    
    for i in range(num_frames):
        rom_off = (addr + 2) - 0x5000  # data starts after the control word
        rom_off *= 2  # byte offset in file
        frame_offset = rom_off + (i * 16)  # 16 bytes per 16x8 sprite
        
        # Check bounds
        if frame_offset + 16 > len(rom):
            break
        
        # Render 2 cards horizontally (16x8 pixels)
        for c in range(2):
            card_off = frame_offset + c * 8
            card_data = rom[card_off : card_off + 8]
            for y, b in enumerate(card_data):
                for x in range(8):
                    color = (255, 255, 255) if (b >> (7 - x)) & 1 else (0, 0, 0)
                    px_x = (i * frame_width) + (c * 8) + x
                    sheet.putpixel((px_x, y), color)
    
    sheet_path = os.path.join(OUT_DIR, f'table_{name}_0x{addr:04X}.png')
    sheet.save(sheet_path)
    print(f"  Saved sheet to {sheet_path}")
    
    # Also render as 16x16 sprites (4 cards = 32 bytes per frame)
    # Render a few frames as 16x16 composite blocks
    sheet_16 = Image.new('RGB', (16 * 8, (num_frames // 8) * 16), (0,0,0))
    for f in range(0, num_frames, 4):
        row = f // 8
        col = (f % 8)
        # 16x16 sprite = 4 cards: top-left, top-right, bottom-left, bottom-right
        # Each card in the data is 8 bytes, in order: top-left, top-right, bottom-left, bottom-right? 
        # Actually for 16x16, the Intellivision stores cards in a 2x2 grid.
        # The exact layout depends on the ROM. Let's just render top-left for now.
        pass

print("\nDone. Check the animation_tables directory.")
