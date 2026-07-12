"""
Render ALL GRAM cards $30-$3F ($3980-$39BF) from the gameplay dump
as individual labeled images, and map BACKTAB tiles to positions.
"""
from PIL import Image, ImageDraw

# Gameplay GRAM data (low bytes from jzintv dump)
# Cards $30-$3F at addresses $3980-$39BF

gram = {}

# Card $30 ($3980)
gram[0x30] = [0x18, 0x3C, 0x7E, 0x73, 0xF9, 0x99, 0x89, 0x89]
# Card $31 ($3988)
gram[0x31] = [0x89, 0x89, 0x99, 0xF9, 0x73, 0x7E, 0x3C, 0x18]
# Card $32 ($3990)
gram[0x32] = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF]
# Card $33 ($3998)
gram[0x33] = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
# Card $34 ($39A0) - gameplay data
gram[0x34] = [0x02, 0x25, 0x6E, 0x3F, 0x7C, 0xF4, 0x98, 0x98]
# Card $35 ($39A8) - gameplay data
gram[0x35] = [0xA8, 0xAA, 0x8D, 0x7A, 0xBF, 0x1E, 0x34, 0x00]
# Card $36 ($39B0) - gameplay data
gram[0x36] = [0x00, 0x01, 0x54, 0x1E, 0x7F, 0xFA, 0x7F, 0x7B]
# Card $37 ($39B8) - gameplay data
gram[0x37] = [0xFE, 0x7E, 0xB6, 0x5D, 0x24, 0x40, 0x10, 0x00]

# IntelliVision palette
TAN = (200, 160, 40)
DARK = (10, 10, 20)
ZOOM = 8

print("=== GAMEPLAY GRAM CARDS $30-$3F ===\n")

for card_num in sorted(gram.keys()):
    data = gram[card_num]
    has_data = any(b != 0 for b in data)
    print(f"\nCard ${card_num:02X} (addr ${0x3800 + card_num*8:04X}):")
    
    # ASCII
    for row in range(8):
        byte = data[row]
        line = ''
        for col in range(8):
            bit = (byte >> (7 - col)) & 1
            line += '##' if bit else '..'
        print(f'  {line}')
    
    if has_data:
        # Render individual card
        img = Image.new('RGBA', (8*ZOOM, 8*ZOOM), DARK + (255,))
        draw = ImageDraw.Draw(img)
        for row in range(8):
            byte = data[row]
            for col in range(8):
                bit = (byte >> (7 - col)) & 1
                color = TAN + (255,) if bit else DARK + (255,)
                px = col * ZOOM
                py = row * ZOOM
                draw.rectangle([px, py, px+ZOOM-1, py+ZOOM-1], fill=color)
        img.save(f'sprites/gameplay_card_{card_num:02X}.png')

# Also render combined pairs
# Cards $30+$31 (possible head)
img_h = Image.new('RGBA', (16*ZOOM, 8*ZOOM), DARK + (255,))
draw_h = ImageDraw.Draw(img_h)
for off, cn in enumerate([0x30, 0x31]):
    data = gram[cn]
    x_off = off * 8 * ZOOM
    for row in range(8):
        byte = data[row]
        for col in range(8):
            bit = (byte >> (7 - col)) & 1
            color = TAN + (255,) if bit else DARK + (255,)
            px = x_off + col * ZOOM
            py = row * ZOOM
            draw_h.rectangle([px, py, px+ZOOM-1, py+ZOOM-1], fill=color)
img_h.save('sprites/gameplay_30_31_pair.png')

# Cards $34+$35
img2 = Image.new('RGBA', (16*ZOOM, 8*ZOOM), DARK + (255,))
draw2 = ImageDraw.Draw(img2)
for off, cn in enumerate([0x34, 0x35]):
    data = gram[cn]
    x_off = off * 8 * ZOOM
    for row in range(8):
        byte = data[row]
        for col in range(8):
            bit = (byte >> (7 - col)) & 1
            color = TAN + (255,) if bit else DARK + (255,)
            px = x_off + col * ZOOM
            py = row * ZOOM
            draw2.rectangle([px, py, px+ZOOM-1, py+ZOOM-1], fill=color)
img2.save('sprites/gameplay_34_35_pair.png')

# Cards $36+$37
img3 = Image.new('RGBA', (16*ZOOM, 8*ZOOM), DARK + (255,))
draw3 = ImageDraw.Draw(img3)
for off, cn in enumerate([0x36, 0x37]):
    data = gram[cn]
    x_off = off * 8 * ZOOM
    for row in range(8):
        byte = data[row]
        for col in range(8):
            bit = (byte >> (7 - col)) & 1
            color = TAN + (255,) if bit else DARK + (255,)
            px = x_off + col * ZOOM
            py = row * ZOOM
            draw3.rectangle([px, py, px+ZOOM-1, py+ZOOM-1], fill=color)
img3.save('sprites/gameplay_36_37_pair.png')

print("\n\n=== SAVED FILES ===")
print("sprites/gameplay_30_31_pair.png - cards $30+$31 as 16-wide pair")
print("sprites/gameplay_34_35_pair.png - cards $34+$35 as 16-wide pair")
print("sprites/gameplay_36_37_pair.png - cards $36+$37 as 16-wide pair")
print("Individual cards: sprites/gameplay_card_*.png")
