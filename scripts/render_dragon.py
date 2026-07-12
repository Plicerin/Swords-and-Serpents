"""
Assemble the dragon/serpent RLE cards (0-3, 8, 11, 13-15, 21-23, 26-30)
into a full dragon sprite with correct IntelliVision STIC colors.

Card anatomy:
  0  - Dragon head (left-heavy, snout on left)
  1  - Chest/upper body (dense, top-heavy, 3 solid rows)
  2  - Main body core (densest, 3 solid rows)
  3  - Neck connector (top-heavy, sparse)
  8  - Serpent body coil (S-curve, balanced)
  11 - Tail segment (bot-heavy, small organic)
  13 - Body with heraldic mark (bot-heavy, diamond pattern, 2 solid rows)
  14 - Eye/head detail (rounded with diamond center)
  15 - Curved body diagonal (gradient stripe)
  21 - Body connector (organic, sparse)
  22 - Lower-mid body (bot-heavy, 3 solid rows, builds from sparse)
  23 - Wing lower-left (complex organic)
  26 - Wing (perfectly symmetric ornate — the WING card)
  27 - Tail tip (small, sparse, diagonal)
  28 - Tail continuation (sparse, reversed diagonal)
  29 - Upper-mid body (top-heavy, 3 solid rows, fades to sparse)
  30 - Wing lower-right (mirror pattern to 23)

STIC Colors:
  Dragon body      → Yellow (6) — rgb(255, 255, 0)
  Dragon eye/detail → Red (2) — rgb(200, 40, 40)  
  Wing membrane    → Yellow (6) with Dark Green(4) accent
  Serpent coil     → Green (5) — rgb(0, 255, 0)

Layout: 6 wide × 6 tall (24 tile grid, 17 dragon cards + 7 empty)
Dragon faces LEFT. Wings spread on both sides.
"""

from PIL import Image, ImageDraw, ImageFont
import os

# ============================================================
# TRUE INTELLIVISION 16-COLOR PALETTE
# ============================================================
INTV = [
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

BG        = INTV[0]   # Black void
DRAGON    = INTV[6]   # Yellow — dragon body/scales
EYE       = INTV[2]   # Red — eye/accents
WING      = INTV[6]   # Yellow — wing membrane
WING_DECO = INTV[4]   # Dark Green — wing ornament
SERPENT   = INTV[5]   # Green — serpent coil
SHADOW    = INTV[8]   # Grey — depth/shadow

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

def read_decle(addr):
    off = (addr - 0x5000) * 2
    if off + 1 < len(rom):
        return (rom[off] << 8) | rom[off + 1]
    return None

# Decode RLE cards
addr = 0x61E7
count = read_decle(addr + 1)
decoded = bytearray()
for i in range(count):
    entry = read_decle(addr + 2 + i)
    if entry is None: break
    repeat = ((entry >> 8) & 0x03) + 1
    for _ in range(repeat):
        decoded.append(entry & 0xFF)
cards = [list(decoded[c*8:(c+1)*8]) for c in range(len(decoded)//8)]

# ============================================================
# DRAW FUNCTIONS
# ============================================================

def hflip(card):
    """Return horizontally flipped card bytes."""
    flipped = []
    for row_byte in card:
        f = 0
        for i in range(8):
            if (row_byte >> i) & 1:
                f |= (1 << (7 - i))
        flipped.append(f)
    return flipped

def draw_card(pixels, tile_x, tile_y, card, zoom, color, bg=None):
    """Draw 8x8 card onto pixel buffer."""
    for row in range(8):
        byte_val = card[row]
        for col in range(8):
            px = tile_x + col * zoom
            py = tile_y + row * zoom
            is_px = (byte_val >> (7 - col)) & 1
            if is_px:
                for dy in range(zoom):
                    for dx in range(zoom):
                        if 0 <= px + dx < len(pixels[0]) and 0 <= py + dy < len(pixels):
                            pixels[py + dy][px + dx] = color
            elif bg is not None:
                for dy in range(zoom):
                    for dx in range(zoom):
                        if 0 <= px + dx < len(pixels[0]) and 0 <= py + dy < len(pixels):
                            pixels[py + dy][px + dx] = bg

# ============================================================
# DRAGON LAYOUT — 6 columns × 6 rows
# ============================================================
ZOOM = 14
TILE = 8 * ZOOM
COLS = 6
ROWS = 6

# Layout: (row, col, card_idx, color, hflip)
# None card_idx = empty tile
dragon_grid = [
    # Row 0: Wings + Head (centered: empty cols 0 & 5 for wing breathing room)
    [(0,0, None, None,    False),   # breathing room left
     (0,1, 26, WING,      False),   # Left wing top
     (0,2, 0,  DRAGON,    False),   # Dragon head (snout left)
     (0,3, 14, EYE,       False),   # Eye/head detail
     (0,4, 3,  DRAGON,    False),   # Neck
     (0,5, 26, WING,      True)],   # Right wing top (hflip)
     
    # Row 1: Upper wings + Chest
    [(1,0, None, None,    False),   # breathing room left
     (1,1, 23, WING,      False),   # Left wing lower
     (1,2, 1,  DRAGON,    False),   # Chest (dense, top-heavy)
     (1,3, 2,  DRAGON,    False),   # Body core (densest)
     (1,4, 15, DRAGON,    False),   # Body curve (diagonal)
     (1,5, 30, WING,      False)],  # Right wing lower
     
    # Row 2: Mid body
    [(2,0, None, None,    False),   # empty
     (2,1, None, None,    False),   # gap for neck
     (2,2, 29, DRAGON,    False),   # Upper-mid body
     (2,3, 13, DRAGON,    False),   # Heraldic body section
     (2,4, 22, DRAGON,    False),   # Lower-mid body
     (2,5, None, None,    False)],  # empty
     
    # Row 3: Lower body + serpent coil
    [(3,0, None, None,    False),   # empty
     (3,1, None, None,    False),   # empty
     (3,2, 21, DRAGON,    False),   # Body connector
     (3,3, 8,  SERPENT,   False),   # Serpent body coil
     (3,4, 11, DRAGON,    False),   # Body segment
     (3,5, None, None,    False)],  # empty
     
    # Row 4: Tail
    [(4,0, None, None,    False),   # empty
     (4,1, None, None,    False),   # empty
     (4,2, 28, SERPENT,   False),   # Tail continuation
     (4,3, 27, EYE,       False),   # Tail tip (red accent)
     (4,4, None, None,    False),   # empty
     (4,5, None, None,    False)],  # empty
     
    # Row 5: Ground shadow (empty row for visual breathing room)
    [(5,0, None, None,    False),
     (5,1, None, None,    False),
     (5,2, None, None,    False),
     (5,3, None, None,    False),
     (5,4, None, None,    False),
     (5,5, None, None,    False)],
]

# ============================================================
# RENDER OPTION 2: Alternative compact layout (5x5 grid)
# ============================================================
# More compact version without the right-side blank column
dragon_grid_v2 = [
    # Row 0: Wings + Head  
    [(0,0, 26, WING,      False),   # Left wing top
     (0,1, 0,  DRAGON,    False),   # Head
     (0,2, 14, EYE,       False),   # Eye detail
     (0,3, 3,  DRAGON,    False),   # Neck
     (0,4, 26, WING,      True)],   # Right wing top
     
    # Row 1: Wings + Chest
    [(1,0, 23, WING,      False),   # Left wing lower
     (1,1, 1,  DRAGON,    False),   # Chest  
     (1,2, 2,  DRAGON,    False),   # Body core
     (1,3, 15, DRAGON,    False),   # Body curve
     (1,4, 30, WING,      False)],  # Right wing lower
     
    # Row 2: Mid body
    [(2,0, None, None,    False),   # empty
     (2,1, 29, DRAGON,    False),   # Upper-mid body
     (2,2, 13, DRAGON,    False),   # Heraldic body
     (2,3, 22, DRAGON,    False),   # Lower-mid body
     (2,4, None, None,    False)],  # empty
     
    # Row 3: Lower body
    [(3,0, None, None,    False),   # empty
     (3,1, 21, DRAGON,    False),   # Connector
     (3,2, 8,  SERPENT,   False),   # Serpent coil
     (3,3, 11, DRAGON,    False),   # Segment
     (3,4, None, None,    False)],  # empty
     
    # Row 4: Tail
    [(4,0, None, None,    False),   # empty
     (4,1, 28, SERPENT,   False),   # Tail continuation
     (4,2, 27, EYE,       False),   # Tail tip (red)
     (4,3, None, None,    False),
     (4,4, None, None,    False)],
]

def render_dragon(grid, cols, rows, output_name, title_text, subtitle_text=""):
    """Render a dragon from a layout grid."""
    border = 2
    img_w = cols * TILE + border * TILE * 2
    img_h = rows * TILE + border * TILE * 2 + 80  # extra for title
    
    pixels = [[BG for _ in range(img_w)] for _ in range(img_h)]
    
    # Fill background area with near-black
    for y in range(img_h):
        for x in range(img_w):
            pixels[y][x] = BG
    
    # Draw each card in the grid
    for row_cells in grid:
        for (r, c, card_idx, color, flip) in row_cells:
            if card_idx is None:
                continue
            card = cards[card_idx]
            if flip:
                card = hflip(card)
            tx = (c + border) * TILE
            ty = (r + border) * TILE
            draw_card(pixels, tx, ty, card, ZOOM, color)
    
    # Convert to PIL
    img = Image.new('RGB', (img_w, img_h), BG)
    pix = img.load()
    for y in range(img_h):
        for x in range(img_w):
            pix[x, y] = pixels[y][x]
    
    draw_obj = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype("arial.ttf", 20)
        font_sub = ImageFont.truetype("arial.ttf", 13)
        font_small = ImageFont.truetype("arial.ttf", 10)
    except (OSError, IOError):
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Title bar
    title_y = img_h - 75
    draw_obj.text((border * TILE + 5, title_y), title_text, fill=DRAGON, font=font_title)
    if subtitle_text:
        draw_obj.text((border * TILE + 5, title_y + 25), subtitle_text, fill=(150, 150, 170), font=font_sub)
    
    # Color legend at bottom
    legend_y = title_y + 48
    legend_items = [
        (DRAGON, "Dragon body", "Yellow #6"),
        (EYE, "Eye/accent", "Red #2"),
        (SERPENT, "Serpent coil", "Green #5"),
    ]
    lx = border * TILE + 5
    for color, name, inv_num in legend_items:
        draw_obj.rectangle([lx, legend_y, lx + 12, legend_y + 10], fill=color, outline=(60, 60, 80))
        draw_obj.text((lx + 18, legend_y - 2), f"{name} ({inv_num})", fill=(180, 175, 200), font=font_small)
        lx += 160
    
    fname = f'sprites/{output_name}.png'
    img.save(fname)
    print(f"  Saved: {fname} ({img_w}x{img_h})")

# ============================================================
# RENDER BOTH LAYOUTS
# ============================================================
print("=" * 60)
print("DRAGON SPRITE ASSEMBLY")
print("=" * 60)
print(f"Using {len(cards)} RLE cards from ROM $61E7")
print(f"Dragon cards: [0,1,2,3,8,11,13,14,15,21,22,23,26,27,28,29,30]")
print(f"Zoom: {ZOOM}x  (each card = {TILE}x{TILE} px)")
print()

# Layout 1: 6x6 (wider, with gap column)
print("Layout 1 — 6×6 grid (wide, with gap for wing separation):")
render_dragon(dragon_grid, 6, 6, "dragon_wide",
    "DRAGON — Wide Layout (6×6 grid)",
    "17 RLE cards from ROM $61E7  |  STIC colors: Body=Yellow#6 Eye=Red#2 Serpent=Green#5")
print()

# Layout 2: 5x5 (compact)
print("Layout 2 — 5×5 grid (compact):")
render_dragon(dragon_grid_v2, 5, 5, "dragon_compact",
    "DRAGON — Compact Layout (5×5 grid)",
    "17 RLE cards  |  Dragon faces left with wings spread")
print()

# ============================================================
# RENDER CARDS IN NATURAL PAIRINGS (as they would appear on screen)
# ============================================================
print("Rendering individual card reference with colors...")

# All dragon cards with their assigned colors
dragon_cards_info = [
    (0,  "Head (snout left)", DRAGON),
    (1,  "Chest (dense)", DRAGON),
    (2,  "Body core", DRAGON),
    (3,  "Neck connector", DRAGON),
    (8,  "Serpent coil", SERPENT),
    (11, "Body segment", DRAGON),
    (13, "Heraldic body", DRAGON),
    (14, "Eye / detail", EYE),
    (15, "Body curve", DRAGON),
    (21, "Body connector", DRAGON),
    (22, "Lower-mid body", DRAGON),
    (23, "Wing lower L", WING),
    (26, "Wing ornate", WING),
    (27, "Tail tip", EYE),
    (28, "Tail cont.", SERPENT),
    (29, "Upper-mid body", DRAGON),
    (30, "Wing lower R", WING),
]

RZOOM = 18
RCARD = 8 * RZOOM
RCOLS = 6
RROWS = (len(dragon_cards_info) + RCOLS - 1) // RCOLS
r_w = RCOLS * (RCARD + 40) + 40
r_h = RROWS * (RCARD + 70) + 60

ref = Image.new('RGB', (r_w, r_h), BG)
ref_draw = ImageDraw.Draw(ref)
try:
    font_ref = ImageFont.truetype("arial.ttf", 11)
except (OSError, IOError):
    font_ref = ImageFont.load_default()

for idx, (card_idx, label, color) in enumerate(dragon_cards_info):
    col = idx % RCOLS
    row = idx // RCOLS
    cx = 30 + col * (RCARD + 40)
    cy = 30 + row * (RCARD + 70)
    card = cards[card_idx]
    
    ref_pix = ref.load()
    for r in range(8):
        byte_val = card[r]
        for c in range(8):
            if (byte_val >> (7 - c)) & 1:
                for dy in range(RZOOM):
                    for dx in range(RZOOM):
                        ref_pix[cx + c * RZOOM + dx, cy + r * RZOOM + dy] = color
    
    ref_draw.rectangle([cx-1, cy-1, cx+RCARD, cy+RCARD], outline=color, width=1)
    ref_draw.text((cx, cy + RCARD + 4), f"Card {card_idx}", fill=(180,180,200), font=font_ref)
    ref_draw.text((cx, cy + RCARD + 19), label, fill=color, font=font_ref)

ref_fname = 'sprites/dragon_card_reference.png'
ref.save(ref_fname)
print(f"  Saved: {ref_fname} ({r_w}x{r_h})")

print("\nDone! Rendered:")
print("  sprites/dragon_wide.png — Wide layout (6×6 grid)")
print("  sprites/dragon_compact.png — Compact layout (5×5 grid)")
print("  sprites/dragon_card_reference.png — Individual card reference")
