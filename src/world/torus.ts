// Toroidal level world — matches the ROM background renderer:
//
//   L_5EE2  masks the camera column `ANDI #$001F` (mod 32) and, when the
//           20-wide window crosses column 31 mid-row, rewinds the source row
//           and continues from column 0 (L_5F0C → CLRR R1).
//   L_5EAE  advances the row counter `INCR R0; ANDI #$003F` (mod 64).
//   L_5E8D  keeps the camera position masked `ANDI #$007F` (G_0175).
//
// So each dungeon level is a 32×64 torus that scrolls infinitely in both
// axes, with the Prince fixed at the centre of the screen (manual p.6:
// "The Prince appears at the center of the screen throughout the quest").

import { Maze, isWalkableWord } from './maze';
import { renderGridToCanvas } from '../platform/stic';

export const TILE = 8;

export function wrap(v: number, size: number): number {
  return ((v % size) + size) % size;
}

/** Shortest signed delta from `from` to `to` on a ring of `size`. */
export function wrapDelta(from: number, to: number, size: number): number {
  let d = to - from;
  if (d > size / 2) d -= size;
  if (d < -size / 2) d += size;
  return d;
}

export class LevelWorld {
  maze: Maze;
  canvas: HTMLCanvasElement | null = null;

  constructor(maze: Maze) {
    this.maze = maze;
  }

  build(gram: Uint8Array, grom: Uint8Array): void {
    this.canvas = renderGridToCanvas(this.maze.grid, gram, grom);
  }

  get pixelWidth(): number { return this.maze.w * TILE; }
  get pixelHeight(): number { return this.maze.h * TILE; }

  canWalk(x: number, y: number): boolean {
    const col = wrap(Math.floor(x / TILE), this.maze.w);
    const row = wrap(Math.floor(y / TILE), this.maze.h);
    return isWalkableWord(this.maze.grid[row]?.[col] ?? 0);
  }

  tileAt(x: number, y: number): number {
    const col = wrap(Math.floor(x / TILE), this.maze.w);
    const row = wrap(Math.floor(y / TILE), this.maze.h);
    return this.maze.grid[row]?.[col] ?? 0;
  }
}
