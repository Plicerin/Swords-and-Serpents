# Dungeon Tileset — Card Identity Map

The dungeon GRAM tileset (cards 0–33) is loaded from the ROM RLE block at `$61E7`
(see `reconstruct_dungeon_gram`). This maps the **low cards (0–15)** to their
in-game identities. Identities marked **[player]** were provided by a player who
knows the original game; **[data]** are confirmed against the ROM/traces;
**[read]** are my reading of the bitmap.

Frequencies are how often each card appears in the Level 1 background maze
(`level0_backtab.json`, from the boot-render scan).

| Card | In maze | Identity | Source / verification |
|---:|---:|---|---|
| 0 | ×4 | Horn / cornucopia — likely **decorative** | [player], tentative |
| 1 | ×5 | **Empty** (blank tile) | [player] + **[data]: GRAM card 1 is all-zero** |
| 2 | ×5 | **Empty** (blank tile) | [player] + **[data]: GRAM card 2 is all-zero** |
| 3 | ×127 | Wall (junction piece) | [read] — 2nd-most-common, structural |
| 4 | ×254 | **Primary wall** tile | [read] — most common tile in the maze |
| 5 | ×18 | Wall variant | [read] |
| 6 | ×4 | Wall fragment | [read] |
| 7 | ×12 | **Gate** — one half of an opening/closing gate | [player], tentative |
| 8 | ×11 | Wall (vertical segment) | [read] |
| 9 | ×0 | **Stairs down** | [player] + **[data]: byte-identical to card 10** |
| 10 | ×0 | **Stairs down** (pairs with 9 → 2-tile staircase) | [player] + **[data]: identical to card 9** |
| 11 | ×1 | **Scroll** (the manual's "scroll rooms" — Wizard learns spells) | [player] |
| 12 | ×1 | **Chest** / Store Room | [player] + **[data]: the one object the game places in Room 0, at spawn center (`$0E60`)** |
| 13 | ×0 | **Stairs up** (distinct from 9/10) | [player], tentative |
| 14 | ×0 | **Oil lamp** — decorative, no gameplay function | [player] |
| 15 | ×0 | **Minotaur mask** — decorative, no gameplay function | [player], tentative |

## Cards 16–33 (sprites — not used in the maze background; all ×0)

These are the upper RLE block, loaded into GRAM but never placed as background
tiles. Identities below are **[player]** game knowledge unless noted.

| Card | Identity | Notes |
|---:|---|---|
| 16 | **Crown** — likely decorative | [player] |
| 17 | **Dish** — likely decorative | [player] |
| 18 | **Shield** | [player] |
| 19 | **Helm** | [player] |
| 20 | **Harp** | [player] |
| 21 | **Potion** | [player] |
| 22 | **Key** | [player] + [read] (round head + shaft + teeth) — the level key |
| 23 | **Copyright © symbol** (reused from the title screen) | [player] |
| 24–33 | **Dragon sprite cards** — individual parts confirmed; assembly unverified | [player] + prior project work |

`dragon_tiles.png` shows cards 16–33. **Cards 24–33 are the Sinister Serpent
(dragon)'s individual sprite cards** — confirmed three ways: the player's read,
the handover naming them "dragon," and the earlier `sprites/characters/dragon.png`
(the same cards, colored green). What is **not** verified is how they *assemble*
into the dragon.

**Status: parts identified, assembly pending.** The dragon's assembled layout
lives only on the **lair screen** — the final boss area (red floor in
`game_ref.png`), reached *after completing all 4 levels*, per the manual
("Locate the lair of the Sinister Serpent"). It is **not a descendable dungeon
level**, so:
- Driving the `$6725` descent to reach it fails — chained jumps corrupt the
  stack and the renderer stops (verified).
- Reaching the lair requires *finishing the game*, which is blocked by the same
  controller-input gate that blocks character-select (the title input handler
  `$5684` is never reached without controller input).

Per project preference, the assembly is **left unverified rather than guessed**.
The real unlock is decoding the controller read so input can be injected — that
would let the game be played to the lair (and also unlock character-select, live
enemies, etc.).

## Notes & cross-references

- **Interactive objects** (placed by gameplay object code `L_63B9` from room data
  at `$64DE`, not the background): the **chest (12)**, **scroll (11)**, and
  **stairs (9/10 down, 13 up)**. Only the chest is present in the Room-0 spawn
  capture (verified). The stairs/scrolls appear elsewhere in the level and show
  ×0 in the spawn-area background scan.
- **Stairs ↔ level descent:** stepping on a down-stair triggers the descent
  handler at `$6725` (`G_019C += 1; JSR L_55F7; G_02F4 += 8`), the mechanism used
  to render Levels 2–4.
- **Decorative (no gameplay function):** cards 0 (horn), 14 (lamp), 15 (mask),
  and the wall-fragment variants. These are what an earlier prototype wrongly
  treated as "treasures" — corrected here.
- **Cards 16–33** (the rest of the RLE block) are not yet identified; the
  handover notes suggest dragon/serpent parts among them.

## Open questions

1. Why are cards 9 and 10 byte-identical (two GRAM slots for the same down-stair
   graphic)? Likely a 2-tile-wide staircase rendered from two tiles.
2. Card 13 ("stairs up") is a different graphic than 9/10 — the player noted it's
   odd they didn't just flip the down-stairs.
3. Confirm the gate (card 7) open/close behavior in the object dispatch (`L_6421`).
