import re
from PIL import Image

def parse_dump(path):
    """Read the jzIntv dump and return a dict of address -> word value."""
    mem = {}
    with open(path, 'r') as f:
        for line in f:
            line=line.strip()
            # Match lines like:
            # 0000:  3B58* 3B60  3800 ...
            m = re.match(r"^([0-9A-F]{4}):\s+((?:[0-9A-F]{4}\s+)+)", line)
            if not m:
                continue
            addr = int(m.group(1), 16)
            values = m.group(2).split()
            for i, v in enumerate(values):
                vstrip = v.strip('*')
                mem[addr + i] = int(vstrip, 16)
    return mem

def render_cards(mem, start_addr=0x0002, num_cards=64):
    """Render cards as a single horizontal strip or grid."""
    # Card is 8 words wide (8x8 colors via 2bpp)
    width = 8  # pixels per card
    img = Image.new('RGB', (width * num_cards, 8 * (256 // (num_cards * 8))))
    # Actually just make a grid
    pass
    return img

# Let's parse the scratchpad dump: it contains multiple m commands (m 0000 256 and m 0100 256). We only want 0000-00FF.
mem = parse_dump("ss_dump_scratch_300k.txt")

# Focus on 0002-007F (126 words, 15.75 cards). Actually let's do 0002-005F to fit in a 4x4 grid.
# Actually let's render all of 0002-007F.
start = 0x0002
end = 0x007F
num_cards = (end - start + 1) // 8

# Build image grid (e.g., 8x8 cards)
grid_w = 8
grid_h = (num_cards + grid_w - 1) // grid_w
img = Image.new('RGB', (grid_w * 8, grid_h * 8))

# Palette mapping: 0->black, 1->blue, 2->green, 3->red
palette = {0: (0,0,0), 1:(0,0,255), 2:(0,255,0), 3:(255,0,0)}

for c in range(num_cards):
    base = start + c * 8
    x_off = (c % grid_w) * 8
    y_off = (c // grid_w) * 8
    for row in range(8):
        addr = base + row
        # In jzintv dump, 8 words per line. Let's check if we parsed correctly.
        if addr not in mem:
            # print(f"Missing address {addr:04x}")
            continue
        w = mem[addr]
        for col in range(8):
            shift = 14 - col * 2
            pix = (w >> shift) & 3
            img.putpixel((x_off + col, y_off + row), palette[pix])

img.save("scratchpad_cards.png")
print("Saved scratchpad_cards.png with {} cards".format(num_cards))
