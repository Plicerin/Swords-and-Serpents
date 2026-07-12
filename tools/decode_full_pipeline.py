#!/usr/bin/env python3
"""
Swords & Serpents -- Full Room Rendering Pipeline Decoder
=========================================================
Traces the complete chain from ROM data through the rendering pipeline:

  ROM file -> $65CE SDBD pointer table -> tile data streams -> L_5EC7 BACKTAB -> screen

Key addresses (CPU space, $5000-$6FFF ROM range):
  $65CE: SDBD pointer table (16 overlapping entries, 1-word stride)
  $65A0: Card/color lookup table (8 entries, indexed by tile_value/32)
  $65B7: Attribute lookup table (8 entries, indexed by tile_value/32)
  $65DC: Room data pointer base (G_02F4)

jzIntv Memory (verified traces):
  $65CE-$65E5: SDBD pointer table
  $65CE: $0098  $65CF: $006C  -> SDBD reads $6C98
  $65D0: $0011  $65D1: $006D  -> SDBD reads $6D11
  $65D2: $0086  $65D3: $006D  -> SDBD reads $6D86 ✓ (traced)
  $65D4: $0013  $65D5: $006E  -> SDBD reads $6E13
  $65D6: $009E  $65D7: $006E  -> SDBD reads $6E9E
  $65D8: $0020  $65D9: $006F  -> SDBD reads $6F20
  $65DA: $009E  $65DB: $006F  -> SDBD reads $6F9E
  $65DC: $0042  $65DD: $006A  -> SDBD reads $6A42

ROM file mapping:
  Big-endian: (offset >> 1) + 0x5000 = CPU address
  File offset = (CPU_addr - 0x5000) * 2
  Verified: $65CE data found at file offset $002B96 with 16/16 match (delta -6 bytes)

Rendering Pipeline (disassembly trace):
  1. L_5E48: (row,col) screen coords -> 4-bit tile index from room data
  2. L_5E60: tile index -> SDBD table -> tile stream pointer (R2)
  3. L_5E6C: skip rows in tile stream to reach current row
  4. L_5E76: consume tile stream entries until column matches
  5. L_5EF4: read tile data word -> L_5EC7 -> BACKTAB card -> write to $0200+

L_5EC7 BACKTAB construction:
  - tile_value/32 -> index into $65B7 (attributes) and $65A0 (card/color)
  - XOR/SWAP/SLL trick extracts FG color, CS advance, and card bits
  - Produces standard Color Stack BACKTAB format:
    bits 0-10:  Card number
    bit 11:     GROM/GRAM select
    bits 15/14/12: Foreground color (0-7)
    bit 13:     Color Stack advance
"""
import struct
import os

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ROM_PATH = os.path.join(PROJECT_DIR, "Swords and Serpents.bin")

# =========================================================================
# ROM Access (big-endian)
# =========================================================================

def load_rom():
    with open(ROM_PATH, 'rb') as f:
        return f.read()

def rw_be(rom, addr):
    """Read 16-bit big-endian word at CPU address (ROM $5000-$6FFF)."""
    if addr < 0x5000 or addr > 0x6FFF:
        return 0
    offset = (addr - 0x5000) * 2
    if offset + 1 < len(rom):
        return (rom[offset] << 8) | rom[offset + 1]
    return 0

def lo(w):
    return w & 0xFF

def hi(w):
    return (w >> 8) & 0xFF

# =========================================================================
# Part 1: SDBD Pointer Table
# =========================================================================

def decode_sdbd_table(rom, base=0x65CE, entries=16):
    """Decode SDBD pointer table: overlapping entries, 1-word stride.
    SDBD reads lo(word[addr+0]) and lo(word[addr+1]) and concats them.
    Result = (lo(word[addr+1]) << 8) | lo(word[addr])
    """
    pointers = []
    for i in range(entries):
        byte0 = lo(rw_be(rom, base + i))
        byte1 = lo(rw_be(rom, base + i + 1))
        ptr = (byte1 << 8) | byte0
        pointers.append(ptr)
    return pointers

# =========================================================================
# Part 2: Room Data -> Tile Index
# =========================================================================

def get_room_tile_index(rom, room_base, row, col):
    """Get the 4-bit tile index for screen position (row, col).
    
    From L_5E48:
      row_nibble = (row & 0x30) >> 3
      col_nibble = (col & 0x60) >> 5
      offset = row_nibble + (col_nibble >> 1)  ; col_nibble * 1.5
      word_addr = room_base + offset
      word = MVI@ word_addr
      if col_nibble & 1:  ; odd column nibble
          word >>= 4
      return word & 0xF
    """
    row_nibble = (row & 0x30) >> 3
    col_nibble = (col & 0x60) >> 5
    offset = row_nibble + (col_nibble >> 1)
    word_addr = room_base + offset
    word = rw_be(rom, word_addr)
    if col_nibble & 1:
        word >>= 4
    return word & 0xF

# =========================================================================
# Part 3: L_5EC7 BACKTAB Word Construction
# =========================================================================

def l5ec7_backtab(tile_value, attr_table, card_table):
    """Construct a BACKTAB word from a tile value using L_5EC7 algorithm.
    
    L_5EC7 algorithm (from disassembly):
      index = tile_value >> 5          ; divide by 32
      attr_word = attr_table[index]
      card_word = card_table[index]
      
      ; Attribute word processing:
      r1 = attr_word >> 2
      r1 = SWAP(r1)                    ; byte swap
      r1 = r1 XOR attr_word            ; nibble extraction trick
      r1 = r1 AND $3607                ; mask: bits 13,12,10,9,2,1,0
      
      ; Card word processing:
      r3 = card_word << 3              ; shift left 3
      
      ; Combine:
      backtab = r1 XOR r3
    
    Where $3607 = 0011 0110 0000 0111 binary
    This preserves:
      bits 13,12: CS advance + FG bit 0
      bits 10,9:  card number bits
      bits 2,1,0: card number bits
    
    The XOR/SWAP trick on the attribute word:
      attr_word = ab cd (bytes)
      r1 = attr_word >> 2 = 00ab cd>>2
      SWAP: cd>>2 00ab  
      XOR with original: upper nibble vs lower nibble interleaving
    
    Essentially extracts interleaved bits from the attribute word for encoding.
    """
    index = tile_value >> 5
    if index >= len(attr_table) or index >= len(card_table):
        return 0
    
    attr_word = attr_table[index]
    card_word = card_table[index]
    
    # Attribute processing (L_5EC7: $5ECF-$5ED9)
    r1 = attr_word >> 2              # SLR R1, 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)  # SWAP R1, 1
    r1 = r1 ^ attr_word              # XOR@ R3, R1
    r1 = r1 & 0x3607                 # ANDI #$3607
    
    # Card processing (L_5EC7: $5EDC-$5EDE)
    r3 = (card_word << 3) & 0xFFFF   # SLL R3, 2; SLL R3, 1
    
    # Combine (L_5EC7: $5EDF)
    backtab = r1 ^ r3
    
    return backtab & 0xFFFF


def decode_backtab_word(word):
    """Decode BACKTAB word into readable components (Color Stack mode)."""
    card = word & 0x7FF                # bits 0-10
    is_gram = bool(word & 0x0800)      # bit 11
    fg = ((word >> 13) & 0x6) | ((word >> 12) & 0x1)  # bits 15,14,12
    cs_advance = (word >> 13) & 1      # bit 13
    return {
        'word': word,
        'card': card,
        'is_gram': is_gram,
        'fg_color': fg,
        'cs_advance': cs_advance,
    }

# =========================================================================
# Part 4: Tile Stream Parser
# =========================================================================

def parse_tile_stream(rom, stream_addr, row, col):
    """Navigate the RLE tile stream to find the tile data for a given screen position.
    
    The tile stream format (inferred from L_5E6C, L_5E73, L_5E76):
      At the stream pointer, there's a count word (low 5 bits = remaining entries).
      The stream is navigated row-by-row using ADD@ R2, R2 (double-indirect skip).
      Within a row, entries are consumed until the column matches.
    
    This is a simplified model based on the empirical jzIntv BACKTAB data.
    For now, we'll map the known tile indices to their BACKTAB outputs.
    """
    # For the initial decode, we work backwards from the known BACKTAB.
    # A full decoder would need to trace the exact stream navigation.
    return None


# =========================================================================
# Part 5: Full Room Rendering Simulation
# =========================================================================

def simulate_room_render(rom, room_index=0):
    """Simulate the full room rendering pipeline for one room.
    
    Returns a 12x20 grid of BACKTAB words.
    """
    # Configure game state (as done by init code at $55C4-$55D5)
    G_02F4 = 0x65DC  # room data base pointer
    
    # The room index selects which data block at $65DC + room*8
    # But room 0 uses $65DC directly (G_019C=0)
    room_base = G_02F4 + room_index * 8
    
    # Read lookup tables
    ATTR_TABLE_BASE = 0x65B7
    CARD_TABLE_BASE = 0x65A0
    
    attr_table = [rw_be(rom, ATTR_TABLE_BASE + i) for i in range(8)]
    card_table = [rw_be(rom, CARD_TABLE_BASE + i) for i in range(8)]
    
    # Read SDBD pointer table
    sdbd_table = decode_sdbd_table(rom)
    
    # Screen dimensions: 20 columns x 12 rows
    # Starting position: G_0175=2, G_0176=26 (empirically verified)
    col_start = 2
    row_start = 26
    
    backtab_grid = [[0] * 20 for _ in range(12)]
    
    for screen_row in range(12):
        game_row = row_start + screen_row
        
        for screen_col in range(20):
            game_col = col_start + screen_col
            
            # Step 1: Get tile index from room data (L_5E48)
            tile_idx = get_room_tile_index(rom, room_base, game_row, game_col)
            
            # Step 2: Get SDBD pointer for this tile (L_5E60)
            if tile_idx < len(sdbd_table):
                stream_ptr = sdbd_table[tile_idx]
            else:
                stream_ptr = 0
            
            # Step 3: For now, use L_5EC7 directly on tile index
            # (Full stream navigation would be needed for accurate row/col skipping)
            # But since each tile index maps to one tile type, and the stream
            # just handles repeating patterns, L_5EC7 on tile_idx is the key.
            
            # Step 4: Construct BACKTAB word (L_5EC7)
            backtab = l5ec7_backtab(tile_idx, attr_table, card_table)
            
            backtab_grid[screen_row][screen_col] = backtab
    
    return backtab_grid, attr_table, card_table, sdbd_table


# =========================================================================
# Main
# =========================================================================

def main():
    rom = load_rom()
    
    print("=" * 70)
    print("  SWORDS & SERPENTS -- FULL RENDERING PIPELINE DECODER")
    print("=" * 70)
    print(f"  ROM: {len(rom)} bytes")
    print()
    
    # === Part 1: SDBD Pointer Table ===
    print("=" * 70)
    print("PART 1: $65CE SDBD Pointer Table")
    print("=" * 70)
    
    sdbd_table = decode_sdbd_table(rom)
    print(f"  Base: $65CE (overlapping entries, 1-word stride)")
    print()
    
    # Show all 16 overlapping entries
    print("  Overlapping entries (1-word stride, as read by SDBD):")
    for i in range(16):
        byte0 = lo(rw_be(rom, 0x65CE + i))
        byte1 = lo(rw_be(rom, 0x65CE + i + 1))
        ptr = sdbd_table[i]
        in_range = "ROM" if 0x5000 <= ptr <= 0x6FFF else "OUT"
        print(f"    [{i:2d}] ${0x65CE+i:04X}: lo={byte0:02X} | ${0x65CF+i:04X}: lo={byte1:02X}  ->  ${ptr:04X}  [{in_range}]")
    
    # Show 8 non-overlapping entries
    print()
    print("  Non-overlapping entries (2-word stride):")
    for i in range(8):
        ptr = sdbd_table[i * 2]
        in_range = "ROM" if 0x5000 <= ptr <= 0x6FFF else "OUT"
        print(f"    [{i}] ${0x65CE+i*2:04X}: ${ptr:04X}  [{in_range}]")
    
    # === Part 2: Lookup Tables ($65A0, $65B7) ===
    print()
    print("=" * 70)
    print("PART 2: $65A0 + $65B7 Lookup Tables (L_5EC7)")
    print("=" * 70)
    
    ATTR_BASE = 0x65B7
    CARD_BASE = 0x65A0
    
    print(f"\n  Attribute table at ${ATTR_BASE:04X} (8 entries, indexed by tile_value/32):")
    attr_table = []
    for i in range(8):
        w = rw_be(rom, ATTR_BASE + i)
        attr_table.append(w)
        print(f"    [{i}] ${ATTR_BASE+i:04X}: ${w:04X}  (bin: {w:016b})")
    
    print(f"\n  Card/Color table at ${CARD_BASE:04X} (8 entries):")
    card_table = []
    for i in range(8):
        w = rw_be(rom, CARD_BASE + i)
        card_table.append(w)
        print(f"    [{i}] ${CARD_BASE+i:04X}: ${w:04X}  (bin: {w:016b})")
    
    # === Part 3: L_5EC7 Trace for Known Tile Values ===
    print()
    print("=" * 70)
    print("PART 3: L_5EC7 BACKTAB Construction Trace")
    print("=" * 70)
    
    # Test with known BACKTAB words from jzIntv dump (room 0)
    # The BACKTAB contains various tile words - let's see what tile indices map to them
    print()
    print("  Tracing L_5EC7 for tile indices 0-15:")
    print(f"  {'tile':>5s} | {'index':>5s} | {'attr':>6s} | {'card':>6s} | {'BACKTAB':>8s} | card | GRAM | FG | CS")
    print(f"  {'-'*5} | {'-'*5} | {'-'*6} | {'-'*6} | {'-'*8} | {'-'*4} | {'-'*4} | {'-'*2} | {'-'*2}")
    
    for tile_val in range(16):
        bt = l5ec7_backtab(tile_val, attr_table, card_table)
        dec = decode_backtab_word(bt)
        print(f"  ${tile_val:04X} | {tile_val>>5:5d} | ${attr_table[tile_val>>5] if tile_val>>5 < 8 else 0:04X} | ${card_table[tile_val>>5] if tile_val>>5 < 8 else 0:04X} | ${bt:04X} | {dec['card']:4d} | {'G' if dec['is_gram'] else 'g'} | {dec['fg_color']:2d} | {dec['cs_advance']:2d}")
    
    # === Part 4: Room Data Analysis ===
    print()
    print("=" * 70)
    print("PART 4: Room Data -> Tile Index Map (Room 0)")
    print("=" * 70)
    
    ROOM_BASE = 0x65DC  # G_02F4 for room 0
    
    print(f"\n  Room data at ${ROOM_BASE:04X} (address = ${ROOM_BASE:04X} + row_nibble + col_nibble>>1):")
    print()
    
    # Show tile index grid for room 0
    print("  Tile index grid (12 rows x 20 cols):")
    print("     " + "".join(f"{c:2d}" for c in range(20)))
    
    for screen_row in range(12):
        game_row = 26 + screen_row
        row_str = f"  {screen_row:2d}: "
        for screen_col in range(20):
            game_col = 2 + screen_col
            tile_idx = get_room_tile_index(rom, ROOM_BASE, game_row, game_col)
            if tile_idx == 0:
                row_str += " . "
            else:
                row_str += f"{tile_idx:2d} "
        print(row_str)
    
    # === Part 5: Simulate Room Render ===
    print()
    print("=" * 70)
    print("PART 5: Simulated Room 0 BACKTAB vs jzIntv Actual")
    print("=" * 70)
    
    backtab_grid, attr_t, card_t, sdbd_t = simulate_room_render(rom, room_index=0)
    
    # Known BACKTAB words from jzIntv dump (room 0, from render_room_0_out.txt)
    jzintv_backtab = [
        [0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1E13, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603],
        [0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603],
        [0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603, 0x02BF, 0x029F, 0x025F, 0x02B7, 0x0207, 0x02BF, 0x0327, 0x0317, 0x0327, 0x02BF],
        [0x020F, 0x02B7, 0x02A7, 0x020F, 0x0257, 0x0287, 0x02BF, 0x0823, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603],
        [0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1EBB, 0x0327, 0x026F, 0x024F, 0x022F, 0x021F, 0x026F],
        [0x023F, 0x0327, 0x03AF, 0x03EF, 0x03E7, 0x03B7, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603],
        [0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x0E60, 0x1603],
        [0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1E5B, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603],
        [0x1603, 0x1E40, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1E40, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603],
        [0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x020F, 0x0257, 0x0287, 0x020F, 0x02B7, 0x0327, 0x021F, 0x022F, 0x024F, 0x020F, 0x0327],
        [0x0367, 0x03AF, 0x0347, 0x03B7, 0x0347, 0x03BF, 0x036F, 0x0823, 0x1E38, 0x1603, 0x1603, 0x1603, 0x1E02, 0x082B, 0x0823, 0x0823, 0x0823, 0x0823, 0x0823, 0x081B],
        [0x1603, 0x1603, 0x0823, 0x0823, 0x0823, 0x0823, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x1603, 0x081B],
    ]
    
    matches = 0
    total = 0
    print()
    print(f"  Comparing simulated vs jzIntv BACKTAB:")
    print(f"  {'Row':>4s} {'Col':>4s} | {'Sim':>6s} | {'jzIntv':>6s} | Match")
    print(f"  {'-'*4} {'-'*4} | {'-'*6} | {'-'*6} | {'-'*5}")
    
    for r in range(12):
        for c in range(20):
            sim = backtab_grid[r][c]
            jz = jzintv_backtab[r][c]
            total += 1
            if sim == jz:
                matches += 1
            else:
                print(f"  {r:4d} {c:4d} | ${sim:04X} | ${jz:04X} | {'YES' if sim == jz else 'NO'}")
    
    accuracy = matches / total * 100 if total > 0 else 0
    print(f"\n  Accuracy: {matches}/{total} = {accuracy:.1f}%")
    
    # === Summary ===
    print()
    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  SDBD pointers: {len([p for p in sdbd_table if 0x5000 <= p <= 0x6FFF])} in ROM range")
    print(f"  Lookup tables: 8 entries each at $65A0 (cards) and $65B7 (attributes)")
    print(f"  Room data base: $65DC (G_02F4)")
    print(f"  Pipeline accuracy: {accuracy:.1f}% ({matches}/{total} tiles)")
    print()
    print("  NOTE: This pipeline decodes tile indices via the room data + L_5EC7 lookup.")
    print("  The tile stream (RLE data at pointer destinations) provides per-row/col")
    print("  variations that the simple tile-index approach doesn't capture.")
    print("  Full accuracy requires parsing the tile stream navigation logic.")
    print()


if __name__ == '__main__':
    main()
