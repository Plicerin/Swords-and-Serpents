# Swords and Serpents — Reverse Engineering Project

This repository contains reverse-engineering tools, analysis scripts, and a custom renderer for the 1982 Intellivision dungeon crawler **Swords and Serpents** (Imagic).

The project reconstructs the game's dungeon rooms by decoding Intellivision STIC video data (BACKTAB, GRAM, GROM) from jzIntv emulator memory dumps. The decode and palette are validated against jzIntv's own source (`vendor/jzintv-src/`), not just screenshots.

> **The authoritative, current write-up of how Room 0 renders is [`docs/room0_decode_findings.md`](docs/room0_decode_findings.md).** Read it first — it supersedes older notes in this repo (e.g. the "Color Stack mode" assumption and `GROM_CARD_MAPPING.md`).

---

## Directory Structure

| Directory | Contents |
|-----------|----------|
| **Root** | Core rendering pipeline and analysis scripts that share local imports |
| `tools/` | Standalone reusable utilities — decoders, dumpers, extractors, renderers for specific data types |
| `analysis/` | One-off experimental / reverse-engineering scripts — analyzers, simulators, solvers, tracers |
| `docs/` | Documentation, notes, and debugger scripts |
| `archive/` | Legacy logs, debug dumps, and temporary outputs |
| `asm/` | Disassembly listings |
| `sprites/` | Generated sprites, decoded boot GRAM, and room output images |
| `traces/` | jzIntv emulator memory dumps and trace logs |

---

## Prerequisites

- Python 3.10+
- [Pillow](https://pillow.readthedocs.io/) (`pip install Pillow`)

---

## Rendering Pipeline

The project supports two rendering approaches:

### Hybrid approach (reference-based)
1. jzIntv reference GIFs (in `sprites/comparisons/`) provide the base playfield image — this preserves the emulator's exact native color rendering for non-overlay pixels.
2. Blue emulator overlay pixels are replaced with colors derived from BACKTAB + card bitmap analysis.
3. White emulator text (copyright, FPS, debugger info) is filtered out from the top tile rows.

### Pure emulator trace approach
`derive_roomzero.py` renders Room 0 from a jzIntv debugger trace (`traces/rooms/render_room_0_out_*.txt`).

```bash
python derive_roomzero.py
```

Output: `roomzero.png` (640×480, 4:3 aspect-corrected)

The render is a complete scene — dungeon **plus** the player sprite — built entirely from real game data. The key findings (all in `docs/room0_decode_findings.md`):

1. **The dungeon uses FG/BG mode, not Color Stack mode.** The screen-setup routine at `$53B5` *writes* STIC mode-select `$0021` (which selects FG/BG mode) and skips the read that would select Color Stack mode. So each BACKTAB tile carries its own foreground/background color — the floor (`$1603`) is GROM card 0 on an olive-green background, and walls sit on black. The decode follows jzIntv's `stic_draw_fgbg` exactly (`render_all_rooms.decode_fgbg_word`), using the authoritative jzIntv palette (`JZINTV_PALETTE`).

2. **The data is a real gameplay capture.** `scripts/debug_capture_gameplay.txt` drives the emulator into the actual first dungeon headlessly — it pokes `G_018C=1` and forces `PC` to the player-count check (`$56C9`), bypassing the keypad menu (which waits for a controller press). `derive_roomzero.py` uses the captured BACKTAB **and** GRAM. (Fallback: `reconstruct_dungeon_gram()` rebuilds the tiles from the ROM's RLE loader — byte-identical to the captured GRAM.)

3. **The player (Warrior/Prince) is overlaid as a hardware sprite (MOB).** `parse_room_mobs()` decodes the MOB from the SYSRAM shadow; `reconstruct_mob_sprite_gram()` rebuilds the Warrior's opening-position sprite from the ROM (char-select, which loads it, is bypassed by the headless capture). MOBs render at 2× vertical resolution (one tile tall), and the sword is drawn as a line east. Validated against a real game screenshot (`game_ref.png`).

4. **Pixel-aspect correction.** The square-pixel render is stretched ×1.25 vertically to the 4:3 TV proportions seen in the manual.

The room structure matches the reference GIF tile-for-tile (floor, walls, chest, hourglass), and the player's shape, size, and position match the real game.

> **Cosmetic / data notes.** (1) Floor hue differs — this build's palette renders olive `(84,110,0)`; the reference GIF used `(58,138,0)`: same color *index*, different RGB. (2) The sword is *drawn* (the real sword-MOB was inactive in the idle capture) and assumed east-facing. (3) Enemies appear only during combat. See `docs/room0_decode_findings.md`.

### Render a single room (hybrid)

```bash
python render_room.py <room_number>
```

Example:
```bash
python render_room.py 0
```

Output: `sprites/rooms/room_0.png` (1280×768, 8× zoom)

### Render all rooms

The game only has 4 valid dungeon levels (0–3). Rooms 4–5 read past the room parameter table at `$5A17` and produce garbage.

```bash
python render_room.py 0
python render_room.py 1
python render_room.py 2
python render_room.py 3
```

### Generate a montage of all rooms

```bash
python montage_rooms.py
```

Output: `sprites/rooms/dungeon_montage.png`

### Generate an animated dungeon walk GIF

```bash
python animated_dungeon.py
```

Output: `sprites/rooms/dungeon_walk.gif`

---

## Key Files

| File | Purpose |
|------|---------|
| `derive_roomzero.py` | **Authoritative Room 0 renderer** — FG/BG-mode decode + captured/reconstructed GRAM + player sprite (Warrior) + drawn sword + 4:3 aspect correction. Output `roomzero.png` |
| `render_room.py` | Main room renderer — uses jzIntv GIF + BACKTAB analysis (hybrid approach) |
| `render_all_rooms.py` | Central decoding module — GROM/GRAM loaders, BACKTAB parsers, empirical color tables |
| `scripts/render_rooms_fixed.py` | Fixed renderer that uses the correct bit 11 GRAM/GROM select (corrects earlier decode bugs) |
| `montage_rooms.py` | Stitches all 6 room PNGs into a single montage image |
| `animated_dungeon.py` | Builds an animated GIF cycling through all rooms |
| `build_clean_room0.py` | Reference-based renderer for room 0 (used to validate the pipeline) |
| `grom.bin` | Intellivision Graphics ROM (GROM) — contains the game's card graphics |
| `exec.bin` | Intellivision EXEC ROM |
| `Swords and Serpents.bin` | The game cartridge ROM |

---

## Data Sources

- **ROM images**: `Swords and Serpents.bin`, `exec.bin`, `grom.bin`
- **Memory dumps**: `traces/rooms/render_room_{N}_out.txt` — jzIntv debugger dumps containing BACKTAB, GRAM, and Color Stack data
- **Reference GIFs**: `sprites/comparisons/room_{N}_jzintv.gif` — jzIntv screenshot captures used as the rendering base

---

## How It Works (Brief)

> This summarizes the **`derive_roomzero.py`** path (the accurate one). See `docs/room0_decode_findings.md` for the full account and citations into jzIntv's source.

1. **Mode**: The dungeon runs in STIC **FG/BG mode** (set at `$53B5`), *not* Color Stack mode — the original project assumption. Each BACKTAB word carries its own foreground and background color.
2. **BACKTAB decode** (per jzIntv `stic_draw_fgbg`): `card# = (word>>3)&0x3F`, `is_gram = word&0x800` (bit 11), `fg = word&7`, `bg = ((word>>9)&0xB)|((word>>11)&0x4)`. The floor (`$1603`) is a blank GROM card on an olive-green (color 11) background; walls are GRAM cards (tan) on black.
3. **GRAM**: Dungeon tile cards (3–33) come from the gameplay-captured GRAM, or are rebuilt from the ROM's RLE loader (`$61E7`); they are byte-identical. Player/enemy sprite cards (48+) come from the ROM sprite block (`$5BCD`).
4. **Palette**: `JZINTV_PALETTE` — the exact 16 colors from jzIntv's `gfx_stic_palette`. (The older `PALETTE`/`PASTEL_PALETTE`, sampled from a screenshot, are kept only for legacy/hybrid paths.)
5. **Sprites & aspect**: Hardware MOBs are overlaid at 2× vertical resolution; the image is stretched ×1.25 vertically for the Intellivision's 4:3 pixel aspect.

---

## Contributing Analysis

If you want to run one-off analysis scripts, explore the `analysis/` directory. Most scripts are standalone and can be run directly:

```bash
python analysis/analyze_backtab_tables.py
```

---

## License

This is a personal reverse-engineering project for educational purposes. All original game assets belong to their respective copyright holders.
