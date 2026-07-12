#!/usr/bin/env python3
"""Simple jzintv debugger interaction - uses -z1 terminal mode + subprocess stdin."""
import subprocess, time, sys, os

ROM = r"C:\Users\vrock\Documents\Swords and Serpents\Swords and Serpents.bin"
JZINTV = r"C:\Users\vrock\Documents\jzintv-20200712-win32-sdl2\jzintv-20200712-win32-sdl2\bin\jzintv.exe"

# Commands: run 3M cycles, dump MOB regs, dump GRAM, quit
cmds = ["r 3000000", "m 0 40", "m 3800 200", "q"]
cmd_str = "\n".join(cmds) + "\n"

print("Starting jzintv -d -z1...")
proc = subprocess.Popen(
    [JZINTV, "-d", "-z1", ROM],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
)

# Send all commands at once
proc.stdin.write(cmd_str)
proc.stdin.flush()

# Read output with timeout
output = ""
start = time.time()
while time.time() - start < 120:
    try:
        line = proc.stdout.readline()
        if not line:
            if proc.poll() is not None:
                break
            time.sleep(0.1)
            continue
        output += line
    except:
        break

# Save
os.makedirs("traces", exist_ok=True)
with open("traces/title_mob_out2.txt", "w") as f:
    f.write(output)

print(f"Captured {len(output)} chars to traces/title_mob_out2.txt")
print(f"Last 500 chars:\n{output[-500:]}")

try:
    proc.terminate()
except:
    pass
