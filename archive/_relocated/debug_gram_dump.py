from render_all_rooms import extract_gram_from_output
import os
import re

trace_path = r"C:\Users\vrock\Documents\Swords and Serpents\traces\rooms\render_room_0_out_0001.txt"
with open(trace_path, 'r', encoding='utf-8', errors='replace') as f:
    raw = f.read()

gram_text = extract_gram_from_output(raw)
# Manually parse the dump to find non-zero entries
lines = gram_text.split('\n')
for line in lines:
    m = re.match(r'^([0-9A-F]{4}):\s+(.*)', line.strip())
    if m:
        addr = int(m.group(1), 16)
        values = m.group(2).split()
        for v in values:
            # Strip trailing * or other non-hex characters
            clean_v = re.sub(r'[^0-9A-F]', '', v)
            if clean_v:
                val = int(clean_v, 16)
                if val != 0:
                    print(f"0x{addr:04X}: {val:04X}")

