from PIL import Image
import re

def parse_dump_gram(path):
    """Parse the m 3800 512 section from a jzIntv dump."""
    mem = {}
    in_gram = False
    with open(path, 'r') as f:
        for line in f:
            line=line.strip()
            if line.startswith('> m 3800'):
                in_gram = True
                continue
            if not in_gram:
                continue
            # Detect end by a new prompt like '>'
            if line.startswith('>'):
                break
            m = re.match(r"^(3[0-9A-F]{3}):\s+((?:[0-9A-F]{4}\s+)+)", line)
            if not m:
                continue
            addr = int(m.group(1), 16)
            values = m.group(2).split()
            for i, v in enumerate(values):
                mem[addr + i] = int(v.strip('*'), 16)
    return mem

def render_gram(mem):
    # GRAM is 64 cards, each 8 words. Address base is 3800.
    # Render as 8x8 grid of 8x8 pixels.
    # Color Stack: 8 pixels per row, 2 bits each.
    # Map 0->black, 1->blue, 2->green, 3->red
    palette = {0: (0,0,0), 1:(0,0,255), 2:(0,255,0), 3:(255,0,0)}
    card_w, card_h = 8, 8
    grid_w, grid_h = 8, 8
    img = Image.new('RGB', (grid_w * card_w, grid_h * card_h))
    for card_idx in range(64):
        base = 0x3800 + card_idx * 8
        x_off = (card_idx % grid_w) * card_w
        y_off = (card_idx // grid_w) * card_h
        for row in range(8):
            addr = base + row
            w = mem.get(addr, 0)
            for col in range(8):
                shift = 14 - col * 2
                pix = (w >> shift) & 3
                img.putpixel((x_off + col, y_off + row), palette[pix])
    return img

mem = parse_dump_gram("ss_dump_system_ram.txt")
img = render_gram(mem)
img.save("gram_sheet.png")
print("Saved gram_sheet.png")
