"""
Render 3 distinct dungeon rooms using actual RLE tile data from ROM $61E7.
Each room uses a different layout configuration while sharing the same
genuine Swords & Serpents tile set.
"""
from PIL import Image, ImageDraw, ImageFont
import os

# ============================================================
# INTELLIVISION 16-COLOR PALETTE
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

# Color scheme (will be overridden per room)
BG       = INTV[0]   # Black
FLOOR    = INTV[3]   # Tan
WALL     = INTV[3]   # Tan
PILLAR   = INTV[3]   # Tan
PORTAL   = INTV[6]   # Yellow
DECO     = INTV[4]   # Dark Green
DARK     = INTV[8]   # Grey
ROOM_BG  = (20, 15, 5)  # Very dark brown

# Room-specific color themes
THEMES = [
    # Room 0: Classic gold/tan dungeon
    {
        'floor': INTV[3], 'wall': INTV[11], 'pillar': INTV[3],
        'portal': INTV[6], 'deco': INTV[4], 'dark': INTV[8],
        'room_bg': (25, 18, 8), 'accent': INTV[10],
    },
    # Room 1: Grey stone / silver hall
    {
        'floor': INTV[8], 'wall': INTV[11], 'pillar': INTV[8],
        'portal': INTV[13], 'deco': INTV[15], 'dark': INTV[0],
        'room_bg': (10, 12, 18), 'accent': INTV[1],
    },
    # Room 2: Dark green / olive crypt
    {
        'floor': INTV[4], 'wall': INTV[11], 'pillar': INTV[14],
        'portal': INTV[12], 'deco': INTV[2], 'dark': INTV[0],
        'room_bg': (8, 15, 5), 'accent': INTV[5],
    },
]

# Tile indices (from render_dungeon_room.py)
T_WALL_TOP       = 5
T_WALL_SIDE      = 17
T_WALL_BASE      = 19
T_WALL_BEAM      = 25
T_PILLAR_TOP     = 4
T_PILLAR_MID     = 6
T_PILLAR_MID2    = 7
T_FLOOR          = 20
T_PORTAL_TOP     = 12
T_PORTAL_BOT     = 16
T_CORNER_DECO    = 9
T_DECO_CAPITAL   = 24
T_BRICK          = 10
T_ARCH_FILL      = 18

# ============================================================
# LOAD RLE TILES FROM ROM
# ============================================================
rom = open('Swords and Serpents.bin', 'rb').read()

def read_decle(addr):
    off = (addr - 0x5000) * 2
    if off + 1 < len(rom):
        return (rom[off] << 8) | rom[off + 1]
    return None

addr = 0x61E7
count = read_decle(addr + 1)
decoded = bytearray()
for i in range(count):
    entry = read_decle(addr + 2 + i)
    if entry is None:
        break
    repeat = ((entry >> 8) & 0x03) + 1
    for _ in range(repeat):
        decoded.append(entry & 0xFF)
cards = [list(decoded[c*8:(c+1)*8]) for c in range(len(decoded)//8)]
print(f"Loaded {len(cards)} RLE cards from ROM $61E7")

# ============================================================
# DRAWING UTILITIES
# ============================================================
ZOOM = 12
TILE = 8 * ZOOM


def draw_card_raw(pixels, tile_x, tile_y, card_bytes, zoom, color, bg=None):
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
    flipped = []
    for row_byte in card_bytes:
        f = 0
        for i in range(8):
            if (row_byte >> i) & 1:
                f |= (1 << (7 - i))
        flipped.append(f)
    draw_card_raw(pixels, tile_x, tile_y, flipped, zoom, color, bg)


def draw_card_vflip(pixels, tile_x, tile_y, card_bytes, zoom, color, bg=None):
    flipped = list(reversed(card_bytes))
    draw_card_raw(pixels, tile_x, tile_y, flipped, zoom, color, bg)


def fill_tile(pixels, tile_x, tile_y, zoom, color):
    for dy in range(8 * zoom):
        for dx in range(8 * zoom):
            px, py = tile_x + dx, tile_y + dy
            if 0 <= px < len(pixels[0]) and 0 <= py < len(pixels):
                pixels[py][px] = color


def tx(c, border=2):
    return (c + border) * TILE


# ============================================================
# ROOM RENDERER
# ============================================================
class RoomLayout:
    """Describes a dungeon room layout."""
    def __init__(self, name, w, h, portal_col, portal_w,
                 pillars, floor_bricks=None, capitals=None, theme=None,
                 side_decos=None, floor_pattern=None):
        self.name = name
        self.w = w
        self.h = h
        self.portal_col = portal_col
        self.portal_w = portal_w
        self.pillars = pillars
        self.floor_bricks = floor_bricks or []
        self.capitals = capitals or []
        self.theme = theme or {}
        self.side_decos = side_decos or []  # list of (col, row) for wall decorations
        self.floor_pattern = floor_pattern or []  # list of (col, row, card_idx, color)


def render_room(layout, out_path):
    border = 2
    img_w = (layout.w + border * 2) * TILE
    img_h = (layout.h + border * 2) * TILE

    # Apply theme colors
    t = layout.theme
    floor = t.get('floor', FLOOR)
    wall = t.get('wall', WALL)
    pillar = t.get('pillar', PILLAR)
    portal = t.get('portal', PORTAL)
    deco = t.get('deco', DECO)
    dark = t.get('dark', DARK)
    room_bg = t.get('room_bg', ROOM_BG)
    accent = t.get('accent', wall)

    pixels = [[BG for _ in range(img_w)] for _ in range(img_h)]

    def _tx(c):
        return tx(c, border)

    # Room interior darkness
    for ty in range(layout.h):
        for trow in range(TILE):
            for tx_pos in range(layout.w):
                for tcol in range(TILE):
                    px = _tx(tx_pos) + tcol
                    py = _tx(ty) + trow
                    pixels[py][px] = room_bg

    # Floor
    for ty in range(3, layout.h - 2):
        for tx_pos in range(1, layout.w - 1):
            draw_card_raw(pixels, _tx(tx_pos), _tx(ty), cards[T_FLOOR], ZOOM, floor, room_bg)

    # Top wall
    for tx_pos in range(0, layout.w):
        draw_card_raw(pixels, _tx(tx_pos), _tx(1), cards[T_WALL_TOP], ZOOM, wall, room_bg)
        if 0 < tx_pos < layout.w - 1:
            draw_card_raw(pixels, _tx(tx_pos), _tx(0), cards[T_WALL_BEAM], ZOOM, wall, BG)

    # Portal
    for pc in range(layout.portal_col, layout.portal_col + layout.portal_w):
        fill_tile(pixels, _tx(pc), _tx(1), ZOOM, room_bg)
        fill_tile(pixels, _tx(pc), _tx(0), ZOOM, BG)

    # Portal arch
    for i, pc in enumerate(range(layout.portal_col, layout.portal_col + layout.portal_w)):
        if i == 0:
            draw_card_raw(pixels, _tx(pc), _tx(0), cards[T_PORTAL_TOP], ZOOM, portal, BG)
            draw_card_raw(pixels, _tx(pc), _tx(1), cards[T_PORTAL_BOT], ZOOM, portal, room_bg)
            draw_card_raw(pixels, _tx(pc), _tx(2), cards[T_ARCH_FILL], ZOOM, deco, room_bg)
            draw_card_raw(pixels, _tx(pc), _tx(3), cards[T_ARCH_FILL], ZOOM, portal, bg=None)
        else:
            draw_card_hflip(pixels, _tx(pc), _tx(0), cards[T_PORTAL_TOP], ZOOM, portal, BG)
            draw_card_hflip(pixels, _tx(pc), _tx(1), cards[T_PORTAL_BOT], ZOOM, portal, room_bg)
            draw_card_hflip(pixels, _tx(pc), _tx(2), cards[T_ARCH_FILL], ZOOM, deco, room_bg)
            draw_card_hflip(pixels, _tx(pc), _tx(3), cards[T_ARCH_FILL], ZOOM, portal, bg=None)

    # Side walls
    for ty in range(2, layout.h - 2):
        draw_card_raw(pixels, _tx(0), _tx(ty), cards[T_WALL_SIDE], ZOOM, wall, room_bg)
        draw_card_hflip(pixels, _tx(layout.w - 1), _tx(ty), cards[T_WALL_SIDE], ZOOM, wall, room_bg)

    # Bottom wall
    for tx_pos in range(0, layout.w):
        draw_card_raw(pixels, _tx(tx_pos), _tx(layout.h - 2), cards[T_WALL_TOP], ZOOM, wall, room_bg)
        draw_card_raw(pixels, _tx(tx_pos), _tx(layout.h - 1), cards[T_WALL_BASE], ZOOM, wall, room_bg)

    # Corner decorations
    draw_card_raw(pixels, _tx(0), _tx(0), cards[T_CORNER_DECO], ZOOM, deco, BG)
    draw_card_hflip(pixels, _tx(layout.w - 1), _tx(0), cards[T_CORNER_DECO], ZOOM, deco, BG)

    # Capitals
    for cap_x in layout.capitals:
        if 0 <= cap_x < layout.w - 1:
            draw_card_raw(pixels, _tx(cap_x), _tx(0), cards[T_DECO_CAPITAL], ZOOM, deco, BG)

    # Side wall decorations
    for sx, sy in layout.side_decos:
        if 0 < sy < layout.h - 2:
            draw_card_raw(pixels, _tx(sx), _tx(sy), cards[T_CORNER_DECO], ZOOM, deco, room_bg)

    # Pillars
    for col, start_row, height in layout.pillars:
        if 0 <= col < layout.w and 2 <= start_row < layout.h - 1:
            draw_card_raw(pixels, _tx(col), _tx(start_row), cards[T_PILLAR_TOP], ZOOM, pillar, room_bg)
            for r in range(height):
                draw_card_raw(pixels, _tx(col), _tx(start_row + 1 + r), cards[T_PILLAR_MID], ZOOM, pillar, room_bg)
            # Pillar base (vflip of top cap)
            base_row = start_row + 1 + height
            if base_row < layout.h - 2:
                draw_card_vflip(pixels, _tx(col), _tx(base_row), cards[T_PILLAR_TOP], ZOOM, pillar, bg=None)
            # Shadow under pillar base
            shadow_row = base_row + 1
            if shadow_row < layout.h - 2:
                for dx in [-1, 0, 1]:
                    sc = col + dx
                    if 1 <= sc < layout.w - 1:
                        draw_card_raw(pixels, _tx(sc), _tx(shadow_row), cards[T_FLOOR], ZOOM, dark, bg=None)

    # Floor brick accents
    for bx, by in layout.floor_bricks:
        if 1 <= bx < layout.w - 1 and 3 <= by < layout.h - 2:
            draw_card_raw(pixels, _tx(bx), _tx(by), cards[T_BRICK], ZOOM, accent, room_bg)

    # Custom floor patterns
    for fx, fy, fcard, fcolor in layout.floor_pattern:
        if 1 <= fx < layout.w - 1 and 3 <= fy < layout.h - 2:
            draw_card_raw(pixels, _tx(fx), _tx(fy), cards[fcard], ZOOM, fcolor, room_bg)

    # Convert to image
    img = Image.new('RGB', (img_w, img_h))
    pix = img.load()
    for y in range(img_h):
        for x in range(img_w):
            pix[x, y] = pixels[y][x]

    img.save(out_path)
    print(f"  Saved {out_path} ({img_w}x{img_h})")
    return img


# ============================================================
# DEFINE 3 DISTINCT ROOMS
# ============================================================
ROOMS = [
    # Room 0: Classic symmetrical gold/tan dungeon
    RoomLayout(
        name="Room 0 — Throne Portal",
        w=16, h=12,
        portal_col=6, portal_w=2,
        pillars=[
            (2, 3, 5),   # left tall
            (2, 8, 1),   # left short
            (13, 3, 5),  # right tall
            (13, 9, 1),  # right short
            (5, 4, 3),   # center-left
            (10, 4, 3),  # center-right
            (7, 7, 2),   # mid-left
            (9, 8, 2),   # mid-right
        ],
        floor_bricks=[(6, 6), (7, 6), (8, 6), (9, 6)],
        capitals=[3, 12],
        theme=THEMES[0],
    ),

    # Room 1: Grey stone / silver hall with wide central aisle
    RoomLayout(
        name="Room 1 — Hall of Pillars",
        w=16, h=12,
        portal_col=3, portal_w=2,
        pillars=[
            (2, 4, 4),   # left cluster
            (2, 8, 2),
            (5, 3, 6),   # center tall
            (10, 3, 6),  # center tall
            (13, 4, 4),  # right cluster
            (13, 8, 2),
            (7, 8, 2),   # bottom row
            (8, 8, 2),
        ],
        floor_bricks=[(6, 5), (7, 5), (8, 5), (9, 5), (6, 7), (7, 7), (8, 7), (9, 7)],
        capitals=[3, 12],
        theme=THEMES[1],
        side_decos=[(0, 5), (0, 8), (15, 5), (15, 8)],
        floor_pattern=[(4, 4, T_ARCH_FILL, INTV[1]), (11, 4, T_ARCH_FILL, INTV[1])],
    ),

    # Room 2: Dark green / olive crypt with asymmetric layout
    RoomLayout(
        name="Room 2 — Crypt Chamber",
        w=16, h=12,
        portal_col=10, portal_w=2,
        pillars=[
            (2, 3, 4),   # left
            (2, 7, 3),
            (5, 4, 3),   # center-left
            (7, 6, 2),   # center
            (12, 3, 5),  # right tall
            (12, 8, 2),  # right short
            (14, 5, 3),  # far right
        ],
        floor_bricks=[(4, 6), (5, 6), (8, 5), (9, 5), (10, 8)],
        capitals=[3, 7, 12],
        theme=THEMES[2],
        side_decos=[(0, 4), (0, 7), (15, 4), (15, 9)],
        floor_pattern=[(3, 5, T_ARCH_FILL, INTV[12]), (8, 7, T_ARCH_FILL, INTV[12])],
    ),
]


# ============================================================
# MAIN
# ============================================================
def main():
    out_dir = 'sprites/rooms'
    os.makedirs(out_dir, exist_ok=True)

    rendered = []
    for idx, layout in enumerate(ROOMS):
        print(f"\nRendering {layout.name}...")
        path = os.path.join(out_dir, f'dungeon_room_{idx}.png')
        img = render_room(layout, path)
        rendered.append((layout.name, path, img))

    # Build montage
    print("\nBuilding montage...")
    montage_w = sum(img.width for _, _, img in rendered) + 40
    montage_h = max(img.height for _, _, img in rendered) + 80
    montage = Image.new('RGB', (montage_w, montage_h), (7, 8, 12))
    draw = ImageDraw.Draw(montage)

    # Try to load a font
    font = None
    for fp in ["C:\\Windows\\Fonts\\segoeui.ttf",
               "C:\\Windows\\Fonts\\arial.ttf"]:
        if os.path.exists(fp):
            try:
                font = ImageFont.truetype(fp, 20)
                break
            except Exception:
                continue
    if font is None:
        font = ImageFont.load_default()

    x = 20
    for name, path, img in rendered:
        # Label
        draw.text((x + 4, 10), name, fill=(242, 215, 164), font=font)
        # Image
        montage.paste(img, (x, 50))
        x += img.width + 20

    montage_path = os.path.join(out_dir, 'dungeon_montage.png')
    montage.save(montage_path)
    print(f"\nSaved montage: {montage_path} ({montage_w}x{montage_h})")

    # Print summary
    print("\n" + "=" * 60)
    print("  RENDER SUMMARY")
    print("=" * 60)
    for name, path, img in rendered:
        colors = set()
        px = img.load()
        for y in range(img.height):
            for x in range(img.width):
                colors.add(px[x, y])
        print(f"  {os.path.basename(path)}: {img.size}  {len(colors)} colors")
    print(f"  Montage: {montage_path}")


if __name__ == '__main__':
    main()
