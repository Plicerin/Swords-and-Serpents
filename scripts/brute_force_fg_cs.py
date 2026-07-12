#!/usr/bin/env python3
"""Brute-force FG bit positions, CS advance bit, and CS color values."""
import sys
sys.path.insert(0, '.')
from render_all_rooms import (
    load_grom, parse_backtab, extract_backtab_from_output,
    extract_gram_from_output, parse_memory_dump,
    PALETTE, PASTEL_PALETTE, DEFAULT_BG,
)
from PIL import Image
from itertools import combinations

with open('traces/_cmp_room_0_out.txt', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
grid = parse_backtab(extract_backtab_from_output(content))
gram_text = extract_gram_from_output(content)
gram_mem = parse_memory_dump(gram_text, 0x3800, 512) if gram_text else {}
grom = load_grom()

scr = Image.open('sprites/room_0_jzintv.gif')
jz_pal = scr.getpalette()
jz_px = scr.load()
def jz_rgb(idx):
    if idx * 3 + 2 < len(jz_pal):
        return (jz_pal[idx*3], jz_pal[idx*3+1], jz_pal[idx*3+2])
    return (0, 0, 0)

JLEFT, JTOP = 80, 52

def cn(rgb):
    for d, lbl in [(PALETTE, 'PAL'), (PASTEL_PALETTE, 'PAS')]:
        for k, v in d.items():
            if v == rgb: return f'{lbl}[{k}]'
    if rgb == (0,0,0): return 'BLACK'
    if rgb == (255,0,255): return 'MAGENTA'
    return str(rgb)

# All 3-bit combinations from 4 bits (bits 12-15)
# We try all C(4,3) = 4 combos, each with all 6 permutations (ordering)
bits_12_15 = [12, 13, 14, 15]
all_fg_combos = []
for combo in combinations(bits_12_15, 3):
    # Try all 6 orderings of these 3 bits -> bits [2,1,0] of FG
    from itertools import permutations
    for perm in permutations(combo):
        all_fg_combos.append(perm)

# CS advance bit: could be any of bits 12-15 that isn't an FG bit
# or any other bit. We'll test bits 9-15.

# CS values to test
all_cs_configs = []
for cs0_idx in range(16):  # 0-7 primary, 8-15 pastel
    for cs1_idx in range(16):
        for cs2_idx in range(16):
            for cs3_idx in range(16):
                all_cs_configs.append([cs0_idx, cs1_idx, cs2_idx, cs3_idx])

def cs_rgb(idx):
    if idx >= 8:
        return PASTEL_PALETTE.get(idx - 8, (255,0,255))
    return PALETTE.get(idx, (255,0,255))

def render_test(fg_bits, cs_adv_bit, fg0_transparent, cs_indices):
    """Render room 0 and compare against jzIntv."""
    # fg_bits is (bit2, bit1, bit0) where bit2 is MSB of FG
    b2, b1, b0 = fg_bits
    
    cs_vals = [cs_rgb(i) for i in cs_indices]
    cs_ptr = 0
    
    match = 0
    total = 0
    mismatches = {}
    
    for row in range(12):
        for col in range(20):
            w = grid[row][col]
            card = w & 0x7FF
            is_gram = bool(w & 0x0800)
            
            # Extract FG
            fg = ((w >> b2) & 1) << 2 | ((w >> b1) & 1) << 1 | ((w >> b0) & 1)
            fg_rgb = PALETTE.get(fg, (255,0,255))
            
            # CS advance
            advance = (w >> cs_adv_bit) & 1
            cs_ptr = (cs_ptr + advance) % 4
            bg = cs_vals[cs_ptr]
            
            # Get card bytes
            if is_gram:
                cidx = card & 0x3F
                base = 0x3800 + cidx * 8
                card_bytes = bytes(gram_mem.get(base+r, 0) & 0xFF for r in range(8))
            else:
                cidx = card & 0xFF
                base = cidx * 8
                card_bytes = grom[base:base+8] if base+8 <= len(grom) else bytes(8)
            
            # Render tile
            for y in range(8):
                b = card_bytes[y]
                for x in range(8):
                    bit = (b >> (7-x)) & 1
                    if bit == 0:
                        our_rgb = bg  # card background = CS bg
                    else:
                        if fg0_transparent and fg == 0:
                            our_rgb = bg  # FG=0 transparent
                        else:
                            our_rgb = fg_rgb
                    
                    jz_idx = jz_px[JLEFT + col*8 + x, JTOP + row*8 + y]
                    jz_rgb_val = jz_rgb(jz_idx)
                    
                    if our_rgb == jz_rgb_val:
                        match += 1
                    else:
                        key = (our_rgb, jz_rgb_val)
                        mismatches[key] = mismatches.get(key, 0) + 1
                    total += 1
    
    return match, total, mismatches

# Test phase 1: Find best FG bit positions + CS advance bit
# (with simple CS = all pastel tan, fg0_transparent=True)
print("=" * 80)
print("PHASE 1: Find correct FG bit positions and CS advance bit")
print("=" * 80)

cs_all_pt = [11, 11, 11, 11]  # all pastel tan (8+3=11)

best_overall = 0
best_config = None

# First find FG bits + CS advance with simple CS
for fg_combo in all_fg_combos:
    # Remaining bit that could be CS advance
    used = set(fg_combo)
    remaining = [b for b in bits_12_15 if b not in used]
    for adv_bit in remaining + list(used):  # CS advance could overlap with FG bits
        for fg0_trans in [True, False]:
            match, total, mm = render_test(fg_combo, adv_bit, fg0_trans, cs_all_pt)
            pct = 100.0 * match / total
            if pct > best_overall:
                best_overall = pct
                best_config = (fg_combo, adv_bit, fg0_trans, cs_all_pt, match, total)
                top_mm = sorted(mm.items(), key=lambda x: -x[1])[:5]
                top_str = ', '.join(f'{cn(o)}->{cn(j)}:{n}' for (o,j),n in top_mm)
                print(f"  NEW BEST: {pct:.2f}% FG_bits={fg_combo} adv=bit{adv_bit} fg0_trans={fg0_trans} CS=all_PAS[3]  mismatches: {top_str}")

print()
print(f"Phase 1 best: {best_overall:.2f}% with {best_config[:4]}")

# Phase 2: With best FG bits, search all CS configurations
# But 16^4 = 65536 is too many. Let's try a smarter approach.
# Many CS values might produce the same effective colors.

# Phase 2a: Try uniform CS (all 4 same)
print()
print("=" * 80)
print("PHASE 2a: With best FG bits, try uniform CS values")
print("=" * 80)

best_fg, best_adv, best_fg0, _, _, _ = best_config

best_uniform = 0
best_uniform_config = None
for cs_val in range(16):
    match, total, mm = render_test(best_fg, best_adv, best_fg0, [cs_val]*4)
    pct = 100.0 * match / total
    if pct > best_uniform:
        best_uniform = pct
        best_uniform_config = (cs_val, match)
    if pct > best_overall - 5:  # show close ones
        top_mm = sorted(mm.items(), key=lambda x: -x[1])[:3]
        top_str = ', '.join(f'{cn(o)}->{cn(j)}:{n}' for (o,j),n in top_mm)
        name = f'PAS[{cs_val-8}]' if cs_val >= 8 else f'PAL[{cs_val}]'
        print(f"  CS={name:>8s}: {pct:.2f}%  top: {top_str}")

print(f"\nPhase 2a best: {best_uniform:.2f}% with CS={best_uniform_config[0]}")

# Phase 2b: Use the CS shadow values from 8-bit RAM
print()
print("=" * 80)
print("PHASE 2b: Test CS shadow values from 8-bit RAM")
print("=" * 80)

# From earlier analysis: $017B=0x0F(pastel white), $017C=0x09(pastel blue), $017D=0x09(pastel blue), $017E=0x02(red)
cs_shadow = [0x0F, 0x09, 0x09, 0x02]  # as raw indices (0-15)
match, total, mm = render_test(best_fg, best_adv, best_fg0, cs_shadow)
pct = 100.0 * match / total
top_mm = sorted(mm.items(), key=lambda x: -x[1])[:5]
top_str = ', '.join(f'{cn(o)}->{cn(j)}:{n}' for (o,j),n in top_mm)
print(f"CS=PAS[7],PAS[1],PAS[1],PAL[2]: {pct:.2f}%  top: {top_str}")

# Phase 3: Per-tile analysis — for each tile, what FG + CS produces perfect match?
print()
print("=" * 80)
print("PHASE 3: Per-tile optimal FG/CS analysis")
print("=" * 80)

# For each unique BACKTAB word, find which FG value and CS bg produce best match
word_analysis = {}
for row in range(12):
    for col in range(20):
        w = grid[row][col]
        if w in word_analysis:
            continue
        card = w & 0x7FF
        is_gram = bool(w & 0x0800)
        
        # Get card bytes
        if is_gram:
            cidx = card & 0x3F
            base = 0x3800 + cidx * 8
            card_bytes = bytes(gram_mem.get(base+r, 0) & 0xFF for r in range(8))
        else:
            cidx = card & 0xFF
            base = cidx * 8
            card_bytes = grom[base:base+8] if base+8 <= len(grom) else bytes(8)
        
        best_fg_for_tile = None
        best_cs_for_tile = None
        best_match = 0
        
        for test_fg in range(8):
            fg_rgb = PALETTE.get(test_fg)
            for test_cs_idx in range(16):
                cs_rgb_val = cs_rgb(test_cs_idx)
                tile_match = 0
                for y in range(8):
                    b = card_bytes[y]
                    for x in range(8):
                        bit = (b >> (7-x)) & 1
                        if bit == 0:
                            our_rgb = cs_rgb_val
                        else:
                            if test_fg == 0:
                                our_rgb = cs_rgb_val  # FG=0 transparent
                            else:
                                our_rgb = fg_rgb
                        jz_idx = jz_px[JLEFT + col*8 + x, JTOP + row*8 + y]
                        jz_val = jz_rgb(jz_idx)
                        if our_rgb == jz_val:
                            tile_match += 1
                if tile_match > best_match:
                    best_match = tile_match
                    best_fg_for_tile = test_fg
                    best_cs_for_tile = test_cs_idx
        
        word_analysis[w] = {
            'card': card, 'is_gram': is_gram, 'cidx': cidx,
            'best_fg': best_fg_for_tile, 'best_cs': best_cs_for_tile,
            'best_match': best_match,
            'card_bytes': list(card_bytes),
        }

# Show results, grouped by pattern
print(f"{'Word':>6} {'c8':>4} {'bits':>5} {'BestFG':>6} {'BestCS':>10} {'Match':>5}")
print("-" * 50)
for w, info in sorted(word_analysis.items(), key=lambda x: -x[1]['best_match']):
    c8 = info['card'] & 0xFF
    bits_set = sum(bin(b).count('1') for b in info['card_bytes'])
    cs_name = f'PAS[{info["best_cs"]-8}]' if info['best_cs'] >= 8 else f'PAL[{info["best_cs"]}]'
    print(f"0x{w:04X} {c8:4d} {bits_set:5d} FG={info['best_fg']:1d} {cs_name:>10s} {info['best_match']:4d}/64")

PYEOF
