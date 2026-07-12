#!/usr/bin/env python3
"""Test whether jzIntv --gui-mode accepts debugger commands without -d."""
import subprocess
import time
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
JZINTV_EXE = PROJECT_ROOT / "jzintv-20200712-win32-sdl2" / "bin" / "jzintv.exe"
EXEC_BIN = PROJECT_ROOT / "exec.bin"
GROM_BIN = PROJECT_ROOT / "grom.bin"
GAME_ROM = PROJECT_ROOT / "Swords and Serpents.bin"

cmd = [
    str(JZINTV_EXE),
    "-d",
    "--gui-mode",
    "-e", str(EXEC_BIN),
    "-g", str(GROM_BIN),
    str(GAME_ROM),
]

print(f"Launching: {' '.join(cmd)}")
print("(Testing --gui-mode without -d)")
print()

proc = subprocess.Popen(
    cmd,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
    cwd=str(PROJECT_ROOT),
)

print("Waiting 5s for emulator to initialize...")
time.sleep(5)

print("Sending 'm 0200 16' command...")
try:
    proc.stdin.write("m 0200 16\n")
    proc.stdin.flush()
except BrokenPipeError:
    print("BROKEN PIPE — jzIntv exited.")
    out, _ = proc.communicate(timeout=2)
    print("STDOUT:")
    print(out[:2000])
    sys.exit(1)

print("Waiting 3s for response...")
time.sleep(3)

# Read available output (avoid select on Windows — use thread-based drain)
stdout_buffer = []

def drain():
    try:
        for line in proc.stdout:
            stdout_buffer.append(line)
    except Exception:
        pass

import threading
drain_thread = threading.Thread(target=drain, daemon=True)
drain_thread.start()

print("Waiting 5s for response...")
time.sleep(5)

response = "".join(stdout_buffer)
print("RESPONSE:")
print(response[:3000])
has_0200 = "0200:" in response
print(f"\nContains '0200:': {has_0200}")
if has_0200:
    print("SUCCESS: --gui-mode accepts debugger commands without -d!")
else:
    print("WARNING: Response did not contain expected memory dump.")

print("\nKilling jzIntv...")
proc.terminate()
try:
    proc.wait(timeout=3)
except subprocess.TimeoutExpired:
    proc.kill()
    proc.wait()
