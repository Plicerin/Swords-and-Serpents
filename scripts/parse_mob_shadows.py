import re
from collections import defaultdict

with open('traces/debug/sprite_extended_out.txt', 'r', encoding='utf-8', errors='replace') as f:
    text = f.read()

# Parse memory dumps. Format: "0320:  0000  0000  0000  0000 ... # comment"
# Each line starts with a 4-digit hex address followed by hex words.

dumps = {}
current_lines = []
current_addr = None

for line in text.split('\n'):
    line = line.rstrip()
    if not line:
        continue
    # Skip debugger command lines and breakpoints
    if line.startswith('>') or 'breakpoint' in line.lower() or 'Hit' in line:
        continue
    m = re.match(r'^([0-9A-F]{4}):\s+(.*)', line)
    if m:
        addr = int(m.group(1), 16)
        current_addr = addr
        current_lines = [line]
        dumps[addr] = current_lines
    elif current_addr is not None and line.startswith('  '):
        # Continuation line (more words for same block)
        dumps[current_addr].append(line)

# Decode MOB state from the dumps
# MOB shadow layout ($0320-$035F):
#   $0320-$032F: X (even) and Y (odd) words for 8 MOBs
#   $0330-$0337: Attributes (color, etc.)
#   $0338-$033F: State pointer or other data
#   $0340-$0347: Collision/interaction data
#   $0348-$034F: Unknown
#   $0350-$0357: GRAM card index or sprite pointer
#   $0358-$035F: State pointer / function pointer

def get_words_at(addr, count):
    # Find the dump line whose base address covers 'addr'
    # Each dump line has 8 words = 8 addresses
    base = None
    for a in sorted(dumps.keys()):
        if a <= addr < a + 8:
            base = a
            break
    if base is None:
        return []
    full = ' '.join(dumps[base])
    words = re.findall(r'\b([0-9A-F]{4})\b', full)
    idx = addr - base
    if idx >= len(words):
        return []
    return [int(words[idx], 16)]

print("=" * 60)
print("MOB SHADOW STATE DECODE")
print("=" * 60)

for mob in range(8):
    x_addr = 0x320 + mob * 2
    y_addr = x_addr + 1
    attr_addr = 0x330 + mob
    state_addr = 0x338 + mob
    coll_addr = 0x340 + mob
    card_addr = 0x350 + mob
    fn_addr = 0x358 + mob

    x_words = get_words_at(x_addr, 1)
    y_words = get_words_at(y_addr, 1)
    attr_words = get_words_at(attr_addr, 1)
    state_words = get_words_at(state_addr, 1)
    coll_words = get_words_at(coll_addr, 1)
    card_words = get_words_at(card_addr, 1)
    fn_words = get_words_at(fn_addr, 1)

    x_val = x_words[0] if x_words else 0
    y_val = y_words[0] if y_words else 0
    attr = attr_words[0] if attr_words else 0
    state = state_words[0] if state_words else 0
    coll = coll_words[0] if coll_words else 0
    card = card_words[0] if card_words else 0
    fn = fn_words[0] if fn_words else 0

    visible = (x_val & 0x0100) != 0
    x_pos = (x_val >> 8) & 0xFF
    y_pos = (y_val >> 8) & 0xFF

    print(f"\nMOB {mob}:")
    print(f"  X=${x_pos:02X} ({x_pos})  Y=${y_pos:02X} ({y_pos})  VISIBLE={'YES' if visible else 'no'}")
    print(f"  attr=${attr:04X}  state=${state:04X}  coll=${coll:04X}")
    print(f"  card=${card:04X}  fn=${fn:04X}")

# Also show raw hex for the key blocks
print("\n" + "=" * 60)
print("RAW MEMORY DUMPS")
print("=" * 60)
for addr in sorted(dumps.keys()):
    if 0x320 <= addr <= 0x35F:
        full = ' '.join(dumps[addr])
        words = re.findall(r'\b([0-9A-F]{4})\b', full)
        hex_str = ' '.join(words[:16])
        print(f"${addr:04X}: {hex_str}")
