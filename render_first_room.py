#!/usr/bin/env python3
"""Thin wrapper: delegates to render_room.py for room 0."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_room import render_room

if __name__ == '__main__':
    render_room(0)

def stic_cs_to_rgb(word):
    """Decode STIC Color Stack / border color word to RGB."""
    idx = word & 7
    is_pastel = (word >> 3) & 1
    return PASTEL[idx + 8] if is_pastel else PRIMARY[idx]

CS_COLORS = [stic_cs_to_rgb(c) for c in STIC_CS]

# ---- Parse jzIntv memory dump ----
def parse_mem(text, base, count):
    mem = {}
    for line in text.strip().split('\n'):
        m = re.match(r'^([0-9A-F]{4}):\s*(.*)', line.strip())
        if not m: continue
        addr = int(m.group(1), 16)
        vals = re.findall(r'([0-9A-F]{4})\*?', m.group(2))
        for v in vals:
            if base <= addr < base + count:
                mem[addr] = int(v, 16)
            addr += 1
    return mem

# ---- Load data ----
with open(DUMP_PATH, 'r', encoding='utf-8', errors='replace') as f:
    raw = f.read()
with open(GROM_PATH, 'rb') as f:
    grom = f.read()

def extract_section(text, start_addr, end_addr=None):
    section = ''
    capture = False
    start_str = f'{start_addr:04X}:'
    end_str = f'{end_addr:04X}:' if end_addr else None
    for line in text.split('\n'):
        if re.match(rf'^{start_str}', line.strip()):
            section = line + '\n'; capture = True
        elif end_str and re.match(rf'^{end_str}', line.strip()):
            break
        elif capture:
            section += line + '\n'
    return section

backtab = parse_mem(extract_section(raw, 0x0200, 0x02F0), 0x0200, 240)
gram_mem = parse_mem(extract_section(raw, 0x3800, 0x3A00), 0x3800, 512)
sysram = parse_mem(extract_section(raw, 0x0300, 0x0360), 0x0300, 96)

# ---- STIC-correct BACKTAB decoding (Color Stack mode) ----
def decode_bt_cs(w):
    """
    Decode BACKTAB word per STIC Color Stack mode (stic.txt).
    Returns one of:
      - ('CS', card#, fg_color_4bit, is_gram, cs_advance) for regular cards
      - ('COLSQ', pix0, pix1, pix2, pix3) for Colored Squares cards
        (pixN are 4-bit colors 0-15; color 7=transparent showing CS top)
    """
    cs_adv = (w >> 13) & 1            # bit 13: advance color stack

    # Colored Squares detection: bit 12=1 AND bit 11=0
    if (w & 0x1800) == 0x1000:        # bit12=1, bit11=0
        pix0 = w & 7                   # bits 2-0
        pix1 = (w >> 3) & 7            # bits 5-3
        pix2 = (w >> 6) & 7            # bits 8-6
        pix3_bit2 = (w >> 13) & 1      # CS advance bit is repurposed as Pix3 bit2
        pix3_lo = (w >> 9) & 3         # bits 10-9 = Pix3 bits 0-1
        pix3 = (pix3_bit2 << 2) | pix3_lo
        return ('COLSQ', pix0, pix1, pix2, pix3, cs_adv)

    # Regular Color Stack card
    gram = bool(w & 0x0800)           # bit 11: 0=GROM, 1=GRAM

    if gram:
        # GRAM: bits 9-10 ignored per STIC spec → card = bits 8-3 only
        card = (w >> 3) & 0x3F        # 6 bits: 0-63
    else:
        # GROM: full 8-bit card number (bits 10-3), FG bit3 must be 0
        card = (w >> 3) & 0xFF        # 8 bits: 0-255

    # FG color: bit 12 (FG bit3) + bits 2-0 (FG bits 2-0)
    fg_bit3 = (w >> 12) & 1
    fg = (fg_bit3 << 3) | (w & 7)    # 4-bit color: 0-15

    return ('CS', card, fg, gram, cs_adv)

# ---- Card pixel data ----
def grom_row(card, row):
    if row >= 8:
        return 0
    return grom[(card & 0xFF) * 8 + row]

def gram_row(card, row):
    if row >= 8:
        return 0
    return gram_mem.get(0x3800 + (card & 0x3F) * 8 + row, 0) & 0xFF

# ---- Render ----
ZOOM = 8  # 8x zoom for detailed view
TILE = 8
COLS, ROWS = 20, 12

img_w, img_h = COLS * TILE * ZOOM, ROWS * TILE * ZOOM
img = Image.new('RGB', (img_w, img_h))
px = img.load()

# Track which pixels are background (for MOB behind-rendering)
is_bg_pixel = [[True] * img_w for _ in range(img_h)]

cs_ptr = 0  # color stack pointer (reset at start of each frame)

for row in range(ROWS):
    for col in range(COLS):
        addr = 0x0200 + row * 20 + col
        w = backtab.get(addr, 0x0000)
        result = decode_bt_cs(w)

        if result[0] == 'COLSQ':
            # Colored Squares card: 4 colored quadrants
            _, pix0, pix1, pix2, pix3, cs_adv = result
            cs_ptr = (cs_ptr + cs_adv) % 4
            bg_rgb = CS_COLORS[cs_ptr]  # top of color stack for color-7 squares

            # Colors 0-6: primary, interacting. Color 7: CS top, non-interacting.
            def colsq_rgb(c):
                if c == 7:
                    return bg_rgb
                return PRIMARY.get(c, (0, 0, 0))

            colors = [colsq_rgb(pix0), colsq_rgb(pix1),
                      colsq_rgb(pix2), colsq_rgb(pix3)]
            # Colored Squares layout: pix0=top-left, pix1=top-right, pix2=bottom-left, pix3=bottom-right
            half = TILE // 2  # 4
            for y in range(TILE):
                for x in range(TILE):
                    if y < half and x < half:
                        rgb = colors[0]
                        is_bg = (pix0 == 7)
                    elif y < half and x >= half:
                        rgb = colors[1]
                        is_bg = (pix1 == 7)
                    elif y >= half and x < half:
                        rgb = colors[2]
                        is_bg = (pix2 == 7)
                    else:
                        rgb = colors[3]
                        is_bg = (pix3 == 7)

                    for dy in range(ZOOM):
                        for dx in range(ZOOM):
                            pxx = col * TILE * ZOOM + x * ZOOM + dx
                            pxy = row * TILE * ZOOM + y * ZOOM + dy
                            px[pxx, pxy] = rgb
                            is_bg_pixel[pxy][pxx] = is_bg
        else:
            # Regular Color Stack card
            _, card_idx, fg_color, is_gram, cs_adv = result

            # Advance color stack BEFORE rendering this card (STIC advances immediately)
            cs_ptr = (cs_ptr + cs_adv) % 4
            bg_rgb = CS_COLORS[cs_ptr]

            # FG color: if GROM, bit3 must be 0 (only primary colors 0-7)
            if not is_gram:
                fg_color = fg_color & 7  # mask to primary only

            fg_rgb = PALETTE.get(fg_color, (0, 0, 0))
            # In CS mode, pixel bit=0 → show CS background (bg_rgb).
            # Pixel bit=1 → show FG color (even FG=0=black).
            # No special FG=0 transparent rule for regular CS cards.

            for y in range(TILE):
                byte_val = gram_row(card_idx, y) if is_gram else grom_row(card_idx, y)
                for x in range(TILE):
                    bit = (byte_val >> (7 - x)) & 1
                    if bit == 0:
                        rgb = bg_rgb
                        is_bg = True
                    else:
                        rgb = fg_rgb
                        is_bg = False

                    for dy in range(ZOOM):
                        for dx in range(ZOOM):
                            pxx = col * TILE * ZOOM + x * ZOOM + dx
                            pxy = row * TILE * ZOOM + y * ZOOM + dy
                            px[pxx, pxy] = rgb
                            is_bg_pixel[pxy][pxx] = is_bg

# ---- MOB overlays (STIC-correct, from STIC registers $0000-$0017) ----
# Parse STIC registers from the jzIntv dump
stic_regs = parse_mem(extract_section(raw, 0x0000, 0x0020), 0x0000, 32)

mobs = []
for mi in range(8):
    xw   = stic_regs.get(0x0000 + mi, 0)   # STIC X register
    yw   = stic_regs.get(0x0008 + mi, 0)   # STIC Y register
    attr = stic_regs.get(0x0010 + mi, 0)   # STIC A (attribute) register

    # STIC X register format (stic.txt):
    # bit 10 = XSIZE (0=8px, 1=16px)
    # bit 9  = VISB (1=visible)
    # bit 8  = INTR (interaction)
    # bits 7-0 = X coordinate (0-255, 0=disabled)
    x = xw & 0xFF
    xsz = (xw >> 10) & 1
    vis = (xw >> 9) & 1
    
    if x == 0 or not vis:  # X=0 disables MOB, VISB=0 hides it
        continue

    # STIC Y register format (stic.txt):
    # bit 11 = YFLIP
    # bit 10 = XFLIP
    # bit 9  = YSIZ4
    # bit 8  = YSIZ2
    # bit 7  = YRES (0=8x8, 1=8x16)
    # bits 6-0 = Y coordinate (0-127)
    y = yw & 0x7F  # 7-bit Y coordinate (per STIC spec: 0-127)
    yres = (yw >> 7) & 1
    ysiz2 = (yw >> 8) & 1
    ysiz4 = (yw >> 9) & 1
    xfl = (yw >> 10) & 1
    yfl = (yw >> 11) & 1

    # STIC A (attribute) register format:
    # bit 13 = PRIO (1=behind background)
    # bit 12 = FG bit3
    # bit 11 = GRAM/GROM (1=GRAM)
    # bits 10-3 = Card # (bits 9-10 ignored for GRAM)
    # bits 2-0 = FG color base
    is_gram_mob = (attr >> 11) & 1
    behind = (attr >> 13) & 1
    
    if is_gram_mob:
        mob_card = (attr >> 3) & 0x3F  # GRAM: bits 8-3 (6 bits, 0-63)
    else:
        mob_card = (attr >> 3) & 0xFF  # GROM: bits 10-3 (8 bits, 0-255)
    
    # MOB FG color: bit 12 (FG bit3) + bits 2-0
    mob_fg = ((attr >> 12) & 8) | (attr & 7)

    # Convert to pixel dimensions
    # Base height: 4 half-pixels (8x8 1x zoom) or 8 half-pixels (8x16 YRES)
    mob_h = 8 if yres else 4  # base in half-pixels
    if ysiz2: mob_h *= 2      # YSIZ2 doubles
    if ysiz4: mob_h *= 2      # YSIZ4 doubles again
    if yres: mob_h *= 2       # 8x16 cards are 2x taller in half-pixels
    # mob_h is now in half-pixels; convert to card-row units for rendering
    # STIC renders at half-pixel vertical resolution; we'll handle this in the render loop
    mob_w = 16 if xsz else 8  # XSIZE: 0=8px, 1=16px

    if x < 168 and y < 104:  # on-screen check
        mobs.append({
            'x': x, 'y': y, 'card': mob_card, 'w': mob_w, 'h': mob_h,
            'xfl': xfl, 'yfl': yfl, 'gram': is_gram_mob, 'behind': behind,
            'fg': mob_fg, 'yres': yres, 'mi': mi
        })

# Render MOBs (behind first, then front)
for mo in sorted(mobs, key=lambda m: m['behind']):
    c, w, h = mo['card'], mo['w'], mo['h']
    fg_rgb = PALETTE.get(mo['fg'] & 7, (255, 255, 255))
    mob_img = Image.new('RGBA', (w * ZOOM, h * ZOOM), (0, 0, 0, 0))
    mp = mob_img.load()

    # For 8x16 cards (yres=1): even card = upper half, odd card = lower half
    if mo['yres']:
        # 8x16: two consecutive cards
        for r in range(h):
            src_r = (h - 1 - r) if mo['yfl'] else r
            half_h = h // 2
            cn = (c & 0xFE) if src_r < half_h else ((c & 0xFE) + 1)
            bo = src_r % 8
            b1 = gram_row(cn, bo) if mo['gram'] else grom_row(cn, bo)
            for cx in range(w):
                src_c = (w - 1 - cx) if mo['xfl'] else cx
                bit = (b1 >> (7 - src_c)) & 1
                if bit:
                    for dy in range(ZOOM):
                        for dx in range(ZOOM):
                            mp[cx * ZOOM + dx, r * ZOOM + dy] = fg_rgb + (255,)
    else:
        for r in range(h):
            src_r = (h - 1 - r) if mo['yfl'] else r
            cn, bo = c, src_r % 8
            b1 = gram_row(cn, bo) if mo['gram'] else grom_row(cn, bo)
            b2 = 0
            if w == 16:
                rcn = (c + 1) if mo['gram'] else ((c + 1) & 0xFF)
                b2 = gram_row(rcn, bo) if mo['gram'] else grom_row(rcn, bo)
            for cx in range(w):
                src_c = (w - 1 - cx) if mo['xfl'] else cx
                bit = ((b2 >> (7 - (src_c - 8))) & 1) if cx >= 8 else ((b1 >> (7 - src_c)) & 1)
                if bit:
                    for dy in range(ZOOM):
                        for dx in range(ZOOM):
                            mp[cx * ZOOM + dx, r * ZOOM + dy] = fg_rgb + (255,)

    ox, oy = mo['x'] * ZOOM, mo['y'] * ZOOM // 2  # Y is in half-scanlines; ZOOM is pixels-per-scanline

    if mo['behind']:
        for py_ in range(mob_img.height):
            for px_ in range(mob_img.width):
                r_, g_, b_, a_ = mp[px_, py_]
                if a_ == 0: continue
                ix, iy = ox + px_, oy + py_
                if 0 <= ix < img_w and 0 <= iy < img_h and is_bg_pixel[iy][ix]:
                    px[ix, iy] = (r_, g_, b_)
    else:
        img.paste(mob_img, (ox, oy), mob_img)

# ---- Save ----
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
img.save(OUT_PATH)
print(f"Saved: {OUT_PATH} ({img_w}x{img_h})")

# ---- Diagnostic output ----
print(f"\nColor Stack: CS0={CS_COLORS[0]} CS1={CS_COLORS[1]} CS2={CS_COLORS[2]} CS3={CS_COLORS[3]}")

# BACKTAB card grid
print("\nBACKTAB card grid (card# src FG CS_adv / COLSQ colors):")
for row in range(ROWS):
    line = ""
    for col in range(COLS):
        w = backtab.get(0x0200 + row * 20 + col, 0)
        result = decode_bt_cs(w)
        if result[0] == 'COLSQ':
            _, p0, p1, p2, p3, _ = result
            line += f"Q{p0}{p1}{p2}{p3} "
        else:
            _, ci, fi, gi, cs = result
            src = "G" if gi else "g"
            fg_str = "t" if fi == 0 else str(fi)
            line += f"{ci:3d}{src}{fg_str} "
    print(f"  row{row:2d}: {line}")

# Unique BACKTAB words
unique = {}
for row in range(ROWS):
    for col in range(COLS):
        w = backtab.get(0x0200 + row * 20 + col, 0)
        unique[w] = unique.get(w, 0) + 1

print(f"\n{len(unique)} unique BACKTAB words ({sum(unique.values())} total):")
for w, cnt in sorted(unique.items(), key=lambda x: -x[1]):
    result = decode_bt_cs(w)
    if result[0] == 'COLSQ':
        _, p0, p1, p2, p3, cs = result
        print(f"  ${w:04X} x{cnt:3d}  ColoredSquares pix0={p0} pix1={p1} pix2={p2} pix3={p3} CS_adv={cs}")
    else:
        _, ci, fi, gi, cs = result
        src = "GRAM" if gi else "GROM"
        fg_name = f"FG={fi}"
        print(f"  ${w:04X} x{cnt:3d}  card={ci:3d} {src} FG={fg_name} CS_adv={cs}")

# MOB summary
print(f"\n{len(mobs)} MOBs rendered:")
for m in mobs:
    print(f"  X={m['x']:3d} Y={m['y']:3d} card={m['card']:3d} {'GRAM' if m['gram'] else 'GROM'} "
          f"{m['w']}x{m['h']} FG={m['fg']} {'behind' if m['behind'] else 'front'}")
