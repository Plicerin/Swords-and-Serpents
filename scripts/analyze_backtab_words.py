#!/usr/bin/env python3
"""Analyze all unique BACKTAB words across rooms 0-5 to diagnose mismatches."""
import sys, os, re
sys.path.insert(0, '.')
from render_all_rooms import decode_backtab_word, load_grom, get_grom_card_bytes, PASTEL_PALETTE, PALETTE

# Collect ALL unique BACKTAB words from all 6 rooms
all_words = set()
word_counts = {}
for room_idx in range(6):
    path = f'traces/_cmp_room_{room_idx}_out.txt'
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    # Parse BACKTAB manually
    lines = content.split('\n')
    for line in lines:
        stripped = line.strip()
        if re.match(r'^0200:', stripped):
            break
    else:
        continue
    
    # Collect words
    in_bt = False
    for line in lines:
        stripped = line.strip()
        m = re.match(r'^([0-9A-F]{4}):\s+(.*)', stripped)
        if m:
            addr = int(m.group(1), 16)
            if addr == 0x0200:
                in_bt = True
            elif addr >= 0x02F0:
                break
        if in_bt and m:
            vals = re.findall(r'([0-9A-F]{4})\*?', m.group(2))
            for v in vals:
                w = int(v, 16)
                all_words.add(w)
                word_counts[w] = word_counts.get(w, 0) + 1

print(f"Total unique BACKTAB words across all rooms: {len(all_words)}")
print(f"Total tiles across all rooms: {sum(word_counts.values())}")
print()

# For each unique word, show current decoding and card properties
print("=== All unique BACKTAB words ===")
print(f"{'Word':>6} {'Card':>5} {'GRAM':>5} {'FG':>3} {'Adv':>4} {'Count':>6} {'CardOnes':>9}")
print("-" * 50)

grom = load_grom()

for word in sorted(all_words):
    card, fg, bg_bits, is_gram, fg_transparent = decode_backtab_word(word)
    advance = (word >> 13) & 1
    
    # Get card ones count
    if is_gram:
        card_ones = '?'  # GRAM varies per room
    else:
        try:
            cbytes = get_grom_card_bytes(grom, card & 0xFF)
            card_ones = sum(bin(b).count('1') for b in cbytes)
        except:
            card_ones = '?'
    
    count = word_counts.get(word, 0)
    print(f"0x{word:04X} {card:5d} {'Y' if is_gram else 'N':>5} {fg:3d} {advance:4d} {count:6d} {str(card_ones):>9}")

print()

# KEY ANALYSIS: alternative FG bit assignment hypotheses
print("=" * 60)
print("TESTING ALTERNATIVE FG BIT ASSIGNMENTS")
print("=" * 60)

# Hypothesis 1: FG from bits 10-12 (instead of 15/14/12)
def fg_hypothesis_1(word):
    """FG from bits 10-12, card from bits 0-9 and 13+"""
    return (word >> 10) & 0x7

# Hypothesis 2: FG from bits 9-11 (EXEC-style)
def fg_hypothesis_2(word):
    """FG from bits 9-11"""
    return (word >> 9) & 0x7

# Hypothesis 3: FG = (bits 15,14,12) but card = bits 0-9 only
def fg_hypothesis_3(word):
    """Card = bits 0-9, FG = bits 15/14/12"""
    return ((word >> 13) & 0x6) | ((word >> 12) & 0x1)

# Hypothesis 4: Card includes higher bits, FG from lower bits
def fg_hypothesis_4(word):
    """FG from bits 0-2 = bg_bits (FG/BG mode)"""
    return word & 0x7

print("\nFloor tile 0x1603 under different hypotheses:")
word = 0x1603
print(f"  H0 (current, bits 15/14/12): fg={fg_hypothesis_3(word)}")
print(f"  H1 (bits 10-12): fg={fg_hypothesis_1(word)}")
print(f"  H2 (bits 9-11): fg={fg_hypothesis_2(word)}")
print(f"  H3 (bits 0-2): fg={fg_hypothesis_4(word)}")

print("\nAll unique words with non-zero FG under each hypothesis:")
for label, fn in [
    ("Current (15/14/12)", fg_hypothesis_3),
    ("H1 (10-12)", fg_hypothesis_1),
    ("H2 (9-11)", fg_hypothesis_2),
]:
    fg_counts = {}
    for word in sorted(all_words):
        fg = fn(word)
        fg_counts[fg] = fg_counts.get(fg, 0) + word_counts.get(word, 0)
    print(f"\n  {label}:")
    for fg_val, n in sorted(fg_counts.items()):
        pct = 100 * n / sum(word_counts.values())
        print(f"    fg={fg_val}: {n:5d} tiles ({pct:.1f}%)")

print()

# Check: for words where current FG=0 (wall tiles), what would alternative FG give?
print("=== Wall tiles (current FG=0): alternative FG values ===")
for word in sorted(all_words):
    card, fg, bg_bits, is_gram, fg_transparent = decode_backtab_word(word)
    if fg != 0:
        continue
    fg1 = fg_hypothesis_1(word)
    fg2 = fg_hypothesis_2(word)
    fg4 = fg_hypothesis_4(word)
    # Only show if alternative FG is interesting
    if fg1 != 0 or fg2 != 0:
        print(f"  0x{word:04X}: current_fg=0, H1_fg={fg1}, H2_fg={fg2}, H3_fg={fg4}, "
              f"card={card}, gram={is_gram}, count={word_counts.get(word,0)}")

print()

# Check: GRAM vs GROM card count for each word type
print("=== GRAM card analysis ===")
gram_cards = {}
for word in sorted(all_words):
    card, fg, bg_bits, is_gram, fg_transparent = decode_backtab_word(word)
    if is_gram:
        if card not in gram_cards:
            gram_cards[card] = {'words': [], 'count': 0}
        gram_cards[card]['words'].append(word)
        gram_cards[card]['count'] += word_counts.get(word, 0)

for card_idx in sorted(gram_cards.keys()):
    info = gram_cards[card_idx]
    print(f"  GRAM card {card_idx}: {info['count']} tiles")
    for w in info['words']:
        _, fg, _, _, _ = decode_backtab_word(w)
        print(f"    0x{w:04X} fg={fg} count={word_counts.get(w,0)}")
