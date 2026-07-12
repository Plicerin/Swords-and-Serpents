/**
 * STIC (Standard Television Interface Chip) renderer for Intellivision.
 *
 * Port of render_all_rooms.py decode_fgbg_word + render_room_fgbg.
 * This is the ONLY correct renderer - see docs/PORT_RUNBOOK.md Section 0.
 *
 * The playfield IS the screen: 20×12 tiles = 160×96 px, no scrolling/camera
 * (the original game hard-cuts between rooms). An earlier 32×64 scrolling
 * experiment was removed — `level0_backtab.json`'s 32×64 grid is the
 * title/debug BACKTAB, not the in-game dungeon room.
 */

/** 16-color Intellivision palette (jzIntv values) */
export const PALETTE: readonly [number, number, number][] = [
  [0x00, 0x00, 0x00],  // 0  black
  [0x00, 0x2D, 0xFF],  // 1  blue
  [0xFF, 0x3D, 0x10],  // 2  red
  [0xC9, 0xCF, 0xAB],  // 3  tan
  [0x38, 0x6B, 0x3F],  // 4  dark green
  [0x00, 0xA7, 0x56],  // 5  green
  [0xFA, 0xEA, 0x50],  // 6  yellow
  [0xFF, 0xFC, 0xFF],  // 7  white
  [0xBD, 0xAC, 0xC8],  // 8  grey
  [0x24, 0xB8, 0xFF],  // 9  cyan
  [0xFF, 0xB4, 0x1F],  // 10 orange
  [0x54, 0x6E, 0x00],  // 11 brown / olive (floor)
  [0xFF, 0x4E, 0x57],  // 12 pink
  [0xA4, 0x96, 0xFF],  // 13 light blue
  [0x75, 0xCC, 0x80],  // 14 yellow-green
  [0xB5, 0x1A, 0x58],  // 15 purple
];

/** Playfield dimensions — per docs/PORT_RUNBOOK.md Section 0.6.
 *  The playfield IS the screen: 20×12 tiles = 160×96 px. No scrolling. */
export const COLS = 20;
export const ROWS = 12;
export const TILE_SIZE = 8;
export const WIDTH = COLS * TILE_SIZE;   // 160
export const HEIGHT = ROWS * TILE_SIZE;  // 96

/** Decoded BACKTAB word */
export interface DecodedTile {
  card: number;    // 0-63
  isGram: boolean; // true = GRAM, false = GROM
  fg: number;      // 0-7 foreground color
  bg: number;      // 0-15 background color
}

/**
 * Decode a BACKTAB word in STIC Foreground/Background mode.
 *
 * Faithful to jzIntv's stic_draw_fgbg (vendor/jzintv-src/stic/stic.c):
 *   gr_idx = word & 0x9F8
 *   card   = (gr_idx >> 3) & 0x3F        # 0..63
 *   is_gram= (gr_idx & 0x800) != 0       # bit 11 -> GRAM, else GROM
 *   fg     = word & 0x7                  # 0..7
 *   bg     = ((word>>9)&0xB) | ((word>>11)&0x4)   # 0..15
 */
export function decodeFgbgWord(word: number): DecodedTile {
  const grIdx = word & 0x9F8;
  return {
    card: (grIdx >> 3) & 0x3F,
    isGram: (grIdx & 0x800) !== 0,
    fg: word & 0x7,
    bg: ((word >> 9) & 0xB) | ((word >> 11) & 0x4),
  };
}

/**
 * Render a 20×12 room to an ImageData buffer (160×96 px).
 *
 * @param backtab - Flat array of 240 BACKTAB words (row-major, 20 per row)
 * @param gram - GRAM tile data (8 bytes per card)
 * @param grom - GROM tile data (8 bytes per card)
 * @param img - Target ImageData (WIDTH × HEIGHT pixels)
 */
export function renderRoom(
  backtab: number[],
  gram: Uint8Array,
  grom: Uint8Array,
  img: ImageData,
): void {
  for (let row = 0; row < ROWS; row++) {
    for (let col = 0; col < COLS; col++) {
      const word = backtab[row * COLS + col] ?? 0;
      const { card, isGram, fg, bg } = decodeFgbgWord(word);

      // Get 8 bytes of card bitmap (1bpp, 8×8)
      const cardBase = card * 8;
      const cardBytes = isGram
        ? gram.subarray(cardBase, cardBase + 8)
        : grom.subarray(cardBase, cardBase + 8);

      const fgColor = PALETTE[fg & 0xF];
      const bgColor = PALETTE[bg & 0xF];

      const x0 = col * TILE_SIZE;
      const y0 = row * TILE_SIZE;

      for (let y = 0; y < TILE_SIZE; y++) {
        const byte = cardBytes[y] ?? 0;
        for (let x = 0; x < TILE_SIZE; x++) {
          // 1bpp: bit 7 = leftmost pixel
          const bit = (byte >> (7 - x)) & 1;
          const [r, g, b] = bit ? fgColor : bgColor;

          const px = (y0 + y) * WIDTH + (x0 + x);
          const idx = px * 4;
          img.data[idx] = r;
          img.data[idx + 1] = g;
          img.data[idx + 2] = b;
          img.data[idx + 3] = 255;
        }
      }
    }
  }
}

/**
 * Render an arbitrary W×H tile grid (e.g. a 32×64 maze level) to an offscreen
 * canvas at native resolution (cols*8 × rows*8). Used by the scrolling viewport,
 * which blits a 160×96 window of this onto the visible canvas each frame.
 */
export function renderGridToCanvas(
  grid: number[][],
  gram: Uint8Array,
  grom: Uint8Array,
): HTMLCanvasElement {
  const rows = grid.length;
  const cols = grid[0]?.length ?? 0;
  const w = cols * TILE_SIZE;
  const h = rows * TILE_SIZE;
  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d')!;
  const img = ctx.createImageData(w, h);
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const { card, isGram, fg, bg } = decodeFgbgWord(grid[row][col] ?? 0);
      const cardBase = card * 8;
      const cardBytes = isGram
        ? gram.subarray(cardBase, cardBase + 8)
        : grom.subarray(cardBase, cardBase + 8);
      const fgColor = PALETTE[fg & 0xF];
      const bgColor = PALETTE[bg & 0xF];
      const x0 = col * TILE_SIZE;
      const y0 = row * TILE_SIZE;
      for (let y = 0; y < TILE_SIZE; y++) {
        const byte = cardBytes[y] ?? 0;
        for (let x = 0; x < TILE_SIZE; x++) {
          const bit = (byte >> (7 - x)) & 1;
          const [r, g, b] = bit ? fgColor : bgColor;
          const px = (y0 + y) * w + (x0 + x);
          const idx = px * 4;
          img.data[idx] = r;
          img.data[idx + 1] = g;
          img.data[idx + 2] = b;
          img.data[idx + 3] = 255;
        }
      }
    }
  }
  ctx.putImageData(img, 0, 0);
  return canvas;
}

/**
 * Create an offscreen canvas and render a room to it.
 * Returns the canvas (160×96 native resolution).
 */
export function renderRoomToCanvas(
  backtab: number[],
  gram: Uint8Array,
  grom: Uint8Array,
): HTMLCanvasElement {
  const canvas = document.createElement('canvas');
  canvas.width = WIDTH;
  canvas.height = HEIGHT;
  const ctx = canvas.getContext('2d')!;
  const img = ctx.createImageData(WIDTH, HEIGHT);
  renderRoom(backtab, gram, grom, img);
  ctx.putImageData(img, 0, 0);
  return canvas;
}
