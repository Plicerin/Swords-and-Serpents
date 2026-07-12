"""
Swords & Serpents — Sequential Integer Versioning Utility

Provides next_versioned_path() so every script run writes a uniquely-numbered
output file instead of clobbering the previous one.  Scan an existing
output directory, find the highest integer suffix on files matching the
given stem, and return the next integer in the sequence.

Usage:
    from versioning import next_versioned_path
    out = next_versioned_path("sprites/rooms", "dungeon_room_0", ".png")
    # → Path("sprites/rooms/dungeon_room_0_0012.png")  (or _0001 if none exist)
"""
import os
import re
from pathlib import Path


def next_versioned_path(directory: str, stem: str, suffix: str) -> Path:
    """Return the next versioned file path in a directory.

    Args:
        directory: Output directory (created if missing).
        stem: Base filename stem, e.g. "dungeon_room_0".
        suffix: File extension including dot, e.g. ".png".

    Returns:
        Path like ``directory/stem_NNNN.suffix`` where NNNN is the next
        available 4-digit integer (0001, 0002, …).
    """
    out_dir = Path(directory)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Pattern: stem_NNNN.suffix
    pattern = re.compile(re.escape(stem) + r"_(\d{4})" + re.escape(suffix) + r"$")

    highest = 0
    if out_dir.exists():
        for entry in os.listdir(out_dir):
            m = pattern.match(entry)
            if m:
                highest = max(highest, int(m.group(1)))

    next_num = highest + 1
    return out_dir / f"{stem}_{next_num:04d}{suffix}"


def latest_versioned_path(directory: str, stem: str, suffix: str) -> Path | None:
    """Return the *latest* versioned file path, or None if none exist.

    Useful when a downstream script needs to consume the most recent artifact.
    """
    out_dir = Path(directory)
    if not out_dir.exists():
        return None

    pattern = re.compile(re.escape(stem) + r"_(\d{4})" + re.escape(suffix) + r"$")
    highest = 0
    for entry in os.listdir(out_dir):
        m = pattern.match(entry)
        if m:
            highest = max(highest, int(m.group(1)))

    if highest == 0:
        return None
    return out_dir / f"{stem}_{highest:04d}{suffix}"


def list_versioned_paths(directory: str, stem: str, suffix: str) -> list[Path]:
    """Return all versioned paths for a stem, sorted by version number."""
    out_dir = Path(directory)
    if not out_dir.exists():
        return []

    pattern = re.compile(re.escape(stem) + r"_(\d{4})" + re.escape(suffix) + r"$")
    results = []
    for entry in os.listdir(out_dir):
        m = pattern.match(entry)
        if m:
            results.append((int(m.group(1)), out_dir / entry))

    results.sort(key=lambda x: x[0])
    return [p for _, p in results]
