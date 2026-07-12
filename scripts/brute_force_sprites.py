from PIL import Image
import struct, os, sys

ROM_PATH = r'C:\Users\vrock\Documents\Swords and Serpents\Swords and Serpents.bin'
OUT_DIR = r'C:\Users\vrock\Documents\Swords and Serpents\sprites'

os.makedirs(OUT_DIR, exist_ok=True)

with open(ROM_PATH, 'rb') as f:
    rom = bytearray(f.read())

def render_block(data, palette=((0,0,0), (255,255,255))):
    img = Image.new('RGB', (8, 8))
    pixels = img.load()
    for y, b in enumerate(data):
        for x in range(8):
            c = palette[1] if (b >> (7 - x)) & 1 else palette[0]
            pixels[x, y] = c
    return img

def humanoid_score(data):
    # Heuristic: count non-zero rows and columns, favor central body
    rows = [b for b in data if b != 0]
    if len(rows) < 2 or len(rows) > 7:
        return 0
    # Count total pixels
    total = sum(bin(b).count('1') for b in data)
    if total < 8 or total > 40:
        return 0
    # Simple symmetry check: how many bits match left-right reflection?
    sym = 0
    for b in data:
        rev = int('{:08b}'.format(b)[::-1], 2)
        sym += bin(b ^ rev).count('1')
    # Good humanoids are roughly symmetric
    # Score boost for moderate symmetry
    if sym > 24:
        return 0
    # Check for head-like top (fewer pixels) and body (more pixels)
    top = bin(data[0]).count('1')
    bot = bin(data[7]).count('1')
    # feet often have fewer pixels
    if top > 6:
        return 0
    return total - sym//2

candidates = []
for i in range(len(rom) - 7):
    block = rom[i:i+8]
    score = humanoid_score(block)
    if score > 0:
        candidates.append((i, score, block))

# Sort by score descending
candidates.sort(key=lambda x: x[1], reverse=True)

# Render top candidates into a composite sheet
sheet_w = 8 * 16
sheet_h = 8 * ((len(candidates) + 15) // 16)
sheet = Image.new('RGB', (sheet_w, sheet_h), (0, 0, 0))

THRESHOLD = 512
candidates = candidates[:THRESHOLD]

for idx, (offset, score, block) in enumerate(candidates):
    img = render_block(block)
    x = (idx % 16) * 8
    y = (idx // 16) * 8
    sheet.paste(img, (x, y))

sheet.save(os.path.join(OUT_DIR, 'candidates_sheet.png'))
print(f'Rendered {len(candidates)} candidates to candidates_sheet.png')

# Also save top individual candidates
for idx, (offset, score, block) in enumerate(candidates[:20]):
    img = render_block(block)
    img.save(os.path.join(OUT_DIR, f'candidate_{idx:03d}_0x{offset:04X}.png'))

print('Done. Check the sprites/ directory.')
