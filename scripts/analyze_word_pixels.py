#!/usr/bin/env python3
"""Analyze per-word pixel mismatches to reverse-engineer correct FG/CS behavior."""
import sys
sys.path.insert(0, '.')
from render_all_rooms import (
    load_grom, parse_backtab, extract_backtab_from_output,
    extract_gram_from_output, parse_memory_dump,
    render_gram_card_with_bitmap, render_grom_card_with_bitmap,
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

# FG extraction: bits 13/14/15, bit 12 = CS advance, fg=0 transparent
def decode_new(word):
    card = word & 0x7FF
    is_gram = bool(word & 0x0800)
    fg = (word >> 13) & 0x7
    fg_transparent = (fg == 0)
    cs_advance = (word >> 12) & 1
    return card, fg, is_gram, fg_transparent, cs_advance

# Build per-word stats
word_stats = {}  # word -> {total_px, our_colors: {rgb: count}, jz_colors: {rgb: count}, mismatches}

cs = [PASTEL_PALETTE[3]] * 4  # all pastel tan
cs_idx = 0

for row in range(12):
    for col in range(20):
        w = grid[row][col]
        card, fg, is_gram, fg_trans, advance = decode_new(w)
        cs_idx = (cs_idx + advance) % 4
        bg = cs[cs_idx]
        fg_rgb = PALETTE.get(fg, (255,0,255))
        
        # Render card
        if is_gram:
            card_idx = card & 0x3F
            base = 0x3800 + card_idx * 8
            card_bytes = bytes(gram_mem.get(base+r, 0) & 0xFF for r in range(8))
        else:
            card_idx = card & 0xFF
            base = card_idx * 8
            card_bytes = grom[base:base+8] if base+8 <= len(grom) else bytes(8)
        
        if w not in word_stats:
            word_stats[w] = {'total_px': 0, 'our_cols': {}, 'jz_cols': {}, 'matches': 0,
                           'card': card, 'fg': fg, 'is_gram': is_gram, 'fg_trans': fg_trans,
                           'advance': advance, 'card_bytes': list(card_bytes)}
        
        ws = word_stats[w]
        for y in range(8):
            b = card_bytes[y]
            for x in range(8):
                bit = (b >> (7-x)) & 1
                is_bg_pixel = (bit == 0)
                if is_bg_pixel or fg_trans:
                    our_rgb = bg
                else:
                    our_rgb = fg_rgb
                
                jz_idx = jz_px[left + col*8 + x, top + row*8 + y]
                jz_rgb_val = jz_rgb(jz_idx)
                
                ws['our_cols'][our_rgb] = ws['our_cols'].get(our_rgb, 0) + 1
                ws['jz_cols'][jz_rgb_val] = ws['jz_cols'].get(jz_rgb_val, 0) + 1
                if our_rgb == jz_rgb_val:
                    ws['matches'] += 1
                ws['total_px'] += 1

# Display results
print("=== Per-word analysis (FG bits 13/14/15, fg=0 transparent, CS=all PASTEL[3]) ===")
print()
print(f"{'Word':>6} {'Card':>4} {'FG':>2} {'Adv':>3} {'Gram':>4} {'Match%':>7} {'Total':>6} {'Our colors':>30} {'Jz colors':>30}")
print("-" * 130)

for w, ws in sorted(word_stats.items(), key=lambda x: x[1]['matches'] / max(x[1]['total_px'], 1)):
    pct = 100.0 * ws['matches'] / ws['total_px'] if ws['total_px'] > 0 else 0
    
    def fmt_colors(col_dict):
        parts = []
        for rgb, n in sorted(col_dict.items(), key=lambda x: -x[1])[:3]:
            name = ''
            for d, lbl in [(PALETTE, 'PAL'), (PASTEL_PALETTE, 'PAS')]:
                for k, v in d.items():
                    if v == rgb:
                        name = f'{lbl}[{k}]'
                        break
            parts.append(f'{name or str(rgb)}:{n}')
        return ', '.join(parts)
    
    our_str = fmt_colors(ws['our_cols'])
    jz_str = fmt_colors(ws['jz_cols'])
    
    gram_str = 'GRAM' if ws['is_gram'] else 'grom'
    print(f"0x{w:04X} {ws['card']:4d} {ws['fg']:2d} {ws['advance']:3d} {gram_str:>4} {pct:6.1f}% {ws['total_px']:6d} {our_str:30s} {jz_str:30s}")

# Summary
print()
print("=== Summary ===")
total_match = sum(ws['matches'] for ws in word_stats.values())
total_px = sum(ws['total_px'] for ws in word_stats.values())
print(f"Overall: {total_match}/{total_px} = {100.0*total_match/total_px:.1f}%")

# Now for each mismatched word, analyze what FG value WOULD produce the jzIntv colors
print()
print("=== What FG values would match jzIntv? ===")
for w, ws in sorted(word_stats.items(), key=lambda x: x[1]['matches'] / max(x[1]['total_px'], 1)):
    if ws['matches'] == ws['total_px']:
        continue  # skip perfect matches
    
    card_bytes = bytes(ws['card_bytes'])
    best_fg = None
    best_match = 0
    
    for test_fg in range(16):  # 0-7 primary, 8-15 pastel
        test_matches = 0
        for y in range(8):
            b = card_bytes[y]
            for x in range(8):
                bit = (b >> (7-x)) & 1
                jz_idx = jz_px[left + (ws.get('_sample_col', 0))*8 + x, 
                               top + (ws.get('_sample_row', 0))*8 + y]  # won't work for aggregate
                # Can't do per-position jzIntv lookup from aggregate stats
                pass
    
    # Alternative: analyze by checking what color scheme jzIntv uses for each pixel type
    # within this word. The key question: for card bit=0 pixels, what color does jzIntv show?
    # For card bit=1 pixels, what color does jzIntv show?
    
    # We need to sample one actual tile position for this word
    # Find first position of this word
    found_row = found_col = None
    for row in range(12):
        for col in range(20):
            if grid[row][col] == w:
                found_row, found_col = row, col
                break
        if found_row is not None:
            break
    
    if found_row is None:
        continue
    
    # Now do per-pixel analysis at this position
    cs_idx2 = 0
    for rr in range(12):
        for cc in range(20):
            w2 = grid[rr][cc]
            _, _, _, _, adv = decode_new(w2)
            cs_idx2 = (cs_idx2 + adv) % 4
            if rr == found_row and cc == found_col:
                break
    
    bg2 = cs[cs_idx2]
    
    # Test different fg values
    best_fg = None
    best_match = 0
    
    for test_fg in range(8):
        test_matches = 0
        test_fg_rgb = PALETTE.get(test_fg, (255,0,255))
        for y in range(8):
            b = card_bytes[y]
            for x in range(8):
                bit = (b >> (7-x)) & 1
                jz_idx = jz_px[left + found_col*8 + x, top + found_row*8 + y]
                jz_val = jz_rgb(jz_idx)
                
                if bit == 0:
                    our_val = bg2  # card bg = CS bg
                else:
                    if test_fg == 0:
                        our_val = bg2  # fg=0 transparent
                    else:
                        our_val = test_fg_rgb
                
                if our_val == jz_val:
                    test_matches += 1
        
        if test_matches > best_match:
            best_match = test_matches
            best_fg = test_fg
    
    best_pct = 100.0 * best_match / 64
    card_str = f'card{ws["card"]}'
    print(f"  Word 0x{w:04X} ({card_str}, adv={ws['advance']}): best_fg={best_fg}, match={best_pct:.0f}% (current fg={ws['fg']}, {ws['matches']*100//ws['total_px']}%)")

PYEOF
