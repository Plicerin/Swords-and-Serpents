"""Extract critical disassembly sections for room rendering analysis."""
import os

ASM_PATH = 'asm/disassembly.asm'
OUTPUT_DIR = 'room_analysis'
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(ASM_PATH, 'r') as f:
    lines = f.readlines()

# Find labels
labels = {}
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith('L_') and ':' in stripped:
        label = stripped.split(':')[0]
        labels[label] = i

print('Found labels:', sorted(labels.keys())[:30], '...')

# Extract sections
SECTIONS = [
    ('L_59FF', 'L_5A27', 'L_59FF_room_setup'),
    ('L_5A27', 'L_5E00', 'L_5A27_to_5E00'),
    ('L_5E00', 'L_5E48', 'L_5E00_helper'),
    ('L_5E48', 'L_5EC7', 'L_5E48_helper'),
    ('L_5EC7', 'L_5EE2', 'L_5EC7_helper'),
    ('L_5EE2', 'L_5F35', 'L_5EE2_room_render'),
    ('L_5F35', 'L_5F43', 'L_5F35_helper'),
    ('L_5F43', 'L_5F5B', 'L_5F43_helper'),
    ('L_5F5B', 'L_5FC1', 'L_5F5B_helper'),
    ('L_5FC1', 'L_6000', 'L_5FC1_helper'),
    ('L_55BF', 'L_5627', 'L_55BF_title_setup'),
]

for start_label, end_label, out_name in SECTIONS:
    start_line = labels.get(start_label)
    end_line = labels.get(end_label)
    if start_line is None:
        print(f'SKIP {start_label}: not found')
        continue
    if end_line is None:
        # Try to find next label after start_line
        end_line = len(lines)
        for lbl, ln in sorted(labels.items(), key=lambda x: x[1]):
            if ln > start_line:
                end_line = ln
                break
    
    out_path = os.path.join(OUTPUT_DIR, f'{out_name}.asm')
    with open(out_path, 'w') as f:
        for i in range(start_line, min(end_line, len(lines))):
            f.write(lines[i])
    print(f'Wrote {out_path}: {end_line - start_line} lines')

# Also extract data at $65B7-$66FF and $5972-$59CF (room name table)
with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

# Dump room-related ROM regions
REGIONS = [
    (0x15B7, 0x16FF, 'room_data_65B7'),
    (0x5972 - 0x5000, 0x59CF - 0x5000, 'room_name_table'),
]

for start, end, name in REGIONS:
    out_path = os.path.join(OUTPUT_DIR, f'{name}.hex')
    with open(out_path, 'w') as f:
        for addr in range(start, end, 16):
            data = rom[addr:addr+16]
            hex_str = ' '.join(f'{b:02X}' for b in data)
            f.write(f'0x{addr+0x5000:04X}: {hex_str}\n')
    print(f'Wrote {out_path}: {end-start} bytes')

print('Done.')
