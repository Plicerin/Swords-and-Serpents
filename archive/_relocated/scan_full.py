import subprocess, os, sys
sys.path.insert(0,'.')
PROJ=os.path.abspath('.')
JZ=os.path.join(PROJ,"jzintv-20200712-win32-sdl2","bin","jzintv.exe")
env=dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
from render_all_rooms import IDLE_PATCHES, parse_backtab, extract_backtab_from_output, reconstruct_dungeon_gram, load_grom, decode_fgbg_word, JZINTV_PALETTE
from PIL import Image

def cap(g175,g176,tag):
    L=[f"p {a:04X} {v:04X}" for a,v in IDLE_PATCHES]
    L+= ["p 55C0 0034","p 55C1 0034","p 55C2 0034",
         "p 55CF 02B8", f"p 55D0 {g175:04X}", "p 55D3 02B8", f"p 55D4 {g176:04X}",
         "b 5038","r 8000000","p 019C 0000","b 55DA","r 8000000","m 0200 240","q"]
    sp=f"traces/rooms/sf_{tag}.txt"; op=f"traces/rooms/sf_{tag}_out.txt"
    open(sp,"w").write("\n".join(L)+"\n")
    with open(op,"w",encoding="utf-8",errors="replace") as f:
        p=subprocess.Popen([JZ,"-d",f"--script={sp}","-e","exec.bin","-g","grom.bin","Swords and Serpents.bin"],
                           stdout=f,stderr=subprocess.STDOUT,env=env,cwd=PROJ)
        try: p.wait(timeout=120)
        except subprocess.TimeoutExpired: p.kill(); p.wait()
    return parse_backtab(extract_backtab_from_output(open(op,encoding="utf-8",errors="replace").read()))

# vertical scan, two horizontal columns (0 and 12) to cover 32 wide
COLS={0:0x00, 12:0x0C}
ROWS=[0x00,0x0C,0x18,0x24,0x30,0x3C]   # 0,12,24,36,48,60
MW,MH=32,72
canvas=[[0x1603]*MW for _ in range(MH)]
for cstart,g175 in COLS.items():
    for g176 in ROWS:
        bt=cap(g175,g176,f"c{cstart}_r{g176:02X}")
        for r in range(12):
            for c in range(20):
                R=g176+r; C=cstart+c
                if R<MH and C<MW: canvas[R][C]=bt[r][c]
# measure non-floor extent
rows_used=[R for R in range(MH) if any(canvas[R][C]!=0x1603 for C in range(MW))]
cols_used=[C for C in range(MW) if any(canvas[R][C]!=0x1603 for R in range(MH))]
print("maze non-floor extent: rows", min(rows_used),"-",max(rows_used),"(=",max(rows_used)-min(rows_used)+1,"tiles tall)")
print("                       cols", min(cols_used),"-",max(cols_used),"(=",max(cols_used)-min(cols_used)+1,"tiles wide)")
print(f"screens: {(max(cols_used)-min(cols_used)+1)/20:.1f} wide x {(max(rows_used)-min(rows_used)+1)/12:.1f} tall")
# render
gram=reconstruct_dungeon_gram(); grom=load_grom(); Z=3
img=Image.new('RGB',(MW*8*Z, MH*8*Z)); px=img.load()
for r in range(MH):
    for c in range(MW):
        w=canvas[r][c]; card,ig,fi,bi=decode_fgbg_word(w)
        fg=JZINTV_PALETTE[fi&0xF]; bg=JZINTV_PALETTE[bi&0xF]
        cb=[gram.get(0x3800+card*8+k,0)&0xFF for k in range(8)] if ig else list(grom[card*8:card*8+8])
        x0,y0=c*8*Z,r*8*Z
        for y in range(8):
            b=cb[y] if y<len(cb) else 0
            for x in range(8):
                col=fg if (b>>(7-x))&1 else bg
                for dy in range(Z):
                    for dx in range(Z): px[x0+x*Z+dx,y0+y*Z+dy]=col
img.save('level0_full.png'); print('saved level0_full.png', img.size)
