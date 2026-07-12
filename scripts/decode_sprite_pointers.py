from PIL import Image
import os

ROM_PATH = r'C:\Users\vrock\Documents\Swords and Serpents\Swords and Serpents.bin'
OUT_DIR = r'C:\Users\vrock\Documents\Swords and Serpents\sprites'

os.makedirs(OUT_DIR, exist_ok=True)

with open(ROM_PATH, 'rb') as f:
    rom = f.read()

print(f"ROM Size: {len(rom)} bytes")

# ROM address $5000 is at file offset 0.
def rom_word(addr):
    """Read a 16-bit word from ROM at given address (e.g., 0x5000)."""
    if addr < 0x5000:
        return None
    offset = (addr - 0x5000) * 2
    if offset + 1 >= len(rom):
        return None
    return (rom[offset] << 8) | rom[offset + 1]

def file_word(offset):
    """Read a 16-bit word from file offset."""
    if offset + 1 >= len(rom):
        return None
    return (rom[offset] << 8) | rom[offset + 1]

# The pointer table is at ROM address 0x5555.
table_addr = 0x5555
file_off = (table_addr - 0x5000) * 2

print(f"\n=== Sprite Pointer Table at ROM {table_addr:04X} (file offset {file_off:04X}) ===")
print(f"File bytes: {rom[file_off]:02X} {rom[file_off+1]:02X}")

# R2 goes 0, 2, 4, 6. So 4 pointers, one for each player.
# Each entry is 1 word (2 bytes).
pointers = []
for i in range(4):
    off = file_off + i * 2
    ptr = file_word(off)
    pointers.append(ptr)
    print(f"  Player {i}: ptr = 0x{ptr:04X}")

# Let's also check the area around the pointer table to see what other data is nearby.
print(f"\n=== Data around pointer table (first 32 words as hex) ===")
for i in range(32):
    off = file_off + i * 2
    w = file_word(off)
    print(f"  0x{table_addr + i:04X}: 0x{w:04X}")

# Render small blocks starting from the pointer targets.
def render_8x8(data, palette=((0,0,0), (255,255,255))):
    img = Image.new('RGB', (8, 8))
    px = img.load()
    for y, b in enumerate(data):
        for x in range(8):
            px[x, y] = palette[1] if (b >> (7 - x)) & 1 else palette[0]
    return img

def render_sprite_at(rom_addr, out_name):
    """Render 16 bytes (2 cards) or 32 bytes (4 cards) as 1 or 2 8x8 cards."""
    file_offset = (rom_addr - 0x5000) * 2
    if file_offset < 0 or file_offset + 16 > len(rom):
        print(f"  {out_name}: Address 0x{rom_addr:04X} out of bounds.")
        return
    
    # Try rendering 2 cards (16 bytes) horizontally
    num_cards = 2
    w = num_cards * 8
    h = 8
    img = Image.new('RGB', (w, h))
    
    for c in range(num_cards):
        card_off = file_offset + c * 8
        card_data = rom[card_off : card_off + 8]
        for y, b in enumerate(card_data):
            for x in range(8):
                color = (255, 255, 255) if (b >> (7 - x)) & 1 else (0, 0, 0)
                img.putpixel((c*8 + x, y), color)
    
    out_path = os.path.join(OUT_DIR, out_name)
    img.save(out_path)
    print(f"  Saved {out_name} from ROM 0x{rom_addr:04X}")

# Let's render a sheet starting from each pointer for several frames
for p_idx, ptr in enumerate(pointers):
    print(f"\n--- Render from player {p_idx} pointer 0x{ptr:04X} ---")
    
    # Render first 16 frames (32 bytes each for 2-card sprites?)
    # Actually, each sprite is 2 cards (16 bytes) for a 16x8 or 8x8 sprite.
    # Let's render a horizontal strip of 16 frames.
    strip = Image.new('RGB', (16 * 8, 8), (0,0,0))
    for frame in range(16):
        rom_addr = ptr + frame * 16
        file_offset = (rom_addr - 0x5000) * 2
        if file_offset < 0 or file_offset + 16 > len(rom):
            break
        for c in range(2):
            card_off = file_offset + c * 8
            card_data = rom[card_off : card_off + 8]
            for y, b in enumerate(card_data):
                for x in range(8):
                    color = (255, 255, 255) if (b >> (7 - x)) & 1 else (0, 0, 0)
                    strip.putpixel((frame*16 + c*8 + x, y), color)
    
    out_name = f"pointer_player_{p_idx}_0x{ptr:04X}.png"
    strip.save(os.path.join(OUT_DIR, out_name))
    print(f"  Saved strip to {out_name}")

