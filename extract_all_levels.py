"""
Swords & Serpents — Extract all 14 dungeon levels (0-13) from ROM via jzIntv.

Each level is a 32x64 tile maze captured by sweeping the (G_0175, G_0176)
viewport across the full grid and stitching 20x12 snapshots together.
"""
import subprocess, os, sys, json, time
sys.path.insert(0, '.')
PROJ = os.path.abspath('.')
JZ = os.path.join(PROJ, "jzintv", "jzintv-20200712-win32-sdl2", "bin", "jzintv.exe")
env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
from render_all_rooms import IDLE_PATCHES, parse_backtab, extract_backtab_from_output

def cap_for_level(level, g175, g176, tag):
    """Capture a 20x12 BACKTAB snapshot from jzIntv at the given viewport offset.
    
    Sets G_019C = level and G_02F4 = $65DC + level*8 so the ROM uses the
    correct tile stream data for this dungeon level.
    """
    data_ptr = 0x65DC + level * 8
    L = [f"p {a:04X} {v:04X}" for a, v in IDLE_PATCHES]
    L += [
        "p 55C0 0034", "p 55C1 0034", "p 55C2 0034",
        "p 55CF 02B8", f"p 55D0 {g175:04X}", "p 55D3 02B8", f"p 55D4 {g176:04X}",
        "b 5038", "r 8000000",
        f"p 019C {level:04X}",
        f"p 02F4 {data_ptr:04X}",
        "b 55DA", "r 8000000",
        "m 0200 240",
        "q",
    ]
    script_path = f"traces/rooms/lv{level}_{tag}.txt"
    output_path = f"traces/rooms/lv{level}_{tag}_out.txt"
    with open(script_path, "w") as f:
        f.write("\n".join(L) + "\n")
    with open(output_path, "w", encoding="utf-8", errors="replace") as f:
        p = subprocess.Popen(
            [JZ, "-d", f"--script={script_path}", "-e", "exec.bin",
             "-g", "grom.bin", "Swords and Serpents.bin"],
            stdout=f, stderr=subprocess.STDOUT, env=env, cwd=PROJ,
        )
        try:
            p.wait(timeout=60)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait()
    text = open(output_path, encoding="utf-8", errors="replace").read()
    return parse_backtab(extract_backtab_from_output(text))

W, H = 32, 64  # all dungeon levels are 32 tiles wide × 64 tall
# Column starts: 0 and 12 cover 32 cols (two 20-wide captures overlap at edges)
COL_STARTS = {0: 0x00, 12: 0x0C}
# Row starts: every 12 rows covers the 64-row height (6 captures × 12 = 72, clamped to 64)
ROW_STARTS = [0x00, 0x0C, 0x18, 0x24, 0x30, 0x3C]

os.makedirs("assets", exist_ok=True)
os.makedirs("traces/rooms", exist_ok=True)

total_start = time.time()
for level in range(14):
    print(f"\n{'='*60}")
    print(f"Level {level} (G_019C={level:#06x}, G_02F4={0x65DC+level*8:#06x})")
    print(f"{'='*60}")
    
    canvas = [[0x1603] * W for _ in range(H)]
    success = True
    viewport_count = 0
    
    for cstart, g175 in COL_STARTS.items():
        for g176 in ROW_STARTS:
            tag = f"c{cstart}_r{g176:02X}"
            try:
                bt = cap_for_level(level, g175, g176, tag)
                for r in range(12):
                    tile_row = g176 + r
                    if tile_row >= H:
                        continue
                    for c in range(20):
                        tile_col = cstart + c
                        if tile_col >= W:
                            continue
                        canvas[tile_row][tile_col] = bt[r][c]
                viewport_count += 1
                print(f"  [{tag}] OK ({len(bt)} rows)", flush=True)
            except Exception as e:
                print(f"  [{tag}] FAILED: {e}", flush=True)
                success = False
    
    if success:
        # Save
        path = f"assets/level{level}_maze.json"
        with open(path, "w") as f:
            json.dump({"w": W, "h": H, "grid": canvas}, f)
        
        # Word frequency summary
        from collections import Counter
        cnt = Counter(canvas[r][c] for r in range(H) for c in range(W))
        print(f"  Saved {path} ({viewport_count} viewports)")
        print(f"  Floor tiles: {cnt.get(0x1603, 0)}/{W*H}")
        for w, n in cnt.most_common(8):
            print(f"    0x{w:04X}: {n}")
    else:
        print(f"  *** Level {level} has errors — partial data saved anyway")
        path = f"assets/level{level}_maze.json"
        with open(path, "w") as f:
            json.dump({"w": W, "h": H, "grid": canvas}, f)
        print(f"  Saved {path} (partial)")

elapsed = time.time() - total_start
print(f"\n{'='*60}")
print(f"All done in {elapsed:.0f}s. Files in assets/level{{0..13}}_maze.json")
