#!/usr/bin/env python3
"""
Pixel-level validation: decode BACKTAB independently and verify against
the STIC Color Stack spec.  Reports per-tile color statistics and any
discrepancies between the renderer and a reference decode.
"""
import re, os, sys
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DUMP_PATH = os.path.join(PROJECT_DIR, "traces", "rooms", "render_room_0_out.txt")
GROM_PATH = os.path.join(PROJECT_DIR, "grom.bin")
PNG_PATH  = os.path.join(PROJECT_DIR, "sprites", "rooms", "first_room.png")

# ---- Palette ----
PRIMARY = {0:(0,0,0),1:(20,56,247),2:(227,91,14),3:(203,241,104),
           4:(0,148,40),5:(7,194,0),6:(255,255,1),7:(255,255,255)}
PASTEL  = {8:(200,200,200),9:(35,206,195),10:(253,153,24),11:(58,138,0),
           12:(240,70,60),13:(211,131,255),14:(72,246,1),15:(184,17,120)}
PAL = {**PRIMARY, **PASTEL}
CS_REGS = [0x3FF0, 0x3FF3, 0x3FF0, 0x3FF0]

def cs_rgb(word):
    idx = word & 7
    return PASTEL[idx+8] if (word>>3)&1 else PRIMARY[idx]

CS_COLORS = [cs_rgb(c) for c in CS_REGS]

# ---- Parse ----
def parse_mem(text, base, count):
    mem = {}
    for line in text.strip().split('\n'):
        m = re.match(r'^([0-9A-F]{4}):\s*(.*)', line.strip())
        if not m: continue
        addr = int(m.group(1),16)
        for v in re.findall(r'([0-9A-F]{4})\*?', m.group(2)):
            if base <= addr < base+count:
                mem[addr] = int(v,16)
            addr += 1
    return mem

def extract_section(text, start_addr, end_addr=None):
    section, capture = '', False
    s0 = f'{start_addr:04X}:'
    s1 = f'{end_addr:04X}:' if end_addr else None
    for line in text.split('\n'):
        if re.match(rf'^{s0}', line.strip()):
            section = line+'\n'; capture = True
        elif s1 and re.match(rf'^{s1}', line.strip()):
            break
        elif capture:
            section += line+'\n'
    return section

with open(DUMP_PATH, 'r', encoding='utf-8', errors='replace') as f:
    raw = f.read()
with open(GROM_PATH, 'rb') as f:
    grom = f.read()

backtab = parse_mem(extract_section(raw, 0x0200, 0x02F0), 0x0200, 240)
gram_mem = parse_mem(extract_section(raw, 0x3800, 0x3A00), 0x3800, 512)

def grom_row(card, row):
    return grom[(card&0xFF)*8+row] if row<8 else 0
def gram_row(card, row):
    return gram_mem.get(0x3800+(card&0x3F)*8+row, 0)&0xFF if row<8 else 0

# ---- STIC-correct BACKTAB decoding ----
def decode_bt(w):
    cs_adv = (w>>13)&1
    if (w&0x1800)==0x1000:  # Colored Squares
        p0 = w&7
        p1 = (w>>3)&7
        p2 = (w>>6)&7
        p3 = ((w>>13)&1)<<2 | ((w>>9)&3)
        return ('COLSQ', p0, p1, p2, p3, cs_adv)
    gram = bool(w&0x0800)
    card = ((w>>3)&0x3F) if gram else ((w>>3)&0xFF)
    fg_bit3 = (w >> 12) & 1
    fg = (fg_bit3 << 3) | (w & 7)
    if not gram: fg &= 7
    return ('CS', card, fg, gram, cs_adv)

# ---- Reference rendering (independent decode) ----
ZOOM = 4  # smaller for speed
TILE = 8
COLS, ROWS = 20, 12

ref = Image.new('RGB', (COLS*TILE*ZOOM, ROWS*TILE*ZOOM))
rpx = ref.load()
cs_ptr = 0

for row in range(ROWS):
    for col in range(COLS):
        w = backtab.get(0x0200+row*20+col, 0)
        res = decode_bt(w)
        if res[0] == 'COLSQ':
            _, p0,p1,p2,p3,adv = res
            cs_ptr = (cs_ptr+adv)%4
            bg = CS_COLORS[cs_ptr]
            def csq(c):
                return bg if c==7 else PRIMARY.get(c,(0,0,0))
            clrs = [csq(p0), csq(p1), csq(p2), csq(p3)]
            half = TILE//2
            for y in range(TILE):
                for x in range(TILE):
                    c = clrs[0] if y<half and x<half else clrs[1] if y<half else clrs[2] if x<half else clrs[3]
                    for dy in range(ZOOM):
                        for dx in range(ZOOM):
                            rpx[col*TILE*ZOOM+x*ZOOM+dx, row*TILE*ZOOM+y*ZOOM+dy] = c
        else:
            _, card, fg, gram, adv = res
            cs_ptr = (cs_ptr+adv)%4
            bg = CS_COLORS[cs_ptr]
            fg_rgb = PAL.get(fg,(0,0,0))
            for y in range(TILE):
                b = gram_row(card,y) if gram else grom_row(card,y)
                for x in range(TILE):
                    c = fg_rgb if (b>>(7-x))&1 else bg
                    for dy in range(ZOOM):
                        for dx in range(ZOOM):
                            rpx[col*TILE*ZOOM+x*ZOOM+dx, row*TILE*ZOOM+y*ZOOM+dy] = c

# ---- Compare with renderer PNG ----
rend = Image.open(PNG_PATH)
# Scale reference to match renderer size (renderer uses ZOOM=8, we used 4)
ref2x = ref.resize((rend.width, rend.height), Image.NEAREST)
rpx2 = ref2x.load()
ppx = rend.load()

total = rend.width * rend.height
match = 0
mismatch_samples = []
for y in range(rend.height):
    for x in range(rend.width):
        if rpx2[x,y] == ppx[x,y]:
            match += 1
        elif len(mismatch_samples) < 20:
            tile_col = x // (TILE*8)
            tile_row = y // (TILE*8)
            mismatch_samples.append((tile_col, tile_row, x, y, rpx2[x,y], ppx[x,y]))

pct = 100.0 * match / total
print(f"Pixel match: {match}/{total} = {pct:.2f}%")

if pct < 100:
    print(f"\n{len(mismatch_samples)} sample mismatches:")
    for tc, tr, px, py, ref_c, ren_c in mismatch_samples:
        print(f"  Tile ({tc},{tr}) pixel ({px},{py}): ref={ref_c} vs ren={ren_c}")
else:
    print("PERFECT MATCH — renderer is pixel-identical to reference decode.")

# ---- Per-tile type summary ----
print("\n=== Backtab word type summary ===")
from collections import Counter
types = Counter()
for row in range(ROWS):
    for col in range(COLS):
        w = backtab.get(0x0200+row*20+col, 0)
        res = decode_bt(w)
        if res[0] == 'COLSQ':
            types['ColoredSquares'] += 1
        else:
            _, card, fg, gram, _ = res
            label = f"GRAM FG{fg}" if gram else f"GROM FG{fg}"
            types[label] += 1

for t, c in types.most_common():
    print(f"  {t}: {c}")

# ---- Color stack tracking verification ----
print("\n=== Color Stack tracking ===")
cs_ptr = 0
cs_events = []
for row in range(ROWS):
    for col in range(COLS):
        w = backtab.get(0x0200+row*20+col, 0)
        adv = (w>>13)&1
        if adv:
            cs_ptr = (cs_ptr+1)%4
            cs_events.append((row, col, cs_ptr, CS_COLORS[cs_ptr]))
        # (advance happens before rendering this card)
        cs_ptr = (cs_ptr + adv) % 4
        # but also after... the STIC spec says advance at the start of the card

if cs_events:
    print(f"  {len(cs_events)} CS advance events:")
    for r,c,p,clr in cs_events:
        print(f"    Row {r} Col {c}: CS->{p} = {clr}")
else:
    print("  No CS advance events (all cards have CS_adv=0)")

print("\nVerification complete.")
