"""
Render a complete dungeon room mockup using RLE tile data from ROM $61E7
with correct IntelliVision STIC register colors.

Tiles available (31 cards indexed 0-30):
  DUNGEON:
    4  - Vertical pillar (left edge)        → Tan (3)
    5  - Horizontal wall top (solid band)    → Tan (3)
    6  - Pillar column (brick pattern)       → Tan (3)
    7  - Pillar column (identical to 6)      → Tan (3)
    9  - Decorative border (striped)         → DarkGreen (4)
    10 - Brick/stone texture (repeating)     → Tan (3)
    12 - Arch/portal (archway shape)         → Yellow (6)
    16 - Door decoration (cross pattern)     → DarkGreen (4)
    17 - Wall side (vertical stripes)        → Tan (3)
    18 - Diamond/floor pattern               → Tan (3)
    19 - Wall base (single-line cap)         → Tan (3)
    20 - Floor tile (rounded square)         → Tan (3)
    24 - Column capital (side extensions)    → Tan (3)
    25 - Horizontal beam (bar pattern)       → Tan (3)

  DECORATION:
    9  - Also usable as border filigree      → DarkGreen (4)
    16 - Portal frame ornament               → DarkGreen (4)

Room layout (14 tiles wide × 10 tiles tall):
  ┌──────────────────────────────────┐
  │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ ← Top wall (card 5)
  │░▓▓▓▓▒▒▓▓▓▓░▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░│ ← Arch + top wall
  │░▓▓▓▓▒▒▓▓▓▓░▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░│
  │░│  ♜  │  ♜  │        ♜       │░│ ← Pillars + side walls
  │░│     │     │                │░│
  │░│  ♜  │     │  ♜        ♜   │░│
  │░│     │     │                │░│
  │░│  ♜  │  ♜  │     ♜         │░│
  │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ ← Bottom wall
  │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│ ← Base (card 19)
  └──────────────────────────────────┘

Floor tiles: card 20 (rounded square) filling the open space
Side walls: card 17 (vertical stripes)
Top wall: card 5 (solid top) / card 25 (beam)
Pillars: cards 6/7 pairs (brick columns)
Arch/portal: card 12 centered in top wall
Bottom wall: card 19 base + card 5 top
Corners: card 9 / card 24 (decorative)
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

# Color scheme
BG       = INTV[0]   # Black (void outside room)
FLOOR    = INTV[3]   # Tan (stone floor)
WALL     = INTV[3]   # Tan (stone walls)
PILLAR   = INTV[3]   # Tan (stone pillars)
PORTAL   = INTV[6]   # Yellow (glowing portal)
DECO     = INTV[4]   # Dark Green (decorative elements)
DARK     = INTV[8]   # Grey (shadow/depth)
ROOM_BG  = (20, 15, 5)  # Very dark brown (room interior darkness)

rom = open('Swords and Serpents.bin', 'rb').read()

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
# TILE INDEX MAP (which RLE card for each role)
# ============================================================
T_WALL_TOP       = 5    # Horizontal solid band
T_WALL_SIDE      = 17   # Vertical stripes
T_WALL_BASE      = 19   # Bottom cap with single line
T_WALL_BEAM      = 25   # Horizontal beam/bar
T_PILLAR_TOP     = 4    # Pillar top/cap
T_PILLAR_MID     = 6    # Pillar column (brick) - use 6 for left, 7 for right
T_PILLAR_MID2    = 7    # Pillar column variant
T_FLOOR          = 20   # Rounded square floor pattern
T_PORTAL_TOP     = 12   # Arch/portal upper
T_PORTAL_BOT     = 16   # Portal frame lower
T_CORNER_DECO    = 9    # Decorative corner
T_DECO_CAPITAL   = 24   # Column capital
T_BRICK          = 10   # Brick texture
T_ARCH_FILL      = 18   # Diamond pattern fill (behind arch)

# ============================================================
# DRAW FUNCTIONS
# ============================================================

def draw_card_raw(pixels, tile_x, tile_y, card_bytes, zoom, color, bg=None):
    """Draw an 8x8 card at tile position with given zoom and color."""
    for row in range(8):
        byte_val = card_bytes[row]
        for col in range(8):
            px = tile_x + col * zoom
            py = tile_y + row * zoom
            if (byte_val >> (7 - col)) & 1:
                for dy in range(zoom):
                    for dx in range(zoom):
                        if 0 <= px + dx < len(pixels[0]) and 0 <= py + dy < len(pixels):
                            pixels[py + dy][px + dx] = color
            elif bg is not None:
                for dy in range(zoom):
                    for dx in range(zoom):
                        if 0 <= px + dx < len(pixels[0]) and 0 <= py + dy < len(pixels):
                            pixels[py + dy][px + dx] = bg

def draw_card_hflip(pixels, tile_x, tile_y, card_bytes, zoom, color, bg=None):
    """Draw an 8x8 card horizontally flipped."""
    flipped = []
    for row_byte in card_bytes:
        f = 0
        for i in range(8):
            if (row_byte >> i) & 1:
                f |= (1 << (7 - i))
        flipped.append(f)
    draw_card_raw(pixels, tile_x, tile_y, flipped, zoom, color, bg)

def draw_card_vflip(pixels, tile_x, tile_y, card_bytes, zoom, color, bg=None):
    """Draw an 8x8 card vertically flipped."""
    flipped = list(reversed(card_bytes))
    draw_card_raw(pixels, tile_x, tile_y, flipped, zoom, color, bg)

def fill_tile(pixels, tile_x, tile_y, zoom, color):
    """Fill an 8x8 tile area with solid color."""
    for dy in range(8 * zoom):
        for dx in range(8 * zoom):
            px, py = tile_x + dx, tile_y + dy
            if 0 <= px < len(pixels[0]) and 0 <= py < len(pixels):
                pixels[py][px] = color

# ============================================================
# ROOM LAYOUT
# ============================================================
ZOOM = 12
TILE = 8 * ZOOM  # pixels per tile

# Room grid: 16 tiles wide × 12 tiles tall
ROOM_W = 16
ROOM_H = 12

# Total image size (with border for void/corridor outside room)
BORDER_TILES = 2
IMG_W = (ROOM_W + BORDER_TILES * 2) * TILE
IMG_H = (ROOM_H + BORDER_TILES * 2) * TILE

# Legend panel on the right side
LEGEND_W = 260
LEGEND_X = IMG_W + 20
TOTAL_W = IMG_W + LEGEND_W + 40
TOTAL_H = IMG_H + 60

os.makedirs('sprites', exist_ok=True)

# Create pixel buffer
pixels = [[BG for _ in range(TOTAL_W)] for _ in range(TOTAL_H)]

# Helper: convert tile coords to pixel coords
def tx(c): return (c + BORDER_TILES) * TILE

# ============================================================
# DRAW ROOM
# ============================================================

# --- Room background (void outside room is already Black) ---
# Fill the room interior with darkness
for ty in range(ROOM_H):
    for trow in range(TILE):
        for tx_pos in range(ROOM_W):
            for tcol in range(TILE):
                px = (tx_pos + BORDER_TILES) * TILE + tcol
                py = (ty + BORDER_TILES) * TILE + trow
                pixels[py][px] = ROOM_BG

# --- Floor (fill room interior with floor pattern) ---
# Floor covers rows 2-9, columns 1-14 (inside walls)
for ty in range(3, ROOM_H - 2):  # rows 3-9
    for tx_pos in range(1, ROOM_W - 1):  # columns 1-14
        draw_card_raw(pixels, tx(tx_pos), tx(ty), cards[T_FLOOR], ZOOM, FLOOR, ROOM_BG)

# --- Top wall (row 1, the ceiling wall) ---
for tx_pos in range(0, ROOM_W):
    draw_card_raw(pixels, tx(tx_pos), tx(1), cards[T_WALL_TOP], ZOOM, WALL, ROOM_BG)
    if tx_pos > 0 and tx_pos < ROOM_W - 1:
        # Add beam layer above top wall
        draw_card_raw(pixels, tx(tx_pos), tx(0), cards[T_WALL_BEAM], ZOOM, WALL, BG)

# --- Arch/Portal in top wall (columns 6-9) ---
# Portal arch (card 12) spanning 2 tiles wide
# Clear the wall tiles first
for tx_pos in range(6, 10):
    fill_tile(pixels, tx(tx_pos), tx(1), ZOOM, ROOM_BG)
    fill_tile(pixels, tx(tx_pos), tx(0), ZOOM, BG)

# Draw portal arch (2 tiles wide, 2 tiles tall)
draw_card_raw(pixels, tx(7), tx(0), cards[T_PORTAL_TOP], ZOOM, PORTAL, BG)
draw_card_hflip(pixels, tx(8), tx(0), cards[T_PORTAL_TOP], ZOOM, PORTAL, BG)
# Portal frame below arch
draw_card_raw(pixels, tx(7), tx(1), cards[T_PORTAL_BOT], ZOOM, PORTAL, ROOM_BG)
draw_card_hflip(pixels, tx(8), tx(1), cards[T_PORTAL_BOT], ZOOM, PORTAL, ROOM_BG)
# Diamond fill behind portal opening (row 2)
draw_card_raw(pixels, tx(7), tx(2), cards[T_ARCH_FILL], ZOOM, DECO, ROOM_BG)
draw_card_hflip(pixels, tx(8), tx(2), cards[T_ARCH_FILL], ZOOM, DECO, ROOM_BG)
# Portal glow on floor below (bg=None so floor shows through gaps)
draw_card_raw(pixels, tx(7), tx(3), cards[T_ARCH_FILL], ZOOM, PORTAL, bg=None)
draw_card_hflip(pixels, tx(8), tx(3), cards[T_ARCH_FILL], ZOOM, PORTAL, bg=None)

# --- Side walls (left and right columns) ---
for ty in range(1, ROOM_H - 1):
    if ty == 1 or ty == ROOM_H - 2:
        continue  # top/bottom handled separately
    
    # Left wall
    draw_card_raw(pixels, tx(0), tx(ty), cards[T_WALL_SIDE], ZOOM, WALL, ROOM_BG)
    # Right wall (horizontal flip for symmetry)
    draw_card_hflip(pixels, tx(ROOM_W - 1), tx(ty), cards[T_WALL_SIDE], ZOOM, WALL, ROOM_BG)

# --- Bottom wall ---
for tx_pos in range(0, ROOM_W):
    draw_card_raw(pixels, tx(tx_pos), tx(ROOM_H - 2), cards[T_WALL_TOP], ZOOM, WALL, ROOM_BG)
    # Base below
    draw_card_raw(pixels, tx(tx_pos), tx(ROOM_H - 1), cards[T_WALL_BASE], ZOOM, WALL, ROOM_BG)

# --- Corner decorations ---
# Top-left corner
draw_card_raw(pixels, tx(0), tx(0), cards[T_CORNER_DECO], ZOOM, DECO, BG)
# Top-right corner (hflip)
draw_card_hflip(pixels, tx(ROOM_W - 1), tx(0), cards[T_CORNER_DECO], ZOOM, DECO, BG)

# Capital decorations on top wall at intervals
for cap_x in [3, 12]:
    draw_card_raw(pixels, tx(cap_x), tx(0), cards[T_DECO_CAPITAL], ZOOM, DECO, BG)
    draw_card_raw(pixels, tx(cap_x + 1), tx(0), cards[T_DECO_CAPITAL], ZOOM, DECO, BG)

# --- PILLARS ---
# Pillars are 1 tile wide, 2 tiles tall (top cap + mid section)
# Each pillar = card 4 (top) + card 6/7 (mid)

def draw_pillar(col, start_row, height):
    """Draw a pillar at tile column, starting at row, with given height."""
    # Pillar top cap
    draw_card_raw(pixels, tx(col), tx(start_row), cards[T_PILLAR_TOP], ZOOM, PILLAR, ROOM_BG)
    # Pillar mid sections
    for r in range(height):
        mid_card = cards[T_PILLAR_MID] if (r % 2 == 0) else cards[T_PILLAR_MID2]
        draw_card_raw(pixels, tx(col), tx(start_row + 1 + r), cards[T_PILLAR_MID], ZOOM, PILLAR, ROOM_BG)
    # Pillar base (bg=None so floor shows through transparent areas)
    draw_card_vflip(pixels, tx(col), tx(start_row + 1 + height), cards[T_PILLAR_TOP], ZOOM, PILLAR, bg=None)

# Left side pillars
draw_pillar(2, 3, 5)   # Tall pillar, left side
draw_pillar(2, 8, 1)   # Short pillar near bottom, left side

# Right side pillars  
draw_pillar(13, 3, 5)  # Tall pillar, right side
draw_pillar(13, 9, 1)  # Short pillar near bottom, right side

# Center pillars
draw_pillar(5, 4, 3)   # Mid pillar near portal
draw_pillar(10, 4, 3)  # Mid pillar near portal

# Far pillars (near bottom)
draw_pillar(7, 7, 2)
draw_pillar(9, 8, 2)

# --- Floor accent (brick texture in center aisle) ---
for tx_pos in range(6, 10):
    draw_card_raw(pixels, tx(tx_pos), tx(6), cards[T_BRICK], ZOOM, WALL, ROOM_BG)

# --- Shadow under pillars (drawn BEFORE bottom wall so wall covers gaps) ---
# (Simple approach: draw dark tint under pillar bases on the floor row only)
for tx_pos in [1, 2, 3, 12, 13, 14]:
    draw_card_raw(pixels, tx(tx_pos), tx(ROOM_H - 3), cards[T_FLOOR], ZOOM, DARK, bg=None)

# ============================================================
# CONVERT PIXEL BUFFER TO IMAGE
# ============================================================
img = Image.new('RGB', (TOTAL_W, TOTAL_H), BG)
pix = img.load()
for y in range(TOTAL_H):
    for x in range(TOTAL_W):
        pix[x, y] = pixels[y][x]

# ============================================================
# LEGEND PANEL
# ============================================================
try:
    font_title = ImageFont.truetype("arial.ttf", 18)
    font_body = ImageFont.truetype("arial.ttf", 12)
    font_small = ImageFont.truetype("arial.ttf", 10)
except (OSError, IOError):
    font_title = ImageFont.load_default()
    font_body = ImageFont.load_default()
    font_small = ImageFont.load_default()

draw_obj = ImageDraw.Draw(img)

# Legend background
legend_bg = (15, 12, 20)
draw_obj.rectangle([LEGEND_X, 20, TOTAL_W - 20, IMG_H + 20], fill=legend_bg, outline=(60, 55, 70))

lx = LEGEND_X + 20
ly = 40

draw_obj.text((lx, ly), "DUNGEON ROOM", fill=PORTAL, font=font_title)
ly += 30
draw_obj.text((lx, ly), "Swords & Serpents", fill=WALL, font=font_body)
ly += 20
draw_obj.text((lx, ly), "RLE tiles from ROM $61E7", fill=(120, 115, 140), font=font_small)
ly += 30

# Color legend
legend_items = [
    (WALL, "Wall / Pillar (Tan, #3)"),
    (FLOOR, "Floor (Tan, #3)"),
    (PORTAL, "Portal/Arch (Yellow, #6)"),
    (DECO, "Decoration (Dark Green, #4)"),
    (DARK, "Shadow (Grey, #8)"),
    (ROOM_BG, "Room darkness"),
    (BG, "Void (Black, #0)"),
]

draw_obj.text((lx, ly), "INTV Color Palette", fill=PORTAL, font=font_body)
ly += 22

for color, label in legend_items:
    draw_obj.rectangle([lx, ly, lx + 16, ly + 12], fill=color, outline=(80, 80, 100))
    draw_obj.text((lx + 22, ly - 1), label, fill=(200, 195, 210), font=font_small)
    ly += 16

ly += 16
draw_obj.text((lx, ly), "Tile Layout:", fill=PORTAL, font=font_body)
ly += 20

tile_legend = [
    ("Card 5", "Top/bottom wall"),
    ("Card 17", "Side wall (striped)"),
    ("Card 19", "Wall base cap"),
    ("Card 25", "Horizontal beam"),
    ("Card 4+6+7", "Pillar (cap+column)"),
    ("Card 12", "Arch/portal top"),
    ("Card 16", "Portal frame"),
    ("Card 20", "Floor (rounded sq.)"),
    ("Card 9", "Corner decoration"),
    ("Card 24", "Column capital"),
    ("Card 10", "Brick texture"),
    ("Card 18", "Diamond fill"),
]

for card_id, desc in tile_legend:
    draw_obj.text((lx, ly), f"  {card_id}", fill=WALL, font=font_small)
    draw_obj.text((lx + 80, ly), desc, fill=(180, 175, 200), font=font_small)
    ly += 15

ly += 10
draw_obj.text((lx, ly), f"Room: {ROOM_W}x{ROOM_H} tiles", fill=(120, 115, 140), font=font_small)
ly += 14
draw_obj.text((lx, ly), f"Zoom: {ZOOM}x  ({ROOM_W*8*ZOOM}x{ROOM_H*8*ZOOM} px)", fill=(120, 115, 140), font=font_small)

# ============================================================
# SAVE
# ============================================================
fname = 'sprites/dungeon_room_mockup.png'
img.save(fname)
print(f"Saved: {fname} ({TOTAL_W}x{TOTAL_H})")

# ============================================================
# ALSO RENDER: Tile reference sheet with all dungeon tiles labeled
# ============================================================
print("\nRendering dungeon tile reference sheet...")

T_ZOOM = 16
T_GAP = 10
T_COLS = 8
dungeon_tiles = [
    (4,  "Pillar\ncap", PILLAR),
    (5,  "Wall\ntop", WALL),
    (6,  "Pillar\ncol A", PILLAR),
    (7,  "Pillar\ncol B", PILLAR),
    (9,  "Corner\ndeco", DECO),
    (10, "Brick\ntexture", WALL),
    (12, "Arch\nportal", PORTAL),
    (16, "Portal\nframe", PORTAL),
    (17, "Wall\nside", WALL),
    (18, "Diamond\nfill", DECO),
    (19, "Wall\nbase", WALL),
    (20, "Floor\ntile", FLOOR),
    (24, "Column\ncapital", DECO),
    (25, "Beam\nbar", WALL),
]

num_tiles = len(dungeon_tiles)
ref_rows = (num_tiles + T_COLS - 1) // T_COLS
cell_w = 8 * T_ZOOM + 40
cell_h = 8 * T_ZOOM + 80
ref_w = T_COLS * cell_w + 40
ref_h = ref_rows * cell_h + 60

ref_img = Image.new('RGB', (ref_w, ref_h), BG)
ref_draw = ImageDraw.Draw(ref_img)

# Title
ref_draw.text((20, 10), "DUNGEON TILE REFERENCE — RLE $61E7", fill=PORTAL, font=font_title)

for idx, (card_idx, label, color) in enumerate(dungeon_tiles):
    col = idx % T_COLS
    row = idx // T_COLS
    
    cx = 20 + col * cell_w + 16
    cy = 50 + row * cell_h
    
    card = cards[card_idx]
    ref_pix = ref_img.load()
    for r in range(8):
        byte_val = card[r]
        for c in range(8):
            px = cx + c * T_ZOOM
            py = cy + r * T_ZOOM
            if (byte_val >> (7 - c)) & 1:
                for dy in range(T_ZOOM):
                    for dx in range(T_ZOOM):
                        ref_pix[px + dx, py + dy] = color
    
    # Border
    ref_draw.rectangle([cx-1, cy-1, cx + 8*T_ZOOM, cy + 8*T_ZOOM], outline=color)
    
    # Card number
    ref_draw.text((cx, cy + 8*T_ZOOM + 5), f"Card {card_idx}", fill=(180, 180, 200), font=font_small)
    
    # Label
    y_off = cy + 8*T_ZOOM + 22
    for line in label.split('\n'):
        ref_draw.text((cx, y_off), line, fill=color, font=font_small)
        y_off += 14

ref_fname = 'sprites/dungeon_tile_reference.png'
ref_img.save(ref_fname)
print(f"Saved: {ref_fname} ({ref_w}x{ref_h})")

print("\nDone! Rendered:")
print(f"  {fname}")
print(f"  {ref_fname}")
