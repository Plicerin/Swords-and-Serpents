"""
Swords & Serpents — Shared Room Renderer Helpers

Provides pixel-level artifact filtering for jzIntv emulator screenshots.
jzIntv overlays UI elements (blue highlight, white text, black outlines)
in the top tile rows that are not part of the actual game graphics.
This module detects and replaces those artifacts with colors computed
from the BACKTAB card bitmap.
"""
from render_all_rooms import PASTEL_PALETTE

BLUE = (20, 56, 247)    # jzIntv emulator overlay / selection highlight
BLACK = (0, 0, 0)       # emulator copyright symbol / outline artifacts
PASTEL_TAN = PASTEL_PALETTE[3]  # default Color Stack background

# Tile rows where jzIntv overlays emulator UI artifacts.
# Rows 0–5 (the upper half of the 12-row playfield) contain blue selection
# highlights, white status text, and black copyright/outline graphics
# that are not part of the actual game.
ARTIFACT_ROW_LIMIT = 6


def is_whiteish(c, thresh=230):
    """Check if a color is white-ish (all channels above threshold)."""
    return c[0] > thresh and c[1] > thresh and c[2] > thresh


def resolve_artifact_pixel(src_color, expected, ty):
    """Resolve a pixel that may be a jzIntv emulator artifact.

    In the top ARTIFACT_ROW_LIMIT tile rows (ty < ARTIFACT_ROW_LIMIT), jzIntv overlays emulator UI elements
    (blue highlight, white text, black outlines / copyright symbol) that
    are not part of the actual game graphics.  This function detects those
    artifacts and substitutes the color computed from the card bitmap.

    Args:
        src_color: The RGB color from the jzIntv reference screenshot.
        expected:  The RGB color computed from the BACKTAB card bitmap.
        ty:        Tile row index (0-based).

    Returns:
        (resolved_color, artifact_type) where artifact_type is one of:
        "blue", "white", "black", or None if the pixel is not an artifact.
    """
    if src_color == BLUE:
        # Blue emulator overlay pixels (highlight, selection box).
        # In the top rows, avoid replacing blue with white — that's the
        # emulator overlay background showing through. Use background color
        # instead to blend with the room.
        if ty < ARTIFACT_ROW_LIMIT and is_whiteish(expected):
            return PASTEL_TAN, "blue"
        return expected, "blue"

    if is_whiteish(src_color) and ty < ARTIFACT_ROW_LIMIT:
        # White emulator text / status-bar artifacts in the top rows.
        # Legitimate white game graphics (e.g. warrior sprite) appear
        # in rows 6 and below.
        if not is_whiteish(expected):
            return expected, "white"
        # Expected is also white — replace with background color so we
        # don't leave a white patch where the emulator text was.
        return PASTEL_TAN, "white"

    if src_color == BLACK and ty < ARTIFACT_ROW_LIMIT and expected != BLACK:
        # Black emulator artifacts (copyright symbol outline, status-bar
        # borders) in the top rows.  Legitimate black game pixels only
        # appear where the card expects black.
        if is_whiteish(expected):
            return PASTEL_TAN, "black"
        return expected, "black"

    return src_color, None
