# BACKTAB Construction Pipeline — End-to-End Analysis
## Swords and Serpents (Intellivision)

---

## 1. OVERVIEW

The BACKTAB is the Intellivision's 20×12 background tile table at STIC addresses $0200–$02EF (240 words). Each word encodes a card number and color information. The game constructs BACKTAB in three layers:

| Layer | Function | What it writes |
|-------|----------|---------------|
| Background | `L_5EC7` (called from `L_5EE2`) | Background tiles with colors |
| Room objects | `L_63B9` | Object card numbers (no colors) |
| Color injection | `L_6445` (via `L_63F5`) | Color prefix before type-7 objects |

The rendering orchestration is driven from `L_55BF` (room init) and `L_55F7` (room render).

---

## 2. BACKGROUND RENDERING — L_5EC7

**Called from**: `L_5EE2` → loop writing to BACKTAB $0200–$02EF

**Inputs**:
- `G_02F5` = `$65B7` — tile map base (19 words at $65B7–$65DB)
- `G_02F4` = `$65DC` — secondary data table (at $65DC+)
- Color table = `$65A0` — 12 words of color data ($65A0–$65B6)
- `G_0175` = starting tile index
- `G_0176` = row count

**Algorithm**:
```
L_5EC7(tile_index):
    idx = tile_index >> 5           # SLR×2, SLR (divide by 32)
    
    # Read tile map entry
    tile_entry = ROM[$65B7 + idx]   # MVI@ R3
    
    # Extract bit pattern from tile entry
    temp = tile_entry >> 2          # SLR R1,2
    temp = SWAP(temp)               # Swap bytes
    temp ^= tile_entry              # XOR with original
    r1 = temp & 0x3607              # Mask: bits 13,12,10,9, 2,1,0
    
    # Read color value
    color = ROM[$65A0 + idx]        # MVI@ R5
    
    # Combine
    color_shifted = color << 3      # SLL×2, SLL
    backtab = r1 ^ color_shifted    # XORR
    
    return backtab
```

**Actual tile map + color table output** (from simulation):

| Tile Index | BACKTAB Word | Card | FG | BG | GRAM |
|-----------|-------------|------|----|----|------|
| 0–10 (sampled) | **$1E02** | $02 | 3 | 3 | 0 |

The background uses card $02 (a blank/wall tile) with FG=3, BG=3 in FG/BG mode.

### Color Table Data ($65A0–$65B6)
```
[ 0] $65A0: $01C4 → <<3 = $0E20 (bits: 5)
[ 1] $65A2: $0104 → <<3 = $0820 (bits: 5)
[ 2] $65A4: $03C4 → <<3 = $1E20 (bits: 5)
[ 3] $65A6: $03C4 → <<3 = $1E20 (bits: 5)
[ 4] $65A8: $03C0 → <<3 = $1E00 (bits: none → all zeros after shift)
[ 5] $65AA: $01C2 → <<3 = $0E10 (bits: 4, 9)
[ 6] $65AC: $03C0 → <<3 = $1E00
[ 7] $65AE: $03C2 → <<3 = $1E10 (bits: 4, 9)
[ 8] $65B0: $03C0 → <<3 = $1E00
[ 9] $65B2: $03C0 → <<3 = $1E00
[10] $65B4: $01C3 → <<3 = $0E18 (bits: 3, 4, 9)
[11] $65B6: $01C0 → <<3 = $0E00 (bits: none)
```

### Tile Map Data ($65B7–$65DB)
19 entries encoding which background patterns to draw for each screen section.

---

## 3. ROOM OBJECT RENDERING — L_63B9

**Called from**: Room rendering loop (called for each of up to 16 room objects)

**Inputs**:
- R0 = column (X position, 0–19)
- R1 = row (Y position, 0–11)
- R4 = pointer into room data array ($64DE+)

**Target**: BACKTAB address = `$0200 + X + Y×20`

**Algorithm**:
```
L_63B9(col, row, room_data_ptr):
    # Calculate BACKTAB destination
    backtab_addr = $0200 + col + row*20   # R5
    
    # Extract type index from room data
    adjusted = room_data_ptr - $64E0       # SUBI #$64E0 (SDBD prefix)
    
    # RRC R1,2 / RLC R0,2: extract nibble selector
    nibble_index = adjusted >> 2
    nibble_sel = adjusted & 3             # bits 1:0
    
    # Read type index table
    type_word = ROM[$6580 + nibble_index]
    
    # Extract 4-bit type number from nibble
    if nibble_sel.bit1:
        raw_type = (type_word >> 5) & 0x1F   # SLR×2, SLR×2, SLR
    elif nibble_sel.bit0:
        raw_type = (type_word >> 4) & 0xF
    else:
        raw_type = type_word & 0xF
    
    # Check discovery/active flags
    if raw_type < 7:
        flag_addr = $0180 + G_019C       # Player-specific flags
        bit = 1 << raw_type              # L_5546: R0 << R2
        if (RAM[flag_addr] & bit) == 0:  # L_646A
            return                        # Object not yet discovered
    
    # Read object card from object table
    obj_addr = $655E + raw_type * 2      # + SDBD prefix
    obj_word = ROM[obj_addr]             # SDBD MVI@
    
    # Write to BACKTAB
    BACKTAB[backtab_addr] = obj_word     # MVO@ R0, R5
```

### Object Table ($655E–$659D) — Interleaved 16-bit structure

**Raw bytes at $655E**:
```
+00: 00 7E | 00 1E | 00 87 | 00 1E | 00 8E | 00 1E | 00 90 | 00 1E
+10: 00 98 | 00 1E | 00 A6 | 00 1E | 00 AE | 00 1E | 00 B0 | 00 1E
+20: 00 76 | 00 1E | 00 60 | 00 0E | 00 6B | 00 08 | 00 4B | 00 08
+30: 00 53 | 00 1E | 00 5B | 00 1E | 00 5B | 00 5E | 00 5B | 00 9E
```

**Structure**: The table is an interleaved array where even-indexed 16-bit words hold actual card numbers (low byte = card, high byte = $00) and odd-indexed words hold $001E (likely a termination/placeholder sentinel).

**Effective entries** (even type numbers only, since `type*2` indexes by 16-bit words):

| Type*2 Offset | Type | ROM Word | Card (low byte) | Notes |
|---------------|------|---------|-----------------|-------|
| 0 | 0 | $007E | $7E → $3E masked | Wall/block |
| 2 | 1 | $001E | $1E | Placeholder? |
| 4 | 2 | $0087 | $87 → $07 masked | |
| 6 | 3 | $001E | $1E | |
| 8 | 4 | $008E | $8E → $0E masked | |
| 10 | 5 | $001E | $1E | |
| 12 | 6 | $0090 | $90 → $10 masked | |
| 14 | 7 | $001E | $1E | |
| 16 | 8 | $0098 | $98 → $18 masked | |
| 18 | 9 | $001E | $1E | |
| 20 | 10 | $00A6 | $A6 → $26 masked | |
| 22 | 11 | $001E | $1E | |
| 24 | 12 | $00AE | $AE → $2E masked | |
| 26 | 13 | $001E | $1E | |
| 28 | 14 | $00B0 | $B0 → $30 masked | |
| 30 | 15 | $001E | $1E | |
| 32 | 16 | $0076 | $76 → $36 masked | |
| 34 | 17 | $001E | $1E | |
| 36 | 18 | $0060 | $60 → $20 masked | |
| 38 | 19 | $000E | $0E | |
| 40 | 20 | $006B | $6B → $2B masked | Treasure/chest |
| 42 | 21 | $0008 | $08 | |
| 44 | 22 | $004B | $4B → $0B masked | |
| 46 | 23 | $0008 | $08 | |
| 48 | 24 | $0053 | $53 → $13 masked | |
| 50 | 25 | $001E | $1E | |
| 52 | 26 | $005B | $5B → $1B masked | Common object |
| 54 | 27 | $001E | $1E | |
| 56 | 28 | $005B | $5B → $1B masked | |
| 58 | 29 | $005E | $5E → $1E masked | |
| 60 | 30 | $005B | $5B → $1B masked | |
| 62 | 31 | $009E | $9E → $1E masked | |

**Important**: The `SDBD` prefix before `MVI@ R4, R0` at L_63F1 causes the read to load a full 16-bit word from ROM (rather than the normal 10-bit read). The high byte ($00) is discarded when the card is written to BACKTAB (which only uses the low 8 bits). The actual displayed card = `byte & 0x3F` (6-bit card number).

### Type Index Table ($6580–$659F) — 16 words, 4 nibbles each

Each 16-bit word packs 4 nibbles (0–15), each selecting a type index:

```
[ 0] $6580: [01,CD] nibbles=[D,C,1,0]
[ 1] $6582: [01,0A] nibbles=[A,0,1,0]
[ 2] $6584: [00,07] nibbles=[7,0,0,0]
[ 3] $6586: [00,83] nibbles=[3,8,0,0]
[ 4] $6588: [01,4C] nibbles=[C,4,1,0]
[ 5] $658A: [02,0F] nibbles=[F,0,2,0]
[ 6] $658C: [00,20] nibbles=[0,2,0,0]
[ 7] $658E: [00,A4] nibbles=[4,A,0,0]
[ 8] $6590: [01,4C] nibbles=[C,4,1,0]
[ 9] $6592: [02,0F] nibbles=[F,0,2,0]
[10] $6594: [00,20] nibbles=[0,2,0,0]
[11] $6596: [00,A4] nibbles=[4,A,0,0]
[12] $6598: [01,AC] nibbles=[C,A,1,0]
[13] $659A: [00,50] nibbles=[0,5,0,0]
[14] $659C: [00,83] nibbles=[3,8,0,0]
[15] $659E: [00,42] nibbles=[2,4,0,0]
```

**Nibble extraction logic** (from L_63B9): `adjusted = ROM_ptr - $64E0`. Then `nibble_index = adjusted >> 2`, `nibble_sel = adjusted & 3`. If `nibble_sel & 2` → shift right 5 (upper nibble pair). Otherwise `nibble_sel & 1` selects high vs low nibble. This maps each room entry's byte offset to a specific type index.

### Room Data ($64DE–$655D) — 40 words (up to 16 objects)

Each room entry is stored as 10-bit DECLE values. The first room's data:

| Entry | Offset | Word | X (low) | Y (high) | Type (via index) | Card | BACKTAB |
|-------|--------|------|---------|----------|-------------------|------|---------|
| 0 | $64DE | $0014 | $14 | $00 | 13 | $1B | $0214 |
| 1 | $64E0 | $006C | $6C | $00 | 12 | $13 | $026C |
| 2 | $64E2 | $004C | $4C | $00 | 14 | $1B | $024C |
| 3 | $64E4 | $004C | $4C | $00 | 14 | $1B | $024C |
| 4 | $64E6 | $006C | $6C | $00 | 10 | $2B | $026C |
| 5 | $64E8 | $003A | $3A | $00 | 0 | $3E | $023A |
| 6 | $64EA | $005C | $5C | $00 | 8 | $36 | $025C |
| 7 | $64EC | $000C | $0C | $00 | 8 | $36 | $020C |
| 8 | $64EE | $0026 | $26 | $00 | 7 | $30 | $0226 |
| 9 | $64F0 | $0033 | $33 | $00 | 0 | $3E | $0233 |
| 10 | $64F2 | $004F | $4F | $00 | 0 | $3E | $024F |
| 11 | $64F4 | $000C | $0C | $00 | 0 | $3E | $020C |
| 12 | $64F6 | $002F | $2F | $00 | 3 | $10 | $022F |
| 13 | $64F8 | $0071 | $71 | $00 | 8 | $36 | $0271 |
| 14 | $64FA | $0006 | $06 | $00 | 4 | $18 | $0206 |
| 15 | $64FC | $002B | $2B | $00 | 4 | $18 | $022B |

**Note**: All Y values are $00 in this room data. The X values appear to be world coordinates (0–255 range), not screen coordinates (0–19). The objects are likely placed in the room using a different coordinate system and converted during rendering.

---

## 4. COLOR INJECTION — L_6445

**Reached via**: `L_63F5` → `L_6436` when type-7 object is found

**What it does**: Writes a **color prefix cell** before the object in BACKTAB.

```
L_6445:
    DECR R4                    # Back up one BACKTAB cell
    MVII #$0016, R0
    SWAP R0, 1                 # R0 = $1600
    MVO@ R0, R4                # Write color prefix to BACKTAB[X-1]
    
    # Toggle discovery flag
    MVII #$019D, R1
    ADD G_019C, R1             # R1 = $019D + player
    JSR L_6459                 # Toggle bit at RAM[R1]
    
    # Clear active flag
    MVII #$0180, R1
    ADD G_019C, R1             # R1 = $0180 + player
    JSR L_6466                 # Clear bit at RAM[R1]
```

**Color prefix breakdown**:
- `$1600` = FG/BG mode, GROM, FG=6 (tan), BG=0 (black), card=0
- For player 2: might use different color (not yet confirmed)
- The card number (0) means this cell is "empty" — it only provides color

This is the **key mechanism** for giving objects their displayed color. The color prefix cell sits at column X-1, and the object card at column X inherits colors from it via the Intellivision's FG/BG rendering mode.

---

## 5. POST-RENDER OBJECT SCANNING — L_63F5

**Purpose**: After rendering, scan the BACKTAB around the player's position to find and process interactive objects.

**Called from**: Room update loop

```
L_63F5:
    # Get player's object reference
    R1 = G_01AB or G_01AC (player 1 or 2)
    if R1 == 0: return          # No player object
    
    # Convert player position to BACKTAB address
    JSR L_6054                  # R4 = BACKTAB at player position
    
    # Scan 3 BACKTAB cells
    for i in 0..2:
        R2 = BACKTAB[R4]        
        R2 &= $09F8             # Mask: card range + FG bit 2
        if $0860 <= R2 <= $08B0:  # Object in range?
            goto dispatch
        
        R4 += 1                 # Next cell (or +18 for next row)
```

### Dispatch Table (from L_6421)

After finding an object, it's classified by `(R2 - $0860) / 4`:

| Normalized Value | Branch | Object Type | Action |
|-----------------|--------|-------------|--------|
| 0 | `L_6472` | Wall/block | Multi-cell fill with $0032 prefix |
| 1 | `L_64BC` | Interactive? | Write $004B to BACKTAB |
| 2 | `L_64CB` | Player-affecting? | AND with $EFF8, XOR with $0007/$1005 |
| 3–6 | `L_6436` | Generic object | Increment `G_01A8` counter |
| 7 | `L_6445` | **Treasure/chest** | Color prefix + flag update |

### L_6472 — Type 0 (Wall fill)

Fills a multi-cell area with $0032 prefix values. Used for drawing wall blocks that span multiple BACKTAB cells. The prefix $0032 = CS mode, advance stack, BG=1, card=$12.

### L_64BC — Type 1

Writes card $004B/$004C to BACKTAB at R4. Reads a flag from $019D+G_019C, and checks bit 7. The outcome determines which card variant is displayed.

### L_64CB — Type 2 (Player collision/action)

Modifies a player-state RAM variable at `$0335+`:
- AND with $EFF8 (clears bits 2-0)
- XOR with $0007 (player 1) or $1005 (player 2)
- **$0335 is a RAM variable** (not STIC), written at `L_56EC: MVO R0, G_0335` and read throughout the game. It appears to be a player collision/interaction state flag.

---

## 6. PLAYER POSITION TO BACKTAB — L_6054

**Purpose**: Convert player world coordinates to BACKTAB address.

```
L_6054(R3 = player_pos_addr):
    # Read X coordinate
    X = RAM[R3 + $0325]          # ADDI #$0325
    X = X & $FF                  # ANDI #$00FF
    X = max(0, X - 8)            # SUBI #$0008, BPL/clamp
    
    # Read Y coordinate  
    Y = RAM[R3 + $032D]          # after ADDI #$0008
    Y = Y & $7F                  # ANDI #$007F
    Y = max(0, Y - 8)            # SUBI #$0008, BPL/clamp
    
    # Convert to grid position
    col = X >> 3                 # SLR×2, SLR (divide by 8)
    row = Y >> 3                 # SLR×2, SLR
    
    # Calculate BACKTAB offset
    R4 = $0200 + col + row * 20  # SLL×2 (row*4) + SLL×2 (row*16) = row*20
    
    return R4
```

---

## 7. RAM VARIABLES — Object State

| Address | Name | Purpose |
|---------|------|---------|
| $0175 | Starting tile | Tile index for background rendering |
| $0176 | Row count | Number of rows to render |
| $0180+ | Object active flags | Bitmask per player: which objects active |
| $019C | Player number | 0=P1, offset for P2 |
| $019D+ | Object discovered flags | Bitmask: which objects discovered/interacted |
| $01A7 | Object counter | Used by L_6472 wall fill |
| $01A8 | Object rendered count | Incremented for types 3-6 |
| $01AB | Player 1 object ref | Pointer/handle |
| $01AC | Player 2 object ref | Pointer/handle |

---

## 8. FULL RENDERING SEQUENCE

```
1. L_6076    — Clear BACKTAB (write $0000 to $0200-$02EF)
2. L_55BF    — Room initialization
     ├─ Set G_02F4 = $65DC (secondary data)
     ├─ Set G_02F5 = $65B7 (tile map)
     ├─ Set G_0175 = 2 (starting tile)
     ├─ Set G_0176 = $1A (26 rows)
     └─ JSR L_5EE2  → RENDER BACKGROUND
     
3. L_5EE2    — Background rendering loop
     └─ for each tile: L_5EC7 → combine tile map + color → write to BACKTAB

4. L_55F7    — Room object rendering
     ├─ Set mode (G_0184)
     ├─ Read room data header ($64DE)
     └─ for each room entry: L_63B9 → read object table → write to BACKTAB

5. L_63F5    — Post-render object scanning (called each frame)
     ├─ L_6054: player position → BACKTAB address
     ├─ Scan nearby BACKTAB cells for objects
     └─ Dispatch to L_6472 / L_64BC / L_64CB / L_6445
```

---

## 9. KNOWN BACKTAB VALUES (First Room — JZINTV Runtime)

| BACKTAB Word | Card | FG | BG | Mode | Source |
|-------------|------|----|----|------|--------|
| $1E02 | $02 | 3 | 3 | FG/BG | Background (L_5EC7) |
| $1703 | $03 | 7 | 0 | FG/BG | Object table [20/31] |
| $172B | $2B | 7 | 0 | FG/BG | Object table [10] |
| $179B | $1B | 7 | 0 | FG/BG | Object table [13-16] |
| $176B | $2B (masked) | 7 | 0 | FG/BG | Object table [10] |
| $1EBB | $3B | 3 | 3 | FG/BG | Background wall |
| $168B | $0B | 2 | 3 | FG/BG | Object after interaction |
| $16CB | $0B (variant) | 2 | 3 | FG/BG | Object after interaction |

---

## 10. STIC DECODE CORRECTION NOTE

When writing software renderers for this game, it is critical to use the **correct Intellivision STIC BACKTAB decode**.

The standard Intellivision decode (confirmed by jzIntv) uses **bit 11** for the GRAM/GROM select:

```
card_idx  = (word >> 3) & 0xFF       # 8-bit card number
fg_color  = word & 0x07              # 3-bit foreground color
is_gram   = (word >> 11) & 1         # bit 11 = GRAM select (0 = GROM, 1 = GRAM)
advance   = (word >> 13) & 1         # bit 13 = color stack advance
```

Earlier experiments in this repository (notably `scripts/render_dungeon_final.py`) incorrectly used **bit 12** as the GRAM/GROM select:

```python
# WRONG — produces a sprite-sheet artifact where every tile reads from GRAM card 0
g = (word >> 12) & 1                 # INCORRECT bit position
```

Using bit 12 causes every BACKTAB word with bit 12 set (including all `$1xxx` words) to be treated as GRAM, which makes the renderer load GRAM card 0 instead of the intended GROM card. The result looks like a repeating grid of identical tiles — a "sprite sheet" — rather than the actual dungeon room.

`render_all_rooms.decode_backtab_word` implements the proper bit-11 decode, matching the authoritative layout in `jzintv-20200712-win32-sdl2/doc/programming/stic.txt` (§ Color Stack Mode). `derive_roomzero.py` delegates to `render_all_rooms.render_room_image`, which also handles **Colored Squares mode** (bit 12=1, bit 11=0).

**Caveat on "pixel-perfect":** the rendered Room 0 is *not* yet a pixel-perfect match to the reference GIF, for a data reason rather than a decode reason. See § 12.

---

## 11. REMAINING OPEN QUESTIONS

1. **$17 vs $16 color prefix**: L_6445 writes $1600 (FG=6, tan) to the color prefix cell, but runtime BACKTAB shows $17xx (FG=7, white) for objects. Likely explanations:
   - The background tile ($1E02) at the object position gets overwritten by the object card, but the `$17` prefix might come from the **Color Stack** advancing (the background has bit 11 set → $1E02 has bit 11=1 which advances the color stack, potentially cycling to color 7)
   - Or L_6445 is only one of several color injection points
   - The `$1600` might be modified by L_64BC/L_64CB handlers in subsequent frames

2. **Cards $23, $33, $3B**: These appear in runtime BACKTAB but have no match in the object table. These are likely from the background tile set rendered by L_5EC7 for tile indices beyond the sampled ones. The tile map at $65B7+ contains 19 entries that define different background patterns for different screen regions.

3. **World-to-screen coordinate conversion**: Room data X values ($14, $6C, $4C, etc.) are in the 0–255 range (world coordinates), not 0–19 screen columns. The game must convert these to BACKTAB positions using a camera/viewport offset during rendering. L_63B9 receives pre-converted column/row values.

4. **Object table encoding**: The object table at $655E stores 16-bit words with card number in the low byte and $00 in the high byte. The `SDBD; MVI@` read loads the full 16-bit word. The card written to BACKTAB is the low 6 bits of the card byte. Bit 6 (value $40) in the object table card appears to be a flag for object behavior, not a GRAM bit.

---

## 12. ROOM 0 RENDERS CORRECTLY IN FG/BG MODE (superseding §10's CS assumption)

The Color Stack analysis above is the *general* STIC reference, but the dungeon
itself does **not** run in Color Stack mode:

- The screen-setup routine at `$53B5` WRITES STIC mode-select `$0021`, which puts
  the STIC in **Foreground/Background mode** (jzIntv `stic.c:253`), then skips the
  `$0021` read that would select Color Stack mode.
- In FG/BG mode there is no color stack and no Colored Squares. Each tile carries
  its own background color: floor `$1603` → GROM card 0 on olive-green (color 11);
  walls → GRAM cards with fg=tan on bg=black. This is why the room has black
  regions around the walls.
- The structural GRAM cards are blank in the `$55DA` trace, so they are rebuilt
  from the ROM by replaying tile loader `L_53EA` (`$61E7` RLE block).

Full write-up, with the exact FG/BG decode and the loader replication:
**`docs/room0_decode_findings.md`**.
