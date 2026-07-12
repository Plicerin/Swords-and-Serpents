"""Test: use 'p' (patch) to write to scratchpad RAM $019C after X_FILL_ZERO."""
import os, sys, subprocess

PROJECT_DIR = r"C:\Users\vrock\Documents\Swords and Serpents"
os.chdir(PROJECT_DIR)

SDL_ENV = {**os.environ, 'SDL_VIDEODRIVER': 'dummy', 'SDL_AUDIODRIVER': 'dummy'}
JZINTV = os.path.join(PROJECT_DIR, "jzintv-20200712-win32-sdl2", "bin", "jzintv.exe")
EXEC_PATH = os.path.join(PROJECT_DIR, "exec.bin")
GROM_PATH = os.path.join(PROJECT_DIR, "grom.bin")
ROM_PATH = os.path.join(PROJECT_DIR, "Swords and Serpents.bin")

# Test 1: Use 'p' to write $019C after X_FILL_ZERO breakpoint
# Test 2: Also try 'p' on $018C
# Then dump scratchpad to verify values

script_lines = [
    "; Test: p command on RAM addresses after X_FILL_ZERO",
    "",
    "; Standard idle patches",
    "p 506A 0034", "p 506B 0034", "p 506C 0034", "p 506D 0034", "p 506E 0034",
    "p 5318 0034", "p 5319 0034", "p 531A 0034", "p 531B 02B8", "p 531C 0001",
    "p 56CC 0034", "p 56CD 0034",
    "p 5638 0034", "p 5639 0034",
    "; NOP CLRR+MVO G_019C at 55C0-55C2",
    "p 55C0 0034", "p 55C1 0034", "p 55C2 0034",
    "; Patch G_02F4 for room 1",
    "p 55C5 00E4", "p 55C6 0065",
    "",
    "; Break after X_FILL_ZERO returns to $5038",
    "b 5038",
    "r 8000000",
    "",
    "; --- NOW try 'p' on $019C and $018C after the zero-fill ---",
    "p 019C 0001",       # TEST: does 'p' write to scratchpad RAM?
    "p 018C 0001",       # TEST: does 'p' write to scratchpad RAM?
    "",
    "; Dump scratchpad $0100-$01EF to verify",
    "m 0100 240",
    "",
    "; Also dump System RAM to verify G_02F4",
    "m 02F0 16",
    "q",
]

script_path = os.path.join(PROJECT_DIR, "traces", "_test_patch_ram.txt")
with open(script_path, 'w') as f:
    f.write('\n'.join(script_lines))

output_path = os.path.join(PROJECT_DIR, "traces", "_test_patch_ram_out.txt")

print("Testing: 'p' command on scratchpad RAM addresses...")
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

# Show key sections
print("\n=== Lines around breakpoint and patches ===")
for i, line in enumerate(content.split('\n')):
    if any(kw in line for kw in ['p 019C', 'p 018C', 'breakpoint', 'Hit break', '5038', '0100:']):
        print(f"  [{i}] {line.strip()[:140]}")

print("\n=== Scratchpad $0100-$01EF dump ===")
lines = content.split('\n')
in_section = False
for i, line in enumerate(lines):
    if line.strip().startswith('0100:'):
        in_section = True
    if in_section:
        print(f"  {line.strip()}")
        if line.strip().startswith('01F0:') or line.strip().startswith('0200:'):
            break

# Specifically check $019C and $018C
print("\n=== Value at $019C and $018C ===")
import re
for i, line in enumerate(lines):
    m = re.match(r'^0190:\s+(.*)', line.strip())
    if m:
        parts = m.group(1).split()
        # Each part is a 4-digit hex word
        # $0190 -> word 0, $0191 -> word 1, ..., $019C -> word 12 (0x019C-0x0190=12)
        idx_019C = 0x019C - 0x0190
        idx_018C = 0x018C - 0x0180  # find $0180 line
        if idx_019C < len(parts):
            print(f"  G_019C ($019C): {parts[idx_019C]}")
        else:
            print(f"  G_019C not found on this line (need {idx_019C} words, have {len(parts)})")
    m2 = re.match(r'^0180:\s+(.*)', line.strip())
    if m2:
        parts = m2.group(1).split()
        idx_018C = 0x018C - 0x0180
        if idx_018C < len(parts):
            print(f"  G_018C ($018C): {parts[idx_018C]}")
