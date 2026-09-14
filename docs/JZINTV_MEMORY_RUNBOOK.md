# jzIntv Memory-Extraction Runbook

> **2026-09-14 — read this first.** For anything that depends on **player
> input** (facing, speed, pickups, stairs, menus, title flow), jzIntv is the
> wrong tool: its debugger cannot inject controller input (§8.3). Use the
> **Intellijsd browser oracle** in `tools/intellijsd/` instead — it boots the
> game legitimately and drives the real controller port from a script
> (`ijsd.setPad`, `ijsd.runFrames`, `ijsd.read`). See its README. jzIntv
> remains the reference for static state dumps (§4) and cross-checks.

> How to pull memory-address data out of the running original game with the
> jzIntv debugger — commands, recipes, parsing, and every pitfall this project
> has hit. Written for an operator (human or agent) with no prior context.
> **Project root:** `C:\Users\vrock\Documents\Swords and Serpents`
> All techniques below were developed and verified on this game; the debugger
> mechanics apply to any Intellivision ROM.

---

## 1. Invocation

```
SDL_VIDEODRIVER=dummy timeout <secs> \
  ./jzintv/jzintv-20200712-win32-sdl2/bin/jzintv.exe \
  -d --script=<script.txt> -e exec.bin -g grom.bin "Swords and Serpents.bin" \
  > <out.txt> 2>&1
```

- `-d` starts the debugger; `--script=` feeds it commands non-interactively.
- `SDL_VIDEODRIVER=dummy` (and optionally `SDL_AUDIODRIVER=dummy`) runs headless.
- **jzIntv runs cycles in REAL TIME** (rate control, ~894,886 cycles/sec NTSC).
  Budget your `timeout` from the script's total cycles:
  `r 8000000` ≈ **9 seconds** wall clock. `exit=124` means the timeout killed
  it mid-script — count your `r` commands and add ~20s for startup.
- One emulator frame ≈ **14,914 cycles** (`r 14000` ≈ 1 frame).

## 2. Debugger commands (verified against `vendor/jzintv-src/debug/debug.c:1093-1115`)

| Command | Effect |
|---|---|
| `p addr val` | Poke memory, **no** peripheral side effects |
| `e addr val` | Write **with** side effects (peripherals see it) |
| `m addr count` | Dump `count` words from `addr` |
| `b addr` / `n addr` | Set / unset breakpoint |
| `r N` | Run up to N cycles — **stops early at a breakpoint** |
| `g <reg> <val>` | **Set a register** (reg 7 = PC, reg 6 = SP). ⚠️ NOT "run to addr" — `g 7 56C9` force-jumps the PC |
| `w addr` / `@ addr` | Watchpoint on writes / reads |
| `h` then `d` | Toggle history, dump it (`dump.hst`) — find where a crash came from |
| `#` | Halt on display blank |
| `q` | Quit |

**Dump line format:** `ADDR:  w1 w2 w3 w4   w5 w6 w7 w8   # ascii` — the first
word may carry a `*` cursor marker; strip it before parsing.
**`HALT! PC=0000`** in output = the CPU executed opcode `0x0000` — the PC
derailed into zeroed memory. The machine is dead; every `r` after it runs
zero game instructions and all dumps show frozen RAM. Check for this before
trusting any capture.

## 3. Memory map — where the data lives

| Range | Contents |
|---|---|
| `$0000-$0007` | STIC MOB X registers (per-MOB: bits 0-7 X, 9 visible, 10 double-width) |
| `$0008-$000F` | STIC MOB Y registers (bits 0-6 Y, 7 double-height, 8-9 zoom, **10 x-flip, 11 y-flip**) |
| `$0010-$0017` | STIC MOB A registers (bits 3-8 card, 11 GRAM select, 0-2 fg color + **bit 12 = fg bit 3**, 13 priority) |
| `$0100-$01EF` | Scratch RAM (8-bit) — game variables (`G_01xx` labels in the disasm) |
| `$01F0-$01FF` | PSG (sound) + controller ports (`$01FE/$01FF` = pads) |
| `$0200-$02EF` | **BACKTAB** — the 20×12 screen, one word per tile |
| `$0300-$035F` | System RAM (16-bit) — entity arrays (this game: X `$0325+i`, Y `$032D+i`, anim-script ptrs `$033D+i`) |
| `$1000-$1FFF` | EXEC ROM |
| `$3000-$37FF` | GROM (256 fixed cards × 8 bytes) |
| `$3800-$39FF+` | **GRAM** (64 loadable cards × 8 bytes; card N at `$3800+N*8`) |
| `$5000-$6FFF` | Cartridge ROM (this game) |

**BACKTAB word decode (FG/BG mode, per jzIntv `stic_draw_fgbg`):**
`card=(w>>3)&0x3F` · `gram=w&0x800` · `fg=w&7` · `bg=((w>>9)&0xB)|((w>>11)&4)`.

**ROM file byte order:** the `.bin` is big-endian 16-bit decles;
CP-1610 address `A` lives at file offset `(A-0x5000)*2`.

## 4. Recipe A — one-shot dump of a rendered state

Use when you need BACKTAB/GRAM/registers for a *specific* game state
(a level, a screen) without playing to it. This is how all level maps were
extracted (`extract_objects_layer.py`, the `world_level{N}.json` captures).

```
; --- NOP the boot idle loops (game-specific; from render_all_rooms.IDLE_PATCHES)
p 506A 0034
p 506B 0034
p 506C 0034
p 506D 0034
p 506E 0034
; --- NOP the state resets inside room-init L_55BF so YOUR pokes survive:
p 55C0 0034      ; CLRR+MVO G_019C   (level index reset)
p 55C1 0034
p 55C2 0034
p 55C7 0034      ; MVO G_02F4 = $65DC  ⚠️ THE BUG THAT COST US WEEKS —
p 55C8 0034      ;   without these two, every "level N" renders level 0!
; --- replace the camera constants (operands of MVII at 55CF/55D3)
p 55CF 02B8
p 55D0 0040      ; G_0175 (camera X: low 5 bits col, bits 5-6 = page 0-3)
p 55D3 02B8
p 55D4 0010      ; G_0176 (camera Y row)
; --- run to just before room init, set state, run to after render
b 5038
r 8000000
p 019C 0003      ; level index
p 02F4 65F4      ; level data ptr ($65DC + 8*level)
p 0180 FFFF      ; object discovery flags (…repeat $0180-$018D, $019D-$01AA)
b 55DA           ; = PULR after JSR L_5EE2 (render done)
r 8000000
m 0200 240       ; BACKTAB
m 3800 200       ; GRAM
q
```

**Rule: patch every store that overwrites state you poked.** Read the disasm
around your breakpoints; the `$55C7` miss silently corrupted 200+ captures.

## 5. Recipe B — stable live gameplay (`scripts/boot_stable.txt`)

The one-shot bypass leaves the stack unbalanced → HLT ~34 frames in.
For sustained gameplay (movement, AI, animation), boot like this:

```
p 506A 0034 ... p 506E 0034   ; NOP idle loops
b 5072                        ; main loop
r 8000000
p 018C 0001                   ; 1-player
n 5072
b 56F8                        ; the unbalanced PULR at menu end
g 7 56DB                      ; run the REAL game-start init
r 8000000
n 56F8
g 6 02F7                      ; reset SP to boot base
g 7 5072                      ; clean entry into the main loop
```

Zero HALTs over millions of cycles. **Why it works:** game-start `L_56DB`
lives inside a routine bracketed by `PSHR R5`/`PULR R7`; jumping past the
push means the pop derails the PC. Break at the pop, fix SP, redirect.

## 6. Recipe C — per-frame capture loops (animation, movement, facing)

The workhorse for dynamic data. After Recipe B, append N copies of:

```
n 5072
r 14000          ; ~1 frame with the breakpoint off (steps off the bp address)
b 5072
r 200000         ; runs to the next main-loop iteration (bp stops it)
m 0000 8         ; MOB X
m 0008 8         ; MOB Y (flips!)
m 0010 8         ; MOB A (card + color)
m 3980 80        ; GRAM cards 48-63 — ALWAYS dump GRAM with MOB regs (see §8)
```

Generate the script with Python (`'\n'.join([frame_block]*240)`); 240 frames
≈ 90s wall clock. Real captures: `scripts/capture_facing_long.txt`,
`scripts/capture_attack_anim.txt`.

## 7. Recipe D — finding unknown addresses

- **Watch-diff:** dump a candidate range (`m 0100 F0`), trigger ONE event,
  dump again, diff offline. Vary the event magnitude; keep addresses that
  move accordingly.
- **Read/write watchpoints:** `@ 01FE` shows *which PC* reads the pads;
  `w 0325` shows which code writes player X. This is how the EXEC input
  decode chain and `L_6054` collision callers were located.
- **Crash forensics:** `h` (history on), reproduce, `d` — `dump.hst` shows
  the instructions leading to the derail.

## 8. Pitfalls (each of these burned us)

1. **GRAM is rewritten at runtime.** A MOB's A-register card number is
   meaningless without the *content* of that card in the same frame —
   identify sprites by comparing GRAM bytes against known bitmaps, never by
   card number. (Knight "walk frames" were misidentified this way.)
2. **The `g` command sets registers.** It is not "go to".
3. **`p` on controller ports does nothing** — jzIntv recomputes pad state
   from host input every read. There is NO debugger-level input injection;
   `e` doesn't help either. Drive entities via velocity pokes
   (`G_0108/G_010C` each frame-top) or state pokes instead — but know their
   limits: they move entities *without* engaging input-gated logic (facing,
   animation), and forcing anim-script pointers (`$033D=5B28` etc.) just
   free-runs the script. For player-input-gated behavior the only oracles
   are NPCs running the same engine, or the owner's observation of the
   real game.
4. **Angle-bin movement data, never sign-bin.** Sign-binning classifies
   (dx=5,dy=1) as "diagonal" and drowns real diagonal samples in cardinal
   noise — it produced a confidently wrong facing map once. Compute
   atan2 over a 3-5 frame span, keep ±15° sectors, discard the rest.
5. **Check for `HALT!` before trusting output** (§2). A dead machine
   happily serves frozen dumps.
6. **Budget wall-clock from cycles** (§1) or `timeout` eats the tail of
   your script (`exit=124`, truncated dumps).
7. **Poked state gets re-stored by init code** — patch the stores (§4).
8. **The `*` cursor marker** appears inside dump lines; strip it.
9. Breakpoint-at-current-PC needs the `n / r 14000 / b / r` dance (§6) —
   `r` while sitting on your own breakpoint stops immediately.

## 9. Parsing dumps in Python

```python
import re
words = {}
for ln in open('out.txt', encoding='utf-8', errors='replace'):
    m = re.match(r'^\s*([0-9A-F]{4}):\s+(.*?)(?:#.*)?$', ln)
    if not m: continue
    addr = int(m.group(1), 16)
    for i, v in enumerate(m.group(2).replace('*', ' ').split()):
        try: words[addr + i] = int(v, 16)
        except ValueError: pass
```

For repeated dumps (per-frame loops), start a new frame record whenever the
first address of your dump block (e.g. `$0000`) reappears. Reusable helpers:
`render_all_rooms.py` → `parse_backtab`, `extract_backtab_from_output`,
`parse_memory_dump`, `IDLE_PATCHES`, `JZINTV_PALETTE`, `_read_rom_decle`.

## 10. Existing artifacts

| What | Where |
|---|---|
| Stable boot harness | `scripts/boot_stable.txt` (+ `boot_stable2.txt`) |
| Level/world captures | `extract_objects_layer.py`, `assets/world_level{0..3}.json`, `traces/realworlds_scan.log` |
| Per-frame captures | `scripts/capture_facing_long.txt`, `capture_attack_anim.txt`, `capture_player_diag.txt` (+ `traces/*_out.txt`) |
| Lair render probe | `traces/rooms/lair_probe_out.txt` (Recipe A worked example) |
| Disassembly (labeled) | `asm/disasm_new.asm` (game), `exec_dis.asm` (EXEC) |
| Analysis conventions | `docs/HANDOVER.md` ROM findings #1-#5 |
