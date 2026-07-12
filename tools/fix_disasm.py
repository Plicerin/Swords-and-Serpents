#!/usr/bin/env python3
"""Fix the disassembly: line 2555 should be MVII #$65CE, R4, not $00CE."""

with open('asm/disasm_new.asm', 'r') as f:
    lines = f.readlines()

# Find and fix line 2555
for i, line in enumerate(lines):
    if 'MVII    #$00CE, R4' in line:
        print(f"Line {i+1}: {line.rstrip()}")
        lines[i] = line.replace('#$00CE, R4', '#$65CE, R4')
        print(f"Fixed to: {lines[i].rstrip()}")
        break
else:
    print("NOT FOUND - searching more broadly...")
    for i, line in enumerate(lines):
        if '00CE' in line and 'R4' in line:
            print(f"Line {i+1}: {line.rstrip()}")

with open('asm/disasm_new.asm', 'w') as f:
    f.writelines(lines)

print("Done. File saved.")
