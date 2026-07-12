"""
Trace JZINTV: Set breakpoint at L_5EC7 ($5EC7) to capture every BACKTAB word
written during room 0 rendering. Log R1 (word) and R4 (address).
Also dump BACKTAB before and after rendering.
"""
import subprocess
import time
import sys
import os

rom_path = r"C:\Users\vrock\Documents\Swords and Serpents\Swords and Serpents.bin"
jzintv_path = r"C:\Users\vrock\Documents\jzintv-20200712-win32-sdl2\jzintv-20200712-win32-sdl2\bin\jzintv.exe"

# Strategy:
# 1. Startup: run past title screen to game start
# 2. Set breakpoint at $5EE2 (render entry) - first time = title screen render
# 3. Continue to next $5EE2 hit = room 0 render (after selecting game)
# 4. Set breakpoint at $5EF9 (MVO@ R1, R4 - the actual BACKTAB write inside L_5EE2)
# 5. For each write, log R1 and R4
# 6. After $5EE2 returns (R4 >= $02EF), dump full BACKTAB

# Actually, simpler approach: break at $5EF9 where MVO@ R1, R4 writes to BACKTAB
# This is line 2686 in the disassembly: MVO@ R1, R4

script_file = os.path.join(os.path.dirname(__file__), "_jzintv_script.txt")

# JZINTV commands are sent via stdin
# b <addr> = set breakpoint
# r <cycles> = run for N cycles  
# n = step (next)
# m <addr> <count> = memory dump
# q = quit

# Approach: run until game enters room, then trace
# L_55BF sets up room params, calls L_5EE2
# We break at L_5EE2 ($5EE2), then set a breakpoint at the MVO@ inside L_5EF4 loop

# But we need the game to be past the title screen. 
# From the traces, after selecting game mode, L_557B is called which calls L_55BF → L_5EE2
# Let's break at L_557B ($557B) which is the room entry point

# Simpler: just run with breakpoint at $5EF9 and capture all writes
# Then filter for those during room 0 render (addresses $0200-$02EF, after game start)

cmds = [
    # First, let it initialize and run through boot
    f"r 600000\n",       # Run through boot sequence
    # Now we should be at title screen. Run more to get past it
    f"r 10000000\n",     # Run for ~10M cycles - should get past title to game
    # Now break at the BACKTAB write point  
    f"b 5EF9\n",         # Break at MVO@ R1, R4 (writes BACKTAB word)
    # Run and capture writes
    f"r 5000000\n",      # Run to capture rendering writes
    # Quit
    f"q\n"
]

print("Starting JZINTV with debugger...")
print(f"ROM: {rom_path}")
print(f"Commands will be sent to JZINTV stdin")

proc = subprocess.Popen(
    [jzintv_path, "-d", rom_path],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=0
)

# Collect all output
all_output = []
backtab_writes = []

print("Sending commands...")
for i, cmd in enumerate(cmds):
    print(f"\n[{i+1}/{len(cmds)}] Sending: {cmd.strip()}")
    proc.stdin.write(cmd)
    proc.stdin.flush()
    
    # Read output with timeout
    start = time.time()
    chunk = ""
    while time.time() - start < 30:
        try:
            line = proc.stdout.readline()
            if not line:
                time.sleep(0.1)
                continue
            chunk += line
            
            # Parse for register state at breakpoint
            # Look for lines like "R1=XXXX R4=XXXX" in the breakpoint output
            if "R1=" in line and "R4=" in line:
                # Extract register values
                parts = line.split()
                r1_val = None
                r4_val = None
                pc_val = None
                for p in parts:
                    if p.startswith("R1="):
                        r1_val = p.split("=")[1]
                    elif p.startswith("R4="):
                        r4_val = p.split("=")[1]
                    elif "CP-1610" in line:
                        pass
                if r1_val and r4_val:
                    try:
                        r1 = int(r1_val, 16)
                        r4 = int(r4_val, 16)
                        # Only log writes to BACKTAB range
                        if 0x0200 <= r4 <= 0x02EF:
                            backtab_writes.append((r4, r1))
                            print(f"  BT WRITE: addr=${r4:04X} word=${r1:04X} (card={(r1>>3)&0x1FF} GRAM={(r1>>11)&1} FG={r1&7})")
                    except:
                        pass
            
            # Check if we've completed
            if i >= len(cmds) - 1 and ("breakpoint" in line.lower() or "halted" in line.lower()):
                # We hit a breakpoint - send continue
                pass
                
        except Exception as e:
            print(f"  Read error: {e}")
            break
    
    all_output.append(chunk)
    print(f"  Got {len(chunk)} chars of output")
    if len(chunk) < 2000:
        print(chunk[-1000:])

print("\n\n=== SUMMARY ===")
print(f"Total BACKTAB writes captured: {len(backtab_writes)}")
print(f"Unique words: {len(set(w for _, w in backtab_writes))}")

# Show the unique words
unique_words = {}
for addr, word in backtab_writes:
    if word not in unique_words:
        unique_words[word] = []
    unique_words[word].append(addr)

print("\nUnique BACKTAB words written:")
for word in sorted(unique_words.keys()):
    addrs = unique_words[word]
    card = (word >> 3) & 0x1FF
    gram = (word >> 11) & 1
    fg = word & 7
    cs = (word >> 13) & 1
    src = 'GRAM' if gram else 'GROM'
    print(f"  ${word:04X}: card={card:3d} {src:4s} FG={fg} CS={cs} at {len(addrs)} positions: {addrs[:10]}{'...' if len(addrs) > 10 else ''}")

# Save full output
with open(os.path.join(os.path.dirname(__file__), "trace_l5ec7_output.txt"), "w") as f:
    f.write("".join(all_output))

proc.terminate()
print("\nDone.")
