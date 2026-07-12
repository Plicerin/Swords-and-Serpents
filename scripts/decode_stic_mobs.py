#!/usr/bin/env python3
"""
Decode STIC MOB registers from jzintv title screen dump and render the actual sprite cards.
"""
from PIL import Image, ImageDraw

# ==== STIC Register Dump from title screen (m 0 40) ====
# Format: 8 consecutive 16-bit words per line, starting at $0000
stic_raw = [
    0x3B58, 0x3B60, 0x3800, 0x384A,  # $0000-$0003: MOB 0
    0x3800, 0x3800, 0x3800, 0x3800,  # $0004-$0007: MOB 1
    0x30B8, 0x30B8, 0x30D2, 0x3089,  # $0008-$000B: MOB 2
    0x3000, 0x3000, 0x3000, 0x3000,  # $000C-$000F: MOB 3
    0x1980, 0x2996, 0x09A7, 0x09B6,  # $0010-$0013: MOB 4
    0x09C0, 0x09D0, 0x09E0, 0x09F0,  # $0014-$0017: MOB 5
    0x3C00, 0x3C00, 0x3C00, 0x3C00,  # $0018-$001B: MOB 6
    0x3C00, 0x3C00, 0x3C00, 0x3C00,  # $001C-$001F: MOB 7
]

# ==== GRAM Card Data from title screen dump ====
# Each entry: 8 bytes (low bytes of 16-bit words at that address)
gram_raw = {}
gram_hex_data = """3800: 0040 0020 00FD 007F 003B 001E 0024 0008
3808: 00F0 00F0 0070 0020 0020 0000 0000 0000
3810: 0000 0000 0080 0080 00D0 00D0 00F0 00F0
3818: 00F0 00F8 00E8 0078 00F0 00F8 00F8 00F8
3820: 00F7 00FF 00FF 00FF 00EF 00E6 0000 0000
3828: 00EF 00FF 007F 00FF 00FF 00FD 00F8 00F8
3830: 00F0 00F8 00E8 00F8 00F0 00B8 0000 0000
3838: 0080 00C0 00E0 00E0 00E0 00E0 00E0 00E0
3840: 00FF 007F 0000 0000 0000 0000 0000 0000
3848: 00E0 00EC 00ED 00ED 00ED 00ED 00EC 00E0
3850: 00E0 00EC 00ED 00ED 00ED 00ED 00EC 00E0
3858: 007F 002E 003A 0036 006C 0074 005C 00FE
3860: 00FF 0000 00FF 00FE 00FE 00FF 0000 00FF
3868: 00AB 00AB 00AB 00AA 00AA 00AB 00AB 00AB
3870: 0000 0000 0087 009D 00FD 003F 0018 003C
3878: 0042 0081 0099 00BD 005A 0024 00DB 007E
3880: 0000 0018 0024 0018 00BD 00FF 00A5 00FF
3888: 0000 003C 004A 00D1 0085 00A9 004A 003C
3890: 00FF 00F9 00F3 00E7 00CF 007E 003C 0018
3898: 0099 00BD 00BD 00FF 0042 0066 0066 0024
38A0: 00C1 0055 007F 0055 0055 0055 0055 003E
38A8: 0018 003C 0018 003C 006E 00DF 006E 003C
38B0: 0000 0000 0040 00BF 0045 0000 0000 0000
38B8: 003C 0042 0099 0091 0091 0099 0042 003C
38C0: 0000 0078 001E 00FC 0018 0018 0031 0073
38C8: 0000 0000 0010 003B 007F 00FF 00FF 00FF
38D0: 000F 003C 00F8 00F0 00E2 00CA 009F 0039
38D8: 0000 0009 0095 00FF 00FF 0095 0009 0000
38E0: 0000 0083 001F 00FD 00FD 001F 0083 0000
38E8: 00F1 00DF 00BE 0076 0076 00BE 00DF 00F1
38F0: 0000 0006 000F 0099 00F3 00E6 000C 0000
38F8: 0073 0031 0018 0018 00FC 001E 0078 0000
3900: 00FF 00FF 00FF 007F 003B 0010 0000 0000
3908: 0039 009F 00CA 00E2 00F0 00F8 003C 000F
3910: 0000 0000 0000 0000 0000 0000 0000 0000
3918: 0000 0000 0000 0000 0000 0000 0000 0000
3920: 0000 0000 0000 0000 0000 0000 0000 0000
3928: 0000 0000 0000 0000 0000 0000 0000 0000
3930: 0000 0000 0000 0000 0000 0000 0000 0000
3938: 0000 0000 0000 0000 0000 0000 0000 0000
3940: 0000 0000 0000 0000 0000 0000 0000 0000
3948: 0000 0000 0000 0000 0000 0000 0000 0000
3950: 0000 0000 0000 0000 0000 0000 0000 0000
3958: 0000 0000 0000 0000 0000 0000 0000 0000
3960: 0000 0000 0000 0000 0000 0000 0000 0000
3968: 0000 0000 0000 0000 0000 0000 0000 0000
3970: 0000 0000 0000 0000 0000 0000 0000 0000
3978: 0000 0000 0000 0000 0000 0000 0000 0000
3980: 0018 003C 007E 0073 00F9 0099 0089 0089
3988: 0089 0089 0099 00F9 0073 007E 003C 0018
3990: 0000 0000 0000 0000 0000 0000 0000 00FF
3998: 0000 0000 0000 0000 0000 0000 0000 0000
39A0: 0000 0000 0000 0000 0018 0024 003C 0066
39A8: 0066 003C 0024 0018 0000 0000 0000 0000
39B0: 0000 0024 0011 003A 00AE 007B 006E 00FE
39B8: 007F 007C 00FE 005C 0088 0024 0000 0000"""

for line in gram_hex_data.strip().split('\n'):
    line = line.strip()
    if not line or ':' not in line:
        continue
    addr_str, bytes_str = line.split(':')
    addr = int(addr_str.strip(), 16)
    bytes_list = [int(b.strip(), 16) for b in bytes_str.strip().split()]
    gram_raw[addr] = bytes_list

# ======== IntelliVision Color Palette ========
INTV_COLORS = [
    (0, 0, 0),        # 0: Black
    (0, 0, 255),      # 1: Blue
    (200, 40, 40),    # 2: Red
    (200, 160, 40),   # 3: Tan/Gold
    (0, 128, 0),      # 4: Dark Green
    (0, 255, 0),      # 5: Green
    (255, 255, 0),    # 6: Yellow
    (255, 255, 255),  # 7: White
    (128, 128, 128),  # 8: Grey
    (0, 255, 255),    # 9: Cyan
    (255, 128, 0),    # A: Orange
    (128, 64, 0),     # B: Brown
    (255, 0, 255),    # C: Magenta
    (128, 128, 255),  # D: Light Blue
    (255, 255, 128),  # E: Light Yellow
    (0, 128, 128),    # F: Dark Cyan
]

# ======== STIC Register Decoding ========
# MOB X register ($00+4N): bits 7-0 = X position (XPOS), bit 8 = XSIZE, bits 10-9 = X high
# But actually the STIC register format in jzintv is:
# Word at $00+4N contains XPOS in lower byte
# Word at $01+4N (Attribute/A): Visibility, XSIZE, interaction, etc.
# Word at $02+4N (Y): YPOS in lower byte
# Word at $03+4N (Card/B): YSIZE, YRES, card number, XFLIP, YFLIP

# From jzintv docs: STIC registers are at specific addresses
# But actually on the real Intellivision hardware, STIC registers are not normal memory
# jzintv maps them to a contiguous memory space
# The exact mapping depends on jzintv's implementation

# Let me use the approach from jzintv source code
# From jzintv's stic.c: the register layout is:
# Offset 0: XPOS (bits 7-0), XSIZE (bit 8)
# Offset 2: YPOS (bits 7-0), YSIZE (bit 8), YRES (bit 9)  
# Offset 4: A register (various control bits)
# Offset 6: B register (card number etc.)

# BUT the debugger dump shows 16-bit words at byte addresses
# Word at $0000 = $3B58 = STIC register $00
# In Intellivision, MOB 0 uses STIC addresses $00-$03
# The jzintv debugger shows 16-bit word at each byte address
# So each pair of bytes is one register

# Let me parse the registers as 8-bit low bytes extracted from the 16-bit words
# since the important data is in the lower byte

print("=" * 70)
print("STIC MOB REGISTER DECODE (Title Screen)")
print("=" * 70)

for mob in range(8):
    base = mob * 4
    x_word = stic_raw[base]
    a_word = stic_raw[base + 1]
    y_word = stic_raw[base + 2]
    b_word = stic_raw[base + 3]
    
    # Extract relevant fields
    xpos = x_word & 0xFF
    ypos = y_word & 0xFF
    
    # A register decode (from word at $01+4N)
    # Bit 7: GROM/GRAM (0=GRAM, 1=GROM) - but this depends on bit position
    # In jzintv's memory model, the A register is the second byte
    
    # B register decode (from word at $03+4N)  
    # Card number in bits 0-7 (but actually varies by GRAM/GROM mode)
    # For GRAM: bits 0-6 = card (0-63)
    # For GROM: bits 0-8 = card (0-255)
    
    # Let me try decoding the B register:
    # $384A -> lower byte = $4A
    card_bits = b_word & 0xFF
    
    # Check A register for GROM/GRAM flag
    a_low = a_word & 0xFF
    
    # For Intellivision MOB A register:
    # Bit 0: Collision detect
    # Bit 1: Reserved  
    # Bit 2: Priority
    # Bit 3: Interaction
    # Bit 4: XSIZE (0=8px, 1=16px)
    # Bit 5: VISB (0=visible, 1=hidden)
    # Bit 6: Reserved
    # Bit 7: GROM/GRAM (0=GROM, 1=GRAM)

    # Wait, I think the register layout in jzintv's dump is:
    # The 16-bit word contains the actual 8-bit register in the LOW byte
    # This matches how jzintv maps STIC to 16-bit memory
    
    x_size_bit = a_word & 0x0010  # XSIZE
    visb_bit = a_word & 0x0020    # VISB (visible=0, hidden=1) 
    gram_flag = a_word & 0x0080   # GRAM flag
    
    # Actually, I think the standard Intellivision format puts:
    # X register = lower byte of word
    # Let me just decode all registers as their lower bytes for now
    
    card_num = b_word & 0xFF  # lower byte of B register
    
    # The upper byte may contain additional card bits
    # For GRAM, card numbers are 0-63 (6 bits)
    # For GROM, card numbers are 0-255 (8 bits)
    
    visible = True  # can't easily determine from just the word
    
    print(f"\nMOB {mob}: X={xpos:3d}, Y={ypos:3d}, Card=${card_num:02X} ({card_num})")
    print(f"  X word=${x_word:04X}, A word=${a_word:04X}, Y word=${y_word:04X}, B word=${b_word:04X}")
    
    # Determine if the MOB is hidden (X=0, Y=0 usually means hidden)
    if xpos == 0 and ypos == 0:
        print(f"  -> HIDDEN (X=0, Y=0)")
        continue
    
    # Check if card is GROM or GRAM
    # GROM cards are at $3000-$37FF (0-255)  
    # GRAM cards are at $3800-$39FF (0-63)
    # If card < 64, could be either GROM or GRAM
    # The A register flag determines this
    
    # Let me just render the card from GRAM and see
    if card_num < 64:
        gram_addr = 0x3800 + card_num * 8
        if gram_addr in gram_raw:
            data = gram_raw[gram_addr]
            print(f"  GRAM card ${card_num:02X} (addr ${gram_addr:04X}):")
            for row in range(8):
                byte = data[row]
                line = ''
                for col in range(8):
                    bit = (byte >> (7 - col)) & 1
                    line += '##' if bit else '..'
                print(f"    {line}")
        else:
            print(f"  GRAM card ${card_num:02X} (addr ${gram_addr:04X}): NO DATA")
    else:
        # GROM card - compute GROM offset
        # GROM is at $3000 in STIC memory, but GROM starts at card 0
        # In the real GROM ROM, cards 0-255
        print(f"  GROM card ${card_num:02X} ({card_num}) - GROM character")

# ======== Render ALL GRAM cards in a sheet ========
print("\n" + "=" * 70)
print("Rendering GRAM card sheet...")
print("=" * 70)

ZOOM = 12
COLS = 8
ROWS = 8
fg_color = INTV_COLORS[3]   # Gold/Tan
bg_color = INTV_COLORS[0]   # Black

img_w = COLS * 8 * ZOOM
img_h = ROWS * 8 * ZOOM
img = Image.new('RGB', (img_w, img_h), (40, 40, 40))
draw = ImageDraw.Draw(img)

for card_idx in range(64):
    gram_addr = 0x3800 + card_idx * 8
    data = gram_raw.get(gram_addr, [0]*8)
    
    col = card_idx % COLS
    row = card_idx // COLS
    ox = col * 8 * ZOOM
    oy = row * 8 * ZOOM
    
    for y in range(8):
        byte = data[y]
        for x in range(8):
            bit = (byte >> (7 - x)) & 1
            color = fg_color if bit else bg_color
            for dy in range(ZOOM):
                for dx in range(ZOOM):
                    px = ox + x * ZOOM + dx
                    py = oy + y * ZOOM + dy
                    if 0 <= px < img_w and 0 <= py < img_h:
                        img.putpixel((px, py), color)
    
    # Label
    label = f"${card_idx:02X}"
    # Put a text label (simple approach: white pixel in corner)
    # We'll just draw a border between cards

img.save('sprites/all_gram_cards_labeled.png')
print("Saved: sprites/all_gram_cards_labeled.png")

# ======== Render only the active MOB cards ========
print("\n" + "=" * 70)
print("Rendering active MOB cards...")
print("=" * 70)

active_cards = []
for mob in range(8):
    base = mob * 4
    x_word = stic_raw[base]
    a_word = stic_raw[base + 1]
    y_word = stic_raw[base + 2]
    b_word = stic_raw[base + 3]
    
    xpos = x_word & 0xFF
    ypos = y_word & 0xFF
    card_num = b_word & 0xFF
    
    if xpos == 0 and ypos == 0:
        continue
    if card_num >= 64:
        continue
    
    active_cards.append((mob, card_num, xpos, ypos))
    print(f"MOB {mob}: card=${card_num:02X}, X={xpos}, Y={ypos}")

# Render active cards side by side
if active_cards:
    num_cards = len(active_cards)
    img_w2 = num_cards * 8 * ZOOM + (num_cards - 1) * 4
    img_h2 = 8 * ZOOM
    img2 = Image.new('RGB', (img_w2, img_h2), (60, 60, 60))
    
    for i, (mob, card_num, xpos, ypos) in enumerate(active_cards):
        gram_addr = 0x3800 + card_num * 8
        data = gram_raw.get(gram_addr, [0]*8)
        
        ox = i * (8 * ZOOM + 4)
        
        for y in range(8):
            byte = data[y]
            for x in range(8):
                bit = (byte >> (7 - x)) & 1
                color = fg_color if bit else bg_color
                for dy in range(ZOOM):
                    for dx in range(ZOOM):
                        px = ox + x * ZOOM + dx
                        py = y * ZOOM + dy
                        if 0 <= px < img_w2 and 0 <= py < img_h2:
                            img2.putpixel((px, py), color)
        
        # Label below
        label = f"MOB{mob}"
    
    img2.save('sprites/active_mob_cards.png')
    print(f"Saved: sprites/active_mob_cards.png ({num_cards} cards)")

# ======== Also dump all GRAM cards as ASCII ========
print("\n" + "=" * 70)
print("ALL GRAM CARDS ASCII (title screen)")
print("=" * 70)
for card_idx in range(64):
    gram_addr = 0x3800 + card_idx * 8
    data = gram_raw.get(gram_addr, [0]*8)
    has_data = any(b != 0 for b in data)
    if not has_data:
        continue
    print(f"\nGRAM ${card_idx:02X} (addr ${gram_addr:04X}):")
    for row in range(8):
        byte = data[row]
        line = ''
        for col in range(8):
            bit = (byte >> (7 - col)) & 1
            line += '##' if bit else '..'
        print(f"  {line}")

print("\nDone!")
