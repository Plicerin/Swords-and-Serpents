#!/usr/bin/env python3
"""Use jzIntv debugger to read memory at $65CE during gameplay and verify table contents."""
import os, subprocess, struct

# First: dump the file bytes directly to see what we expect
with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()

print("=== ROM file bytes at offset 0x15CE-0x15FE (CPU $65CE-$65FE) ===")
for row in range(4):
    offset = 0x15CE + row * 16
    hex_str = ' '.join(f'{b:02X}' for b in rom[offset:offset+16])
    print(f"  ${offset+0x5000:04X}: {hex_str}")

print()

# Read as 16-bit words (little-endian)
print("=== Words at $65CE (table entries 0-15) ===")
for i in range(16):
    off = 0x15CE + i*2
    w = struct.unpack_from('<H', rom, off)[0]
    print(f"  [{i:2d}] ${0x65CE+i*2:04X}: ${w:04X}")

print()

# Now: trace the table values as pointers
# Values > 0x5000 are ROM pointers. Values < 0x5000 might be something else.
print("=== Pointer destinations (if values are direct ROM addresses) ===")
for i in range(16):
    off = 0x15CE + i*2
    ptr = struct.unpack_from('<H', rom, off)[0]
    if ptr == 0:
        continue
    if ptr < 0x5000:
        print(f"  [{i:2d}] ${ptr:04X} -> BELOW ROM range (maybe offset/index?)")
    elif ptr <= 0x6FFF:
        file_off = ptr - 0x5000
        val = struct.unpack_from('<H', rom, file_off)[0]
        print(f"  [{i:2d}] ${ptr:04X} -> file ${file_off:04X}: first word = ${val:04X}")
    else:
        print(f"  [{i:2d}] ${ptr:04X} -> OUT OF RANGE")

print()

# What if these are offsets FROM the table base ($65CE)?
print("=== If values are OFFSETS from $65CE base ===")
for i in range(16):
    off = 0x15CE + i*2
    val = struct.unpack_from('<H', rom, off)[0]
    if val == 0:
        continue
    target = 0x65CE + val
    if 0x5000 <= target <= 0x6FFF:
        file_off = target - 0x5000
        target_val = struct.unpack_from('<H', rom, file_off)[0]
        print(f"  [{i:2d}] val=${val:04X} -> target ${target:04X}: first word = ${target_val:04X}")
    else:
        print(f"  [{i:2d}] val=${val:04X} -> target ${target:04X}: OUT OF RANGE")

print()

# What if the values are actually the TILE DATA themselves, not pointers?
# Looking at the trace: R0=4 (after ANDI #$000F) + entry at $65D2 gave R2=$6D86
# But $65D2 has word $0000 in the file... 
# Maybe jzIntv sees something different. Let's verify with the debugger.

# Create debugger script
script = '''b 5E68
r 12000000
; At breakpoint - read the full table
m 65CE 32
; Read a few words after the table start
m 65D0 4
; Check file offset 15CE area echo
m 65E0 16
q
'''

with open('traces/rooms/verify_mem2.txt', 'w') as f:
    f.write(script)

env = os.environ.copy()
env['SDL_VIDEODRIVER'] = 'dummy'
env['SDL_AUDIODRIVER'] = 'dummy'

cmd = [
    'jzintv-20200712-win32-sdl2/bin/jzintv.exe', '-d',
    '--script=traces/rooms/verify_mem2.txt',
    '-e', 'exec.bin', '-g', 'grom.bin',
    'Swords and Serpents.bin'
]

print("=== Running jzIntv to verify memory... ===")
with open('traces/rooms/verify_mem2_out.txt', 'w', errors='replace') as f:
    proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, env=env)
    try:
        proc.wait(timeout=40)
    except subprocess.TimeoutExpired:
        proc.kill()
        print('Timed out after 40s')

# Read and print the output
print("\n=== jzIntv output ===")
with open('traces/rooms/verify_mem2_out.txt', 'r', errors='replace') as f:
    for line in f:
        if '>' not in line or 'm ' in line or line.startswith('  '):
            print(line.rstrip())

print("\nDone.")
