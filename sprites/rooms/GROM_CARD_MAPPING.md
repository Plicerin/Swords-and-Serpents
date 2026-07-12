# GROM Card Mapping for Swords & Serpents Dungeon Rooms

> ⚠️ **STALE — do not rely on the card numbers below.** This mapping was built
> with a wrong (low-byte, `word & 0xFF`) BACKTAB decode. The structural tiles
> actually reference **GRAM** cards via the FG/BG-mode decode (bit 11 = GRAM),
> not the GROM cards listed here. See **`docs/room0_decode_findings.md`** for the
> correct decode. Kept for historical context only.

## Summary

Only **12 of the 256 GROM cards** are used to render dungeon rooms in *Swords & Serpents*. The game reuses a small core tileset across all 4 dungeon levels, with variations achieved through different spatial layouts of the same cards.

- **Total tile placements across 4 rooms:** 960 (240 cards × 4 rooms)
- **Unique GROM cards used:** 12 / 256
- **Most common tile:** Card 3 (0x03) — 745 placements (77.6%)

---

## Card Index → Tile Type Mapping

### Floor / Background

| Card | Hex | Placements | Visual Description | Role |
|------|-----|------------|--------------------|------|
| **3** | `0x03` | 745 | Stippled / dotted grid pattern | **Primary floor tile** — fills the vast majority of room interiors |

Card 3 is the dominant tile. Its stippled checkerboard pattern gives the dungeon floor a textured stone appearance. It appears in every room at every interior position not occupied by walls or decorations.

---

### Walls & Structure

| Card | Hex | Placements | Visual Description | Role |
|------|-----|------------|--------------------|------|
| **35** | `0x23` | 109 | C-shape / open square | **Primary wall tile** — forms walls, corners, and building blocks |
| **27** | `0x1B` | 68 | Two vertical segments with dot | **Wall edge / door frame** — used at boundaries and openings |
| **43** | `0x2B` | 11 | H-shape / ladder | **Pillar / structural decoration** — vertical support or wall detail |
| **2** | `0x02` | 3 | Two vertical bars | **Wall segment / narrow pillar** — occasional vertical structural accent |

Card 35 is the main wall-building tile. Its open-box shape (like a "C" or "U") connects with adjacent wall tiles to form continuous wall lines. Card 27 appears at door-like openings and screen edges. Card 43 forms thicker vertical pillars. Card 2 is a thinner vertical accent.

---

### Decorative Elements

| Card | Hex | Placements | Visual Description | Role |
|------|-----|------------|--------------------|------|
| **56** | `0x38` | 6 | X / hourglass | **Ornate wall decoration** — symmetrical cross pattern |
| **51** | `0x33` | 5 | S / 5 shape | **Wall sigil / rune** — stylized letter or number pattern |
| **64** | `0x40` | 5 | Diagonal stroke | **Small accent mark** — tiny directional detail |
| **19** | `0x13` | 4 | Upside-down T / anchor | **Hanging fixture / bracket** — top-heavy structural detail |
| **11** | `0x0B` | 2 | Plus / cross | **Cross motif** — religious or magical symbol on walls |
| **91** | `0x5B` | 1 | Mirror-C / bracket | **Corner bracket** — right-side wall fixture |
| **83** | `0x53` | 1 | S-shape | **Alternate sigil** — variation of Card 51 |

Decorations are sparse (21 total placements across all rooms) and always placed on interior wall surfaces or in alcoves. They add visual variety to otherwise repetitive wall structures.

---

## Per-Room Usage

| Card | Room 0 | Room 1 | Room 2 | Room 3 | Category |
|------|--------|--------|--------|--------|----------|
| 3 (0x03) | ✓ | ✓ | ✓ | ✓ | Floor |
| 35 (0x23) | ✓ | ✓ | ✓ | ✓ | Wall |
| 27 (0x1B) | ✓ | ✓ | ✓ | ✓ | Wall/Frame |
| 43 (0x2B) | ✓ | ✓ | ✓ | ✓ | Pillar |
| 56 (0x38) | ✓ | ✓ | ✓ | ✓ | Decoration |
| 51 (0x33) | ✓ | ✓ | ✓ | ✓ | Decoration |
| 64 (0x40) | ✓ | ✓ | ✓ | ✓ | Decoration |
| 19 (0x13) | ✓ | — | — | ✓ | Decoration |
| 2 (0x02) | ✓ | — | ✓ | ✓ | Wall/Pillar |
| 11 (0x0B) | ✓ | — | — | ✓ | Decoration |
| 91 (0x5B) | ✓ | — | — | — | Decoration |
| 83 (0x53) | — | — | ✓ | — | Decoration |

---

## ASCII Art Reference

```
Card 3 (0x03) — Floor
        ##  ##
      ##########
        ##  ##
      ##########
        ##  ##

Card 35 (0x23) — Wall
  ############
  ####    ####
  ####
  ####
  ####
  ####    ####
  ############

Card 27 (0x1B) — Wall Edge / Door Frame
        ####
        ####
        ####
        ####
          ##

Card 43 (0x2B) — Pillar
  ####    ####
  ####    ####
  ####  ####
  ########
  ####    ####
  ####    ####
  ####    ####

Card 56 (0x38) — Decoration (X/Hourglass)
  ####    ####
  ####    ####
    ########
      ####
    ########
  ####    ####
  ####    ####

Card 51 (0x33) — Decoration (Sigil)
  ############
  ####    ####
  ####
  ############
          ####
  ####    ####
  ############

Card 64 (0x40) — Decoration (Accent)
            ##
              ##
                ##

Card 19 (0x13) — Decoration (Bracket)
  ############
          ####
    ########
          ####
          ####
  ############

Card 2 (0x02) — Wall Segment
  ####    ####
  ####    ####

Card 11 (0x0B) — Decoration (Cross)
      ####
      ####
  ############
      ####
      ####

Card 91 (0x5B) — Decoration (Corner Bracket)
        ######
        ##
        ##
    ####
        ##
        ##
        ######

Card 83 (0x53) — Decoration (Alternate Sigil)
  ############
  ####
  ############
          ####
  ############
```

---

## Methodology

1. **Captured** all 4 dungeon room BACKTAB dumps via jzIntv debugger scripts
2. **Extracted** all 240 card indices per room (20 columns × 12 rows)
3. **Cross-referenced** each unique card index with its 8-byte GROM bitmap from `grom.bin`
4. **Analyzed** placement frequency and screen position patterns
5. **Categorized** tiles by visual appearance and positional context (edge vs. interior, frequency, symmetry)

## Unified Tileset Discovery

This 12-card set is **not dungeon-specific**. The same cards are reused for the **title screen, gameplay HUD, character selection, and class selection** screens. The game copies these GROM shapes into GRAM and rearranges them to build every screen in the game.

Two UI-specific cards augment this set:
- **Card 32 (0x20)** — Cursor / selector icon (appears only on character/class select screens)
- **Card 59 (0x3B)** — Vertical bracket / UI border (frames HUD and menu panels)

See the companion document **`GROM_CARD_MAPPING_UI.md`** for the full cross-screen analysis.

---

## Files Generated

- `sprites/grom_tileset_labeled.png` — Full 256-card GROM tileset with index labels
- `sprites/rooms/used_cards_reference.png` — Large zoom render of the 12 dungeon cards
- `sprites/rooms/ui_cards_reference.png` — High-zoom labeled reference of all 12 unified cards (dungeon + UI)
- `sprites/rooms/card_usage_analysis.txt` — Raw frequency and position statistics
- `sprites/rooms/dungeon_room_0.png` — `dungeon_room_3.png` — Rendered dungeon rooms for visual cross-check
