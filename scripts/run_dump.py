#!/usr/bin/env python3
"""
run_dump.py — Python automation wrapper for jzIntv Swords & Serpents dumps

Usage:
    python scripts/run_dump.py room        # Capture first room
    python scripts/run_dump.py all         # Full memory dump (interactive)
    python scripts/run_dump.py trace       # Single-frame trace
    python scripts/run_dump.py render      # Run capture + render PNGs

Requirements:
    - jzIntv emulator at jzintv-20200712-win32-sdl2/bin/jzintv.exe
    - exec.bin and grom.bin in project root
    - Swords and Serpents.bin in project root
    - Python 3 with PIL/Pillow installed

The emulator will open a window. For automated scripts, the script
handles most of the flow; you may need to press a key on the title screen.
"""

import os
import sys
import subprocess
from pathlib import Path

# === Configuration ===
PROJECT_ROOT = Path(__file__).resolve().parent.parent
JZINTV_EXE = PROJECT_ROOT / "jzintv-20200712-win32-sdl2" / "bin" / "jzintv.exe"
EXEC_BIN = PROJECT_ROOT / "exec.bin"
GROM_BIN = PROJECT_ROOT / "grom.bin"
GAME_ROM = PROJECT_ROOT / "Swords and Serpents.bin"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
SPRITES_DIR = PROJECT_ROOT / "sprites"
DUMP_DIR = PROJECT_ROOT / "dumps"

# === Helper Functions ===

def find_jzintv():
    """Locate the jzIntv executable."""
    if JZINTV_EXE.exists():
        return str(JZINTV_EXE)
    print(f"ERROR: jzIntv not found at: {JZINTV_EXE}")
    print("Download from: http://spatula-city.org/~im14u2c/intv/")
    return None


def check_roms():
    """Verify all required ROM files exist."""
    missing = []
    for name, path in [("exec.bin", EXEC_BIN), ("grom.bin", GROM_BIN),
                        ("Swords and Serpents.bin", GAME_ROM)]:
        if not path.exists():
            missing.append(name)
    if missing:
        print(f"ERROR: Missing ROM files: {', '.join(missing)}")
        print("Place them in the project root directory.")
        return False
    return True


def prepare_dirs():
    """Create output directories."""
    DUMP_DIR.mkdir(exist_ok=True)
    SPRITES_DIR.mkdir(exist_ok=True)


def run_jzintv(script_name, extra_args=None):
    """Run jzIntv with a debugger script.
    Returns True if the emulator ran successfully.
    """
    jzintv = find_jzintv()
    if not jzintv:
        print("ERROR: jzIntv not found!")
        print(f"Expected at: {JZINTV_EXE}")
        print("Download from: http://spatula-city.org/~im14u2c/intv/")
        return False

    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        print(f"ERROR: Script not found: {script_path}")
        return False

    cmd = [
        jzintv,
        "-d",                           # Enable debugger
        f"--script={script_path}",       # Run this debugger script
        "-e", str(EXEC_BIN),            # EXEC ROM
        "-g", str(GROM_BIN),            # GROM
        str(GAME_ROM),                  # Game cartridge
    ]
    if extra_args:
        cmd.extend(extra_args)

    print("=" * 60)
    print("Launching jzIntv...")
    print(f"Command: {' '.join(cmd)}")
    print()
    print("NOTE: The emulator window will open.")
    print("      For 'room' capture: press 1 on the title screen when ready.")
    print("      For 'all' dump: press F4 to break, then script runs.")
    print("=" * 60)
    print()

    try:
        result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
        return result.returncode == 0
    except FileNotFoundError:
        print(f"ERROR: Could not execute: {jzintv}")
        return False


def render_from_rom():
    """Render sprites directly from the ROM binary."""
    print("\nRendering sprites from ROM...")
    render_scripts = [
        "render_colored_sprites.py",
        "render_dragon.py",
        "render_dungeon_room.py",
    ]
    for script in render_scripts:
        script_path = PROJECT_ROOT / script
        if script_path.exists():
            print(f"  Running: {script}")
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(PROJECT_ROOT),
                capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"  WARNING: {script} exited with code {result.returncode}")
                if result.stderr:
                    print(f"  {result.stderr[:200]}")
        else:
            print(f"  SKIP: {script} not found")


def show_dump_info():
    """Show info about any dump files created."""
    dumps = sorted(DUMP_DIR.glob("*.bin"))
    if not dumps:
        # Check project root too
        dumps = sorted(PROJECT_ROOT.glob("dump_*.bin"))
    if dumps:
        print(f"\nDump files created ({len(dumps)}):")
        for d in dumps:
            size = d.stat().st_size
            print(f"  {d.name} — {size:,} bytes")
    else:
        print("\nNo dump files found. Did jzIntv run successfully?")


def print_room_reconstruction_help():
    """Print Python snippet to help reconstruct room from BackTab dump."""
    print("""
# === Python snippet to reconstruct room from BackTab dump ===
# After running: python scripts/run_dump.py room
# Use this to visualize the room layout:

import struct

with open('dump_room_backtab.bin', 'rb') as f:
    data = f.read()

# BackTab is 240 words (20 columns × 12 rows), big-endian
words = struct.unpack(f'>{len(data)//2}H', data)

# Decode: bits 10-3 = GRAM card #, bits 2-0 = FG color
for row in range(12):
    line = ''
    for col in range(20):
        w = words[row * 20 + col]
        card = (w >> 3) & 0xFF
        color = w & 0x07
        line += f'{card:02x}:{color} '
    print(line)
""")


# === Commands ===

def cmd_room():
    """Capture the first game room."""
    print("Room Capture Mode")
    print("-----------------")
    print("The emulator will open. On the title screen, press 1 to start a 1-player game.")
    print("The script will auto-capture the first room after 3 frames.")
    print()
    input("Press ENTER to launch jzIntv...")

    if not check_roms():
        return
    prepare_dirs()
    run_jzintv("debug_capture_room.txt")
    show_dump_info()
    print_room_reconstruction_help()


def cmd_all():
    """Full memory dump (interactive)."""
    print("Full Memory Dump Mode")
    print("---------------------")
    print("The emulator will open.")
    print("1. Navigate to the screen you want to capture")
    print("2. Press F4 to break into the debugger")
    print("3. The script will dump all memory regions")
    print()
    input("Press ENTER to launch jzIntv...")

    if not check_roms():
        return
    prepare_dirs()
    run_jzintv("debug_dump_all.txt")
    show_dump_info()


def cmd_trace():
    """Single-frame trace."""
    print("Frame Trace Mode")
    print("---------------")
    print("The emulator will open. On the title screen, press 1.")
    print("The script will capture the full frame rendering pipeline in stages.")
    print()
    input("Press ENTER to launch jzIntv...")

    if not check_roms():
        return
    prepare_dirs()
    run_jzintv("debug_trace_frame.txt")
    show_dump_info()


def cmd_render():
    """Capture room then render all PNGs."""
    print("Full Render Pipeline")
    print("-------------------")
    print("Step 1: Capture room dumps via jzIntv")
    print("Step 2: Render colored sprites, dragon, dungeon room mockup")
    print()
    input("Press ENTER to begin...")

    if not check_roms():
        return
    prepare_dirs()

    # Step 1: Capture
    print("\n[1/2] Capturing room data...")
    if not run_jzintv("debug_capture_room.txt"):
        print("jzIntv exited with error. Skipping render step.")
        return

    # Step 2: Render
    print("\n[2/2] Rendering PNGs...")
    render_from_rom()

    # Show output
    print("\nDone! Check sprites/ for PNG files.")


def cmd_help():
    """Show help."""
    print(__doc__)
    print("Commands:")
    print("  room      Capture first game room (auto)")
    print("  all       Full memory dump (interactive F4)")
    print("  trace     Single-frame rendering pipeline trace")
    print("  render    Full pipeline: capture + render PNGs")
    print("  help      This help")


# === Main ===

def main():
    if len(sys.argv) < 2:
        cmd_help()
        return

    command = sys.argv[1].lower()

    commands = {
        "room": cmd_room,
        "all": cmd_all,
        "trace": cmd_trace,
        "render": cmd_render,
        "help": cmd_help,
        "--help": cmd_help,
        "-h": cmd_help,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        cmd_help()


if __name__ == "__main__":
    main()
