# Room 0 Decode — Findings

_How Room 0 actually renders, established against jzIntv's authoritative STIC
source (`vendor/jzintv-src/stic/stic.c`), palette (`gfx/gfx.c`), and the game's
own disassembly._

## TL;DR

1. **The dungeon runs in FG/BG mode, not Color Stack mode.** This was the key
   wrong assumption in the project. The screen-setup routine at `$53B5`
   (`asm/disasm_new.asm`) reads `ROM[$554E] = $0001` (non-zero) and then:
   ```
   MVO@ R0, $0021   ; WRITE $0021  -> selects FG/BG mode  (stic.c:253)
   INCR R7          ; skip the next instruction (the $0021 READ that would
                    ;   have selected Color Stack mode, stic.c:176)
   ```
   So the STIC is left in **Foreground/Background mode** for the dungeon.

2. **In FG/BG mode each tile carries its own background color** — there is no
   color stack and no "Colored Squares". jzIntv's `stic_draw_fgbg`
   (stic.c:1347-1357) decodes a BACKTAB word as:
   ```
   card#   = (word >> 3) & 0x3F      # bits 3-8 (0-63)
   is_gram = word & 0x800            # bit 11
   fg      = word & 7                # bits 0-2     (primary 0-7)
   bg      = ((word>>9)&0xB) | ((word>>11)&0x4)   # bits 12,13,10,9 (0-15)
   ```
   `render_all_rooms.decode_fgbg_word()` / `render_room_fgbg()` implement this.

3. **This explains the floor and the black regions at once:**
   - Floor **`$1603`** → GROM card 0 (blank bitmap), fg=3, **bg=11 (olive green)**
     → a solid olive-green floor (77% of the room).
   - Walls **`$0823`/`$081B`/…** → GRAM cards 4/3/…, fg=3 (tan), **bg=0 (black)**
     → tan walls outlined by their own black background.

4. **Palette.** Colors use jzIntv's actual table (`gfx_stic_palette`,
   `vendor/jzintv-src/gfx/gfx.c`), exposed as `render_all_rooms.JZINTV_PALETTE`.
   The project's older `PALETTE`/`PASTEL_PALETTE` were sampled from a reference
   GIF whose palette does not match the `20200712` build (e.g. the GIF's floor
   `(58,138,0)` vs. this build's olive `(84,110,0)`), so they are kept only for
   the legacy color-stack code paths.

5. **A real gameplay trace is now captured** (`render_room_0_out_0005.txt`, via
   `scripts/debug_capture_gameplay.txt`). The title-screen keypad menu waits on
   a controller press (impossible headless), so the capture instead pokes
   `G_018C=1` and forces `PC` (`g 7 56C9`) to the player-count check, which
   falls through to game-start `$56DB`, bypassing the menu. After a few frames
   the dungeon is rendered and GRAM holds the real tiles. `derive_roomzero.py`
   uses this trace's BACKTAB **and** its captured GRAM.

6. **GRAM can also be reconstructed from the ROM** without any emulator run.
   `reconstruct_dungeon_gram()` replays the game's RLE tile loader **`L_53EA`**
   (`$53EA`) against the block at **`$61E7`**: `offset=DECLE[$61E7]`,
   `count=DECLE[$61E8]`, then per entry `rep=((w>>8)&3)+1`, `byte=w&0xFF`. It
   fills 31 cards (3-33), **byte-identical to the captured gameplay GRAM** —
   used as the fallback for boot-only traces.

7. **`GROM_CARD_MAPPING.md` is based on a wrong (low-byte) decode** (`word & 0xFF`)
   and should be regenerated or marked stale.

## Result

`python derive_roomzero.py` renders the actual first dungeon room: olive-green
floor, cream walls outlined in black, the **chest** (center), the **hourglass**
(right), and the **Warrior/Prince** at center with his **sword** drawn east.
Output `roomzero.png` (640×480, 4:3 aspect-corrected); a square-pixel side-by-side
with the reference is in `sprites/comparisons/roomzero_vs_reference.png`. The
structure matches the reference GIF tile-for-tile — chest, hourglass, walls — and
the player's shape/size/position match a real game screenshot (`game_ref.png`).

## All 4 dungeon levels

The game has 4 levels (0-3), selected by `G_019C`, which indexes the room-param
table at `$5A17`. The dungeon tileset (GRAM cards 3-33) is shared across all
levels — only the BACKTAB layout differs. `all_dungeon_levels.png` renders all
four, each a distinct maze.

- **Levels 0-1** are real gameplay captures. A level descent is driven by jumping
  to the stair handler `$6725` (with R1=+1, R2=+8), which does
  `G_019C += 1; JSR L_55F7 (re-render); G_02F4 += 8`.
- **Chaining descents desyncs the `G_02F4` data pointer** (level 2+ came out
  cleared), so **levels 2-3** are rendered from the boot-patched param traces
  (`render_room_{2,3}_out.txt`) instead — valid, distinct layouts. A clean
  multi-level gameplay capture (correct `G_02F4` handling, or navigating real
  stairs) is the remaining refinement.

## Sprite (MOB) layer

`render_room_fgbg(..., mobs=...)` overlays the hardware sprites; `parse_room_mobs()`
decodes the 8 MOBs from the SYSRAM shadow ($0325 X, $032D Y, $0335 attr). The
attr shadow is raw STIC A-register format (verified equal to STIC $0010-$0017),
decoded per jzIntv `stic.c`: `color = ((a>>9)&8)|(a&7)`, `card = (a&0xFF8)>>3`,
`is_gram = a&0x800`. Room 0's player decodes to MOB0 at (88,56), card 48, white.

**Sprite graphics are reconstructed from ROM.** The player/enemy sprite cards
(48+) are loaded into GRAM by the sprite loader at `$5216`/`$5235`, with the
GRAM target read from the `$5555` table (MOB0 → `$180` = card 48) and the source
being the character chosen at character-select. A headless capture forces `PC`
past the menu, so character-select never runs and those cards stay blank — and
the title input handler `$5684` isn't even reached without controller input
(which a headless run never produces).

**The player sprite is reconstructed from ROM (Warrior opening position).** The
headless capture bypasses character-select, so the player's GRAM card (48, from
the `$5555` table) is blank. The game has two playable characters — the
**Warrior/Prince** and the **Wizard**. The DECLE block at `$5BCD` holds the
Warrior's 5 rotation frames (cards 0+1 = opening position, rotating CCW to
north-facing at cards 8+9), followed by the Sorcerer's two fireball sprites
(cards 10-13); this was confirmed by visual identification
(`character_sprites.png`), the manual (top-down view, "the Prince appears at the
centre of the screen"), and a real game screenshot (`game_ref.png`).
`reconstruct_mob_sprite_gram(frame=N)` loads a chosen rotation frame's two cards
into GRAM card 48/49; Room 0 uses frame 0 (the player has just entered).

Which *class* loads into card 48 is set at character-select; for the 1-player
default the Warrior is used. A real character-select capture (blocked by the
controller-input gate — the title input handler `$5684` is never reached without
controller input) would confirm the class and frame per session.

**MOBs render at 2× vertical resolution.** Per jzIntv stic.c the MOB plane is
twice the BACKTAB height (`y_pos = (y_reg & 0x7F) * 2`), so the Warrior's two
cards (16 rows of bitmap data) **display as 8 pixels tall — one tile**, not two.
The overlay draws MOB rows at half vertical zoom. This was the key sizing fix:
measured against `game_ref.png` (calibrated to the known 96-row playfield) the
Prince is a compact ~8-px-tall hollow oval; an earlier full-height render made
him twice too tall.

**The sword is a separate element.** The opening-position body sprite (cards 0+1)
is a perfect vertical palindrome — it contains **no sword**. In the game the
sword is drawn as a line in the Warrior's facing direction (it can extend well
past the 8-px body, as in `game_ref.png`). The capture's MOB1 (the likely sword,
card 50) sits at (0,0) — inactive/mispositioned because the PC-force capture
bypassed the weapon setup. `derive_roomzero.py` therefore **draws** the blade
(white, ~1 tile, pointing east to match the reference) from the player MOB's
right edge. Caveat: this is a drawn approximation and its direction is assumed
east; the true facing for the opening position needs a trace dumping the
player's direction variable.

**Enemies.** The overlay renders every on-screen MOB the same way (sprite if its
GRAM card is loaded, else a solid marker). Room 0 at entry has only the player on
screen (the other MOB slots are off-screen / inactive); the Sorcerer and his
fireball sprites (cards 10-13) appear during combat.

**Aspect.** `derive_roomzero.py` saves `roomzero.png` with Intellivision
pixel-aspect correction (square-pixel render stretched height ×1.25 → 4:3),
matching the manual's TV proportions. The underlying `render_room_fgbg` stays
square-pixel for validation against the jzIntv GIF.

## Remaining gaps (cosmetic / data-dependent)

1. **Palette hue.** The render uses the authoritative jzIntv `20200712` palette
   (floor = olive `(84,110,0)`); the reference GIF was made with a different
   palette (floor `(58,138,0)`), so per-pixel RGB differs even though structure
   and color *indices* agree.
2. **Sword is drawn, not captured.** The blade is a drawn approximation pointing
   east; the real sword-MOB was inactive in the idle capture, and the opening-
   position facing is assumed. A capture dumping the player's direction variable
   would pin the true facing (and let rotation frames be selected live).
3. **Enemies / other characters.** Only the player is on-screen in this capture.
   Rendering the Sorcerer + fireballs, or the Wizard, needs a combat / Wizard
   capture (their sprite sources are identified: fireballs = DECLE cards 10-13).
4. **Levels 2-3** are boot-param traces, not full gameplay captures (see "All 4
   dungeon levels").

## Files

- `render_all_rooms.py` — `JZINTV_PALETTE`, `decode_fgbg_word`, `render_room_fgbg`
  (FG/BG render + MOB overlay at 2× vertical resolution), `reconstruct_dungeon_gram`,
  `reconstruct_mob_sprite_gram`, `parse_room_mobs`, `_read_rom_decle`.
- `derive_roomzero.py` — renders Room 0 via `render_room_fgbg` (captured GRAM,
  ROM-reconstruction fallback) + reconstructed player sprite + drawn sword +
  4:3 aspect correction.
- `scripts/debug_capture_gameplay.txt` — headless gameplay-room capture.
- `traces/rooms/render_room_0_out_0006.txt` — the gameplay trace (BACKTAB + GRAM
  + SYSRAM MOB shadow) that `derive_roomzero.py` reads.
- `character_sprites.png`, `game_ref.png` — sprite reference / real-game screenshot.
- `README.md`, `docs/backtab_pipeline_analysis.md` — updated.
