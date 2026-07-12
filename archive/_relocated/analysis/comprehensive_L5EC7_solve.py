#!/usr/bin/env python3
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
"""
Comprehensive L_5EC7 Solver — Systematically tests ALL possible SDBD interpretations
against the actual room 0 BACKTAB data from JZINTV capture.

Tests every combination of:
  1. Card table source (ROM $65A0, scratchpad $00A0 via GRAM, etc.)
  2. Card table word vs byte reads
  3. ANDI mask interpretation ($3607 vs others)
  4. XOR target (attr[i] vs attr[i+1])

Goal: Find the ONE interpretation that produces ALL 35 distinct BACKTAB words.
"""

import os
import struct

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ROM_PATH = os.path.join(PROJECT_DIR, "Swords and Serpents.bin")

# =========================================================================
# ROM Access (big-endian 16-bit words)
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

def rb(rom, addr):
    """Read big-endian byte at CPU address (low byte)."""
    return rw_be(rom, addr) & 0xFF

# =========================================================================
# Actual BACKTAB from JZINTV capture (room 0)
# =========================================================================

BACKTAB_GRID = [
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

# All distinct BACKTAB words
ALL_DISTINCT = set()
for row in BACKTAB_GRID:
    for word in row:
        ALL_DISTINCT.add(word)
DISTINCT_LIST = sorted(ALL_DISTINCT)
print(f"Distinct BACKTAB words: {len(ALL_DISTINCT)}")
for w in DISTINCT_LIST:
    card = w & 0x7FF
    is_gram = bool(w & 0x0800)
    fg = ((w >> 13) & 0x6) | ((w >> 12) & 0x1)
    cs_adv = (w >> 13) & 1
    print(f"  ${w:04X}  card={card:4d}  {'GRAM' if is_gram else 'grom'}  FG={fg}  CSadv={cs_adv}")


# =========================================================================
# ROM Lookup Tables
# =========================================================================

rom = load_rom()
print(f"\nROM loaded: {len(rom)} bytes")

# Read attr table at $65B7 (8 entries, 16-bit words)
ATTR_BASE = 0x65B7
attr_table = [rw_be(rom, ATTR_BASE + i) for i in range(8)]
print(f"\nAttr table @ ${ATTR_BASE:04X}:")
for i, a in enumerate(attr_table):
    print(f"  [{i}] ${a:04X}  ({a:016b})")

# Read card table at $65A0 (8 entries) - multiple interpretations
CARD_BASE = 0x65A0
card_words = [rw_be(rom, CARD_BASE + i) for i in range(8)]
print(f"\nCard table @ ${CARD_BASE:04X} (word reads):")
for i, c in enumerate(card_words):
    print(f"  [{i}] ${c:04X}  ({c:016b})")

# Byte reads from card table (low bytes only)
card_bytes = [rb(rom, CARD_BASE + i) for i in range(8)]
print(f"\nCard table @ ${CARD_BASE:04X} (byte reads, low):")
for i, c in enumerate(card_bytes):
    print(f"  [{i}] ${c:02X}")

# High bytes from card table
card_bytes_hi = [(rw_be(rom, CARD_BASE + i) >> 8) & 0xFF for i in range(8)]
print(f"\nCard table @ ${CARD_BASE:04X} (byte reads, high):")
for i, c in enumerate(card_bytes_hi):
    print(f"  [{i}] ${c:02X}")

# =========================================================================
# GRAM data from JZINTV capture (the card table could live here at runtime)
# =========================================================================

# GRAM memory dump from render_room_0_out.txt
# We'll load it as a dict: {address: low_byte_value}
GRAM_DATA = {}
gram_text = """
3800:  0000  0028  007F  0018   002F  000D  0010  0000
3808:  0000  0000  0000  0000   0000  0000  0000  0000
3810:  0000  0000  0080  0080   00D0  00D0  00F0  00F0
3818:  00F0  00F8  00E8  0078   00F0  00F8  00F8  00F8
3820:  00F7  00FF  00FF  00FF   00EF  00E6  0000  0000
3828:  00EF  00FF  007F  00FF   00FF  00FD  00F8  00F8
3830:  00F0  00F8  00E8  00F8   00F0  00B8  0000  0000
3838:  0080  00C0  00E0  00E0   00E0  00E0  00E0  00E0
3840:  00FF  007F  0000  0000   0000  0000  0000  0000
3848:  00E0  00EC  00ED  00ED   00ED  00ED  00EC  00E0
3850:  00E0  00EC  00ED  00ED   00ED  00ED  00EC  00E0
3858:  007F  002E  003A  0036   006C  0074  005C  00FE
3860:  00FF  0000  00FF  00FE   00FE  00FF  0000  00FF
3868:  00AB  00AB  00AB  00AA   00AA  00AB  00AB  00AB
3870:  0000  0000  0087  009D   00FD  003F  0018  003C
3878:  0042  0081  0099  00BD   005A  0024  00DB  007E
"""

# Parse GRAM
for line in gram_text.strip().split('\n'):
    line = line.strip()
    if ':' not in line:
        continue
    addr_part, data_part = line.split(':', 1)
    addr = int(addr_part.strip(), 16)
    words = data_part.strip().split()
    for w in words:
        GRAM_DATA[addr] = int(w, 16) & 0xFF
        addr += 1

# =========================================================================
# L_5EC7 formula — the CORE function we're testing
# =========================================================================

def l5ec7_compute(attr_table, card_table, group_idx, 
                  card_is_byte_read=False, 
                  xor_next_attr=True,
                  andi_mask=0x3607,
                  andi_is_sdbd=False):
    """
    Simulate L_5EC7 for a given group index.
    
    Parameters:
      attr_table: list of 8 attr word values
      card_table: list of 8 card values (words or bytes depending on card_is_byte_read)
      group_idx: which group (0-7) to compute for
      card_is_byte_read: if True, MVI@ R5 reads a byte (card = card_table[idx] & 0xFF),
                         else reads a word (card = card_table[idx])
      xor_next_attr: if True, XOR@ R3 reads attr[group+1]; if False, reads attr[group]
      andi_mask: the ANDI mask (default $3607)
      andi_is_sdbd: if True, ANDI with SDBD byte-masks (different behavior)
    
    Returns: 16-bit BACKTAB word
    """
    if group_idx >= len(attr_table) or group_idx >= len(card_table):
        return 0
    
    attr_word = attr_table[group_idx]
    
    # --- Attribute processing ---
    # R1 = attr_word >> 2 (SLR R1, 2)
    r1 = (attr_word >> 2) & 0xFFFF
    
    # R1 = SWAP R1 (swap bytes)
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    
    # R1 ^= attr[group+1] (or attr[group] if not xor_next_attr)
    if xor_next_attr and group_idx + 1 < len(attr_table):
        xor_val = attr_table[group_idx + 1]
    else:
        xor_val = attr_word  # XOR with self (different from XOR@ which reads NEXT word)
    
    r1 ^= xor_val
    
    # R1 &= mask (ANDI #$3607)
    if andi_is_sdbd:
        # SDBD byte-wise AND: low byte & low byte, high byte & high byte
        # Mask $3607 -> lo=$07, hi=$36
        lo_mask = andi_mask & 0xFF   # $07
        hi_mask = (andi_mask >> 8) & 0xFF  # $36
        r1 = ((r1 & 0xFF) & lo_mask) | (((r1 >> 8) & 0xFF) & hi_mask) << 8
    else:
        r1 &= andi_mask
    
    # --- Card processing ---
    if card_is_byte_read:
        # SDBD was active at MVII so R5 points to byte table
        # MVI@ R5 reads a word but only low byte is meaningful
        # Actually: if R5=$00A0 (GRAM), MVI@ reads the GRAM word
        # But for byte interpretation, card = low byte
        card_val = card_table[group_idx] & 0xFF
    else:
        card_val = card_table[group_idx] & 0xFFFF
    
    # R3 = card_val << 3 (SLL R3, 2; SLL R3, 1)
    r3 = (card_val << 3) & 0xFFFF
    
    # --- Combine ---
    backtab = (r1 ^ r3) & 0xFFFF
    
    return backtab


# =========================================================================
# Test each interpretation
# =========================================================================

print("\n" + "=" * 80)
print("INTERPRETATION TESTS")
print("=" * 80)

interpretations = []

# Interpretation 1: Standard (no SDBD effects), card=word from ROM $65A0
# R5=$65A0, MVI@ reads word, XOR next attr, ANDI=$3607
interpretations.append({
    'name': 'I1: R5=$65A0, word card, xor=next, andi=$3607',
    'card_table': card_words,
    'card_is_byte_read': False,
    'xor_next_attr': True,
    'andi_mask': 0x3607,
    'andi_is_sdbd': False,
})

# Interpretation 2: SDBD makes MVII load byte → R5=$00A0
# Card table at GRAM $00A0, reads GRAM words
interpretations.append({
    'name': 'I2: R5=$00A0 (GRAM), word card, xor=next, andi=$3607',
    'card_table': [GRAM_DATA.get(0x00A0 + i, 0) for i in range(8)],
    'card_is_byte_read': False,
    'xor_next_attr': True,
    'andi_mask': 0x3607,
    'andi_is_sdbd': False,
})

# Interpretation 3: Card table from ROM $65A0 as bytes (MVI@ reads bytes due to SDBD)
interpretations.append({
    'name': 'I3: R5=$65A0, byte card (MVI@ SDBD inherit), xor=next, andi=$3607',
    'card_table': card_bytes,
    'card_is_byte_read': True,
    'xor_next_attr': True,
    'andi_mask': 0x3607,
    'andi_is_sdbd': False,
})

# Interpretation 4: XOR with self (not next attr)
interpretations.append({
    'name': 'I4: R5=$65A0, word card, xor=self, andi=$3607',
    'card_table': card_words,
    'card_is_byte_read': False,
    'xor_next_attr': False,
    'andi_mask': 0x3607,
    'andi_is_sdbd': False,
})

# Interpretation 5: SDBD ANDI byte masking
interpretations.append({
    'name': 'I5: R5=$65A0, word card, xor=next, andi=$3607 SDBD',
    'card_table': card_words,
    'card_is_byte_read': False,
    'xor_next_attr': True,
    'andi_mask': 0x3607,
    'andi_is_sdbd': True,
})

# Interpretation 6: Different ANDI mask
interpretations.append({
    'name': 'I6: R5=$65A0, word card, xor=next, andi=$07FF',
    'card_table': card_words,
    'card_is_byte_read': False,
    'xor_next_attr': True,
    'andi_mask': 0x07FF,
    'andi_is_sdbd': False,
})

# Interpretation 7: ANDI with $3F07 (common alternative)
interpretations.append({
    'name': 'I7: R5=$65A0, word card, xor=next, andi=$3F07',
    'card_table': card_words,
    'card_is_byte_read': False,
    'xor_next_attr': True,
    'andi_mask': 0x3F07,
    'andi_is_sdbd': False,
})

# Interpretation 8: R5=$00A0 with byte reads from GRAM
interpretations.append({
    'name': 'I8: R5=$00A0, GRAM byte, xor=next, andi=$3607',
    'card_table': [GRAM_DATA.get(0x00A0 + i, 0) for i in range(8)],
    'card_is_byte_read': True,
    'xor_next_attr': True,
    'andi_mask': 0x3607,
    'andi_is_sdbd': False,
})

# Interpretation 9: R5=$00A0 from GRAM bytes at even/odd addresses
# GRAM alias might use different byte offsets
gram_bytes_even = [GRAM_DATA.get(0x00A0 + i, 0) for i in range(0, 16, 2)]
gram_words_from_gram = [
    (GRAM_DATA.get(0x00A0 + i*2 + 1, 0) << 8) | GRAM_DATA.get(0x00A0 + i*2, 0)
    for i in range(8)
]
interpretations.append({
    'name': 'I9: R5=$00A0, GRAM 16-bit words, xor=next, andi=$3607',
    'card_table': gram_words_from_gram,
    'card_is_byte_read': False,
    'xor_next_attr': True,
    'andi_mask': 0x3607,
    'andi_is_sdbd': False,
})

# Interpretation 10: The card table needs to be modified — try common game patterns
# What if the card table is REVERSED (group 0 gets card[7], etc)?
interpretations.append({
    'name': 'I10: reversed word card, xor=next, andi=$3607',
    'card_table': list(reversed(card_words)),
    'card_is_byte_read': False,
    'xor_next_attr': True,
    'andi_mask': 0x3607,
    'andi_is_sdbd': False,
})

# Interpretation 11: Card = attr (game reuses attr as card)
interpretations.append({
    'name': 'I11: card=attr, xor=next, andi=$3607',
    'card_table': attr_table,
    'card_is_byte_read': False,
    'xor_next_attr': True,
    'andi_mask': 0x3607,
    'andi_is_sdbd': False,
})

# Interpretation 12: Card table from nearby ROM data
# Maybe the card table is at $65A7 or some other offset
for offset in [-2, -1, 1, 2, 4, 8]:
    base = 0x65A0 + offset
    interp_card = [rw_be(rom, base + i) for i in range(8)]
    interpretations.append({
        'name': f'I{len(interpretations)+1}: R5=${base:04X}, word card, xor=next, andi=$3607',
        'card_table': interp_card,
        'card_is_byte_read': False,
        'xor_next_attr': True,
        'andi_mask': 0x3607,
        'andi_is_sdbd': False,
    })


# =========================================================================
# Test all interpretations
# =========================================================================

print(f"\nTesting {len(interpretations)} interpretations...")
print(f"Distinct BACKTAB words to match: {len(ALL_DISTINCT)}")
print(f"  {[f'${w:04X}' for w in sorted(ALL_DISTINCT)]}")
print()

best_interpretation = None
best_match_count = 0

for interp in interpretations:
    # Compute BACKTAB for all 8 group indices (tile_value >> 5)
    outputs = {}
    for group_idx in range(8):
        bt = l5ec7_compute(
            attr_table, interp['card_table'], group_idx,
            card_is_byte_read=interp['card_is_byte_read'],
            xor_next_attr=interp['xor_next_attr'],
            andi_mask=interp['andi_mask'],
            andi_is_sdbd=interp['andi_is_sdbd'],
        )
        outputs[group_idx] = bt
    
    # Count matches
    matches = set()
    for group_idx, bt in outputs.items():
        if bt in ALL_DISTINCT:
            matches.add(bt)
    
    match_count = len(matches)
    
    if match_count > best_match_count:
        best_match_count = match_count
        best_interpretation = interp
    
    if match_count >= 3:  # Show interpretations with at least 3 matches
        print(f"{interp['name']}")
        print(f"  Matches: {match_count} words: {[f'${w:04X}' for w in sorted(matches)]}")
        for g in range(8):
            bt = outputs[g]
            marker = " ✓" if bt in ALL_DISTINCT else "  "
            print(f"    Group {g}: ${bt:04X}{marker}")
        print()

print("=" * 80)
print(f"Best: {best_match_count} matches")
print("=" * 80)

# =========================================================================
# Reverse-engineer: what card values does the game ACTUALLY use?
# =========================================================================

print("\n" + "=" * 80)
print("REVERSE ENGINEERING: What card values does the game actually use?")
print("=" * 80)

# For each BACKTAB word, compute the necessary card value given the attr
# and the L_5EC7 formula (with XOR next attr and ANDI=$3607)

for group_idx in range(8):
    attr_word = attr_table[group_idx]
    
    # The attr contribution to BACKTAB
    r1 = (attr_word >> 2) & 0xFFFF
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    if group_idx + 1 < len(attr_table):
        r1 ^= attr_table[group_idx + 1]
    else:
        r1 ^= attr_word
    r1 &= 0x3607
    
    # We need: backtab = r1 ^ (card << 3)
    # So: card_needed = ((backtab ^ r1) >> 3) & mask
    # For each actual BACKTAB word, find which group might produce it
    
    print(f"\n  Group {group_idx} (attr=${attr_word:04X}, r1_attr=${r1:04X}):")
    print(f"    R1 attr contribution: ${r1:04X} ({r1:016b})")
    
    # Show which BACKTAB words this group CAN produce with various card values
    for bt in sorted(ALL_DISTINCT):
        needed_card = ((bt ^ r1) >> 3) & 0x1FFF
        # Check if this card value is reasonable (0-255 for GROM, or 0x100-0x1FF for GRAM)
        if 0 <= needed_card <= 0x1FF:
            # Recompute to verify
            recomputed = r1 ^ ((needed_card << 3) & 0xFFFF)
            if recomputed == bt:
                print(f"    → ${bt:04X} needs card=${needed_card:04X} (${needed_card:02X} byte) {'GRAM' if needed_card & 0x100 else 'GROM'}")


# =========================================================================
# Conclusion: what WORKS
# =========================================================================

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)

if best_match_count >= 30:
    print(f"  FOUND WORKING INTERPRETATION: {best_interpretation['name']}")
    print(f"  Matches: {best_match_count}/{len(ALL_DISTINCT)} distinct BACKTAB words")
else:
    print(f"  No single interpretation matches all {len(ALL_DISTINCT)} words.")
    print(f"  Best: {best_match_count}/{len(ALL_DISTINCT)} matches.")
    print()
    print("  This strongly suggests the card table IS modified at runtime.")
    print()
    
    # Try: what if groups 0-2 use card=$0000 (walls), groups 3-5 use ROM values (doors)?
    print("  Testing runtime modification hypothesis:")
    print("  (Groups 0-2: card=$0000, Groups 3-5: ROM values, Groups 6-7: ?)")
    
    # Build reasonable card table
    modified_card = list(card_words)
    modified_card[0] = 0x0000  # wall
    modified_card[1] = 0x0000  # wall  
    modified_card[2] = 0x0000  # wall
    # Groups 3-5 keep ROM values (doors)
    # Groups 6-7: try common floor values
    
    for trial_card6 in [0x0000, 0x0106, 0x03C8, 0x0008, 0x0108]:
        for trial_card7 in [0x0000, 0x0107, 0x0108, 0x030C, 0x0008]:
            trial_card = list(modified_card)
            trial_card[6] = trial_card6
            trial_card[7] = trial_card7
            
            outputs = {}
            for g in range(8):
                bt = l5ec7_compute(attr_table, trial_card, g)
                outputs[g] = bt
            
            match_set = set()
            for g, bt in outputs.items():
                if bt in ALL_DISTINCT:
                    match_set.add(bt)
            
            if len(match_set) >= 5:
                print(f"\n  card[6]=${trial_card6:04X}, card[7]=${trial_card7:04X}: {len(match_set)} matches")
                for g in range(8):
                    marker = " ✓" if outputs[g] in ALL_DISTINCT else "  "
                    print(f"    Group {g}: ${outputs[g]:04X}{marker}  (card=${trial_card[g]:04X})")
