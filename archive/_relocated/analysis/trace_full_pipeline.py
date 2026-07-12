#!/usr/bin/env python3
"""Trace the complete L_5E48 -> L_5EC7 pipeline using jzIntv debugger."""
import os, subprocess

# Main script: break at $5E68, dump pointers, also break at L_5EC7 
script3 = '''
b 5E68
r 12000000
s
; Now R2 has the tile data pointer - dump known pointer destinations
; Table entries (SDBD pairs):
;   entry[0,1]: $98,$11 -> $1198
;   entry[2,3]: $6D,$86 -> $6D86
;   entry[4,5]: $6D,$13 -> $136D
;   entry[6,7]: $9E,$6E -> $6E9E
;   entry[8,9]: $6E,$06 -> $066E
;   entry[10,11]: $A6,$AA -> $AAA6
;   entry[12,13]: $02,$80 -> $8002
;   entry[14,15]: $40,$2A -> $2A40
m 6D86 32
m 136D 32
m 6E9E 32
m 066E 32
m AAA6 32
m 8002 32
m 2A40 32
q
'''

with open('traces/rooms/dump_pointers.txt', 'w') as f:
    f.write(script3)

env = os.environ.copy()
env['SDL_VIDEODRIVER'] = 'dummy'
env['SDL_AUDIODRIVER'] = 'dummy'

print("=== Running pointer destination dump ===")
cmd = [
    'jzintv-20200712-win32-sdl2/bin/jzintv.exe', '-d',
    '--script=traces/rooms/dump_pointers.txt',
    '-e', 'exec.bin', '-g', 'grom.bin',
    'Swords and Serpents.bin'
]

with open('traces/rooms/dump_pointers_out.txt', 'w', errors='replace') as f:
    proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, env=env)
    try:
        proc.wait(timeout=45)
    except subprocess.TimeoutExpired:
        proc.kill()
        print('Timed out')

print("\n=== jzIntv pointer destination dump ===")
with open('traces/rooms/dump_pointers_out.txt', 'r', errors='replace') as f:
    for line in f:
        s = line.rstrip()
        if 'm ' in s or (s and (s[0].isdigit() or s[0] in 'ABCDEF')):
            print(s)

print("\nDone.")
