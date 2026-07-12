// Scrolling maze level — the CORRECT model.
//
// Per the manual ("THE QUEST BEGINS", p.6): "The Prince appears at the center
// of the screen throughout the quest" and characters can wander "out of view".
// A dungeon level is a large maze (32×64 tiles for level 0); the 20×12 screen
// is a window that scrolls to keep the Prince centred. This matches the ROM's
// L_5EE2 background renderer, which windows a 20-wide view (MVII #$0014) out of
// a 32-wide map (ANDI #$001F) at camera position G_0175/G_0176.
//
// Data: assets/level0_maze.json = { w:32, h:64, grid:[row][col] BACKTAB words }.
// (This is the 32×64 grid prior work wrongly dismissed as "title/debug".)

export interface Maze {
  w: number;        // tiles wide (32)
  h: number;        // tiles tall (64)
  grid: number[][]; // [row][col] -> BACKTAB word
}

export const TILE = 8;

// Walkable = floor background colour 11 (olive) — same predicate as the rooms.
export function isWalkableWord(word: number): boolean {
  return ((((word >> 9) & 0xB) | ((word >> 11) & 0x4)) === 11);
}

// Maze tile (BACKTAB word) at a world pixel position. Out of bounds → 0 (wall).
export function mazeTileAt(maze: Maze, x: number, y: number): number {
  const col = Math.floor(x / TILE);
  const row = Math.floor(y / TILE);
  if (col < 0 || row < 0 || col >= maze.w || row >= maze.h) return 0;
  return maze.grid[row]?.[col] ?? 0;
}

export function canWalk(maze: Maze, x: number, y: number): boolean {
  return isWalkableWord(mazeTileAt(maze, x, y));
}

export function pixelWidth(maze: Maze): number { return maze.w * TILE; }
export function pixelHeight(maze: Maze): number { return maze.h * TILE; }

// Clamp a camera origin so the window [0..viewW]×[0..viewH] stays inside the maze.
export function clampCamera(maze: Maze, camX: number, camY: number, viewW: number, viewH: number): { x: number; y: number } {
  const maxX = Math.max(0, pixelWidth(maze) - viewW);
  const maxY = Math.max(0, pixelHeight(maze) - viewH);
  return {
    x: Math.min(Math.max(0, camX), maxX),
    y: Math.min(Math.max(0, camY), maxY),
  };
}
