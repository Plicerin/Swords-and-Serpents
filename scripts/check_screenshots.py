"""
Check existing jzIntv screenshots and understand capture infrastructure.
"""
import os
from PIL import Image

# 1. Check existing screenshots
print("=== Existing Screenshots ===")
for f in ['jzintv-20200712-win32-sdl2/bin/shot0001.gif', 
          'jzintv-20200712-win32-sdl2/bin/shot0002.gif']:
    if os.path.exists(f):
        img = Image.open(f)
        px = img.load()
        colors = {}
        for y in range(img.height):
            for x in range(img.width):
                c = px[x,y]
                colors[c] = colors.get(c, 0) + 1
        sorted_colors = sorted(colors.items(), key=lambda x: -x[1])
        print(f'{f}:')
        print(f'  Size: {img.size[0]}x{img.size[1]}, Mode: {img.mode}, {len(colors)} colors')
        for c, n in sorted_colors[:10]:
            print(f'  {c}: {n} px')
        print()
    else:
        print(f'{f}: MISSING')

# 2. Check trace capture infrastructure
print("=== Capture Scripts ===")
for pattern in ['capture', 'trace', 'render_room']:
    for root, dirs, files in os.walk('.'):
        for fn in files:
            if pattern in fn.lower() and fn.endswith(('.py', '.sh', '.txt', '.bat')):
                path = os.path.join(root, fn)
                size = os.path.getsize(path)
                print(f'  {path} ({size} bytes)')

print()
print("=== Debugger Scripts ===")
for root, dirs, files in os.walk('traces'):
    for fn in files:
        if fn.endswith('.txt'):
            path = os.path.join(root, fn)
            # Read first few lines
            try:
                with open(path, 'r') as f:
                    first_lines = [f.readline().strip() for _ in range(5)]
                if any('p ' in l or 'r ' in l or 'm ' in l or 'b ' in l or 'vs' in l for l in first_lines):
                    print(f'  {path}:')
                    for l in first_lines:
                        if l.strip():
                            print(f'    {l}')
                    print()
            except:
                pass

# 3. Check render_all_rooms.py for capture info
print("=== render_all_rooms.py capture section ===")
with open('render_all_rooms.py', 'r') as f:
    content = f.read()

# Find the section that launches jzIntv
for keyword in ['jzintv', 'subprocess', 'Popen', 'debugger', '--script', '-d']:
    idx = content.lower().find(keyword)
    if idx >= 0:
        start = max(0, idx - 100)
        end = min(len(content), idx + 300)
        print(f'  ...found "{keyword}" at offset {idx}:')
        print(f'  {content[start:end]}')
        print()
