#!/usr/bin/env python3
"""
Launch jzintv with debugger, run to title screen (~3M cycles),
then capture STIC MOB registers and GRAM data.

The STIC registers at $0000-$0017 tell us which GRAM cards each
MOB (hardware sprite) uses:
  $00-$07: MOB 0-7 X positions
  $08-$0F: MOB 0-7 Y positions  
  $10-$17: MOB 0-7 A (attribute) registers
    - bits 0-7: card number (0-63)
    - bit 11: X-size (1 = double width)
    - bit 12: Y-size (1 = double height -> 16px)
    - bit 13: Y-flip
    - bit 14: X-flip
    - bit 15: GRAM flag (1 = GRAM, 0 = GROM)

We capture both the MOB registers and a full GRAM dump so we can
render the actual sprites.
"""
import subprocess
import time
import sys
import os

ROM_PATH = r"C:\Users\vrock\Documents\Swords and Serpents\Swords and Serpents.bin"
JZINTV_PATH = r"C:\Users\vrock\Documents\jzintv-20200712-win32-sdl2\jzintv-20200712-win32-sdl2\bin\jzintv.exe"
OUTPUT_FILE = "traces/title_mob_capture.txt"

# Commands to send to jzintv debugger
# Run 3M cycles to reach title screen
# Then read MOB registers and GRAM
DEBUG_COMMANDS = [
    "r 3000000\n",      # Run ~3M cycles to hit title screen
    "m 0 20\n",         # Read STIC registers $00-$1F (MOB X, Y, A)
    "m 3800 200\n",     # Read GRAM $3800-$39FF (256 words = 512 bytes = 64 cards)
    "q\n",              # Quit
]

print("Launching jzintv debugger...")
print(f"ROM: {ROM_PATH}")
print(f"Output: {OUTPUT_FILE}")

proc = subprocess.Popen(
    [JZINTV_PATH, "-d", ROM_PATH],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
)

output_lines = []
start_time = time.time()
READ_TIMEOUT = 120  # 2 minutes total

def read_available():
    """Read whatever stdout data is available (non-blocking via small timeout)"""
    import select
    import sys as _sys
    data = ""
    while True:
        if _sys.platform == 'win32':
            # Windows doesn't support select on pipes well
            # Use a different approach
            try:
                # On Windows with text mode, we can't do non-blocking easily
                # Just read line by line with a short timeout approach
                return data  # rely on send_commands loop instead
            except:
                return data
        else:
            ready, _, _ = select.select([proc.stdout], [], [], 0.1)
            if not ready:
                break
            char = proc.stdout.read(1)
            if not char:
                break
            data += char
    return data

# Wait for initial debugger prompt
print("Waiting for debugger initialization...")
initial_output = ""
while time.time() - start_time < 30:
    try:
        line = proc.stdout.readline()
        if not line:
            time.sleep(0.5)
            continue
        initial_output += line
        output_lines.append(line.rstrip())
        # The debugger typically shows "Starting jzIntv..." and then
        # a register dump with "R0=...". When we see register dump, it's ready.
        if "R0=" in line or "PC=" in line:
            print("Debugger ready!")
            break
    except Exception as e:
        print(f"Read error: {e}")
        time.sleep(0.5)

print(f"Initial output ({len(initial_output)} chars):")
print(initial_output[-500:])

# Send commands with pauses between them
for i, cmd in enumerate(DEBUG_COMMANDS):
    cmd_stripped = cmd.strip()
    print(f"\n--- Sending command [{i+1}/{len(DEBUG_COMMANDS)}]: {cmd_stripped} ---")
    
    proc.stdin.write(cmd)
    proc.stdin.flush()
    
    # Wait and read output for this command
    cmd_start = time.time()
    cmd_output = ""
    
    # For "r 3000000", we need to wait much longer
    timeout = 60 if cmd.startswith("r ") else 15
    
    while time.time() - cmd_start < timeout:
        try:
            line = proc.stdout.readline()
            if not line:
                time.sleep(0.1)
                # Check if process is still alive
                if proc.poll() is not None:
                    print("Process terminated!")
                    break
                continue
            
            cmd_output += line
            output_lines.append(line.rstrip())
            
            # If we see a prompt-like pattern, command is done
            if ">" in line and len(line.strip()) < 80:
                # This might be a new debug prompt
                if any(reg in line for reg in ["R0=", "R1=", "R2="]):
                    # Still in register dump, keep reading
                    pass
                elif line.strip().startswith(">"):
                    break
        except Exception as e:
            print(f"Read error during command: {e}")
            break
    
    # Print a summary of what we got
    print(f"  Got {len(cmd_output)} chars of output")
    if cmd_output:
        # Show last few lines
        lines = cmd_output.strip().split('\n')
        for l in lines[-10:]:
            print(f"  | {l.rstrip()[:120]}")

# Try to read any remaining output
try:
    remaining = proc.stdout.read()
    if remaining:
        output_lines.append(remaining)
        print(f"\nRemaining output: {len(remaining)} chars")
except:
    pass

# Save all output
os.makedirs("traces", exist_ok=True)
with open(OUTPUT_FILE, 'w') as f:
    f.write('\n'.join(output_lines))

print(f"\nSaved {len(output_lines)} lines to {OUTPUT_FILE}")

# Clean up
try:
    proc.terminate()
    proc.wait(timeout=5)
except:
    proc.kill()

print("Done!")
