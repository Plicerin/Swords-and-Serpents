# RUNBOOK — Clean up the repo & finish the native JS port of *Swords and Serpents*

> **Audience:** an executing agent with **no prior context**. Read Section 0 fully before doing anything.
> **Project root:** `C:\Users\vrock\Documents\Swords and Serpents` (Windows, PowerShell). **Not a git repo — deletions are unrecoverable.**
> **Objective:** reimplement the Intellivision *Swords and Serpents* `.bin` as a **native JS/TS game** whose logic is hand-written and parameterized by **data tables extracted from the ROM**. **No emulator is shipped.** `jzintv.exe` is used **offline only** as a ground-truth oracle.

> **See `docs/HANDOVER.md` for the current bug list and the jzintv oracle steps that
> must be completed before any further code changes.**

---

## Known Bugs (as of 2026-06-12, owner-verified)

These bugs were confirmed by the project owner watching the actual game behaviour.
**Do not attempt to fix any of them without first running the jzintv oracle steps
described in `docs/HANDOVER.md`.**

| # | Bug | File | Status |
|---|-----|------|--------|
| BUG-1 | **Wrong architecture**: knight should stay centred; dungeon should scroll around it in all directions. Current code moves the knight across a fixed background — the opposite of correct. | `src/engine/movement.ts`, `src/main.ts`, `src/engine/collision.ts` | Unresolved — oracle required |
| BUG-2 | **Knight does not face direction of travel.** Sprite frame assignment has been attempted several times without success. Needs a jzintv oracle to map disc-direction → GRAM card. | `src/main.ts` lines 193–198 | Unresolved — oracle required |
| BUG-3 | **Wall collision is broken.** Knight passes through walls or stops in open space. | `src/engine/collision.ts` | Unresolved — oracle required |
| BUG-4 | **Movement speed is wrong.** Has been toggled between 0.5–2.0 px/frame; owner reports current value (1.5) is "unrealistically fast." Authoritative value must come from a jzintv frame-by-frame position delta. | `src/engine/movement.ts` line 33 | Unresolved — oracle required |

---

## Section 0 — Ground truth you MUST internalize

**0.1 The renderer is already solved in Python — port THAT, not the existing TS/JS.**
The only correct rendering math is in `render_all_rooms.py`. Three existing renderers are **buggy and must be retired**:
- `src/renderer.ts` — `getTile()` wrongly treats GROM as 2bpp/16-byte and GRAM as a 64-byte palette buffer, and its `JZINTV_PALETTE` is a *third, wrong* palette. (Its `decodeFgbgWord` is correct.)
- `web/renderer.js` and `web/game.js` — use a wrong **8-color** legacy palette and mask fg/bg to 3 bits (`PALETTE[fg & 0x7]`), discarding the 4-bit background color. `web/game.js` collision is a placeholder.

**0.2 Authoritative decode (from `render_all_rooms.py:512`, faithful to jzIntv `stic_draw_fgbg`):**
```
gr_idx = word & 0x9F8
card   = (gr_idx >> 3) & 0x3F        # 0..63
is_gram= (gr_idx & 0x800) != 0       # bit 11 -> GRAM, else GROM
fg     = word & 0x7                  # 0..7
bg     = ((word>>9)&0xB) | ((word>>11)&0x4)   # 0..15
```
Both GROM and GRAM cards are **8 bytes, 1bpp, 8×8**: pixel = `fg if (byte>>(7-x))&1 else bg`. Index the **16-color** palette with the full 4-bit fg/bg.

**0.3 The exact 16-color palette (`render_all_rooms.py:492`) — use these RGB values verbatim:**
```
0 (0x00,0x00,0x00) black     8 (0xBD,0xAC,0xC8) grey
1 (0x00,0x2D,0xFF) blue      9 (0x24,0xB8,0xFF) cyan
2 (0xFF,0x3D,0x10) red      10 (0xFF,0xB4,0x1F) orange
3 (0xC9,0xCF,0xAB) tan      11 (0x54,0x6E,0x00) olive/brown (floor)
4 (0x38,0x6B,0x3F) dkgreen  12 (0xFF,0x4E,0x57) pink
5 (0x00,0xA7,0x56) green    13 (0xA4,0x96,0xFF) lt-blue
6 (0xFA,0xEA,0x50) yellow   14 (0x75,0xCC,0x80) yellow-green
7 (0xFF,0xFC,0xFF) white    15 (0xB5,0x1A,0x58) purple
```

**0.4 GRAM tiles are reconstructed from ROM (no emulator needed at runtime)** — port `reconstruct_dungeon_gram` (`render_all_rooms.py:627`): read RLE block at CP addr `$61E7`: `start_off=DECLE[$61E7]`, `count=DECLE[$61E8]`, then per entry `rep=((w>>8)&3)+1; byte=w&0xFF`, write `byte` `rep` times to GRAM starting at `0x3800+start_off`. Fills cards 3–33.

**0.5 ROM addressing** (`_read_rom_decle`, `render_all_rooms.py:615`): `Swords and Serpents.bin` is 16384 bytes = 8192 big-endian 16-bit DECLEs covering CP `$5000–$6FFF`. File offset for CP addr `A` = `(A-0x5000)*2`, big-endian. `grom.bin` = 2048 bytes = 256 cards × 8 bytes.

**0.6 Geometry:** playfield = **20×12 tiles** (BACKTAB at `$0200`, 240 words), 8×8 px each → 160×96 px; aspect-correct ×1.25 vertically for 4:3. MOBs render at **2× vertical resolution** (16-row sprite = 8 px tall = one tile); player = two stacked cards N, N+1.

**0.7 jzIntv oracle:** binary at `jzintv\jzintv-20200712-win32-sdl2\bin\jzintv.exe`. Run a capture:
```
.\jzintv\jzintv-20200712-win32-sdl2\bin\jzintv.exe -d --script=<script.txt> -e exec.bin -g grom.bin "Swords and Serpents.bin" > <out.txt>
```
Debugger commands (VERIFIED against `vendor/jzintv-src/debug/debug.c:1093-1115` —
the earlier "`g cyc addr` run-to-PC" claim was WRONG): `p addr val` poke (no side
effects) · `e addr val` write **with** peripheral side effects · `b addr` break ·
`g <reg> <val>` **change a register** (so `g 7 56C9` *sets PC*=$56C9; reg 7 = PC) ·
`r N` run up to N cycles (stops early on a breakpoint) · `m addr count` dump ·
`w addr` watch writes · `@ addr` watch reads · `h` toggle history (dump via `d`) ·
`#` toggle halt-on-display-blank · `n addr` unset breakpoint · `c`/`q`. Dump format
per line: `ADDR: w w w w   w w w w   # ascii` (first word may carry a `*` cursor
marker — strip it). **A line `HALT! PC=0000` means the CPU executed opcode `0x0000`
(HLT) — i.e. the PC derailed into zeroed memory; the game has crashed, not paused.**

**0.8 Reference debugger script** (`scripts/debug_capture_gameplay.txt`) bypasses the controller-input menu gate: NOP boot idle loops (`p 506A..506E 0034`), break at main loop `$5072`, poke single-player `p 018C 0001`, force PC to player-count check `g 7 56C9` (falls through to game start `$56DB`), advance frames, dump `m 0200 240` + `m 3800 512`. This is the template for the input-driver in Section 3.

---

## Section 1 — Repo cleanup (DO FIRST)

Mode: **delete clearly-safe bloat; archive ambiguous items.** Verify before destructive steps.

**1.1 Safety preflight (must pass before any delete):**
```powershell
Test-Path ".\jzintv\jzintv-20200712-win32-sdl2\bin\jzintv.exe"   # must be True (the install we keep)
Test-Path ".\render_all_rooms.py"; Test-Path ".\grom.bin"; Test-Path ".\Swords and Serpents.bin"  # all True
```
If any is False, STOP and report.

**1.2 DELETE (regenerable / duplicate / WASM-only):**
```powershell
$del = @(
  "emsdk-main","emsdk.zip",
  "jzintv_extracted","jzintv-20200712-win32-sdl2","jzintv.zip",
  "tools\jzintv-20200712-win32-sdl2.zip","make.zip","make",
  "__pycache__","scripts\__pycache__","tools\__pycache__",
  "traces\debug",
  "clean_build.js","web\index.html","web\test.html"
)
foreach ($p in $del) { if (Test-Path $p) { Remove-Item -Recurse -Force $p; "deleted $p" } }
Get-ChildItem -Recurse -Force -Filter "nul" | Remove-Item -Force   # Windows redirect junk
```

**1.3 ARCHIVE (move, don't delete) → `archive\_relocated\`:**
```powershell
New-Item -ItemType Directory -Force "archive\_relocated" | Out-Null
# whole exploratory dirs
foreach ($d in @("analysis","captures")) { if (Test-Path $d) { Move-Item $d "archive\_relocated\" } }
# root one-off scripts (KEEP the core ones listed in 1.4 — move the rest)
Get-ChildItem -File ".\*.py" | Where-Object { $_.Name -match '^(analyze_|scan_|search_|compare_|find_|debug_|dump_)' -or $_.Name -in @('derive_empirical_data.py','solve_card_table.py','versioning.py','build_clean_room0.py') } | Move-Item -Destination "archive\_relocated\"
# intermediate images + scratch traces
Get-ChildItem -File ".\*.png" | Where-Object { $_.Name -match '^(dungeon_map_|room.?_cropped|.*_test)\b' -or $_.Name -match '^dungeon_.*_render' } | Move-Item -Destination "archive\_relocated\"
Get-ChildItem -File ".\*.txt" | Where-Object { $_.Name -match '^(long_trace|new_trace|short_|quit_|trace_)' } | Move-Item -Destination "archive\_relocated\"
if (Test-Path "manual_map18.png") { Move-Item "manual_map18.png" "manual_pages\" }
```
> The agent should **list** the matched files first (`-WhatIf` on Move-Item) and sanity-check before committing each glob move.

**1.4 KEEP — do NOT move/delete:**
- **CORE:** `Swords and Serpents.bin`, `Swords and Serpents_patched.bin`, `grom.bin`, `exec.bin`; `render_all_rooms.py`, `derive_roomzero.py`, `render_room.py`, `montage_rooms.py`, `animated_dungeon.py`; `src/`, `web/*.js` (retired in P0, not now); `level0_{backtab,collision,items}.json`; `server.py`, `run_server.bat`; `README.md`, `DUNGEON_MAP_DOCUMENTATION.md`.
- **REFERENCE:** `asm/`, `docs/`, `room_analysis/`, `vendor/jzintv-src/`, `jzintv/`, `traces/rooms/`, `traces/first_room_run/`, `manual_pages/`, `room_{0..5}_authoritative.png` (P0 oracle, MD5s in `DUNGEON_MAP_DOCUMENTATION.md`), `sprites/`, and `scripts/{extract_all_sprites,decode_sprite_pointers,decode_sprite_tables,parse_backtab,dump_rom_tables}.py`, `scripts/debug_capture_gameplay.txt`, `capture_all_rooms.script`.

**1.5 DONE WHEN:** preflight still passes; repo footprint ~2.6 GB → ~200–300 MB (`(Get-ChildItem -Recurse -File | Measure-Object Length -Sum).Sum/1GB`); `jzintv.exe` runs.

---

## Section 2 — Phase P0: build scaffold + correct renderer + static rooms

**2.1 Scaffold (Vite + TypeScript):**
```powershell
npm create vite@latest . -- --template vanilla-ts   # or scaffold manually if dir non-empty
npm install
```
Create `tsconfig.json`, `vite.config.ts`, `index.html` (canvas + `<script type="module" src="/src/main.ts">`). Target layout:
```
src/platform/{palette,stic,gram,grom,aspect}.ts
src/engine/{loop,input,state,collision}.ts
src/world/rooms.ts
src/main.ts
assets/{palette.json,grom.bin,gram_tiles.json,rooms.json}
tools/extract_assets.py
```

**2.2 Extract assets (offline Python, reuse `render_all_rooms.py`).** Write `tools/extract_assets.py` that imports `render_all_rooms` and emits:
- `assets/palette.json` ← `JZINTV_PALETTE`.
- `assets/grom.bin` ← copy of `grom.bin`.
- `assets/gram_tiles.json` ← `reconstruct_dungeon_gram()` (dict `addr→byte`; serialize as a 0x3800-based byte array for cards 0–63).
- `assets/rooms.json` ← for each level: the 20×12 BACKTAB word grid. Source the BACKTAB from the captured traces `traces/rooms/render_room_{N}_out*.txt` via `parse_backtab()` / `extract_backtab_from_output()` (rooms 0–5 exist today; 6–13 deferred to P6).

**2.3 Port the renderer** (`src/platform/stic.ts`) — direct translation of `decode_fgbg_word` + `render_room_fgbg`:
```ts
export const PALETTE: [number,number,number][] = [/* the 16 triples from Section 0.3 */];
export function decodeFgbgWord(w:number){
  const gr=w&0x9F8;
  return { card:(gr>>3)&0x3F, isGram:(gr&0x800)!==0, fg:w&0x7, bg:((w>>9)&0xB)|((w>>11)&0x4) };
}
// 8 bytes/card, 1bpp; GROM: grom[card*8..]; GRAM: gramBytes[card*8..] (0x3800-based)
export function renderRoom(backtab:number[], gram:Uint8Array, grom:Uint8Array, img:ImageData){
  const COLS=20, ROWS=12, TS=8;
  for(let r=0;r<ROWS;r++) for(let c=0;c<COLS;c++){
    const {card,isGram,fg,bg}=decodeFgbgWord(backtab[r*COLS+c]);
    const cb = isGram ? gram.subarray(card*8, card*8+8) : grom.subarray(card*8, card*8+8);
    for(let y=0;y<TS;y++){ const byte=cb[y]??0;
      for(let x=0;x<TS;x++){ const [R,G,B]=PALETTE[((byte>>(7-x))&1)?fg:bg];
        const px=(r*TS+y)*(COLS*TS)+(c*TS+x); img.data[px*4]=R; img.data[px*4+1]=G; img.data[px*4+2]=B; img.data[px*4+3]=255; }}
  }
}
```
> Note GRAM indexing: store reconstructed GRAM as a flat `Uint8Array` where card `k` row `r` = index `k*8+r` (i.e. pre-subtract the `0x3800` base when building from `gram_tiles.json`). MOB overlay: port the `render_room_fgbg` MOB block (`render_all_rooms.py:573-606`) — two cards N/N+1, vertical zoom = zoom/2.

**2.4 Wire up** `main.ts`: fetch assets, build GROM/GRAM `Uint8Array`s, render each level to an offscreen canvas, scale to canvas (nearest-neighbor, `image-rendering:pixelated`), aspect ×1.25.

**2.5 Retire** the buggy renderers: delete `web/renderer.js`, `web/game.js`; replace `src/renderer.ts` with the new `platform/stic.ts` (or delete it).

**2.6 Validate (pixel-diff vs ground truth):** render levels 0–3 (rooms 0–5) and compare to `room_{0..5}_authoritative.png`. Use a Python check (PIL) — note the authoritative PNGs are 640×480 aspect-corrected; compare at matching scale or compare the pre-stretch 160×96 against a downscale. **DONE WHEN** structure matches tile-for-tile (floor olive, walls tan-on-black, chest/hourglass present) and `npm run dev` shows the rooms.

---

## Section 3 — RE oracle methodology (prerequisite for P2–P6)

Build this early — every dynamic system depends on it.

**3.1 Scripted-input driver** (`tools/capture/play_<name>.txt`): start from `debug_capture_gameplay.txt` (Section 0.8), then **inject per-frame input** and dump between frames. Pattern:
```
p 506A 0034 ... p 506E 0034     ; NOP boot idle
b 5072
r 8000000
p 018C 0001
g 7 56C9                         ; into game start
; --- per-frame input loop (repeat the pair as needed) ---
p <INPUT_ADDR> <VAL>             ; poke decoded key / disc-direction (see 3.2)
r 8000000                        ; advance one frame
m <WATCH_ADDR> <COUNT>           ; dump watched region
q
```
`<INPUT_ADDR>`: determine experimentally — either the keypad shadow / `G_018C` the menu reads, or the disc-direction RAM movement reads each frame, or keypad reg `$01FA` decoded by `$5684`. Confirm by poking a direction and verifying player X/Y (`$0325`/`$032D`) changes the expected way.

**3.2 Locate unknown variables (watch-diff)** — `tools/watch_diff.py` parses the dump format (0.7) and diffs two dumps:
1. Baseline-dump candidate RAM: scratch `$0100–$01EF` + uncharted system RAM `$0300–$035F` (known there: X `$0325`, Y `$032D`, state `$0335`).
2. Trigger ONE event via 3.1, re-dump, diff → candidate addresses.
3. Vary event magnitude; keep addresses that move the right direction/amount.
4. **Shortcut for HUD values:** the print-number routine `X_PRNUM_RGT` is called from `$57FB/$5816/$583B/$5851/$5868` — disassemble each call site (`asm/disasm_new.asm`) to see which RAM it reads → directly identifies HP / score / level / gold.

**3.3 Find the RNG (do this in P2 — it's the long pole):**
1. Dump scratch `$0100–$01EF` every frame for ~20 frames with **zero input**. The address changing every frame (non-trivially) is the RNG state.
2. Capture a long value sequence; offline brute-force the generator: test LFSR `next=(x>>1)^(x&1?MASK:0)` over all 8/16-bit masks, and LCG `x=A*x+C`, until one reproduces the sequence bit-exactly.
3. Confirm the consumer with a read-watchpoint / by finding the in-place read-modify-write the ISR (`$538E`) does each frame.
4. Port to `src/engine/rng.ts`; store seed/constants in `assets/rng.json`.

---

## Sections P1–P6 — phased roadmap

Each phase: **extract / build / validate**. Validation everywhere = run JS headless (node) for a fixed input script, dump JS `state`, diff vs a jzIntv RAM dump from the same input script (`tools/validate.py`).

### P1 — Walkable dungeon (mostly understood)
- **Extract:** object/room data (`$64DE` room data → `$6580` type index → `$655E` object cards; see `docs/backtab_pipeline_analysis.md`); boundary thresholds `L_6677` (`$6677`): `Y<$10`→level+1 (north), `Y≥$40`→south transition, X-edge→level−1; stair descent `L_6725` (`$6725`): `G_019C+=1; re-render L_55F7; G_02F4+=8`; param table `$5A17` (indexed by `G_019C`); coord→BACKTAB `L_6054`.
- **Build:** `engine/collision.ts` (port `L_6054`: col=clamp(x/8), row=y/8, `addr=$0200+col+row*20`; wall/object test), `engine/movement.ts`, `world/rooms.ts`, `world/transitions.ts`; player MOB sprite from `reconstruct_mob_sprite_gram` (`$5BCE`, frame 0). Build the **input-driver** (Section 3.1) here.
- **Validate:** scripted walk → diff `$0325/$032D/$019C/$02F4` vs emulator; room after a stair descent matches.

### P2 — RNG + score/HP/inventory (HIGHEST RISK)
- **Extract:** RNG (Section 3.3) → `rng.json`; HP/score/gold/XP/inventory addresses (Section 3.2). Inventory likely near object flags `$019D+G_019C` (discovered) / `$0180+G_019C` (active).
- **Build:** `engine/rng.ts`; HP/score/gold/inventory fields in `engine/state.ts`; pickup logic (chest/key/potion/scroll).
- **Validate:** pinned-seed RNG sequence **bit-identical** to emulator; pickup state matches RAM. *Gate: P3 cannot be validated until RNG is exact.*

### P3 — Combat + enemy AI + spells (long pole #2)
- **Extract:** monster stat table (HP/attack/defense/card/color — find the table the spawn routine indexes by monster type; vary rooms to disambiguate) → `monsters.json`; damage formula via **pinned-RNG curve fitting** (poke fixed RNG, vary stats, record damage tuples, solve `f`) → `formulas.json`; spell/MAGIC effects (trace MAGIC keypress through `$5684` to mana/HP changes); hit detection thread `L_6421`/`L_64CB`.
- **Build:** `combat/{monsters,ai,damage,spells}.ts`; enemy MOB rendering (fireball cards 10–13 known); HP/death.
- **Validate (RNG pinned):** monster HP, player HP, score after each turn match; monster positions match frame-by-frame.

### P4 — Audio
- **Extract:** PSG register-write streams — set write-watchpoints on `$01F0–$01FF`, capture per event (boot jingle, footstep, hit, spell, death).
- **Build:** `audio/psg.ts` — AY-3-8914 model (3 squares + noise + envelope) → WebAudio; replay captured register streams keyed to events.
- **Validate:** emitted register-write timeline per event matches the captured one (functional match).

### P5 — Title / menu / character-select + HUD
- **Extract:** title BACKTAB/MOBs; `$5684` menu decode (1/2-player, MAGIC); char-select (which class loads card 48 via `$5555` table); HUD layout (map fields via the `X_PRNUM_RGT` call sites).
- **Build:** `ui/{title,charselect,hud}.ts`; wire keyboard→menu in `input.ts`.
- **Validate:** menu state transitions match `G_018C`/keypad for the same keypresses; HUD numbers match the RAM the print routines read.

### P6 — Rooms 6–13 + dragon boss
- **Extract:** capture rooms 6–13 via real stair descents using the P1 input-driver (linear vertical corridor, `DUNGEON_MAP_DOCUMENTATION.md`; navigating real stairs avoids the chained-descent `G_02F4` desync noted in `docs/room0_decode_findings.md`); decode dragon assembly (cards 24–33) on the lair screen (now reachable). `scripts/render_dragon.py` is a stub to finish.
- **Build:** complete `rooms.json`; dragon boss (reuse P3 combat); win condition.
- **Validate:** render rooms 6–13 vs fresh captures; full playthrough reaches the lair; boss fight diffs match.

---

## Appendix A — ROM address / label reference (CP-1610)

| Label / addr | Meaning |
|---|---|
| `$5017` entry · `$538E` ISR (vblank) · `L_5072` main loop | boot / per-frame |
| `$53B5` screen setup (writes `$0021` → FG/BG mode) · `L_53EA $53EA` RLE tile loader · `$61E7` RLE block | video setup / tiles |
| `L_55BF $55BF` room init · `L_55F7 $55F7` room render · `L_5EE2` background render | room build |
| `L_6677 $6677` boundary (Y<$10 / Y≥$40 / X-edge) · `L_6725 $6725` stair descent · `$5A17` room param table · `G_019C $019C` level index · `G_02F4 $02F4` data ptr | progression |
| `L_6054` coord→BACKTAB · `G_0325 $0325` playerX · `G_032D $032D` playerY · `$0335` player state | movement/collision |
| `$5684` keypad/menu decode (MAGIC, player count) · `G_018C $018C` decoded key/player count · `$01FA` keypad reg · `$56C9` player-count check · `$56DB` game start | input/menu |
| `$5555` MOB→GRAM target table · `$5BCD/$5BCE` character sprite block (Warrior 5 frames + fireballs cards 10–13) | sprites |
| `$64DE` room object data · `$6580` object type index · `$655E` object card lookup · `$0180+` active flags · `$019D+` discovered flags | objects |
| `X_PRNUM_RGT` (callers `$57FB/$5816/$583B/$5851/$5868`) | HUD number print → locate HP/score/gold |
| BACKTAB `$0200` (20×12) · GRAM `$3800` (cards, 8B each) · PSG `$01F0–$01FF` | memory regions |
| **GAPS to find:** RNG state (unknown), HP/score/gold/XP/inventory (scratch `$0100–$01EF` / `$0300–$035F`), monster stat table, damage formula, audio routines | the RE targets |

## Appendix B — Reuse map (don't re-derive)

| Need | Reuse |
|---|---|
| Renderer math | `render_all_rooms.py`: `JZINTV_PALETTE` (492), `decode_fgbg_word` (512), `render_room_fgbg` (536), `reconstruct_dungeon_gram` (627), `reconstruct_mob_sprite_gram` (674), `parse_room_mobs` (696), `_read_rom_decle` (615) |
| BACKTAB parsing | `parse_backtab` (392), `extract_backtab_from_output` (971), `parse_memory_dump` (364) |
| Asset/table extraction | `scripts/{extract_all_sprites,decode_sprite_pointers,decode_sprite_tables,dump_rom_tables}.py` |
| Capture template | `scripts/debug_capture_gameplay.txt`, `capture_all_rooms.script` |
| P0 pixel-diff oracle | `room_{0..5}_authoritative.png` (MD5s in `DUNGEON_MAP_DOCUMENTATION.md`) |
| Data already dumped | `grom.bin`, `level0_{backtab,collision,items}.json`, sprite PNGs in `sprites/`, `dragon_tiles.png` |
| RE map | `asm/disasm_new.asm` (fully address-labeled) |

## Appendix C — Risks
- **RNG (P2)** is the critical dependency for validating P3; budget a full phase. Brute-forcing LFSR taps / LCG constants against a captured sequence is the decisive technique.
- **Input-driver (Section 3)** gates P2–P6; build and prove it inside P1.
- **Chained stair descents desync `$02F4`** — navigate real stairs via injected input, don't chain-jump `$6725`.
- Rendering/movement/progression are low-risk (already ~85–90% understood).

## Final acceptance
- **Cleanup:** footprint ~200–300 MB; `jzintv.exe` runs; core files intact.
- **P0:** `npm run dev` serves rooms 0–5, pixel-matching `room_{N}_authoritative.png`.
- **Each later phase:** `python tools/validate.py <input-script>` reports zero diffs between JS state and the jzIntv RAM dump for the watched addresses (RNG bit-identical from P2 on).
