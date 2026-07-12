#!/usr/bin/env python3
"""Brute-force test ALL possible FG bit mappings and rendering models.

Tests every possible combination of:
- Which BACKTAB bits encode FG color (up to 4 bits → 3-bit color)
- Which bit encodes transparency
- Whether to use Colored Squares cycling
- Different CS advance models
"""
import sys
sys.path.insert(0, '.')
from render_all_rooms import (
    load_grom, parse_backtab, extract_backtab_from_output,
    extract_gram_from_output, parse_memory_dump,
    PALETTE, PASTEL_PALETTE, DEFAULT_BG,
)
from PIL import Image
from collections import Counter
from itertools import product

def cn(rgb):
    for d, lbl in [(PALETTE, 'PAL'), (PASTEL_PALETTE, 'PAS')]:
        for k, v in d.items():
            if v == rgb: return '%s[%d]' % (lbl, k)
    if rgb == (0,0,0): return 'BLK'
    return 'RGB'+str(rgb)

grom = load_grom()
with open('traces/_cmp_room_0_out.txt', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
grid = parse_backtab(extract_backtab_from_output(content))
gram_text = extract_gram_from_output(content)
gram_mem = parse_memory_dump(gram_text, 0x3800, 512) if gram_text else {}

scr = Image.open('sprites/room_0_jzintv.gif')
scr_w, scr_h = scr.size
jz_pal = scr.getpalette()
jz_px = scr.load()

def jz_rgb(idx):
    if idx * 3 + 2 < len(jz_pal):
        return (jz_pal[idx*3], jz_pal[idx*3+1], jz_pal[idx*3+2])
    return (0,0,0)

JLEFT, JTOP = 80, 52
CS_DEFAULT = [PASTEL_PALETTE[3]] * 4  # all pastel tan

# ============================================================
# ALL possible FG bit mappings
# ============================================================
# We have bits 12, 13, 14, 15 to work with
# FG is 0-7 (3 bits). We need to map 1-4 input bits to 3 output bits.
# Also: which bit (if any) encodes the "transparent" flag?

def make_fg_decoders():
    """Generate all possible FG color decoders.
    Each decoder is: f(word) -> (fg_color, transparent)
    """
    decoders = []
    
    # Model A: FG bits at specific positions, no transparency flag
    for fg12 in [0, 1]:
        for fg13 in [0, 1]:
            for fg14 in [0, 1]:
                for fg15 in [0, 1]:
                    # Build mask and shift amounts
                    fg_bits = []
                    if fg12: fg_bits.append((12, 0))
                    if fg13: fg_bits.append((13, 1))
                    if fg14: fg_bits.append((14, 2))
                    if fg15: fg_bits.append((15, 3 if len(fg_bits) >= 3 else 2))
                    if len(fg_bits) == 0:
                        continue
                    # Normalize: use the first 3 bits as FG
                    # FG = sum of bit[pos] * 2^idx
                    def make_decoder(bits):
                        def decode(word):
                            fg = 0
                            for pos, idx in bits[:3]:
                                if (word >> pos) & 1:
                                    fg |= (1 << idx)
                            return fg & 0x7, (fg & 0x7) == 0  # FG=0 → transparent
                        return decode
                    decoders.append((f'FG_bits={[(p,i) for p,i in fg_bits[:3]]}', make_decoder(fg_bits[:3])))
    
    # Model B: Transparency controlled by specific bit
    for transp_bit in [12, 13, 14, 15]:
        remaining = [b for b in [12, 13, 14, 15] if b != transp_bit]
        for r0, r1, r2 in product(remaining, repeat=3):
            if r0 == r1 or r0 == r2 or r1 == r2:
                continue
            tb = transp_bit
            b0, b1, b2 = r0, r1, r2
            def make_transp_decoder(t_bit, bg0, bg1, bg2):
                def decode(word):
                    transparent = ((word >> t_bit) & 1) == 0
                    fg = 0
                    if (word >> bg0) & 1: fg |= 1
                    if (word >> bg1) & 1: fg |= 2
                    if (word >> bg2) & 1: fg |= 4
                    if transparent:
                        return 0, True
                    return fg & 0x7, False
                return decode
            decoders.append((f'Transp_b{tb}_FG_b{b0}{b1}{b2}', make_transp_decoder(tb, b0, b1, b2)))
    
    return decoders

# ============================================================
# CS advance models
# ============================================================
# Model 1: No advance (all tiles use CS0)
# Model 2: Advance by 1 per tile (cs = position % 4)
# Model 3: Advance when bit N is set
# Model 4: Colored Squares (cs = (col % 4))

def cs_no_advance(row, col, word):
    return 0

def cs_per_tile(row, col, word):
    return (row * 20 + col) % 4

def cs_per_col(row, col, word):
    return col % 4

def cs_per_row(row, col, word):
    return row % 4

def cs_advance_bit12(row, col, word):
    # Stateful - need external counter. Use absolute position for now.
    return 0

def cs_advance_bit13(row, col, word):
    return 0

cs_models = [
    ('CS_fixed_0', cs_no_advance),
    ('CS_per_tile', cs_per_tile),
    ('CS_per_col', cs_per_col),
    ('CS_per_row', cs_per_row),
]

# ============================================================
# GROM card bytes cache
# ============================================================
card_cache = {}
def get_card_bytes(is_gram, card_idx):
    key = (is_gram, card_idx)
    if key in card_cache:
        return card_cache[key]
    if is_gram:
        cidx = card_idx & 0x3F
        baddr = 0x3800 + cidx * 8
        cb = bytes(gram_mem.get(baddr + ry, 0) & 0xFF for ry in range(8))
    else:
        cidx = card_idx & 0xFF
        baddr = cidx * 8
        cb = grom[baddr:baddr+8] if baddr+8 <= len(grom) else bytes(8)
    card_cache[key] = cb
    return cb

# ============================================================
# Test ALL combinations
# ============================================================
decoders = make_fg_decoders()
print(f'Testing {len(decoders)} FG decoders × {len(cs_models)} CS models = {len(decoders)*len(cs_models)} combinations')
print()

# Only test on GROM tiles (no GRAM, to avoid dynamic content issues)
grom_positions = []
for row in range(12):
    for col in range(20):
        w = grid[row][col]
        if not (w & 0x0800):  # GROM
            grom_positions.append((row, col, w))

results = []

for cs_name, cs_fn in cs_models:
    for fg_name, fg_fn in decoders:
        match = 0
        total = 0
        
        for row, col, w in grom_positions:
            card_idx = w & 0xFF
            cb = get_card_bytes(False, card_idx)
            
            fg_color, transparent = fg_fn(w)
            cs_idx = cs_fn(row, col, w)
            bg = CS_DEFAULT[cs_idx]
            fg_rgb = PALETTE.get(fg_color, (255, 0, 255))
            
            tx = JLEFT + col * 8
            ty = JTOP + row * 8
            
            for y in range(8):
                py = ty + y
                if py >= scr_h: continue
                byte_val = cb[y]
                for x in range(8):
                    px = tx + x
                    if px >= scr_w: continue
                    bit = (byte_val >> (7 - x)) & 1
                    actual = jz_rgb(jz_px[px, py])
                    
                    if transparent:
                        expected = bg
                    elif bit == 0:
                        expected = bg
                    else:
                        expected = fg_rgb
                    
                    total += 1
                    if expected == actual:
                        match += 1
        
        acc = match / total * 100 if total > 0 else 0
        results.append((acc, cs_name, fg_name, match, total))

# Sort by accuracy
results.sort(key=lambda x: -x[0])

print('=== TOP 20 MODELS ===')
print(f'{"Rank":>4s} {"Accuracy":>8s} {"CS Model":>20s} {"FG Decoder":>40s}')
print('-' * 80)
for i, (acc, cs_name, fg_name, match, total) in enumerate(results[:20]):
    print(f'{i+1:4d} {acc:7.2f}% {cs_name:>20s} {fg_name:>40s}')

# ============================================================
# Also test with correct card number (from L_5EC7 constructor)
# ============================================================
# The constructor uses: bits 0-2 = card low, ANDI $3607 preserves bits 0,1,2,9,10,12,13
# Final card = (bits 3-10 from attribute) | (bits 0-2 from card)
# Let me test what happens if we use the FULL card number (bits 0-10) correctly

print()
print('=== TESTING WITH FULL CARD NUMBER (bits 0-10) ===')

# Standard card: word & 0x7FF
# L_5EC7 card: still word & 0x7FF (the constructor ensures this)

# But what if the card is just bits 0-7 and bits 8-10 are for FG?
results2 = []

for cs_name, cs_fn in cs_models:
    for fg_name, fg_fn in decoders:
        match = 0
        total = 0
        
        for row, col, w in grom_positions:
            # Use just bits 0-7 as card index
            card_idx = w & 0xFF
            cb = get_card_bytes(False, card_idx)
            
            fg_color, transparent = fg_fn(w)
            cs_idx = cs_fn(row, col, w)
            bg = CS_DEFAULT[cs_idx]
            fg_rgb = PALETTE.get(fg_color, (255, 0, 255))
            
            tx = JLEFT + col * 8
            ty = JTOP + row * 8
            
            for y in range(8):
                py = ty + y
                if py >= scr_h: continue
                byte_val = cb[y]
                for x in range(8):
                    px = tx + x
                    if px >= scr_w: continue
                    bit = (byte_val >> (7 - x)) & 1
                    actual = jz_rgb(jz_px[px, py])
                    
                    if transparent:
                        expected = bg
                    elif bit == 0:
                        expected = bg
                    else:
                        expected = fg_rgb
                    
                    total += 1
                    if expected == actual:
                        match += 1
        
        acc = match / total * 100 if total > 0 else 0
        results2.append((acc, cs_name, fg_name, match, total))

results2.sort(key=lambda x: -x[0])

print('=== TOP 10 CARD=BYTE MODELS ===')
for i, (acc, cs_name, fg_name, match, total) in enumerate(results2[:10]):
    print(f'{i+1:4d} {acc:7.2f}% {cs_name:>20s} {fg_name:>40s}')

# ============================================================
# Test Colored Squares with specific per-tile FG
# ============================================================
print()
print('=== TESTING COLORED SQUARES SCENARIO ===')
# In Colored Squares mode, CS cycles but FG is per-tile
# What if FG color is determined by bits 9-10 (from ANDI mask)?
# ANDI #$3607 preserves bits 9,10 in the final word
# Maybe bits 9-10 encode the FG color!

# Also test: what if bits 0-2 encode the FG color (in CS mode)?
results3 = []

# Test: FG = bits 9-10 (2 bits → 0-3), transparent=auto when FG=0
def fg_bits_9_10(word):
    fg = (word >> 9) & 0x3
    return fg, (fg == 0)

# Test: FG = bits 12,9,10 (3 bits → 0-7)  
def fg_bits_12_9_10(word):
    fg = ((word >> 12) & 0x1) | ((word >> 9) & 0x6)
    return fg, (fg == 0)

# Test: FG = bits 13,12 (2 bits), transparent=bit9
def fg_b13_12_transp_b9(word):
    fg = ((word >> 13) & 0x2) | ((word >> 12) & 0x1)
    transp = ((word >> 9) & 1) == 0
    return fg, transp

# Test: FG from ANDI-preserved bits in non-standard arrangement
# ANDI keeps bits 0,1,2,9,10,12,13
# Maybe: FG = bits 12,9,10; Card = bits 0,1,2,?; CS advance = bit 13
def fg_12_9_10_transp_auto(word):
    fg = ((word >> 12) & 0x1) | ((word >> 9) & 0x6)
    return fg, (fg == 0)

# Test: FG = bits 13,10,9
def fg_13_10_9(word):
    fg = ((word >> 13) & 0x4) | ((word >> 10) & 0x2) | ((word >> 9) & 0x1)
    return fg & 0x7, (fg & 0x7) == 0

special_decoders = [
    ('FG_9_10', fg_bits_9_10),
    ('FG_12_9_10', fg_bits_12_9_10),
    ('FG_13_10_9', fg_13_10_9),
    ('FG_13_12_transp_b9', fg_b13_12_transp_b9),
    ('FG_12_9_10_auto', fg_12_9_10_transp_auto),
]

for fg_name, fg_fn in special_decoders:
    for cs_name, cs_fn in cs_models:
        match = 0
        total = 0
        
        for row, col, w in grom_positions:
            card_idx = w & 0xFF
            cb = get_card_bytes(False, card_idx)
            
            fg_color, transparent = fg_fn(w)
            cs_idx = cs_fn(row, col, w)
            bg = CS_DEFAULT[cs_idx]
            fg_rgb = PALETTE.get(fg_color, (255, 0, 255))
            
            tx = JLEFT + col * 8
            ty = JTOP + row * 8
            
            for y in range(8):
                py = ty + y
                if py >= scr_h: continue
                byte_val = cb[y]
                for x in range(8):
                    px = tx + x
                    if px >= scr_w: continue
                    bit = (byte_val >> (7 - x)) & 1
                    actual = jz_rgb(jz_px[px, py])
                    
                    if transparent:
                        expected = bg
                    elif bit == 0:
                        expected = bg
                    else:
                        expected = fg_rgb
                    
                    total += 1
                    if expected == actual:
                        match += 1
        
        acc = match / total * 100 if total > 0 else 0
        results3.append((acc, cs_name, fg_name, match, total))

results3.sort(key=lambda x: -x[0])
for i, (acc, cs_name, fg_name, match, total) in enumerate(results3):
    print(f'  {acc:6.2f}% {cs_name:>20s} {fg_name:>40s}')

# Show average accuracy for the simple "always PAS[3]" model
print()
pas3_match = 0
pas3_total = 0
for row, col, w in grom_positions:
    card_idx = w & 0xFF
    cb = get_card_bytes(False, card_idx)
    tx = JLEFT + col * 8
    ty = JTOP + row * 8
    for y in range(8):
        py = ty + y
        if py >= scr_h: continue
        for x in range(8):
            px = tx + x
            if px >= scr_w: continue
            actual = jz_rgb(jz_px[px, py])
            pas3_total += 1
            if actual == PASTEL_PALETTE[3]:
                pas3_match += 1
print(f'Baseline (always PAS[3]): {pas3_match/pas3_total*100:.2f}% ({pas3_match}/{pas3_total})')
