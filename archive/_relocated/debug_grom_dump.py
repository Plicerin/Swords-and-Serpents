from render_all_rooms import load_grom
import os

grom = load_grom()
for i, byte in enumerate(grom):
    if byte != 0:
        prefix = " [OVERLAY-CARD]" if 0x90 <= byte <= 0x9F else ""
        print(f"Index {i:03d}: {byte:02X}{prefix}")

