import json
from PIL import Image
from render_all_rooms import render_room_image, load_grom, reconstruct_dungeon_gram, PALETTE, PASTEL_PALETTE

def render_room_json_to_image(json_path, output_path):
    # 1. Load raw data
    with open(json_path, 'r') as f:
        data = json.load(f)
    grid = data['grid']
    
    # 2. Load Game Assets
    grom = load_grom()
    # Reconstruct the dungeon GRAM (this ensures walls/pillars have the correct card bitmaps)
    # Based on the script, RLE base is 0x61E7
    gram_mem = reconstruct_dungeon_gram(rle_addr=0x61E7)
    
    # 3. Prepare BackTab Grid
    # The JSON grid is 32x64. The render_room_image expects a 20x12 grid (BackTab size).
    # We need to map our 32x64 collision grid to the 20x12 BackTab space.
    # Assuming 1 collision cell = 1 BackTab tile (approx)
    # We'll take the top-left 20x12 area for this test.
    backtab_grid = []
    for r in range(12):
        row_data = []
        for c in range(20):
            tile_id = grid[r][c]
            # If tile is 0 (floor), word is 0. 
            # If tile is 1 (wall), we need a word that decodes to card 1, FG color 3 (tan), BG bit 0.
            # Card 1 = (1 << 3) = 0x08. FG 3 = 0x3. Is_gram = 0. 
            # Total word = 0x0B
            if tile_id == 1:
                row_data.append(0x0B)
            else:
                row_data.append(0x00)
        backtab_grid.append(row_data)

    # 4. Render
    # We pass the reconstructed GRAM so that walls (card 1) use the correct bitmap.
    # Use a zoom of 4 to match the README's standard.
    img = render_room_image(
        backtab_grid, 
        gram_mem, 
        grom, 
        color_stack=[PASTEL_PALETTE[3]] * 4, 
        zoom=4,
        use_fgbg=False # Dungeon uses FG/BG, but we'll stick to CS for now to see the result
    )
    
    # Save result
    img.save(output_path)
    print(f"Successfully rendered room from JSON to {output_path}")

if __name__ == "__main__":
    render_room_json_to_image(
        r"C:\Users\vrock\Documents\Swords and Serpents\level0_collision.json",
        r"C:\Users\vrock\Documents\Swords and Serpents\render_final_test.png"
    )
