from PIL import Image
import os, sys

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

def humanoid_score(block):
    # Heuristic: count non-zero rows, total pixels, rough symmetry
    nonzero = sum(1 for b in block if b != 0)
    if nonzero < 2 or nonzero > 7:
        return 0
    total = sum(bin(b).count('1') for b in block)
    if total < 8 or total > 40:
        return 0
    # Penalize high asymmetry
    sym = 0
    for b in block:
        rev = int('{:08b}'.format(b)[::-1], 2)
        sym += bin(b ^ rev).count('1')
    if sym > 24:
        return 0
    # bonus for shape: head at top, wider middle/bottom
    top = bin(block[0]).count('1')
    mid = sum(bin(block[i]).count('1') for i in range(2,6))
    bot = sum(bin(block[i]).count('1') for i in range(5,8))
    # a simple torso-heuristic: mid should be reasonably high
    if mid < 8:
        return 0
    # feet should exist
    if bot < 2:
        return 0
    return total - sym//2 + mid

# score every block
scores = [0] * (len(rom) - 7)
for i in range(len(rom) - 7):
    block = rom[i:i+8]
    scores[i] = humanoid_score(block)

# find contiguous clusters of high scores
clusters = []
in_cluster = False
start = 0
for i, s in enumerate(scores):
    if s > 0 and not in_cluster:
        in_cluster = True
        start = i
    elif s == 0 and in_cluster:
        in_cluster = False
        clusters.append((start, i))
if in_cluster:
    clusters.append((start, len(scores)))

# Keep clusters with at least 2 blocks (likely animation frames)
clusters = [(a, b) for a, b in clusters if b - a >= 16]

print(f'Found {len(clusters)} clusters of length >= 16 bytes')

# Render each cluster as a horizontal sheet of 8x8 cards, 16 per row
sheet_idx = 0
for start, end in clusters:
    length = end - start
    print(f'Cluster at ROM offset 0x{start:04X}: length {length}')
    cols = 16
    rows = (length + cols - 1) // cols
    sheet = Image.new('RGB', (cols * 8, rows * 8), (0,0,0))
    for i in range(length):
        block = rom[start + i : start + i + 8]
        img = render_block(block)
        x = (i % cols) * 8
        y = (i // cols) * 8
        sheet.paste(img, (x, y))
    fname = os.path.join(OUT_DIR, f'sheet_{sheet_idx:02d}_0x{start:04x}.png')
    sheet.save(fname)
    sheet_idx += 1

print(f'Wrote {sheet_idx} sheets to {OUT_DIR}')
