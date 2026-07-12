"""Scan entire ROM for unknown (not yet categorized) sprite card clusters."""
import sys
rom = open("Swords and Serpents.bin", "rb").read()

def rom_bytes(addr, count):
    off = (addr - 0x5000) * 2
    return [rom[off + 2*i + 1] for i in range(count)]

# Known regions to exclude
known_regions = [(0x5A00, 0x5D00), (0x5DE0, 0x5E40), (0x6600, 0x6800), (0x61E0, 0x6200),
                 (0x62D0, 0x6330), (0x5B00, 0x5B50)]  # title sprites + descriptor table

# Scan in batches
def is_empty_card(addr):
    """Check if an 8-card address has all zeros."""
    off = (addr - 0x5000) * 2
    for i in range(8):
        pos = off + 2*i + 1
        if pos < len(rom) and rom[pos] != 0:
            return False
    return True

def pixel_count(addr):
    """Count active pixels in card at addr."""
    off = (addr - 0x5000) * 2
    total = 0
    for i in range(8):
        pos = off + 2*i + 1
        if pos < len(rom):
            total += bin(rom[pos]).count("1")
    return total

def ascii_card(addr):
    off = (addr - 0x5000) * 2
    lines = []
    for i in range(8):
        pos = off + 2*i + 1
        b = rom[pos] if pos < len(rom) else 0
        lines.append("".join("#" if (b>>(7-c))&1 else "." for c in range(8)))
    return "\n".join(lines)

# Find runs of non-empty cards
addr = 0x5000
in_run = False
run_start = 0
run_len = 0

unknown_clusters = []
while addr <= 0x6FF8:
    px = pixel_count(addr)
    if px >= 4 and not is_empty_card(addr):
        if not in_run:
            run_start = addr
            run_len = 1
            in_run = True
        else:
            run_len += 1
    else:
        if in_run and run_len >= 2:
            # Check if in known region
            in_known = any(ks <= run_start < ke for ks, ke in known_regions)
            if not in_known:
                unknown_clusters.append((run_start, run_len))
        in_run = False
    addr += 8

if in_run and run_len >= 2:
    in_known = any(ks <= run_start < ke for ks, ke in known_regions)
    if not in_known:
        unknown_clusters.append((run_start, run_len))

print(f"Found {len(unknown_clusters)} unknown clusters with >=2 non-empty cards:\n")

for start, length in unknown_clusters:
    total_px = sum(pixel_count(start + i*8) for i in range(length))
    print(f"--- ${start:04X}-${start+length*8-1:04X} ({length} cards, {total_px} px) ---")
    for i in range(length):
        ca = start + i*8
        px = pixel_count(ca)
        print(f"  Card {i} @ ${ca:04X} ({px} px):")
        print(f"    {ascii_card(ca)}")
    print()

if not unknown_clusters:
    print("No unknown clusters found!")
    
# Also print known clusters for reference
print("\n\n===== KNOWN CLUSTER SIZES (for reference) =====")
known_clusters_info = [
    (0x5AE6, "anim_sprite_a (spawn effect)"),
    (0x5BCC, "dragon (boss)"),
    (0x5C1C, "enemy_char"),
    (0x5C4E, "projectile (fireball)"),
    (0x5C9E, "anim_sprite_b (wizard)"),
    (0x5DE5, "desc3 (item)"),
    (0x6677, "desc1 target"),
    (0x6760, "desc567 target"),
]
for addr, name in known_clusters_info:
    px = sum(pixel_count(addr + i*8) for i in range(4))
    print(f"  ${addr:04X}: {name} ({px} px over 4 cards)")
