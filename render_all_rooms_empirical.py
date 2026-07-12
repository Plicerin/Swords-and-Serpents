#!/usr/bin/env python3
"""
Swords & Serpents — Render All 6 Rooms with Empirical BACKTAB Model
Loads cached trace outputs, renders rooms with empirical rendering,
and produces side-by-side comparisons against jzIntv screenshots.
"""
import os
import re
from PIL import Image, ImageDraw, ImageFont

from render_all_rooms import (
    load_grom,
    parse_backtab, extract_backtab_from_output,
    extract_gram_from_output, parse_memory_dump,
    extract_memory_section,
    parse_mobs,
    render_room_image,
    decode_backtab_word,
    PALETTE, PASTEL_PALETTE,
    EMPIRICAL_TRANSPARENT, EMPIRICAL_FG,
)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
TRACES_DIR = os.path.join(PROJECT_DIR, "traces")
COMPARISONS_DIR = os.path.join(PROJECT_DIR, "sprites", "comparisons")

NUM_ROOMS = 6
ZOOM = 4

def load_room_data(room_idx, use_fresh=False):
    """Load and parse a room's trace output."""
    if use_fresh:
        trace_path = os.path.join(TRACES_DIR, "rooms", f"render_room_{room_idx}_out.txt")
    else:
        trace_path = os.path.join(TRACES_DIR, "debug", f"_cmp_room_{room_idx}_out.txt")
    if not os.path.exists(trace_path):
        print(f"  WARNING: No trace file for room {room_idx}")
        return None

    with open(trace_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    backtab_text = extract_backtab_from_output(content)
    if not backtab_text:
        print(f"  WARNING: No BACKTAB data for room {room_idx}")
        return None

    grid = parse_backtab(backtab_text)
    gram_text = extract_gram_from_output(content)
    gram_mem = parse_memory_dump(gram_text, 0x3800, 512) if gram_text else {}
    sysram_text = extract_memory_section(content, 0x0300, 0x0360)
    mobs = parse_mobs(sysram_text) if sysram_text else []

    return {'grid': grid, 'gram_mem': gram_mem, 'mobs': mobs}


def load_jzintv_screenshot(room_idx):
    """Load jzIntv reference screenshot for a room.
    
    Returns the GIF in its native paletted ('P') mode so that getpalette()
    works correctly for pixel-level accuracy comparison. Callers that need
    RGB should use .convert('RGB') on the returned image.
    """
    path = os.path.join(COMPARISONS_DIR, f"room_{room_idx}_jzintv.gif")
    if not os.path.exists(path):
        print(f"  WARNING: No jzIntv screenshot for room {room_idx}")
        return None
    return Image.open(path)


def compute_pixel_accuracy(rendered_1x, jzintv, jz_left=80, jz_top=52,
                          bg_only_1x=None):
    """Compare rendered room (at 1x zoom, 160x96) against jzIntv screenshot pixel-by-pixel.

    If bg_only_1x is provided, also computes MOB-specific accuracy by isolating
    pixels that differ between bg_only_1x and rendered_1x (MOB-affected pixels).

    Returns (overall_accuracy, matches, total, tile_results, mob_stats)
    where mob_stats is None if bg_only_1x is not provided, or a dict:
        {'mob_matches', 'mob_total', 'bg_matches', 'bg_total', 'combined_acc'}
    """
    total = 0
    matches = 0

    jz_pal = jzintv.getpalette()
    if not jz_pal:
        empty_tiles = [[{'total': 0, 'matches': 0} for _ in range(20)] for _ in range(12)]
        return 0, 0, 0, empty_tiles, None
    def jz_rgb(idx):
        if idx is not None and idx * 3 + 2 < len(jz_pal):
            return (jz_pal[idx*3], jz_pal[idx*3+1], jz_pal[idx*3+2])
        return None

    jz_px = jzintv.load()
    rnd_px = rendered_1x.load()
    bg_px = bg_only_1x.load() if bg_only_1x else None

    tile_results = [[{'total': 0, 'matches': 0} for _ in range(20)] for _ in range(12)]

    # MOB accuracy tracking
    mob_total = mob_matches = 0
    bg_total = bg_matches = 0

    for row in range(12):
        for col in range(20):
            tile_total = 0
            tile_matches = 0
            for y in range(8):
                for x in range(8):
                    jx = jz_left + col * 8 + x
                    jy = jz_top + row * 8 + y

                    if jx < jzintv.width and jy < jzintv.height:
                        r_r, r_g, r_b = rnd_px[col * 8 + x, row * 8 + y]
                        j_idx = jz_px[jx, jy]
                        if isinstance(j_idx, int):
                            j_rgb = jz_rgb(j_idx)
                        else:
                            j_rgb = j_idx
                        total += 1
                        tile_total += 1
                        if j_rgb and (r_r, r_g, r_b) == j_rgb:
                            matches += 1
                            tile_matches += 1

                        # Isolate MOB-affected vs background-only pixels
                        if bg_px is not None:
                            bg_rgb = bg_px[col * 8 + x, row * 8 + y]
                            is_mob_pixel = (bg_rgb != (r_r, r_g, r_b))
                            if is_mob_pixel:
                                mob_total += 1
                                if j_rgb and (r_r, r_g, r_b) == j_rgb:
                                    mob_matches += 1
                            else:
                                bg_total += 1
                                if j_rgb and (r_r, r_g, r_b) == j_rgb:
                                    bg_matches += 1

            tile_results[row][col] = {
                'total': tile_total,
                'matches': tile_matches,
                'accuracy': tile_matches / tile_total if tile_total > 0 else 0
            }

    overall = matches / total if total > 0 else 0

    mob_stats = None
    if bg_px is not None:
        mob_stats = {
            'mob_matches': mob_matches,
            'mob_total': mob_total,
            'bg_matches': bg_matches,
            'bg_total': bg_total,
            'combined_acc': matches / total if total > 0 else 0,
        }

    return overall, matches, total, tile_results, mob_stats


def create_comparison_image(room_idx, rendered, jzintv, accuracy, tile_results):
    """Create a side-by-side comparison: jzIntv | Our render | Diff heatmap."""
    room_w = 20 * 8 * ZOOM   # 640px at 4x
    room_h = 12 * 8 * ZOOM   # 384px at 4x

    # Crop jzIntv screenshot to playfield (1x scale: 160x96 region at offset 80,52)
    jz_left, jz_top = 80, 52
    jz_playfield_w = 20 * 8    # 160px
    jz_playfield_h = 12 * 8    # 96px

    # Convert to RGB for visual comparison (preserves palette mapping)
    jz_rgb = jzintv.convert('RGB')
    jz_cropped = jz_rgb.crop((jz_left, jz_top, jz_left + jz_playfield_w, jz_top + jz_playfield_h))
    jz_4x = jz_cropped.resize((room_w, room_h), Image.NEAREST)

    # Diff heatmap
    diff_img = Image.new('RGB', (room_w, room_h), (20, 20, 30))
    diff_px = diff_img.load()
    rnd_px = rendered.load()
    jz_px = jz_4x.load()

    for y in range(room_h):
        for x in range(room_w):
            r = rnd_px[x, y]
            j = jz_px[x, y]
            if r == j:
                diff_px[x, y] = (20, 20, 30)  # match = dark
            else:
                # Show the difference as red tint
                dr = max(0, min(255, r[0] + 60))
                dg = max(0, min(255, r[1] - 40))
                db = max(0, min(255, r[2] - 40))
                diff_px[x, y] = (dr, dg, db)

    # Tile-level accuracy overlay
    tile_size = 8 * ZOOM  # 32px
    accuracy_overlay = Image.new('RGBA', (room_w, room_h), (0, 0, 0, 0))
    acc_px = accuracy_overlay.load()

    for row in range(12):
        for col in range(20):
            acc = tile_results[row][col]['accuracy']
            if acc < 0.3:
                color = (255, 0, 0, 80)  # red overlay for bad tiles
            elif acc < 0.6:
                color = (255, 165, 0, 60)  # orange for mediocre
            elif acc < 0.85:
                color = (255, 255, 0, 40)  # yellow for good
            else:
                color = (0, 255, 0, 20)  # green for great

            tx = col * tile_size
            ty = row * tile_size
            for dy in range(tile_size):
                for dx in range(tile_size):
                    if dy < 2 or dy >= tile_size - 2 or dx < 2 or dx >= tile_size - 2:
                        # Border only
                        px_x = tx + dx
                        px_y = ty + dy
                        if 0 <= px_x < room_w and 0 <= px_y < room_h:
                            existing = acc_px[px_x, px_y]
                            # blend
                            a = color[3]
                            r = (color[0] * a + existing[0] * (255 - a)) // 255
                            g = (color[1] * a + existing[1] * (255 - a)) // 255
                            b = (color[2] * a + existing[2] * (255 - a)) // 255
                            acc_px[px_x, px_y] = (r, g, b, min(255, a + existing[3]))

    # Composite accuracy overlay onto diff
    diff_with_acc = diff_img.copy()
    diff_with_acc.paste(accuracy_overlay, (0, 0), accuracy_overlay)

    # Build composite: [jzIntv] [Our Render] [Diff]
    padding = 16
    label_h = 30
    comp_w = room_w * 3 + padding * 4
    comp_h = room_h + label_h + padding * 2

    comp = Image.new('RGB', (comp_w, comp_h), (30, 30, 40))
    draw = ImageDraw.Draw(comp)

    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except:
        font = ImageFont.load_default()

    # Labels
    draw.text((padding, 6), "jzIntv Screenshot", fill=(200, 200, 200), font=font)
    draw.text((room_w + padding * 3, 6), "Empirical Render", fill=(200, 200, 200), font=font)
    draw.text((room_w * 2 + padding * 5, 6), f"Diff (accuracy: {accuracy*100:.1f}%)", fill=(200, 200, 200), font=font)

    # Paste images
    y0 = label_h + padding
    comp.paste(jz_4x, (padding, y0))
    comp.paste(rendered, (room_w + padding * 3, y0))
    comp.paste(diff_with_acc, (room_w * 2 + padding * 5, y0))

    return comp


def main():
    os.makedirs(COMPARISONS_DIR, exist_ok=True)

    print("=" * 70)
    print("  SWORDS & SERPENTS — EMPIRICAL RENDER (ALL 6 ROOMS)")
    print("=" * 70)
    print(f"  EMPIRICAL_TRANSPARENT: {len(EMPIRICAL_TRANSPARENT)} words")
    print(f"  EMPIRICAL_FG: {len(EMPIRICAL_FG)} words")
    print()

    grom = load_grom()
    print(f"  GROM loaded: {len(grom)} bytes ({len(grom) // 8} cards)")
    print()

    # Collect per-room stats
    all_accuracies = []
    all_mob_accuracies = []
    all_rendered = []

    for room_idx in range(NUM_ROOMS):
        print(f"  Room {room_idx}:")

        data = load_room_data(room_idx, use_fresh=True)
        if data is None:
            continue

        jzintv = load_jzintv_screenshot(room_idx)
        if jzintv is None:
            continue

        # Render room at 1x WITHOUT MOBs (background only)
        rendered_bg_1x = render_room_image(
            data['grid'], data['gram_mem'], grom,
            zoom=1, mobs=[]
        )

        # Render room at 1x WITH MOBs (for combined + MOB accuracy)
        mobs = data.get('mobs', [])
        rendered_mob_1x = render_room_image(
            data['grid'], data['gram_mem'], grom,
            zoom=1, mobs=mobs
        )

        # Compute accuracy: bg-only, MOB, and combined
        accuracy, matches, total, tile_results, mob_stats = compute_pixel_accuracy(
            rendered_mob_1x, jzintv, bg_only_1x=rendered_bg_1x
        )

        # Render room at 4x with MOBs for visual comparison
        rendered_4x = render_room_image(
            data['grid'], data['gram_mem'], grom,
            zoom=ZOOM, mobs=mobs
        )

        # Tile type breakdown
        unique_words = set()
        for row in range(12):
            for col in range(20):
                unique_words.add(data['grid'][row][col])

        print(f"    Pixel accuracy: {accuracy*100:.1f}% ({matches}/{total})")
        if mob_stats:
            mob_acc_pct = (mob_stats['mob_matches'] / mob_stats['mob_total'] * 100
                           if mob_stats['mob_total'] > 0 else 0)
            print(f"      Background only: {mob_stats['bg_matches']}/{mob_stats['bg_total']}"
                  f" = {mob_stats['bg_matches']/mob_stats['bg_total']*100:.1f}%"
                  if mob_stats['bg_total'] > 0 else
                  f"      Background only: 0/0")
            print(f"      MOB pixels only:  {mob_stats['mob_matches']}/{mob_stats['mob_total']}"
                  f" = {mob_acc_pct:.1f}%")
        print(f"    Unique BACKTAB words: {len(unique_words)}")
        print(f"    MOBs: {len(mobs)}")

        # Per-word accuracy stats
        word_acc = {}
        for row in range(12):
            for col in range(20):
                word = data['grid'][row][col]
                ta = tile_results[row][col]
                if word not in word_acc:
                    word_acc[word] = {'total': 0, 'matches': 0}
                word_acc[word]['total'] += ta['total']
                word_acc[word]['matches'] += ta['matches']

        # Show poorly-matched words
        poor_words = [(w, d['matches'] / d['total'] if d['total'] > 0 else 0, d['total'])
                      for w, d in word_acc.items()]
        poor_words.sort(key=lambda x: x[1])
        if poor_words:
            print(f"    Worst-matching words (bottom 5):")
            for w, acc, t in poor_words[:5]:
                card, fg, bg_bits, is_gram, fg_transparent = decode_backtab_word(w)
                in_emp = "EMP" if w in EMPIRICAL_TRANSPARENT or w in EMPIRICAL_FG else "   "
                print(f"      0x{w:04X} card={card:3d} fg={fg} {in_emp} acc={acc*100:.1f}% ({t}px)")

        all_accuracies.append(accuracy)
        if mob_stats:
            mob_acc = (mob_stats['mob_matches'] / mob_stats['mob_total'] * 100
                       if mob_stats['mob_total'] > 0 else 0)
            all_mob_accuracies.append({
                'mob_acc': mob_acc,
                'mob_matches': mob_stats['mob_matches'],
                'mob_total': mob_stats['mob_total'],
                'bg_acc': mob_stats['bg_matches'] / mob_stats['bg_total'] * 100
                          if mob_stats['bg_total'] > 0 else 0,
            })

        # Create and save comparison image
        comp = create_comparison_image(room_idx, rendered_4x, jzintv, accuracy, tile_results)
        comp_path = os.path.join(COMPARISONS_DIR, f"room_{room_idx}_comparison.png")
        comp.save(comp_path)
        print(f"    Comparison saved: {comp_path}")

        # Save individual render
        render_path = os.path.join(COMPARISONS_DIR, f"room_{room_idx}_empirical.png")
        rendered_4x.save(render_path)
        all_rendered.append((room_idx, rendered_4x))

    # Summary
    print()
    print("-" * 70)
    print("  SUMMARY")
    print("-" * 70)
    if all_accuracies:
        avg = sum(all_accuracies) / len(all_accuracies)
        print(f"  Rooms rendered: {len(all_accuracies)}/{NUM_ROOMS}")
        print(f"  Per-room accuracy (combined bg + MOB):")
        for i, acc in enumerate(all_accuracies):
            bar = '#' * int(acc * 40) + '.' * (40 - int(acc * 40))
            mob_info = ""
            if i < len(all_mob_accuracies):
                ma = all_mob_accuracies[i]
                mob_info = (f"  [bg={ma['bg_acc']:.1f}%"
                           f" mob={ma['mob_acc']:.1f}%"
                           f" ({ma['mob_matches']}/{ma['mob_total']}px)]")
            print(f"    Room {i}: {acc*100:.1f}% {bar} {mob_info}")
        print(f"  Average accuracy: {avg*100:.1f}%")
        if all_mob_accuracies:
            avg_bg = sum(m['bg_acc'] for m in all_mob_accuracies) / len(all_mob_accuracies)
            avg_mob = sum(m['mob_acc'] for m in all_mob_accuracies) / len(all_mob_accuracies)
            total_mob_px = sum(m['mob_total'] for m in all_mob_accuracies)
            total_mob_match = sum(m['mob_matches'] for m in all_mob_accuracies)
            print(f"  Avg background accuracy: {avg_bg:.1f}%")
            print(f"  Avg MOB accuracy: {avg_mob:.1f}%"
                  f" ({total_mob_match}/{total_mob_px} px)")
    else:
        print("  No rooms rendered successfully!")

    # Create atlas of all empirical renders
    if all_rendered:
        print()
        print("  Creating atlas...")
        room_w = 20 * 8 * ZOOM   # 640px
        room_h = 12 * 8 * ZOOM   # 384px
        cols = 3
        rows = (len(all_rendered) + cols - 1) // cols
        margin = 16
        label_h = 24

        atlas_w = cols * room_w + (cols + 1) * margin
        atlas_h = rows * (room_h + label_h + margin) + margin
        atlas = Image.new('RGB', (atlas_w, atlas_h), (20, 20, 30))
        draw = ImageDraw.Draw(atlas)
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()

        for i, (room_idx, rendered) in enumerate(all_rendered):
            r = i // cols
            c = i % cols
            x0 = margin + c * (room_w + margin)
            y0 = margin + r * (room_h + label_h + margin)
            draw.text((x0 + 4, y0 + 2), f"Room {room_idx}", fill=(200, 200, 200), font=font)
            atlas.paste(rendered, (x0, y0 + label_h))

        atlas_path = os.path.join(COMPARISONS_DIR, "all_rooms_empirical.png")
        atlas.save(atlas_path)
        print(f"  Atlas saved: {atlas_path}  ({atlas_w}×{atlas_h}px)")

    print()
    print("=" * 70)
    print("  DONE")
    print("=" * 70)


if __name__ == '__main__':
    main()
