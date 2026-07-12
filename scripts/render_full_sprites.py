"""
Swords & Serpents — Full-Length Sprite Sheet Renderer
======================================================
Extracts ALL character sprite cards from ROM and renders comprehensive PNG
sprite sheets organized by class with all animation frames.

Data sources:
  - Direct ROM cards at $62DE-$6317 (warrior & wizard head/side frames)
  - RLE-compressed data at $61E7 (feet card + title screen decorations)
  - Animation frame variants (warrior head has 2 frames)

Sprite composition (Intellivision MOB 8x16 double-height):
  - Top card: head/body (8x8)
  - Bottom card: feet (8x8)
  - Orientation: facing-right side view (walk frame)
"""

import re
import os
import sys
from PIL import Image, ImageDraw, ImageFont

# ── ROM Setup ───────────────────────────────────────────────
ROM_PATH = "Swords and Serpents.bin"
try:
    with open(ROM_PATH, "rb") as f:
        rom = f.read()
except FileNotFoundError:
    print(f"ERROR: ROM file '{ROM_PATH}' not found in current directory.")
    print("Please run this script from the project root (Swords and Serpents/).")
    sys.exit(1)

def rom_bytes(addr, count):
    """Read count bytes from ROM at logical address (lo bytes of DECLE words)."""
    off = (addr - 0x5000) * 2
    return [rom[off + 2*i + 1] if off + 2*i + 1 < len(rom) else 0 for i in range(count)]

def rom_decile(addr):
    """Read a full 16-bit DECLE word from ROM."""
    off = (addr - 0x5000) * 2
    if off + 1 < len(rom):
        return (rom[off] << 8) | rom[off + 1]
    return 0

# ── RLE Decompressor (L_53EA algorithm) ────────────────────
def rle_decode(addr):
    """Decode RLE-compressed sprite data.
    Word 0: GRAM byte offset, Word 1: entry count
    Each entry: lo byte = pixel value, bits 8-9 = repeat count (0-3 -> 1-4)"""
    gram_off = rom_decile(addr)
    count = rom_decile(addr + 1)
    result = []
    for i in range(count):
        entry = rom_decile(addr + 2 + i)
        byte_val = entry & 0xFF
        repeat = ((entry >> 8) & 0x03) + 1
        result.extend([byte_val] * repeat)
    return gram_off, result

# ── Palettes ────────────────────────────────────────────────
BG = (0, 0, 0, 0)

class Palette:
    """1bpp palette: index 0 = transparent, index 1 = foreground color."""
    def __init__(self, name, fg_color):
        self.name = name
        self.fg = fg_color
        self.colors = [BG, fg_color]
    
    def get(self, pixel):
        return self.colors[pixel]

PAL_WARRIOR = Palette("Warrior (White Knight)", (235, 230, 220, 255))
PAL_WIZARD  = Palette("Wizard (Blue Robe)",   (60, 100, 210, 255))
PAL_REF     = Palette("Reference (Orange)",   (255, 180, 80, 255))

# ── Card Rendering ─────────────────────────────────────────
ZOOM = 12  # pixels per source pixel
CARD_W = 8 * ZOOM
CARD_H = 8 * ZOOM

def card_pixels(data):
    """Convert 8 bytes -> 8x8 pixel array (0=bg, 1=fg). MSB = leftmost pixel."""
    rows = []
    for i in range(8):
        b = data[i] if i < len(data) else 0
        rows.append([(b >> (7 - col)) & 1 for col in range(8)])
    return rows

def card_image_8x8(data, palette):
    """Render a single 8x8 card as PIL Image at zoom scale."""
    px = card_pixels(data)
    raw = Image.new("RGBA", (8, 8))
    for y in range(8):
        for x in range(8):
            raw.putpixel((x, y), palette.get(px[y][x]))
    if ZOOM > 1:
        return raw.resize((CARD_W, CARD_H), Image.NEAREST)
    return raw

def sprite_image_8x16(top_data, bot_data, palette):
    """Compose an 8x16 sprite from top card (head/body) and bottom card (feet)."""
    img = Image.new("RGBA", (CARD_W, CARD_H * 2))
    top_img = card_image_8x8(top_data, palette)
    bot_img = card_image_8x8(bot_data, palette)
    img.paste(top_img, (0, 0))
    img.paste(bot_img, (0, CARD_H))
    return img

def ascii_card(data):
    """Render card as ASCII art."""
    chars = {0: ".", 1: "#"}
    px = card_pixels(data)
    return "\n".join("".join(chars[p] for p in row) for row in px)

def data_hex(data):
    return " ".join(f"{b:02X}" for b in data)

# ── Load GRAM dump for verification ────────────────────────
def load_gram(path):
    """Load GRAM dump from clean format: '3800: F0 F0 70 20 ...'"""
    gram = {}
    try:
        with open(path) as f:
            content = f.read()
    except FileNotFoundError:
        return gram
    
    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([0-9A-F]{4}):\s+((?:[0-9A-F]{2}\s*)+)", line, re.I)
        if m:
            addr = int(m.group(1), 16)
            byte_vals = [int(b, 16) for b in m.group(2).split()]
            for i, v in enumerate(byte_vals):
                if addr + i < 0x3A00:
                    gram[addr + i] = v
    return gram

gram = load_gram("traces/title_gram_dump.txt")

# ── Sprite Data ─────────────────────────────────────────────

# RLE block at $61E7: decompresses to 248 bytes = 31 cards (GRAM cards 3-33)
rle_gram_off, rle_bytes = rle_decode(0x61E7)
rle_cards = [rle_bytes[i*8:(i+1)*8] for i in range(len(rle_bytes) // 8)]
FEET_CARD = rle_cards[0]  # GRAM card 3: warrior/wizard feet [F0 F8 E8 78 F0 F8 F8 F8]

# === WARRIOR (White Knight) ===
# Verified against jzintv title screen GRAM
WARRIOR = {
    "name": "Warrior",
    "palette": PAL_WARRIOR,
    "head_frames": [
        ("$62DE (frame 1)", rom_bytes(0x62DE, 8)),   # F0 F0 70 20 20 00 00 00 ✓
        ("$62E6 (frame 2)", rom_bytes(0x62E6, 8)),   # F0 F0 F0 70 70 20 A0 A0
    ],
    "side_frames": [
        ("$6300 (walk)",    rom_bytes(0x6300, 8)),   # 00 00 80 80 D0 D0 F0 F0 ✓
    ],
    "feet": ("RLE $61E7", FEET_CARD),
    "verified": True,
}

# === WIZARD (Blue Robe) ===
# ROM-inferred — not verified against gameplay GRAM
WIZARD = {
    "name": "Wizard",
    "palette": PAL_WIZARD,
    "head_frames": [
        ("$6302 (frame 1)", rom_bytes(0x6302, 8)),   # 80 80 D0 D0 F0 F0 A0 A0
    ],
    "side_frames": [
        ("$630A (walk)",    rom_bytes(0x630A, 8)),   # 80 D0 D0 F0 F0 F0 00 00
    ],
    "feet": ("RLE $61E7 (shared)", FEET_CARD),
    "verified": False,
}

CLASSES = [WARRIOR, WIZARD]

# ── Load GRAM for comparison ───────────────────────────────
warrior_gram_cards = {}
for card_num in [1, 2, 3]:
    base = 0x3800 + card_num * 8
    warrior_gram_cards[card_num] = [gram.get(base + i, 0) for i in range(8)]

# ── Helper: labeled strip of cards ─────────────────────────
try:
    LABEL_FONT = ImageFont.truetype("arial.ttf", 11)
    TITLE_FONT = ImageFont.truetype("arial.ttf", 14)
    SMALL_FONT = ImageFont.truetype("arial.ttf", 9)
except Exception:
    LABEL_FONT = ImageFont.load_default()
    TITLE_FONT = LABEL_FONT
    SMALL_FONT = LABEL_FONT

def draw_label(draw, x, y, text, color=(220, 220, 220, 255), font=None):
    if font is None:
        font = LABEL_FONT
    # Draw shadow then text
    draw.text((x + 1, y + 1), text, fill=(0, 0, 0, 180), font=font)
    draw.text((x, y), text, fill=color, font=font)

def make_labeled_card_strip(cards_with_labels, palette, bg=(18, 18, 28, 255)):
    """Create a horizontal strip of labeled cards."""
    n = len(cards_with_labels)
    gap = 16
    padding = 16
    strip_w = n * (CARD_W + gap) + padding * 2
    strip_h = CARD_H + 48
    img = Image.new("RGBA", (strip_w, strip_h), bg)
    draw = ImageDraw.Draw(img)
    for i, (label, data) in enumerate(cards_with_labels):
        x = padding + i * (CARD_W + gap)
        ci = card_image_8x8(data, palette)
        img.paste(ci, (x, 8), ci)
        draw_label(draw, x + 2, CARD_H + 14, label, font=SMALL_FONT)
    return img

# ═══════════════════════════════════════════════════════════
#  MAIN OUTPUT
# ═══════════════════════════════════════════════════════════

os.makedirs("sprites", exist_ok=True)

H1 = "=" * 70
H2 = "-" * 70

print(H1)
print("  SWORDS & SERPENTS -- FULL-LENGTH SPRITE SHEETS")
print(H1)

# -- 1. Individual 8x8 cards per class --
print("\n-- ALL 8x8 CARDS BY CLASS --")

for cls in CLASSES:
    all_cards = []
    
    print(f"\n  {cls['name']} ({'VERIFIED' if cls['verified'] else 'ROM-INFERRED'}):")
    
    for label, data in cls["head_frames"]:
        print(f"    Head {label}: {data_hex(data)}")
        all_cards.append((f"HEAD\n{label}", data))
    
    for label, data in cls["side_frames"]:
        print(f"    Side {label}: {data_hex(data)}")
        all_cards.append((f"SIDE\n{label}", data))
    
    feet_label, feet_data = cls["feet"]
    print(f"    Feet {feet_label}: {data_hex(feet_data)}")
    all_cards.append((f"FEET\n{feet_label}", feet_data))
    
    # Render strip
    strip = make_labeled_card_strip(all_cards, cls["palette"])
    fname = f"sprites/full_{cls['name'].lower()}_cards.png"
    strip.save(fname)
    print(f"    -> Saved {fname}")

# -- 2. Composed 8x16 sprites (head + feet per frame) --
print("\n-- COMPOSED 8x16 SPRITES (head + feet) --")

for cls in CLASSES:
    sprites = []
    
    print(f"\n  {cls['name']} ({'VERIFIED' if cls['verified'] else 'ROM-INFERRED'}):")
    
    for label, head_data in cls["head_frames"]:
        feet_label, feet_data = cls["feet"]
        sprite = sprite_image_8x16(head_data, feet_data, cls["palette"])
        sprites.append((f"FRAME: {label}\n+ {feet_label}", head_data, feet_data))
        print(f"    8x16 sprite: {label} head + {feet_label} feet")
    
    for label, side_data in cls["side_frames"]:
        feet_label, feet_data = cls["feet"]
        sprite = sprite_image_8x16(side_data, feet_data, cls["palette"])
        sprites.append((f"WALK: {label}\n+ {feet_label}", side_data, feet_data))
        print(f"    8x16 sprite: {label} side + {feet_label} feet")
    
    # Render composed sprites as labeled strip
    n = len(sprites)
    gap = 24
    padding = 20
    strip_w = n * (CARD_W + gap) + padding * 2
    strip_h = CARD_H * 2 + 52
    
    sheet = Image.new("RGBA", (strip_w, strip_h), (18, 18, 28, 255))
    draw = ImageDraw.Draw(sheet)
    
    draw_label(draw, 8, 6, f"{cls['name']} — 8×16 Sprites",
               color=cls["palette"].fg[:3] + (200,), font=TITLE_FONT)
    
    for i, (label, head_data, feet_data) in enumerate(sprites):
        x = padding + i * (CARD_W + gap)
        sprite_img = sprite_image_8x16(head_data, feet_data, cls["palette"])
        sheet.paste(sprite_img, (x, 28), sprite_img)
        
        # Label each frame
        short_label = label.split("\n")[0]
        draw_label(draw, x + 2, CARD_H * 2 + 34, short_label,
                   color=(200, 200, 200, 255), font=SMALL_FONT)
    
    fname = f"sprites/full_{cls['name'].lower()}_8x16_sprites.png"
    sheet.save(fname)
    print(f"    -> Saved {fname}")

# -- 3. Full comparison sheet --
print("\n-- COMPARISON SHEET (warrior vs wizard all frames) --")

# Layout: 2 rows (warrior, wizard) × cols frames
all_sprites_data = []
for cls in CLASSES:
    frames = []
    for label, head_data in cls["head_frames"]:
        frames.append((f"{cls['name']}\nHead {label.split('(')[0].strip()}", head_data, cls["palette"]))
    for label, side_data in cls["side_frames"]:
        frames.append((f"{cls['name']}\nSide {label.split('(')[0].strip()}", side_data, cls["palette"]))
    all_sprites_data.append(frames)

max_frames = max(len(f) for f in all_sprites_data)
cols = max_frames
rows = len(CLASSES)

gap = 20
padding = 24
comp_w = cols * (CARD_W + gap) + padding * 2
comp_h = rows * (CARD_H + 50) + padding * 2 + 10

comp = Image.new("RGBA", (comp_w, comp_h), (15, 15, 25, 255))
draw = ImageDraw.Draw(comp)

draw_label(draw, padding, 8, "SPRITE CARD COMPARISON",
           color=(255, 220, 150, 255), font=TITLE_FONT)

for ri, frames in enumerate(all_sprites_data):
    y = padding + 30 + ri * (CARD_H + 50)
    
    # Class label
    cls_name = CLASSES[ri]["name"]
    status = "[VERIFIED]" if CLASSES[ri]["verified"] else "[ROM-inferred]"
    draw_label(draw, padding, y - 18, f"{cls_name} {status}",
               color=CLASSES[ri]["palette"].fg[:3] + (220,), font=LABEL_FONT)
    
    for ci, (label, data, pal) in enumerate(frames):
        x = padding + ci * (CARD_W + gap)
        ci_img = card_image_8x8(data, pal)
        comp.paste(ci_img, (x, y), ci_img)
        
        short = label.split("\n")[1] if "\n" in label else label
        draw_label(draw, x + 2, y + CARD_H + 4, short,
                   color=(200, 200, 200, 255), font=SMALL_FONT)

comp.save("sprites/full_comparison.png")
print("    -> Saved sprites/full_comparison.png")

# -- 4. Animation sequence sheet --
print("\n-- ANIMATION SEQUENCE SHEET --")

# Show warrior: head frame 1 -> head frame 2 -> feet
# Show wizard: head frame 1 -> feet
# For each, render 8x16 composed sprites side by side

for cls in CLASSES:
    frames = []
    
    # Full 8x16 sprites (head + feet)
    for label, head_data in cls["head_frames"]:
        _, feet_data = cls["feet"]
        frames.append((f"Frame\n{label.split('(')[0].strip()}", 
                       sprite_image_8x16(head_data, feet_data, cls["palette"])))
    
    for label, side_data in cls["side_frames"]:
        _, feet_data = cls["feet"]
        frames.append((f"Walk\n{label.split('(')[0].strip()}",
                       sprite_image_8x16(side_data, feet_data, cls["palette"])))
    
    n = len(frames)
    gap = 16
    padding = 20
    sheet_w = n * (CARD_W + gap) + padding * 2
    sheet_h = CARD_H * 2 + 60
    
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (18, 18, 28, 255))
    draw = ImageDraw.Draw(sheet)
    
    status = "[GRAM-VERIFIED]" if cls["verified"] else "[ROM-inferred]"
    draw_label(draw, padding, 6, f"{cls['name']} Animation Frames {status}",
               color=cls["palette"].fg[:3] + (220,), font=TITLE_FONT)
    
    for i, (label, sprite) in enumerate(frames):
        x = padding + i * (CARD_W + gap)
        sheet.paste(sprite, (x, 28), sprite)
        draw_label(draw, x + 2, CARD_H * 2 + 34, label,
                   color=(200, 200, 200, 255), font=SMALL_FONT)
    
    fname = f"sprites/full_{cls['name'].lower()}_animation.png"
    sheet.save(fname)
    print(f"    -> Saved {fname}")

# -- 5. RLE cards reference sheet --
print("\n-- RLE-DECODED CARDS (from $61E7) --")
print(f"  GRAM offset: ${rle_gram_off:04X} (card {rle_gram_off//8})")
print(f"  Total: {len(rle_cards)} cards (GRAM cards {rle_gram_off//8}-{rle_gram_off//8 + len(rle_cards) - 1})")

cols = 8
rows = (len(rle_cards) + cols - 1) // cols
gap = 6
padding = 16
grid_w = cols * (CARD_W + gap) + padding * 2
grid_h = rows * (CARD_H + gap + 14) + padding * 2 + 20

grid = Image.new("RGBA", (grid_w, grid_h), (18, 18, 28, 255))
draw = ImageDraw.Draw(grid)

draw_label(draw, padding, 4, f"RLE Sprite Data — ROM ${0x61E7:04X} ({len(rle_cards)} cards, GRAM {rle_gram_off//8}-{rle_gram_off//8 + len(rle_cards) - 1})",
           color=(255, 220, 150, 255), font=TITLE_FONT)

for i, data in enumerate(rle_cards):
    col = i % cols
    row = i // cols
    x = padding + col * (CARD_W + gap)
    y = padding + 24 + row * (CARD_H + gap + 14)
    
    ci = card_image_8x8(data, PAL_REF)
    grid.paste(ci, (x, y), ci)
    
    card_num = rle_gram_off // 8 + i
    marker = ""
    if i == 0:
        marker = " (FEET)"
    draw_label(draw, x + 2, y + CARD_H + 2, f"#{card_num}{marker}",
               color=(200, 200, 200, 255), font=SMALL_FONT)

grid.save("sprites/full_rle_cards.png")
print(f"    -> Saved sprites/full_rle_cards.png")

# -- 6. All-sprite-hero image: big comprehensive sheet --
print("\n-- COMPREHENSIVE MASTER SHEET --")

# Combine everything into one tall image
sections = []

for cls in CLASSES:
    frames = []
    for label, head_data in cls["head_frames"]:
        _, feet_data = cls["feet"]
        frames.append(("HEAD " + label, sprite_image_8x16(head_data, feet_data, cls["palette"])))
    for label, side_data in cls["side_frames"]:
        _, feet_data = cls["feet"]
        frames.append(("SIDE " + label, sprite_image_8x16(side_data, feet_data, cls["palette"])))
    
    sections.append((cls, frames))

max_frames_section = max(len(f) for _, f in sections)
sheet_cols = max_frames_section
sheet_gap = 20
sheet_pad = 24

section_h = CARD_H * 2 + 60
title_h = 30
total_h = title_h + len(sections) * section_h + 20

sheet_w = sheet_cols * (CARD_W + sheet_gap) + sheet_pad * 2

master = Image.new("RGBA", (sheet_w, total_h), (15, 15, 25, 255))
draw = ImageDraw.Draw(master)

draw_label(draw, sheet_pad, 6, "SWORDS & SERPENTS — Full-Length Sprite Sheets",
           color=(255, 220, 150, 255), font=TITLE_FONT)

for si, (cls, frames) in enumerate(sections):
    y = title_h + si * section_h
    
    status = "GRAM-VERIFIED" if cls["verified"] else "ROM-INFERRED"
    draw_label(draw, sheet_pad, y, f"> {cls['name']} [{status}]",
               color=cls["palette"].fg[:3] + (220,), font=LABEL_FONT)
    
    for fi, (label, sprite) in enumerate(frames):
        x = sheet_pad + fi * (CARD_W + sheet_gap)
        master.paste(sprite, (x, y + 20), sprite)
        draw_label(draw, x + 2, y + CARD_H * 2 + 24, label, font=SMALL_FONT)

master.save("sprites/full_master_sheet.png")
print("    -> Saved sprites/full_master_sheet.png")

# -- 7. Title screen GRAM verification sheet --
print("\n-- GRAM VERIFICATION --")

if gram:
    # Show warrior cards side by side with ROM
    gram_cards = []
    for card_num in [1, 2, 3]:
        base = 0x3800 + card_num * 8
        data = [gram.get(base + i, 0) for i in range(8)]
        gram_cards.append((f"GRAM\nCard {card_num}", data, PAL_REF))
    
    # ROM cards (verified warrior)
    rom_cards_verify = [
        ("ROM\n$62DE", rom_bytes(0x62DE, 8), PAL_WARRIOR),
        ("ROM\n$6300", rom_bytes(0x6300, 8), PAL_WARRIOR),
        ("RLE\nFeet", FEET_CARD, PAL_WARRIOR),
    ]
    
    n = len(gram_cards)
    gap = 12
    pad = 16
    v_w = n * 2 * (CARD_W + gap) + pad * 2 + 40
    v_h = CARD_H + 80
    
    verify_img = Image.new("RGBA", (v_w, v_h), (18, 18, 28, 255))
    draw = ImageDraw.Draw(verify_img)
    
    draw_label(draw, pad, 6, "GRAM vs ROM Verification",
               color=(255, 220, 150, 255), font=TITLE_FONT)
    
    for i in range(n):
        x1 = pad + i * (CARD_W + gap) * 2
        x2 = x1 + CARD_W + gap
        
        # GRAM card
        ci = card_image_8x8(gram_cards[i][1], gram_cards[i][2])
        verify_img.paste(ci, (x1, 28), ci)
        draw_label(draw, x1 + 2, CARD_H + 32, gram_cards[i][0], font=SMALL_FONT)
        
        # ROM card
        ci = card_image_8x8(rom_cards_verify[i][1], rom_cards_verify[i][2])
        verify_img.paste(ci, (x2, 28), ci)
        draw_label(draw, x2 + 2, CARD_H + 32, rom_cards_verify[i][0], font=SMALL_FONT)
        
        # Match indicator
        match = rom_cards_verify[i][1] == gram_cards[i][1]
        indicator = "[MATCH]" if match else "[DIFF]"
        color = (100, 255, 100, 255) if match else (255, 100, 100, 255)
        draw_label(draw, x1 + CARD_W // 2 - 10, CARD_H + 50, indicator,
                   color=color, font=SMALL_FONT)
    
    verify_img.save("sprites/full_gram_verification.png")
    print("    -> Saved sprites/full_gram_verification.png")
    
    # Byte-level verification
    print("\n  Byte-perfect verification:")
    rom_refs = [rom_bytes(0x62DE, 8), rom_bytes(0x6300, 8), FEET_CARD]
    gram_refs = [gram_cards[i][1] for i in range(3)]
    all_ok = True
    for i in range(3):
        match = rom_refs[i] == gram_refs[i]
        status = "[OK]" if match else "[DIFF]"
        print(f"    Card {i}: ROM == GRAM? {status} {match}")
        if not match:
            all_ok = False
            for j in range(8):
                if rom_refs[i][j] != gram_refs[i][j]:
                    print(f"      Byte[{j}]: ROM={rom_refs[i][j]:02X}  GRAM={gram_refs[i][j]:02X}")
    if all_ok:
        print("    ALL WARRIOR CARDS VERIFIED [OK]")
else:
    print("  (No GRAM dump — verification skipped)")

# -- Summary --
print("\n" + H1)
print("  SPRITE SHEETS RENDERED:")
print(H1)
print(f"  sprites/full_warrior_cards.png        — Warrior 8×8 cards")
print(f"  sprites/full_wizard_cards.png         — Wizard 8×8 cards")
print(f"  sprites/full_warrior_8x16_sprites.png — Warrior composed 8×16")
print(f"  sprites/full_wizard_8x16_sprites.png  — Wizard composed 8×16")
print(f"  sprites/full_warrior_animation.png    — Warrior animation frames")
print(f"  sprites/full_wizard_animation.png     — Wizard animation frames")
print(f"  sprites/full_comparison.png           — Side-by-side comparison")
print(f"  sprites/full_rle_cards.png            — RLE-decoded cards ({len(rle_cards)} cards)")
print(f"  sprites/full_gram_verification.png    — GRAM verification")
print(f"  sprites/full_master_sheet.png         — Comprehensive master sheet")
print()
print("  Done!")
