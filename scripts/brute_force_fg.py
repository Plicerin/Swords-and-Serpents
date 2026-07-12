#!/usr/bin/env python3
"""Brute-force search for correct FG bit positions and CS color stack values."""
import sys
sys.path.insert(0, '.')
from render_all_rooms import (
    load_grom, parse_backtab, extract_backtab_from_output,
    extract_gram_from_output, parse_memory_dump,
    PALETTE, PASTEL_PALETTE, DEFAULT_BG,
)
from PIL import Image

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

left, top = 80, 52

# All 16 color values (primary 0-7, pastel 8-15)
ALL_COLORS = {}
for i in range(8):
    ALL_COLORS[i] = PALETTE[i]
    ALL_COLORS[8+i] = PASTEL_PALETTE[i]

def render_with_config(fg_bit0, fg_bit1, fg_bit2, cs_adv_bit, cs_colors, fg_zero_transparent):
    """Render room with given FG bit positions and CS config.
    
    fg_bit0/1/2: which BACKTAB bit positions contain FG bits 0/1/2
    cs_adv_bit: which bit is the CS advance
    cs_colors: list of 4 RGB tuples (CS0-CS3)
    fg_zero_transparent: if True, fg=0 means transparent (show CS bg for card bit=1)
    """
    img = Image.new('RGB', (160, 96))
    px = img.load()
    cs_idx = 0
    
    for row in range(12):
        for col in range(20):
            w = grid[row][col]
            
            # Extract card
            card = w & 0x7FF
            is_gram = bool(w & 0x0800)
            
            # Extract FG
            fg = (((w >> fg_bit2) & 1) << 2) | \
                 (((w >> fg_bit1) & 1) << 1) | \
                 ((w >> fg_bit0) & 1)
            
            # CS advance
            cs_idx = (cs_idx + ((w >> cs_adv_bit) & 1)) % 4
            bg = cs_colors[cs_idx]
            
            fg_trans = fg_zero_transparent and (fg == 0)
            fg_rgb = ALL_COLORS.get(fg, (255, 0, 255))
            
            # Render card
            if is_gram:
                cidx = card & 0x3F
                base = 0x3800 + cidx * 8
                card_bytes = bytes(gram_mem.get(base+r, 0) & 0xFF for r in range(8))
            else:
                cidx = card & 0xFF
                base = cidx * 8
                card_bytes = grom[base:base+8] if base+8 <= len(grom) else bytes(8)
            
            for y in range(8):
                b = card_bytes[y]
                for x in range(8):
                    bit = (b >> (7-x)) & 1
                    if bit == 0 or fg_trans:
                        rgb = bg
                    else:
                        rgb = fg_rgb
                    px[col*8+x, row*8+y] = rgb
    
    # Compare
    match = 0
    total = 0
    for y in range(96):
        for x in range(160):
            our = img.getpixel((x, y))
            jz = jz_rgb(jz_px[left+x, top+y])
            if our == jz:
                match += 1
            total += 1
    return match, total, img

# Define CS configurations to test
def make_cs(c0_primary, c0_pastel, c1_primary, c1_pastel, c2_primary, c2_pastel, c3_primary, c3_pastel):
    """Build CS list. color_idx 0-7, pastel flag."""
    def rgb(primary_idx, pastel_flag):
        if pastel_flag:
            return PASTEL_PALETTE.get(primary_idx, DEFAULT_BG)
        return PALETTE.get(primary_idx, DEFAULT_BG)
    return [rgb(c0_primary, c0_pastel), rgb(c1_primary, c1_pastel),
            rgb(c2_primary, c2_pastel), rgb(c3_primary, c3_pastel)]

# Key CS configs to test
cs_configs = [
    ("all PASTEL[3]", [PASTEL_PALETTE[3]]*4),
    ("all PASTEL[5]", [PASTEL_PALETTE[5]]*4),
    ("all PAL[3]", [PALETTE[3]]*4),
    ("all PAL[5]", [PALETTE[5]]*4),
    ("PASTEL[3],PASTEL[1],PASTEL[1],PAL[2]", [PASTEL_PALETTE[3], PASTEL_PALETTE[1], PASTEL_PALETTE[1], PALETTE[2]]),
    ("PASTEL[7],PASTEL[1],PASTEL[1],PASTEL[3]", [PASTEL_PALETTE[7], PASTEL_PALETTE[1], PASTEL_PALETTE[1], PASTEL_PALETTE[3]]),
    ("PASTEL[3],PAL[1],PAL[1],PASTEL[3]", [PASTEL_PALETTE[3], PALETTE[1], PALETTE[1], PASTEL_PALETTE[3]]),
    ("PAL[0],PAL[1],PASTEL[3],PASTEL[3]", [PALETTE[0], PALETTE[1], PASTEL_PALETTE[3], PASTEL_PALETTE[3]]),
]

# FG bit position combinations to test (bit0, bit1, bit2, cs_adv_bit)
# Standard: (12, 14, 15, 13)
fg_configs = [
    # Standard Color Stack
    ("std(12,14,15) csadv=13", 12, 14, 15, 13),
    # GSG (bits 9-11 for FG)
    ("GSG(9,10,11) csadv=12", 9, 10, 11, 12),
    ("GSG(9,10,11) csadv=13", 9, 10, 11, 13),
    ("GSG(9,10,11) csadv=14", 9, 10, 11, 14),
    # Various FG combos
    ("(10,11,12) csadv=13", 10, 11, 12, 13),
    ("(10,11,12) csadv=9", 10, 11, 12, 9),
    ("(11,12,13) csadv=10", 11, 12, 13, 10),
    ("(11,12,13) csadv=14", 11, 12, 13, 14),
    ("(12,13,14) csadv=15", 12, 13, 14, 15),
    ("(12,13,14) csadv=11", 12, 13, 14, 11),
    ("(12,13,15) csadv=14", 12, 13, 15, 14),
    ("(13,14,15) csadv=12", 13, 14, 15, 12),
    # Bit 11 is GRAM select, don't use as FG
    ("(10,12,14) csadv=13", 10, 12, 14, 13),
    ("(9,11,14) csadv=13", 9, 11, 14, 13),  # bit 11 is GRAM though
]

print("=== Brute-force FG + CS search ===")
print()

best_overall = (0, None, None, None)

for fg_name, b0, b1, b2, cs_adv in fg_configs:
    best_for_fg = (0, None)
    for cs_name, cs_colors in cs_configs:
        for fg0_trans in [True, False]:
            match, total, img = render_with_config(b0, b1, b2, cs_adv, cs_colors, fg0_trans)
            pct = 100.0 * match / total if total else 0
            if pct > best_for_fg[0]:
                best_for_fg = (pct, cs_name, fg0_trans)
            if pct > best_overall[0]:
                best_overall = (pct, fg_name, cs_name, fg0_trans, b0, b1, b2, cs_adv)
    
    print(f"  {fg_name}: best={best_for_fg[0]:.1f}% with CS={best_for_fg[1]}, fg0_trans={best_for_fg[2]}")

print()
print(f"=== BEST OVERALL: {best_overall[0]:.1f}% ===")
print(f"  FG bits: {best_overall[1]} (bit0={best_overall[4]}, bit1={best_overall[5]}, bit2={best_overall[6]})")
print(f"  CS advance bit: {best_overall[7]}")
print(f"  CS config: {best_overall[2]}")
print(f"  fg=0 transparent: {best_overall[3]}")

# Now test CS individually for top FG config
print()
print("=== Testing all single-color CS configs with best FG ===")
_, b0, b1, b2, cs_adv = best_overall[1], best_overall[4], best_overall[5], best_overall[6], best_overall[7]

for ci in range(8):
    for pastel in [False, True]:
        palette = PASTEL_PALETTE if pastel else PALETTE
        label = f"{'PASTEL' if pastel else 'PAL'}[{ci}]"
        cs = [palette[ci]] * 4
        for fg0_trans in [True, False]:
            match, total, _ = render_with_config(b0, b1, b2, cs_adv, cs, fg0_trans)
            pct = 100.0 * match / total if total else 0
            if pct > 30:
                print(f"  CS=all {label:12s} fg0_trans={fg0_trans}: {pct:.1f}%")

print()
print("=== Testing top CS + individual fg0_trans on CS advance behavior ===")
# Test with best FG but non-uniform CS where CS1 differs
for ci in range(8):
    for pastel in [False, True]:
        palette = PASTEL_PALETTE if pastel else PALETTE
        cs0 = PASTEL_PALETTE[3]  # CS0 = pastel tan (for floor)
        cs1 = palette[ci]
        cs = [cs0, cs1, cs1, cs0]
        for fg0_trans in [True, False]:
            match, total, _ = render_with_config(b0, b1, b2, cs_adv, cs, fg0_trans)
            pct = 100.0 * match / total if total else 0
            if pct > 50:
                label = f"{'PASTEL' if pastel else 'PAL'}[{ci}]"
                print(f"  CS=[PASTEL[3],{label},{label},PASTEL[3]] fg0_trans={fg0_trans}: {pct:.1f}%")
