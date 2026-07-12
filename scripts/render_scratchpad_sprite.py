from PIL import Image

# Word values from scratchpad dump at 0002 (after 300k cycles)
# Each card is 8 words. Let's render a few cards.
# For Color Stack: 8 words, each word = 1 row of 8 pixels, 2 bits each.
# Pixel pairs: bits 14-15 = first pixel (leftmost in the Intellivision's internal order?)
# Standard order in Intellivision is actually MSB first for the leftmost of each pair? Let's assume big-endian: bits 15:14 = pixel 0
# Wait, standard is: bits 0-1 = first pixel, bits 2-3 = second pixel, etc. Actually let's try both.

# Let's try: pairs from left to right are bits (15,14), (13,12), ..., (1,0)
data_words = {
    "card_0002": [0x3800, 0x3800, 0x3800, 0x3800, 0x3800, 0x3800, 0x3000, 0x3000],
    "card_000A": [0x3000, 0x3000, 0x3000, 0x3000, 0x3000, 0x3000, 0x0000, 0x0000],
    "card_0012": [0x09A0, 0x09B0, 0x09C0, 0x09D0, 0x09E0, 0x09F0, 0x5B28, 0x5B36],
    "card_001A": [0x3C00, 0x3C00, 0x3C00, 0x3C00, 0x3C00, 0x3C00, 0x3C00, 0x3C00],
    "card_0022": [0x3FFF, 0x3FFF, 0x3FFF, 0x3FFF, 0x3FFF, 0x3FFF, 0x3FFF, 0x3FFF],
    "card_002A": [0x3FF0, 0x3FF3, 0x3FF0, 0x3FF0, 0x3FF0, 0x3FFF, 0x3FFF, 0x3FFF]
}

def render_card(words, width=8):
    img = Image.new('RGB', (width, 8))
    for y, w in enumerate(words[:8]):
        for x in range(width):
            # extract 2-bit pixel: we need to know the pixel order
            # Intellivision STIC color stack: each word has 8 pixels * 2 bits
            # Standard docs say bits 15:14 = first pixel, 13:12 = second, etc.
            shift = 14 - (x * 2)
            pix = (w >> shift) & 3
            # We'll map 0->black, 1->red, 2->green, 3->blue for visual
            if pix == 0: color = (0, 0, 0)
            elif pix == 1: color = (255, 0, 0)
            elif pix == 2: color = (0, 255, 0)
            elif pix == 3: color = (0, 0, 255)
            img.putpixel((x, y), color)
    return img

for name, words in data_words.items():
    img = render_card(words)
    img.save(f"s_{name}.png")
    print(f"Saved {name}.png")
