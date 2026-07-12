"""
Extract the warrior/wizard sprites from the title screen GRAM and render them nicely.
These were loaded during boot/GRAM init and are visible on the character selection screen.
"""
import re
from PIL import Image, ImageDraw

# Parse GRAM from character select capture
with open("traces/capture_char_select_out.txt", "r", errors="replace") as f:
    content = f.read()

lines = content.split(chr(10))
gram = {}
addr = None
in_gram = False

for line in lines:
    stripped = line.strip()
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

def get_card_data(card_num):
    """Get 8 bytes for a GRAM card"""
    base = 0x3800 + card_num * 8
    return [gram.get(base + r, 0) for r in range(8)]

def render_sprite(card_list, fg=7, bg=0, scale=8):
    """Render multiple GRAM cards stacked vertically as one sprite"""
    total_rows = len(card_list) * 8
    img = Image.new("RGB", (8 * scale, total_rows * scale), PALETTE[bg])
    px_small = Image.new("RGB", (8, total_rows))
    px_small_px = px_small.load()
    
    for card_idx, card_num in enumerate(card_list):
        data = get_card_data(card_num)
        for row in range(8):
            word = data[row]
            for col in range(8):
                bit = (word >> (7 - col)) & 1
                y = card_idx * 8 + row
                px_small_px[col, y] = PALETTE[fg] if bit else PALETTE[bg]
    
    img = px_small.resize((8 * scale, total_rows * scale), Image.NEAREST)
    return img

# Render specific sprite groups found in GRAM
scale = 12
margin = 40
bg_color = (20, 20, 30)
card_color = (40, 40, 50)

# === SPRITE 1: Cards 48-49 (Head/Torso figure - likely Warrior or Wizard) ===
print("\n=== Character Portrait (Cards 48-49) ===")
for r in range(16):
    card = 48 + r // 8
    base = 0x3800 + card * 8
    row_in_card = r % 8
    val = gram.get(base + row_in_card, 0)
    bits = "".join("#" if (val >> (7-c)) & 1 else "." for c in range(8))
    print(f"  Row {r:2d}: {bits}  (${val:04X})")

# === SPRITE 2: Cards 52-53 (X/hourglass shape - icon) ===
print("\n=== Icon (Cards 52-53) ===")
for r in range(16):
    card = 52 + r // 8
    base = 0x3800 + card * 8
    row_in_card = r % 8
    val = gram.get(base + row_in_card, 0)
    bits = "".join("#" if (val >> (7-c)) & 1 else "." for c in range(8))
    print(f"  Row {r:2d}: {bits}  (${val:04X})")

# === SPRITE 3: Cards 54-55 (Organic shape with spikes - Wizard?) ===
print("\n=== Wizard/Magic Figure (Cards 54-55) ===")
for r in range(16):
    card = 54 + r // 8
    base = 0x3800 + card * 8
    row_in_card = r % 8
    val = gram.get(base + row_in_card, 0)
    bits = "".join("#" if (val >> (7-c)) & 1 else "." for c in range(8))
    print(f"  Row {r:2d}: {bits}  (${val:04X})")

# Create main composite image
composite_w = 3 * (8 * scale + margin) + margin
composite_h = 16 * scale + margin * 3
composite = Image.new("RGB", (composite_w, composite_h), bg_color)
draw = ImageDraw.Draw(composite)

# Render each sprite
sprites = [
    ([48, 49], "Warrior / Knight", (240, 210, 100)),   # gold
    ([52, 53], "Item / Shield",     (180, 200, 220)),   # silver
    ([54, 55], "Wizard / Mage",     (150, 180, 255)),   # blue-white
]

for i, (cards, label, fg_rgb) in enumerate(sprites):
    x = margin + i * (8 * scale + margin)
    y = margin
    
    # Find approximate RGB color in palette
    fg_idx = 7  # default white
    
    sprite = render_sprite(cards, fg=fg_idx, bg=0, scale=scale)
    composite.paste(sprite, (x, y))
    
    # Label
    draw.text((x + 4, y + 16 * scale + 4), label, fill=(200, 200, 220))

composite.save("sprites/character_portraits.png")
print(f"\nSaved sprites/character_portraits.png")

# Also save individual sprites
for cards, label, fg_rgb in sprites:
    sprite = render_sprite(cards, fg=7, bg=0, scale=scale)
    fname = f"sprites/{label.replace(' / ', '_').replace(' ', '_').lower()}.png"
    sprite.save(fname)
    print(f"Saved {fname}")
