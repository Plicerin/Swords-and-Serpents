# GROM Card Mapping — Title Screen, HUD, and Menu UI

## Summary

*Swords & Serpents* reuses the **same core 12-card tileset** across **all screens** — dungeon rooms, title screen, gameplay HUD, character selection, and class selection. The game does not load a separate UI tileset; instead, it copies a curated subset of GROM cards into GRAM and rearranges them to build each screen.

- **Unique cards used across all UI screens:** 12 / 256
- **Cards shared with dungeon rooms:** 10
- **UI-specific additions:** Card 32 (cursor/selector), Card 59 (vertical bracket/border)
- **GROM → GRAM copy:** All BACKTAB references point to GRAM, never directly to GROM

---

## How the Game Builds Each Screen

### Title Screen (`L_55BF` → `L_5EE2`)

The title screen is constructed by the same room renderer used for dungeons:

```
L_55BF:
  G_019C = 0              ; room index
  G_0175 = $0002          ; room data pointer (same table as dungeons)
  G_0176 = $001A          ; room parameter
  JSR L_5EE2              ; render room into BACKTAB
  ; then sets color stack at $017B for title-specific colors
```

This means the title screen background is technically a "room" rendered with parameter pair `($0002, $001A)`. The visible title text and decorations are then overlaid by modifying the color stack and possibly additional BACKTAB writes.

### Gameplay HUD

During gameplay, the engine leaves the top 2-3 rows of the 20×12 BACKTAB grid for the HUD, while the remaining rows show the dungeon room. The same wall/floor/decoration cards are reused, but placed in different spatial patterns:

- **Card 3** (floor) fills the dungeon viewport
- **Cards 35, 27, 43** form the dungeon walls
- **Cards 19, 11, 51, 56** decorate interior walls
- **Card 59** appears in the top/side border regions — likely framing the HUD area
- **Card 0** (blank) may clear unused HUD tiles

### Character / Class Selection Screens

These screens use an **identical BACKTAB layout** (confirmed by parsing `capture_char_select_out.txt` and `capture_class_select_out.txt`):

| Card | Count | Region | Role |
|------|-------|--------|------|
| 3 | 161 | Background fill | Floor / backdrop |
| 27 | 27 | Border/edges | Wall frame around selection area |
| 35 | 17 | Border/edges | Wall corners and structural lines |
| 43 | 8 | Border/edges | Pillar accents |
| 11 | 8 | Right side | Cross decorations |
| 19 | 6 | Mixed | Hanging fixtures |
| 59 | 5 | Mixed | Vertical brackets / dividers |
| 51 | 3 | Mixed | Sigils |
| 0 | 2 | Side | Blank spacers |
| 56 | 1 | Bottom | Ornate decoration |
| 2 | 1 | Bottom | Thin wall segment |
| **32** | **1** | **Central (10,6)** | **Cursor / selector icon** |

Card 32 is the only tile that appears strictly in the **central area** (coordinates 10,6), making it the selection cursor.

---

## Complete Card Index → Role Mapping (Unified)

### Background / Floor

| Card | Hex | Visual | Role |
|------|-----|--------|------|
| **0** | `0x00` | Empty | Blank / transparent spacer — used to clear tiles or leave gaps |
| **3** | `0x03` | Stippled grid | **Primary floor / background** — dominates every screen |

### Walls & Structure

| Card | Hex | Visual | Role |
|------|-----|--------|------|
| **2** | `0x02` | Two thin vertical bars | Narrow wall segment or pillar accent |
| **35** | `0x23` | C-shape / open square | **Primary wall tile** — builds walls, corners, frames |
| **27** | `0x1B` | Two vertical segments with gap | Wall edge, door frame, or boundary marker |
| **43** | `0x2B` | H-shape / ladder | Pillar, column, or thick vertical support |
| **59** | `0x3B` | Vertical bracket / bar | **UI border / divider** — frames HUD and menu panels |

### Decorative Elements

| Card | Hex | Visual | Role |
|------|-----|--------|------|
| **11** | `0x0B` | Plus / cross | Religious or magical cross motif on walls |
| **19** | `0x13` | Upside-down T / anchor | Hanging fixture, bracket, or ceiling mount |
| **51** | `0x33` | S / stylized number | Wall sigil, rune, or magical symbol |
| **56** | `0x38` | X / hourglass | Ornate symmetrical wall decoration |

### UI-Specific

| Card | Hex | Visual | Role |
|------|-----|--------|------|
| **32** | `0x20` | Box with inner pattern | **Cursor / selector icon** — appears only at center of char/class select |

---

## ASCII Art Reference (Unified Tileset)

```
Card 0 (0x00) — Blank / Transparent
  
  
  
  
  
  
  
  

Card 3 (0x03) — Floor / Background
        ##  ##
      ##########
        ##  ##
      ##########
        ##  ##

Card 2 (0x02) — Wall Segment (thin)
    ####    ####
    ####    ####

Card 35 (0x23) — Primary Wall
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

Card 43 (0x2B) — Pillar / Structural
  ####    ####
  ####    ####
  ####  ####
  ########
  ####    ####
  ####    ####
  ####    ####

Card 59 (0x3B) — Vertical Bracket / UI Border
        ########
        ####
        ####
        ####
        ####
        ####
        ####
        ########

Card 19 (0x13) — Hanging Bracket / Fixture
  ############
          ####
    ########
          ####
          ####
  ############

Card 11 (0x0B) — Cross Motif
      ####
      ####
  ############
      ####
      ####

Card 51 (0x33) — Sigil / Rune
  ############
  ####    ####
  ####
  ############
          ####
  ####    ####
  ############

Card 56 (0x38) — Ornate Decoration (X)
  ####    ####
  ####    ####
    ########
      ####
    ########
  ####    ####
  ####    ####

Card 32 (0x20) — UI Cursor / Selector
  ##############
  ##          ##
  ##  ######  ##
  ##  ##  ##  ##
  ##  ##########
  ##
  ##############
```

---

## Per-Screen Usage Matrix

| Card | Dungeon | Title | Gameplay HUD | Char Select | Class Select | Category |
|------|---------|-------|--------------|-------------|--------------|----------|
| 0 | — | ? | ✓ | ✓ | ✓ | Blank |
| 3 | ✓ | ✓ | ✓ | ✓ | ✓ | Floor |
| 2 | ✓ | ? | — | ✓ | ✓ | Wall |
| 35 | ✓ | ✓ | ✓ | ✓ | ✓ | Wall |
| 27 | ✓ | ✓ | ✓ | ✓ | ✓ | Wall/Frame |
| 43 | ✓ | ✓ | ✓ | ✓ | ✓ | Pillar |
| 59 | — | ? | ✓ | ✓ | ✓ | UI Border |
| 19 | ✓ | ? | ✓ | ✓ | ✓ | Decoration |
| 11 | ✓ | ? | ✓ | ✓ | ✓ | Decoration |
| 51 | ✓ | ? | ✓ | ✓ | ✓ | Decoration |
| 56 | ✓ | ? | — | ✓ | ✓ | Decoration |
| 32 | — | — | — | ✓ | ✓ | Cursor |

*Title screen card usage inferred from disassembly (`L_55BF` calls room renderer) rather than direct BACKTAB capture.*

---

## Technical Findings

### GROM → GRAM Copy Mechanism

Despite having a 256-card GROM, the game **never references GROM directly in BACKTAB**. All observed BACKTAB words have bit 13 = 0 (GRAM flag). The engine copies the needed subset of GROM cards into GRAM during screen setup, then references them via GRAM indices.

This is confirmed across:
- All 4 dungeon room BACKTAB dumps (`render_room_0_out.txt` through `render_room_3_out.txt`)
- Gameplay HUD BACKTAB dump (`gameplay_out.txt`)
- Character selection BACKTAB dump (`capture_char_select_out.txt`)
- Class selection BACKTAB dump (`capture_class_select_out.txt`)

### Screen-to-Screen Consistency

The character select and class select screens use **identical BACKTAB layouts** (same card counts at same positions). The only difference is the sprite/MOB overlay showing the warrior vs. wizard character portraits, which are drawn as MOBs (Mobile Objects) rather than BACKTAB tiles.

### The 12-Card Limit

The game operates with a remarkably small working set:
- **1** background tile (Card 3)
- **4** wall/structure tiles (Cards 2, 27, 35, 43)
- **1** UI border tile (Card 59)
- **5** decoration tiles (Cards 11, 19, 51, 56, 32)
- **1** blank tile (Card 0)

This is likely a deliberate memory optimization: by keeping the GRAM working set small, the game leaves GRAM space free for sprite graphics (MOBs) and dynamic tile modifications.

---

## Files Generated

| File | Description |
|------|-------------|
| `sprites/rooms/ui_cards_reference.png` | High-zoom labeled reference of all 12 unified cards |
| `sprites/rooms/GROM_CARD_MAPPING.md` | Dungeon-room-specific mapping (companion document) |
| `sprites/grom_tileset_labeled.png` | Full 256-card GROM tileset with index labels |
| `sprites/rooms/card_usage_analysis.txt` | Raw per-screen frequency statistics |

---

## Methodology

1. **Captured BACKTAB dumps** for gameplay HUD, character select, and class select via jzIntv debugger scripts
2. **Parsed** all 240 BACKTAB words per screen to extract card indices, GROM/GRAM flags, and colors
3. **Cross-referenced** card indices with `grom.bin` bitmaps to generate visual reference art
4. **Analyzed** position patterns (x, y coordinates) to infer tile roles by screen region
5. **Compared** per-screen usage to identify UI-specific cards (32, 59) and universal cards (3, 35, 27, etc.)
6. **Read disassembly** at `L_55BF` to understand title screen construction (calls room renderer)
7. **Verified** GROM vs. GRAM usage by checking bit 13 in all captured BACKTAB dumps
