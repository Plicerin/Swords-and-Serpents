#!/usr/bin/env python3
"""
Comprehensive Swords & Serpents Room Tile Pipeline Decoder
===========================================================
Decodes the complete rendering pipeline:
  ROM → SDBD pointer table → tile stream → L_5EC7 BACKTAB construction

Key addresses:
  $65A0 - Card table (23 entries, GRAM card indices $0100-$0121)
  $65B7 - Attr table (24 entries, color/FG/CS attributes)
  $65CE - SDBD pointer table (16-bit LE offsets from $65DC)
  G_02F4 = $65DC (base for SDBD pointers)
  G_02F5 = $65B7 (base for attr table)

Rendering pipeline:
  L_5E48: Sets up room rendering using G_0175/G_0176 (tile stream position)
  L_5E63: Reads SDBD pointer, sets R2 to tile stream address
  L_5E27: Inner loop - reads tile from stream, calls L_5EC7
  L_5EC7: Constructs BACKTAB word from tile value
    Input:  R1 = tile value (0-2047), R4 = BACKTAB pointer
    Output: R1 = BACKTAB word, written directly to [R4]
  L_5EAE: Row renderer - calls L_5E48, then processes a row of tiles

L_5EC7 Algorithm (confirmed):
  1. tile >>= 5 to get group index (0-22)
  2. R3 = $65B7 + idx; R5 = $65A0 + idx
  3. attr_lo = MEM[R3]; R3++ (reads attr[idx])
  4. attr_lo >>= 2; SWAP(attr_lo, 1)
  5. attr_lo ^= MEM[R3]; R3++ (XOR with attr[idx+1])
  6. R1 = attr_lo & $3607 (intermediate mask)
  7. card = MEM[R5]; R5++ (reads card[idx])
  8. R1 ^= (card << 3) (final BACKTAB word)
"""

import sys
sys.stdout.reconfigure(encoding='cp1252', errors='replace')

with open('Swords and Serpents.bin', 'rb') as f:
    rom = f.read()


def rw_be(addr):
    """Read a 16-bit Big-Endian word from ROM at CPU address."""
    off = (addr - 0x5000) * 2
    if off + 1 >= len(rom):
        return 0
    return (rom[off] << 8) | rom[off + 1]


def swap_byte(val):
    """CP-1610 SWAP instruction: swap bytes of 16-bit word."""
    return ((val & 0xFF) << 8) | ((val >> 8) & 0xFF)


def l5ec7(tile_value, attr_table, card_table):
    """
    Simulate L_5EC7 BACKTAB construction.
    
    Args:
        tile_value: 16-bit tile value from tile stream
        attr_table: array of 24 attr values (16-bit each)
        card_table: array of 23 card values (16-bit each)
    
    Returns: 16-bit BACKTAB word
    """
    idx = tile_value >> 5  # group index (0-22)
    if idx >= 23:
        idx = 22  # clamp
    
    # Step 3-4: Read attr[idx], shift + swap
    attr0 = attr_table[idx]
    r1 = attr0 >> 2
    r1 = swap_byte(r1)  # SWAP R1, 1
    
    # Step 5: XOR with attr[idx+1]
    attr1 = attr_table[idx + 1]
    r1 ^= attr1
    
    # Step 6: ANDI #$3607 mask
    r1 &= 0x3607
    
    # Step 7-8: Read card, shift, XOR
    card = card_table[idx]
    card_shifted = (card << 3) & 0xFFFF
    r1 ^= card_shifted
    
    return r1 & 0xFFFF


def decode_backtab_word(bt_word):
    """Decode a BACKTAB word into its components."""
    card = bt_word & 0x07F8  # bits 3-10 (shift for display)
    gram_flag = (bt_word >> 11) & 1
    fg_color = ((bt_word >> 13) & 0x6) | ((bt_word >> 12) & 0x1)
    cs = (bt_word >> 13) & 1
    
    if gram_flag:
        src = f"GRAM card {card >> 3}"
    else:
        src = f"GROM card {card >> 3}"
    
    return {
        'word': bt_word,
        'card_num': card >> 3,
        'gram': gram_flag,
        'fg': fg_color,
        'cs': cs,
        'src': src
    }


def main():
    print("=" * 70)
    print("Swords & Serpents - Room Tile Pipeline Decoder")
    print("=" * 70)
    
    # ============================================================
    # 1. Read ROM tables
    # ============================================================
    print("\n--- 1. ROM DATA TABLES ---")
    
    # Card table: $65A0 (23 entries)
    card_table = [rw_be(0x65A0 + i) for i in range(23)]
    print(f"\nCard table @ $65A0 ({len(card_table)} entries):")
    for i, c in enumerate(card_table):
        gram_label = "GRAM" if (c & 0x0100) else "GROM"
        print(f"  [{i:2d}] ${c:04X} ({c:4d}) -> {gram_label} card {c & 0x3F} (<<3=${(c<<3)&0xFFFF:04X})")
    
    # Attr table: $65B7 (24 entries)
    attr_table = [rw_be(0x65B7 + i) for i in range(24)]
    print(f"\nAttr table @ $65B7 ({len(attr_table)} entries):")
    for i, a in enumerate(attr_table):
        print(f"  [{i:2d}] ${a:04X}")
    
    # SDBD pointer table: $65CE (up to 16 pointers)
    # Base = G_02F4 = $65DC
    base_ptr = 0x65DC
    print(f"\nSDBD pointer table @ $65CE (base=$65DC):")
    sdbd_ptrs = {}
    for i in range(16):
        ptr = rw_be(0x65CE + i)
        if ptr == 0:
            continue
        dest = base_ptr + ptr
        sdbd_ptrs[i] = dest
        print(f"  [{i:2d}] ptr=${ptr:04X} -> dest=${dest:04X} (file offset {(dest-0x5000)*2:04X})")
        # Show first few words
        preview = [f"${rw_be(dest+j):04X}" for j in range(min(8, (0x7000 - dest)))]
        print(f"       preview: {' '.join(preview)}")
    
    # ============================================================
    # 2. L_5EC7 intermediate analysis
    # ============================================================
    print("\n\n--- 2. L_5EC7 INTERMEDIATE ANALYSIS ---")
    print(f"{'Idx':>4} {'Tile>>5':>8} {'attr0':>6} {'attr1':>6} {'SWAP>>2':>6} {'XOR':>6} {'&$3607':>6}")
    print("-" * 52)
    
    intermediates = []
    for idx in range(23):
        attr0 = attr_table[idx]
        attr1 = attr_table[idx + 1]
        
        r1 = attr0 >> 2
        r1_swapped = swap_byte(r1)
        r1_xor = r1_swapped ^ attr1
        r1_final = r1_xor & 0x3607
        
        intermediates.append(r1_final)
        
        print(f"  {idx:2d}  {'--':>6}  ${attr0:04X}  ${attr1:04X}  ${r1_swapped:04X}  ${r1_xor:04X}  ${r1_final:04X}")
    
    # ============================================================
    # 3. FULL L_5EC7 SIMULATION for all tile groups
    # ============================================================
    print("\n\n--- 3. FULL L_5EC7 SIMULATION (all tile groups) ---")
    print(f"{'Grp':>4} {'intermed':>8} {'card':>6} {'<<3':>6} {'BACKTAB':>8} {'GRAM':>5} {'Card#':>6} {'FG':>3} {'CS':>3} {'Decode'}")
    print("-" * 80)
    
    results = {}
    for idx in range(23):
        im = intermediates[idx]
        card = card_table[idx]
        card_s3 = (card << 3) & 0xFFFF
        bt = im ^ card_s3
        
        dec = decode_backtab_word(bt)
        results[idx] = bt
        
        print(f"  {idx:2d}  ${im:04X}     ${card:04X}  ${card_s3:04X}  ${bt:04X}     {dec['gram']:>5}  {dec['card_num']:5d}  {dec['fg']:3d}  {dec['cs']:3d}  {dec['src']}")
    
    # ============================================================
    # 4. Cross-reference with known room 0 BACKTAB words
    # ============================================================
    print("\n\n--- 4. ROOM 0 BACKTAB CROSS-REFERENCE ---")
    
    # Extract unique BACKTAB words from room 0 dump
    # (These are the actual values from the jzIntv dump)
    room0_backtab = {
        # Format: (row*20 + col): value
        0x1603, 0x081B, 0x1E13, 0x020F, 0x02B7, 0x02A7, 0x0257, 0x0287,
        0x02BF, 0x029F, 0x025F, 0x0207, 0x0327, 0x0317, 0x1EBB, 0x026F,
        0x024F, 0x022F, 0x021F, 0x023F, 0x03AF, 0x03EF, 0x03E7, 0x03B7,
        0x1E5B, 0x1E40, 0x0E60, 0x0823, 0x1E38, 0x1E02, 0x082B, 0x0367,
        0x0347, 0x036F, 0x03BF,
    }
    
    print(f"Room 0 has {len(room0_backtab)} unique BACKTAB words")
    print(f"L_5EC7 produces {len(set(results.values()))} unique BACKTAB words across 23 groups")
    
    # Which L_5EC7 groups match room 0 BACKTAB?
    print("\nMatching groups (L_5EC7 output appears in room 0):")
    matches = []
    for idx, bt in results.items():
        if bt in room0_backtab:
            dec = decode_backtab_word(bt)
            matches.append(idx)
            print(f"  Group {idx:2d}: ${bt:04X} -> {dec['src']} (FG={dec['fg']}, CS={dec['cs']})")
    
    print(f"\n  {len(matches)}/23 groups produce BACKTAB words used in room 0")
    
    # Room 0 BACKTAB words NOT produced by L_5EC7
    unmatched_bt = room0_backtab - set(results.values())
    print(f"\nRoom 0 BACKTAB words NOT from L_5EC7 ({len(unmatched_bt)}):")
    for bt in sorted(unmatched_bt):
        dec = decode_backtab_word(bt)
        print(f"  ${bt:04X} -> {dec['src']} (FG={dec['fg']}, CS={dec['cs']})")
    
    # ============================================================
    # 5. Tile stream analysis for room 0
    # ============================================================
    print("\n\n--- 5. TILE STREAM FOR ROOM 0 ---")
    
    # SDBD pointer table resolution:
    # Step trace confirms: at L_5E63, R0=4, R4=$65D2, SDBD+MVI@ R4,R2 → R2=$6D86
    # Word at $65D2 = $0086 (BE). Destination = $6D00 + $0086 = $6D86.
    # So effective base for SDBD pointers is $6D00, NOT $65DC (G_02F4).
    # 
    # For room 0: entry 0 at $65CE = $0098 → $6D00 + $0098 = $6D98
    # Let's verify both candidates:
    
    sdbd_base = 0x6D00  # Empirically determined effective base
    
    print("SDBD pointers with effective base $6D00:")
    for i in range(16):
        ptr = rw_be(0x65CE + i)
        if ptr != 0:
            dest = sdbd_base + ptr
            print(f"  [{i:2d}] ptr=${ptr:04X} -> dest=${dest:04X}")
            if i == 0:
                # Show preview of room 0 tile stream
                preview = [f"${rw_be(dest+j):04X}" for j in range(min(12, 0x7000 - dest))]
                print(f"       preview: {' '.join(preview)}")
    
    # Room 0 uses SDBD entry 0
    stream_addr = sdbd_base + rw_be(0x65CE)  # $6D00 + $0098 = $6D98
    print(f"\nRoom 0 tile stream at ${stream_addr:04X}")
    
    # Also show what $6D86 would produce (from step trace, room 4)
    stream_addr_room4 = sdbd_base + rw_be(0x65D2)  # $6D00 + $0086 = $6D86
    print(f"Room 4 tile stream at ${stream_addr_room4:04X} (matches step trace)")
    
    # Read tile stream at this destination
    # Tile format: run-length encoded
    # Value > $1F: literal tile, passed to L_5EC7
    # Value <= $1F: repeat count for next tile
    print(f"\n=== Decoding tile stream at ${stream_addr:04X} ===")
    
    # Also decode the room 4 stream for comparison
    print(f"\n(For reference, room 4 stream at ${stream_addr_room4:04X} from step trace:)")
    tiles_r4 = []
    addr = stream_addr_room4
    while len(tiles_r4) < 30 and addr < 0x7000:
        val = rw_be(addr)
        if val == 0xFFFF:
            break
        if val <= 0x001F:
            count = val
            addr += 1
            if addr < 0x7000:
                tile_val = rw_be(addr)
                for _ in range(count):
                    tiles_r4.append(tile_val)
        else:
            tiles_r4.append(val)
        addr += 1
    print(f"  First 30 tiles: {' '.join(f'${t:04X}' for t in tiles_r4[:30])}")
    
    print(f"\nTile stream data at ${stream_addr:04X}:")
    
    tiles = []
    addr = stream_addr
    max_tiles = 240  # 12x20 BACKTAB = 240 tiles max
    
    while len(tiles) < max_tiles and addr < 0x7000:
        val = rw_be(addr)
        if val == 0xFFFF or val == 0x0000 and addr > stream_addr + 20:
            break  # likely end of stream
        
        if val <= 0x001F:
            # Run-length encoding: repeat count
            count = val
            addr += 1
            if addr < 0x7000:
                tile_val = rw_be(addr)
                for _ in range(count):
                    tiles.append(tile_val)
            else:
                break
        else:
            # Literal tile
            tiles.append(val)
        
        addr += 1
    
    print(f"  Decoded {len(tiles)} tiles from stream")
    if tiles:
        print(f"  First 20 tiles: {' '.join(f'${t:04X}' for t in tiles[:20])}")
    
    # ============================================================
    # 6. Render room 0 using L_5EC7
    # ============================================================
    print("\n\n--- 6. SIMULATED ROOM 0 BACKTAB ---")
    
    if tiles:
        # Don't include $1603 floor fill - L_5EC7 doesn't handle that
        sim_backtab = []
        for t in tiles:
            bt = l5ec7(t, attr_table, card_table)
            sim_backtab.append(bt)
        
        # Compare with actual room 0 BACKTAB
        # First, extract the actual BACKTAB grid from the dump file
        actual_grid = []
        try:
            with open('traces/rooms/render_room_0_out.txt') as f:
                in_bt = False
                for line in f:
                    if line.startswith('0200:') and '1603' in line:
                        in_bt = True
                    if in_bt:
                        if line.startswith('02') and ':' in line:
                            parts = line.split()
                            for p in parts[1:]:
                                if p.endswith('*'):
                                    p = p[:-1]
                                if len(p) == 4:
                                    try:
                                        actual_grid.append(int(p, 16))
                                    except:
                                        pass
                        if line.startswith('02F0:'):
                            break
        except FileNotFoundError:
            actual_grid = []
        
        # Print 12x20 grid comparison
        print(f"\n  Simulated: {len(sim_backtab)} tiles, Actual: {len(actual_grid)} tiles")
        
        if actual_grid:
            matches = sum(1 for s, a in zip(sim_backtab, actual_grid) if s == a)
            floor_count = sum(1 for a in actual_grid if a == 0x1603)
            print(f"  Exact matches: {matches}/{min(len(sim_backtab), len(actual_grid))}")
            print(f"  Floor tiles ($1603) in actual: {floor_count}")
            
            # Show non-floor comparison
            non_floor_matches = 0
            non_floor_total = 0
            for s, a in zip(sim_backtab, actual_grid):
                if a != 0x1603:
                    non_floor_total += 1
                    if s == a:
                        non_floor_matches += 1
            
            print(f"  Non-floor matches: {non_floor_matches}/{non_floor_total}")
            
            if non_floor_total > 0:
                accuracy = non_floor_matches / non_floor_total * 100
                print(f"  Non-floor accuracy: {accuracy:.1f}%")
        
        # Show the simulated grid
        print("\n  Simulated BACKTAB grid (12 rows x 20 cols):")
        for row in range(min(12, (len(sim_backtab) + 19) // 20)):
            start = row * 20
            end = min(start + 20, len(sim_backtab))
            row_tiles = sim_backtab[start:end]
            print(f"    Row {row:2d}: " + " ".join(f"${t:04X}" for t in row_tiles))
    
    # ============================================================
    # 7. Summary
    # ============================================================
    print("\n\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"""
Rendering Pipeline:
  1. ROM SDBD table at $65CE provides 16-bit offsets from $65DC
  2. Each offset points to a tile stream in ROM ($5000-$6FFF)
  3. Tile streams are run-length encoded:
     - Value > $1F: literal tile, passed to L_5EC7
     - Value <= $1F: repeat count for next tile
  4. L_5EC7 converts each tile to a BACKTAB word:
     a. tile >>= 5 → group index (0-22)
     b. Look up attr[idx] and attr[idx+1] from $65B7
     c. Transform attrs: SLR 2, SWAP, XOR → ANDI $3607
     d. Look up card[idx] from $65A0 (GRAM card indices)
     e. XOR intermediate with (card << 3) → BACKTAB word
  5. X_FILL_MEM pre-fills BACKTAB with $1603 (floor)
  6. L_5EC7 overwrites only non-floor tile positions

Key Tables:
  $65A0: Card table - 23 GRAM card indices ($0100-$0122, etc.)
  $65B7: Attr table - 24 color/FG/CS attribute entries
  $65CE: SDBD pointer table - room tile stream offsets
  
L_5EC7 produces BACKTAB words for tiles actually in the room.
$1603 (floor fill) comes from X_FILL_MEM, not L_5EC7.
""")


if __name__ == '__main__':
    main()
