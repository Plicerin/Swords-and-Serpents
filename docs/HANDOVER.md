# Swords and Serpents — JS Port Handover

> **For the next executing agent.** Memory-extraction techniques (debugger
> commands, capture recipes, parsing, pitfalls) are in
> **`docs/JZINTV_MEMORY_RUNBOOK.md`** — read it before writing any capture
> script. This document records the current state of the
> JS/TS port, the outstanding bugs, and the exact investigative steps needed before
> writing any more game code.  Read `docs/PORT_RUNBOOK.md` for the full architecture
> reference.  **Project root:** `C:\Users\vrock\Documents\Swords and Serpents`
> (Windows, PowerShell). A git repo since 2026-07-12 (initial commit
> e9ddd29) - commit before risky changes.

---

## ✅ BUG #1 — vertical-movement side-to-side wiggle (CLOSED — owner confirmed fixed 2026-07-12)

**Symptom:** the player sprite appears to wiggle side-to-side while moving up
or down. Not present moving left/right or on any diagonal. Reported
repeatedly on 2026-07-06 and still present after three fixes.

**Fixed along the way (each verified to change what it targeted, none
resolved the symptom):**
1. F3 walk-alt "flash" (2-of-16 duty) → replaced with the captured 50/50
   ~5-frame F4/F3 cadence.
2. F3 x-flip "rock" → removed; flips constant (N: F3 plain, S: F3 y-flip).
3. Fractional camera resampling → camera + all sprite draws quantized to
   integer world pixels. Post-fix measurement: wall-edge bands stable at
   identical x for 17 consecutive frames of vertical scroll; player bbox
   constant (304-335) every frame.

**Measurements say canvas is stable** — sprite edges and background columns
do not move horizontally per-frame after fix 3. The perceived wiggle
therefore likely lives in something measurements haven't covered yet.

**Prime suspects for the next session (in order):**
1. **The F4↔F3 alternation itself** — the helm SILHUETTE changes shape every
   5 frames (edge pixels pulse ±1-2 world px even though centroids match to
   0.05px). A/B test: add a `?noanim=1` URL flag rendering static F4 on
   vertical movement and have the owner compare. If wiggle disappears, the
   player (script $5B28) does not use the knights' ($5B5E) walk cycle and
   vertical should be static — remove the cycle for the player only.
2. **Compositor resampling** — Windows display scaling (e.g. 125%) or
   browser zoom resamples the 640×480 canvas at non-integer DPR; combined
   with vertical motion this can shimmer. Test: set canvas CSS size to
   integer multiple / use `image-rendering: pixelated` on the scaled canvas
   (already set?) and devicePixelRatio-aware sizing.
3. **The vertical sword column** — drawn at body x+3 while the original
   x-flips the sword MOB for N (column x=4 when flipped, $10 → $08 mirror).
   Check whether the sword column should sit at x=3 (S) vs x=4 (N) and
   whether any per-frame flip state alternates it.

**RESOLUTION (2026-07-06).** Whole-frame differencing (diff consecutive rAF
frames, aggregate by screen column) proved that during vertical movement the
ONLY changing pixels in the player's screen band besides scrolling
background tiles were the player's own columns 308-335 — i.e. the F4↔F3
walk alternation itself. All positional causes were measured out (sprite
bbox constant, background columns stable, canvas layout rect constant at
DPR 1.25). The F4/F3 cycle was captured from KNIGHTS (script $5B5E); the
owner reported the real player does not wiggle, and **ROM finding #6 later
proved it directly** (233+ identical frames on straight runs under real
input): **the player renders a static frame in all directions**; knights
keep their captured walk cycle. (The `?anim=1` A/B flag was removed once
the ground truth was captured.)
Verified: 20 sampled frames of downward walking → exactly 1 distinct sprite
pixel profile (zero changes).

**Verification protocol for future rendering bugs:** whole-frame consecutive
diffs (column-aggregated) catch what filtered measurements miss; also check
canvas getBoundingClientRect stability and devicePixelRatio. Owner
confirmation required to close — instrument measurements alone missed this
symptom three times.

---

## ✅ 2026-07-04 — GAMEPLAY COMPLETE (toroidal levels, ROM-verified scrolling)

The port is now a complete, winnable game with the ROM's real scrolling model.

**ROM finding — each level scrolls INFINITELY (torus), verified in
`asm/disasm_new.asm`:** the background renderer `L_5EE2` masks the camera
column `ANDI #$001F` (mod 32) and, when the 20-wide window crosses column 31
mid-row, rewinds the source row and continues from column 0 (`L_5F0C` →
`CLRR R1`). The vertical scroll filler `L_5EAE` advances the row counter
`INCR R0; ANDI #$003F` (mod 64), and the camera position is kept masked
`ANDI #$007F` (`G_0175`, low 5 bits = X column, upper bits = coarse Y). So a
level is a 32×64 **torus**: walk off any edge and re-enter the opposite side;
the Prince stays screen-centred (manual p.6). An earlier "stacked mazes with
seam gates" world (archive/_relocated/endless.ts.retired) was replaced by
`src/world/torus.ts` (`LevelWorld`, `wrap`, `wrapDelta`) on 2026-07-04.

**Architecture (2026-07-05):** the **4 real fortress levels**
(`assets/world_level{0..3}.json`, 128×64 tiles = 1024×512 px each), each a
`LevelWorld` pre-rendered to an offscreen canvas and blitted in up to 4 wrap
pieces under a never-clamped Prince-centred camera. Positions wrap mod
(1024, 512) px; chase/contact/pickup distances use shortest-torus-path
deltas. Fixed 60 Hz timestep. The Serpent's tiles are stripped from the
level-3 grid at load (`extractSerpentLair`) and the boss entity spawns at the
exact ROM position (neck card 27 → row 23 col 67); the Crown sits behind it
inside the ziggurat chamber. Player start = the ROM's boot camera position
(tile ~12,32). Old 32×64 single-page mazes (`assets/level{N}_maze.json`) are
obsolete for gameplay but kept for reference.

**ROM finding #2 — enemies do NOT collide with walls.** Only the two player
slots run the movement wall test: `L_63F5` ($63F5) selects `G_01AB`/`G_01AC`
by player index (R3=0/1) before calling `L_6054`; the other `L_6054` callers
($5983, $61BD, $65FE) are object/tile-effect checks. Enemy MOBs are driven by
animation-script velocities with no BACKTAB lookup — phantom knights fly
straight through walls (owner-confirmed vs the real game, 2026-07-04).

**ROM finding #4 — THE REAL WORLD STRUCTURE (2026-07-05, definitive).**
(a) A level is **128×64 tiles = four 32-column pages**: `L_5E80` advances the
camera page (`G_0175 + $20, ANDI #$0060`; bits 5-6 = page). Every capture
before this date covered page 0 only. (b) There are **exactly 4 levels** —
the level structs live at `$65DC + 8·N` for N=0..3; at `$65FC` the data
becomes CPU code (our old "levels 4-13" were garbage reads). (c) Levels are
assembled from **8 map sections** (pre-doubled nibble indexes into the
pointer table at `$65CE`; struct word = base + band·2 + (page>>1), >>4 if
page odd). Section nibble $C ($6F9E) is referenced ONLY by level 3 band 1
page 2 — it is the ziggurat/lair. (d) **CAPTURE-SCRIPT BUG (fixed):** all
old captures NOP'd `$55C0-55C2` but not the `G_02F4 = $65DC` store at
`$55C7-55C8`, so every "level N" render actually used level 0's maze with
level N's objects — this is why all 14 old mazes looked identical and the
ziggurat never appeared. Fixed captures: `assets/world_level{0..3}.json`
(128×64 each; see traces/realworlds_scan.log).

**ROM finding #3 — the real enemy roster (2026-07-04/05, GROUND-TRUTHED).**
The Sinister Serpent's authentic form was decoded pixel-exact from a REAL
level-4 gameplay screenshot (CRPG Addict review; saved analysis pipeline:
downscale 4×→160×96, quantize to the jzIntv palette, brute-force the 8-px
camera offset — (2,1) — then match every tile against GRAM/GROM; the dragon
region matched at Hamming distance 0). It is a **6×3-tile dragon facing left** drawn as background tiles, now ALSO
captured directly from the ROM's own renderer (level 3 page 2, rows 22-24 —
`traces/rooms/lair_probe_out.txt`, words 1EC5..1F0D):
`. . 24 25 26 . / 27 28 29 29 29 30 / . . 31 32 33 .` — all green (fg 5) on
olive, EXCEPT the three repeated card-29 body segments on RED (word $0CED) =
the fiery belly; card 30 is the tail tip. The neck (27, 28) extends left toward its fire
breath, which it breathes down the approach corridor (per the CRPG Addict
description of level 4's ziggurat lair; note the real game has NO final
battle — the dev ran out of ROM). See `sprites/dragon_comparison.png`
(real-vs-port, pixel-identical) and `SERPENT_LAYOUT` in main.ts. Earlier
guesses (3×2 grid, the 7×2 jigsaw in `sprites/serpent_assembled.png`, the
small green MOB at `$5C9E`) are all WRONG as the boss; the $5C9E MOB is a
different creature (kept as SERPENT_SPRITES reference data). **Phantom
Knights (CORRECTED 2026-07-06, live-captured):** a knight enemy = the
PLAYER'S OWN 5-frame figure rendered in **BLACK (fg 0)** plus a separate
axis-aligned 8-px **sword MOB** ($FF row horizontal / $10 column vertical).
Captured from live gameplay (traces/capture_attack_anim_out.txt): enemy MOB
A-registers = GRAM cards 52/56 fg 0, and those cards' runtime bytes are
byte-identical to player_sprites frames 4 and 0; companion MOBs hold the
sword bitmaps. GRAM is static across 60 straight frames — no walk-cycle
animation. The earlier "$5C1C/$5C2C knight walk frames" were WRONG data
(removed); the June note "knights use the player sprite" was right. Red
Sorcerers `$6677/$6687`; knights are FASTER than the player (manual p.8,
KNIGHT_SPEED 0.28 vs 0.25).
Manual p.8 also settles speed: knights "move FASTER than the Wizard or the
Warrior Prince" → KNIGHT_SPEED 0.28 vs player 0.25; you must turn and strike,
not flee. NOTE for future fidelity work: the manual says the Fortress has
**4 levels** (scoring caps at "Fourth Level") — our 14 extracted mazes beyond
level 3 may be reading past the real level table; the 14-level descent is a
designed mode, not ROM truth.

**ROM finding #18 — SOUND (2026-09-16, Intellijsd: PSG register snapshot
every frame — `ijsd.psg.registers` — across every event, plus a trap on
the ROM's sound call `L_6932`).** The ROM plays effects through the EXEC's
sound processor (writers at `$1Cxx/$1Dxx`), one effect at a time; a new
effect cuts the old. Everything is on PSG channel B. Register order
A_lo B_lo C_lo E_lo A_hi B_hi C_hi E_hi enable noise shape volA volB volC:
  * **Silent:** title screen, game start, keypad 1/ENTER, pickup, chest
    store, status screen, wall bump (`L_6699` calls sound 0 = nothing),
    the stairs message/transition, knight spawn and charge, sorcerer
    vanish, revive. Wall bumps being silent surprised me; verified twice.
  * **Footstep** — every 8 ticks while walking: 2 frames, E period `$080`,
    shape 0, noise B enveloped (`enable $2F`, `volB $30`), noise period 0
    then 1, then off.
  * **Sorcerer materialise** (each appearance, not the red phase): 33
    frames, E period `$CF8`, shape `$F` (attack + hold), noise `$F`, volB env.
  * **Fireball flight**: fixed volume 15 noise, period `$1F` for 7 frames
    then −1 per frame, for as long as the fireball lives (cut by the hit).
  * **Hit** (ROM sound 7 — knight sword and door): tone B + noise B
    (`enable $2D`), E `$A00`, shape 0, noise `$B`, tone period alternating
    `$20`/`$40` (17/8/2/5 frames), 32 frames.
  * **Death burst** — the Prince's fall, a slain knight, a landing fireball
    (the fireball hit plays this, not sound 7): shape `$E`, E `$200` for 9
    frames then `$F00`, noise 0 then 1, volB env; 74 frames (a fireball
    hit's instance was cut at 43 by the sorcerer's despawn write).
  * Envelope rate: one step per 16 × EP clocks of the 1.79 MHz PSG clock
    (a full 16-step ramp = 256 × EP) — with the wrong 256× the swells
    rendered as silence.
  * Port: `src/audio/psg.ts` (AudioWorklet AY-3-8914 model: 3 tones, LFSR
    noise, envelope shapes, log DAC), `sounds.ts` (the scripts above),
    `sfx.ts` (one-voice sequencer with the fireball as the idle-priority
    sound). Audio unlocks on the first key/pointer. `g.audioRms(regs, s)`
    renders a register image offline for verification.

**ROM finding #17 — THE SPAWN RULE, EXACT (2026-09-16, disassembly of
`L_69FA` confirmed by tracing its RNG calls live).** Supersedes the
estimates in #11.
  * `$0163` counts down once per tick; at 0 the timer table (`$5566`)
    reloads it with 35 and calls `L_69FA`, which adds `G_0184` (starts 30):
    **rolls every 65 ticks**. Every 4th roll (the first after 9) `G_0184--`
    until 0, so the interval ramps 65 → 35 ticks over the first ~120 rolls
    (`G_017E` is the 9/4 counter). First roll at tick 36 after ENTER; the
    cold-boot RNG is deterministic, which is why two boots both spawned a
    sorcerer at tick 101 — a human's ENTER timing changes it.
  * Roll: `X_RAND2(5 − level) == 0` → spawn: **1/5, 1/4, 1/3, 1/2** on
    levels 1-4. Needs a free slot among 2/4/6 (`G_017B` bits) — max 3 foes.
  * Type: `X_RAND2(5 − level) == 0` → **Red Sorcerer**, else Phantom Knight
    (`L_6A7D`: record `$5AB4` knight, `$5AB4+$1C` sorcerer).
  * Sorcerer position (`L_6AF9`): `X_RAND2(16)` → `G_01A1` direction, the
    16-direction velocity table at magnitude 28 (`L_6046`, R1 = −28) added
    to (88,56): **28 px from the Prince in one of 16 directions** (all six
    observed offsets in #11 are on that circle).
  * Knight position (`L_6A8F`): `X_RAND2(4)` into the table at `$6AA6` —
    MOB (0,52), (88,0), (168,52), (88,107): **the left, top, right or bottom
    screen edge** (observed: bottom ×3, top ×1, right ×1).
  * Port: `spawnDirector()` in main.ts now runs exactly this (timer, ramp,
    odds, slots, placements); the tick-101 pin and the offset lists are
    gone. Chained sorcerer reappearances use the same 16×28 rule.

**ROM finding #16 — LEVEL 3: THE SERPENT IS INERT, ITS FIRE IS THE GATE,
NO CROWN, NO WIN IN 1-PLAYER MODE (2026-09-15/16, Intellijsd; descended
via poked stairs tiles, walked to the ziggurat).**
  * The ziggurat (cols 64-95, rows 16-31 of level 3) is a sealed chamber
    whose ONLY opening is the row-23 corridor from the west: three flame
    tiles (card 0, `$1E02`, red) at (64-66,23), then the Serpent's neck
    (card 27) at (67,23), its body (24-33) at (67-72, 22-24), and three
    treasures behind it — cards 17/15/16 (types 2/0/1) at (77,23), (79,23),
    (81,23). Level 3's object table has no key, no marker and no Crown; no
    "crown" card exists anywhere in the ROM tables.
  * **The Serpent does nothing.** Its cards are not in the classifier, so
    walking into/through it gives no code, no hit, no sound; the sword on it
    for 100+ frames changes nothing; its GRAM never changes. It is scenery.
  * **The flames are the gate, through wall geometry alone.** With the
    sprite's top-left tile at column 63 the 2×2 block holds (63,24)=card 4
    and (64,24)=card 3 → code `$A` (push west+north; or `2` when straddling
    row 22); at column ≥64 the block holds (64/65,24)=card 3,3 → code `3`
    then `1` → push EAST. Any flame pixel touched at x=512 fires the west
    push first, so the Prince can never reach column 64 by walking (max x =
    504); poked to x=520 he is dragged east through the neck into the body
    unharmed and can walk the chamber. No 1-player mechanism was found that
    removes the flames: keypad 0-9/C/E/L/T/R do nothing but the status
    screen (0), there is no key, the lantern only cures.
  * Title modes: 1 = "1 PLAYER", 2 = "2 PLAYER", 3 = "2 PLAYER/MAGIC" — the
    Wizard (slot 2, light-blue, script `$5B5E`, the bitmap the port used to
    call the "serpent sprite" `$5C9E`) exists only in modes 2/3 on the OTHER
    controller; his spells were not found by single key presses either.
    Whether the Wizard can quench the fire is the open question — outside a
    1-player port's scope.
  * Card 0 (the flames, also the 21 "torches" on level 1) animates: 4 ROM
    frames `$62B0/$62B8/$62C0/$62C8`, countdown 4 stepped by 2 → new frame
    every 2 animation steps. All animated-card countdowns (`$02F1-$02F4`)
    step together every SECOND game tick (4/6/8-frame intervals), which
    makes a door phase 11 steps = 22 ticks and a flame frame 4 ticks.
  * Port: the Serpent stays in the map as background (no entity, no Crown,
    no win screen — `gameWon` can no longer become true); `src/world/
    doors.ts` now serves cards 0/1/2 from the tick clock (`animatedCards`)
    and the flames collide/push exactly as measured (max x 504 from the
    west, eastward drag inside). Game-select modes 2/3 are not ported.

**ROM finding #15 — SORCERER IMMUNITY, SWORD PARRY, KNIGHT DEATH (2026-09-15,
Intellijsd, collision-register capture).**
  * The Prince's sword MOB sat on the Red Sorcerer's body (`$0019` bit 2
    set continuously) for 80 frames, red and then white: **no effect** — the
    sorcerer cannot be struck; it finishes its timeline regardless.
  * The fireball launched into the sword: on the very next frame the
    fireball's script went to 0 and it vanished (`$0019` = sword∩fireball,
    `$001B` = fireball∩sword) with the Prince unhurt — **the sword parries
    fireballs**.
  * A knight that runs into the sword dies (`$0019` bit 2, then `$5B94`):
    the same burst as the Prince's death — dot 8 ticks, sparkle 8, big
    burst 2-3 — with a random colour 0-7 each tick and no sword MOB, gone
    19 ticks after the killing tick. (The old "20-65 frames, black→white→
    blue" note came from frame sampling without the tick model.)
  * Port: sorcerers skipped by the strike test, `playerSwordHitsBox` kills
    fireballs, knights use `DEATH_BURST` for 19 ticks.

**ROM finding #14 — DEATH, THE FALL, REVIVAL, GAME OVER (2026-09-15,
Intellijsd, per-frame MOB/GRAM/script capture of two full deaths).**
  * Fatal hit (gray + hit) at tick T: script `$5B94`, sword MOB hidden,
    every foe and fireball wiped, `G_01AB=1`. GRAM card 48 (the body) is
    rewritten: **dot** `00…18 18…` ticks T+1..7, **sparkle** `…14 28 08 24…`
    +8..14, **big burst** `81 04 40 10 00 41 00 80 04 00 40 04 20 00 01 80`
    +15..21, tail `41 80 … 82` 2 ticks; colour = a random 9-15 each tick.
  * At T+23 (26 ticks after the hit): `$017C--` and script `$5B9A` (FALLEN):
    twinkling remains — 4 poses of 2-px dots (`08 24…82`, `…18(row7)…82`,
    `18(row0)…82`, `…14 28(rows 6-7)…82`; row 15 = `82` throughout) cycling
    every 4 ticks, colour random 0-7 per tick, **for 61 ticks** (738f →
    918f = 180 frames) — then script `$5B28`, white, sword back, same spot
    (MOB hidden for 2 frames). The EXEC controller-release wait (`$14B7`)
    is only entered if the disc is HELD at that moment; released = instant.
  * **Game over is one fall later than the port had it:** `$017C` 1 → 0 on a
    fall and the Prince still revives (lives shows 0); the NEXT fatal hit
    plays the burst (25 ticks) and then everything disappears (all MOBs
    off, script 0), the maze stays frozen and the CPU idles at `$15AA`
    awaiting a game-select key. No text, no piling MOBs (the old #8 note
    about "MOBs pile on" was wrong).
  * Port: `deathPhase` dying/fallen/gone with the captured bitmaps and tick
    counts (`DEATH_BURST`, `FALLEN_POSES`), reincarnation decremented at
    the fall, game over only when a fatal hit lands at 0 reincarnations.

**ROM finding #13 — THE GAME TICK (2026-09-15, Intellijsd: per-pass cycle
counts of the main loop `$5D08`, 5,800 passes over mixed play).**
  * The main loop **never waits for VBLANK**. Each pass simply costs CPU
    cycles and the ISR (velocities, screen shift, GRAM animation scheduler)
    steals ~1.4k of each frame's 14.9k. So frames-per-tick = work / ~13.6k:
    ~37k cycles with three foes alive (2.7 frames), ~41k with all slots
    empty (+1.4k per empty slot; 3.0 frames), and **+35k on any pass where
    the camera scrolled a column/row** (5-5.5 frames). Knight AI and the
    sorcerer add nothing measurable. (The earlier "3.6 frames/tick, slower
    with knights" note in #10 was the same thing measured badly — it
    included the ISR/spawn-search overhead of empty slots.)
  * What runs per TICK: controller read (→ velocity latch, so disc input
    lags up to a tick), collision dispatch + classifier (walls/doors/stairs/
    sword hits), ENTER handling, `G_01A4` stun/pickup countdowns (**the stun
    is 40 TICKS ≈ 117 frames, not 40 frames**; pickup lock 21 ticks), the
    stun palette flash (one colour per tick), knight re-aim (30 ticks) and
    sword pose sweep (~5 ticks), the sorcerer timeline (11 / 17 with the
    fireball at +7 / 13 ticks), the `$0163` spawn countdown (64), the first
    spawn at tick 101. What runs per FRAME: all MOB velocities (player 0.5,
    knight 30/64, fireball 100/64 px/frame), the wall push (`G_034D`), the
    door GRAM phases (48-60 frames), the stairs (226) and status (227)
    screens, `G_0103` waits.
  * Port: `tickDue()` in main.ts models exactly that cost function
    (`CYCLES_PER_FRAME 13600`, base 37000, +1400/empty slot, +35000/scroll);
    `update()` is split into frame work and `doTick` work; combat/knight/
    sorcerer/spawn timers are in ticks; `g.ticks()` on the bridge. Verified:
    3.0 frames/tick idle, 6-frame scroll ticks, a 40-tick stun = 121 frames.
    Not modelled: per-pass cycle jitter beyond those three terms.

**ROM finding #12 — WALLS: PIXEL COLLISION + PUSH-BACK (2026-09-15,
Intellijsd, per-frame `G_0108/G_010C/G_0179/G_034D` + classifier trap).**
  * Walls never block a move. The disc handler (`$56F9`) turns the disc
    direction into a velocity pair `G_0108/G_010C` (walking: ±50 = 0.5
    px/frame — sign convention: +G_0108 moves LEFT, −G_010C moves DOWN) that
    the frame code applies every frame. The Prince walks into anything.
  * When the STIC reports MOB0 touching a background pixel, the classifier
    (finding #10) ORs a code over the 2×2 block: bit0 push EAST, bit1 WEST,
    bit2 SOUTH, bit3 NORTH (tables: card 3 in a left tile → east, right tile
    → west; card 4 in a top tile → south, bottom tile → north; card 5 both).
    `L_669C`: `RRC` precedence — bit0 beats bit1, bit2 beats bit3 — sets
    `G_0108/G_010C = ±40`, `G_0179 |= 1` (disc IGNORED), clears bit 8 of the
    X word (MOB collision OFF) and `G_034D = 10`, counted down ONCE PER
    FRAME; at 0 velocity = 0, flag/collision restored (`$5D67`). Measured:
    bump at x=1092 → 1095 over frames 83-93: **3 px in 10 frames**, then
    control returns; holding into a wall bounces every ~15-20 frames.
  * Wall cards are half transparent (card 3 `f0f8e878f0f8f8f8` = left 4-5
    px; card 4 `f7ffffffefe60000` = top 6 rows; card 5 corner), so the
    Prince can stand in the empty half of a wall tile — corridors are
    effectively 3-4 px wider than the tiles suggest.
  * **Doors bite by BLOCK, not by jaw pixels:** with a BLANK (open) card 1
    poked into the block, touching the neighbouring wall gave code `$43` →
    `G_01A3=1, G_01A4=40` (the hit) and a 3-px push. So any background
    contact while a door card is in the 2×2 block is a bite; a clean pass
    through the middle of an open doorway touches nothing and is safe.
  * Port: `src/world/classifier.ts` (tables, `pushVector`, 10 frames ×
    0.3 px), `PlayerState.pushTimer/pushVx/pushVy`; `canWalk` no longer
    gates the player. NOT modelled: the ROM only classifies once per game
    tick (~3.6 frames), so it penetrates ~1 px deeper before the push; the
    bump sound (`L_6932`).

**ROM finding #11 — KNIGHT CHARGES, 16 POSES, SORCERER/FIREBALL AIM
(2026-09-15, Intellijsd, per-frame MOB/GRAM/velocity capture; owner
reported the port's knights "zig-zag").** Supersedes the "axis-locked"
knight movement of #7.
  * **Straight-line charges.** A knight's velocity (per slot, integer
    components in 1/64 px/frame) is re-aimed at the player's CURRENT position
    every **90 frames** (30 ticks at the observed 3 frames/tick; whether the
    ROM counts ticks or frames is undetermined) with magnitude **30** →
    0.469 px/frame (e.g. (28,-11) for a 37×-15 offset; E charge 41 px per 91
    frames). Nothing steers in between, so it overshoots a standing Prince by
    ~20 px and turns back at the next re-aim — a pendulum through him.
    Movement is applied per FRAME (the tick slowdown only delays decisions).
  * **Facing = nearest of 16 directions of the velocity** (checked for 12
    distinct velocity vectors), body frames F0/F1/F2/F3/F4 = E/ENE/NE/NNE/N
    with the player's flip scheme (N = F4 x-flip, W = F0 xy, …; flips live
    in the MOB **Y register** bits 10/11, not the A register — the A register
    is always `$987`/`$99x`, the ROM rewrites GRAM cards 52-55 instead).
    The sword MOB per direction (offset, 16-row bitmap, flips): E (8,0) $FF
    row; ENE (8,-2) `06 0c 30 60 c0` rows 5-9; NE (7,-7) the 45° blade; NNE
    (3,-8) `08×4 10×4 20×4` rows 4-15; N (0,-8) $10 column, x-flipped;
    mirrored for the other quadrants (south half inferred from the shared
    scheme; 2 samples each). **The pose sweeps main, +1, main, −1 with each
    pose held ~15 frames** — the "sword swing".
  * **Red Sorcerer (level 1, ~374 frames after the start!):** slot 2 script
    `$5B76` appears WHITE with a 3-pose materialise (small diamond
    `18243c66663c2418`, large `42 18 24 24 5a 5a 24 24 18 42`, sparkle
    `18 00 42 00 18 bd bd 18 00 42 00 18`, ~12 frames each), turns RED
    (`$5B7C`, body `507038703af572fbdeced6d747fd3000`) for ~61 frames and
    fires ONE fireball (slot 3, `$5B82`, 3 bitmaps cycling every 4 frames,
    fg 6/10 alternating) **aimed straight at the player at any angle,
    magnitude 100/64 ≈ 1.56 px/frame**, then goes white, reverses the
    materialise and is gone ~147 frames after appearing; the fireball dies
    with it. Reappeared 83 frames later at another spot near the player.
    Three more appearances (frames 604/754/5443/5587 idle) agreed: appear
    small-diamond 20 → large 12 → sparkle 8 (40 frames), RED 61 frames with
    the fireball at +27..31, white body 22 → sparkle 12 → large 12 → gone
    (46); 2 of 4 visits chained straight into a second appearance at a new
    offset. **A fireball that touches the Prince** (collision bit 3) vanishes
    and is the same hit as a sword (`G_01A3/G_01A4=40`, white→gray); when
    the Prince FALLS every foe and fireball is wiped at once.
  * **Spawns (idle, level 1, ghost):** sorcerer at 374 (offset (-10,26)),
    604 (-20,20) chained to 754 (-20,-20); knights at 1557 (0,50), 4229
    (0,51), 5850 (0,51); sorcerer 5438 (0,28) chained (26,11). Wandering:
    sorcerer 314 (-9,28), knights 2553 (2,55), 3549 (2,-53), 4156 (1,-52).
    So sorcerers materialise ~20-30 px from the Prince, knights at the top or
    bottom screen edge above/below him. A per-tick countdown at `$0163`
    reloads to 64 (≈230 frames) — the spawn roll — but the odds/selection
    were not captured (10 events in ~13k frames ≈ 1 in 5 rolls). Port:
    `spawnDirector()` in main.ts implements exactly that (20 %/roll, 50/50,
    ≤3 live foes) and the captured sorcerer timeline; the old pre-placed
    knight/sorcerer scatter is gone. Whether a sorcerer can be struck by the
    sword is NOT captured (port lets you, while it is red).

**ROM finding #10 — STAIRS, OBJECT TABLES, KEY, CHEST, LANTERN — SOLVED
(2026-09-15, disassembly + live verification in Intellijsd, both directions).**
Supersedes the "Stairs (partially solved)" paragraph of #8 below.
  * **Object tables (ROM):** `$64DE` = 16 records per level × 4 levels, 2
    words each **(column, row)**; `$6580` = 5-bit object TYPE per record, two
    per word (low field = even record, `>>5` = odd), indexed by the GLOBAL
    record number (level×16+i); `$655E` = BACKTAB word per type (2 bytes,
    SDBD). Extracted by `scripts/extract_objects.mjs` → `assets/objects.json`
    and verified word-for-word against the captured `world_level{N}.json`
    grids (every object tile is baked in there at its real position).
    Types: **0-6 treasures** (GRAM cards 15-21, fg 6 on olive), **7 = KEY**
    (card 22), **8 = Lantern** (card 14, two per level), **9 = chest** (card
    12, level 0 only, at (12,32) = the start), **10 = locked-stairway MARKER**
    (card 13, the checkered `abababaaaaababab` tile, tan on black, one on
    levels 0-2, none on 3), **11 = DOWN stairs** (card 9, `$084B`, never in
    the table), **12 = UP stairs** (card 10 — same bitmap as 9, tan on olive,
    one on levels 1-3), **13-16 = card 11** with bits 14-15 varying (four per
    level; purpose not captured). Positions: L0 marker (108,7), key (38,54);
    L1 up (104,6), marker (43,33), key (26,2); L2 up (41,33), marker (76,1),
    key (42,46); L3 up (75,1).
  * **Drawing (`L_6377`)** runs after every scroll/redraw: each on-screen
    record is written over the map tile; types 0-7 only while their bit in
    `G_0180+level` is set. `L_5EC7` builds map words from section data (tile
    type → card via `$65A0`: 0-8 → GRAM 0-8, 9 → GROM 0, 10-19 → GRAM 24-33
    (Serpent), …) — so cards 9/10/12-22 can ONLY come from the object system.
  * **ENTER handler `L_63F5`** (any tile, disc released): compute the 2×2
    tile block under the sprite (`L_6054`: TL = ((mobX-8)>>3, (mobY-8)>>3),
    then TR, BL, BR), take the FIRST card in 12..22:
      - card 12 (chest) → `L_6472` store: per level, each set treasure bit
        of `G_019D` scores 50×(level+1), bits cleared (key bit 7 kept),
        `G_01A7` stored count, `G_01A5/6` value, a reincarnation (`$017C++`)
        per 300 points, in-hand `G_01A8 = 0`.
      - card 13 (marker) → `L_64BC`: **if `G_019D[level] & $80` (the KEY bit)
        write `$084B` (card 9 = DOWN STAIRS) into the BACKTAB word AFTER the
        marker — one column to the RIGHT** (no `DECR R4` before the store).
        Verified: marker (108,7) → `$84B` at BACKTAB `$284` from PC `$64C9`,
        i.e. world (109,7).
      - card 14 (lantern) → `L_64CB`: `$0335+slot` colour bits ← 7 (white):
        the Lantern of Life CURES the injury (from code; not yet observed).
      - cards 15-22 → `L_6445`: tile ← `$1600`, `G_019D |= 1<<type`,
        `G_0180 &= ~(1<<type)`, `G_01A8++` (refused at 6) — **except card 22,
        the KEY, which skips the in-hand count**. Duplicate types on level 3
        share one bit.
  * **Descending/ascending is a background COLLISION, not a button.** The
    player's MOB-vs-background collision bit (`$0018` bit 8) dispatches
    (`$5107` table → `L_6679`) into the classifier `L_65FC`, which scans the
    same 2×2 block with four quadrant code tables (`$6632/$6639/$6640/$6647`):
    cards 3/4/5 → wall push codes, 1/2 → `$41/$42` (door hit), **9 → `$10` →
    `L_6717`: level+1**, **10 → `$20` → `L_671B`: level−1**, `G_02F4 ±= 8`.
    So with the marker at (108,7) and the stairs at (109,7), walking EAST
    descends the moment the sprite is at world x=864 (block = cols 108-109,
    the checkered marker supplies the collision). No keypad key is involved.
  * **Transition (captured frame by frame):** `G_019C` changes at once;
    next frame row 5 of the CURRENT screen is overwritten with `$0000` at
    columns 0-1 and 19 and **"Stairs to level N"** (N = new level, 1-based,
    GROM text, **fg 2 = red**, words like `$819A`) from column 2; MOB 0 is
    hidden from frame 2; `G_0103 = 2` and the game busy-waits (`L_6746`) —
    **226 frames** — then `L_5EE2` redraws the new level with the camera
    (`G_0175/6`) UNCHANGED and the Prince re-shown at the SAME screen and
    world position (frame ~231). Level 1's up-stairs (104,6) is therefore
    four tiles from where you arrive; on the way back up you arrive inside
    level 0's sealed room at (108,7) (the wall push at `$5FA1` nudges you).
  * **The stairs tile is transient:** it is a bare BACKTAB write. BACKTAB
    column/row shifts (`L_54D8/L_54EF/L_5526/L_5539`) carry it along, but as
    soon as its column scrolls off and back on, the column is regenerated
    from map+objects and it is floor again (verified: walk to column 94 and
    back → `$1603`). A level redraw (arriving on a level) also drops it.
    ENTER at the marker simply re-creates it.
  * **Walls are the classifier too:** `isWalkableWord` in the port now
    follows it — only GRAM cards 3/4/5 block; the marker, chest, items,
    lanterns and decorations 0/6/7/8 are walked over even where they are
    drawn on black. Wall cards have transparent halves (card 3 = left 4-5 px
    only; card 4 = top 6 rows) and the ROM only reacts to PIXEL overlap, then
    pushes back a few px over 10 ticks (`G_034D=$0A`, `G_0108/G_010C=±$28`):
    the push dynamics are NOT captured yet — the port still blocks by tile.
  * **Game-logic tick ≠ frame:** SUPERSEDED by finding #13 (the loop never
    waits for VBLANK; ~3 frames per tick, ~5.5 on a scroll; MOB motion is
    per frame so px/frame speeds stand).
  * CORRECTION to #8: `G_018C` is not a game-over marker — it is the last
    classifier code stored by `L_668E` (`$41/$42` = door contact from the
    left/right quadrants; the status/spell screens store `$41` too).
  Oracle notes: the classifier only runs on a background collision, so the
  GHOST helper now keeps bit 8 of `$0018` (MOB0-vs-background) and zeroes
  only the MOB-MOB bits — stairs/doors/walls work, knights can't hit. When
  the game runs at 1 tick per 3 frames, disc input lags ~2 frames: `NAV.goto`
  re-checks the position 4 frames after releasing, and `gotoSafe` releases
  the disc whenever the PC sits in the EXEC's controller-release wait
  (`$14B7-$14CD`, the loop that gates revival). One-tile gaps need the
  sprite exactly row-aligned (`(y-8)&7 == 0`).

**ROM finding #9 — THE CHOMPING DOORS ARE THE MYSTERY LIFE LOSS (2026-09-15).**
Doors are vertical pairs of GRAM cards **1** (upper jaw) and **2** (lower
jaw) — 11 pairs on level 1, BACKTAB words `$1E0B/$1E13` never change. The
ROM animates them by **rewriting the two GRAM cards** (writer `$529E`, the
animated-card scheduler at `$5270`: per-card word `$02F2`/`$02F3`, low
nibble = frame 0-3 open/half/closed/half from `$62D6`/`$62F8` + 8×frame,
high byte = countdown reloaded to `$16`, stepped by 2 about every 5 frames;
G_0104 round-robins cards 0-3 one per frame, so card 2 changes 1 frame
after card 1; card 0 is the animated red decoration, 4 frames every 8-12
frames). **Phase = 48-60 frames, mean 55; period ≈ 220 frames** (17
consecutive phases from a fresh boot, no knights; with knights hunting a
phase stretches to 60-73 frames). The first estimate of 148 frames was
wrong (owner: "closing too fast"). Bitmaps: open = blank; c1 half
`f0f0702020000000`, closed `f0f0f0707020a0a0`; c2 half `00008080d0d0f0f0`,
closed `a0a080d0d0f0f0f0`. Because it is GRAM, every door on the level
chomps in lockstep. Standing in a doorway while jaw
pixels are drawn sets MOB0's background-collision bit → classifier code
`$41/$42` → `L_668E` → the SAME hit as a knight sword (`G_01A3`, `G_01AB`
lock, 40-frame palette flash, white→gray); a second bite while gray → script
`$5B94`, `$017C--` at PC `$68D4`, then `$5B9A` fallen. Ghost mode hid this
because it zeroed the background bit along with the MOB bits. Port:
`src/world/doors.ts` (keyframes + bitmaps), `LevelWorld.setCardBitmap`
repaints all door tiles per phase, and the player-vs-tile PIXEL test in
`main.ts` (`spriteHitsTile`) bites through `injurePlayer`. The cycle's phase
at power-on was not captured (port starts a cycle at game start).

**ROM finding #8 — ITEMS, STATUS, DEATH, STAIRS MECHANICS (2026-09-14).**
Captured live in Intellijsd (real input, legitimately booted game):
  * **Pickup** = stand ON the object tile, disc released, press ENTER. The
    tile is replaced by floor **2 frames** later; a **21-frame** movement lock
    (`G_01A4=21`, `G_01AB=1`) accompanies it. Per-level bitmasks:
    `$0180+lvl` = object ACTIVE bits, `$019D+lvl` = COLLECTED bits; each of
    the 8 pickable objects owns one bit (level 1: treasure c21=bit6, key
    c22=bit7, c18=bit3, c20=bit5, c15=bit2, c17=bit0, c16=bit1, c19=bit4).
    **Card 14 (Lantern) is NOT pickable** (no bits change). Max 6 treasures in
    hand (status screen showed INHAND: 6). The object list for a level is at
    `$64DE` (16 records; low byte = world tile COLUMN — verified against the
    12 object tiles in `world_level0.json`; rows come from elsewhere).
  * **Status screen = keypad `0`** (not a side button). Layout in the game's
    font (uppercase decode card+32, lowercase/digits card+64):
    REINCARNATIONS / KNIGHT: n / TREASURES / INHAND: n / STORED: n / VALUE: n.
    Shown ~227 frames then returns to the maze. **ENTER on the treasure
    chest (card 12, start room) = store** and also shows this screen.
  * **Death → revive:** at 0 half-lives the player's script becomes `$5B9A`
    (the address the ROM compares at `$5716/$5751`), sword MOB removed, body
    recoloured, movement locked. **Revival happens only after the disc is
    RELEASED** (≈120 idle frames sufficed); holding a direction keeps the
    player fallen indefinitely. On revive: script `$5B28`, white, sword back,
    `$017C` (reincarnations) already decremented.
  * **Game over:** `$017C=0` → all 8 MOBs pile onto the player (knights +
    swords at the Prince's position), `G_018C=$41`, disc ignored, maze stays
    on screen, PC idles in the EXEC awaiting a game-select key.
  * **Something besides knight swords costs lives**: with MOB collisions
    disabled (ghost mode) `$017C` still fell 1→0 over a long walk. Suspect the
    chomping doors (cards 1/2, 11 pairs on level 1) — UNVERIFIED.
  * **Stairs (partially solved):** the walk-on classifier `L_65FC` (called
    every frame from `L_6677`) masks the tile under the player with `$09F8`
    and matches `$662A` entries shifted <<3: GRAM cards 1,2,10,9,3,4,5 →
    codes `$6632`: 5,4,1,**$10**,**$20**,$41,$41. Code `$10` (card **9**, the
    barred-column glyph) → `L_6717` → `L_6725`: level+1, `G_02F4 += 8`,
    prints "Stairs to level N" (text at `$6751`), re-renders. Code `$20`
    (card 10) → level−1. So **walking onto a card-9 tile descends
    immediately; ENTER is what must create that tile** ("Stairs will open").
    Card 9/10 words appear NOWHERE in the extracted maps or ROM data (the
    card is computed), and no BACKTAB write of card 9 was observed after
    ENTER with the key + 6 treasures in hand, at ~200 tested tiles. The
    card-13 (`⊗`) room at (108,7) is walled off from the rest of level 1 —
    almost certainly the level-2→1 ARRIVAL point (stairs-up marker). OPEN:
    where/how ENTER opens the down-stairs on level 1. Best next step: trap
    `L_692A/L_692F` BACKTAB writes with card 9 while pressing ENTER at the
    remaining untested landmark — the chest (12,32) with the key held — and
    the four `$64DE` records at columns 76/108 whose rows are unknown.
  Oracle technique notes: navigate with a BFS over `world_level{N}.json`
  (pixel-exact vs live BACKTAB — 0 mismatches) using player world pixel =
  `(g175&31 + page*32)*8 + (mobX-8)+4`; the camera moves in whole tiles
  while the sprite's screen X/Y drifts within an 8-px band. "Ghost mode"
  (skip the MOB pass so collisions never register) makes navigation safe
  but must be OFF for any collision-dependent test.

**ROM finding #7 — COMBAT, CAPTURED (2026-09-14).** With the Intellijsd
oracle patched so `runFrames` also runs the STIC MOB pass (the collision
registers `$0018-$001F` are computed by `renderMobs()`, which upstream only
called from rAF — without the patch they read `$3C00` forever and NOTHING
ever hit anything), real fights were observed frame by frame:
  * Knights (script `$5B30` walking, `$5B76/$5B7C` entry, `$5B94` death)
    walk at **0.5 px/frame, same as the player**, axis-locked, sword MOB
    (card 54 vertical / 50 horizontal) held 8 px ahead in the facing
    direction. Spawn on a timer (`$017E` counts 4→1 in ~178-frame steps);
    one knight at a time was seen.
  * **Hit detection = STIC per-pixel MOB collision between SWORD and BODY
    MOBs.** Knight-sword ∩ player-body → player hit. Player-sword ∩
    knight-body → knight dies (death flash black→white→blue, ~20-65 frames,
    then despawn). Body∩body does NOTHING — a knight sat at distance 0 on the
    player for 400+ frames with no effect. Simultaneous strikes: the
    player's wins.
  * **Being hit:** `G_01A3=1` (hit), `G_01AB=1` (disc locked — the register
    `L_63F5` gates movement on), `G_01A4=40` countdown; body colour cycles
    through the palette every 1-3 frames for those 40 frames. Then: white(7)
    → **gray(8)** ("half a life"); a hit while gray decrements
    **`$017C` = the Prince's reincarnations (starts 9)** and restores white.
    Gray never recovers on its own. `$017B` (3/15/51/63) is a separate
    timer, not health.
  * The player's **sword colour cycles through the palette every frame,
    always** (rainbow shimmer) — cosmetic, now reproduced.
Implemented in combat.ts (`swordHitsBody`, new `injurePlayer`, knight
`faceDx/faceDy` + `dying`) and main.ts (stun/sword palette cycles, death
flash). Verified via `g.step`: hit→40-frame stun→gray with no life lost;
hit while gray → life lost + white; knight walking into the sword dies at
the expected range with no damage taken. Still uncaptured: death (0 lives)
→ respawn timing; knight spawn placement rule; sorcerer encounters.

**ROM finding #6 — REAL PLAYER INPUT, AT LAST (2026-09-14). SUPERSEDES #5.**
The owner found **Intellijsd** (a pure-JS Intellivision emulator). A local,
patched copy lives in `tools/intellijsd/` (README there) and exposes
`window.ijsd` — load ROMs, run N frames synchronously, and drive controller
1 through the real port encodings (`psg.setController`). This removes the
"no input injection" wall entirely: the game is booted LEGITIMATELY (title →
'1' → ENTER, all via the EXEC's own keypad decode) and the PLAYER is
observed under REAL disc input. Results (40 frames held per direction,
dominant frame ≥33/40; then 240-frame straight runs):
  E: F0 · W: F0 xy · N: F4 x · S: F4 y ·
  **NE: F2 · SE: F2 y · NW: F2 x · SW: F2 xy**   (diagonal pose is F2, NOT F1)
  **NO walk animation in any direction** — 233/234 consecutive identical
  frames on S/E runs. Turning = 3-4 frame transition (old frame, then old
  frame with the new flips). F1/F3 are never a steady player pose; the F4/F3
  cycle in #5 was a KNIGHT behaviour (knights keep it).
  **Sword MOB (card 50):** E/W `$FF` row at (±8,0); N/S `$10` column at
  (0,±8); diagonals a 12-row 45° blade (rows 4-15: 04 04 08 08 10 10 20 20
  40 40 80 80, NE-pointing) at **(±7, ±7)** flipped per quadrant — not the
  (±8,∓2) 5-row blade guessed from knight data.
  **Speed:** `$0325` advances 1 px every 2 frames → **0.5 px/frame** on
  cardinals; diagonals ≈0.35 px/frame per axis (trig decomposition, ≈0.5·√½).
  The port ran at 0.25 — half speed — since June. Now 0.5 (knights 0.56).
  MOB X (`$0000`) is a screen position that oscillates 81–88 as the camera
  snaps; always use `$0325`/`$032D` deltas for speed.
All of the above is now in main.ts (`facingFrame`, `DIAG_SWORD`,
`drawSword`, `MOVE_SPEED`) and verified through the `window.__game` bridge
(`g.facing`, `g.step(n)` — deterministic stepping for hidden-tab tests).
Bridge additions: `step(n)`.

**ROM finding #5 — FACING (2026-07-06; knight-derived, PARTLY WRONG — see #6
for the player truth: diagonals are F2 not F1, no player walk cycle, sword
blade at (±7,±7)).** First analysis (sign-binned) wrongly concluded "no diagonal
poses" — owner caught it (SW didn't face SW). Angle-binned re-analysis of a
700-frame live capture (scripts/capture_facing_long.txt, ±15° sectors) plus
visual identification of the frames settles it:
  E:  F0 unflipped (STATIC — a 455-sample pure-west chase shows E/W have NO
  W:  F0 xflip+yflip            walk alternates)
  N:  F4 X-FLIPPED                     S: F4 Y-FLIPPED
  Vertical WALK CYCLE (captured sequence `4y 4y 3xy 3xy 4y 4y 3y ...`):
  F4/F3 alternate in ~5-frame 50/50 phases while moving; idle shows static
  F4. F3's flips are CONSTANT per direction — N: F3 unflipped, S: F3 y-flip
  (the DOMINANT captured variants; the minority x-flipped samples flicker
  sample-to-sample = aliasing, not a steady rock). Two owner-caught wrong
  renderings of this cycle: a 2-of-16 F3 "flash" (reads as jitter) and an
  x-flip "rock" on F3 (reads as left-right wiggle).
  NE: F1 unflipped (captured)          SE: F1 yflip (captured)
  NW: F1 xflip ┐ derived via the game's own mirror convention (same
  SW: F1 xyflip┘ transform the game uses for W); F1 is visually the 3/4
NE-facing helm. F2 is unused in-dungeon (never displayed in any capture).
Direction sectors are ±22.5°: shallow angles snap to cardinals. Sword MOB
offsets: E (+8,0), W (−8,0), N (0,−8), S (0,+8); DIAGONALS use a dedicated
45° blade bitmap (rows $06 $0C $30 $60 $C0 — NE-pointing, y-flip for SE,
mirror convention for NW/SW) at offset (±8, ∓2) from the body — captured
during F1 frames in the same trace. Knights move axis-locked
(zero true-45° samples in 700 frames), so knight captures alone cannot show
diagonals — the F1 diagonal evidence comes from the edge-of-sector samples.
NOTE: script-pointer pokes ($033D=5B28/$033F=5B5E + G_0179/G_017A/G_017F per
frame) make the anim scripts free-run through all 5 frames without movement —
NOT a valid facing oracle (traces/capture_player_diag_out.txt).
`facingFrame()` in main.ts implements exactly this map; `g.facing(dx,dy,alt)`
on the test bridge exposes it for verification.

**Gameplay loop (all verified in-browser via the `window.__game` test bridge):**
- Phantom knights (2–8/level) — the player's knight figure in BLACK with a
  black sword MOB — fly through walls straight at the player via the shortest
  torus path; slain by walking INTO them while facing (manual-correct contact
  combat). Activation radius is kept tight since cover doesn't exist. The
  player's sword is likewise a white axis-aligned sword MOB (drawSword).
- Red Sorcerers (ROM sprites `$6677/$6687`, red) teleport near the player
  (onto floor, so they stay reachable/killable), materialize, and fire 4-way
  axis-snapped fireballs (ROM frames `$5C4E`). Fireballs also ignore walls
  (MOBs), range-limited to ~one screen.
- Items (ROM-exact since 2026-09-15, finding #10): every treasure, key,
  lantern, chest and stairway is a ROM object at its real tile
  (`assets/objects.json`), already drawn in the captured level grids.
  ENTER on the tile picks up / stores / cures / opens; the checkered marker
  plus this level's KEY writes the DOWN-stairs tile one column to its right,
  and walking into it (a background collision) descends; the UP-stairs tile
  (levels 1-3) ascends. Both in place — same coordinates, 226-frame red
  "Stairs to level N" freeze. Chomping doors (finding #9) bite.
- Death revives in place after the disc is released (finding #8).
- Level 3 (the 4th): the Sinister Serpent (6×3 GRAM-card dragon at its real
  map position in the ziggurat, 6 HP, breathes fire down the approach
  corridor). The Crown of Kings cannot be taken while it lives. Slay it,
  claim the Crown → win. 9 reincarnations → game over.
- Deterministic population (seeded mulberry32) — same dungeon every run.

**Rendering rule — INTEGER-PIXEL CAMERA (2026-07-06, owner-reported
"wiggle").** The camera and every sprite draw position quantize to integer
world pixels (Math.floor) before scaling. With fractional camera coords
(player moves 0.25 px/frame), the background blit sampled a fractional
source rect and nearest-neighbour resampling redistributed tile rows every
frame — wall stipple dots visibly danced sideways during vertical scroll,
reading as the (screen-fixed) player wiggling side to side. Horizontal
movement masked it. Real STIC hardware has no sub-pixel positions — integer
quantization is both the fix and the authentic behavior. Diagnosis method:
per-frame wall-edge band tracking on the canvas (stable at (192,416) for
17 straight frames after the fix vs ±4px flicker before).

**Bugs fixed this session:** fireballs spawned inside walls (double +4
y-offset) and died instantly; diagonal fireballs useless in 1-tile corridors
(now 4-way); dragon unreachable for strikes behind wall pockets (sword-reach
strike pad, claw-back only at close range); rAF-rate-dependent game speed
(fixed timestep); `dist/` build shipped no data assets (build script now
copies `assets/`).

**Test bridge** (`window.__game`): `getState teleport setLevel giveKey stairs
entry probe rowMap nearestEnemy nearestItem sorcerers serpent crown hold info
step objects objectState marker upStairs tileWord doorClock transition` — used for
all headless verification (movement, wall collision, wrap crossing both axes,
wrap-seam rendering, cross-seam chase, strike/injury/death/respawn, stairs
lock/unlock/descend, all-14-level entry sweep, fireball hit, dragon fight,
crown gating, win). Keep it.

**Deliberately NOT ROM-exact:** enemy/item placement, keys-and-stairs
progression, Serpent HP/fire rate, the 14-level depth (manual says 4).
ROM-exact combat/RNG/HUD (P2/P3 in the runbook) remain open if the goal ever
returns to 1:1. Audio (P4) and title/menu (P5) are still unimplemented. The
ROM's own stair placement/level-connection data has not been extracted — the
stairway locations here are generated.

---

## ⚠️ 2026-06-13 LATE UPDATE — read this before the older sections below

The architecture is **SCROLLING (Prince-centred viewport)**, now **implemented**. Earlier
sections in this doc that say "fixed-room confirmed airtight" are **WRONG** — that conclusion
came from emulator pokes that bypassed the camera logic. The manual settles it ("The Prince
appears at the center of the screen throughout the quest"; `manual_map18.png` shows level 1 is
a large maze), and the ROM `L_5EE2` windows a 20-wide view out of a 32-wide map (camera
`G_0175`/`G_0176`). The real level-0 data is the **32×64 maze** in `level0_backtab.json` (was
wrongly dismissed as "title/debug"; copied to `assets/level0_maze.json`). It is now rendered
as a Prince-centred scrolling viewport: `src/world/maze.ts` + `renderGridToCanvas` (stic.ts) +
a rewritten `src/main.ts` (state.x/y are now WORLD pixels; camera clamps at maze edges).
Controls (keyboard, manual-sourced) and contact-based combat (9 lives) are also implemented.
Open: full mazes for levels 1–13 (need ROM level-data extraction), the per-direction facing
sprites, stairs between levels.

## Current State

The Vite/TypeScript scaffold is running at `http://localhost:4040/` (`npm run dev`).
The renderer (`src/platform/stic.ts`) correctly draws the 20×12 dungeon rooms.
A warrior sprite is displayed.  Arrow keys / WASD are wired to movement.

**Nothing else is correct.**  The four bugs listed below must be resolved before
any further feature work.

---

## ⚠️ Oracle session 2026-06-12 — findings & a retraction (READ THIS FIRST)

An attempt to run the BUG-1 architecture decider in jzintv uncovered that **the
gameplay oracle does not actually work**, which changes the priority order.

**What happened**
- `scripts/oracle_arch.txt` / `oracle_arch2.txt` boot via the same bypass as
  `scripts/debug_capture_gameplay.txt` (force PC past the 1-player menu gate).
- The dungeon **renders once** (BACKTAB fills with real tiles, warrior MOB-0 at
  screen centre 88,56) — this is why *static room capture has always worked*.
- But ~34 frames in, **the CPU executes opcode `0x0000` (HLT)**: the PC has
  derailed into zeroed memory. `traces/oracle_arch*_out.txt` show `HALT!` and
  `Cycles:` frozen at ~507421 while the instruction count barely advances.
- Therefore every `r 8000000` *after* the halt ran **zero game instructions**.

**Retraction.** Mid-session I briefly concluded "the warrior MOB is pinned at
screen-centre (88) and does not follow `$0325`, so the game scrolls." **That was
wrong** — it was frozen RAM read from a *halted* CPU. Poking `$0325` changed RAM
(debugger pokes work on a dead machine) but no code ran to act on it, so the MOB
"not moving" proved nothing. **BUG-1 remains UNANSWERED.**

**Root cause of the dead oracle.** The boot-bypass (`G 7 56C9` to skip the menu)
leaves some pointer/vector uninitialised; after a few frames the game jumps
through it into `$0000` and HLTs. The bypass is fine for a one-shot render, useless
for sustained gameplay.

**Corrected jzintv debugger reference** (the runbook's Section 0.7 was wrong):
- `G <reg> <val>` = **change a register** (e.g. `G 7 56C9` *sets PC*), NOT "run to PC".
- `P addr val` = poke RAM, no side effects.  `E addr val` = write **with** peripheral side effects.
- `W addr` = watch writes · `@ addr` = watch reads · `H` = toggle history · `#` = halt-on-display-blank.
- Verified command table: `vendor/jzintv-src/debug/debug.c:1093-1115`.

**This means there has never been a working gameplay harness** — which explains why
every dynamic value (speed, facing, collision) has been guessed.

### ✅ RESOLVED later the same session — stable harness + architecture answer

**1. The harness is fixed.** `scripts/boot_stable.txt` (and `boot_stable2.txt`) boot to
**stable gameplay — 0 HALTs over thousands of frames** (verified to cycle 69M+, PC in
valid game code). Root cause of the old crash: the game-start code `L_56DB` lives
*inside* the menu routine that starts at `$5684` with `PSHR R5` and ends at `$56F8`
with `PULR R7`. The bypass force-jumped past the `PSHR R5`, so `$56F8`'s `PULR R7`
popped stack garbage and derailed to `$0000` (opcode `0x0000` = HLT) ~34 frames later.
**Fix:** let `L_56DB` run (it does the real init), break at `$56F8`, then redirect
`PC=$5072` (main loop) with the stack reset (`G 6 02F7`). Recipe is in `boot_stable.txt`
— **use it as the base for ALL future gameplay oracles.**

**2. Architecture (BUG-1): strong evidence it is FIXED-ROOM (moving sprite), NOT
scrolling.** On the *live* machine (`scripts/decide_live.txt`, 0 HALTs), poking player
X `$0325` 88→32 made the game copy 32 into the warrior MOB's **screen** register and
render the knight at screen-X=32, while the **BACKTAB did not change** (0 tiles). A
pinned-sprite/scrolling engine would never draw the knight off-centre — it would ignore
`$0325`. So the render path honours a *variable* sprite position over a *static*
background = fixed-room. **This is the model the current JS code already uses.**

**Reconciling the owner's "knight stays centred, rooms scroll" report:** that was almost
certainly the *symptom* of two real bugs, not a scrolling engine — `MOVE_SPEED=0.5`
(≈2 canvas px/frame) made the knight look stationary, and hard-cut room transitions at
the screen edges made the world appear to "move" when you crossed a boundary. All prior
project evidence (single-screen room PNGs, linear-dungeon docs, hard-cut transitions)
agrees with fixed-room.

**Final airtight confirmation still worth doing:** an *input-driven* run (hold one disc
direction, watch whether `$0325` moves away from 88 [fixed] or stays pinned [scroll]).
That same run also yields `MOVE_SPEED` (BUG-4), the facing→frame map (BUG-2), and
collision stops (BUG-3). It needs the decoded-direction RAM variable, which is the next
thing to find now that the machine actually runs.

**Artifacts:** `scripts/oracle_arch.txt`, `oracle_arch2.txt`, `oracle_watch.txt`
(early/invalid — halted), `diag_halt.txt` (found the crash via `dump.hst` history),
`boot_stable.txt` + `boot_stable2.txt` (✅ the working harness), `decide_live.txt`
(✅ live decider). Outputs in `traces/*_out.txt`.

### 🔜 NEXT: input injection (gates BUG-2/3/4 measurement) — intel gathered

The airtight architecture confirmation + speed/facing/collision measurements all need
to drive **real disc input** in the stable harness. Progress so far:

- **Controller-port injection is IMPOSSIBLE via the debugger.** `p`/`e` on `$01FE`/`$01FF`
  do not change what the game reads — jzintv recomputes pad state from host input each
  read (verified: read stays `00FF`). See `scripts/inject_test.txt`.
- **The disc is read ONLY by the EXEC**, routine at `$14F1` (reads `$01FE`=right/player-1,
  `$01FF`=left at PCs `$14F4/$14F8/$1525/$152C`). Found via read-watchpoint
  (`scripts/find_input.txt`).
- **The EXEC decodes & stores player-1 controller state at base `$0120`** (`$011F` =
  player-2), via sub-routine `.EXEC.52F` (`$152F`): inverts the raw read (`XORI #$00FF`),
  stores raw at `R1+4 = $0124`, table-decodes the disc (table near `$1543`). Disassembly
  in `exec_dis.asm` (regenerate: `dis1600 -a -H -B -f exec.bin exec_dis.asm` with
  `exec.cfg` mapping `$0000-$0FFF → $1000`).
- **Poking `$0120`/`$0121` with `0x04/0x08/0x40` each frame did NOT move the player**
  (`scripts/drive_test.txt`). So either the movement reads a different sub-offset of the
  `$0120` block, or the decoded-direction encoding differs.

**Dead-ends ruled out (so the next pass doesn't repeat them):**
- A READ-watch on `$011F-$0124` over live frames showed **the game never reads the EXEC
  decode block** — only the EXEC's own debounce reads it (PCs `$1536/$154E/$15AC`); idle
  value `0x40`. (`scripts/find_consumer.txt`.) Caveat: capture was with *idle* input, so an
  "input-present" path may simply not have run — not fully excluded.
- `G_0102` (EXEC sets `0x80`=idle / `0xA0`=active) is **not** the movement gate — the game
  uses it at `$51CC` for video-blank / attract timing only.
- `.EXEC.AAD` (`$1AAD`, 2nd EXEC call/frame) does not read `$0120` either.

**Conclusion:** the input→movement handoff is deeper than a single RAM variable; pinning it
is a dedicated EXEC/game-loop RE task (follow `.EXEC.AAD`, or capture a full-frame `h`
history with input forced present and trace what perturbs the player's `$033D`/velocity).

**RECOMMENDED PIVOT (faster path to actually fixing BUG-2/3/4):** the three values don't
*require* live input — they live in the ROM movement code and can be extracted STATICALLY,
then spot-checked with the harness via position-pokes:
- **BUG-4 speed:** velocity routine at `$5731` uses `G_017F` (=`0x32`=50) → `L_6046` (trig
  decomposition). Port `L_6046`'s math for exact px/frame per direction.
- **BUG-2 facing:** find the disc-direction → warrior GRAM-card (sprite-frame) selection in
  the ROM; map to `player_sprites.json` indices.
- **BUG-3 collision:** port `L_6054` (coord→BACKTAB, already matched) + the actual wall/
  object predicate and sample footprint the movement code uses.

Artifacts: `scripts/find_input.txt`, `inject_test.txt`, `drive_test.txt`,
`find_consumer.txt`; `exec_dis.asm`.

### 🔬 Movement-code static RE (2026-06-13) — findings

Pivoted to extracting BUG-2/3/4 values straight from the ROM movement code. Key results:

- **The ROM movement system is an 8-direction, trig-based, animation-script engine** — far
  more complex than the JS port's 4-direction integer model:
  - Disc direction + magnitude `G_017F` (=`0x32`=50) → `L_6046` → EXEC sin/cos (`.EXEC.629`)
    → an (X,Y) velocity **vector**, accumulated in fixed-point (`L_5323`/`L_5546`, a
    `<<G_0116` scaler). There is **no single px/frame constant** — speed is vector math.
  - Each MOB runs an **animation script** via a pointer in `$033D[i]`; the player's
    facing/movement state machine is `$56F9-$57Cx`, keyed on direction-sign flags
    `G_0179` (X) / `G_017A` (Y), dispatching to `L_57DA`/`L_5894`/`L_5885`.

- **BUG-2 facing — DEEPER THAN MAPPING; still unresolved. (Corrects an earlier overstatement
  that the sprites were simply "wrong" — frame 0 IS correct.)**
  - **Verified live:** the warrior's displayed sprite is GRAM **card 48** (`$3980`), and in
    the idle dungeon state it equals `18 3C 7E 73 F9 99 89 89 89 89 99 F9 73 7E 3C 18` =
    **exactly `player_sprites.json` frame 0**. So the extraction base (`$5BCE`) is right.
  - **The displayed sprite does NOT change** when the warrior is driven in any of the 4
    directions (`scripts/facing_capture.txt`), nor when the direction-sign flags `G_0179`/
    `G_017A` are poked (`scripts/facing_g0179.txt`), nor when the descriptor `$033D` is poked
    (`scripts/decode_facing2.txt`). Three independent methods → card 48 stays frame 0.
  - ⇒ In-dungeon facing rotation is gated behind the **real disc-input animation path** that
    none of these pokes trigger — OR the in-dungeon warrior **doesn't rotate at all** and the
    5 frames are used elsewhere (e.g. the character-select screen). Cannot distinguish without
    driving real disc input (the deep blocker) or fully decoding the `$56F9`/`$033D` animation
    interpreter. **Recommendation: stop re-guessing the frame map** (3 attempts failed for this
    reason); either show frame 0 only (matches every movement test) or defer until real input
    is solved and the actual per-direction sprites can be captured from card 48.

- **BUG-4 speed:** vector/trig (above). To match the ROM, port `L_6046`'s decomposition +
  the `L_5323` accumulator; a scalar `MOVE_SPEED` can only ever approximate it.

- **BUG-3 collision:** `L_6054` (coord→BACKTAB) already matches; still need to port the
  exact wall/object predicate + sample footprint the movement code applies.

- **BUG-1 architecture — now AIRTIGHT (fixed-room).** `scripts/vel_drive.txt`: injecting
  X-velocity `G_0108` each frame-top moved player X `$0325` 88→86 — i.e. the position
  variable **walks off centre** during movement (it is not pinned). Combined with the earlier
  finding that the MOB renders at `$0325`'s value, the warrior moves across a static
  background. Fixed-room confirmed; the JS model is correct.

- **NEW TOOL — velocity injection drives movement.** Poking `G_0108` (X) / `G_010C` (Y,
  signed 16-bit) at every frame-top makes the player move (position integrator applies it
  before the next recompute). This is a working movement-drive that does NOT need the EXEC
  disc-input path — usable for collision tests and rough speed work. Caveat: it injects an
  *arbitrary* velocity, so it confirms architecture and lets you exercise movement, but the
  *natural* ROM speed still requires the disc→`G_017F`→`L_6046` value (real input path).

**Bottom line:** the JS port's simplified 4-dir model is architecturally divergent from the
ROM's 8-way trig+script engine. Making movement ROM-exact is a real sub-project. BUG-1 is
resolved (fixed-room). Facing (BUG-2) is blocked behind the real disc-input path and may not
even rotate in-dungeon — stop re-guessing it. Velocity injection is available for BUG-3
collision work. Artifacts reproducible from `Swords and Serpents.bin` + the `scripts/*.txt`.

---

## Bug List (owner-verified, in priority order)

### BUG-1 — Wrong game architecture: knight should be centred, rooms should scroll

**Observed:** The knight sprite moves across a fixed background.  
**Required:** The knight remains at the centre of the screen; the dungeon background
scrolls around it in all four directions as the player moves.  This is the
authoritative behaviour reported by the owner watching the real game.

**Why this matters:** Every other bug (facing direction, collision, speed) cannot be
properly evaluated until this is correct, because they all assume the wrong model.

**Status (2026-06-12): LIKELY FIXED-ROOM (moving sprite) — the current JS model is
probably correct.** After fixing the harness, a live decider (`scripts/decide_live.txt`)
showed the engine renders the warrior at a *variable* screen position driven by `$0325`
with a static BACKTAB — the opposite of a scrolling/pinned engine. The owner's
"scrolling" report is best explained as a symptom of `MOVE_SPEED≈0` + hard-cut
transitions. Final confirmation = an input-driven run (next step). See the ✅ RESOLVED
section above for the full evidence.

**Open question — MUST be resolved with a jzintv oracle before any code changes:**

Run the reference debug script (`scripts/debug_capture_gameplay.txt`), inject
directional input for several frames, and compare two addresses each frame:

| Address | Meaning |
|---------|---------|
| `$0000` | STIC shadow MOB-X register for MOB 0 (the warrior) |
| `$0325` | G_0325 — currently believed to be the warrior's STIC X |

If `$0000` stays at `0x58` (=88, screen centre) while `$0325` changes as the player
moves → the architecture is **scrolling viewport** (player centred, BACKTAB updates
each frame).  
If `$0000` tracks `$0325` and changes frame-to-frame → the architecture is **moving
MOB** (our current, apparently wrong, model).

The L_5EE2 routine writes all 240 BACKTAB tiles; confirm whether it is called
every frame (scrolling) or only on room transitions (fixed-room).  Look for the call
sites of L_5EE2 in the main loop at `$5072`.

Also confirm: if the architecture is scrolling, what is the "dungeon position"
register that L_5EE2 reads to decide which tiles to write?  Candidate: a separate
scroll-offset RAM word, likely near `$0325`.

---

### BUG-2 — Knight does not face the direction of travel

**Observed:** The sprite does not rotate to face the direction the player is moving.

**Background:** Five warrior frames are extracted from ROM `$5BCE` and stored in
`assets/player_sprites.json`.  The frame assignment in `src/main.ts` (around
line 193) has been changed multiple times without success.

**Required oracle work:**  
1. In a jzintv session, poke the disc direction register (locate via watch-diff on
   `$0100–$01EF` while pushing different disc directions).  
2. At each direction, dump the STIC A register (`m 0010 8`) and record which card
   number (bits 8–3 of the STIC A word) the ROM places in the warrior MOB slot.  
3. Map disc-direction → GRAM card number → frame index in `player_sprites.json`.

Do **not** guess at the mapping.  Until this oracle is run the frame assignment must
remain unchanged.

---

### BUG-3 — Wall collision is broken

**Observed:** The knight passes through walls or is stopped in open corridors.

**Root cause (likely):** `canMoveTo` in `src/engine/collision.ts` uses `bg === 11`
(olive floor) as the walkability predicate.  This is correct for floor tiles but has
not been validated against wall tiles, object tiles, and boundary tiles across all
six captured rooms.  The collision footprint is also a single tile point-sample;
the ROM may test a bounding box or multiple sample points.

**Required oracle work:**  
Run the jzintv input-driver (Section 3 of PORT_RUNBOOK.md), walk the knight into
walls from several angles, and dump `$0325`/`$032D` (player position) each frame.
If the ROM never lets `$0325` reach a wall tile's pixel boundary → confirm the
collision predicate and footprint by reading L_5323 and L_6054 carefully in
`asm/disasm_new.asm`.

---

### BUG-4 — Movement speed is wrong

**Observed:** Speed has been toggled between 0.5, 1.0, 1.5, 2.0 px/frame.  At 1.5
the owner reports it is "unrealistically fast."  The ROM value (G_017F = 0x32 = 50,
÷16 ≈ 3.1 STIC px/frame) was considered but not empirically verified.

**Required oracle work:**  
Using the jzintv input-driver, hold one disc direction for exactly N frames and
measure the change in `$0325` (player position).  `delta / N` = pixels per frame.
This is the authoritative speed.  Do **not** adjust `MOVE_SPEED` further without
this measurement.

Current value in `src/engine/movement.ts`: `MOVE_SPEED = 0.5` (placeholder, reset
from 1.5).  Do not change until the oracle is run.

---

## Controls — keyboard mapping (manual-sourced, implemented 2026-06-13)

Per the game manual ("HAND CONTROLLERS", `manual_pages/embedded_p02_00.jpeg`), the
Right Knight / Warrior Prince (the 1-player character) maps to the keyboard as:

| Manual control | Key | Status in JS |
|---|---|---|
| Disc — Move Prince (move + face) | Arrows / WASD | ✅ implemented |
| "Warrior Prince backs up" (move opposite facing, no turn) | **B** | ✅ implemented (`movement.ts` `backUp`) |
| "Pick up/store Treasures; open" | **Space** | wired to input, logic = P2 |
| "Stairs; use Lantern of Life" | **F** | ✅ stairs now button-gated (`main.ts`) |
| "Read Scroll" | **R** | wired to input, logic = P5 |
| "Call up Status Screen" | **Tab** | wired to input, logic = P5 |
| "Enter" / game-select (1/2/2-Magic) | **Enter**, **1/2/3** | wired to input, menu = P5 |

**Combat has NO button** — the manual states the Warrior "must strike them with his
sword" by **moving INTO** the enemy. Contact-based combat; build it that way in P3.
The 2-player Wizard's spell keypad (FREEZE/FIRE BALL/HEAL/…) is on the left overlay
(`embedded_p02_00.jpeg`) — defer to the 2-player pass.

The HUD now shows a live `Buttons:` line so the mapping is testable on screen.

---

## Combat (P3 first cut — manual-sourced, implemented 2026-06-13)

`src/engine/combat.ts` (+ wiring in `main.ts`, combat fields in `state.ts`). Rules from
the manual ("Evil Adversaries" p7, "Injuries, Cures & Reincarnations" p10):
- **Contact-based, no attack button** — the Prince strikes by *moving into* a foe.
  `resolveContact()`: if the Prince is moving + facing the foe → he strikes (foe dies);
  otherwise the foe injures him.
- **9 reincarnations**, each injury = **half a life**: white → **gray** (injured + stunned,
  can't move) → a further hit **kills** (flashing red **X**, lose a reincarnation, respawn at
  the entry point after a pause). Implemented in `injurePlayer()` / `tickPlayerCombat()`.
- A **Phantom Knight** spawns each room and chases the Prince (`updateEnemy()` chase AI,
  wall-respecting). HUD shows reincarnations / health / foe count.

**Placeholders to replace (NOT ROM-extracted):** enemy/player speeds, stun & respawn
lengths, the contact distance, and `PHANTOM_KNIGHT_SPRITE` (an inline placeholder — the
real monster sprites are GRAM cards ~0x23–0x33; extract like the warrior). Monster stat
tables + the exact damage/RNG model are still P2/P3 ROM-extraction work. Cures (Lantern of
Life + Enter) and the Wizard are not implemented yet.

⚠️ Combat positions are in the current fixed-room model; **if the architecture turns out to
be Prince-centred scrolling (see memory — the manual says it is), enemy/world positions
become camera-relative.** The combat *logic* (contact, HP, strike-first) is camera-agnostic.

---

## What Has Been Confirmed (do not re-derive)

| Fact | Source |
|------|--------|
| START_X = 0x58 = 88 (from ROM $5A40) | ROM analysis, session context |
| START_Y = 0x38 = 56 (from ROM $5A40–$5A41, SDBD) | ROM analysis, session context |
| HDLY ($0030) and VDLY ($0031) are set to 0 every VBlank at L_53A8 | `asm/disasm_new.asm` line 820–821 |
| `pixelToBacktabIndex` formula matches ROM L_6054 exactly | Verified |
| Room 0 tile (10,6) is walkable (bg=11); all 4 neighbours are also walkable | Python check |
| North boundary (Y<16) at col 10 is a wall tile (bg=0, not walkable) | Python check |
| Warrior sprite has 5 frames at ROM $5BCE; frame 4 is front-facing (symmetric) | Verified |
| `assets/player_sprites.json` bytes match ROM exactly | Verified |

---

## Files to Change (and what NOT to change)

| File | Status |
|------|--------|
| `src/engine/movement.ts` — `MOVE_SPEED` | Reset to 0.5 until BUG-4 oracle is done |
| `src/main.ts` — frame assignment | Do NOT change until BUG-2 oracle is done |
| `src/engine/collision.ts` — `canMoveTo` | Do NOT change until BUG-1 architecture is confirmed |
| `src/platform/stic.ts` — renderer | Correct, do not touch |
| `assets/player_sprites.json` | Correct, do not touch |
| `assets/rooms.json` | May be wrong if architecture is scrolling — verify after BUG-1 oracle |

---

## Recommended First Step — fix the oracle (Phase 0), then everything else follows

**You cannot measure anything until the game runs stably under jzintv.** The current
bypass HLTs after ~34 frames. Two routes to a stable gameplay harness:

**Route A — diagnose & patch the bad vector (most direct).**
1. Reproduce the halt: run `scripts/oracle_arch2.txt`; confirm `HALT!` in the output.
2. Enable history before it dies: in the script, after reaching gameplay, add `H`
   (toggle history), run a few frames, let it HLT; then the recent-PC trace shows the
   instruction that jumped to `$0000`. (`H` dumps to `dump.hst` via the `d` command —
   see `debug.c:142-145`.)
3. Work back: the jump target came from an uninitialised RAM pointer the bypass
   skipped. Initialise it with a `P`/`E` poke in the boot script, or NOP the derailing
   call, until the main loop survives indefinitely (instr count keeps climbing, no HLT).

**Route B — don't bypass the menu; select 1-player legitimately.**
The menu waits for a controller press. Drive it with a *real* input event instead of
forcing PC. jzintv has no `--demo` playback, and `P`-poking `$01FE/$01FF` is overwritten
by the pad emulation each frame — so try `E <port> <val>` (write **with** side effects)
on the PSG controller port, or set the PSG port-direction to output first. If the menu
advances to the dungeon and the game keeps running, the harness is healthy and properly
initialised (no skipped state).

**Once the harness is healthy, the original decider plan applies** (it was sound — only
the dead machine invalidated it). Hold one disc direction for N frames and dump
`$0000` (MOB-0 X shadow) and `$0325` (player X) each frame:
- `$0000` low byte stays 88 while the world (`$0200` BACKTAB) shifts → **scrolling** (BUG-1).
- `$0000` follows `$0325` and BACKTAB is static → **fixed-room** (current model).
- `(Δ$0325)/N` → authoritative `MOVE_SPEED` (BUG-4).
- Per-direction dump of the warrior MOB's STIC card → direction→frame table (BUG-2).

The disc-direction RAM variable still has to be found (watch-diff `$0100–$01EF` across a
held direction) — but that watch-diff is only meaningful **once the machine runs**, which
is why Phase 0 comes first.
