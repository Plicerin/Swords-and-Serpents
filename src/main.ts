import { WIDTH, HEIGHT } from './platform/stic';
import { createInitialState, PlayerState } from './engine/state';
import { InputHandler } from './engine/input';
import { Maze, isWalkableWord } from './world/maze';
import { LevelWorld, wrap, wrapDelta, TILE } from './world/torus';
import {
  Enemy, Fireball, GameItem, ItemKind,
  createEnemy, createItem, updateEnemy, resolveContact,
  injurePlayer, tickPlayerCombat, isGameOver,
  SORCERER_SPRITES, SERPENT_W, SERPENT_H,
  FIREBALL_FRAMES, SPAWN_EFFECT, ITEM_SPRITES,
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

// --- Per-level world content ---
interface Stairs { x: number; y: number; unlocked: boolean; }
interface DeathFx { x: number; y: number; t: number; }

let enemiesByLevel: Enemy[][] = [];
let itemsByLevel: GameItem[][] = [];
let stairsByLevel: (Stairs | null)[] = [];
let entryByLevel: { x: number; y: number }[] = [];
let fireballs: Fireball[] = [];
let deathFx: DeathFx[] = [];
let kills = 0;

const PLAYER_SCALE = 4;
const PLAYER_ASPECT_SCALE = 1.25;
const PLAYER_WIDTH = 8 * PLAYER_SCALE;
const VIEW_W = WIDTH;
const VIEW_H = HEIGHT;
const MOVE_SPEED = 0.25;

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

// A/B flag for OPEN BUG #1: `?anim=1` re-enables the knight-style F4/F3
// vertical walk animation on the PLAYER. Default is static — the owner
// reports the real game's player does not wiggle vertically, and player
// animation is unverifiable in the emulator (no input injection).
const PLAYER_VERTICAL_ANIM = new URLSearchParams(location.search).has('anim');

const lw = (): LevelWorld => levels[state.level];

// Facing — from angle-binned live captures of the game's own display logic
// (traces/capture_facing_long_out.txt, ±15° sectors):
//   E:  frame 0 unflipped (static — the 455-sample pure-W chase shows NO
//   W:  frame 0 xflip+yflip        walk alternates on E/W)
//   N:  frame 4 X-FLIPPED, walk-alt frame 3
//   S:  frame 4 Y-FLIPPED, walk-alt frame 3 (y-flipped)
//   NE: frame 1 unflipped   (captured: F1(0,0) during NE-ward movement)
//   SE: frame 1 y-flipped   (captured: F1(0,1) during SE-ward movement)
//   NW: frame 1 x-flipped   ┐ derived by the game's own mirror convention
//   SW: frame 1 xy-flipped  ┘ (identical to how W mirrors E)
// F1 is visually the 3/4 NE-facing helm; F2 remains unused in-dungeon.
// Vertical walk cycle (captured sequence, e.g. `4y 4y 3xy 3xy 4y 4y 3y ...`):
// F4 and F3 alternate in ~5-frame phases (50/50), and F3's x-flip wobbles
// between cycles. Horizontal movement is static (455-sample W run, no alts).
function facingFrame(dx: number, dy: number, moving = false): { frame: number; mirror: boolean; flip: boolean } {
  const ax = Math.abs(dx);
  const ay = Math.abs(dy);
  if (ax > 0 && ay > 0 && Math.min(ax, ay) / Math.max(ax, ay) > 0.414) {
    // within ±22.5° of a diagonal
    return { frame: 1, mirror: dx < 0, flip: dy > 0 };
  }
  if (ax >= ay && ax > 0) {
    return { frame: 0, mirror: dx < 0, flip: dx < 0 };
  }
  if (ay > 0) {
    if (moving && Math.floor(frameCount / 5) % 2 === 1) {
      // F3 walk phase — flips are CONSTANT per direction (dominant captured
      // variants: N = F3 unflipped, S = F3 y-flip only). An x-flip "rock"
      // reads as left-right wiggle and is wrong.
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

  const [gramRes, gromRes, spritesRes, ...mazeResps] = await Promise.all([
    fetch('/assets/gram_tiles.json'),
    fetch('/assets/grom.bin'),
    fetch('/assets/player_sprites.json'),
    ...levelUrls,
  ]);

  const gramArray = await gramRes.json() as number[];
  const gromBuffer = await gromRes.arrayBuffer();
  const spritesData = await spritesRes.json() as { warrior: number[][] };
  playerSprites = spritesData.warrior;

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

// Scatter enemies, items, and the key-gated stairway across each toroidal
// level; the Serpent and the Crown of Kings wait on the last one.
function populateWorld(rand: () => number) {
  enemiesByLevel = [];
  itemsByLevel = [];
  stairsByLevel = [];
  entryByLevel = [];
  fireballs = [];
  deathFx = [];
  kills = 0;

  // Level 0 entry: the ROM boots with camera (2, $1A) → the Prince stands
  // near tile (12, 32).
  entryByLevel.push(findWalkableNear(0, 12 * TILE, 32 * TILE));

  for (let i = 0; i < mazes.length; i++) {
    const m = mazes[i];
    const entry = entryByLevel[i];
    const enemies: Enemy[] = [];
    const items: GameItem[] = [];

    const spots: { x: number; y: number }[] = [];
    for (let r = 0; r < m.h; r++) {
      for (let c = 0; c < m.w; c++) {
        if (!isWalkableWord(m.grid[r][c])) continue;
        const s = { x: c * TILE, y: r * TILE };
        if (tDist(i, s.x, s.y, entry.x, entry.y) < 60) continue; // keep the entry safe
        spots.push(s);
      }
    }
    const take = (): { x: number; y: number } | null => {
      if (spots.length === 0) return null;
      return spots.splice(Math.floor(rand() * spots.length), 1)[0];
    };
    const takeFar = (minDist: number): { x: number; y: number } | null => {
      for (let attempt = 0; attempt < 40; attempt++) {
        const idx = Math.floor(rand() * spots.length);
        const s = spots[idx];
        if (s && tDist(i, s.x, s.y, entry.x, entry.y) >= minDist) {
          return spots.splice(idx, 1)[0];
        }
      }
      return take();
    };

    // Phantom knights — more as you descend (2/4/6/8 across the 4 levels).
    const knightCount = 2 + i * 2;
    for (let k = 0; k < knightCount; k++) {
      const p = take();
      if (p) enemies.push(createEnemy(p.x, p.y, 'phantom_knight'));
    }

    // Red Sorcerers from level 2 down.
    const sorcererCount = i === 0 ? 0 : i;
    for (let w = 0; w < sorcererCount; w++) {
      const p = take();
      if (p) enemies.push(createEnemy(p.x, p.y, 'sorcerer'));
    }

    // Items: potions, scrolls — and the key that opens this level's stairway.
    for (let n = 0; n < 3; n++) {
      const p = take();
      if (p) items.push(createItem(p.x, p.y, 'potion'));
    }
    if (i >= 1) {
      const p = take();
      if (p) items.push(createItem(p.x, p.y, 'scroll'));
    }

    if (i < mazes.length - 1) {
      const p = take();
      if (p) items.push(createItem(p.x, p.y, 'key'));
      const sp = takeFar(100);
      stairsByLevel.push(sp ? { x: sp.x, y: sp.y, unlocked: false } : null);
      // Next level's entry: descend "in place" — same coordinates, snapped to floor.
      const stair = stairsByLevel[i];
      entryByLevel.push(stair ? findWalkableNear(i + 1, stair.x, stair.y) : { x: entry.x, y: entry.y });
    } else {
      stairsByLevel.push(null);
      // The Serpent's lair at its REAL position from the level-3 map data
      // (the ziggurat chamber); the Crown of Kings lies behind its tail.
      if (serpentLair) {
        enemies.push(createEnemy(serpentLair.x, serpentLair.y, 'serpent'));
        const cpos = findWalkableNear(i, serpentLair.x + SERPENT_W + 16, serpentLair.y + 8);
        items.push(createItem(cpos.x, cpos.y, 'crown'));
      }
    }

    enemiesByLevel.push(enemies);
    itemsByLevel.push(items);
  }
}

function descend() {
  if (state.level >= levels.length - 1) return;
  state.level++;
  const entry = entryByLevel[state.level];
  state.x = entry.x;
  state.y = entry.y;
  state.invuln = Math.max(state.invuln, 60);
  fireballs = [];
  setInfo(`Level ${state.level + 1} — the air grows colder...`, 180);
}

function initGame() {
  state = createInitialState();
  input = new InputHandler();

  populateWorld(mulberry32(0x5E44E27));

  state.level = 0;
  state.x = entryByLevel[0].x;
  state.y = entryByLevel[0].y;

  gameWon = false;
  gameStarted = true;
  setInfo('Slay foes by walking INTO them. Find the key, then the stairs (F)!', 420);
}

function update() {
  if (!gameStarted || levels.length === 0) return;
  frameCount++;
  if (infoTimer > 0) infoTimer--;

  if (gameWon || isGameOver(state)) return;

  const world = lw();
  const W = world.pixelWidth;
  const H = world.pixelHeight;
  const inputState = input.getInput();

  const respawned = tickPlayerCombat(state);
  if (respawned) {
    const entry = entryByLevel[state.level];
    state.x = entry.x;
    state.y = entry.y;
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

  // --- Stairway ---
  const stairs = stairsByLevel[state.level];
  if (stairs && !state.dead && tDist(state.level, state.x, state.y, stairs.x, stairs.y) < 8) {
    if (!stairs.unlocked) {
      if (state.keys > 0) {
        state.keys--;
        stairs.unlocked = true;
        setInfo('The stairway is unlocked — press F to descend', 180);
      } else if (infoTimer < 30) {
        setInfo('The stairway is barred — find a key!', 60);
      }
    } else if (inputState.stairs) {
      descend();
    } else if (infoTimer < 30) {
      setInfo('Press F to descend', 60);
    }
  }

  // --- Enemies (current level only; targets use shortest torus path) ---
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
      deathFx.push({ x: enemy.x, y: enemy.y, t: 24 });
      if (enemy.type === 'serpent') setInfo('THE SERPENT IS SLAIN! Claim the Crown!', 300);
      else if (enemy.type === 'sorcerer') setInfo('Red Sorcerer vanquished!', 90);
      else setInfo('Phantom Knight slain!', 90);
    } else if (event === 'player_strikes') {
      setInfo('You wound the Serpent!', 90);
    } else if (event === 'player_injured') {
      if (state.invuln === 0 && !state.dead) {
        injurePlayer(state);
        setInfo(state.dead ? 'You have fallen...' : 'Injured! Strike back or flee!', 90);
      }
    }
  }

  // --- Fireballs (MOBs — no wall test in the ROM; range-limited instead) ---
  for (const fb of fireballs) {
    if (!fb.alive) continue;
    fb.age++;
    fb.x = wrap(fb.x + fb.dx * fb.speed, W);
    fb.y = wrap(fb.y + fb.dy * fb.speed, H);
    if (fb.age > 200) { // ~one screen of travel at 0.8 px/frame
      fb.alive = false;
      continue;
    }
    if (!state.dead && tDist(state.level, fb.x, fb.y, state.x, state.y) < 5) {
      fb.alive = false;
      if (state.invuln === 0) {
        injurePlayer(state);
        setInfo(state.dead ? 'Burned down...' : 'Scorched by a fireball!', 90);
      }
    }
  }
  fireballs = fireballs.filter(fb => fb.alive);

  // --- Death effects ---
  for (const fx of deathFx) fx.t--;
  deathFx = deathFx.filter(fx => fx.t > 0);

  // --- Items ---
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
        item.collected = true;
        gameWon = true;
        setInfo('', 0);
        continue;
      }
      item.collected = true;
      switch (item.kind) {
        case 'key':    state.keys++;    setInfo('Found a key!', 90); break;
        case 'potion': state.potions++; setInfo('Found a potion!', 90); break;
        case 'scroll': state.scrolls++; setInfo('Found a scroll — press R to read', 120); break;
      }
    }
  }

  // Read scroll
  if (inputState.readScroll && state.scrolls > 0 && infoTimer < 30) {
    setInfo('The scroll reads: "The Serpent guards the Crown in the deepest dark..."', 240);
  }

  // Auto-use a potion when injured
  if (state.injured && !state.dead && state.potions > 0 && state.stunned === 0) {
    state.potions--;
    state.injured = false;
    setInfo('Used a potion — healed!', 90);
  }
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
// $10 column (vertical), or a 45° blade for diagonals (rows $06 $0C $30 $60
// $C0, NE-pointing, y-flipped for SE, offset (+8,∓2) from the body — captured
// live during F1 diagonal frames in traces/capture_facing_long_out.txt;
// cardinals from traces/capture_attack_anim_out.txt cards 50/54/58).
const DIAG_SWORD: number[] = [
  0x00, 0x00, 0x00, 0x00, 0x00, 0x06, 0x0C, 0x30,
  0x60, 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
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
    // diagonal blade: (+8, -2) for NE, y-offset +2 when facing south
    const sx = px + (dirX > 0 ? 8 : -8) * u;
    const sy = py + (dirY > 0 ? 2 : -2) * uy;
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

  // --- Stairway ---
  const stairs = stairsByLevel[state.level];
  if (stairs && onScreen(stairs.x, stairs.y)) {
    const sx = toScreenX(stairs.x);
    const sy = toScreenY(stairs.y);
    const u = PLAYER_SCALE;
    const uy = PLAYER_SCALE * PLAYER_ASPECT_SCALE;
    // Descending steps
    ctx.fillStyle = stairs.unlocked ? '#FFFCFF' : '#BDACC8';
    ctx.fillRect(sx,         sy,          u * 8, uy * 2);
    ctx.fillRect(sx + u * 2, sy + uy * 2, u * 6, uy * 2);
    ctx.fillRect(sx + u * 4, sy + uy * 4, u * 4, uy * 2);
    ctx.fillRect(sx + u * 6, sy + uy * 6, u * 2, uy * 2);
    if (!stairs.unlocked) {
      ctx.fillStyle = '#FFB41F';
      ctx.fillRect(sx, sy + uy * 3, u * 8, uy);
    }
  }

  // --- Items ---
  const ITEM_COLORS: Record<ItemKind, string> = {
    key: '#FAEA50', potion: '#FF4E57', scroll: '#FFFCFF', crown: '#FAEA50',
  };
  for (const item of itemsByLevel[state.level]) {
    if (item.collected || !onScreen(item.x, item.y)) continue;
    const color = (item.kind === 'crown' && Math.floor(frameCount / 10) % 2 === 0)
      ? '#FFFCFF' : ITEM_COLORS[item.kind];
    drawBitmap(ctx, ITEM_SPRITES[item.kind], 8, toScreenX(item.x), toScreenY(item.y), color);
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
      // The player's own knight figure in BLACK, facing its chase direction,
      // with its black sword MOB in front.
      const kdx = wrapDelta(enemy.x, state.x, W);
      const kdy = wrapDelta(enemy.y, state.y, H);
      const f = facingFrame(kdx, kdy, true);
      const bytes = playerSprites[f.frame];
      const color = flash ? '#FFFCFF' : '#000000';
      if (bytes) drawBitmap(ctx, bytes, 16, ex, ey, color, f.mirror, f.flip);
      drawSword(ctx, ex, ey, kdx, kdy, color);
    } else if (enemy.type === 'sorcerer') {
      if (enemy.phase === 'hidden') continue;
      const blink = (enemy.phase === 'appearing' || enemy.phase === 'vanishing')
        && Math.floor(frameCount / 4) % 2 === 0;
      if (blink) continue;
      const frame = SORCERER_SPRITES[Math.floor(frameCount / 12) % 2];
      drawBitmap(ctx, frame, 16, ex, ey, flash ? '#FFFCFF' : '#FF3D10');
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
    const frame = FIREBALL_FRAMES[Math.floor(fb.age / 6) % 4];
    drawBitmap(ctx, frame, 8, toScreenX(fb.x), toScreenY(fb.y),
      Math.floor(fb.age / 4) % 2 === 0 ? '#FFB41F' : '#FAEA50');
  }

  // --- Death effects ---
  for (const fx of deathFx) {
    if (!onScreen(fx.x, fx.y)) continue;
    const frame = SPAWN_EFFECT[fx.t > 12 ? 0 : 1];
    drawBitmap(ctx, frame, 16, toScreenX(fx.x), toScreenY(fx.y), '#FF3D10');
  }

  const px = toScreenX(state.x);
  const py = toScreenY(state.y);

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
  if (state.dead) {
    if (Math.floor(frameCount / 8) % 2 === 0) {
      ctx.strokeStyle = '#FF3D10';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(px, py); ctx.lineTo(px + PLAYER_WIDTH, py + PLAYER_WIDTH);
      ctx.moveTo(px + PLAYER_WIDTH, py); ctx.lineTo(px, py + PLAYER_WIDTH);
      ctx.stroke();
    }
  } else {
    const visible = state.invuln === 0 || Math.floor(frameCount / 4) % 2 === 0;
    const facingF = facingFrame(state.faceDx, state.faceDy, PLAYER_VERTICAL_ANIM && state.moving);
    const spriteBytes = playerSprites[facingF.frame];
    const playerColor = state.injured ? '#BDACC8' : '#FFFCFF';
    if (visible && spriteBytes) {
      drawBitmap(ctx, spriteBytes, 16, px, py, playerColor, facingF.mirror, facingF.flip);
    }
  }

  // Sword — the player's own sword MOB (axis-aligned, white like the Prince)
  if (!state.dead) {
    const playerColor = state.injured ? '#BDACC8' : '#FFFCFF';
    drawSword(ctx, px, py, state.faceDx, state.faceDy, playerColor);
  }

  // --- HUD ---
  const health = state.dead ? 'DEAD' : state.injured ? 'GRAY' : 'WHITE';

  ctx.fillStyle = 'rgba(0,0,0,0.7)';
  ctx.fillRect(0, 0, scaledW, 20);
  ctx.fillStyle = '#FFF';
  ctx.font = 'bold 11px monospace';
  ctx.fillText(`Level ${state.level + 1}/4  ❤${state.reincarnations}  HP:${health}`, 8, 14);
  ctx.fillText(`🔑${state.keys}  🧪${state.potions}  📜${state.scrolls}  ⚔${kills}`, 280, 14);

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
    ctx.fillText('WASD move | walk INTO foes to strike | key opens the stairs (F) | slay the Serpent', 8, scaledH - 8);
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
    setLevel: (l: number) => {
      state.level = Math.max(0, Math.min(levels.length - 1, l));
      const entry = entryByLevel[state.level];
      state.x = entry.x;
      state.y = entry.y;
      fireballs = [];
    },
    giveKey: () => { state.keys++; },
    facing: (dx: number, dy: number, alt = false) => facingFrame(dx, dy, alt),
    info: () => infoMessage,
    // Hold a key for `ms` milliseconds (resolves after release) — lets an
    // agent "play" with real input instead of teleports.
    hold: (key: string, ms: number) => new Promise<void>(resolve => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key }));
      setTimeout(() => {
        window.dispatchEvent(new KeyboardEvent('keyup', { key }));
        resolve();
      }, ms);
    }),
    stairs: () => stairsByLevel[state.level],
    entry: () => entryByLevel[state.level],
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
