"""
Test 2: Capture screenshot at VBlank boundary for a complete frame.
Sets a breakpoint at VBlank ISR entry ($5F60) so we capture a fully-drawn frame.
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

# Strategy: 
# 1. Boot past title screen (8M cycles)
# 2. Set breakpoint at VBlank ISR ($5F60) — fires at start of each frame
# 3. Run until breakpoint hits
# 4. Take screenshot (frame is complete at VBlank start)
# 5. Dump memory
script = """\
; Boot patches
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
; Run past boot
r 8000000
; Set breakpoint at VBlank ISR entry ($5F60)
b 5F60
; Run until VBlank (complete frame drawn)
r 2000000
; Take screenshot at known frame boundary
vs
; Remove breakpoint
n 5F60
; Dump memory
m 0200 240
m 3800 512
m 0000 32
m 0300 96
m 0100 256
q
"""

script_path = os.path.join(PROJECT_DIR, "test_screenshot2.txt")
with open(script_path, 'w') as f:
    f.write(script)

# Remove existing screenshots
for i in range(10):
    for prefix in ['shot', 'shot0']:
        shot_path = os.path.join(PROJECT_DIR, f"shot{i:04d}.gif")
        if os.path.exists(shot_path):
            os.remove(shot_path)

out_path = os.path.join(PROJECT_DIR, "test_screenshot2_out.txt")
cmd = [JZINTV, "-d", f"--script={script_path}", "-e", EXEC_PATH, "-g", GROM_PATH, ROM_PATH]

print(f"Running jzIntv with VBlank breakpoint...")
with open(out_path, 'w', encoding='utf-8', errors='replace') as out_f:
    proc = subprocess.Popen(cmd, stdout=out_f, stderr=subprocess.STDOUT, env=SDL_ENV, cwd=PROJECT_DIR)
    try:
        proc.wait(timeout=180)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        print("TIMEOUT")

# Check screenshots
print("\n=== Screenshots ===")
for i in range(10):
    shot_path = os.path.join(PROJECT_DIR, f"shot{i:04d}.gif")
    if os.path.exists(shot_path):
        size = os.path.getsize(shot_path)
        from PIL import Image
        img = Image.open(shot_path)
        pal = img.getpalette()
        print(f"  shot{i:04d}.gif: {size} bytes, {img.size[0]}x{img.size[1]}")
        # Show active colors
        active = {}
        for y in range(img.height):
            for x in range(img.width):
                idx = img.getpixel((x,y))
                pal_color = (pal[idx*3], pal[idx*3+1], pal[idx*3+2])
                active[pal_color] = active.get(pal_color, 0) + 1
        for c, n in sorted(active.items(), key=lambda x: -x[1])[:8]:
            print(f"    {c}: {n} px")
