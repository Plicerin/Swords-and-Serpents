from PIL import Image
import os

ROM_PATH = r'C:\Users\vrock\Documents\Swords and Serpents\Swords and Serpents.bin'
OUT_DIR = r'C:\Users\vrock\Documents\Swords and Serpents\sprites'

os.makedirs(OUT_DIR, exist_ok=True)

with open(ROM_PATH, 'rb') as f:
    rom = bytearray(f.read())

def humanoid_score(block):
    nonzero = sum(1 for b in block if b != 0)
    if nonzero < 2 or nonzero > 7:
        return 0
    total = sum(bin(b).count('1') for b in block)
    if total < 8 or total > 40:
        return 0
    sym = 0
    for b in block:
        rev = int('{:08b}'.format(b)[::-1], 2)
        sym += bin(b ^ rev).count('1')
    if sym > 24:
        return 0
    mid = sum(bin(block[i]).count('1') for i in range(2, 6))
    bot = sum(bin(block[i]).count('1') for i in range(5, 7))
    if mid < 8 or bot < 2:
        return 0
    return total - sym//2 + mid

# Scan at 8-byte aligned boundaries
scores = []
for i in range(0, len(rom) - 7, 8):
    block = rom[i:i+8]
    s = humanoid_score(block)
    if s > 0:
        scores.append((i, s, block))

# Find contiguous clusters (8-byte aligned, consecutive cards)
clusters = []
if scores:
    start_idx = scores[0][0]
    current_cluster = [(scores[0][0], scores[0][2])]
    for i in range(1, len(scores)):
        prev_off = scores[i-1][0]
        cur_off = scores[i][0]
        if cur_off == prev_off + 8:
            current_cluster.append((cur_off, scores[i][2]))
        else:
            if len(current_cluster) >= 2:
                clusters.append(current_cluster)
            current_cluster = [(cur_off, scores[i][2])]
    if len(current_cluster) >= 2:
        clusters.append(current_cluster)

print(f'8-byte aligned candidates with humanoid_score > 0: {len(scores)}')
print(f'Found {len(clusters)} contiguous clusters (>= 2 cards)')

def render_card(data, palette=((0,0,0), (255,255,255))):
    img = Image.new('RGB', (8, 8))
    pixels = img.load()
    for y, b in enumerate(data):
        for x in range(8):
            c = palette[1] if (b >> (7 - x)) & 1 else palette[0]
            pixels[x, y] = c
    return img

sheet_idx = 0
for cl in clusters:
    cols = 16
    rows = (len(cl) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * 8, rows * 8), (0,0,0))
    for ci, (offset, block) in enumerate(cl):
        img = render_card(rom[offset:offset+8])
        x = (ci % cols) * 8
        y = (ci // cols) * 8
        sheet.paste(img, (x, y))
    fname = f'sheet_aligned_{sheet_idx:02d}_0x{cl[0][0]:04x}_len{len(cl)}.png'
    sheet.save(os.path.join(OUT_DIR, fname))
    print(f'  {fname}: {len(cl)} cards at 0x{cl[0][0]:04X}')
    sheet_idx += 1

print(f'Wrote {sheet_idx} aligned sheets to {OUT_DIR}')