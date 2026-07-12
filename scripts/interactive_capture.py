#!/usr/bin/env python3
"""
interactive_capture.py — Interactive dungeon room capture for Swords & Serpents

Launches a visible jzIntv SDL window for gameplay and captures rooms via
separate hidden headless jzIntv instances.  This guarantees zero debugger-overlay
exposure: the visible emulator never enters debugger mode during play, and
captures happen in hidden windows that the user never sees.

Usage:
    python scripts/interactive_capture.py

Capture workflow:
    1. Emulator opens with the game running (first room)
    2. Move the warrior with arrow keys / numpad
    3. In THIS terminal, type the room number you want to capture (0-5)
       and press ENTER.
    4. A hidden jzIntv instance boots to that room, dumps memory, and quits.
       The room is rendered later from the memory dump (no screenshot needed).
    5. Keep exploring!  The visible emulator stays running.
    6. Type 'q' in this terminal to quit and render captures.

Post-processing:
    python scripts/process_captures.py captures/YYYYMMDD_HHMMSS

Game controls (jzIntv defaults for Swords & Serpents):
    Arrow keys / Numpad  = Move warrior (disc)
    Enter / Space        = Action buttons
    Keypad 1-9           = Numeric inputs
"""

import subprocess
import threading
import time
import sys
from pathlib import Path
from datetime import datetime

# === Paths ===
PROJECT_ROOT = Path(__file__).resolve().parent.parent
JZINTV_EXE = PROJECT_ROOT / "jzintv-20200712-win32-sdl2" / "bin" / "jzintv.exe"
EXEC_BIN = PROJECT_ROOT / "exec.bin"
GROM_BIN = PROJECT_ROOT / "grom.bin"
GAME_ROM = PROJECT_ROOT / "Swords and Serpents.bin"

# Reuse the proven pipeline from render_all_rooms.py
sys.path.insert(0, str(PROJECT_ROOT))
from render_all_rooms import (
    generate_debugger_script,
    run_debugger_script,
)

# Patches to skip title screen idle loops (from render_all_rooms.py)
IDLE_PATCHES = [
    (0x506A, 0x0034), (0x506B, 0x0034), (0x506C, 0x0034),
    (0x506D, 0x0034), (0x506E, 0x0034),
    (0x5318, 0x0034), (0x5319, 0x0034), (0x531A, 0x0034),
    (0x531B, 0x02B8), (0x531C, 0x0001),
    (0x56CC, 0x0034), (0x56CD, 0x0034),
]

X_FILL_MEM_NOP = [
    (0x5638, 0x0034),  # NOP the JSR R5 opcode
    (0x5639, 0x0034),  # NOP the X_FILL_MEM address
]


def find_jzintv():
    """Find jzIntv executable."""
    paths = [
        PROJECT_ROOT / "jzintv-20200712-win32-sdl2" / "bin" / "jzintv.exe",
        PROJECT_ROOT / "jzintv-20200712-win32-sdl2" / "jzintv-20200712-win32-sdl2" / "bin" / "jzintv.exe",
    ]
    for p in paths:
        if p.exists():
            return str(p)
    print(f"ERROR: jzIntv not found. Expected at: {paths[0]}")
    return None


def create_setup_script(capture_dir):
    """Create the debugger script that boots to first room and continues.

    The visible emulator runs this script once, then stays in gameplay mode.
    The user never interacts with the debugger in the visible window.
    """
    lines = ["; Auto-generated interactive setup script", ""]

    # Skip title screen idle loops
    lines.append("; --- Skip title screen idle loops ---")
    for addr, val in IDLE_PATCHES:
        lines.append(f"p {addr:04X} {val:04X}")
    lines.append("")

    # NOP the CLRR R0 + MVO R0, G_019C at boot ($55C0-$55C2)
    lines.append("; --- NOP CLRR + MVO G_019C at boot ---")
    lines.append("p 55C0 0034")
    lines.append("p 55C1 0034")
    lines.append("p 55C2 0034")
    lines.append("")

    # NOP X_FILL_MEM at $5638 to prevent BACKTAB wipe
    lines.append("; --- NOP X_FILL_MEM (prevents title screen from wiping BACKTAB) ---")
    for addr, val in X_FILL_MEM_NOP:
        lines.append(f"p {addr:04X} {val:04X}")
    lines.append("")

    # Break after X_FILL_ZERO returns (G_018C/G_019C get wiped here, must write after)
    lines.append("; --- Break after X_FILL_ZERO ($5038) ---")
    lines.append("b 5038")
    lines.append("")

    # Run through boot
    lines.append("; --- Boot through initialization ---")
    lines.append("r 8000000")
    lines.append("")

    # Write G_019C=0 (room index) and G_018C=1 (force 1-player start)
    lines.append("; --- Set room index + force 1-player game start ---")
    lines.append("p 019C 0000")
    lines.append("p 018C 0001")
    lines.append("")

    # Continue to gameplay — let the game fully settle.
    lines.append("; --- Run into first room ---")
    lines.append("r 8000000")
    lines.append("")

    # Continue — game runs, user can move warrior and explore
    lines.append("; --- Continue (game runs; visible window is for play only) ---")
    lines.append("c")
    lines.append("")

    script_path = capture_dir / "setup.script"
    script_path.write_text("\n".join(lines), encoding="utf-8")
    return str(script_path)


def drain_stdout(proc, log_path):
    """Continuously read jzIntv stdout and write to log file."""
    with open(log_path, 'w', encoding='utf-8', errors='replace') as f:
        try:
            for line in proc.stdout:
                f.write(line)
                f.flush()
        except Exception as e:
            f.write(f"\n[STDOUT DRAIN ERROR: {e}]\n")


def capture_room_hidden(room_index: int, capture_dir: Path, session_log: Path) -> bool:
    """Capture a single room via a hidden headless jzIntv instance.

    Launches jzIntv with a hidden window (STARTUPINFO wShowWindow=SW_HIDE),
    runs the room-specific debugger script, and appends the output to the
    shared session log.  The user never sees a debugger overlay.
    """
    script_path = capture_dir / f"capture_room_{room_index}.script"
    output_path = capture_dir / f"capture_room_{room_index}_out.txt"

    print(f"  [hidden] Booting jzIntv for room {room_index}...")
    generate_debugger_script(room_index, script_path)
    output = run_debugger_script(str(script_path), str(output_path), hidden=True)

    if not output:
        print(f"  [hidden] WARNING: No output for room {room_index}")
        return False

    # Append to shared session log so process_captures.py can find it
    with open(session_log, 'a', encoding='utf-8', errors='replace') as f:
        f.write(output)
        f.write("\n")

    has_backtab = bool(output.strip() and "0200:" in output)
    if has_backtab:
        print(f"  [hidden] Room {room_index} captured successfully.")
    else:
        print(f"  [hidden] WARNING: Room {room_index} capture missing BACKTAB.")
    return has_backtab


def print_banner(capture_dir):
    """Print the user-facing banner with instructions."""
    print("=" * 65)
    print("  Swords & Serpents — Interactive Dungeon Capture")
    print("  (Zero overlay exposure — captures are headless)")
    print("=" * 65)
    print()
    print(f"  Capture directory: {capture_dir}")
    print()
    print("┌" + "─" * 63 + "┐")
    print("│  EMULATOR CONTROLS                                           │")
    print("│    Arrow keys / Numpad = Move warrior (disc)                 │")
    print("│    Enter / Space       = Action buttons                      │")
    print("│    Keypad 1-9          = Numeric inputs                      │")
    print("├" + "─" * 63 + "┤")
    print("│  CAPTURE WORKFLOW                                            │")
    print("│    1. Move warrior to a new room in the emulator             │")
    print("│    2. In THIS terminal, type the room number (0-5)           │")
    print("│       and press ENTER to capture it headlessly               │")
    print("│    3. Keep exploring!                                        │")
    print("│    ⚠ Do NOT press F4 in the emulator — debugger overlay     │")
    print("│      is still active in the visible window.                  │")
    print("├" + "─" * 63 + "┤")
    print("│  TERMINAL COMMANDS                                             │")
    print("│    Type 0-5  = Capture that room (headless, no overlay)      │")
    print("│    Type 'q'  = Quit and process captures                   │")
    print("└" + "─" * 63 + "┘")
    print()


def main():
    jzintv = find_jzintv()
    if not jzintv:
        return 1

    # Check ROMs
    for name, path in [("exec.bin", EXEC_BIN), ("grom.bin", GROM_BIN),
                       ("Swords and Serpents.bin", GAME_ROM)]:
        if not path.exists():
            print(f"ERROR: Missing {name} at {path}")
            return 1

    # Create capture directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    capture_dir = PROJECT_ROOT / "captures" / timestamp
    capture_dir.mkdir(parents=True, exist_ok=True)

    session_log = capture_dir / "session.log"
    visible_log = capture_dir / "visible.log"

    # Initialize session log (empty — captures appended by hidden instances)
    session_log.write_text("; Session log — appended by hidden capture instances\n", encoding="utf-8")

    print_banner(capture_dir)

    # Create setup script for the visible instance
    setup_script = create_setup_script(capture_dir)

    # Build jzIntv command for the VISIBLE instance (gameplay only)
    cmd = [
        jzintv,
        "-d",                          # debugger needed for script execution
        f"--script={setup_script}",
        "-e", str(EXEC_BIN),
        "-g", str(GROM_BIN),
        str(GAME_ROM),
    ]

    print(f"  Launching visible emulator: {' '.join(cmd)}")
    print()

    # Launch visible jzIntv
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=str(PROJECT_ROOT),
    )

    drain_thread = threading.Thread(
        target=drain_stdout, args=(proc, visible_log), daemon=True
    )
    drain_thread.start()

    # In visible mode jzIntv runs at real-time (~894 kHz).
    # 16M cycles = ~18 s; wait 22 s to be safe.
    print("  Waiting for game to boot (visible emulator, ~22 s)...")
    print("  The emulator window should appear and show the title screen, then room 0.")
    for remaining in range(22, 0, -1):
        time.sleep(1)
        if remaining % 5 == 0:
            print(f"    ... {remaining}s remaining")
    print("  Boot complete. Look for the warrior in the dungeon!")
    print()

    captured_rooms = set()

    try:
        while True:
            try:
                user_input = input("> ").strip().lower()
            except EOFError:
                break

            if user_input == 'q':
                print("  Quitting...")
                break

            # Parse room number
            try:
                room_num = int(user_input)
            except ValueError:
                print("  Unknown command. Type a room number 0-5, or 'q' to quit.")
                continue

            if not (0 <= room_num <= 5):
                print("  Room number must be between 0 and 5.")
                continue

            if proc.poll() is not None:
                print("  ERROR: Visible emulator has exited. Cannot continue.")
                break

            # Run a hidden headless capture for this room
            ok = capture_room_hidden(room_num, capture_dir, session_log)
            if ok:
                captured_rooms.add(room_num)

    except KeyboardInterrupt:
        print("\n  Interrupted by user.")

    finally:
        print()
        print("  Shutting down visible emulator...")

        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

        print()
        print("=" * 65)
        print("  CAPTURE SESSION COMPLETE")
        print("=" * 65)
        print(f"  Visible log:   {visible_log}")
        print(f"  Session log:   {session_log}")
        print(f"  Captures dir:  {capture_dir}")
        print(f"  Rooms captured: {sorted(captured_rooms) if captured_rooms else 'none'}")
        print()
        if captured_rooms:
            print("  Next step: process captures into room PNGs")
            print(f"    python scripts/process_captures.py {capture_dir}")
        else:
            print("  No rooms were captured.")
        print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
