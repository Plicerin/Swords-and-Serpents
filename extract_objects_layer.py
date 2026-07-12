"""
Swords & Serpents - Re-capture level BACKTABs with ALL object discovery/active
flags forced on ($0180-$018D and $019D-$01AA poked to $FFFF), so the object
overlay pass (L_63F5 pipeline) draws every object - items, treasures, and the
Serpent - into the BACKTAB. Diff against assets/level{N}_maze.json to find the
object tiles.

Usage: python extract_objects_layer.py <level> [<level> ...]
"""
import subprocess, os, sys, json, time
sys.path.insert(0, '.')
PROJ = os.path.abspath('.')
JZ = os.path.join(PROJ, "jzintv", "jzintv-20200712-win32-sdl2", "bin", "jzintv.exe")
env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
from render_all_rooms import IDLE_PATCHES, parse_backtab, extract_backtab_from_output

FLAG_POKES = [f"p {a:04X} FFFF" for a in list(range(0x0180, 0x018E)) + list(range(0x019D, 0x01AB))]

def cap_for_level(level, g175, g176, tag):
    data_ptr = 0x65DC + level * 8
    L = [f"p {a:04X} {v:04X}" for a, v in IDLE_PATCHES]
    L += [
        "p 55C0 0034", "p 55C1 0034", "p 55C2 0034",
        "p 55CF 02B8", f"p 55D0 {g175:04X}", "p 55D3 02B8", f"p 55D4 {g176:04X}",
        "b 5038", "r 8000000",
        f"p 019C {level:04X}",
        f"p 02F4 {data_ptr:04X}",
    ]
    L += FLAG_POKES
    L += [
        "b 55DA", "r 8000000",
        "m 0200 240",
        "q",
    ]
    script_path = f"traces/rooms/obj_lv{level}_{tag}.txt"
    output_path = f"traces/rooms/obj_lv{level}_{tag}_out.txt"
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

W, H = 32, 64
COL_STARTS = {0: 0x00, 12: 0x0C}
ROW_STARTS = [0x00, 0x0C, 0x18, 0x24, 0x30, 0x3C]

levels = [int(a) for a in sys.argv[1:]] or [0]
for level in levels:
    print(f"=== level {level} (flags forced) ===", flush=True)
    canvas = [[None] * W for _ in range(H)]
    for cstart, g175 in COL_STARTS.items():
        for g176 in ROW_STARTS:
            tag = f"c{cstart}_r{g176:02X}"
            try:
                bt = cap_for_level(level, g175, g176, tag)
                for r in range(12):
                    tr = g176 + r
                    if tr >= H: continue
                    for c in range(20):
                        tc = cstart + c
                        if tc >= W: continue
                        canvas[tr][tc] = bt[r][c]
                print(f"  [{tag}] OK", flush=True)
            except Exception as e:
                print(f"  [{tag}] FAILED: {e}", flush=True)

    out = {"w": W, "h": H, "grid": [[v if v is not None else 0 for v in row] for row in canvas]}
    path = f"assets/level{level}_objects.json"
    json.dump(out, open(path, "w"))
    print(f"  saved {path}", flush=True)

    # Diff vs the plain maze
    base = json.load(open(f"assets/level{level}_maze.json"))["grid"]
    diffs = []
    for r in range(H):
        for c in range(W):
            v = canvas[r][c]
            if v is None: continue
            if v != base[r][c]:
                card = (v >> 3) & 0x3F
                gram = bool(v & 0x800)
                fg = v & 7
                bg = ((v >> 9) & 0xB) | ((v >> 11) & 0x4)
                diffs.append((r, c, v, card, gram, fg, bg))
    print(f"  {len(diffs)} tiles differ from plain maze:")
    for d in diffs:
        r, c, v, card, gram, fg, bg = d
        tag = "GRAM" if gram else "GROM"
        star = "  <== DRAGON RANGE" if gram and 24 <= card <= 33 else ""
        print(f"    row {r:2d} col {c:2d}: {v:04X} {tag} card {card:2d} fg {fg} bg {bg}{star}", flush=True)
