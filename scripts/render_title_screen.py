#!/usr/bin/env python3
"""Render the Swords & Serpents title screen from jzIntv BackTab + GRAM dumps.

Reads jzintv_room_v2.txt output file and renders the 20x12 tile grid
using GRAM card pixel data.

IntelliVision BackTab word format (Color Stack mode):
  bits 15-14: CS advance
  bit 13:     0=GRAM, 1=GROM
  bits 12-11: BG color (0-3 in CS mode)
  bits 10-8:  FG color (0-7)
  bit 7:      Pastel flag (for GRAM)
  bits 6-0:   Card number (0-63 for GRAM, 0-63 for GROM)

IntelliVision 16-color palette:
  0: Black    (0,0,0)      8: DarkGrey   (64,64,64)
  1: Blue     (0,0,255)    9: Cyan       (0,255,255)
  2: Red      (255,0,0)   10: Orange     (255,128,0)
  3: Tan      (200,170,50) 11: Brown      (128,64,0)
  4: DarkGreen(0,128,0)   12: Pink       (255,128,255)
  5: Green    (0,255,0)   13: LightBlue  (128,128,255)
  6: Yellow   (255,255,0) 14: LightGreen (128,255,128)
  7: Grey     (128,128,128)15: White     (255,255,255)
"""

from PIL import Image, ImageDraw, ImageFont
import re

# IntelliVision palette (primary colors)
PALETTE = {
    0: (0, 0, 0),          # Black
    1: (0, 0, 255),        # Blue
    2: (255, 0, 0),        # Red
    3: (200, 170, 50),     # Tan
    4: (0, 128, 0),        # Dark Green
    5: (0, 255, 0),        # Green
    6: (255, 255, 0),      # Yellow
    7: (128, 128, 128),    # Grey
}
# Pastel variants (approximation - lighter versions)
PASTEL = {
    0: (64, 64, 64),        # Dark Grey
    1: (128, 128, 255),     # Light Blue
    2: (255, 128, 128),     # Light Red/Pink
    3: (255, 220, 140),     # Light Tan
    4: (128, 255, 128),     # Light Green
    5: (128, 255, 128),     # Light Green
    6: (255, 255, 128),     # Light Yellow
    7: (192, 192, 192),     # Light Grey/White
}

ZOOM = 14  # pixels per tile pixel

def parse_jzintv_output(filepath):
    """Parse jzIntv m command output, extracting BackTab and GRAM."""
    with open(filepath, 'r') as f:
        text = f.read()
    
    lines = text.split('\n')
    
    # Parse BackTab ($0200-$02EF) - 240 words
    backtab = {}
    in_section = False
    for line in lines:
        if line.startswith('0200:') and not in_section:
            in_section = True
        if not in_section:
            continue
        parts = line.strip().split()
        if not parts:
            continue
        addr_str = parts[0].replace(':', '').replace('*', '')
        try:
            addr = int(addr_str, 16)
        except:
            continue
        if addr > 0x02EF:
            break
        col = 0
        for part in parts[1:]:
            if part == '#':
                break
            part = part.replace('*', '')
            try:
                val = int(part, 16)
                backtab[addr] = val
                addr += 1
            except:
                break
    
    # Parse GRAM ($3800-$39FF) - 256 words (512 bytes, 64 cards x 8 bytes)
    gram = {}
    in_section = False
    for line in lines:
        if line.startswith('3800:') and not in_section:
            in_section = True
        if not in_section:
            continue
        parts = line.strip().split()
        if not parts:
            continue
        addr_str = parts[0].replace(':', '').replace('*', '')
        try:
            addr = int(addr_str, 16)
        except:
            continue
        if addr > 0x39FF:
            break
        for part in parts[1:]:
            if part == '#':
                break
            part = part.replace('*', '')
            try:
                val = int(part, 16)
                gram[addr] = val
                addr += 1
            except:
                break
    
    return backtab, gram

def decode_backtab(word):
    """Decode an IntelliVision BackTab word. Returns (is_gram, card_num, fg_color, bg_color, pastel)."""
    cs_advance = (word >> 14) & 3
    is_gram = ((word >> 13) & 1) == 0  # 0=GRAM
    bg = (word >> 11) & 3
    fg = (word >> 8) & 7
    pastel = (word >> 7) & 1
    card = word & 0x7F  # bits 6-0
    return is_gram, card, fg, bg, pastel, cs_advance

def gram_to_card_pixels(gram, card_num):
    """Extract 8x8 pixel data for a GRAM card.
    GRAM is stored as 16-bit words. Each card is 8 bytes (4 words).
    Word at $3800+N*4 contains bytes for rows 0-1, etc."""
    base = 0x3800 + card_num * 4
    pixels = []
    for word_offset in range(4):
        word = gram.get(base + word_offset, 0)
        # Low byte = even row, high byte = odd row
        pixels.append(word & 0xFF)        # row word_offset*2
        pixels.append((word >> 8) & 0xFF)  # row word_offset*2+1
    return pixels[:8]  # 8 rows

def render_screen(backtab, gram, output_path):
    """Render the full 20x12 tile grid."""
    SCREEN_W = 20
    SCREEN_H = 12
    TILE_PX = 8 * ZOOM
    
    img_w = SCREEN_W * TILE_PX + 200  # extra for legend
    img_h = SCREEN_H * TILE_PX + 60   # extra for title
    
    img = Image.new('RGB', (img_w, img_h), (0, 0, 0))
    pixels = img.load()
    
    # Track color stats
    color_stats = {}
    
    for row in range(SCREEN_H):
        for col in range(SCREEN_W):
            addr = 0x0200 + row * 20 + col
            word = backtab.get(addr, 0)
            is_gram, card_num, fg, bg, pastel, cs_adv = decode_backtab(word)
            
            # Get card pixel data
            if is_gram:
                card_rows = gram_to_card_pixels(gram, card_num)
            else:
                # GROM - we'd need GROM data; for now use blank
                card_rows = [0] * 8
            
            # Get colors
            if pastel:
                fg_color = PASTEL.get(fg, PALETTE.get(fg, (255,255,255)))
            else:
                fg_color = PALETTE.get(fg, (255, 255, 255))
            bg_color = PALETTE.get(bg, (0, 0, 0))
            
            # Draw the tile
            tx = col * TILE_PX
            ty = row * TILE_PX
            for y in range(8):
                row_byte = card_rows[y]
                for x in range(8):
                    bit = (row_byte >> (7 - x)) & 1
                    color = fg_color if bit else bg_color
                    color_stats[color] = color_stats.get(color, 0) + 1
                    for dy in range(ZOOM):
                        for dx in range(ZOOM):
                            px = tx + x * ZOOM + dx
                            py = ty + y * ZOOM + dy
                            if 0 <= px < img_w and 0 <= py < img_h:
                                pixels[px, py] = color
    
    # Add title/labels
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    draw.text((10, SCREEN_H * TILE_PX + 5), 
              f"Swords & Serpents - Title Screen (BackTab+GRAM from jzIntv)", 
              fill=(200, 200, 200), font=font)
    
    # Show color legend
    legend_x = SCREEN_W * TILE_PX + 10
    legend_y = 10
    draw.text((legend_x, legend_y), "Colors:", fill=(200, 200, 200), font=font)
    color_names = {v: k for k, v in {**PALETTE, **PASTEL}.items()}
    y_off = 30
    for color, count in sorted(color_stats.items(), key=lambda x: -x[1]):
        draw.rectangle([legend_x, legend_y + y_off, legend_x + 15, legend_y + y_off + 15], fill=color)
        draw.text((legend_x + 20, legend_y + y_off), f"cnt={count}", fill=(200, 200, 200), font=font)
        y_off += 18
    
    img.save(output_path)
    print(f"Saved: {output_path} ({img_w}x{img_h})")
    
    # Also dump tile grid as text
    print(f"\nTile grid (card numbers, FG/BG):")
    for row in range(SCREEN_H):
        line = ""
        for col in range(SCREEN_W):
            addr = 0x0200 + row * 20 + col
            word = backtab.get(addr, 0)
            is_gram, card_num, fg, bg, pastel, cs_adv = decode_backtab(word)
            if card_num == 3 and not pastel:
                line += " ."
            elif card_num != 0:
                line += f"{card_num:2d}"
            else:
                line += "  "
        print(line)
    
    return img

if __name__ == "__main__":
    backtab, gram = parse_jzintv_output("jzintv_room_v2.txt")
    print(f"BackTab entries: {len(backtab)}")
    print(f"GRAM entries: {len(gram)}")
    
    # Show unique card numbers
    cards_seen = set()
    for addr in range(0x200, 0x2F0):
        word = backtab.get(addr, 0)
        is_gram, card_num, fg, bg, pastel, cs_adv = decode_backtab(word)
        if card_num > 0:
            cards_seen.add(card_num)
    print(f"Unique GRAM cards used: {sorted(cards_seen)}")
    print(f"Max card: {max(cards_seen) if cards_seen else 0}")
    
    # Show GRAM card 3 pixel data
    print("\nGRAM card 3 pixel data:")
    for row_byte in gram_to_card_pixels(gram, 3):
        line = ""
        for b in range(7, -1, -1):
            line += "#" if (row_byte >> b) & 1 else "."
        print(f"  {line}")
    
    print("\nGRAM card 27 pixel data:")
    for row_byte in gram_to_card_pixels(gram, 27):
        line = ""
        for b in range(7, -1, -1):
            line += "#" if (row_byte >> b) & 1 else "."
        print(f"  {line}")
    
    render_screen(backtab, gram, "sprites/title_screen.png")
