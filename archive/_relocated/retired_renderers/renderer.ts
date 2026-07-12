/* -------------------------------------------------------------
 *  Swords & Serpents – Browser renderer (all 5 optional features)
 * ------------------------------------------------------------- */

export const TILE_W = 8; // tile width (pixels)
export const TILE_H = 8; // tile height (pixels)
export const PLAYFIELD_W = 32; // tiles across
export const PLAYFIELD_H = 24; // tiles down
export const SCREEN_W = PLAYFIELD_W * TILE_W; // 256 px
export const SCREEN_H = PLAYFIELD_H * TILE_H; // 192 px
export const ASPECT_FACTOR = 1.25; // vertical stretch for 4:3 TV

/** -----------------------------------------------------------
 *  1️⃣  Intellivision palette (exact JZINTV_PALETTE)
 * ----------------------------------------------------------- */
export const JZINTV_PALETTE: [number, number, number][] = [
  [0, 0, 0],          // 0 – black
  [33, 200, 66],      // 1 – green
  [94, 220, 120],    // 2 – pastel‑green
  [84, 84, 84],      // 3 – dark‑gray
  [255, 255, 255],   // 4 – white
  [255, 255, 0],     // 5 – yellow
  [255, 120, 0],     // 6 – orange
  [255, 0, 0],       // 7 – red
  [255, 0, 255],     // 8 – magenta
  [0, 0, 255],       // 9 – blue
  [0, 255, 255],     // A – cyan
  [0, 255, 0],       // B – bright‑green
  [84, 110, 0],      // C – olive (floor)
  [120, 120, 120],   // D – light‑gray
  [180, 180, 180],   // E – very light gray
  [255, 180, 180]    // F – pink / skin
];

/** -----------------------------------------------------------
 *  2️⃣  Binary helpers
 * ----------------------------------------------------------- */
export async function loadBinary(file: File): Promise<Uint8Array> {
  const buf = await file.arrayBuffer();
  return new Uint8Array(buf);
}
export function readWord(buf: Uint8Array, offset: number): number {
  return (buf[offset] << 8) | buf[offset + 1];
}

/** -----------------------------------------------------------
 *  3️⃣  BACKTAB decoder (FG/BG mode)
 * ----------------------------------------------------------- */
export interface DecodedTile {
  card: number;
  isGram: boolean;
  fg: number; // palette index 0‑15
  bg: number; // palette index 0‑15
}
export function decodeFgbgWord(word: number): DecodedTile {
  const card = (word >>> 3) & 0x3f;
  const isGram = (word & 0x800) !== 0; // bit 11
  const fg = word & 0x7;
  const bg = ((word >>> 9) & 0xb) | ((word >>> 11) & 0x4);
  return { card, isGram, fg, bg };
}

/** -----------------------------------------------------------
 *  4️⃣  Parse a binary BACKTAB dump (256 words = 512 bytes)
 * ----------------------------------------------------------- */
export function parseBacktab(buf: Uint8Array): DecodedTile[] {
  const tiles: DecodedTile[] = [];
  for (let i = 0; i < 256; i++) {
    const word = readWord(buf, i * 2);
    tiles.push(decodeFgbgWord(word));
  }
  return tiles;
}

/** -----------------------------------------------------------
 *  5️⃣  Extract a tile (GROM or GRAM) → 8×8 palette‑index array
 * ----------------------------------------------------------- */
export function getTile(
  graphics: Uint8Array,
  tileIndex: number,
  isGram: boolean
): Uint8Array {
  const tileSize = isGram ? 64 : 16; // bytes per tile
  const offset = tileIndex * tileSize;
  const raw = graphics.slice(offset, offset + tileSize);

  if (!isGram) {
    // GROM: each byte holds two 2‑bit pixels (high‑order first)
    const out = new Uint8Array(64);
    for (let y = 0; y < 8; y++) {
      const byte = raw[y];
      for (let x = 0; x < 8; x++) {
        const shift = 6 - (x & 6);
        out[y * 8 + x] = (byte >>> shift) & 0x3;
      }
    }
    return out;
  }
  // GRAM already stores a palette index per pixel (0‑15)
  return raw;
}

/** -----------------------------------------------------------
 *  6️⃣  Draw a tile onto an ImageData buffer
 * ----------------------------------------------------------- */
export function drawTile(
  imgData: ImageData,
  tx: number,
  ty: number,
  tilePixels: Uint8Array, // 64 entries (0‑3 for GROM, 0‑15 for GRAM)
  fgIdx: number,
  bgIdx: number
) {
  const { data, width } = imgData;
  const baseX = tx * TILE_W;
  const baseY = ty * TILE_H;

  for (let y = 0; y < TILE_H; y++) {
    for (let x = 0; x < TILE_W; x++) {
      const pix = tilePixels[y * TILE_W + x];
      const paletteIdx = pix === 0 ? bgIdx : fgIdx; // 0 = background for GROM
      const [r, g, b] = JZINTV_PALETTE[paletteIdx];
      const px = baseX + x;
      const py = baseY + y;
      const i = (py * width + px) * 4;
      data[i] = r;
      data[i + 1] = g;
      data[i + 2] = b;
      data[i + 3] = 255;
    }
  }
}

/** -----------------------------------------------------------
 *  7️⃣  MOB (player sprite) overlay – optional
 * ----------------------------------------------------------- */
export interface MobInfo {
  /** 16×16 pixel sprite (palette indices) */
  pixels: Uint8Array;
  /** top‑left tile column where the sprite starts */
  xTile: number;
  /** top‑left tile row (will be doubled vertically) */
  yTile: number;
}
export function drawMob(imgData: ImageData, mob: MobInfo) {
  const { data, width } = imgData;
  const baseX = mob.xTile * TILE_W;
  const baseY = mob.yTile * TILE_H * 2; // vertical stretch factor = 2

  for (let y = 0; y < 16; y++) {
    for (let x = 0; x < 16; x++) {
      const paletteIdx = mob.pixels[y * 16 + x];
      const [r, g, b] = JZINTV_PALETTE[paletteIdx];
      const px = baseX + x;
      const py = baseY + y;
      const i = (py * width + px) * 4;
      data[i] = r;
      data[i + 1] = g;
      data[i + 2] = b;
      data[i + 3] = 255;
    }
  }
}

/** -----------------------------------------------------------
 *  8️⃣  Hybrid mode – overlay a reference GIF and replace blue pixels
 * ----------------------------------------------------------- */
export async function applyHybridOverlay(
  ctx: CanvasRenderingContext2D,
  referenceImg: HTMLImageElement,
  decodedImg: HTMLCanvasElement
) {
  // draw reference GIF
  ctx.drawImage(referenceImg, 0, 0, SCREEN_W, SCREEN_H);

  // read both buffers
  const refData = ctx.getImageData(0, 0, SCREEN_W, SCREEN_H);
  const decodedData = decodedImg
    .getContext('2d')!
    .getImageData(0, 0, SCREEN_W, SCREEN_H);

  // replace pure blue (0,0,255) with decoded pixel
  for (let i = 0; i < refData.data.length; i += 4) {
    const r = refData.data[i];
    const g = refData.data[i + 1];
    const b = refData.data[i + 2];
    if (r === 0 && g === 0 && b === 255) {
      refData.data[i] = decodedData.data[i];
      refData.data[i + 1] = decodedData.data[i + 1];
      refData.data[i + 2] = decodedData.data[i + 2];
    }
  }
  ctx.putImageData(refData, 0, 0);
}

/** -----------------------------------------------------------
 *  9️⃣  Pixel‑aspect correction (vertical stretch ×1.25)
 * ----------------------------------------------------------- */
export function applyAspectCorrection(srcCanvas: HTMLCanvasElement): HTMLCanvasElement {
  const dst = new OffscreenCanvas(SCREEN_W, Math.round(SCREEN_H * ASPECT_FACTOR));
  const dctx = dst.getContext('2d')!;
  dctx.imageSmoothingEnabled = false;
  dctx.drawImage(
    srcCanvas,
    0,
    0,
    SCREEN_W,
    SCREEN_H,
    0,
    0,
    SCREEN_W,
    Math.round(SCREEN_H * ASPECT_FACTOR)
  );
  return dst;
}

/** -----------------------------------------------------------
 * 10️⃣  Full room render (core pipeline)
 * ----------------------------------------------------------- */
export interface RenderOptions {
  /** Optional reference GIF for hybrid mode */
  referenceGif?: HTMLImageElement;
  /** Optional MOB overlay */
  mobInfo?: MobInfo;
  /** Enable hybrid mode? (default false) */
  hybrid?: boolean;
  /** Enable aspect‑stretch? (default false) */
  stretch?: boolean;
}
export async function renderRoom(
  backtab: Uint8Array,
  grom: Uint8Array,
  gram: Uint8Array,
  opts: RenderOptions = {}
): Promise<HTMLCanvasElement> {
  const tiles = parseBacktab(backtab);
  const canvas = new OffscreenCanvas(SCREEN_W, SCREEN_H);
  const ctx = canvas.getContext('2d')!;
  const imgData = ctx.createImageData(SCREEN_W, SCREEN_H);

  // draw tiles
  for (let ty = 0; ty < PLAYFIELD_H; ty++) {
    for (let tx = 0; tx < PLAYFIELD_W; tx++) {
      const idx = ty * PLAYFIELD_W + tx;
      const { card, isGram, fg, bg } = tiles[idx];
      const graphics = isGram ? gram : grom;
      const tilePixels = getTile(graphics, card, isGram);
      drawTile(imgData, tx, ty, tilePixels, fg, bg);
    }
  }
  ctx.putImageData(imgData, 0, 0);

  // optional MOB overlay
  if (opts.mobInfo) {
    drawMob(imgData, opts.mobInfo);
    ctx.putImageData(imgData, 0, 0);
  }

  // hybrid mode
  if (opts.hybrid && opts.referenceGif) {
    await applyHybridOverlay(ctx, opts.referenceGif, canvas);
  }

  // aspect stretch
  if (opts.stretch) {
    const stretched = applyAspectCorrection(canvas);
    return stretched as unknown as HTMLCanvasElement;
  }

  return canvas as unknown as HTMLCanvasElement;
}

/** -----------------------------------------------------------
 * 11️⃣  Animated GIF generation (rooms 0‑5)
 * ----------------------------------------------------------- */
import GIF from 'gif.js';
export async function renderAnimatedDungeon(
  backtabFiles: Uint8Array[], // one per room (0‑5)
  grom: Uint8Array,
  gram: Uint8Array,
  referenceGif?: HTMLImageElement,
  mobInfo?: MobInfo
): Promise<Blob> {
  const gif = new GIF({
    workers: 2,
    quality: 10
    // let GIF.js load its own internal worker script
  });

  for (let room = 0; room < backtabFiles.length; room++) {
    const canvas = await renderRoom(backtabFiles[room], grom, gram, {
      hybrid: !!referenceGif,
      referenceGif,
      mobInfo,
      stretch: true // aspect‑corrected frames look best
    });
    gif.addFrame(canvas, { delay: 500 });
  }

  return new Promise((resolve, reject) => {
    gif.on('finished', (blob: Blob) => resolve(blob));
    gif.on('error', (e: any) => reject(e));
    gif.render();
  });
}

/** -----------------------------------------------------------
 * 12️⃣  Helper: parse a plain‑text hex dump (optional)
 * ----------------------------------------------------------- */
export function parseHexDump(text: string): Uint8Array {
  const bytes: number[] = [];
  const parts = text.split(/\s+/);
  for (const p of parts) {
    if (p.length === 0) continue;
    bytes.push(parseInt(p, 16));
  }
  return new Uint8Array(bytes);
}
