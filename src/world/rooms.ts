// Room/world management for Swords & Serpents.
//
// Per DUNGEON_MAP_DOCUMENTATION.md, the dungeon is a *linear vertical* sequence:
// Room 0 -> 1 -> 2 -> ... -> N-1. The captured BACKTAB layouts are stacked,
// with the level index G_019C selecting which layout to render. Walking north
// (Y < 16) advances to the next level; walking south (Y >= 64) descends to the
// previous level. There are no east/west room transitions — side openings in
// the mazes are visual only.

// Room connection parameters (linear vertical dungeon).
export interface RoomParams {
  north: number | null;  // Level to go to when moving north (null at the top)
  south: number | null;  // Level to go to when moving south (null at the bottom)
}

// Room data (loaded from rooms.json at runtime)
let cachedRooms: number[][] | null = null;

// Load room data from JSON
export function setRoomsData(rooms: number[][]): void {
  cachedRooms = rooms;
}

// Get room BACKTAB data
export function getRoomBacktab(level: number): number[] | null {
  if (!cachedRooms) return null;
  if (level < 0 || level >= cachedRooms.length) {
    return null;
  }
  return cachedRooms[level];
}

// Total number of captured/loaded rooms
export function getRoomCount(): number {
  return cachedRooms?.length ?? 0;
}

// Compute linear connections for a given level.
//   north = level+1, null at the top
//   south = level-1, null at the bottom
export function getRoomConnections(level: number): RoomParams | null {
  const total = getRoomCount();
  if (total === 0) return null;
  if (level < 0 || level >= total) return null;

  return {
    north: level < total - 1 ? level + 1 : null,
    south: level > 0 ? level - 1 : null,
  };
}

// Handle stair descent.
// Based on L_6725 disassembly: G_019C += 1; re-render; G_02F4 += 8.
export function handleStairDescent(
  currentLevel: number,
  currentDataPtr: number
): { newLevel: number; newDataPtr: number } {
  return { newLevel: currentLevel + 1, newDataPtr: currentDataPtr + 8 };
}

// Check if level transition is valid
export function isValidLevel(level: number): boolean {
  return level >= 0 && level < 14; // 0-13 are valid levels
}

// Get level name (for debugging)
export function getLevelName(level: number): string {
  if (level === 0) return 'Entrance Hall';
  if (level === 13) return "Dragon's Lair";
  return `Dungeon Level ${level}`;
}
