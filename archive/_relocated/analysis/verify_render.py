#!/usr/bin/env python3
"""
Verify render_first_room.py against jzIntv ground truth.
Uses jzIntv's dumped BACKTAB + GRAM + STIC registers to re-derive
the exact Color Stack state, then re-renders and pixel-diffs.
"""
import re, os, sys
from PIL import Image
from collections import Counter

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DUMP_PATH   = os.path.join(PROJECT_DIR, "traces", "rooms", "render_room_0_out.txt")
GROM_PATH   = os.path.join(PROJECT_DIR, "grom.bin")
OUR_PNG     = os.path.join(PROJECT_DIR, "sprites", "rooms", "first_room.png")

# --- STIC color registers from jzIntv dump ---
# 0028: 3FF0* 3FF3  3FF0  3FF0
STIC_CS = [0x3FF0, 0x3FF3, 0x3FF0, 0x3FF0]  # CS0-CS3
STIC_BORDER = 0x3FF0

# --- Palette ---
PRIMARY = [(0,0,0), (20,56,247), (227,91,14), (203,241,104),
           (0,148,40), (7,194,0), (255,255,1), (255,255,255)]
PASTEL  = [(200,200,200), (35,206,195), (253,153,24), (58,138,0),
           (240,70,60), (211,131,255), (72,246,1), (184,17,120)]

def stic_to_rgb(w):
    """Convert STIC color word to RGB tuple"""
    idx = w & 7
    is_pastel = (w >> 3) & 1
    return PASTEL[idx] if is_pastel else PRIMARY[idx]

# --- Parse jzIntv dump ---
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

# --- Load data ---
with open(DUMP_PATH, 'r', encoding='utf-8', errors='replace') as f:
    raw = f.read()
with open(GROM_PATH, 'rb') as f:
    grom = f.read()

# Extract sections
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

# --- Decode BACKTAB word ---
def decode_bt(w):
    card = w & 0x07F8
    gram = bool(w & 0x0800)
    fg   = ((w >> 13) & 6) | ((w >> 12) & 1)
    cs_adv = (w >> 13) & 1
    return card >> 3, fg, gram, cs_adv

# Card pixel data
def grom_row(card, row):
    return grom[(card & 0xFF) * 8 + row] if row < 8 else 0

def gram_row(card, row):
    return gram_mem.get(0x3800 + (card & 0x3F) * 8 + row, 0) & 0xFF

# --- Render with CORRECT Color Stack from jzIntv ---
ZOOM = 4
TILE = 8
COLS, ROWS = 20, 12

img_w, img_h = COLS * TILE * ZOOM, ROWS * TILE * ZOOM
img = Image.new('RGB', (img_w, img_h))
px = img.load()

# Color stack initialized from jzIntv STIC dump
cs_colors = [stic_to_rgb(c) for c in STIC_CS]
border_color = stic_to_rgb(STIC_BORDER)

cs_ptr = 0

for row in range(ROWS):
    for col in range(COLS):
        addr = 0x0200 + row * 20 + col
        w = backtab.get(addr, 0x1603)
        card_idx, fg_idx, is_gram, cs_adv = decode_bt(w)

        cs_ptr = (cs_ptr + cs_adv) % 4
        bg = cs_colors[cs_ptr]
        fg_rgb = PRIMARY[fg_idx] if fg_idx < 8 else (0,0,0)

        # FG=0 is transparent
        fg_trans = (fg_idx == 0)

        for y in range(TILE):
            byte_val = gram_row(card_idx, y) if is_gram else grom_row(card_idx, y)
            for x in range(TILE):
                bit = (byte_val >> (7 - x)) & 1
                is_bg_px = (bit == 0)
                if is_bg_px or fg_trans:
                    rgb = bg
                else:
                    rgb = fg_rgb
                for dy in range(ZOOM):
                    for dx in range(ZOOM):
                        pxx = col * TILE * ZOOM + x * ZOOM + dx
                        pxy = row * TILE * ZOOM + y * ZOOM + dy
                        px[pxx, pxy] = rgb

# --- Compare with our renderer's PNG ---
our_img = Image.open(OUR_PNG)

# Our image is 1280x768 (2x ZOOM), this one is 640x384 (1x ZOOM)
# Scale this one to match
jz_img = img.resize((img_w * 2, img_h * 2), Image.NEAREST)

if jz_img.size != our_img.size:
    print(f"SIZE MISMATCH: jzIntv={jz_img.size} our={our_img.size}")
    sys.exit(1)

jp = jz_img.load()
op = our_img.load()

total = jz_img.width * jz_img.height
match = 0
mismatch_pixels = []
for y in range(jz_img.height):
    for x in range(jz_img.width):
        if jp[x, y] == op[x, y]:
            match += 1
        else:
            mismatch_pixels.append((x, y, jp[x, y], op[x, y]))

pct = 100.0 * match / total

print(f"=== Pixel Comparison ===")
print(f"Total pixels: {total}")
print(f"Matching:     {match} ({pct:.2f}%)")
print(f"Mismatched:   {total - match} ({100.0-pct:.2f}%)")
print()

if pct >= 99.9:
    print("RESULT: ESSENTIALLY PERFECT MATCH (< 0.1% difference)")
elif pct >= 99.0:
    print("RESULT: VERY CLOSE MATCH (< 1% difference)")
elif pct >= 95.0:
    print("RESULT: GOOD MATCH (< 5% difference)")
else:
    print(f"RESULT: SIGNIFICANT DIFFERENCES ({100.0-pct:.2f}% mismatch)")

# Show sample mismatches
if mismatch_pixels:
    print(f"\nSample mismatches (up to 20):")
    for i, (x, y, j_rgb, o_rgb) in enumerate(mismatch_pixels[:20]):
        col = x // (TILE * ZOOM * 2)  # adjusted for 2x zoom
        row = y // (TILE * ZOOM * 2)
        bt_addr = 0x0200 + row * 20 + col
        bt_word = backtab.get(bt_addr, 0)
        print(f"  [{i}] ({x},{y}) tile({col},{row}) BT=${bt_word:04X}  "
              f"jzIntv={j_rgb}  ours={o_rgb}")

# --- Show key state differences ---
print(f"\n=== Color Stack State ===")
print(f"  jzIntv STIC dump: CS0={stic_to_rgb(STIC_CS[0])} CS1={stic_to_rgb(STIC_CS[1])} CS2={stic_to_rgb(STIC_CS[2])} CS3={stic_to_rgb(STIC_CS[3])}")
print(f"  Our renderer:     all pastel tan = {PASTEL[3]}")

# Show which BG color each cell uses
print(f"\n=== Cell-by-cell CS pointer analysis ===")
cs_ptr = 0
for row in range(ROWS):
    line = ""
    for col in range(COLS):
        addr = 0x0200 + row * 20 + col
        w = backtab.get(addr, 0x1603)
        _, fg_idx, _, cs_adv = decode_bt(w)
        cs_ptr = (cs_ptr + cs_adv) % 4
        line += f"{cs_ptr} "
    print(f"  row{row:2d}: {line}")
