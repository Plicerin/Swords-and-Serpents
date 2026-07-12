"""
Scan the Swords and Serpents ROM for potential character sprites.
MOB sprites are typically 16 bytes (8x16 pixels, 1bpp).
Renders ALL candidates into a visual sprite sheet for inspection.
"""
from PIL import Image
import struct

# Read ROM binary
with open("Swords and Serpents.bin", "rb") as f:
    rom = f.read()

print(f"ROM size: {len(rom)} bytes (${len(rom):04X})")
print(f"ROM address range: $5000-${0x5000 + len(rom) - 1:04X}")

# IntelliVision palette
PALETTE = {
    0:  (0, 0, 0),         # black
    1:  (0, 60, 220),      # blue
    2:  (220, 0, 20),      # red
    3:  (200, 170, 100),   # tan
    4:  (0, 80, 20),       # dark green
    5:  (0, 150, 50),      # green
    6:  (240, 220, 80),    # yellow
    7:  (255, 255, 255),   # white
}

def render_sprite_1bpp(data, fg=7, bg=0, width=8, height=16):
    """Render a 1bpp sprite where each byte is a row, MSB left"""
    img = Image.new("RGB", (width, height))
    px = img.load()
    for row in range(min(height, len(data))):
        byte_val = data[row]
        for col in range(width):
            bit = (byte_val >> (7 - col)) & 1
            px[col, row] = PALETTE[fg] if bit else PALETTE[bg]
    return img

def score_sprite(data, min_len=16):
    """Score how likely this is actual sprite data (not code/data)"""
    if len(data) < min_len:
        return -1
    
    chunk = data[:min_len]
    
    # Count zero bytes, all-zero rows, all-FF rows
    zeros = chunk.count(0)
    all_ff = chunk.count(0xFF)
    unique = len(set(chunk))
    
    # Check for repeating patterns (code/data tends to repeat)
    # Real sprites have varied bytes
    # Code often has $02, $03, $00 patterns
    
    # Check horizontal symmetry (common in character sprites)
    symmetric_rows = 0
    for row in range(min_len):
        b = chunk[row]
        # Check if byte is horizontally symmetric (bit pattern)
        mirrored = 0
        for i in range(4):
            if (b >> (7-i)) & 1:
                mirrored |= 1 << i
            if (b >> i) & 1:
                mirrored |= 1 << (7-i)
        if b == mirrored:
            symmetric_rows += 1
    
    # Score: prefer non-empty, non-uniform, varied data
    # But not TOO varied (code bytes are very varied)
    if zeros >= min_len - 1:
        return -1  # almost empty
    if all_ff >= min_len - 1:
        return -1  # almost all 1s
    
    # Check for typical code markers
    code_markers = [0x02B8, 0x02BA, 0x0004, 0x0034, 0x02B7]
    has_code = any(
        (chunk[i] == 0x02 and chunk[i+1] in [0xB8, 0xBA, 0xB7]) or
        (chunk[i] == 0x00 and chunk[i+1] == 0x04 and chunk[i+2] in [0x01, 0x00])
        for i in range(min_len - 2)
    )
    if has_code:
        return -1
    
    score = unique * 2 + symmetric_rows * 3
    if zeros > min_len // 3:
        score -= zeros * 2
    
    return score

# Scan for 16-byte sprite candidates
print("\nScanning for 16-byte (8x16) sprite candidates...")
candidates = []
for addr in range(0, len(rom) - 16):
    chunk = rom[addr:addr+16]
    score = score_sprite(chunk, 16)
    if score >= 8:  # threshold
        # Also check +8 bytes (16x16 double card)
        next8 = rom[addr+16:addr+24] if addr+24 <= len(rom) else b''
        next_score = score_sprite(next8 + b'\x00'*8, 16) if len(next8) >= 8 else -1
        candidates.append((addr + 0x5000, score + next_score, addr))

# Sort by score descending
candidates.sort(key=lambda x: -x[1])
print(f"Found {len(candidates)} candidates")

# Also scan for 8-byte (8x8) sprites
print("\nScanning for 8-byte (8x8) sprite candidates...")
candidates_8 = []
for addr in range(0, len(rom) - 8):
    chunk = rom[addr:addr+8]
    score = score_sprite(chunk, 8) // 2  # lower threshold for smaller sprites
    if score >= 3:
        candidates_8.append((addr + 0x5000, score, addr))

candidates_8.sort(key=lambda x: -x[1])
print(f"Found {len(candidates_8)} candidates")

# Render top 200 candidates as a sprite sheet
TOP_N = 200
sprites_per_row = 20
rows_needed = (TOP_N + sprites_per_row - 1) // sprites_per_row

sprite_w = 8
sprite_h = 16
scale = 4
margin = 2

sheet_w = sprites_per_row * (sprite_w * scale + margin) + margin
sheet_h = rows_needed * (sprite_h * scale + margin) + margin

sheet_16 = Image.new("RGB", (sheet_w, sheet_h), (30, 30, 40))
sheet_8 = Image.new("RGB", (sheet_w, sheet_h), (30, 30, 40))

# Label rendering helper
from PIL import ImageDraw, ImageFont
try:
    font = ImageFont.truetype("arial.ttf", 8)
except:
    font = ImageFont.load_default()

for i, (rom_addr, score, offset) in enumerate(candidates[:TOP_N]):
    row = i // sprites_per_row
    col = i % sprites_per_row
    
    x = col * (sprite_w * scale + margin) + margin
    y = row * (sprite_h * scale + margin) + margin
    
    data = rom[offset:offset+16]
    
    # Check if this is part of a 16x16 sprite (two 8x8 cards stacked or side by side)
    # For 8x16, render as single column
    sprite_img = render_sprite_1bpp(data, fg=7, bg=0, width=8, height=16)
    sprite_img = sprite_img.resize((sprite_w * scale, sprite_h * scale), Image.NEAREST)
    sheet_16.paste(sprite_img, (x, y))
    
    # Add label
    draw = ImageDraw.Draw(sheet_16)
    draw.text((x, y - 2), f"${rom_addr:04X}", fill=(100, 100, 120))

sheet_16.save("sprites/rom_sprites_8x16.png")
print(f"\nSaved sprites/rom_sprites_8x16.png ({min(TOP_N, len(candidates))} candidates)")

# Also render top 8x8 candidates
for i, (rom_addr, score, offset) in enumerate(candidates_8[:TOP_N]):
    row = i // sprites_per_row
    col = i % sprites_per_row
    
    x = col * (sprite_w * scale + margin) + margin
    y = row * (8 * scale + margin) + margin
    
    data = rom[offset:offset+8]
    sprite_img = render_sprite_1bpp(data, fg=7, bg=0, width=8, height=8)
    sprite_img = sprite_img.resize((sprite_w * scale, 8 * scale), Image.NEAREST)
    sheet_8.paste(sprite_img, (x, y))

sheet_8.save("sprites/rom_sprites_8x8.png")
print(f"Saved sprites/rom_sprites_8x8.png ({min(TOP_N, len(candidates_8))} candidates)")

# Print top 20 addresses for manual inspection
print("\n--- Top 20 8x16 sprite candidates ---")
for addr, score, offset in candidates[:20]:
    data = rom[offset:offset+16]
    hex_str = " ".join(f"{b:02X}" for b in data)
    print(f"  ROM ${addr:04X} (score={score:2d}): {hex_str}")

print("\n--- Top 20 8x8 sprite candidates ---")
for addr, score, offset in candidates_8[:20]:
    data = rom[offset:offset+8]
    hex_str = " ".join(f"{b:02X}" for b in data)
    print(f"  ROM ${addr:04X} (score={score:2d}): {hex_str}")
