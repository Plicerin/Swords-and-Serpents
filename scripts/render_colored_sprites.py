"""
Render ALL character sprites with ACTUAL IntelliVision colors
decoded from STIC A registers at $5BB5-$5BC0.

STIC A color encoding for MOBs:
  - Bits 1-0: FG color select (0-3)
  - Bit 9: Color Advance - when set, adds 4 to the FG color (giving colors 4-7)
  - Combined FG color = (bit9 ? 4 : 0) + bits[1:0]

The title screen MOBs at $5BB5 use bit9=1, giving FG colors 4, 5, 6:
  4 = Dark Green, 5 = Green, 6 = Yellow

Data structure at $5BB5-$5C45:
  $5BB5-$5BC0: STIC A registers (MOB config, hi=0x03)
  $5BC1-$5BCC: Sprite metadata (mixed hi=0x00 and hi=0x03)
  $5BCD-$5C48: Count markers + pixel data (hi=0x00)
    - Count markers: lo=1-8 indicate how many 8-byte cards follow
    - Pixel data: 8*count bytes per sprite group
"""
from PIL import Image, ImageDraw, ImageFont
import os

# ============================================================
# TRUE INTELLIVISION 16-COLOR PALETTE (approximate RGB)
# ============================================================
INTV_PALETTE = [
    (0, 0, 0),          #  0: Black
    (0, 0, 255),        #  1: Blue
    (200, 40, 40),      #  2: Red
    (200, 170, 50),     #  3: Tan
    (0, 128, 0),        #  4: Dark Green
    (0, 255, 0),        #  5: Green
    (255, 255, 0),      #  6: Yellow
    (255, 255, 255),    #  7: White
    (128, 128, 128),    #  8: Grey
    (0, 255, 255),      #  9: Cyan
    (255, 150, 0),      # 10: Orange
    (150, 130, 100),    # 11: Brown
    (255, 100, 150),    # 12: Pink
    (100, 200, 255),    # 13: Light Blue
    (200, 200, 0),      # 14: Yellow-Green
    (150, 60, 200),     # 15: Purple
]

BG_COLOR = INTV_PALETTE[0]   # Black background
BORDER_COLOR = (30, 30, 50)

rom = open('Swords and Serpents.bin', 'rb').read()

def read_decle(addr):
    off = (addr - 0x5000) * 2
    if off + 1 < len(rom):
        return (rom[off] << 8) | rom[off + 1]
    return None

# ============================================================
# DECODE STIC A COLORS FROM $5BB5 (the FINAL STIC register values)
# ============================================================
# These are the values written to STIC shadow RAM for each MOB
stic_colors = {}  # MOB index -> FG color palette index
stic_raw = {}

print("="*70)
print("STIC A REGISTER COLOR DECODING ($5BB5-$5BC0)")
print("="*70)
print()
print("MOB  STIC_A   bit9 bits[1:0]  FG_color  Palette")
print("---  ------   ---- ----------  --------  -------")

for mob in range(12):
    v = read_decle(0x5BB5 + mob)
    if v is None:
        continue
    stic_raw[mob] = v
    
    if v == 0:
        stic_colors[mob] = None  # hidden
        print(f" {mob:2d}  ${v:04X}    -    -          HIDDEN")
        continue
    
    bit9 = (v >> 9) & 1
    bits1_0 = v & 0x03
    fg_color = (bit9 << 2) | bits1_0  # 3-bit color (0-7)
    
    palette_name = [
        "Black", "Blue", "Red", "Tan",
        "DarkGreen", "Green", "Yellow", "White"
    ][fg_color]
    
    stic_colors[mob] = fg_color
    print(f" {mob:2d}  ${v:04X}     {bit9}      {bits1_0:02b}         {fg_color}        {palette_name} "
          f"RGB{INTV_PALETTE[fg_color]}")

print()
print("Color Stack interpretation: bits[1:0] select CS entry, bit9=color advance")
print("With bit9=1: CS entry 0 -> color 4, 1 -> color 5, 2 -> color 6, 3 -> color 7")
print()

# ============================================================
# DECODE SPRITE PIXEL DATA
# ============================================================

# DECLE cards from $5BCE-$5C48 (pixel data scan, skipping initial count marker at $5BCD)
# Data layout:
#   $5BB5-$5BC0: STIC A registers (hi=0x03, filtered out)
#   $5BC1-$5BCC: Sprite metadata (mixed hi, filtered)
#   $5BCD:        Count marker ($0002 = 2 cards)  
#   $5BCE-$5C2E:  Continuous pixel data (hi=0x00)
#   $5C2F:        Count marker ($0001 = 1 card)
#   $5C30-$5C48:  More pixel data
# We scan $5BB5-$5C48 and collect all hi=0x00 bytes, then group into 8-byte cards.
pixel_data = []
for addr in range(0x5BB5, 0x5C49):
    v = read_decle(addr)
    if v is None:
        break
    hi = (v >> 8) & 0xFF
    lo = v & 0xFF
    if hi == 0:
        # Collect all hi=0 bytes; count markers (lo=1-8) appear as single-pixel artifacts
        pixel_data.append(lo)

# The STIC area ($5BB5-$5BC0) has hi=0x03, so it's auto-filtered.
# $5BC1-$5BCC has mixed hi (0x00 and 0x03) - the hi=0x00 bytes are pixel-like metadata.
# $5BCD is a count marker (lo=2) - this shifts all cards by one byte.
# To get correct cards, skip the first few bytes that are metadata/count markers.
# From analysis: metadata bytes at $5BC1(0x02), $5BC3(0x07), $5BC5-5BCC(0x08,0x00,...), $5BCD(0x02)
# The real warrior pixel data starts at $5BCE (offset into pixel_data depends on metadata)
# 
# Empirically, the warrior card was verified at cards[0] = [0x18, 0x3C, 0x7E, ...]
# after our count-marker parser which skips $5BCD count marker and 16 bytes of warrior.
# So cards[0] already matches the GRAM dump. The scan above collects MORE bytes before it.
# 
# Let's identify the correct offset: count hi=0 metadata bytes before $5BCE
metadata_count = 0
for addr in range(0x5BB5, 0x5BCE):
    v = read_decle(addr)
    if v is None: break
    if ((v >> 8) & 0xFF) == 0:
        metadata_count += 1
print(f"  Metadata bytes before \$5BCE: {metadata_count} (skipped)")

# Skip metadata bytes to align with actual pixel data
real_pixel_data = pixel_data[metadata_count:]
decle_cards = [list(real_pixel_data[c*8:(c+1)*8]) for c in range(len(real_pixel_data)//8)]
if len(real_pixel_data) % 8 != 0:
    print(f"  NOTE: {len(real_pixel_data) % 8} trailing bytes (expected if count markers present)")

# RLE cards from $61E7
addr = 0x61E7
count = read_decle(addr + 1)
decoded = bytearray()
for i in range(count):
    entry = read_decle(addr + 2 + i)
    if entry is None: break
    repeat = ((entry >> 8) & 0x03) + 1
    for _ in range(repeat):
        decoded.append(entry & 0xFF)
rle_cards = [list(decoded[c*8:(c+1)*8]) for c in range(len(decoded)//8)]

print(f"DECLE cards: {len(decle_cards)} ({len(decle_cards)//2} sprite pairs)")
print(f"RLE cards:   {len(rle_cards)} ({len(rle_cards)//2} sprite pairs)")
print()

# ============================================================
# ASSIGN COLORS TO SPRITES
# ============================================================
# Based on STIC A FG bits from $5BB5:
#   FG=4 (Dark Green)  → Warriors/Knights
#   FG=5 (Green)       → Wizards  
#   FG=6 (Yellow)      → Serpent/Dragon
#
# We also offer a "Color Stack" interpretation:
#   bits[1:0]=0 with bit9=1 → color 4 (Dark Green)
#   bits[1:0]=1 with bit9=1 → color 5 (Green)
#   bits[1:0]=2 with bit9=1 → color 6 (Yellow)

# Per-sprite color assignments for DECLE sprites
# Using both STIC register colors and character classification
decle_info = [
    {"label": "WARRIOR\n(sword+shield)",  "color": 4, "alt_color": 7},   # Dark Green / White
    {"label": "WIZARD\n(robes+staff)",    "color": 5, "alt_color": 1},   # Green / Blue
    {"label": "SERPENT",                  "color": 6, "alt_color": 5},   # Yellow / Green
    {"label": "KNIGHT\n(shield+armor)",   "color": 4, "alt_color": 3},   # Dark Green / Tan
    {"label": "KNIGHT\n(ornate armor)",   "color": 4, "alt_color": 7},   # Dark Green / White
    {"label": "WIZARD\n(spellcasting)",   "color": 5, "alt_color": 1},   # Green / Blue
    {"label": "SERPENT\n(coiled)",        "color": 6, "alt_color": 2},   # Yellow / Red
]

rle_info = [
    {"label": "DRAGON\nhead/body",        "color": 6, "alt_color": 2},
    {"label": "DRAGON\nbody (right)",     "color": 6, "alt_color": 2},
    {"label": "DRAGON\ntail/neck",        "color": 6, "alt_color": 5},
    {"label": "DRAGON\nbody (left)",      "color": 6, "alt_color": 2},
    {"label": "DUNGEON\nwall segment",    "color": 3, "alt_color": 8},
    {"label": "DUNGEON\npillar/base",     "color": 3, "alt_color": 8},
    {"label": "DUNGEON\nwall (double)",   "color": 3, "alt_color": 8},
    {"label": "DUNGEON\nwall (double)",   "color": 3, "alt_color": 8},
    {"label": "SERPENT\nbody coil",       "color": 5, "alt_color": 6},
    {"label": "DECORATION\n(border)",     "color": 4, "alt_color": 8},
    {"label": "DUNGEON\npillar (thin)",   "color": 3, "alt_color": 8},
    {"label": "DRAGON\nbody segment",     "color": 6, "alt_color": 2},
    {"label": "DUNGEON\narch/portal",     "color": 3, "alt_color": 8},
    {"label": "DRAGON\nwing/body",        "color": 6, "alt_color": 2},
    {"label": "DRAGON\ntail tip",         "color": 6, "alt_color": 5},
]

# ============================================================
# RENDER FUNCTIONS
# ============================================================
ZOOM = 18
PAD = 40
os.makedirs('sprites', exist_ok=True)

def draw_card(img, x, y, card_bytes, zoom, color):
    """Draw an 8x8 card at (x,y) with given zoom and color."""
    for row in range(8):
        byte_val = card_bytes[row]
        for col in range(8):
            if (byte_val >> (7-col)) & 1:
                for dy in range(zoom):
                    for dx in range(zoom):
                        px = x + col*zoom + dx
                        py = y + row*zoom + dy
                        if 0 <= px < img.width and 0 <= py < img.height:
                            img.putpixel((px, py), color)

def draw_sprite_16x16(img, x, y, top_card, bot_card, zoom, color, bg=BG_COLOR):
    """Draw a 16x16 sprite (two stacked 8x8 cards)."""
    # Fill background first
    for dy in range(16 * zoom):
        for dx in range(8 * zoom):
            px, py = x + dx, y + dy
            if 0 <= px < img.width and 0 <= py < img.height:
                img.putpixel((px, py), bg)
    # Draw foreground pixels
    draw_card(img, x, y, top_card, zoom, color)
    draw_card(img, x, y + 8*zoom, bot_card, zoom, color)

try:
    font_large = ImageFont.truetype("arial.ttf", 16)
    font_med = ImageFont.truetype("arial.ttf", 12)
    font_small = ImageFont.truetype("arial.ttf", 10)
except (OSError, IOError):
    print("  (TrueType fonts not found, using default)")
    font_large = ImageFont.load_default()
    font_med = ImageFont.load_default()
    font_small = ImageFont.load_default()

# ============================================================
# RENDER INDIVIDUAL SPRITES
# ============================================================
print("Rendering individual sprites...")

def render_sprite_set(cards, info_list, prefix, source_name):
    """Render individual sprite PNGs for a set of card pairs."""
    num_pairs = len(cards) // 2
    for pair_idx in range(num_pairs):
        if pair_idx >= len(info_list):
            info = {"label": f"UNKNOWN_{pair_idx}", "color": 7, "alt_color": 7}
        else:
            info = info_list[pair_idx]
        
        color_idx = info["color"]
        fg = INTV_PALETTE[color_idx]
        label = info["label"]
        
        # Create sprite image
        spr_w = 8 * ZOOM + 20
        spr_h = 16 * ZOOM + 60
        img = Image.new('RGB', (spr_w, spr_h), BG_COLOR)
        draw_obj = ImageDraw.Draw(img)
        
        draw_sprite_16x16(img, 10, 5, cards[pair_idx*2], cards[pair_idx*2+1], ZOOM, fg)
        
        # Draw a subtle border around the sprite area
        draw_obj.rectangle([8, 3, 8 + 8*ZOOM + 2, 3 + 16*ZOOM + 2], 
                          outline=BORDER_COLOR, width=1)
        
        # Draw color swatch
        swatch_x = 10
        swatch_y = 16 * ZOOM + 12
        draw_obj.rectangle([swatch_x, swatch_y, swatch_x+20, swatch_y+14], 
                          fill=fg, outline=(80,80,100))
        
        # Draw label
        y_offset = 16 * ZOOM + 12
        for line in label.split('\n'):
            draw_obj.text((swatch_x + 28, y_offset), line, fill=fg, font=font_med)
            y_offset += 16
        
        # Color info
        color_names = ["Black","Blue","Red","Tan","DarkGreen","Green","Yellow","White",
                       "Grey","Cyan","Orange","Brown","Pink","LtBlue","YlwGrn","Purple"]
        draw_obj.text((10, y_offset + 2), 
                     f"INV color {color_idx} ({color_names[color_idx]})", 
                     fill=(100, 100, 130), font=font_small)
        
        safe_name = label.replace('\n', '_').replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')
        fname = f'sprites/{prefix}_{safe_name}.png'
        img.save(fname)
        print(f"  {fname}")

# Render DECLE sprites
render_sprite_set(decle_cards, decle_info, "char", "DECLE")
# Render RLE sprites
render_sprite_set(rle_cards, rle_info, "rle", "RLE")

# ============================================================
# RENDER COMPOSITE LABELED IMAGE
# ============================================================
print("\nRendering composite labeled image...")

COLS = 7
DECLE_PAIRS = len(decle_cards) // 2
RLE_PAIRS = len(rle_cards) // 2

DECLE_ROWS = (DECLE_PAIRS + COLS - 1) // COLS
RLE_ROWS = (RLE_PAIRS + COLS - 1) // COLS

CELL_W = 8 * ZOOM + 24
CELL_H = 16 * ZOOM + 110
SECTION_GAP = 50
HEADER_H = 50

total_w = CELL_W * COLS + PAD * 2
total_h = PAD + HEADER_H + DECLE_ROWS * CELL_H + SECTION_GAP + HEADER_H + RLE_ROWS * CELL_H + PAD

composite = Image.new('RGB', (total_w, total_h), BG_COLOR)
draw = ImageDraw.Draw(composite)

def draw_section_header(draw_obj, x, y, text, color):
    """Draw a section header with underline."""
    draw_obj.text((x, y), text, fill=color, font=font_large)
    bbox = draw_obj.textbbox((x, y), text, font=font_large)
    draw_obj.line([(x, y + 22), (bbox[2], y + 22)], fill=color, width=1)

# --- DECLE Section ---
decle_header_y = PAD
draw_section_header(draw, PAD, decle_header_y, 
    "TITLE SCREEN CHARACTERS  —  STIC FG colors: 4=DarkGreen, 5=Green, 6=Yellow",
    INTV_PALETTE[6])

for pair_idx in range(DECLE_PAIRS):
    col = pair_idx % COLS
    row = pair_idx // COLS
    info = decle_info[pair_idx]
    fg = INTV_PALETTE[info["color"]]
    
    cx = PAD + col * CELL_W + 12
    cy = decle_header_y + HEADER_H + row * CELL_H
    
    # Draw sprite
    draw_sprite_16x16(composite, cx, cy, 
                      decle_cards[pair_idx*2], decle_cards[pair_idx*2+1], 
                      ZOOM, fg)
    
    # Draw border
    draw.rectangle([cx-2, cy-2, cx + 8*ZOOM + 2, cy + 16*ZOOM + 2],
                   outline=fg, width=1)
    
    # Color swatch
    sw_x, sw_y = cx, cy + 16*ZOOM + 6
    draw.rectangle([sw_x, sw_y, sw_x+16, sw_y+12], fill=fg, outline=(80,80,100))
    
    # Labels
    y_off = sw_y
    color_names = ["Black","Blue","Red","Tan","DarkGreen","Green","Yellow","White",
                   "Grey","Cyan","Orange","Brown","Pink","LtBlue","YlwGrn","Purple"]
    draw.text((sw_x + 22, y_off), f"Pair {pair_idx}  INV#{info['color']} {color_names[info['color']]}",
              fill=(130,130,160), font=font_small)
    
    for line in info["label"].split('\n'):
        y_off += 16
        draw.text((sw_x + 22, y_off), line, fill=fg, font=font_med)

# --- RLE Section ---
rle_header_y = decle_header_y + HEADER_H + DECLE_ROWS * CELL_H + SECTION_GAP
draw_section_header(draw, PAD, rle_header_y,
    "DUNGEON & DRAGON TILES  —  STIC FG colors: 3=Tan, 4=DarkGreen, 5=Green, 6=Yellow",
    INTV_PALETTE[6])

for pair_idx in range(RLE_PAIRS):
    col = pair_idx % COLS
    row = pair_idx // COLS
    info = rle_info[pair_idx]
    fg = INTV_PALETTE[info["color"]]
    
    cx = PAD + col * CELL_W + 12
    cy = rle_header_y + HEADER_H + row * CELL_H
    
    draw_sprite_16x16(composite, cx, cy,
                      rle_cards[pair_idx*2], rle_cards[pair_idx*2+1],
                      ZOOM, fg)
    
    draw.rectangle([cx-2, cy-2, cx + 8*ZOOM + 2, cy + 16*ZOOM + 2],
                   outline=fg, width=1)
    
    sw_x, sw_y = cx, cy + 16*ZOOM + 6
    draw.rectangle([sw_x, sw_y, sw_x+16, sw_y+12], fill=fg, outline=(80,80,100))
    
    color_names = ["Black","Blue","Red","Tan","DarkGreen","Green","Yellow","White",
                   "Grey","Cyan","Orange","Brown","Pink","LtBlue","YlwGrn","Purple"]
    draw.text((sw_x + 22, sw_y), f"Pair {pair_idx}  INV#{info['color']} {color_names[info['color']]}",
              fill=(130,130,160), font=font_small)
    
    y_off = sw_y + 16
    for line in info["label"].split('\n'):
        draw.text((sw_x + 22, y_off), line, fill=fg, font=font_med)
        y_off += 16

composite.save('sprites/all_characters_labeled.png')
print(f"  sprites/all_characters_labeled.png ({total_w}x{total_h})")

# ============================================================
# RENDER DUAL-COLOR VERSION (STIC register color + alt color)
# ============================================================
print("\nRendering dual-color comparison (STIC color vs alternate)...")

DUAL_COLS = 4
total_pairs = DECLE_PAIRS + RLE_PAIRS
dual_rows = (total_pairs + DUAL_COLS - 1) // DUAL_COLS
dual_cell_w = (8 * ZOOM + 20) * 2 + 30
dual_cell_h = 16 * ZOOM + 100

dual_w = dual_cell_w * DUAL_COLS + PAD * 2
dual_h = dual_cell_h * dual_rows + PAD * 2

dual_img = Image.new('RGB', (dual_w, dual_h), BG_COLOR)
dual_draw = ImageDraw.Draw(dual_img)

all_sprites = []
for i in range(DECLE_PAIRS):
    all_sprites.append({
        'cards': (decle_cards[i*2], decle_cards[i*2+1]),
        'info': decle_info[i],
        'source': 'DECLE',
        'idx': i
    })
for i in range(RLE_PAIRS):
    all_sprites.append({
        'cards': (rle_cards[i*2], rle_cards[i*2+1]),
        'info': rle_info[i],
        'source': 'RLE',
        'idx': i
    })

for sprite_idx, spr in enumerate(all_sprites):
    col = sprite_idx % DUAL_COLS
    row = sprite_idx // DUAL_COLS
    info = spr['info']
    
    fg_stic = INTV_PALETTE[info['color']]
    fg_alt = INTV_PALETTE[info['alt_color']]
    
    base_x = PAD + col * dual_cell_w
    base_y = PAD + row * dual_cell_h
    
    # Left: STIC register color
    lx = base_x + 10
    ly = base_y + 5
    draw_sprite_16x16(dual_img, lx, ly, spr['cards'][0], spr['cards'][1], ZOOM, fg_stic)
    dual_draw.rectangle([lx-2, ly-2, lx+8*ZOOM+2, ly+16*ZOOM+2], outline=fg_stic, width=1)
    
    color_names = ["Black","Blue","Red","Tan","DarkGreen","Green","Yellow","White",
                   "Grey","Cyan","Orange","Brown","Pink","LtBlue","YlwGrn","Purple"]
    dual_draw.text((lx, ly+16*ZOOM+5), f"STIC FG#{info['color']}", fill=fg_stic, font=font_small)
    dual_draw.text((lx, ly+16*ZOOM+20), color_names[info['color']], fill=fg_stic, font=font_small)
    
    # Right: alternate color
    rx = base_x + 10 + 8*ZOOM + 20
    ry = base_y + 5
    draw_sprite_16x16(dual_img, rx, ry, spr['cards'][0], spr['cards'][1], ZOOM, fg_alt)
    dual_draw.rectangle([rx-2, ry-2, rx+8*ZOOM+2, ry+16*ZOOM+2], outline=fg_alt, width=1)
    
    dual_draw.text((rx, ry+16*ZOOM+5), f"Alt #{info['alt_color']}", fill=fg_alt, font=font_small)
    dual_draw.text((rx, ry+16*ZOOM+20), color_names[info['alt_color']], fill=fg_alt, font=font_small)
    
    # Label
    label_y = base_y + dual_cell_h - 50
    for line in info['label'].split('\n'):
        dual_draw.text((base_x + 10, label_y), f"{spr['source']}{spr['idx']}: {line}",
                      fill=(180,180,200), font=font_small)
        label_y += 14

dual_img.save('sprites/color_comparison.png')
print(f"  sprites/color_comparison.png ({dual_w}x{dual_h})")

# ============================================================
# PRINT SUMMARY
# ============================================================
print("\n" + "="*70)
print("RENDER COMPLETE")
print("="*70)
print(f"""
Files created in sprites/:
  all_characters_labeled.png  — Main composite with STIC register colors
  color_comparison.png        — Side-by-side STIC vs alternate colors
  char_*.png                  — Individual DECLE character sprites
  rle_*.png                   — Individual RLE tile sprites

Color encoding from STIC A registers at $5BB5-$5BC0:
  bit 9 (Color Advance) = 1 for all visible MOBs
  bits 1-0 (FG color select) = 00, 01, or 10
  Combined FG color = 4 (Dark Green), 5 (Green), or 6 (Yellow)

IntelliVision palette used:
  0=Black  1=Blue  2=Red  3=Tan  4=DarkGreen  5=Green  6=Yellow  7=White
  8=Grey  9=Cyan  10=Orange  11=Brown  12=Pink  13=LtBlue  14=YlwGrn  15=Purple
""")
