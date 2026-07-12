#!/usr/bin/env python3
"""
P1 Validation Script - Swords & Serpents
Validates JS player movement against jzIntv emulator state.
"""

import subprocess
import re
from pathlib import Path

# Paths
JZINTV = Path("jzintv/jzintv-20200712-win32-sdl2/bin/jzintv.exe")
ROM = Path("Swords and Serpents.bin")
EXEC_BIN = Path("exec.bin")
GROM_BIN = Path("grom.bin")
SCRIPT = Path("tools/capture/walk_test.txt")

def parse_mem_dump(output: str, word_addr: int) -> int:
    """Parse a single 16-bit value from jzIntv memory dump.
    
    Format: ADDR:  w w w w   w w w w   # ascii
    Each row starts at WORD address aligned to 8 words (multiple of 0x8).
    """
    # Find the row containing this word address
    # Rows start at word addresses like 0320, 0328, 0330, etc. (every 8 words)
    row_start = word_addr & ~0x7  # Align down to multiple of 8
    row_start_hex = f"{row_start:04X}"
    
    # Find the row - capture everything up to the # comment
    pattern = rf"{row_start_hex}:\s+(.+?)\s*#"
    match = re.search(pattern, output)
    if not match:
        return 0
    
    # Parse all words in the row
    words_str = match.group(1)
    words = re.findall(r'[0-9A-Fa-f]{4}\*?', words_str)
    
    # Get the offset within the row (in words)
    offset = word_addr - row_start
    if offset < 0 or offset >= len(words):
        return 0
    
    # Strip the * marker and parse
    word = words[offset].rstrip('*')
    return int(word, 16)

def run_capture(script_path: Path) -> str:
    """Run jzIntv with a script and capture output."""
    cmd = [
        str(JZINTV),
        "-d",
        f"--script={script_path}",
        "-e", str(EXEC_BIN),
        "-g", str(GROM_BIN),
        str(ROM)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.stdout + result.stderr

def validate():
    """Run validation against emulator."""
    print("P1 Validation - Swords & Serpents")
    print("=" * 40)
    
    # Check files exist
    for f in [JZINTV, ROM, EXEC_BIN, GROM_BIN, SCRIPT]:
        if not f.exists():
            print(f"ERROR: Missing {f}")
            return False
    
    # Run capture
    print("\nRunning jzIntv capture...")
    output = run_capture(SCRIPT)
    
    # Extract state (addresses are WORD addresses)
    state = {
        "x": parse_mem_dump(output, 0x0325),
        "y": parse_mem_dump(output, 0x032D),
        "level": parse_mem_dump(output, 0x019C),
        "dataPtr": parse_mem_dump(output, 0x02F4),
    }
    
    print(f"\nEmulator state after 20 frames:")
    print(f"  X: ${state['x']:04X} ({state['x']})")
    print(f"  Y: ${state['y']:04X} ({state['y']})")
    print(f"  Level: {state['level']}")
    print(f"  DataPtr: ${state['dataPtr']:04X}")
    
    # Expected values from initial capture
    expected = {
        "x": 0x1958,
        "y": 0x20B8,
        "level": 0,
        "dataPtr": 0x65DC,
    }
    
    print(f"\nExpected state (after 20 frames):")
    print(f"  X: ${expected['x']:04X} ({expected['x']})")
    print(f"  Y: ${expected['y']:04X} ({expected['y']})")
    print(f"  Level: {expected['level']}")
    print(f"  DataPtr: ${expected['dataPtr']:04X}")
    
    # Compare
    print("\nValidation:")
    all_match = True
    for key in expected:
        match = state[key] == expected[key]
        status = "[OK]" if match else "[FAIL]"
        print(f"  {status} {key}: got ${state[key]:04X}, expected ${expected[key]:04X}")
        if not match:
            all_match = False
    
    if all_match:
        print("\n[PASS] P1 validation PASSED")
        return True
    else:
        print("\n[FAIL] P1 validation FAILED")
        return False

if __name__ == "__main__":
    import sys
    success = validate()
    sys.exit(0 if success else 1)