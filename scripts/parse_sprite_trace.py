import re
from collections import defaultdict

with open('traces/debug/sprite_extended_out.txt', 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

hits = []
i = 0
while i < len(lines):
    if 'Hit breakpoint at' in lines[i]:
        m = re.search(r'\$([0-9A-F]+)', lines[i], re.I)
        pc = m.group(1) if m else None
        if i+1 < len(lines):
            data_line = lines[i+1].strip()
            hex_words = re.findall(r'\b([0-9A-F]{4})\b', data_line)
            if len(hex_words) >= 8:
                try:
                    regs = [int(w, 16) for w in hex_words[:8]]
                    hits.append({
                        'pc': pc,
                        'r0': regs[0], 'r1': regs[1], 'r2': regs[2], 'r3': regs[3],
                        'r4': regs[4], 'r5': regs[5], 'r6': regs[6], 'r7': regs[7]
                    })
                except:
                    pass
        i += 2
    else:
        i += 1

print(f'Total breakpoint hits parsed: {len(hits)}')

# At $5249: MVI@ R4, R0 -- R4=source ROM addr, R0=data word
gram_writes = []
for idx, h in enumerate(hits):
    if h['pc'] == '5249':
        gram_writes.append({
            'hit': idx,
            'data': h['r0'],
            'rom_src': h['r4'],
            'r5': h['r5']
        })

print(f'Gram write breakpoint hits at $5249: {len(gram_writes)}')

print('\n--- First 20 writes ---')
for i, gw in enumerate(gram_writes[:20]):
    print(f'{i+1}: hit={gw["hit"]}, data=${gw["data"]:04X}, rom_src=${gw["rom_src"]:04X}, r5=${gw["r5"]:04X}')

print('\n--- Last 20 writes ---')
start_idx = len(gram_writes) - 20
for i, gw in enumerate(gram_writes[-20:]):
    print(f'{start_idx + i + 1}: hit={gw["hit"]}, data=${gw["data"]:04X}, rom_src=${gw["rom_src"]:04X}, r5=${gw["r5"]:04X}')
