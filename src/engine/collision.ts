// Collision detection for Swords & Serpents.
//
// Walkability is determined by the BACKTAB tile's background colour.  In the
// dungeon the ROM uses bg=11 (olive/brown, STIC colour index 11) exclusively
// for passable floor tiles, and bg=0/3 for walls and obstacles.  This matches
// the ROM's tile classification scheme observed across all captured rooms
// (rooms 0–5).  The bg field is extracted from BACKTAB bits 9, 10, 12, 13.

// GRAM card indices for special tile types
export const TILE_FLOOR_GROM = 0x00;  // GROM card 0 – standard floor
export const TILE_STAIR_GRAM = 0x09;  // GRAM card 9 – stair trigger (code 0x10 → L_6717)

// GRAM cards that are objects (not walkable without interaction)
const OBJECT_GRAM = new Set([
  0x5B, 0x5C, 0x5D, 0x5E,  // Chest, key, potion, scroll
  0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2A, 0x2B, 0x2C, 0x2D, 0x2E, 0x2F, 0x30, 0x31, 0x32, 0x33,  // Monster sprites
]);

// Decode a BACKTAB word to get tile properties
export function decodeTile(word: number): {
  card: number;
  isGram: boolean;
  fg: number;
  bg: number;
} {
  const gr = word & 0x9F8;
  return {
    card: (gr >> 3) & 0x3F,
    isGram: (gr & 0x800) !== 0,
    fg: word & 0x7,
    bg: ((word >> 9) & 0xB) | ((word >> 11) & 0x4),
  };
}

// Check if a tile is walkable.
//
// ROM-faithful: the dungeon uses bg=11 (olive, STIC index 11) for all
// passable floor tiles and bg=0/3 for walls/obstacles.  bg is packed into the
// BACKTAB word across bits 9, 10, 12, 13 per the STIC FG/BG colour encoding.
// This predicate has been validated against all unique tile words in the
// captured 32×64 multi-room map (rooms 0–5).
export function isWalkable(word: number): boolean {
  const bg = ((word >> 9) & 0xB) | ((word >> 11) & 0x4);
  return bg === 11;
}

// Check if a tile is an object that can be picked up
export function isObject(word: number): boolean {
  const { card, isGram } = decodeTile(word);
  if (!isGram) return false;
  return OBJECT_GRAM.has(card);
}

// Check if a tile is a stair (for level transitions).
// Stair tiles use GRAM card 8 (word 0x1E40 in the dungeon).
export function isStair(word: number): boolean {
  const { card, isGram } = decodeTile(word);
  return isGram && card === TILE_STAIR_GRAM;
}

// Convert a player pixel position to its BACKTAB index.
//
// Faithful port of L_6054 ($6054): the player's reference tile is computed from
// (X-8, Y-8), each clamped to ≥0, then >>3, giving idx = col + row*roomCols.
// X/Y are in STIC coordinates where the visible playfield starts at x=8, so the
// -8 maps pixel space to tile space (e.g. the start X=0x58=88 → col 10, the
// center of a 20-wide room). The game samples this single reference tile.
export function pixelToBacktabIndex(x: number, y: number, roomCols: number = 20): number {
  const col = Math.max(0, (x & 0xFF) - 8) >> 3;
  const row = Math.max(0, (y & 0x7F) - 8) >> 3;
  return row * roomCols + col;
}

// Get the BACKTAB word at a given pixel position (20×12 room).
export function getTileAt(backtab: number[], x: number, y: number, roomCols: number = 20): number {
  const index = pixelToBacktabIndex(x, y, roomCols);
  if (index < 0 || index >= backtab.length) return 0;
  return backtab[index] ?? 0;
}

// Check if the player can move to a position. Samples the tile at (x,y) via
// pixelToBacktabIndex (L_6054 port) and tests it with isWalkable.
export function canMoveTo(backtab: number[], x: number, y: number, roomCols: number = 20): boolean {
  return isWalkable(getTileAt(backtab, x, y, roomCols));
}

// GRAM card 3 (word 0x081B) is the south stair trigger in the ROM's L_65FC scan.
// The ROM checks tile+18 (not the player's tile directly) for card 3 — the card
// is placed as a wall adjacent to the stairway, 18 backtab indices ahead of the
// player's floor tile. Card 3 has bg=0 so the player can't stand on it directly.
const SOUTH_STAIR_CARD = 3;

// Check for room boundary transitions (port of $6679 / L_65FC logic).
//
// North zone (Y < 0x10, STIC rows 0–1): fires whenever the player is on any
// walkable tile (bg=11). Rooms without a specific arch card (e.g. room 3) have
// plain floor in rows 0–1, and the ROM's arch-zoom (cards 1/2/10, code < $10)
// still produces a level+1 transition — the bg=11 guard is the right predicate.
//
// South zone (Y ≥ 0x40, STIC rows 7+): fires only when backtab[playerIdx+18]
// is GRAM card 3 (code $20, south stair trigger). This prevents false triggers
// when the player is in the south area of a newly-entered room — the decorative
// arch tiles in that zone (cards 1/2) don't generate a south transition.
export function checkBoundary(
  backtab: number[],
  x: number,
  y: number,
  roomCols: number = 20
): { direction: 'north' | 'south' | null; triggerTile: number } {
  const yCoord = y & 0x7F;
  const xCoord = x & 0xFF;

  if (yCoord < 0x10) {
    const tile = getTileAt(backtab, xCoord, yCoord, roomCols);
    return { direction: isWalkable(tile) ? 'north' : null, triggerTile: tile };
  }

  if (yCoord >= 0x40) {
    const playerIdx = pixelToBacktabIndex(xCoord, yCoord, roomCols);
    const aheadIdx = playerIdx + 18;
    if (aheadIdx < backtab.length) {
      const aheadTile = backtab[aheadIdx] ?? 0;
      const { card, isGram } = decodeTile(aheadTile);
      if (isGram && card === SOUTH_STAIR_CARD) {
        const playerTile = getTileAt(backtab, xCoord, yCoord, roomCols);
        return { direction: 'south', triggerTile: playerTile };
      }
    }
  }

  return { direction: null, triggerTile: 0 };
}
