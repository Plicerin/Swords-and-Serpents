import subprocess
import os
import re

PROJECT_DIR = '.'
JZINTV = os.path.join('jzintv-20200712-win32-sdl2', 'bin', 'jzintv.exe')
ROM_PATH = 'Swords and Serpents.bin'
OUT_DIR = os.path.join('traces', 'rooms')
os.makedirs(OUT_DIR, exist_ok=True)

# Create debugger script that:
# 1. Boots game
# 2. Patches title screen idle loop
# 3. Sets 1-player mode
# 4. Runs main loop for many cycles
# 5. Dumps scratchpad and key memory areas

script_lines = [
    '; Dump scratchpad and key memory after title screen bypass',
    # Patch title screen idle loop ($506A-$506E) to NOPs
    'p 506A 0034', 'p 506B 0034', 'p 506C 0034', 'p 506D 0034', 'p 506E 0034',
    # Also patch the game-over/re-entry loop at $5318-$531C
    'p 5318 0034', 'p 5319 0034', 'p 531A 0034', 'p 531B 02B8', 'p 531C 0001',
    # Patch status screen idle loop at $55C0-$55C2
    'p 55C0 0034', 'p 55C1 0034', 'p 55C2 0034',
    # Break after boot init at $5038
    'b 5038',
    # Run to breakpoint
    'r 8000000',
    # Set player count to 1-player
    'p 018C 0001',
    # Run for a very long time to let game flow execute
    'r 50000000',
    # Dump scratchpad RAM
    'm 0000 256',
    # Dump BACKTAB area
    'm 0200 240',
    # Dump GRAM area
    'm 3800 512',
    # Dump $0325-$035F area
    'm 0325 64',
    # Dump $0160-$017F area (G_0160 - G_017F)
    'm 0160 32',
    'q',
]

script_path = os.path.join(OUT_DIR, 'dump_scratchpad_script.txt')
with open(script_path, 'w') as f:
    f.write('\n'.join(script_lines) + '\n')

out_path = os.path.join(OUT_DIR, 'dump_scratchpad_out.txt')
cmd = [
    JZINTV,
    '-z', '1',  # 1x zoom for speed
    '-d', script_path,
    ROM_PATH,
]

print(f'Running jzIntv with scratchpad dump script...')
print(f'Command: {" ".join(cmd)}')
print()

try:
    result = subprocess.run(
        cmd,
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
    )
    with open(out_path, 'wb') as f:
        f.write(b'=== STDOUT ===\n')
        f.write(result.stdout)
        f.write(b'\n=== STDERR ===\n')
        f.write(result.stderr)
    print(f'Exit code: {result.returncode}')
    print(f'Output saved to {out_path} ({os.path.getsize(out_path)} bytes)')
except subprocess.TimeoutExpired:
    print('TIMEOUT: jzIntv took too long')
except Exception as e:
    print(f'ERROR: {e}')
