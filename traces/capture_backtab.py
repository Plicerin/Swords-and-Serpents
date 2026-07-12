#!/usr/bin/env python3
"""JZINTV debugger script to capture BACKTAB and scratchpad RAM after room 0 rendering.
Set breakpoint at L_5F21 ($5F21) which is where L_5EE2 completes (BACKTAB fully written).
Also capture scratchpad at $0080-$01FF to see loaded room data."""
import subprocess, sys, time, os

rom = r'C:\Users\vrock\Documents\Swords and Serpents\Swords and Serpents.bin'
jz = r'C:\Users\vrock\Documents\jzintv-20200712-win32-sdl2\jzintv-20200712-win32-sdl2\bin\jzintv.exe'

if not os.path.exists(rom):
    print(f"ROM not found: {rom}")
    sys.exit(1)
if not os.path.exists(jz):
    print(f"JZINTV not found: {jz}")
    sys.exit(1)

# Strategy:
# 1. Run 50M cycles to get past boot/title into first room
# 2. Set breakpoint at $5F21 (end of L_5EE2, BACKTAB done)
# 3. When hit, dump BACKTAB and scratchpad
# 4. Continue a bit and dump again for comparison

commands = [
    'r 50000000\n',        # Run 50M cycles to get into game
    'b 5F21\n',            # Set breakpoint at end of L_5EE2
    'r 10000000\n',        # Run until breakpoint
    'm 0200 256\n',        # Dump BACKTAB ($0200-$02FF)
    'm 0080 128\n',        # Dump scratchpad area with room data ($0080-$00FF)
    'm 0100 128\n',        # Dump scratchpad ($0100-$017F)
    'm 0180 128\n',        # Dump scratchpad ($0180-$01FF)
    'r 1000000\n',         # Run a bit more
    'm 0200 256\n',        # Dump BACKTAB again
    'q\n'
]

print("Starting JZINTV debugger...")
p = subprocess.Popen(
    [jz, '-d', '-z1', rom],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

output_lines = []
for cmd in commands:
    print(f"Sending: {cmd.strip()}")
    try:
        p.stdin.write(cmd)
        p.stdin.flush()
    except:
        print("Failed to write command, process may have exited")
        break
    time.sleep(3)

# Read all remaining output
try:
    p.stdin.write('q\n')
    p.stdin.flush()
except:
    pass

time.sleep(2)
try:
    remaining = p.stdout.read()
    output_lines = remaining.split('\n')
except:
    pass

p.terminate()

# Save output
out_path = os.path.join(os.path.dirname(__file__), 'capture_backtab_out.txt')
with open(out_path, 'w') as f:
    f.write('\n'.join(output_lines[-500:]))  # Last 500 lines

print(f"\nOutput saved to {out_path}")
print(f"Total output lines: {len(output_lines)}")
# Print last 50 lines for verification
for line in output_lines[-50:]:
    print(line)
