import sys
sys.stdout.reconfigure(encoding='utf-8')

rom = open('Swords and Serpents.bin', 'rb').read()

# jzIntv verified values (from verify_mem2_out.txt):
# $65CE=$0098, $65CF=$006C, $65D0=$0011, $65D1=$006D, $65D2=$0086
JZ_CONFIRMED = {0x65CE: 0x0098, 0x65CF: 0x006C, 0x65D0: 0x0011, 0x65D1: 0x006D, 0x65D2: 0x0086}

print("=== Comparing BE vs LE against confirmed jzIntv values ===")
print()
print("Addr    RawBytes    BE       LE       jzIntv   BE_match  LE_match")
print("-" * 72)
for addr in sorted(JZ_CONFIRMED.keys()):
    off = (addr - 0x5000) * 2
    b0, b1 = rom[off], rom[off+1]
    be = (b0 << 8) | b1
    le = b0 | (b1 << 8)
    jz = JZ_CONFIRMED[addr]
    be_ok = "YES" if be == jz else "NO"
    le_ok = "YES" if le == jz else "NO"
    print(f"${addr:04X}   {b0:02X} {b1:02X}      ${be:04X}     ${le:04X}     ${jz:04X}     {be_ok:5s}    {le_ok:5s}")

print()
print("=== BE reading of $65A0-$65C7 (the lookup tables) ===")
for i in range(40):
    addr = 0x65A0 + i
    off = (addr - 0x5000) * 2
    be = (rom[off] << 8) | rom[off+1]
    print(f"  BE ${addr:04X} = ${be:04X}")

print()
print("=== LE reading of $65A0-$65C7 ===")
for i in range(40):
    addr = 0x65A0 + i
    off = (addr - 0x5000) * 2
    le = rom[off] | (rom[off+1] << 8)
    print(f"  LE ${addr:04X} = ${le:04X}")

# Now do the L_5EC7 simulation with BE data
print()
print("=== L_5EC7 simulation using BE data ===")
def rw(rom, addr, be_mode=True):
    off = (addr - 0x5000) * 2
    if be_mode:
        return (rom[off] << 8) | rom[off+1]
    else:
        return rom[off] | (rom[off+1] << 8)

def l5ec7(tv, rom, be_mode=True):
    idx = tv >> 5
    if idx >= 23:
        return 0
    attr0 = rw(rom, 0x65B7 + idx, be_mode)
    attr1 = rw(rom, 0x65B7 + idx + 1, be_mode)
    card_val = rw(rom, 0x65A0 + idx, be_mode)
    
    r1 = attr0 >> 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)  # SWAP
    r1 ^= attr1
    r1 &= 0x3607
    r3 = (card_val << 3) & 0xFFFF
    r1 ^= r3
    return r1

KNOWN = {0x1603, 0x081B, 0x1E13, 0x020F, 0x02B7, 0x02A7, 0x0257, 0x0287,
         0x02BF, 0x029F, 0x025F, 0x0207, 0x0327, 0x0317, 0x1EBB, 0x026F,
         0x024F, 0x022F, 0x021F, 0x023F, 0x03AF, 0x03EF, 0x03E7, 0x03B7,
         0x1E5B, 0x1E40, 0x0E60, 0x0823, 0x1E38, 0x1E02, 0x082B, 0x0367,
         0x0347, 0x036F, 0x03BF}

# BE mode
matches_be = 0
for idx in range(23):
    tv = idx << 5
    bt = l5ec7(tv, rom, be_mode=True)
    if bt in KNOWN:
        matches_be += 1
        print(f"  BE tile group {idx:2d} (${tv:04X}) -> ${bt:04X}  MATCH!")

print(f"\n  BE mode: {matches_be}/23 tile groups produce known BACKTAB words")

# LE mode
matches_le = 0
for idx in range(23):
    tv = idx << 5
    bt = l5ec7(tv, rom, be_mode=False)
    if bt in KNOWN:
        matches_le += 1
        print(f"  LE tile group {idx:2d} (${tv:04X}) -> ${bt:04X}  MATCH!")

print(f"\n  LE mode: {matches_le}/23 tile groups produce known BACKTAB words")

# Also check: what if $65A0 card table is 0 (only attr table matters)?
print()
print("=== Testing: card table = 0 (only attr table provides BACKTAB) ===")
for idx in range(8):
    tv = idx << 5
    attr0 = rw(rom, 0x65B7 + idx, True)
    attr1 = rw(rom, 0x65B7 + idx + 1, True)
    r1 = attr0 >> 2
    r1 = ((r1 & 0xFF) << 8) | ((r1 >> 8) & 0xFF)
    r1 ^= attr1
    r1 &= 0x3607
    # No card XOR
    known_str = " MATCH!" if r1 in KNOWN else ""
    print(f"  tile group {idx} (${idx<<5:04X}): attr0=${attr0:04X} attr1=${attr1:04X} -> ${r1:04X}{known_str}")
