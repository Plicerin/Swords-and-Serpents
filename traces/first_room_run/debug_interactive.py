import subprocess
import time
import re

rom_path = r"C:\Users\vrock\Documents\Swords and Serpents\Swords and Serpents.bin"
jzintv_path = r"C:\Users\vrock\Documents\jzintv-20200712-win32-sdl2\jzintv-20200712-win32-sdl2\bin\jzintv.exe"

# Commands to run jzIntv, set a breakpoint at the warrior's GRAM write, and dump registers
# We'll break at 524A (MVO@ R0, R5 - the first write to GRAM)
cmds = [
    "b 5249\n",  # Break on the first MVO@ inside L_520A's copy block
    "r 100000\n", # Run for 100,000 cycles (should hit BP for dungeon)
    "r 100000\n", # Run again
    "r 100000\n",
    "r 100000\n",
    "q\n"
]

proc = subprocess.Popen(
    [jzintv_path, "-d", rom_path],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

# Wait for jzIntv to initialize and reach the debug prompt
print("Waiting for jzIntv to start...")
output = ""
start_time = time.time()

# Read until we see the initial PC state or a timeout
while "1000" not in output:
    try:
        char = proc.stdout.read(1)
        if not char:
            break
        output += char
    except Exception:
        break
    if time.time() - start_time > 30:
        break

print("Initial output:")
print(output[-500:])

# Send commands one by one
for cmd in cmds:
    proc.stdin.write(cmd)
    proc.stdin.flush()
    time.sleep(2)  # Give it time to execute
    
    # Read output for this command
    chunk = ""
    start = time.time()
    while time.time() - start < 60:
        # Non-blocking read would be better, but let's just timed-read
        try:
            line = proc.stdout.readline()
            if not line:
                break
            chunk += line
        except Exception:
            break
    
    print(f"--- After command: {cmd.strip()} ---")
    print(chunk[-2000:])

# Final cleanup
proc.terminate()
print("Done")
