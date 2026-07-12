"""
Quick test: Does jzIntv 'vs' screenshot command work in headless SDL mode?
"""
import os
import subprocess
import sys

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
JZINTV = os.path.join(PROJECT_DIR, "jzintv-20200712-win32-sdl2", "bin", "jzintv.exe")
ROM_PATH = os.path.join(PROJECT_DIR, "Swords and Serpents.bin")
GROM_PATH = os.path.join(PROJECT_DIR, "grom.bin")
EXEC_PATH = os.path.join(PROJECT_DIR, "exec.bin")

SDL_ENV = os.environ.copy()
SDL_ENV["SDL_VIDEODRIVER"] = "dummy"
SDL_ENV["SDL_AUDIODRIVER"] = "dummy"

# Create a test script: boot, run 1M cycles, take screenshot, quit
script = """\
; Test screenshot in headless mode
p 506A 0034
p 506B 0034
p 506C 0034
p 506D 0034
p 506E 0034
p 5318 0034
p 5319 0034
p 531A 0034
p 531B 02B8
p 531C 0001
p 56CC 0034
p 56CD 0034
p 5638 0034
p 5639 0034
; Patch G_02F4 for room 0
p 55C5 DC
p 55C6 65
; Force past title screen
w 018C 0001
; Run enough cycles to render room
r 8000000
; Take screenshot
vs
; Dump some memory to verify we're in-game
m 0200 10
; Quit
q
"""

script_path = os.path.join(PROJECT_DIR, "test_screenshot.txt")
with open(script_path, 'w') as f:
    f.write(script)

# Remove any existing screenshots to see fresh ones
for i in range(10):
    shot_path = os.path.join(PROJECT_DIR, f"shot{i:04d}.gif")
    if os.path.exists(shot_path):
        os.remove(shot_path)
        print(f"Removed existing: shot{i:04d}.gif")

# Run jzIntv
out_path = os.path.join(PROJECT_DIR, "test_screenshot_out.txt")
cmd = [
    JZINTV, "-d",
    f"--script={script_path}",
    "-e", EXEC_PATH,
    "-g", GROM_PATH,
    ROM_PATH,
]

print(f"Running: {' '.join(cmd)}")
print()
with open(out_path, 'w', encoding='utf-8', errors='replace') as out_f:
    proc = subprocess.Popen(
        cmd,
        stdout=out_f,
        stderr=subprocess.STDOUT,
        env=SDL_ENV,
        cwd=PROJECT_DIR,
    )
    try:
        proc.wait(timeout=120)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        print("TIMEOUT after 120s")

# Check for screenshots
print()
print("=== Screenshots created ===")
found = False
for i in range(10):
    shot_path = os.path.join(PROJECT_DIR, f"shot{i:04d}.gif")
    if os.path.exists(shot_path):
        size = os.path.getsize(shot_path)
        print(f"  shot{i:04d}.gif: {size} bytes")
        found = True

if not found:
    print("  NO screenshots found!")
    # Check bin directory too
    for i in range(10):
        shot_path = os.path.join(PROJECT_DIR, "jzintv-20200712-win32-sdl2", "bin", f"shot{i:04d}.gif")
        if os.path.exists(shot_path):
            size = os.path.getsize(shot_path)
            print(f"  bin/shot{i:04d}.gif: {size} bytes")

# Show output preview
print()
print("=== Output preview ===")
with open(out_path, 'r', errors='replace') as f:
    content = f.read()
    # Show last 20 lines
    lines = content.split('\n')
    for line in lines[-30:]:
        print(line)
