# Swords and Serpents — Reverse Engineering Handover

## Project Overview

Reverse-engineering the 1982 IntelliVision game **Swords and Serpents** (Mattel Electronics). The ROM binary is `Swords and Serpents.bin`, mapped from address `$5000`. The CP-1610 CPU uses 16-bit DECLEs (stored big-endian in the ROM file: `(rom[off] << 8) | rom[off + 1]`).

---

## Quick Reference

| Item | Location | Details |
|------|----------|---------|
| ROM binary | `Swords and Serpents.bin` | $5000–$6FFF mapped |
| Disassembly | `disasm_new.asm` | 7,325 lines, CP-1610 |
| Full trace | `traces/first_room_run/trace_all.txt` | 915 KB, 96K cycles |
| STIC writes trace | `traces/first_room_run/trace_frames.txt` | ~1,700 BackTab writes |
| GRAM dump | `traces/first_room_run/dump_scratch_and_gram.txt` | Full GRAM contents |
| System RAM dump | `traces/first_room_run/ss_dump_system_ram.txt` | jzIntv memory map |

---

## ROM Data Map

### STIC MOB Configuration

| Address | Content | Details |
|---------|---------|---------|
| `$5A40–$5A9F` | Sprite definition table | 12 MOBs × 8 DECLEs each: X_pos, Y_pos, card/color, … |
| `$5BB5–$5BC0` | STIC A shadow registers | 12 MOB entries with FG color + card number + flags |
| `$5BC1–$5BCC` | Sprite metadata | Mixed hi-bytes (dimensions, grouping info) |

### STIC A Color Encoding (per MOB)

```
Bit 9   (Color Advance)  — when set, adds 4 to FG color
Bits 1-0 (FG color select) — 00, 01, 10, or 11
Combined FG color = (bit9 << 2) | bits[1:0]   → 3-bit value 0–7
```

For the title screen, `bit9=1` on all visible MOBs, giving FG colors 4, 5, or 6.

### IntelliVision 16-Color Palette (approximate RGB)

| # | Color | RGB |
|---|-------|-----|
| 0 | Black | `(0,0,0)` |
| 1 | Blue | `(0,0,255)` |
| 2 | Red | `(200,40,40)` |
| 3 | Tan | `(200,170,50)` |
| 4 | Dark Green | `(0,128,0)` |
| 5 | Green | `(0,255,0)` |
| 6 | Yellow | `(255,255,0)` |
| 7 | White | `(255,255,255)` |
| 8 | Grey | `(128,128,128)` |
| 9 | Cyan | `(0,255,255)` |
| 10 | Orange | `(255,150,0)` |
| 11 | Brown | `(150,130,100)` |
| 12 | Pink | `(255,100,150)` |
| 13 | Light Blue | `(100,200,255)` |
| 14 | Yellow-Green | `(200,200,0)` |
| 15 | Purple | `(150,60,200)` |

### Sprite Pixel Data

| Address | Source | Format | Cards | Description |
|---------|--------|--------|-------|-------------|
| `$5BCD–$5C48` | DECLE (ROM) | Count-marker + raw bytes (hi=0x00) | 14 (7 pairs) | Title screen character sprites |
| `$61E7–$62DF` | RLE (ROM) | Run-length encoded (hi-byte = repeat count, lo-byte = pixel byte) | 31 cards | Dungeon tiles + dragon parts |

#### DECLE Data Structure ($5BCD)
```
$5BCD: count marker ($0002 = 2 cards follow)
$5BCE: card 0, byte 0  ($0018)  ← Warrior top card starts here
...
$5C2F: count marker ($0001 = 1 card follows)
$5C30: more pixel data
```

Count markers have `hi=0x00` and `lo=1–8` (number of 8-byte cards that follow). The pixel data is stored as `hi=0x00, lo=pixel_byte`.

#### RLE Data Structure ($61E7)
```
$61E7: GRAM card offset (card number to start loading at)
$61E8: entry count (number of RLE entries)
$61E9+: RLE entries — each is 1 DECLE:
  hi-byte bits [15:14] = repeat count (1–4)
  lo-byte = pixel value
Example: $0102 → repeat 1× byte 0x02
         $0240 → repeat 2× byte 0x40
```

---

## Character Classification

### Title Screen Characters (DECLE $5BCD, 7 pairs)

| Pair | Name | Cards | STIC FG | Features |
|------|------|-------|---------|----------|
| 0 | **Warrior** (sword+shield) | 0+1 | 4 (Dark Green) | Humanoid, sword on right, shield left, symmetric (77%) |
| 1 | **Wizard** (robes+staff) | 2+3 | 5 (Green) | Humanoid, flowing robes, staff left side |
| 2 | **Serpent** | 4+5 | 6 (Yellow) | Elongated, no legs, serpentine |
| 3 | **Knight** (shield+armor) | 6+7 | 4 (Dark Green) | Dense blocky, shield left, heavy armor |
| 4 | **Knight** (ornate armor) | 8+9 | 4 (Dark Green) | Diamond lower body, 95% symmetric, heraldic |
| 5 | **Wizard** (spellcasting) | 10+11 | 5 (Green) | Checkerboard headpiece, magic staff |
| 6 | **Serpent** (coiled) | 12+13 | 6 (Yellow) | Sparse, coiled form |

### Dungeon & Dragon Tiles (RLE $61E7, 31 cards)

| Cards | Type | STIC FG | Usage |
|-------|------|---------|-------|
| 0–3 | **Dragon** head/body/neck | 6 (Yellow) | Composite dragon parts |
| 4–7 | **Dungeon** pillar cap + columns + double wall | 3 (Tan) | Pillar and wall segments |
| 8 | **Serpent** body coil | 5 (Green) | Serpentine coil pattern |
| 9 | **Decoration** border | 4 (Dark Green) | Ornamental border/corner |
| 10 | **Brick** texture | 3 (Tan) | Floor accent |
| 11 | **Dragon** body segment | 6 (Yellow) | Additional dragon body |
| 12, 16 | **Arch/portal** | 6 (Yellow) | Glowing archway |
| 13–15 | **Dragon** body/eye/wing | 6 (Yellow) | Additional dragon parts |
| 17 | **Wall** side (striped) | 3 (Tan) | Vertical wall segment |
| 18 | **Diamond** fill | 4 (Dark Green) | Decorative fill pattern |
| 19 | **Wall** base | 3 (Tan) | Bottom wall cap |
| 20 | **Floor** tile | 3 (Tan) | Rounded square pattern |
| 21–23 | **Dragon** body/wing | 6 (Yellow) | Lower dragon parts |
| 24 | **Column** capital | 3 (Tan) | Pillar top decoration |
| 25 | **Beam** bar | 3 (Tan) | Horizontal beam |
| 26–30 | **Dragon** wing/tail | 6 (Yellow) / 5 (Green) | Symmetric wings, tail |

---

## Key Render Scripts

All scripts read `Swords and Serpents.bin` directly and output to `sprites/`.

### 1. `render_colored_sprites.py` — Main Character Renderer

Renders all DECLE and RLE sprites with STIC register colors.

**Outputs:**
- `sprites/all_characters_labeled.png` — Full composite grid (14 DECLE + 14 RLE pairs)
- `sprites/color_comparison.png` — Side-by-side STIC vs alternate color per sprite
- `sprites/char_*.png` — Individual DECLE character sprites (7 files)
- `sprites/rle_*.png` — Individual RLE tile sprites (14 files)

**To run:** `python3 render_colored_sprites.py`

### 2. `render_dragon.py` — Dragon Sprite Assembly

Assembles 17 dragon RLE cards (0–3, 8, 11, 13–15, 21–23, 26–30) into a full dragon sprite.

**Outputs:**
- `sprites/dragon_wide.png` — 6×6 grid layout, wings spread wide
- `sprites/dragon_compact.png` — 5×5 grid layout, compact
- `sprites/dragon_card_reference.png` — All 17 dragon cards individually labeled

**To run:** `python3 render_dragon.py`

### 3. `render_dungeon_room.py` — Dungeon Room Mockup

Renders a complete dungeon room (16×12 tiles) using the dungeon wall/pillar/floor tiles.

**Outputs:**
- `sprites/dungeon_room_mockup.png` — Full room with walls, pillars, portal, legend
- `sprites/dungeon_tile_reference.png` — All 14 dungeon tiles individually labeled

**To run:** `python3 render_dungeon_room.py`

### 4. `label_sprites_final.py` — Earlier Classification Script

Original sprite classification and labeling (pre- STIC color work). May still be useful for raw analysis.

### Other Analysis Scripts

| Script | Purpose |
|--------|---------|
| `analyze_sprites.py` / `analyze_sprites_v2.py` | Raw pixel analysis of DECLE and RLE cards |
| `decode_sprite_pointers.py` | Decode sprite pointer tables |
| `render_gram.py` | Render GRAM cards from the dump |
| `render_rom_visualization.py` | Visualize ROM regions as sprites |
| `render_cards.py` | Generic card renderer |
| `render_animation_tables.py` | Render animation frame tables |
| `find_sprite_sheets.py` | Brute-force sprite sheet search |
| `inspect_clusters.py` / `inspect_tables.py` | ROM table inspection |
| `extract_trace.py` | Parse jzIntv trace output |

---

## Sprite Output Directory (`sprites/`)

Over 300 PNG files. Key highlights:

| File | Description |
|------|-------------|
| `all_characters_labeled.png` | Master composite — all sprites with STIC colors |
| `character_trio.png` | Showcase: Warrior + Wizard + Dragon |
| `color_comparison.png` | STIC color vs alternate palette comparison |
| `dragon_wide.png` | Dragon assembled (wide layout) |
| `dragon_compact.png` | Dragon assembled (compact layout) |
| `dungeon_room_mockup.png` | Complete dungeon room render |
| `dungeon_tile_reference.png` | Dungeon tiles labeled |
| `char_warrior_sword+shield.png` | Warrior in Dark Green |
| `char_wizard_robes+staff.png` | Wizard in Green |
| `char_serpent.png` | Serpent in Yellow |
| `char_knight_*.png` | Knight variants |
| `rle_dragon_*.png` | Individual dragon body parts |
| `rle_dungeon_*.png` | Individual dungeon tiles |

---

## jzIntv Emulator & Traces

### Trace Files (`traces/first_room_run/`)

The debugger script (`traces/first_room_debugger_script.txt`) captured execution during the first room of gameplay:

| File | Size | Content |
|------|------|---------|
| `trace_all.txt` | 915 KB | Complete CPU trace (~96K cycles) |
| `trace_frames.txt` | — | Per-frame STIC/BackTab write summary (~1,700 writes) |
| `trace_summary.txt` | — | High-level trace summary |
| `ss_trace_out.txt` | — | Main trace output with STIC writes |
| `dump_scratch_and_gram.txt` | — | Full GRAM dump |
| `dump_system_ram.txt` | — | jzIntv memory map + initialized state |
| `watch_0002.txt` | — | Watchpoint output for address $0002 |

### jzIntv Resources

- [jzIntv Debugger Guide](https://wiki.intellivision.us/index.php/Introducing_jzIntv%27s_Debugger)
- jzIntv is NOT currently installed on this system (traces were collected previously)

---

## Key Discoveries

1. **STIC color encoding**: Bit 9 (Color Advance) + bits 1–0 (FG select) → colors 4/5/6 for title screen MOBs
2. **DECLE format**: Count-marker-delimited pixel data with `hi=0x00` bytes; metadata bytes at $5BC1–$5BCC must be skipped
3. **RLE format**: 2-bit repeat counter in bits 15–14, 8-bit pixel value in bits 7–0; each entry expands to 1–4 bytes
4. **Dragon assembly**: 17 separate 8×8 cards form a composite dragon with symmetric wings, head facing left, tapering to a coiled tail
5. **Dungeon tiles**: 14 distinct tile types — walls, pillars (cap+column+base), portal/arch, floor, decorative elements
6. **Character roles**: Warrior (melee), Wizard (magic), Knight (defense), Serpent (enemy/monster)

---

## ROM Address Cheat Sheet

| Address | What | Format |
|---------|------|--------|
| `$5000` | ROM base | — |
| `$5A40` | Sprite definition table (12 MOBs × 8 DECLEs) | X, Y, card, … |
| `$5BB5` | STIC A shadow registers (12 entries) | FG color + card + flags |
| `$5BCD` | DECLE sprite count marker | `hi=0x00, lo=count` |
| `$5BCE` | Warrior top card (first pixel byte) | `$0018` |
| `$61E7` | RLE base: GRAM offset | Card number |
| `$61E8` | RLE entry count | — |
| `$61E9` | RLE data start | Run-length encoded bytes |

### Python Helper

```python
rom = open('Swords and Serpents.bin', 'rb').read()

def read_decle(addr):
    """Read a 16-bit DECLE from ROM at CP-1610 address."""
    off = (addr - 0x5000) * 2
    if off + 1 < len(rom):
        return (rom[off] << 8) | rom[off + 1]
    return None
```

---

## Next Steps (Suggested)

1. **Install jzIntv** and run fresh debugging sessions to capture more trace data (BackTab tile writes, MOB collisions, game state)
2. **Reconstruct the first room** from the captured BackTab writes — build a pixel-perfect replica of the actual first dungeon room
3. **Decode the game loop** from `disasm_new.asm` — trace the main dispatch, input handling, and enemy AI routines
4. **Extract animation frames** — the sprites likely have multiple animation frames; find the animation pointer tables
5. **Map the sound/music data** — IntelliVision uses the AY-3-8914 PSG; locate sound effect and music tables
6. **Create a playable level viewer** — combine the dungeon tile renderer with the BackTab trace to visualize any room
