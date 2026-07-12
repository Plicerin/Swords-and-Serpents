# Swords & Serpents — jzIntv Debugger Scripts

## Quick Start

```batch
cd "C:\Users\vrock\Documents\Swords and Serpents"

:: Option A: Python automation (recommended)
python scripts/run_dump.py room

:: Option B: Run jzIntv directly with a script
jzintv-20200712-win32-sdl2\bin\jzintv.exe -d --script=scripts/debug_capture_room.txt -e exec.bin -g grom.bin "Swords and Serpents.bin"
```

## Scripts

### `debug_capture_gameplay.txt` — Headless Gameplay Room Capture ★
- **What it does:** Drives the emulator into the *actual* first dungeon without any controller input. Breaks at the main loop (`$5072`), pokes `G_018C=1` (single player), and **forces `PC` to the player-count check (`g 7 56C9`)**, which falls through to game-start `$56DB` — bypassing the keypad menu (which otherwise waits for a controller press that a headless run can't provide). Advances a few frames so the dungeon renders and GRAM loads real tiles, then dumps BACKTAB + GRAM (+ the SYSRAM MOB shadow when capturing sprites).
- **Why it matters:** This is the capture that `derive_roomzero.py` consumes. Unlike the `$55DA` boot captures, GRAM here holds real dungeon tiles, not the IMAGIC logo.
- **Trace consumed:** `traces/rooms/render_room_0_out_0006.txt`. See `docs/room0_decode_findings.md`.

### `debug_capture_room.txt` — Auto Room Capture
- **What it does:** Breaks at the main idle loop ($506A) right after init, patches G_018C=1 (single player) and G_018B=$0001, then runs through the title screen automatically. Breaks at the main game loop ($5072), waits 5 frames for the room to render, then dumps BackTab, GRAM, scratchpad, sprite tables, and STIC color registers.
- **Output files:** `dump_room_backtab.bin`, `dump_room_gram.bin`, `dump_room_scratch.bin`, `dump_room_stic_shadow.bin`, `dump_room_sprite_table.bin`, `dump_room_stic_a.bin`
- **User interaction:** Fully automatic — no keypress needed!
- **Note:** Memory-edit command may be `e` or `ew` depending on jzIntv version. If the script fails at the `e` commands, try `ew` instead.

### `debug_dump_all.txt` — Full Memory Dump
- **What it does:** Dumps EVERY useful memory region in one shot: BackTab, GRAM, scratchpad, system RAM, STIC shadows, sprite tables, HUD area, Color Stack.
- **Output files:** `dump_all_backtab.bin`, `dump_all_gram.bin`, `dump_all_scratch.bin`, `dump_all_system.bin`, `dump_all_stic_shadow.bin`, `dump_all_sprite_table.bin`, `dump_all_hud.bin`, `dump_all_color_stack.bin`
- **User interaction:** Press F4 at your desired capture point, then the script runs.

### `debug_trace_frame.txt` — Single Frame Trace
- **What it does:** Captures 4 stages of a single frame's rendering pipeline through the main game loop at $5072: pre-frame, after sprite handler ($5143), after screen render ($5400), and final state after frame complete.
- **Output files:** `trace_frame_00_backtab.bin` through `trace_frame_03_hud.bin`
- **User interaction:** Fully automatic — no keypress needed!

### `run_dump.py` — Python Wrapper
- **What it does:** Orchestrates jzIntv with the appropriate script, plus can chain capture → render.
- **Commands:** `room`, `all`, `trace`, `render`, `help`

## jzIntv Debugger Commands Reference

| Command | Syntax | Description |
|---------|--------|-------------|
| Breakpoint | `b $ADDR` | Set breakpoint at address |
| Run | `r` | Run until next breakpoint |
| Step | `s [N]` | Step N instructions |
| Memory dump | `m $START $END file.bin` | Dump memory range to file |
| Memory edit | `e $ADDR $VALUE` | Write value to address |
| Watch | `w $ADDR` | Watch memory location |
| Quit | `q` | Exit emulator |

## Key Memory Map

| Address | Size | Description |
|---------|------|-------------|
| `$0100-$01EF` | 240 words | Scratchpad RAM (16-bit game variables) |
| `$015D-$0183` | — | HUD data (health, score, inventory) |
| `$018B` | 1 word | Game mode ($0001=single, $0083=2-player) |
| `$018C` | 1 word | Number of players (1-3) |
| `$0200-$02EF` | 240 words | BackTab (20×12 tile map) |
| `$0325-$032F` | 12 words | MOB attribute shadows |
| `$033D-$0344` | 8 words | Collision/status registers |
| `$0355-$035D` | 9 words | STIC register shadows (border, hdly, vdly, etc.) |
| `$3800-$39FF` | 256 words | GRAM (64 sprite cards × 4 words) |
| `$5A40-$5A9F` | 96 DECLEs | Sprite definition table (12 MOBs × 8) |
| `$5BB5-$5BC0` | 12 DECLEs | STIC A color register shadows |
| `$5BCD-$5C49` | — | DECLE sprite pixel data |
| `$61E7-$62CF` | — | RLE tile data (dungeon + dragon) |

## Key Code Addresses

| Address | Label | Description |
|---------|-------|-------------|
| `$5017` | TITLECODE | Game startup / ISR setup |
| `$5072` | — | Main game loop dispatch |
| `$538E` | ISR | VBLANK interrupt handler |
| `$5400` | L_5400 | Screen scroll/render |
| `$5072` | L_5072 | Main game loop (per-frame dispatch) |
| `$5143` | L_5143 | Sprite handler (BackTab/GRAM updates) |
| `$5400` | L_5400 | Screen scroll/render |
| `$557B` | L_557B | Game init (called once at startup) |
| `$55BF` | L_55BF | Game state init |
| `$55DB` | L_55DB | HUD update |
| `$5627` | L_5627 | Title screen render |
| `$56DB` | — | Post-player-count selection |
| `$5EE2` | L_5EE2 | Sound/note player |
| `$5F43` | L_5F43 | Collision detection |
| `$5FC1` | L_5FC1 | MOB sprite setup (reads $5A40) |

## Typical Workflow

### Capture a new room
```batch
python scripts/run_dump.py room
:: Press 1 on title screen
:: Script dumps everything automatically
```

### Interactive debugging
```batch
jzintv-20200712-win32-sdl2\bin\jzintv.exe -d -e exec.bin -g grom.bin "Swords and Serpents.bin"
:: Press F4 to break
> b $557B        :: Break every frame
> r              :: Run until next breakpoint
> m $0200 $02EF backtab.bin   :: Dump current BackTab
> s 100          :: Step 100 instructions
> q              :: Quit
```

### Reconstruct room from BackTab dump
```python
import struct

with open('dump_room_backtab.bin', 'rb') as f:
    data = f.read()

words = struct.unpack(f'>{len(data)//2}H', data)

# 20 columns × 12 rows
for row in range(12):
    for col in range(20):
        w = words[row * 20 + col]
        card = (w >> 3) & 0xFF   # GRAM card number
        fg = w & 0x07            # Foreground color (0-7)
        print(f'{card:02x}:{fg} ', end='')
    print()
```

## Tips

- **jzIntv must open a window** — it requires SDL2/display. Can't run headless.
- **Scripts execute sequentially** — if you set a breakpoint, the script pauses until that breakpoint is hit.
- **Memory dumps are raw binary** — use `struct.unpack('>H', ...)` to read 16-bit big-endian words.
- **GRAM is interlaced** — 8 rows per card, each row is stored as consecutive bytes. Card 0 = bytes 0-7, Card 1 = bytes 8-15, etc.
- **STIC colors are 3-bit** — bits 2-0 of $5BB5+ entries encode color index 0-7.
