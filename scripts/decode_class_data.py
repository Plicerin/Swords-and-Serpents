import struct

with open('Swords and Serpents.bin', 'rb') as f:
    # Class data for warrior (CPU address 5B28)
    class_ptr = 0x5B28
    for i in range(10):
        w = struct.unpack('<H', f.read(2))[0]
        print(f"  {class_ptr + i*2:04X}: {w:04X}")

    # Destination pointer table at 5555 (ROM)
    f.seek(0x0555)  # File offset for CPU address 5555
    print("\nDestination pointer table (ROM 5555):")
    for i in range(4):
        w = struct.unpack('<H', f.read(2))[0]
        print(f"  {0x5555 + i*2:04X}: {w:04X}")
