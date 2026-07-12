import re
from PIL import Image

# Parse GRAM from character select capture
with open("traces/capture_char_select_out.txt", "r", errors="replace") as f:
    content = f.read()

lines = content.split(chr(10))
gram = {}
addr = None
in_gram = False

for line in lines:
    stripped = line.strip()
    
    # Check for address lines - track current address
    m = re.match(r'^([0-9A-F]{4}):', stripped)
    if m:
        addr = int(m.group(1), 16)
        if addr >= 0x3D00:
            break
        if addr >= 0x3800:
            in_gram = True
    
    if in_gram and addr is not None:
        words = re.findall(r'([0-9A-F]{4})\*?', stripped)
        for w in words:
            if 0x3800 <= addr < 0x3A00:
                gram[addr] = int(w, 16)
                addr += 1

print(f"Parsed {len(gram)} GRAM words")

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

def render_card(card_num, fg_color=7, bg_color=0):
    img = Image.new("RGB", (8, 8))
    px = img.load()
    base_addr = 0x3800 + card_num * 8
    for row in range(8):
        addr = base_addr + row
        if addr in gram:
            word = gram[addr]
            for col in range(8):
                bit = (word >> (7 - col)) & 1
                px[col, row] = PALETTE[fg_color] if bit else PALETTE[bg_color]
        else:
            for col in range(8):
                px[col, row] = (128, 128, 128)  # missing data
    return img

# Render all 64 cards as a sprite sheet (8 cols x 8 rows)
card_size = 8
scale = 6
margin = 2
cols = 8
rows = 8

sheet_w = cols * (card_size * scale + margin) + margin
sheet_h = rows * (card_size * scale + margin) + margin
sprite_sheet = Image.new("RGB", (sheet_w, sheet_h), (40, 40, 40))

for card in range(64):
    col = card % cols
    row_pos = card // cols
    card_img = render_card(card)
    card_img = card_img.resize((card_size * scale, card_size * scale), Image.NEAREST)
    x = col * (card_size * scale + margin) + margin
    y = row_pos * (card_size * scale + margin) + margin
    sprite_sheet.paste(card_img, (x, y))

sprite_sheet.save("sprites/gram_char_select_all.png")
print("Saved sprites/gram_char_select_all.png")

# Dump non-empty card data
print()
print("Non-empty GRAM cards:")
for card in range(64):
    base = 0x3800 + card * 8
    empty = True
    for row in range(8):
        if gram.get(base + row, 0) != 0:
            empty = False
            break
    if not empty:
        data = " ".join(f"{gram.get(base+r, 0):04X}" for r in range(8))
        print(f"  Card {card:2d} (${card*8:03X}): {data}")
