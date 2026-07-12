"""Quick test: capture rooms 1 & 3 and verify they produce different data."""
import sys, os, hashlib
sys.path.insert(0, '.')
from compare_all_rooms import capture_room, extract_backtab_from_output, parse_backtab, decode_backtab_word

print("=== Testing room teleport fix ===")

results = {}
for room in [1, 3]:
    print(f"\nCapturing room {room}...")
    output, scr_path = capture_room(room)
    
    bt = extract_backtab_from_output(output)
    grid = parse_backtab(bt) if bt else None
    
    if grid:
        bt_hash = hash(tuple(tuple(row) for row in grid))
        # Count unique cards
        unique = set()
        for row in range(12):
            for col in range(20):
                card, fg, bg_bits, is_gram, _ = decode_backtab_word(grid[row][col])
                unique.add((card, is_gram))
        print(f"  BACKTAB hash: {bt_hash}, unique cards: {len(unique)}")
        
        # Show first 3 non-floor cards
        count = 0
        for row in range(12):
            for col in range(20):
                word = grid[row][col]
                if word != 0x1603:
                    card, fg, bg_bits, is_gram, _ = decode_backtab_word(word)
                    src = "GRAM" if is_gram else "GROM"
                    print(f"  [{row}][{col}] word=${word:04X} card={card} fg={fg} {src}")
                    count += 1
                    if count >= 3:
                        break
            if count >= 3:
                break
        
        results[room] = bt_hash
    
    if scr_path:
        print(f"  Screenshot: {scr_path}")
        # MD5 of screenshot
        from PIL import Image
        img = Image.open(scr_path)
        md5 = hashlib.md5(img.tobytes()).hexdigest()
        print(f"  Screenshot MD5: {md5[:16]}...")
        results[f"{room}_md5"] = md5

print()
if results.get(1) != results.get(3):
    print("SUCCESS: Rooms 1 and 3 have DIFFERENT BACKTAB hashes!")
else:
    print("FAIL: Rooms 1 and 3 still have the SAME BACKTAB hash!")

if results.get("1_md5") != results.get("3_md5"):
    print("SUCCESS: Rooms 1 and 3 have DIFFERENT screenshots!")
else:
    print("FAIL: Rooms 1 and 3 still have the SAME screenshot!")
