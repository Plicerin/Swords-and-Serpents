# Swords & Serpents — Dungeon Room Extraction Summary

> **Note:** The "4 dungeon levels" finding and capture method below are still
> valid, but the **decode/rendering** notes here describe the old Color-Stack
> approach. The dungeon actually renders in **FG/BG mode** — see
> **`docs/room0_decode_findings.md`** for the current, correct pipeline.

## Finding: The Game Has Only 4 Dungeon Levels

After disassembling the room setup function (`L_59FF` at `$59FF`) and analyzing the room parameter table at `$5A17`, it is clear that **Swords & Serpents only has 4 dungeon levels** (indices 0–3). The room table contains exactly 4 parameter pairs:

| Level | G_0175 | G_0176 | Description |
|-------|--------|--------|-------------|
| 0     | `$0062` | `$000B` | Standard dungeon layout (type A) |
| 1     | `$000C` | `$001A` | Sparse / corridor layout |
| 2     | `$001B` | `$001C` | Standard dungeon layout (type B) |
| 3     | `$0062` | `$0004` | Standard dungeon layout (type C) |

Attempts to render "room 4" or "room 5" read past the table into executable code (`RSWD R3 = $003B` at `$5A1F`), which is **not valid room data**. Rooms 4–5 do not exist in this game.

## Output Files

| File | Description |
|------|-------------|
| `dungeon_levels_atlas.png` | 2×2 labeled atlas of all 4 dungeon levels |
| `level_0_labeled.png` – `level_3_labeled.png` | Individual labeled room renders |
| `dungeon_room_0.png` – `dungeon_room_3.png` | Raw 640×384 room renders |
| `render_room_0_out.txt` – `render_room_3_out.txt` | jzIntv debugger trace outputs with BACKTAB + GRAM dumps |
| `roomzero.png` | Authoritative Room 0 render (640×384, 4× zoom) from `derive_roomzero.py` |
| `room_0.png` | Reference render from `scripts/render_rooms_fixed.py` (160×96, native resolution) |

## How the Renders Were Captured

1. **Bypass title screen**: Patch boot code to skip idle loops (`$506A`) and set room parameters directly.
2. **Break after renderer**: Set a breakpoint at `$55DA`, immediately after `L_5EE2` (the room renderer) returns but before the title screen code wipes BACKTAB.
3. **Dump BACKTAB + GRAM**: Capture the 240-word BACKTAB (`$0200–$02EF`) and 512-word GRAM (`$3800–$39FF`) from the emulator.
4. **Decode and render**: Parse BACKTAB words into card indices, foreground colors, and color-stack advances; render each 8×8 tile using the actual GROM/GRAM bitmaps.

### Correct decode for rendering

When decoding BACKTAB words, use **bit 11** for the GRAM/GROM select:
```python
is_gram = (word >> 11) & 1   # 0 = GROM, 1 = GRAM
```

Earlier scripts incorrectly used bit 12, which produces a sprite-sheet artifact. The authoritative Room 0 render is produced by **`derive_roomzero.py`** in the project root, which uses the correct decode and the jzIntv-verified palette.

## Room Type Breakdown

- **Levels 0, 2, 3** use dense tile layouts with walls, floors, and decorative elements.
- **Level 1** is deliberately sparse — mostly empty floor tiles (`$1603`) with a few structural pieces. This appears to be an intentional "corridor" or "empty room" level type in the game design.

## Technical Note

The room parameter table at `$5A17` is read by `L_59FF` using:
```
index = (G_019C << 2) + (R1 << 1)
```
Where `G_019C` is the current dungeon level (0–3) and `R1` is a sub-index passed from the caller (determined by game state, e.g., player count or level variant). For our capture we used `sub=0` for all levels, which yields the primary layout for each level.
