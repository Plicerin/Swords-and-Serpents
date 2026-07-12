import re
from collections import defaultdict

with open('traces/debug/sprite_extended_out.txt', 'r', encoding='utf-8', errors='replace') as f:
    text = f.read()

# Build a flat memory map from ALL dump lines.
# Format: "0320:  0000  0000  0000  0000   0000  1B58  6B60  9A44"
# Each dump line gives 8 words for addresses base, base+1, ..., base+7
memory = {}  # addr -> word value (last write wins)

for line in text.split('\n'):
    line = line.rstrip()
    if not line:
        continue
    m = re.match(r'^([0-9A-F]{4}):\s+(.*)', line)
    if not m:
        continue
    base = int(m.group(1), 16)
    rest = m.group(2)
    # Remove comments (# ...)
    rest = rest.split('#')[0]
    words = re.findall(r'\b([0-9A-F]{4})\b', rest)
    for i, w in enumerate(words[:8]):
        memory[base + i] = int(w, 16)

print(f"Total memory words parsed: {len(memory)}")
print(f"Address range: ${min(memory.keys()):04X} - ${max(memory.keys()):04X}")

# MOB shadow layout
print("\n" + "=" * 70)
print("MOB SHADOW DECODE ($0320-$035F)")
print("=" * 70)

for mob in range(8):
    x_addr = 0x320 + mob * 2
    y_addr = x_addr + 1
    attr_addr = 0x330 + mob
    state_addr = 0x338 + mob
    coll_addr = 0x340 + mob
    # Some dumps may not have all addresses
    x_val = memory.get(x_addr, 0)
    y_val = memory.get(y_addr, 0)
    attr = memory.get(attr_addr, 0)
    state = memory.get(state_addr, 0)
    coll = memory.get(coll_addr, 0)
    
    # For $0350-$035F, this may be card info or other data
    card_addr = 0x350 + mob
    fn_addr = 0x358 + mob
    card = memory.get(card_addr, 0)
    fn = memory.get(fn_addr, 0)
    
    visible = (x_val & 0x0100) != 0
    x_pos = (x_val >> 8) & 0xFF
    y_pos = (y_val >> 8) & 0xFF
    
    # Determine if this MOB is "active" (non-zero position or visible)
    active = visible or x_pos != 0 or y_pos != 0 or state != 0
    status = "ACTIVE" if active else "inactive"
    
    print(f"\nMOB {mob} [{status}]:")
    print(f"  X=${x_pos:02X} ({x_pos:3d})  Y=${y_pos:02X} ({y_pos:3d})  VISIBLE={'YES' if visible else 'no'}")
    print(f"  attr=${attr:04X}  state_ptr=${state:04X}  coll=${coll:04X}")
    print(f"  card_raw=${card:04X}  fn_ptr=${fn:04X}")
    
    # Decode state pointer if it looks like a code address
    if 0x5000 <= state <= 0x6FFF:
        print(f"    -> state points to ROM code ${state:04X}")
    
    # Decode card index if in valid range
    card_idx = card & 0xFF
    if 0 <= card_idx <= 63:
        print(f"    -> card index = {card_idx} (GRAM ${0x3800 + card_idx*8:04X})")

# Show raw hex for key ranges
print("\n" + "=" * 70)
print("RAW HEX ($0320-$035F)")
print("=" * 70)
for base in range(0x320, 0x360, 8):
    words = [f"{memory.get(base+i, 0):04X}" for i in range(8)]
    print(f"${base:04X}: {'  '.join(words)}")
