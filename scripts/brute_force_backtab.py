#!/usr/bin/env python3
"""Brute-force test all possible FG/BG bit layouts against jzIntv screenshot.
Find which encoding best predicts the actual pixel colors."""

import sys
sys.path.insert(0, '.')
from render_all_rooms import (
    load_grom, parse_backtab, extract_backtab_from_output,
    extract_gram_from_output, parse_memory_dump,
    PALETTE, PASTEL_PALETTE, DEFAULT_BG,
)
from PIL import Image
from itertools import product

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

# ============================================================
# Test different FG/BG encodings
# ============================================================

# For FG/BG mode, the BACKTAB word encodes:
# - Card number (some subset of bits)
# - GRAM flag (bit 11 in standard format)
# - BG color (3-bit index) + BG pastel flag
# - FG color (3-bit index) + FG pastel flag
# 
# We test different bit positions for each field.

def test_encoding(desc, card_bits, card_shift, fg_bits, fg_shift, bg_bits, bg_shift,
                  fg_pastel_bit, bg_pastel_bit, transparent_fg0=True):
    """
    Test a specific FG/BG bit layout.
    
    card_bits: number of bits for card number
    card_shift: right-shift to extract card number bits
    fg_bits: number of FG color bits (1-3)
    fg_shift: right-shift for FG lsb
    bg_bits: number of BG color bits (1-3)
    bg_shift: right-shift for BG lsb
    fg_pastel_bit: bit position of FG pastel flag (-1 if none)
    bg_pastel_bit: bit position of BG pastel flag (-1 if none)
    """
    match = 0
    total = 0
    
    for row in range(12):
        for col in range(20):
            w = grid[row][col]
            is_gram = bool(w & 0x0800)  # bit 11 is always GRAM flag
            
            # Extract card
            card_mask = (1 << card_bits) - 1
            card = (w >> card_shift) & card_mask
            if is_gram:
                card = card & 0x3F  # GRAM: 6 bits
            else:
                card = card & 0xFF  # GROM: 8 bits
            
            # Extract FG color
            fg_mask = (1 << fg_bits) - 1
            fg_idx = (w >> fg_shift) & fg_mask
            fg_pastel = (w >> fg_pastel_bit) & 1 if fg_pastel_bit >= 0 else 0
            
            # Extract BG color
            bg_mask = (1 << bg_bits) - 1
            bg_idx = (w >> bg_shift) & bg_mask
            bg_pastel = (w >> bg_pastel_bit) & 1 if bg_pastel_bit >= 0 else 0
            
            # FG color
            if fg_pastel:
                fg_rgb = PASTEL_PALETTE.get(fg_idx, (255,0,255))
            else:
                fg_rgb = PALETTE.get(fg_idx, (255,0,255))
            
            # BG color
            if bg_pastel:
                bg_rgb = PASTEL_PALETTE.get(bg_idx, DEFAULT_BG)
            else:
                bg_rgb = PALETTE.get(bg_idx, DEFAULT_BG)
            
            # Transparent FG?
            fg_transparent = transparent_fg0 and (fg_idx == 0) and not fg_pastel
            
            # Get card data
            if is_gram:
                cidx = card & 0x3F
                base = 0x3800 + cidx * 8
                card_bytes = bytes(gram_mem.get(base + r, 0) & 0xFF for r in range(8))
            else:
                cidx = card & 0xFF
                off = cidx * 8
                card_bytes = grom[off:off+8] if off+8 <= len(grom) else bytes(8)
            
            tx = JLEFT + col * 8
            ty = JTOP + row * 8
            
            for y in range(8):
                py = ty + y
                if py >= scr_h: continue
                by = card_bytes[y]
                for x in range(8):
                    px = tx + x
                    if px >= scr_w: continue
                    
                    bit = (by >> (7 - x)) & 1
                    actual = jz_rgb(jz_px[px, py])
                    
                    if fg_transparent:
                        expected = bg_rgb
                    elif bit == 0:
                        expected = bg_rgb
                    else:
                        expected = fg_rgb
                    
                    total += 1
                    if expected == actual:
                        match += 1
    
    acc = match / total * 100 if total > 0 else 0
    return match, total, acc


# ============================================================
# Test encodings
# ============================================================
print("=" * 100)
print("BRUTE-FORCE FG/BG BIT LAYOUT SEARCH")
print("=" * 100)
print(f"Testing {240} tiles × {64} pixels = {240*64} total pixels against screenshot")
print()

results = []

# Standard CS mode (baseline)
# Card: bits 0-10, FG: bits 15,14,12, CS advance: bit 13, GRAM: bit 11
def test_cs_mode(transparent_fg0):
    match = 0
    total = 0
    cs_index = 0
    CS = [PASTEL_PALETTE[3]] * 4  # default CS all pastel tan
    
    for row in range(12):
        for col in range(20):
            w = grid[row][col]
            is_gram = bool(w & 0x0800)
            card = w & 0x7FF
            if is_gram: card &= 0x3F
            else: card &= 0xFF
            
            fg_idx = ((w >> 13) & 0x6) | ((w >> 12) & 0x1)
            fg_rgb = PALETTE.get(fg_idx, (255,0,255))
            fg_transparent = transparent_fg0 and (fg_idx == 0)
            
            advance = (w >> 13) & 1
            cs_index = (cs_index + advance) % 4
            bg_rgb = CS[cs_index]
            
            if is_gram:
                cidx = card & 0x3F
                base = 0x3800 + cidx * 8
                card_bytes = bytes(gram_mem.get(base + r, 0) & 0xFF for r in range(8))
            else:
                cidx = card & 0xFF
                off = cidx * 8
                card_bytes = grom[off:off+8] if off+8 <= len(grom) else bytes(8)
            
            tx = JLEFT + col * 8
            ty = JTOP + row * 8
            
            for y in range(8):
                py = ty + y
                if py >= scr_h: continue
                by = card_bytes[y]
                for x in range(8):
                    px = tx + x
                    if px >= scr_w: continue
                    
                    bit = (by >> (7 - x)) & 1
                    actual = jz_rgb(jz_px[px, py])
                    
                    if fg_transparent:
                        expected = bg_rgb
                    elif bit == 0:
                        expected = bg_rgb
                    else:
                        expected = fg_rgb
                    
                    total += 1
                    if expected == actual:
                        match += 1
    
    return match, total, match/total*100

m, t, a = test_cs_mode(True)
print(f"  {'CS mode (FG0=transparent)':45s}: {a:5.1f}%  ({m:6d}/{t:6d})")
results.append(('CS_fg0trans', a))

m, t, a = test_cs_mode(False)
print(f"  {'CS mode (FG0=black)':45s}: {a:5.1f}%  ({m:6d}/{t:6d})")
results.append(('CS_fg0black', a))

# CS mode but advance every tile
def test_cs_advance_every(transparent_fg0):
    match = 0
    total = 0
    cs_index = 0
    CS = [PASTEL_PALETTE[3], PASTEL_PALETTE[3], PALETTE[3], PALETTE[0]]
    
    for row in range(12):
        for col in range(20):
            w = grid[row][col]
            is_gram = bool(w & 0x0800)
            card = w & 0x7FF
            if is_gram: card &= 0x3F
            else: card &= 0xFF
            
            fg_idx = ((w >> 13) & 0x6) | ((w >> 12) & 0x1)
            fg_rgb = PALETTE.get(fg_idx, (255,0,255))
            fg_transparent = transparent_fg0 and (fg_idx == 0)
            
            # Advance CS every tile
            cs_index = (cs_index + 1) % 4
            bg_rgb = CS[cs_index]
            
            if is_gram:
                cidx = card & 0x3F
                base = 0x3800 + cidx * 8
                card_bytes = bytes(gram_mem.get(base + r, 0) & 0xFF for r in range(8))
            else:
                cidx = card & 0xFF
                off = cidx * 8
                card_bytes = grom[off:off+8] if off+8 <= len(grom) else bytes(8)
            
            tx = JLEFT + col * 8
            ty = JTOP + row * 8
            
            for y in range(8):
                py = ty + y
                if py >= scr_h: continue
                by = card_bytes[y]
                for x in range(8):
                    px = tx + x
                    if px >= scr_w: continue
                    
                    bit = (by >> (7 - x)) & 1
                    actual = jz_rgb(jz_px[px, py])
                    
                    if fg_transparent:
                        expected = bg_rgb
                    elif bit == 0:
                        expected = bg_rgb
                    else:
                        expected = fg_rgb
                    
                    total += 1
                    if expected == actual:
                        match += 1
    
    return match, total, match/total*100

m, t, a = test_cs_advance_every(True)
print(f"  {'CS advance-every (FG0=transparent)':45s}: {a:5.1f}%  ({m:6d}/{t:6d})")
results.append(('CS_adv_every_fg0trans', a))

m, t, a = test_cs_advance_every(False)
print(f"  {'CS advance-every (FG0=black)':45s}: {a:5.1f}%  ({m:6d}/{t:6d})")
results.append(('CS_adv_every_fg0black', a))

print()

# Now test FG/BG mode variants
# Card number is typically in bits 0-10 (same as CS mode)
# But BG color replaces some of the unused bits

# Test: standard FG/BG format from Intellivision docs
# GROM: bits 0-7=card, bits 8-10=bg, bit11=0, bits12-14=fg, bit15=bg_pastel
fgbg_variants = [
    # (name, card_bits, card_shift, fg_bits, fg_shift, bg_bits, bg_shift, fg_pastel, bg_pastel, transparent_fg0)
    ("FG/BG: card0-7 bg8-10 fg12-14 bgpast15", 8, 0, 3, 12, 3, 8, -1, 15, True),
    ("FG/BG: card0-7 bg8-10 fg12-14 bgpast15 (no transp)", 8, 0, 3, 12, 3, 8, -1, 15, False),
    ("FG/BG: card0-7 bg8-10 fg12-14 fgpast15 bgpast3", 8, 0, 3, 12, 3, 8, 15, 3, False),
    ("FG/BG: card0-10 bg? fg12-14 bgpast15", 11, 0, 3, 12, 3, 8, -1, 15, True),
    ("FG/BG: card0-10 bg? fg12-14 bgpast15 (nt)", 11, 0, 3, 12, 3, 8, -1, 15, False),
    # FG bits in different positions
    ("FG/BG: card0-7 fg8-10 bg12-14 bgpast15", 8, 0, 3, 8, 3, 12, -1, 15, True),
    ("FG/BG: card0-7 fg8-10 bg12-14 fgpast15", 8, 0, 3, 8, 3, 12, 15, -1, False),
    # bg and fg swapped
    ("FG/BG: card0-7 bg12-14 fg8-10 bgpast15", 8, 0, 3, 8, 3, 12, -1, 15, False),
    ("FG/BG: card0-7 bg12-14 fg8-10 fgpast15", 8, 0, 3, 8, 3, 12, 15, -1, False),
    # bit12 as transparency flag
    ("FG/BG: card0-7 bg8-10 fg? bit12=transp", 8, 0, 3, 13, 3, 8, 14, 15, False),
    # Various card shift ranges
    ("FG/BG: card0-6 bg7-9 fg10-12 bgpast13", 7, 0, 3, 10, 3, 7, -1, 13, True),
    ("FG/BG: card0-6 bg7-9 fg10-12 bgpast13 (nt)", 7, 0, 3, 10, 3, 7, -1, 13, False),
]

for name, cb, cs, fb, fs, bb, bs, fp, bp, t0 in fgbg_variants:
    m, t, a = test_encoding(name, cb, cs, fb, fs, bb, bs, fp, bp, t0)
    print(f"  {name:55s}: {a:5.1f}%  ({m:6d}/{t:6d})")
    results.append((name, a))

# ============================================================
# Brute force: systematic search
# ============================================================
print()
print("=" * 100)
print("SYSTEMATIC SEARCH OVER BIT POSITIONS")
print("=" * 100)

# Fixed: card in bits 0-7 (8 bits), GRAM at bit 11
# Search: FG bits 12-14 or 8-10, BG bits 12-14 or 8-10, pastel at 15 or 3
best_acc = 0
best_params = None

for fg_shift in [8, 12]:
    for bg_shift in [8, 12]:
        if fg_shift == bg_shift:
            continue
        for fg_pastel in [-1, 3, 15]:
            for bg_pastel in [-1, 3, 15]:
                for transparent_fg0 in [True, False]:
                    m, t, a = test_encoding("", 8, 0, 3, fg_shift, 3, bg_shift, fg_pastel, bg_pastel, transparent_fg0)
                    if a > best_acc:
                        best_acc = a
                        best_params = (fg_shift, bg_shift, fg_pastel, bg_pastel, transparent_fg0, m, t)
                    
                    if a > 65:
                        desc = f"card0-7 fg{fg_shift}-{fg_shift+2} bg{bg_shift}-{bg_shift+2} fgp{fg_pastel} bgp{bg_pastel} t0={transparent_fg0}"
                        print(f"  {desc:60s}: {a:5.1f}%  ({m:6d}/{t:6d})")

print()
print(f"BEST: fg_shift={best_params[0]}, bg_shift={best_params[1]}, "
      f"fg_pastel={best_params[2]}, bg_pastel={best_params[3]}, "
      f"transparent_fg0={best_params[4]}")
print(f"  Accuracy: {best_params[6]}/{best_params[7]} = {best_params[6]/best_params[7]*100:.1f}%")
print()

# ============================================================
# Print detailed breakdown for best encoding
# ============================================================
fg_shift, bg_shift, fg_pastel, bg_pastel, transparent_fg0, _, _ = best_params

print("=" * 100)
print(f"DETAILED BREAKDOWN: fg bits {fg_shift}-{fg_shift+2}, bg bits {bg_shift}-{bg_shift+2}, "
      f"fgp={fg_pastel}, bgp={bg_pastel}, t0={transparent_fg0}")
print("=" * 100)

def cn(rgb):
    for d, lbl in [(PALETTE, 'PAL'), (PASTEL_PALETTE, 'PAS')]:
        for k, v in d.items():
            if v == rgb: return '%s[%d]' % (lbl, k)
    if rgb == (0,0,0): return 'BLACK'
    return 'RGB'+str(rgb)

print(f"{'Row':>3s} {'Col':>3s} {'Word':>6s} {'Card':>5s} {'Src':>7s} "
      f"{'b12':>3s} {'b13':>3s} {'FG':>10s} {'BG':>10s} "
      f"{'bit0_dom':>14s} {'bit1_dom':>14s} {'match':>6s}")
print("-" * 130)

for row in range(12):
    for col in range(20):
        w = grid[row][col]
        is_gram = bool(w & 0x0800)
        card = (w >> 0) & 0xFF
        if is_gram: card &= 0x3F
        else: card &= 0xFF
        
        fg_mask = (1 << 3) - 1
        fg_idx = (w >> fg_shift) & fg_mask
        fg_p = (w >> fg_pastel) & 1 if fg_pastel >= 0 else 0
        
        bg_mask = (1 << 3) - 1
        bg_idx = (w >> bg_shift) & bg_mask
        bg_p = (w >> bg_pastel) & 1 if bg_pastel >= 0 else 0
        
        fg_rgb = PASTEL_PALETTE.get(fg_idx, (255,0,255)) if fg_p else PALETTE.get(fg_idx, (255,0,255))
        bg_rgb = PASTEL_PALETTE.get(bg_idx, DEFAULT_BG) if bg_p else PALETTE.get(bg_idx, DEFAULT_BG)
        t0_flag = transparent_fg0 and (fg_idx == 0) and not fg_p
        
        if is_gram:
            cidx = card & 0x3F
            base = 0x3800 + cidx * 8
            card_bytes = bytes(gram_mem.get(base + r, 0) & 0xFF for r in range(8))
        else:
            cidx = card & 0xFF
            off = cidx * 8
            card_bytes = grom[off:off+8] if off+8 <= len(grom) else bytes(8)
        
        tx = JLEFT + col * 8
        ty = JTOP + row * 8
        
        bit0_colors = {}
        bit1_colors = {}
        tile_match = 0
        tile_total = 0
        
        for y in range(8):
            py = ty + y
            if py >= scr_h: continue
            by = card_bytes[y]
            for x in range(8):
                px = tx + x
                if px >= scr_w: continue
                
                bit = (by >> (7 - x)) & 1
                actual = jz_rgb(jz_px[px, py])
                
                if t0_flag:
                    expected = bg_rgb
                elif bit == 0:
                    expected = bg_rgb
                else:
                    expected = fg_rgb
                
                tile_total += 1
                if expected == actual:
                    tile_match += 1
                
                if bit == 0:
                    bit0_colors[actual] = bit0_colors.get(actual, 0) + 1
                else:
                    bit1_colors[actual] = bit1_colors.get(actual, 0) + 1
        
        b0d = max(bit0_colors.items(), key=lambda x: x[1]) if bit0_colors else ((0,0,0),0)
        b1d = max(bit1_colors.items(), key=lambda x: x[1]) if bit1_colors else ((0,0,0),0)
        
        b12 = (w >> 12) & 1
        b13 = (w >> 13) & 1
        
        acc = tile_match / tile_total * 100 if tile_total > 0 else 0
        marker = '✓' if acc > 80 else ('~' if acc > 50 else '✗')
        
        print(f"{row:3d} {col:3d} 0x{w:04X} {card:5d} {'GRAM' if is_gram else 'grom':>7s} "
              f"{b12:3d} {b13:3d} {cn(fg_rgb):>10s} {cn(bg_rgb):>10s} "
              f"{cn(b0d[0]):>14s} {cn(b1d[0]):>14s} {marker}{acc:4.0f}%")

print()
print("✓ = >80% match, ~ = 50-80%, ✗ = <50%")
