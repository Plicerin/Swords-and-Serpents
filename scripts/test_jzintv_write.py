"""Test: find the correct jzIntv debugger command to write to RAM."""
import os, sys, subprocess

PROJECT_DIR = r"C:\Users\vrock\Documents\Swords and Serpents"
os.chdir(PROJECT_DIR)

SDL_ENV = {**os.environ, 'SDL_VIDEODRIVER': 'dummy', 'SDL_AUDIODRIVER': 'dummy'}
JZINTV = r"C:\Users\vrock\Downloads\jzintv-20250221-win32\bin\jzintv.exe"
EXEC_PATH = os.path.join(PROJECT_DIR, "exec.bin")
GROM_PATH = os.path.join(PROJECT_DIR, "grom.bin")
ROM_PATH = os.path.join(PROJECT_DIR, "Swords and Serpents.bin")

# Test different write commands
# Test 1: Try "m 019C 0042" — does m support writing?
# Test 2: Try writing via register: set R0, then use existing code
# Test 3: Is there a "poke" or "set" command?

script_lines = [
    # Standard idle patches
    "p 506A 0034", "p 506B 0034", "p 506C 0034", "p 506D 0034", "p 506E 0034",
    "p 5318 0034", "p 5319 0034", "p 531A 0034", "p 531B 02B8", "p 531C 0001",
    "p 56CC 0034", "p 56CD 0034",
    "p 5638 0034", "p 5639 0034",
    # NOP CLRR+MVO at 55C0-55C2  
    "p 55C0 0034", "p 55C1 0034", "p 55C2 0034",
    # Patch G_02F4 for room 1
    "p 55C5 00E4", "p 55C6 0065",
    # Break after X_FILL_ZERO
    "b 5038",
    "r 8000000",
    # --- TEST MEMORY WRITE APPROACHES ---
    # Approach A: Does "m <addr> <val>" write memory?
    "m 019C 0001",       # Try writing to 019C via m command
    
    # Approach B: Let's also try using a register set then drop a NOP
    # First, read what's at 019C now (after X_FILL_ZERO, should be 0)
    "b 55BF",             # break at L_55BF entry
    "r 8000000",
    # Dump scratchpad to see 019C
    "m 0100 240",         # dump scratchpad (0100-01EF)
    "q",
]

script_path = os.path.join(PROJECT_DIR, "traces", "_test_write.txt")
with open(script_path, 'w') as f:
    f.write('\n'.join(script_lines))

output_path = os.path.join(PROJECT_DIR, "traces", "_test_write_out.txt")

print("Running jzIntv write test...")
with open(output_path, 'w', encoding='utf-8', errors='replace') as out_f:
    proc = subprocess.Popen(
        [JZINTV, '-d', f'--script={script_path}',
         '-e', EXEC_PATH, '-g', GROM_PATH, ROM_PATH],
        stdout=out_f, stderr=subprocess.STDOUT,
        env=SDL_ENV, cwd=PROJECT_DIR,
    )
    try:
        proc.wait(timeout=120)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()

with open(output_path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Show relevant sections
print("\n=== Output excerpt ===")
for i, line in enumerate(content.split('\n')):
    if any(kw in line.lower() for kw in ['019c', 'm 01', 'm 01', 'breakpoint', '55bf', 'write', 'watching', 'now watching']):
        print(f"  {line.strip()[:150]}")
