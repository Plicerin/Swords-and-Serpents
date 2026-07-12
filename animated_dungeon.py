#!/usr/bin/env python3
"""
Render all 6 dungeon rooms and create an animated GIF that simulates
walking through the dungeon with cross-fade transitions between rooms.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOMS_DIR = os.path.join(PROJECT_DIR, "sprites", "rooms")
OUT_PATH = os.path.join(PROJECT_DIR, "sprites", "rooms", "dungeon_walk.gif")

# Timing (in milliseconds)
HOLD_MS = 1000       # how long each room is displayed
FADE_MS = 600        # duration of cross-fade transition
FADE_STEPS = 6       # number of intermediate blend frames
FRAME_MS = FADE_MS // FADE_STEPS  # each blend frame duration

# Label overlay
LABEL_H = 48
BORDER = 12

ROOM_NAMES = {
    0: "Room 0 -- Entrance",
    1: "Room 1 -- Empty Passage",
    2: "Room 2 -- Guard Post",
    3: "Room 3 -- Guard Post",
    4: "Room 4 -- Boss Chamber",
    5: "Room 5 -- Empty Passage",
}

MOB_SUMMARIES = {
    0: "2 MOBs -- player + enemy",
    1: "Empty room",
    2: "3 MOBs -- guards",
    3: "2 MOBs -- guards",
    4: "1 MOB -- boss?",
    5: "Empty room",
}


def load_fonts():
    """Try to load a nice font, fall back to default."""
    font_paths = [
        "C:\\Windows\\Fonts\\segoeui.ttf",
        "C:\\Windows\\Fonts\\seguiemj.ttf",
        "C:\\Windows\\Fonts\\cour.ttf",
        "C:\\Windows\\Fonts\\consola.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                title_font = ImageFont.truetype(fp, 28)
                sub_font = ImageFont.truetype(fp, 17)
                return title_font, sub_font
            except Exception:
                continue
    return None, None


def add_label_overlay(img, room_idx, title_font, sub_font):
    """Draw a dark label bar at the bottom of the room image."""
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Semi-transparent dark bar at bottom
    bar_top = h - LABEL_H
    draw.rectangle([(0, bar_top), (w - 1, h - 1)], fill=(7, 8, 12, 180))

    # Room name
    name = ROOM_NAMES.get(room_idx, f"Room {room_idx}")
    mob_text = MOB_SUMMARIES.get(room_idx, "")

    GOLD = (242, 215, 164)
    LAVENDER = (177, 160, 232)

    if title_font:
        draw.text((BORDER + 4, bar_top + 3), name, fill=GOLD, font=title_font)
        draw.text((BORDER + 4, bar_top + 29), mob_text, fill=LAVENDER, font=sub_font)
    else:
        draw.text((BORDER + 4, bar_top + 6), name, fill=GOLD)
        draw.text((BORDER + 4, bar_top + 28), mob_text, fill=LAVENDER)

    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def blend_frames(img_a, img_b, t):
    """
    Cross-fade blend between two images using PIL's native C blend.
    t=0.0 → fully img_a, t=1.0 → fully img_b.
    """
    return Image.blend(img_a, img_b, t)


def build_gif():
    """Load all room PNGs, build labeled frames, and save animated GIF."""
    # Load room images
    rooms = []
    for i in range(6):
        path = os.path.join(ROOMS_DIR, f"room_{i}.png")
        if not os.path.exists(path):
            # Render it first
            from render_room import render_room
            render_room(i, silent=True)
        img = Image.open(path).convert("RGB")
        rooms.append(img)

    # Ensure all same size
    w, h = rooms[0].size
    for i, img in enumerate(rooms):
        if img.size != (w, h):
            rooms[i] = img.resize((w, h))

    title_font, sub_font = load_fonts()

    # Build frame sequence
    frames = []
    durations = []

    for i in range(6):
        # Labeled version of current room
        labeled = add_label_overlay(rooms[i].copy(), i, title_font, sub_font)

        # Hold frame for this room
        frames.append(labeled)
        durations.append(HOLD_MS)

        # Cross-fade to next room (room 5 fades to room 0 for seamless loop)
        next_i = (i + 1) % 6
        next_labeled = add_label_overlay(rooms[next_i], next_i, title_font, sub_font)

        for step in range(1, FADE_STEPS):
            t = step / FADE_STEPS
            blended = blend_frames(labeled, next_labeled, t)
            frames.append(blended)
            durations.append(FRAME_MS)

    # Convert durations to milliseconds for PIL (it uses ms for duration in newer
    # versions, but we'll set per-frame duration via the save kwargs)
    # Actually, PIL GIF save uses a global duration. We need frame-level durations.
    # We'll use the append_images approach with per-frame durations.
    frames[0].save(
        OUT_PATH,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,          # loop forever
        optimize=False,  # keep quality
        disposal=1,      # don't dispose — all frames are full-size, just overlay
    )

    # Report
    total_frames = len(frames)
    total_sec = sum(durations) / 1000.0
    file_size = os.path.getsize(OUT_PATH)

    print(f"Saved: {OUT_PATH}")
    print(f"  Size: {file_size:,} bytes")
    print(f"  Frames: {total_frames} ({6} holds + {6 * FADE_STEPS} transitions)")
    print(f"  Duration: {total_sec:.1f}s per loop")
    print(f"  Resolution: {w}x{h}")
    print(f"  Rooms: 0 + 1 + 2 + 3 + 4 + 5")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    build_gif()
