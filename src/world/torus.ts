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

import { Maze, isWalkableWord, gramCard } from './maze';
import { renderGridToCanvas, paintTile } from '../platform/stic';

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
  maze: Maze;                 // the LIVE tile words — what the ROM's BACKTAB holds
  base: number[][];           // the map as captured (objects baked in)
  canvas: HTMLCanvasElement | null = null;
  private gram: Uint8Array | null = null;
  private grom: Uint8Array | null = null;
  // GRAM card bitmap overrides (animated cards — the chomping doors rewrite
  // cards 1 and 2 in place, see docs/HANDOVER.md finding #9).
  private cardOverride = new Map<number, ArrayLike<number>>();
  // Tiles whose live word differs from what a redraw would produce. The ROM
  // only ever regenerates BACKTAB from map + object data when a column/row
  // scrolls in (or the level is redrawn), so these persist while on screen.
  stale = new Set<number>();

  constructor(maze: Maze) {
    this.maze = maze;
    this.base = maze.grid.map(r => r.slice());
  }

  build(gram: Uint8Array, grom: Uint8Array): void {
    this.gram = gram;
    this.grom = grom;
    this.canvas = renderGridToCanvas(this.maze.grid, gram, grom);
  }

  key(col: number, row: number): number { return row * this.maze.w + col; }

  /** Write one live tile word (a BACKTAB write) and repaint it. */
  setWord(col: number, row: number, word: number): void {
    col = wrap(col, this.maze.w);
    row = wrap(row, this.maze.h);
    this.maze.grid[row][col] = word;
    this.repaint(col, row);
  }

  repaint(col: number, row: number): void {
    if (!this.canvas || !this.gram || !this.grom) return;
    const word = this.maze.grid[row][col];
    paintTile(this.canvas, col, row, word, this.gram, this.grom, this.cardOverride.get(gramCard(word)));
  }

  /** Replace a GRAM card's bitmap and repaint every tile that uses it. */
  setCardBitmap(card: number, bytes: ArrayLike<number>): void {
    this.cardOverride.set(card, bytes);
    for (let r = 0; r < this.maze.h; r++) {
      for (let c = 0; c < this.maze.w; c++) {
        if (gramCard(this.maze.grid[r][c]) === card) this.repaint(c, r);
      }
    }
  }

  cardBitmap(card: number): ArrayLike<number> | undefined {
    const o = this.cardOverride.get(card);
    if (o) return o;
    return this.gram?.subarray(card * 8, card * 8 + 8);
  }

  /** Positions of every tile using a given GRAM card (live words). */
  tilesWithCard(card: number): { col: number; row: number }[] {
    const out: { col: number; row: number }[] = [];
    for (let r = 0; r < this.maze.h; r++) {
      for (let c = 0; c < this.maze.w; c++) {
        if (gramCard(this.maze.grid[r][c]) === card) out.push({ col: c, row: r });
      }
    }
    return out;
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
