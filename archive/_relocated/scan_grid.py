import subprocess, os, sys, json
sys.path.insert(0,'.')
PROJ=os.path.abspath('.')
JZ=os.path.join(PROJ,"jzintv-20200712-win32-sdl2","bin","jzintv.exe")
env=dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
from render_all_rooms import IDLE_PATCHES, parse_backtab, extract_backtab_from_output
def cap(g175,g176,tag):
    L=[f"p {a:04X} {v:04X}" for a,v in IDLE_PATCHES]
    L+= ["p 55C0 0034","p 55C1 0034","p 55C2 0034",
         "p 55CF 02B8", f"p 55D0 {g175:04X}", "p 55D3 02B8", f"p 55D4 {g176:04X}",
         "b 5038","r 8000000","p 019C 0000","b 55DA","r 8000000","m 0200 240","q"]
    sp=f"traces/rooms/sg_{tag}.txt"; op=f"traces/rooms/sg_{tag}_out.txt"
    open(sp,"w").write("\n".join(L)+"\n")
    with open(op,"w",encoding="utf-8",errors="replace") as f:
        p=subprocess.Popen([JZ,"-d",f"--script={sp}","-e","exec.bin","-g","grom.bin","Swords and Serpents.bin"],
                           stdout=f,stderr=subprocess.STDOUT,env=env,cwd=PROJ)
        try: p.wait(timeout=120)
        except subprocess.TimeoutExpired: p.kill(); p.wait()
    return parse_backtab(extract_backtab_from_output(open(op,encoding="utf-8",errors="replace").read()))
W,H=32,64
canvas=[[0x1603]*W for _ in range(H)]
for cstart,g175 in {0:0x00,12:0x0C}.items():
    for g176 in [0x00,0x0C,0x18,0x24,0x30,0x3C]:
        bt=cap(g175,g176,f"c{cstart}_r{g176:02X}")
        for r in range(12):
            for c in range(20):
                R,C=g176+r,cstart+c
                if R<H and C<W: canvas[R][C]=bt[r][c]
json.dump({'w':W,'h':H,'grid':canvas}, open('level0_backtab.json','w'))
from collections import Counter
cnt=Counter(canvas[r][c] for r in range(H) for c in range(W))
print('saved level0_backtab.json. word frequencies:')
for w,n in cnt.most_common(): print(f'  0x{w:04X}: {n}')
