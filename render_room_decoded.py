import json
from PIL import Image

# Configuration based on reverse engineering findings
PALETTE = [
    (0,0,0), (0,0,255), (200,40,40), (200,170,50),
    (0,128,0), (0,255,0), (255,255,0), (255,255,255),
    (128,128,128), (0,255,255), (255,150,0), (150,130,100),
    (255,100,150), (100,200,255), (200,200,0), (150,60,200)
]

def render_room_from_json(json_path, output_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    grid = data['grid']
    rows = len(grid)
    cols = len(grid[0])
    
    # The manual says 4:3 aspect correction (x1.25 vertical stretch)
    # We'll render a standard 640x480 buffer as suggested in README
    img = Image.new('RGB', (640, 480), (0, 0, 0))
    
    # Mapping tile IDs to (CardID, FG_Color_Idx, BG_Color_Idx)
    # Based on 'handover.md' and 'render_room.py' context
    tile_map = {
        0: (None, 0, 0),           # Floor
        1: (4, 3, 0),               # Wall (Tan)
        24: (0, 6, 0),              # Special Pillar
        # Add other tiles as identified in handover
    }

    for r in range(rows):
        for c in range(cols):
            tile_id = grid[r][c]
            if tile_id in tile_map and tile_map[tile_id][0] is not None:
                card_id, fg_idx, bg_idx = tile_map[tile_id]
                
                # Coordinate Transformation (Decoded from disasm_new.asm L_520A)
                # Grid (r, c) -> Pixel (c*8, r*8)
                px = c * 8
                py = r * 8
                
                # In a real implementation, we would fetch the 8x8 card here.
                # For now, we'll draw a placeholder colored block.
                fg_color = PALETTE[fg_idx]
                bg_color = PALETTE[bg_idx]
                
                # Draw a 8x8 block (simulating the STIC tile)
                # Since we don't have the GROM card logic fully implemented yet,
                # we draw a solid color block.
                block = Image.new('RGB', (8, 8), fg_color)
                img.paste(block, (px, py))

    img.save(output_path)
    print(f"Rendered room to {output_path}")

if __name__ == "__main__":
    render_room_from_json(
        r"C:\Users\vrock\Documents\Swords and Serpents\level0_collision.json",
        r"C:\Users\vrock\Documents\Swords and Serpents\render_test_decoded.png"
    )
