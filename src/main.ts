import { WIDTH, HEIGHT } from './platform/stic';
import { createInitialState, PlayerState } from './engine/state';
import { InputHandler } from './engine/input';
import { Maze, isWalkableWord, gramCard } from './world/maze';
import { LevelWorld, wrap, wrapDelta, TILE } from './world/torus';
import {
  ObjectTables, LevelObjectState, createObjectState, tileBlock, pickupType,
  TYPE_KEY, TYPE_MARKER, TYPE_UP_STAIRS, CARD_DOWN_STAIRS, CARD_UP_STAIRS,
  CARD_CHEST, CARD_MARKER, CARD_LANTERN, CARD_KEY, WORD_DOWN_STAIRS, WORD_TAKEN,
  MAX_IN_HAND,
} from './world/objects';
import { doorCards } from './world/doors';
import {
  Enemy, Fireball, GameItem, ItemKind,
  createEnemy, createItem, updateEnemy, resolveContact,
  injurePlayer, tickPlayerCombat, isGameOver,
  SERPENT_W, SERPENT_H,
  FIREBALL_FRAMES, SPAWN_EFFECT, ITEM_SPRITES,
  KNIGHT_POSES, SWORD_BITMAPS, knightPoseSector,
  SORCERER_BODY, SORCERER_MATERIALISE, sorcererAppearPose, sorcererVanishPose,
  SORCERER_OFFSETS, KNIGHT_SPAWN_DY,
} from './engine/combat';

let state: PlayerState;
let input: InputHandler;
let gameStarted = false;
let gameWon = false;
let playerSprites: number[][] = [];
let frameCount = 0;
let infoMessage = '';
let infoTimer = 0;

let mazes: Maze[] = [];
let levels: LevelWorld[] = [];
let gramData: Uint8Array;
let gromData: Uint8Array;
let objectTables: ObjectTables;

// --- Per-level world content ---
interface DeathFx { x: number; y: number; t: number; }

let enemiesByLevel: Enemy[][] = [];
let itemsByLevel: GameItem[][] = [];       // only the Crown now — ROM objects live in the tile grid
let objStateByLevel: LevelObjectState[] = [];
// The DOWN-stairs tile written by ENTER at a level's marker (finding #10):
// a transient BACKTAB word — gone once its column/row scrolls off screen.
let openStairs: ({ col: number; row: number } | null)[] = [];
let entry0: { x: number; y: number } = { x: 0, y: 0 };
let fireballs: Fireball[] = [];
let deathFx: DeathFx[] = [];
let kills = 0;

// Captured item/status mechanics (docs/HANDOVER.md ROM finding #8)
const PICKUP_LOCK_FRAMES = 21;   // movement lock after ENTER on an object
const STATUS_FRAMES = 227;       // keypad 0 status screen duration
let statusTimer = 0;
let pickupFlash = -1;            // >=0 while a pickup lock is running (no injury flash)
let inHandValue = 0;             // value of treasures currently carried

// Stairs transition (captured, finding #10): the level number changes at
// once, "Stairs to level N" is printed in RED over row 5 of the OLD screen,
// the Prince vanishes, everything freezes for 226 frames, then the new level
// is drawn with the Prince at the SAME coordinates.
const STAIRS_FRAMES = 226;
let transition: { timer: number; toLevel: number; text: string } | null = null;

// Chomping-door clock (finding #9) — all doors on a level chomp in lockstep.
let doorClock = 0;
let doorPhaseKey = '';

const PLAYER_SCALE = 4;
const PLAYER_ASPECT_SCALE = 1.25;
const PLAYER_WIDTH = 8 * PLAYER_SCALE;
const VIEW_W = WIDTH;
const VIEW_H = HEIGHT;
// Real ROM walking speed: 0.5 px/frame on cardinals (1 px every 2 frames),
// ~0.35 px/frame per axis on diagonals — captured frame-by-frame from the
// player position word ($0325) under real disc input (Intellijsd oracle).
const MOVE_SPEED = 0.5;

// Enemies farther than this (torus distance) from the player are dormant.
// Kept tight: knights fly through walls, so anything active WILL reach you.
const ACTIVATION_X = 110;
const ACTIVATION_Y = 120;

// The Sinister Serpent — GRAM cards 24-33 assembled as background art.
// Layout decoded pixel-exact from a real level-4 screenshot (see
// docs/HANDOVER.md ROM finding #3): a 5×3-tile dragon facing left, neck
// (27, 28) extended toward its fire breath, fiery red belly behind the
// repeated card-29 body segments.
const OLIVE = '#546E00';
const FIRE_RED = '#FF3D10';
// Verified against the ROM's own renderer (traces/rooms/lair_probe_out.txt):
// level 3 page 2 rows 22-24 — words 1EC5..1F0D, the 29s are 0CED (bg red).
const SERPENT_LAYOUT: { r: number; c: number; card: number; bg: string }[] = [
  { r: 0, c: 2, card: 24, bg: OLIVE },
  { r: 0, c: 3, card: 25, bg: OLIVE },
  { r: 0, c: 4, card: 26, bg: OLIVE },
  { r: 1, c: 0, card: 27, bg: OLIVE },
  { r: 1, c: 1, card: 28, bg: OLIVE },
  { r: 1, c: 2, card: 29, bg: FIRE_RED },
  { r: 1, c: 3, card: 29, bg: FIRE_RED },
  { r: 1, c: 4, card: 29, bg: FIRE_RED },
  { r: 1, c: 5, card: 30, bg: OLIVE },
  { r: 2, c: 2, card: 31, bg: OLIVE },
  { r: 2, c: 3, card: 32, bg: OLIVE },
  { r: 2, c: 4, card: 33, bg: OLIVE },
];

// ---------------------------------------------------------------------------
// PLAYER FACING — ground truth from the REAL player under REAL disc input,
// captured in the Intellijsd browser emulator (tools/intellijsd/) with a
// legitimately booted game (title → '1' → ENTER). See docs/HANDOVER.md
// ROM finding #6. Dominant body frame per direction (≥33 of 40 frames):
//   E:  F0            W:  F0 xflip+yflip
//   N:  F4 xflip      S:  F4 yflip
//   NE: F2            SE: F2 yflip     NW: F2 xflip     SW: F2 xflip+yflip
// The player has NO walk animation in any direction (233+ consecutive
// identical frames on straight runs). Turning shows a 3-4 frame transition
// (old frame, then old frame with new flips) — cosmetic, not modelled.
// F1 and F3 are never the player's steady pose; the earlier F4/F3 walk cycle
// was a KNIGHT behaviour and is knight-only below.
// ---------------------------------------------------------------------------
const lw = (): LevelWorld => levels[state.level];

// STIC 8-colour foreground palette (indices 0-7) as CSS.
const FG = ['#000000', '#002DFF', '#FF3D10', '#C9CFAB', '#386B3F', '#00A756', '#FAEA50', '#FFFCFF'];
// Captured colour sequences (fg index per frame) — see HANDOVER finding #7.
// Player body while stunned (samples every ~2 frames over the 40-frame stun):
const STUN_CYCLE = [5, 4, 2, 1, 4, 5, 0, 1, 0, 3, 7, 5, 0, 4, 2, 1, 3, 4, 6, 5, 2, 3, 4].map(i => FG[i]);
// Player sword, every frame, always:
const SWORD_CYCLE = [6, 1, 2, 4, 6, 1, 0, 4, 3, 2, 3, 0, 2, 3, 6, 5, 0, 1, 7, 2, 7, 4, 1, 3].map(i => FG[i]);

function facingFrame(dx: number, dy: number, knightWalk = false): { frame: number; mirror: boolean; flip: boolean } {
  const ax = Math.abs(dx);
  const ay = Math.abs(dy);
  if (ax > 0 && ay > 0 && Math.min(ax, ay) / Math.max(ax, ay) > 0.414) {
    // within ±22.5° of a diagonal
    return { frame: 2, mirror: dx < 0, flip: dy > 0 };
  }
  if (ax >= ay && ax > 0) {
    return { frame: 0, mirror: dx < 0, flip: dx < 0 };
  }
  if (ay > 0) {
    if (knightWalk && Math.floor(frameCount / 5) % 2 === 1) {
      // Knight-only F3 walk phase (captured from knight animation scripts).
      return { frame: 3, mirror: false, flip: dy > 0 };
    }
    return dy < 0
      ? { frame: 4, mirror: true,  flip: false }   // N
      : { frame: 4, mirror: false, flip: true  };  // S
  }
  return { frame: 0, mirror: false, flip: false };
}

interface MazeData { w: number; h: number; grid: number[][]; }

async function loadAssets() {
  // The 4 real fortress levels (128×64 tiles each) captured from the ROM's
  // renderer — see docs/HANDOVER.md ROM finding #4.
  const levelUrls = Array.from({ length: 4 }, (_, i) =>
    fetch(`/assets/world_level${i}.json`));

  const [gramRes, gromRes, spritesRes, objectsRes, ...mazeResps] = await Promise.all([
    fetch('/assets/gram_tiles.json'),
    fetch('/assets/grom.bin'),
    fetch('/assets/player_sprites.json'),
    fetch('/assets/objects.json'),
    ...levelUrls,
  ]);

  const gramArray = await gramRes.json() as number[];
  const gromBuffer = await gromRes.arrayBuffer();
  const spritesData = await spritesRes.json() as { warrior: number[][] };
  playerSprites = spritesData.warrior;
  // The ROM's object tables ($64DE/$6580/$655E) — scripts/extract_objects.mjs
  objectTables = await objectsRes.json() as ObjectTables;

  const loadedMazes: Maze[] = [];
  for (const resp of mazeResps) {
    const md = await resp.json() as MazeData;
    loadedMazes.push({ w: md.w, h: md.h, grid: md.grid });
  }

  return {
    gram: new Uint8Array(gramArray),
    grom: new Uint8Array(gromBuffer),
    mazes: loadedMazes,
  };
}

// Deterministic RNG so every playthrough gets the same dungeon.
function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function setInfo(msg: string, frames: number = 180) {
  infoMessage = msg;
  infoTimer = frames;
}

// Torus Chebyshev distance within level `li`.
function tDist(li: number, ax: number, ay: number, bx: number, by: number): number {
  const w = levels[li].pixelWidth;
  const h = levels[li].pixelHeight;
  return Math.max(Math.abs(wrapDelta(ax, bx, w)), Math.abs(wrapDelta(ay, by, h)));
}

// Nearest walkable spot to (x,y) in level `li` (expanding ring, wrap-aware).
function findWalkableNear(li: number, x: number, y: number): { x: number; y: number } {
  const world = levels[li];
  if (world.canWalk(x + 4, y + 4)) return { x: wrap(x, world.pixelWidth), y: wrap(y, world.pixelHeight) };
  for (let r = TILE; r <= TILE * 16; r += TILE) {
    for (let dy = -r; dy <= r; dy += TILE) {
      for (let dx = -r; dx <= r; dx += TILE) {
        if (world.canWalk(x + dx + 4, y + dy + 4)) {
          return { x: wrap(x + dx, world.pixelWidth), y: wrap(y + dy, world.pixelHeight) };
        }
      }
    }
  }
  return { x: wrap(x, world.pixelWidth), y: wrap(y, world.pixelHeight) };
}

const FLOOR_WORD = 0x1603;
let serpentLair: { x: number; y: number } | null = null;

// The Serpent is baked into level 3's map as background tiles (cards 24-33).
// Strip them from the grid (so the dead Serpent leaves floor behind) and
// remember where it was — the live entity is drawn at that exact spot.
function extractSerpentLair(): void {
  serpentLair = null;
  const m = mazes[mazes.length - 1];
  for (let r = 0; r < m.h; r++) {
    for (let c = 0; c < m.w; c++) {
      const w = m.grid[r][c];
      const card = (w >> 3) & 0x3F;
      if ((w & 0x800) && card >= 24 && card <= 33) {
        if (card === 27) serpentLair = { x: c * TILE, y: (r - 1) * TILE };
        m.grid[r][c] = FLOOR_WORD;
      }
    }
  }
}

// Enemies are still scattered (spawn placement not captured yet); every
// item, key, chest, lantern and stairway comes from the ROM's object tables
// and is already baked into the captured tile grids at its real position.
// The Serpent and the Crown of Kings wait on the last level.
function populateWorld(rand: () => number) {
  enemiesByLevel = [];
  itemsByLevel = [];
  objStateByLevel = [];
  openStairs = [];
  fireballs = [];
  deathFx = [];
  kills = 0;

  // Level 0 entry: the ROM boots with camera (2, $1A) → the Prince stands
  // near tile (12, 32) — on the treasure chest (object type 9).
  entry0 = findWalkableNear(0, 12 * TILE, 32 * TILE);

  for (let i = 0; i < mazes.length; i++) {
    const m = mazes[i];
    const enemies: Enemy[] = [];
    const items: GameItem[] = [];
    objStateByLevel.push(createObjectState());
    openStairs.push(null);

    // Knights and sorcerers are not pre-placed: the ROM spawns them around
    // the Prince as the game runs (see spawnDirector).
    void m; void rand;

    if (i === mazes.length - 1 && serpentLair) {
      // The Serpent's lair at its REAL position from the level-3 map data
      // (the ziggurat chamber); the Crown of Kings lies behind its tail.
      enemies.push(createEnemy(serpentLair.x, serpentLair.y, 'serpent'));
      const cpos = findWalkableNear(i, serpentLair.x + SERPENT_W + 16, serpentLair.y + 8);
      items.push(createItem(cpos.x, cpos.y, 'crown'));
    }

    enemiesByLevel.push(enemies);
    itemsByLevel.push(items);
  }
}

// --- Spawn director (finding #11) ---
// Captured: enemies appear around the Prince during play, never pre-placed.
// Sorcerers materialise at a small offset from him (observed offsets in
// SORCERER_OFFSETS); knights appear at the TOP or BOTTOM screen edge, x ≈
// his. Over ~13,000 idle/wandering frames on level 1 there were 10 spawn
// events (first one 314-374 frames in), i.e. roughly one per 5 rolls of the
// ROM's 64-tick (~230-frame) spawn timer — the exact roll/odds are NOT
// captured; 20 % per roll, 50/50 knight vs sorcerer, at most 3 live foes.
const SPAWN_ROLL_FRAMES = 230;
const SPAWN_CHANCE = 0.2;
const MAX_LIVE_FOES = 3;
// Captured: the first foe of a game is a Red Sorcerer 374 frames after the
// quest starts (two identical boots), at offset (-10, 26) from the Prince.
const FIRST_SPAWN_FRAME = 374;
let spawnClock = 0;
let firstSpawnDone = false;
let rng: () => number = Math.random;

function spawnDirector() {
  spawnClock++;
  const foes = enemiesByLevel[state.level];
  const world = lw();
  if (!firstSpawnDone) {
    if (spawnClock < FIRST_SPAWN_FRAME) return;
    firstSpawnDone = true;
    spawnClock = 0;
    foes.push(createEnemy(wrap(state.x - 10, world.pixelWidth), wrap(state.y + 26, world.pixelHeight), 'sorcerer'));
    return;
  }
  if (spawnClock < SPAWN_ROLL_FRAMES) return;
  spawnClock = 0;
  const live = foes.filter(e => e.alive && e.type !== 'serpent').length;
  if (live >= MAX_LIVE_FOES || rng() >= SPAWN_CHANCE) return;
  if (rng() < 0.5) {
    const off = SORCERER_OFFSETS[Math.floor(rng() * SORCERER_OFFSETS.length)];
    foes.push(createEnemy(wrap(state.x + off[0], world.pixelWidth), wrap(state.y + off[1], world.pixelHeight), 'sorcerer'));
  } else {
    const dy = rng() < 0.5 ? KNIGHT_SPAWN_DY : -KNIGHT_SPAWN_DY;
    foes.push(createEnemy(wrap(state.x + Math.round(rng() * 2), world.pixelWidth), wrap(state.y + dy, world.pixelHeight), 'phantom_knight'));
  }
}

// Captured: when the Prince falls, every knight/sorcerer/fireball vanishes.
function clearFoes() {
  for (const e of enemiesByLevel[state.level]) if (e.type !== 'serpent') e.alive = false;
  fireballs = [];
}

// ROM object record at a tile of the given level, if any.
function objectAt(level: number, col: number, row: number) {
  return objectTables.levels[level].find(o => o.col === col && o.row === row) ?? null;
}

// What a BACKTAB regeneration from map + object data would draw at a tile
// (L_5EC7 map word, then the L_6377 object overlay gated by G_0180).
function regeneratedWord(level: number, col: number, row: number): number {
  const base = levels[level].base[row][col];
  const obj = objectAt(level, col, row);
  if (!obj) return base;
  if (obj.type <= TYPE_KEY && !objStateByLevel[level].present[obj.type]) return WORD_TAKEN;
  return obj.word;
}

// Tiles that scrolled off screen come back regenerated (finding #10): this
// is how the stairs tile disappears and how duplicate treasures of a taken
// type vanish.
function refreshOffscreenTiles(camX: number, camY: number) {
  const world = lw();
  for (const key of world.stale) {
    const col = key % world.maze.w;
    const row = Math.floor(key / world.maze.w);
    const dx = wrap(col * TILE - camX, world.pixelWidth);
    const dy = wrap(row * TILE - camY, world.pixelHeight);
    const visible = dx < VIEW_W && dy < VIEW_H;
    if (visible) continue;
    world.setWord(col, row, regeneratedWord(state.level, col, row));
    world.stale.delete(key);
    const os = openStairs[state.level];
    if (os && os.col === col && os.row === row) openStairs[state.level] = null;
  }
}

function markStale(level: number, col: number, row: number) {
  const w = levels[level];
  if (w.maze.grid[row][col] !== regeneratedWord(level, col, row)) w.stale.add(w.key(col, row));
  else w.stale.delete(w.key(col, row));
}

// Full BACKTAB redraw (L_5EE2) — on entering a level everything regenerates.
function redrawLevel(level: number) {
  const w = levels[level];
  for (const key of w.stale) {
    const col = key % w.maze.w;
    const row = Math.floor(key / w.maze.w);
    w.setWord(col, row, regeneratedWord(level, col, row));
  }
  w.stale.clear();
  openStairs[level] = null;
  applyDoorPhase(level, true);
}

function applyDoorPhase(level: number, force = false) {
  const { c1, c2 } = doorCards(doorClock);
  const key = c1.join() + '|' + c2.join();
  if (!force && key === doorPhaseKey) return;
  doorPhaseKey = key;
  levels[level].setCardBitmap(1, c1);
  levels[level].setCardBitmap(2, c2);
}

// Player MOB as an 8×8 world-pixel mask (the 8×16 MOB rows are half-height).
function playerMask(): number[] {
  const f = facingFrame(state.faceDx, state.faceDy);
  const bytes = playerSprites[f.frame] ?? [];
  const mask: number[] = [];
  for (let y = 0; y < 8; y++) {
    const r0 = f.flip ? 15 - 2 * y : 2 * y;
    const r1 = f.flip ? 14 - 2 * y : 2 * y + 1;
    let b = (bytes[r0] ?? 0) | (bytes[r1] ?? 0);
    if (f.mirror) {
      let m = 0;
      for (let i = 0; i < 8; i++) if (b & (1 << i)) m |= 0x80 >> i;
      b = m;
    }
    mask.push(b);
  }
  return mask;
}

// STIC MOB-vs-background collision for one tile: any sprite pixel over any
// foreground pixel of the tile's (possibly animated) card bitmap.
function spriteHitsTile(sx: number, sy: number, mask: number[], col: number, row: number): boolean {
  const world = lw();
  const bm = world.cardBitmap(gramCard(world.maze.grid[row][col]));
  if (!bm) return false;
  const dx = wrapDelta(sx, col * TILE, world.pixelWidth);
  const dy = wrapDelta(sy, row * TILE, world.pixelHeight);
  if (Math.abs(dx) >= 8 || Math.abs(dy) >= 8) return false;
  for (let py = 0; py < 8; py++) {
    const ty = py - dy;
    if (ty < 0 || ty > 7) continue;
    const srow = mask[py];
    const trow = bm[ty] ?? 0;
    if (!srow || !trow) continue;
    for (let px = 0; px < 8; px++) {
      const tx = px - dx;
      if (tx < 0 || tx > 7) continue;
      if ((srow >> (7 - px)) & 1 && (trow >> (7 - tx)) & 1) return true;
    }
  }
  return false;
}

function changeLevel(toLevel: number) {
  // Captured: "Stairs to level N" names the level being entered (1-based).
  transition = { timer: STAIRS_FRAMES, toLevel, text: `Stairs to level ${toLevel + 1}` };
  fireballs = [];
}

function initGame() {
  state = createInitialState();
  input = new InputHandler();

  rng = mulberry32(0x5E44E27);
  populateWorld(rng);
  spawnClock = 0;
  firstSpawnDone = false;

  state.level = 0;
  state.x = entry0.x;
  state.y = entry0.y;
  transition = null;
  doorClock = 0;
  doorPhaseKey = '';
  applyDoorPhase(0, true);

  gameWon = false;
  gameStarted = true;
  setInfo('Slay foes by walking INTO them. Find the key, ENTER at the checkered marker, walk onto the stairs!', 420);
}

function update() {
  if (!gameStarted || levels.length === 0) return;
  frameCount++;
  if (infoTimer > 0) infoTimer--;

  if (gameWon || isGameOver(state)) return;

  // Stairs transition: the ROM busy-waits (L_6746) — the whole game freezes
  // under the message, then the new level is drawn in place.
  if (transition) {
    transition.timer--;
    if (transition.timer <= 0) {
      state.level = transition.toLevel;
      transition = null;
      redrawLevel(state.level);
      state.stunned = 0;
    }
    return;
  }

  // Chomping doors: both GRAM jaw cards follow one 148-frame clock.
  doorClock++;
  applyDoorPhase(state.level);

  const world = lw();
  const W = world.pixelWidth;
  const H = world.pixelHeight;
  const inputState = input.getInput();
  const objState = objStateByLevel[state.level];
  state.keys = objState.taken[TYPE_KEY] ? 1 : 0;

  // Captured: the fallen Prince revives IN PLACE once the disc is released.
  const discReleased = inputState.dx === 0 && inputState.dy === 0;
  const respawned = tickPlayerCombat(state, discReleased);
  if (respawned) {
    setInfo('Reincarnated!', 90);
  }

  // --- Player movement (torus: coordinates wrap, camera stays centred) ---
  if (!state.dead && state.stunned === 0) {
    let mvx = 0;
    let mvy = 0;
    if (inputState.backUp && (state.faceDx !== 0 || state.faceDy !== 0)) {
      mvx = -state.faceDx;
      mvy = -state.faceDy;
      state.moving = true;
    } else if (inputState.dx !== 0 || inputState.dy !== 0) {
      mvx = inputState.dx;
      mvy = inputState.dy;
      state.faceDx = inputState.dx;
      state.faceDy = inputState.dy;
      if (inputState.dx > 0) state.facing = 'right';
      else if (inputState.dx < 0) state.facing = 'left';
      else if (inputState.dy < 0) state.facing = 'up';
      else if (inputState.dy > 0) state.facing = 'down';
      state.moving = true;
    } else {
      state.moving = false;
    }
    if (mvx !== 0 || mvy !== 0) {
      if (mvx !== 0 && mvy !== 0) { mvx *= 0.7071; mvy *= 0.7071; }
      const nx = state.x + mvx * MOVE_SPEED;
      const ny = state.y + mvy * MOVE_SPEED;
      if (world.canWalk(nx + 4, ny + 4)) {
        state.x = nx;
        state.y = ny;
      } else if (mvx !== 0 && world.canWalk(nx + 4, state.y + 4)) {
        state.x = nx;
      } else if (mvy !== 0 && world.canWalk(state.x + 4, ny + 4)) {
        state.y = ny;
      }
      state.x = wrap(state.x, W);
      state.y = wrap(state.y, H);
    }
  } else {
    state.moving = false;
  }

  // --- Background collision → tile classifier (L_6679 → L_65FC) ---
  // The STIC reports the player MOB touching ANY foreground pixel; the ROM
  // then scans the 2×2 tile block under the sprite: card 9 → down a level,
  // card 10 → up a level, cards 1/2 (door jaws) → a knight-sword-grade hit.
  if (!state.dead) {
    const sx = Math.floor(state.x);
    const sy = Math.floor(state.y);
    const block = tileBlock(sx, sy, world.maze.w, world.maze.h);
    const mask = playerMask();
    let bgHit = false;
    let doorBite = false;
    for (const t of block) {
      if (!spriteHitsTile(sx, sy, mask, t.col, t.row)) continue;
      bgHit = true;
      const card = gramCard(world.maze.grid[t.row][t.col]);
      if (card === 1 || card === 2) doorBite = true;
    }
    if (bgHit) {
      const cards = block.map(t => gramCard(world.maze.grid[t.row][t.col]));
      if (cards.includes(CARD_DOWN_STAIRS) && state.level < levels.length - 1) {
        changeLevel(state.level + 1);
        return;
      }
      if (cards.includes(CARD_UP_STAIRS) && state.level > 0) {
        changeLevel(state.level - 1);
        return;
      }
      if (doorBite && state.stunned === 0) {
        const wasGray = state.injured;
        injurePlayer(state);
        setInfo(state.dead ? 'The door bit you down...' : wasGray ? 'The door bites — a life is lost!' : 'The door bites!', 90);
      }
    }
  }

  // --- Enemies (current level only; targets use shortest torus path) ---
  if (!state.dead) spawnDirector();
  const walkFn = (x: number, y: number) => world.canWalk(x, y);
  for (const enemy of enemiesByLevel[state.level]) {
    if (!enemy.alive) continue;
    const dx = wrapDelta(enemy.x, state.x, W);
    const dy = wrapDelta(enemy.y, state.y, H);
    // The Serpent is static lair art — its own fire range gates it instead.
    if (enemy.type !== 'serpent' &&
        (Math.abs(dx) > ACTIVATION_X || Math.abs(dy) > ACTIVATION_Y)) continue;

    // Present the player at their nearest torus representation.
    const shim: PlayerState = { ...state, x: enemy.x + dx, y: enemy.y + dy };
    const shot = updateEnemy(enemy, shim, walkFn);
    enemy.x = wrap(enemy.x, W);
    enemy.y = wrap(enemy.y, H);
    if (shot) {
      shot.x = wrap(shot.x, W);
      shot.y = wrap(shot.y, H);
      fireballs.push(shot);
    }

    const event = resolveContact(shim, enemy);
    if (event === 'enemy_slain') {
      kills++;
      if (enemy.type !== 'phantom_knight') deathFx.push({ x: enemy.x, y: enemy.y, t: 24 });
      if (enemy.type === 'serpent') setInfo('THE SERPENT IS SLAIN! Claim the Crown!', 300);
      else if (enemy.type === 'sorcerer') setInfo('Red Sorcerer vanquished!', 90);
      else setInfo('Phantom Knight slain!', 90);
    } else if (event === 'player_strikes') {
      setInfo('You wound the Serpent!', 90);
    } else if (event === 'player_injured') {
      if (state.stunned === 0 && !state.dead) {
        const wasGray = state.injured;
        injurePlayer(state);
        setInfo(state.dead ? 'You have fallen...' : wasGray ? 'A life is lost!' : 'Injured! (half a life)', 90);
      }
    }
  }

  // --- Fireballs (MOBs — no wall test in the ROM; range-limited instead) ---
  for (const fb of fireballs) {
    if (!fb.alive) continue;
    fb.age++;
    fb.x = wrap(fb.x + fb.dx * fb.speed, W);
    fb.y = wrap(fb.y + fb.dy * fb.speed, H);
    if (fb.age > 80) { // captured: flew 80 frames (~125 px) and vanished with its sorcerer
      fb.alive = false;
      continue;
    }
    if (!state.dead && tDist(state.level, fb.x, fb.y, state.x, state.y) < 5) {
      fb.alive = false;
      if (state.stunned === 0) {
        injurePlayer(state);
        setInfo(state.dead ? 'Burned down...' : 'Scorched by a fireball!', 90);
      }
    }
  }
  fireballs = fireballs.filter(fb => fb.alive);

  // Captured: the moment the Prince falls, every foe and fireball vanishes.
  if (state.dead && enemiesByLevel[state.level].some(e => e.alive && e.type !== 'serpent')) clearFoes();

  // --- Death effects ---
  for (const fx of deathFx) fx.t--;
  deathFx = deathFx.filter(fx => fx.t > 0);

  // --- Items (captured: stand ON the tile, release the disc, press ENTER;
  //     the tile vanishes 2 frames later with a 21-frame movement lock) ---
  const wantPickup = (inputState.enter || inputState.pickup) && discReleased && !state.dead && state.stunned === 0;
  for (const item of itemsByLevel[state.level]) {
    if (item.collected) continue;
    if (tDist(state.level, item.x, item.y, state.x, state.y) < 6) {
      if (item.kind === 'crown') {
        // The Crown cannot be taken while the Serpent lives.
        const serpent = enemiesByLevel[state.level].find(e => e.type === 'serpent');
        if (serpent && serpent.alive) {
          if (infoTimer < 30) setInfo('The Serpent still guards the Crown!', 60);
          continue;
        }
        if (!wantPickup) { if (infoTimer < 30) setInfo('Press ENTER to claim the Crown', 60); continue; }
        item.collected = true;
        gameWon = true;
        setInfo('', 0);
        continue;
      }
    }
  }

  // --- ENTER on a ROM object (L_63F5): first card 12..22 in the 2×2 block ---
  if (wantPickup) {
    const sx = Math.floor(state.x);
    const sy = Math.floor(state.y);
    const block = tileBlock(sx, sy, world.maze.w, world.maze.h);
    for (const t of block) {
      const card = gramCard(world.maze.grid[t.row][t.col]);
      if (card < CARD_CHEST || card > CARD_KEY) continue;
      if (card === CARD_CHEST) {
        storeTreasures();
      } else if (card === CARD_MARKER) {
        // Locked stairway: with this level's key, the DOWN stairs appear in
        // the BACKTAB word after the marker — one column to the right.
        if (objState.taken[TYPE_KEY]) {
          const col = wrap(t.col + 1, world.maze.w);
          world.setWord(col, t.row, WORD_DOWN_STAIRS);
          markStale(state.level, col, t.row);
          openStairs[state.level] = { col, row: t.row };
        }
      } else if (card === CARD_LANTERN) {
        // L_64CB: the player's colour word is reset to white — the injury is cured.
        state.injured = false;
      } else {
        const type = pickupType(card);
        if (type !== TYPE_KEY && state.potions >= MAX_IN_HAND) break; // L_643C: refused
        world.setWord(t.col, t.row, WORD_TAKEN);
        objState.taken[type] = true;
        objState.present[type] = false;
        // Other tiles of this type stay drawn until they scroll off (G_0180 gate).
        for (const o of objectTables.levels[state.level]) {
          if (o.type === type) markStale(state.level, o.col, o.row);
        }
        state.stunned = PICKUP_LOCK_FRAMES;
        pickupFlash = 0;
        if (type === TYPE_KEY) {
          setInfo('Found the key!', 90);
        } else {
          state.potions++;
          inHandValue += 50 * (state.level + 1);
          setInfo('Found a treasure!', 90);
        }
      }
      break;
    }
  }

  // Tiles that left the screen come back regenerated from map + object data.
  refreshOffscreenTiles(wrap(Math.floor(state.x) + 4 - VIEW_W / 2, W), wrap(Math.floor(state.y) + 4 - VIEW_H / 2, H));

  // Status screen (captured: keypad 0; shown ~227 frames)
  if (inputState.status && statusTimer === 0 && !state.dead) statusTimer = STATUS_FRAMES;
  if (statusTimer > 0) statusTimer--;
  if (pickupFlash >= 0 && state.stunned === 0) pickupFlash = -1;

  // Read scroll
  if (inputState.readScroll && state.scrolls > 0 && infoTimer < 30) {
    setInfo('The scroll reads: "The Serpent guards the Crown in the deepest dark..."', 240);
  }

}

// Treasure chest (card 12, level 0 entry): ENTER stores what's in hand and
// shows the status screen (captured; L_6472). Value 50/100/150/200 by the
// level the treasure was found on; a Reincarnation per 300 points.
function storeTreasures() {
  if (state.potions === 0) return;
  state.stored += state.potions;
  const before300 = Math.floor(state.storedValue / 300);
  state.storedValue += inHandValue;
  state.reincarnations += Math.floor(state.storedValue / 300) - before300;
  inHandValue = 0;
  state.potions = 0;
  state.stunned = PICKUP_LOCK_FRAMES;
  pickupFlash = 0;
  statusTimer = STATUS_FRAMES;
  setInfo('Treasures stored!', 90);
}

// Draw a 1bpp sprite in a solid color. rows=16 sprites are MOBs at 2× vertical
// resolution (16 rows = 8 world px); rows=8 sprites are tile-sized.
function drawBitmap(
  ctx: CanvasRenderingContext2D,
  bytes: number[], rows: number,
  px: number, py: number, color: string,
  mirror = false, flip = false,
): void {
  ctx.fillStyle = color;
  const zoomX = PLAYER_SCALE;
  const worldRowH = (rows === 16)
    ? (PLAYER_SCALE * PLAYER_ASPECT_SCALE) / 2
    : PLAYER_SCALE * PLAYER_ASPECT_SCALE;
  for (let y = 0; y < rows; y++) {
    const srcY = flip ? rows - 1 - y : y;
    const byte = bytes[srcY] ?? 0;
    const rowY0 = Math.round(py + y * worldRowH);
    const rowY1 = Math.round(py + (y + 1) * worldRowH);
    const rowH = Math.max(1, rowY1 - rowY0);
    for (let x = 0; x < 8; x++) {
      const bit = mirror ? (byte >> x) & 1 : (byte >> (7 - x)) & 1;
      if (bit) ctx.fillRect(px + x * zoomX, rowY0, zoomX, rowH);
    }
  }
}

// The sword is its own 8×16 MOB in the original: a $FF row (horizontal), a
// $10 column (vertical), or a 45° blade for diagonals. Captured from the
// PLAYER's own sword MOB under real input (Intellijsd oracle, HANDOVER #6):
//   E/W: $FF row at (±8, 0)        N/S: $10 column at (0, ±8)
//   diagonals: a 12-row blade (rows 4-15: 04 04 08 08 10 10 20 20 40 40 80 80,
//   NE-pointing) at (±7, ±7), x/y-flipped per quadrant.
const DIAG_SWORD: number[] = [
  0x00, 0x00, 0x00, 0x00, 0x04, 0x04, 0x08, 0x08,
  0x10, 0x10, 0x20, 0x20, 0x40, 0x40, 0x80, 0x80,
];

function drawSword(
  ctx: CanvasRenderingContext2D,
  px: number, py: number, dirX: number, dirY: number, color: string,
): void {
  const u = PLAYER_SCALE;
  const uy = PLAYER_SCALE * PLAYER_ASPECT_SCALE;
  ctx.fillStyle = color;
  if (dirX === 0 && dirY === 0) dirX = 1;
  const ax = Math.abs(dirX);
  const ay = Math.abs(dirY);
  if (ax > 0 && ay > 0 && Math.min(ax, ay) / Math.max(ax, ay) > 0.414) {
    // diagonal blade at (±7, ±7) from the body, flipped per quadrant
    const sx = px + (dirX > 0 ? 7 : -7) * u;
    const sy = py + (dirY > 0 ? 7 : -7) * uy;
    drawBitmap(ctx, DIAG_SWORD, 16, sx, sy, color, dirX < 0, dirY > 0);
    return;
  }
  if (ax >= ay) {
    const sx = dirX >= 0 ? px + 8 * u : px - 8 * u;
    ctx.fillRect(sx, py + 7 * (uy / 2), 8 * u, Math.max(2, Math.round(uy / 2)));
  } else {
    const sy = dirY >= 0 ? py + 8 * uy : py - 8 * uy;
    ctx.fillRect(px + 3 * u, sy, u, 8 * uy);
  }
}

function render(ctx: CanvasRenderingContext2D) {
  const scaledW = VIEW_W * PLAYER_SCALE;
  const scaledH = Math.round(VIEW_H * PLAYER_SCALE * PLAYER_ASPECT_SCALE);
  ctx.fillStyle = '#000';
  ctx.fillRect(0, 0, scaledW, scaledH);
  if (!gameStarted || levels.length === 0) return;

  const world = lw();
  const W = world.pixelWidth;
  const H = world.pixelHeight;

  // Prince-centred camera — never clamped: the torus wraps instead (L_5EE2).
  // INTEGER world pixels only: the STIC has no fractional scroll, and a
  // fractional source rect makes nearest-neighbour resampling redistribute
  // tile rows every frame (background "dances" sideways during vertical
  // scroll — owner-reported wiggle). All draw positions quantize likewise.
  const camX = wrap(Math.floor(state.x) + 4 - VIEW_W / 2, W);
  const camY = wrap(Math.floor(state.y) + 4 - VIEW_H / 2, H);

  // Blit the level in up to 4 pieces across the wrap seams.
  const canvas = world.canvas;
  if (canvas) {
    ctx.imageSmoothingEnabled = false;
    const w1 = Math.min(VIEW_W, W - camX);
    const w2 = VIEW_W - w1;
    const h1 = Math.min(VIEW_H, H - camY);
    const h2 = VIEW_H - h1;
    const SX = PLAYER_SCALE;
    const SY = PLAYER_SCALE * PLAYER_ASPECT_SCALE;
    ctx.drawImage(canvas, camX, camY, w1, h1, 0, 0, w1 * SX, h1 * SY);
    if (w2 > 0) ctx.drawImage(canvas, 0, camY, w2, h1, w1 * SX, 0, w2 * SX, h1 * SY);
    if (h2 > 0) ctx.drawImage(canvas, camX, 0, w1, h2, 0, h1 * SY, w1 * SX, h2 * SY);
    if (w2 > 0 && h2 > 0) ctx.drawImage(canvas, 0, 0, w2, h2, w1 * SX, h1 * SY, w2 * SX, h2 * SY);
  }

  // World point → screen offset (wrap-aware; margin lets sprites straddle edges)
  const MARGIN = 24;
  const offX = (wx: number) => {
    let d = wrap(Math.floor(wx) - camX, W);
    if (d > W - MARGIN) d -= W;
    return d;
  };
  const offY = (wy: number) => {
    let d = wrap(Math.floor(wy) - camY, H);
    if (d > H - MARGIN) d -= H;
    return d;
  };
  const toScreenX = (wx: number) => offX(wx) * PLAYER_SCALE;
  const toScreenY = (wy: number) => offY(wy) * PLAYER_SCALE * PLAYER_ASPECT_SCALE;
  const onScreen = (wx: number, wy: number) => {
    const dx = offX(wx);
    const dy = offY(wy);
    return dx > -MARGIN && dx < VIEW_W + MARGIN && dy > -MARGIN && dy < VIEW_H + MARGIN;
  };

  // --- Items: every ROM object is a background tile already in the level
  //     canvas; only the Crown (not yet captured) is drawn as a sprite ---
  const ITEM_COLORS: Record<ItemKind, string> = {
    key: '#FAEA50', potion: '#FF4E57', scroll: '#FFFCFF', crown: '#FAEA50',
  };
  for (const item of itemsByLevel[state.level]) {
    if (item.collected || !onScreen(item.x, item.y)) continue;
    const color = (item.kind === 'crown' && Math.floor(frameCount / 10) % 2 === 0)
      ? '#FFFCFF' : ITEM_COLORS[item.kind];
    drawBitmap(ctx, ITEM_SPRITES[item.kind], 8, toScreenX(item.x), toScreenY(item.y), color);
  }

  // --- Stairs transition (captured): row 5 of the frozen screen is cleared
  //     to black and "Stairs to level N" printed in RED from column 2; the
  //     Prince is hidden. Nothing else changes for 226 frames. ---
  if (transition) {
    const u = PLAYER_SCALE;
    const uy = PLAYER_SCALE * PLAYER_ASPECT_SCALE;
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, Math.round(5 * TILE * uy), VIEW_W * u, Math.round(TILE * uy));
    for (let i = 0; i < transition.text.length; i++) {
      const card = transition.text.charCodeAt(i) - 32;
      const bytes = Array.from(gromData.subarray(card * 8, card * 8 + 8));
      drawBitmap(ctx, bytes, 8, (2 + i) * TILE * u, Math.round(5 * TILE * uy), FG[2]);
    }
  }

  // --- Enemies ---
  for (const enemy of enemiesByLevel[state.level]) {
    if (!enemy.alive) continue;
    const visible = enemy.type === 'serpent'
      ? (onScreen(enemy.x, enemy.y) || onScreen(enemy.x + SERPENT_W - 8, enemy.y + SERPENT_H - 8))
      : onScreen(enemy.x, enemy.y);
    if (!visible) continue;
    const ex = toScreenX(enemy.x);
    const ey = toScreenY(enemy.y);
    const flash = enemy.hitCd > 0 && Math.floor(frameCount / 3) % 2 === 0;

    if (enemy.type === 'phantom_knight') {
      // The player's own knight figure in BLACK in one of 16 captured poses
      // (body frame + sword MOB offset/bitmap, finding #11), sweeping ±1
      // sixteenth around its charge direction. A slain knight plays a
      // captured death flash (black → white → blue) before vanishing.
      const pose = KNIGHT_POSES[knightPoseSector(enemy)];
      const bytes = playerSprites[pose.frame];
      let color = '#000000';
      if (enemy.dying > 0) color = ['#FFFCFF', '#002DFF', '#000000'][Math.floor(frameCount / 4) % 3];
      else if (flash) color = '#FFFCFF';
      if (bytes) drawBitmap(ctx, bytes, 16, ex, ey, color, pose.mirror, pose.flip);
      drawBitmap(ctx, SWORD_BITMAPS[pose.sword], 16,
        toScreenX(enemy.x + pose.sx), toScreenY(enemy.y + pose.sy), color, pose.smirror, pose.sflip);
    } else if (enemy.type === 'sorcerer') {
      // Captured: white materialise poses → red body (fires once) → white
      // body → dematerialise poses.
      if (enemy.phase === 'hidden') continue;
      let bytes: number[] = SORCERER_BODY;
      let color = FG[7];
      if (enemy.phase === 'appearing') bytes = SORCERER_MATERIALISE[sorcererAppearPose(enemy.phaseTimer)];
      else if (enemy.phase === 'active') color = flash ? FG[7] : FG[2];
      else { const p = sorcererVanishPose(enemy.phaseTimer); if (p >= 0) bytes = SORCERER_MATERIALISE[p]; }
      drawBitmap(ctx, bytes, 16, ex, ey, color);
    } else if (enemy.type === 'serpent') {
      const color = flash ? '#FFFCFF' : '#00A756';
      const tw = TILE * PLAYER_SCALE;
      const th = TILE * PLAYER_SCALE * PLAYER_ASPECT_SCALE;
      for (const cell of SERPENT_LAYOUT) {
        const sx = toScreenX(enemy.x + cell.c * TILE);
        const sy = toScreenY(enemy.y + cell.r * TILE);
        ctx.fillStyle = cell.bg;
        ctx.fillRect(sx, sy, tw, th);
        const bytes = Array.from(gramData.subarray(cell.card * 8, cell.card * 8 + 8));
        drawBitmap(ctx, bytes, 8, sx, sy, color);
      }
      ctx.fillStyle = '#FF3D10';
      for (let h = 0; h < enemy.hp; h++) {
        ctx.fillRect(ex + h * 6, ey - 10, 4, 4);
      }
    }
  }

  // --- Fireballs ---
  for (const fb of fireballs) {
    if (!fb.alive || !onScreen(fb.x, fb.y)) continue;
    // Captured: 3 bitmaps every 4 frames; yellow/orange alternating ~5 frames.
    const frame = FIREBALL_FRAMES[Math.floor(fb.age / 4) % 3];
    drawBitmap(ctx, frame, 16, toScreenX(fb.x), toScreenY(fb.y),
      Math.floor(fb.age / 5) % 2 === 0 ? FG[6] : '#FFB41F');
  }

  // --- Death effects ---
  for (const fx of deathFx) {
    if (!onScreen(fx.x, fx.y)) continue;
    const frame = SPAWN_EFFECT[fx.t > 12 ? 0 : 1];
    drawBitmap(ctx, frame, 16, toScreenX(fx.x), toScreenY(fx.y), '#FF3D10');
  }

  const px = toScreenX(state.x);
  const py = toScreenY(state.y);

  // --- Status screen (captured layout: keypad 0, black screen, game font) ---
  if (statusTimer > 0) {
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, scaledW, scaledH);
    ctx.fillStyle = '#FFFCFF';
    ctx.font = `bold ${PLAYER_SCALE * 7}px monospace`;
    ctx.textAlign = 'left';
    const row = (r: number) => Math.round((r * 8 + 7) * PLAYER_SCALE * PLAYER_ASPECT_SCALE);
    const col = (c: number) => c * 8 * PLAYER_SCALE;
    ctx.fillText('REINCARNATIONS', col(2), row(2));
    ctx.fillText(`KNIGHT:  ${state.reincarnations}`, col(4), row(3));
    ctx.fillText('TREASURES', col(2), row(6));
    ctx.fillText(`INHAND: ${state.potions}`, col(4), row(7));
    ctx.fillText(`STORED: ${state.stored}`, col(4), row(8));
    ctx.fillText(` VALUE: ${state.storedValue}`, col(4), row(9));
    return;
  }

  // --- Win screen ---
  if (gameWon) {
    ctx.fillStyle = 'rgba(0,0,0,0.6)';
    ctx.fillRect(0, 0, scaledW, scaledH);
    ctx.fillStyle = '#FAEA50';
    ctx.font = 'bold 26px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('THE CROWN OF KINGS IS YOURS!', scaledW / 2, scaledH / 2 - 20);
    ctx.fillStyle = '#FFF';
    ctx.font = 'bold 14px monospace';
    ctx.fillText(`Foes slain: ${kills}   Reincarnations left: ${state.reincarnations}`, scaledW / 2, scaledH / 2 + 12);
    ctx.font = '12px monospace';
    ctx.fillStyle = '#888';
    ctx.fillText('Refresh to quest again', scaledW / 2, scaledH / 2 + 36);
    ctx.textAlign = 'left';
    return;
  }

  // --- Game over screen ---
  if (isGameOver(state)) {
    ctx.fillStyle = '#FF3D10';
    ctx.font = 'bold 28px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('GAME OVER', scaledW / 2, scaledH / 2);
    ctx.fillStyle = '#FFF';
    ctx.font = 'bold 13px monospace';
    ctx.fillText(`Foes slain: ${kills}`, scaledW / 2, scaledH / 2 + 24);
    ctx.textAlign = 'left';
    return;
  }

  // --- Player (always at screen centre — the world scrolls around him) ---
  if (transition) {
    // MOB 0 is hidden for the whole stairs message (captured).
  } else if (state.dead) {
    if (Math.floor(frameCount / 8) % 2 === 0) {
      ctx.strokeStyle = '#FF3D10';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(px, py); ctx.lineTo(px + PLAYER_WIDTH, py + PLAYER_WIDTH);
      ctx.moveTo(px + PLAYER_WIDTH, py); ctx.lineTo(px, py + PLAYER_WIDTH);
      ctx.stroke();
    }
  } else {
    const facingF = facingFrame(state.faceDx, state.faceDy);
    const spriteBytes = playerSprites[facingF.frame];
    // Captured: while stunned by a HIT (40 frames) the body colour cycles
    // through the palette every ~2 frames; steady colour is white, or GRAY
    // once injured. The 21-frame pickup lock does not flash.
    const hitFlash = state.stunned > 0 && pickupFlash < 0;
    const playerColor = hitFlash
      ? STUN_CYCLE[Math.floor(frameCount / 2) % STUN_CYCLE.length]
      : (state.injured ? '#BDACC8' : '#FFFCFF');
    if (spriteBytes) {
      drawBitmap(ctx, spriteBytes, 16, px, py, playerColor, facingF.mirror, facingF.flip);
    }
  }

  // Sword — the player's own sword MOB. Captured: it cycles through the
  // palette every frame, always (a rainbow shimmer), independent of state.
  if (!state.dead && !transition) {
    drawSword(ctx, px, py, state.faceDx, state.faceDy, SWORD_CYCLE[frameCount % SWORD_CYCLE.length]);
  }

  // --- HUD ---
  const health = state.dead ? 'DEAD' : state.injured ? 'GRAY' : 'WHITE';

  ctx.fillStyle = 'rgba(0,0,0,0.7)';
  ctx.fillRect(0, 0, scaledW, 20);
  ctx.fillStyle = '#FFF';
  ctx.font = 'bold 11px monospace';
  ctx.fillText(`Level ${state.level + 1}/4  ❤${state.reincarnations}  HP:${health}`, 8, 14);
  ctx.fillText(`🔑${state.keys}  💰${state.potions}/${MAX_IN_HAND} (${state.stored} stored, ${state.storedValue}pts)  📜${state.scrolls}  ⚔${kills}`, 250, 14);

  if (infoTimer > 0) {
    ctx.fillStyle = '#FAEA50';
    ctx.font = 'bold 13px monospace';
    ctx.textAlign = 'center';
    ctx.fillText(infoMessage, scaledW / 2, 54);
    ctx.textAlign = 'left';
  }

  if (frameCount < 600) {
    const alpha = Math.max(0, 1 - (frameCount / 600));
    ctx.fillStyle = `rgba(200,200,200,${alpha * 0.5})`;
    ctx.font = '10px monospace';
    ctx.fillText('WASD move | walk INTO foes to strike | ENTER picks up / opens the stairs | slay the Serpent', 8, scaledH - 8);
  }

  const debugEl = document.getElementById('debug');
  if (debugEl) {
    debugEl.textContent =
      `level=${state.level} pos=(${state.x.toFixed(0)},${state.y.toFixed(0)}) ` +
      `enemies=${enemiesByLevel[state.level].filter(e => e.alive).length} ` +
      `items=${itemsByLevel[state.level].filter(i => !i.collected).length} ` +
      `kills=${kills} won=${gameWon}`;
  }
}

// Fixed 60Hz timestep — all speeds/timers are tuned in px-per-frame at 60fps,
// so the simulation must not scale with the display refresh rate.
const STEP_MS = 1000 / 60;
let lastTime = 0;
let accum = 0;

function gameLoop(ctx: CanvasRenderingContext2D, now: number) {
  if (lastTime === 0) lastTime = now;
  accum += Math.min(now - lastTime, 250); // clamp long tab-away gaps
  lastTime = now;
  while (accum >= STEP_MS) {
    update();
    accum -= STEP_MS;
  }
  render(ctx);
  requestAnimationFrame(t => gameLoop(ctx, t));
}

async function main() {
  console.log('Loading Swords and Serpents (4 real fortress levels, 128×64 each)...');
  const assets = await loadAssets();
  gramData = assets.gram;
  gromData = assets.grom;
  mazes = assets.mazes;
  extractSerpentLair();

  levels = mazes.map(m => new LevelWorld(m));
  for (const world of levels) world.build(gramData, assets.grom);
  console.log(`Built ${levels.length} wrap-around levels (${levels[0].pixelWidth}×${levels[0].pixelHeight} px each)`);

  const canvas = document.getElementById('game') as HTMLCanvasElement;
  if (!canvas) { console.error('Canvas not found!'); return; }
  const ctx = canvas.getContext('2d')!;
  canvas.width = VIEW_W * PLAYER_SCALE;
  canvas.height = Math.round(VIEW_H * PLAYER_SCALE * PLAYER_ASPECT_SCALE);

  initGame();
  requestAnimationFrame(t => gameLoop(ctx, t));
  console.log(`Quest started — ${enemiesByLevel.flat().length} foes across ${levels.length} levels.`);

  // Debug/test bridge (headless verification — see docs/HANDOVER.md)
  (window as unknown as Record<string, unknown>).__game = {
    getState: () => ({ ...state, gameWon, kills,
      enemies: enemiesByLevel[state.level].filter(e => e.alive).length,
      fireballs: fireballs.length,
      items: itemsByLevel[state.level].filter(i => !i.collected).length }),
    teleport: (x: number, y: number) => { state.x = x; state.y = y; },
    // Levels are entered in place (same coordinates) — like the real stairs.
    setLevel: (l: number) => {
      state.level = Math.max(0, Math.min(levels.length - 1, l));
      redrawLevel(state.level);
      fireballs = [];
    },
    giveKey: () => { objStateByLevel[state.level].taken[TYPE_KEY] = true; },
    // ROM object records of the current level (col,row,type,word).
    objects: () => objectTables.levels[state.level],
    objectState: () => objStateByLevel[state.level],
    marker: () => objectTables.levels[state.level].find(o => o.type === TYPE_MARKER) ?? null,
    upStairs: () => objectTables.levels[state.level].find(o => o.type === TYPE_UP_STAIRS) ?? null,
    tileWord: (col: number, row: number) => lw().maze.grid[row]?.[col],
    doorClock: () => doorClock,
    transition: () => transition,
    facing: (dx: number, dy: number, alt = false) => facingFrame(dx, dy, alt),
    info: () => infoMessage,
    // Deterministic stepping for headless verification: run N simulation
    // frames synchronously (rAF is paused when the tab is hidden).
    step: (n: number) => { for (let i = 0; i < n; i++) update(); },
    // Hold a key for `ms` milliseconds (resolves after release) — lets an
    // agent "play" with real input instead of teleports.
    hold: (key: string, ms: number) => new Promise<void>(resolve => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key }));
      setTimeout(() => {
        window.dispatchEvent(new KeyboardEvent('keyup', { key }));
        resolve();
      }, ms);
    }),
    stairs: () => openStairs[state.level],
    entry: () => entry0,
    nearestEnemy: () => {
      let best: Enemy | null = null;
      let bd = Infinity;
      for (const e of enemiesByLevel[state.level]) {
        if (!e.alive) continue;
        const d = tDist(state.level, e.x, e.y, state.x, state.y);
        if (d < bd) { bd = d; best = e; }
      }
      return best ? { x: best.x, y: best.y, type: best.type, dist: bd } : null;
    },
    nearestItem: () => {
      let best: GameItem | null = null;
      let bd = Infinity;
      for (const it of itemsByLevel[state.level]) {
        if (it.collected) continue;
        const d = tDist(state.level, it.x, it.y, state.x, state.y);
        if (d < bd) { bd = d; best = it; }
      }
      return best ? { x: best.x, y: best.y, kind: best.kind, dist: bd } : null;
    },
    sorcerers: () => enemiesByLevel[state.level]
      .filter(e => e.type === 'sorcerer' && e.alive)
      .map(e => ({ x: e.x, y: e.y, phase: e.phase, pt: e.phaseTimer, ft: e.fireTimer, vt: e.visibleTimer,
        dist: tDist(state.level, e.x, e.y, state.x, state.y) }))
      .sort((a, b) => a.dist - b.dist)
      .slice(0, 3),
    serpent: () => {
      const d = enemiesByLevel[levels.length - 1].find(e => e.type === 'serpent');
      return d ? { x: d.x, y: d.y, hp: d.hp, alive: d.alive } : null;
    },
    crown: () => {
      const c = itemsByLevel[levels.length - 1].find(i => i.kind === 'crown');
      return c ? { x: c.x, y: c.y, collected: c.collected } : null;
    },
    probe: (x: number, y: number) => lw().canWalk(x, y),
    rowMap: (r0: number, r1: number) => {
      const m = lw().maze;
      const out: string[] = [];
      for (let r = r0; r <= r1; r++) {
        let line = '';
        for (let c = 0; c < m.w; c++) {
          line += isWalkableWord(m.grid[wrap(r, m.h)]?.[c] ?? 0) ? '.' : '#';
        }
        out.push(`${r}: ${line}`);
      }
      return out;
    },
  };
}

main().catch(console.error);
