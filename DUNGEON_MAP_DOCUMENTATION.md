# Swords and Serpents - Dungeon Map Reverse Engineering

## Project Summary
Reverse-engineered the dungeon room layouts from the 1982 Intellivision game "Swords and Serpents" using jzIntv emulator traces and ROM analysis.

## Key Findings

### 1. Dungeon Connectivity (from ROM boundary logic at L_6677)
- **14 rooms total** in a **linear vertical sequence**: Room 0 -> 1 -> 2 -> ... -> 13
- Boundary crossing logic:
  - North (Y < 16): `room += 1`
  - South (Y >= 64): Special transition
  - Middle (16 <= Y < 64) + X edge: `room -= 1`

### 2. Room Templates (from ROM table at 0x617)
| Room | Template | PTR0 (BACKTAB RLE) | Type |
|------|----------|-------------------|------|
| 0 | 0 | 0x1702 | A |
| 1 | 1 | 0x0004 | B |
| 2 | 2 | 0x0140 | C |
| 3 | 3 | 0x0218 | D |
| 4 | 4 | 0x00B8 | A (dup) |
| 5 | 5 | 0x02C0 | B (dup) |
| 6-13 | 6-13 | ... | Uncaptured |

**6 unique templates captured** (templates 4,5 are duplicates of 0,1)

### 3. Captured Rooms (0-5)
All authoritative renders generated with:
- ROM-reconstructed GRAM (RLE at 0x61E7)
- Debug text overlay removal
- Debug MOB filtering (cards 50-63, HUD bar card 9)
- MOB sprite reconstruction (cards 48, 50, 52, 54)

| Room | Template | MD5 Hash | Status |
|------|----------|----------|--------|
| 0 | 0 | c14d299ebd2c4eb2bafc9f0416cb55c2 | ✅ |
| 1 | 1 | 9fb566c0a556af473899d7dc9c9cc4da | ✅ |
| 2 | 2 | 875f20e6200294e084c0161060b1e622 | ✅ |
| 3 | 3 | 87871e8921384b1a86e1ee64476d53ec | ✅ |
| 4 | 4 | d9128c6c9a84d1f34c44bbb46a317d80 | ✅ |
| 5 | 5 | 09be794a37b0123903c71b1a5d80e427 | ✅ |

**All 6 rooms unique** (MD5 verified).

## Key Files Generated

| File | Description |
|------|-------------|
| `room_0_authoritative.png` - `room_5_authoritative.png` | Clean authoritative renders (640x480) |
| `dungeon_vertical_map.png` | 6 rooms stacked vertically (640x2880) |
| `dungeon_grid_3x2.png` | 3x2 grid layout (1920x960) |
| `captures/20260606_full/session.log` | Full 14-room capture session log |
| `DUNGEON_MAP_DOCUMENTATION.md` | This file |

## Technical Details

### ROM Template Structure (from table at 0x617)
Each room has 4 pointers (PTR0=BACKTAB RLE, PTR1=GRAM, PTR2=MOB, PTR3=CFG):
```
Room 0: PTR0=0x1702, PTR1=0x0180, PTR2=0x0018, PTR3=0x0280
Room 1: PTR0=0x0004, PTR1=0x0307, PTR2=0x0180, PTR3=0x021A
Room 2: PTR0=0x0140, PTR1=0x001A, PTR2=0x0210, PTR3=0x0140
Room 3: PTR0=0x0218, PTR1=0x0180, PTR2=0x0004, PTR3=0x0308
Room 4: PTR0=0x00B8, PTR1=0x0203, PTR2=0x0140, PTR3=0x0104
Room 5: PTR0=0x02C0, PTR1=0x0140, PTR2=0x0203, PTR3=0x02B7
```

### RLE Decoding (PTR0)
Format: `[gram_off][count][entries...]` where entry = `(repeat-1)<<8 | byte_val`
- Template 0: 75 entries -> 121 bytes = 60 words
- Template 1: 80 entries -> 156 bytes = 78 words  
- Template 3: 616 entries -> 1383 bytes = 691 words
- Template 4: 616 entries -> 1340 bytes = 670 words
- Template 5: 753 entries -> 1638 bytes = 819 words

### CFG Data (PTR3)
Contains door/connection data for each template:
- Template 4 CFG at 0x0104: 16 words
- Template 5 CFG at 0x02B7: 16 words

### Rendering Pipeline
1. Parse BACKTAB from jzIntv trace
2. Clean debug text (rows 2,4,9 for room 5)
3. Force ROM-reconstructed GRAM (RLE at 0x61E7)
4. Filter debug MOBs (cards 50-63, HUD bar card 9)
5. Reconstruct MOB sprites (cards 48,50,52,54)
6. Render FG/BG mode with aspect correction (4:5)

## Next Steps
- Capture remaining rooms 6-13 using actual boundary transitions
- Decode CFG data to extract door/connection coordinates
- Map full 14-room vertical corridor
- Create complete dungeon map with all 14 rooms