import { PlayerState } from './state';

export type EnemyType = 'phantom_knight' | 'sorcerer' | 'serpent';

export interface Enemy {
  x: number;
  y: number;
  type: EnemyType;
  alive: boolean;
  hp: number;               // strikes needed to kill (1 except the dragon)
  hitCd: number;            // frames of post-strike grace (multi-hit enemies)
  homeX: number;            // spawn point (dragon guards it)
  homeY: number;
  // facing (unit-ish vector) — knights hold their sword ~8 px ahead along this.
  faceDx: number;
  faceDy: number;
  // Knight charge (finding #11): straight-line velocity in px/frame, re-aimed
  // at the player every KNIGHT_REAIM_TICKS; `aimTimer` counts down to it.
  vx: number;
  vy: number;
  aimTimer: number;
  // Sword-swing sweep: 16-direction sector of the charge, and the sweep phase
  // clock (pose = sector, sector+1, sector, sector-1 — 15 frames each).
  sector: number;
  swingClock: number;
  dying: number;            // >0: death-flash frames remaining (still drawn, harmless)
  // sorcerer-specific state (captured timeline, finding #11)
  visibleTimer: number;     // unused (kept for the bridge)
  fireTimer: number;        // serpent: frames until next breath
  phase: 'hidden' | 'appearing' | 'active' | 'vanishing';
  phaseTimer: number;       // frames elapsed in the current phase
  visits: number;           // appearances left in this visit (1 or 2)
}

export interface Fireball {
  x: number;
  y: number;
  dx: number;
  dy: number;
  speed: number;
  alive: boolean;
  age: number;
}

export interface GameItem {
  x: number;
  y: number;
  kind: 'key' | 'potion' | 'scroll' | 'crown';
  collected: boolean;
}

export type ItemKind = GameItem['kind'];

export type CanWalkFn = (x: number, y: number) => boolean;

// ---------------------------------------------------------------------------
// COMBAT — captured from the real game under real input in the Intellijsd
// oracle, reading the STIC MOB-collision registers ($0018-$001F) every
// frame (docs/HANDOVER.md ROM finding #7):
//  * Knights CHARGE in straight lines (finding #11, 2026-09-15): every 90
//    frames the velocity is re-aimed at the player's current position with
//    magnitude 30/64 px/frame (velocity components are integers in 1/64 px
//    units, e.g. (28,-11) for a 37×-15 offset). Nothing steers in between —
//    a knight overshoots ~20 px past a standing Prince, then turns back on
//    the next re-aim. The body faces the nearest of 16 directions of its
//    velocity and SWEEPS its sword pose ±1 sixteenth (see KNIGHT_POSES).
//  * Hit detection is PIXEL collision between SWORD MOBs and BODY MOBs:
//      knight-sword pixels ∩ player-body pixels  → the player is hit
//      player-sword pixels ∩ knight-body pixels  → the knight dies
//    Body-on-body overlap does NOTHING (a knight can stand exactly on the
//    player for hundreds of frames with no effect). When both swords land
//    on the same frame the player's strike wins.
//  * Being hit: hit flag G_01A3=1, movement lock G_01AB=1, timer G_01A4=40
//    frames during which the player's colour cycles through the palette
//    every 1-3 frames (the "stunned" flash). Afterwards: white (7) → GRAY
//    (8) on the first hit ("loses half a life"); a hit while gray costs a
//    reincarnation ($017C, 9 at start) and restores white. Gray never heals
//    by itself (manual: Lantern of Life / Heal spell only).
//  * A slain knight runs a short death script ($5B94): its colour flashes
//    (black→white→blue) for ~20-65 frames, then it despawns.
// ---------------------------------------------------------------------------
// TIME UNITS (finding #13): everything below counts GAME TICKS — one pass of
// the ROM main loop, ~2.7-3.7 frames each — except px/frame speeds, which
// the ROM's frame code applies every frame.
const KNIGHT_SPEED_UNITS = 30;      // captured: |v| = 30 in 1/64 px/frame ≈ 0.469 px/frame
const KNIGHT_REAIM_TICKS = 30;      // captured: re-aim every 30 ticks (90 frames at 3/tick)
export const KNIGHT_POSE_TICKS = 5; // captured: each sword pose held ~15 frames ≈ 5 ticks
const STUN_TICKS = 40;              // captured: G_01A4 = 40, decremented once per tick (~117 frames)

// 16-direction facing table (sector 0 = E, counter-clockwise with screen-y
// up, i.e. sector 4 = N, 8 = W, 12 = S). Captured from the knight's GRAM
// rewrite + MOB Y-register flip bits alongside its velocity: body frame
// F0..F4 with flips exactly like the player's own scheme, and the sword MOB
// offset/bitmap per direction:
//   h   = $FF row 7            v   = $10 column rows 2-15
//   d45 = 04 04 08 08 10 10 20 20 40 40 80 80 (rows 4-15)
//   d63 = 08 08 08 08 10 10 10 10 20 20 20 20 (rows 4-15)
//   d27 = 06 0c 30 60 c0 (rows 5-9)
export interface KnightPose { frame: number; mirror: boolean; flip: boolean; sx: number; sy: number; sword: 'h' | 'v' | 'd45' | 'd63' | 'd27'; smirror: boolean; sflip: boolean; }
export const KNIGHT_POSES: KnightPose[] = [
  { frame: 0, mirror: false, flip: false, sx:  8, sy:  0, sword: 'h',   smirror: false, sflip: false }, // E
  { frame: 1, mirror: false, flip: false, sx:  8, sy: -2, sword: 'd27', smirror: false, sflip: false }, // ENE
  { frame: 2, mirror: false, flip: false, sx:  7, sy: -7, sword: 'd45', smirror: false, sflip: false }, // NE
  { frame: 3, mirror: false, flip: false, sx:  3, sy: -8, sword: 'd63', smirror: false, sflip: false }, // NNE
  { frame: 4, mirror: true,  flip: false, sx:  0, sy: -8, sword: 'v',   smirror: true,  sflip: false }, // N
  { frame: 3, mirror: true,  flip: false, sx: -3, sy: -8, sword: 'd63', smirror: true,  sflip: false }, // NNW
  { frame: 2, mirror: true,  flip: false, sx: -7, sy: -7, sword: 'd45', smirror: true,  sflip: false }, // NW
  { frame: 1, mirror: true,  flip: false, sx: -8, sy: -2, sword: 'd27', smirror: true,  sflip: false }, // WNW
  { frame: 0, mirror: true,  flip: true,  sx: -8, sy:  0, sword: 'h',   smirror: true,  sflip: true  }, // W
  { frame: 1, mirror: true,  flip: true,  sx: -8, sy:  2, sword: 'd27', smirror: true,  sflip: true  }, // WSW
  { frame: 2, mirror: true,  flip: true,  sx: -7, sy:  7, sword: 'd45', smirror: true,  sflip: true  }, // SW
  { frame: 3, mirror: true,  flip: true,  sx: -3, sy:  8, sword: 'd63', smirror: true,  sflip: true  }, // SSW
  { frame: 4, mirror: false, flip: true,  sx:  0, sy:  8, sword: 'v',   smirror: false, sflip: true  }, // S
  { frame: 3, mirror: false, flip: true,  sx:  3, sy:  8, sword: 'd63', smirror: false, sflip: true  }, // SSE
  { frame: 2, mirror: false, flip: true,  sx:  7, sy:  7, sword: 'd45', smirror: false, sflip: true  }, // SE
  { frame: 1, mirror: false, flip: true,  sx:  8, sy:  2, sword: 'd27', smirror: false, sflip: true  }, // ESE
];
export const SWORD_BITMAPS: Record<KnightPose['sword'], number[]> = {
  h:   [0, 0, 0, 0, 0, 0, 0, 0xFF, 0, 0, 0, 0, 0, 0, 0, 0],
  v:   [0, 0, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10],
  d45: [0, 0, 0, 0, 0x04, 0x04, 0x08, 0x08, 0x10, 0x10, 0x20, 0x20, 0x40, 0x40, 0x80, 0x80],
  d63: [0, 0, 0, 0, 0x08, 0x08, 0x08, 0x08, 0x10, 0x10, 0x10, 0x10, 0x20, 0x20, 0x20, 0x20],
  d27: [0, 0, 0, 0, 0, 0x06, 0x0C, 0x30, 0x60, 0xC0, 0, 0, 0, 0, 0, 0],
};

/** Nearest 16-direction sector of a velocity (screen y down). */
export function velocitySector(vx: number, vy: number): number {
  const a = Math.atan2(-vy, vx);
  return ((Math.round(a / (Math.PI / 8)) % 16) + 16) % 16;
}

/** Current sword-swing pose sector: main, +1, main, -1 (15 frames each). */
export function knightPoseSector(enemy: Enemy): number {
  const step = Math.floor(enemy.swingClock / KNIGHT_POSE_TICKS) % 4;
  const off = [0, 1, 0, -1][step];
  return ((enemy.sector + off) % 16 + 16) % 16;
}

function aimKnight(enemy: Enemy, player: PlayerState): void {
  const dx = player.x - enemy.x;
  const dy = player.y - enemy.y;
  const dist = Math.hypot(dx, dy) || 1;
  // Integer 1/64-px components, magnitude 30 (e.g. (28,-11) captured).
  const ux = Math.round(KNIGHT_SPEED_UNITS * dx / dist);
  const uy = Math.round(KNIGHT_SPEED_UNITS * dy / dist);
  enemy.vx = ux / 64;
  enemy.vy = uy / 64;
  enemy.sector = velocitySector(ux, uy);
  enemy.aimTimer = KNIGHT_REAIM_TICKS;
}
const HIT_GRACE_TICKS = 10;        // ~30 frames
// Captured (finding #15): a slain knight runs the same $5B94 burst as the
// Prince — dot 8 ticks, sparkle 8, big burst 2-3 — with a random colour 0-7
// per tick, then despawns (19 ticks after the killing tick).
export const KNIGHT_DEATH_TICKS = 19;
export function knightDeathPose(ticksLeft: number): number {
  const t = KNIGHT_DEATH_TICKS - ticksLeft;
  return t < 8 ? 0 : t < 16 ? 1 : 2;
}
// Sword MOB is 8×16 at 2× vertical resolution: reach is ~8 px along the
// facing axis; the blade is 1 px thick on the perpendicular axis (a single
// row/column) so the perpendicular tolerance is small.
const SWORD_REACH = 8;
const SWORD_HALF_WIDTH = 3;

export const RESPAWN_INVULN = 120;

const FIREBALL_SPEED = 100 / 64;   // captured: 100 units of 1/64 px/frame

const SERPENT_HP = 6;
const SERPENT_FIRE_INTERVAL = 27;  // ticks (~80 frames); not captured
const SERPENT_FIRST_SHOT = 5;       // ticks; fires almost immediately on aggro
const SERPENT_RANGE = 110;          // fires when the player is this close

// The Serpent's body: 6 cards wide × 3 tall (GRAM cards 24-33), captured from
// the ROM's own renderer (level 3 page 2 — traces/rooms/lair_probe_out.txt):
//        [24][25][26]          (green on olive)
// [27][28][29][29][29][30]     (neck left; 29s green on RED = fiery belly; 30 = tail tip)
//        [31][32][33]          (green on olive)
export const SERPENT_W = 48;
export const SERPENT_H = 24;

export function createEnemy(x: number, y: number, type: EnemyType): Enemy {
  const isSorcerer = type === 'sorcerer';
  return {
    x, y, type, alive: true,
    hp: type === 'serpent' ? SERPENT_HP : 1,
    hitCd: 0,
    homeX: x,
    homeY: y,
    faceDx: 0,
    faceDy: -1,
    vx: 0,
    vy: 0,
    aimTimer: 0,
    sector: 0,
    swingClock: 0,
    dying: 0,
    visibleTimer: 0,
    fireTimer: type === 'serpent' ? SERPENT_FIRST_SHOT : 0,
    phase: isSorcerer ? 'appearing' : 'active',
    phaseTimer: 0,
    // Captured: half the sorcerer visits chained into a second appearance.
    visits: isSorcerer ? (Math.random() < 0.5 ? 2 : 1) : 1,
  };
}

export function createItem(x: number, y: number, kind: ItemKind): GameItem {
  return { x, y, kind, collected: false };
}

// Captured (finding #11): a sorcerer's fireball is aimed STRAIGHT at the
// player at any angle — the same normalise-to-N-units aim as the knights,
// magnitude 100/64 ≈ 1.56 px/frame — and flies through walls off screen.
function aimedFireball(ex: number, ey: number, player: PlayerState, speed: number): Fireball {
  const ddx = player.x - ex;
  const ddy = player.y - ey;
  const dist = Math.hypot(ddx, ddy) || 1;
  return { x: ex, y: ey, dx: ddx / dist, dy: ddy / dist, speed, alive: true, age: 0 };
}

// Enemies do NOT collide with walls. In the ROM, only the two player slots run
// the movement wall test (L_63F5 selects G_01AB/G_01AC by player index before
// calling L_6054); enemy MOBs are driven by animation-script velocities with
// no BACKTAB lookup — phantom knights chase straight through walls.

/** Per-FRAME motion: the ROM's frame code applies each MOB's velocity. */
export function moveEnemy(enemy: Enemy): void {
  if (!enemy.alive || enemy.dying > 0) return;
  if (enemy.type === 'phantom_knight') {
    enemy.x += enemy.vx;
    enemy.y += enemy.vy;
  }
}

/** Per-TICK decisions (the ROM main loop, finding #13). */
export function updateEnemy(enemy: Enemy, player: PlayerState, _canWalk: CanWalkFn): Fireball | null {
  if (!enemy.alive) return null;
  if (enemy.dying > 0) {
    // Death flash plays out, then the knight is removed.
    enemy.dying--;
    if (enemy.dying === 0) enemy.alive = false;
    return null;
  }
  if (enemy.hitCd > 0) enemy.hitCd--;

  if (enemy.type === 'phantom_knight') {
    // Captured: straight-line charge, re-aimed every 30 ticks, 30/64 px/frame.
    if (enemy.aimTimer <= 0) aimKnight(enemy, player);
    enemy.aimTimer--;
    enemy.swingClock++;
    // The sword hit box follows the current swing pose.
    const pose = KNIGHT_POSES[knightPoseSector(enemy)];
    enemy.faceDx = Math.sign(pose.sx);
    enemy.faceDy = Math.sign(pose.sy);
    return null;
  }

  if (enemy.type === 'serpent') {
    // The Sinister Serpent is background-tile art in the ROM (GRAM cards
    // 24-33, a 5×3-card dragon facing left) — it does not move. It lies in
    // its lair (enemy.x/y = top-left of its 40×24 px body) and breathes fire
    // from its neck tip (left end) when the player comes near.
    const cx = enemy.x + SERPENT_W / 2;
    const cy = enemy.y + SERPENT_H / 2;
    const dist = Math.max(Math.abs(player.x - cx), Math.abs(player.y - cy));
    if (dist <= SERPENT_RANGE) {
      if (enemy.fireTimer > 0) enemy.fireTimer--;
      if (enemy.fireTimer <= 0) {
        enemy.fireTimer = SERPENT_FIRE_INTERVAL;
        // Fire comes from the neck tip (middle row, left end)
        return aimedFireball(enemy.x, enemy.y + 8, player, FIREBALL_SPEED);
      }
    }
    return null;
  }

  if (enemy.type === 'sorcerer') {
    // Captured timeline (finding #11). phaseTimer counts UP within a phase.
    enemy.phaseTimer++;
    if (enemy.phase === 'appearing') {
      if (enemy.phaseTimer >= SORCERER_APPEAR) { enemy.phase = 'active'; enemy.phaseTimer = 0; }
      return null;
    }
    if (enemy.phase === 'active') {
      if (enemy.phaseTimer === SORCERER_FIRE_AT) {
        return aimedFireball(enemy.x, enemy.y, player, FIREBALL_SPEED);
      }
      if (enemy.phaseTimer >= SORCERER_RED) { enemy.phase = 'vanishing'; enemy.phaseTimer = 0; }
      return null;
    }
    if (enemy.phase === 'vanishing') {
      if (enemy.phaseTimer >= SORCERER_VANISH) {
        enemy.visits--;
        if (enemy.visits > 0) {
          // Chained appearance at a fresh spot near the player (captured
          // offsets: one of the observed spawn offsets).
          const off = SORCERER_OFFSETS[Math.floor(Math.random() * SORCERER_OFFSETS.length)];
          enemy.x = player.x + off[0];
          enemy.y = player.y + off[1];
          enemy.phase = 'appearing';
          enemy.phaseTimer = 0;
        } else {
          enemy.alive = false;
        }
      }
      return null;
    }
    return null;
  }

  return null;
}

// Observed sorcerer spawn offsets from the Prince (screen px), 6 samples:
export const SORCERER_OFFSETS: [number, number][] = [[-10, 26], [-20, 20], [-20, -20], [0, 28], [26, 11], [-9, 28]];
// Observed knight spawn: at the top or bottom edge of the screen, x ≈ Prince
export const KNIGHT_SPAWN_DY = 52;

export type CombatEvent = 'player_strikes' | 'enemy_slain' | 'player_injured' | null;

// Sword hitbox: the blade sits SWORD_REACH px ahead of a body along its
// facing axis; a body is an 8×8 box. Mirrors the STIC per-pixel MOB collision
// closely enough for a 1-px-thick blade (a thin box, SWORD_HALF_WIDTH).
function swordHitsBody(
  sx: number, sy: number, fdx: number, fdy: number,
  bx: number, by: number, bw: number, bh: number,
): boolean {
  // blade centre, SWORD_REACH px ahead of the wielder's body centre
  const cx = sx + 4 + fdx * SWORD_REACH;
  const cy = sy + 4 + fdy * SWORD_REACH;
  // blade extent: 8 px along facing axis, thin across it (diagonals: 8×8)
  const alongX = fdx !== 0, alongY = fdy !== 0;
  const hw = alongX && !alongY ? 4 : (alongY && !alongX ? SWORD_HALF_WIDTH : 4);
  const hh = alongY && !alongX ? 4 : (alongX && !alongY ? SWORD_HALF_WIDTH : 4);
  return cx + hw > bx && cx - hw < bx + bw && cy + hh > by && cy - hh < by + bh;
}

// The knight's sword MOB (8×16, half-height rows) in its current pose against
// an 8×8 body box — per-pixel on the sword side, which is what matters for a
// 1-px-thick blade.
function knightSwordHitsBox(enemy: Enemy, bx: number, by: number): boolean {
  const pose = KNIGHT_POSES[knightPoseSector(enemy)];
  const bm = SWORD_BITMAPS[pose.sword];
  const ox = enemy.x + pose.sx;
  const oy = enemy.y + pose.sy;
  for (let r = 0; r < 16; r++) {
    const byte = bm[pose.sflip ? 15 - r : r];
    if (!byte) continue;
    const wy = oy + r / 2;
    if (wy < by || wy >= by + 8) continue;
    for (let c = 0; c < 8; c++) {
      const bit = pose.smirror ? (byte >> c) & 1 : (byte >> (7 - c)) & 1;
      if (!bit) continue;
      const wx = ox + c;
      if (wx >= bx && wx < bx + 8) return true;
    }
  }
  return false;
}

/** Captured (finding #15): the Prince's sword pixels destroy a fireball. */
export function playerSwordHitsBox(player: PlayerState, bx: number, by: number): boolean {
  if (player.dead) return false;
  const pfx = player.faceDx || (player.faceDy ? 0 : 1);
  return swordHitsBody(player.x, player.y, pfx, player.faceDy, bx, by, 8, 8);
}

export function resolveContact(player: PlayerState, enemy: Enemy): CombatEvent {
  if (!enemy.alive || enemy.dying > 0 || player.dead) return null;
  // Sorcerers can only be fought while materialized.
  if (enemy.type === 'sorcerer' && enemy.phase !== 'active') return null;
  if (enemy.hitCd > 0) return null;

  const bw = enemy.type === 'serpent' ? SERPENT_W : 8;
  const bh = enemy.type === 'serpent' ? SERPENT_H : 8;

  // 1) Player's sword on the enemy body → the enemy is struck. Captured:
  //    this wins ties with the enemy's own strike on the same frame.
  //    Captured (finding #15): the SORCERER is immune — the sword sat on its
  //    body for 80 frames, red and white, with no effect.
  const pfx = player.faceDx || (player.faceDy ? 0 : 1);
  const pfy = player.faceDy;
  if (!player.dead && enemy.type !== 'sorcerer' && swordHitsBody(player.x, player.y, pfx, pfy, enemy.x, enemy.y, bw, bh)) {
    enemy.hp--;
    enemy.hitCd = HIT_GRACE_TICKS;
    if (enemy.hp <= 0) {
      enemy.dying = KNIGHT_DEATH_TICKS;
      return 'enemy_slain';
    }
    return 'player_strikes';
  }

  // 2) Enemy's sword on the player body → the player is hit. Only knights
  //    carry a sword; the Serpent bites at close range; sorcerers use fire.
  if (enemy.type === 'phantom_knight') {
    if (knightSwordHitsBox(enemy, player.x, player.y)) return 'player_injured';
    return null;
  }
  if (enemy.type === 'serpent') {
    const ex = Math.max(enemy.x, Math.min(player.x, enemy.x + SERPENT_W - 8));
    const ey = Math.max(enemy.y, Math.min(player.y, enemy.y + SERPENT_H - 8));
    if (Math.max(Math.abs(player.x - ex), Math.abs(player.y - ey)) <= 5) return 'player_injured';
  }
  return null;
}

// Captured injury model (findings #7, #13, #14): a hit = 40-TICK stun with a
// random palette colour per tick (movement locked), then white → GRAY on
// the first hit. A hit while gray runs the DEATH script ($5B94): the sword
// vanishes and the body plays a 23-tick burst (dot 7, sparkle 7, big burst
// 7, tail 2 — colours 9-15, one per tick); then, if a reincarnation is
// left, $017C-- and the FALLEN script ($5B9A): twinkling remains (4 poses,
// 4 ticks each, colours 0-7) for 61 ticks, after which the Prince stands
// up white, in place — but only once the disc is released. With no
// reincarnation left the burst simply ends with the Prince gone: game over
// (screen frozen, ROM idles). No natural recovery from gray.
export const DEATH_BURST_TICKS = 23;
export const FALLEN_TICKS = 61;
export function injurePlayer(player: PlayerState): void {
  if (player.dead || player.stunned > 0) return;

  player.stunned = STUN_TICKS;
  if (!player.injured) {
    player.injured = true;
  } else {
    player.injured = false;
    player.dead = true;
    player.deathPhase = 'dying';
    player.deathTick = 0;
    player.stunned = 0;
  }
}

// `discReleased` must be true for the revive to happen (captured: holding
// a direction keeps the player fallen indefinitely).
export function tickPlayerCombat(player: PlayerState, discReleased = true): boolean {
  if (player.stunned > 0) player.stunned--;
  if (player.invuln > 0) player.invuln--;

  if (!player.dead) return false;
  player.deathTick++;
  if (player.deathPhase === 'dying' && player.deathTick >= DEATH_BURST_TICKS) {
    if (player.reincarnations > 0) {
      player.reincarnations--;          // captured: $017C-- as the fallen script starts
      player.deathPhase = 'fallen';
      player.deathTick = 0;
    } else {
      player.deathPhase = 'gone';
    }
  } else if (player.deathPhase === 'fallen' && player.deathTick >= FALLEN_TICKS && discReleased) {
    player.dead = false;
    player.deathPhase = null;
    player.injured = false;
    player.stunned = 0;
    return true;
  }
  return false;
}

export function isGameOver(player: PlayerState): boolean {
  return player.deathPhase === 'gone';
}

// Death-script bitmaps captured from GRAM card 48 (8×16):
export const DEATH_BURST: number[][] = [
  [0, 0, 0, 0, 0, 0, 0, 0x18, 0x18, 0, 0, 0, 0, 0, 0, 0],                       // dot (ticks 0-6)
  [0, 0, 0, 0, 0, 0, 0x14, 0x28, 0x08, 0x24, 0, 0, 0, 0, 0, 0],                 // sparkle (7-13)
  [0x81, 0x04, 0x40, 0x10, 0x00, 0x41, 0x00, 0x80, 0x04, 0x00, 0x40, 0x04, 0x20, 0x00, 0x01, 0x80], // burst (14-20)
  [0x41, 0x80, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x82],                     // tail (21-22)
];
export function deathBurstPose(t: number): number { return t < 7 ? 0 : t < 14 ? 1 : t < 21 ? 2 : 3; }
// Fallen remains: 4 poses cycling, 4 ticks each (row 15 = $82 throughout).
export const FALLEN_POSES: number[][] = [
  [0x08, 0x24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x82],
  [0, 0, 0, 0, 0, 0, 0, 0x18, 0, 0, 0, 0, 0, 0, 0, 0x82],
  [0x18, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x82],
  [0, 0, 0, 0, 0, 0, 0x14, 0x28, 0, 0, 0, 0, 0, 0, 0, 0x82],
];
export function fallenPose(t: number): number { return Math.floor(t / 4) % 4; }

// --- Sprite data (ROM-extracted, verified against binary) ---

// Phantom Knights use the PLAYER's own 5-frame knight figure, rendered in
// BLACK (fg 0), plus a separate axis-aligned 8-px sword MOB — captured live
// from the running game (traces/capture_attack_anim_out.txt): enemy MOB A
// registers = cards 52/56 fg 0, whose runtime GRAM bytes are byte-identical
// to player_sprites frames 4 and 0; companion sword MOBs are a $FF row
// (horizontal) or $10 column (vertical). The old "$5C1C walk frames" were
// wrong data and have been removed.

// Red Sorcerer — captured from the live GRAM card the sorcerer MOB uses
// (finding #11; the earlier "$6677/$6687" bytes were code, not a sprite).
// One body bitmap; it is white while materialising/dematerialising and red
// (fg 2) while active.
export const SORCERER_BODY: number[] = [
  0x50, 0x70, 0x38, 0x70, 0x3A, 0xF5, 0x72, 0xFB,
  0xDE, 0xCE, 0xD6, 0xD7, 0x47, 0xFD, 0x30, 0x00,
];
// Materialise poses (white), captured in order: small diamond, large
// diamond, sparkle. Dematerialise plays sparkle → large → gone.
export const SORCERER_MATERIALISE: number[][] = [
  [0x00, 0x00, 0x00, 0x00, 0x18, 0x24, 0x3C, 0x66, 0x66, 0x3C, 0x24, 0x18, 0x00, 0x00, 0x00, 0x00],
  [0x00, 0x00, 0x00, 0x42, 0x18, 0x24, 0x24, 0x5A, 0x5A, 0x24, 0x24, 0x18, 0x42, 0x00, 0x00, 0x00],
  [0x00, 0x00, 0x18, 0x00, 0x42, 0x00, 0x18, 0xBD, 0xBD, 0x18, 0x00, 0x42, 0x00, 0x18, 0x00, 0x00],
];
// Captured timeline of one appearance (frames at the observed ~3.6
// frames/tick; three instances agreed to ±4 frames):
//   materialise  small 20 → large 12 → sparkle 8         (40)
//   RED body 61 frames, ONE fireball launched at +27          (61)
//   white body 22 → sparkle 12 → large 12 → gone             (46)
// Half the visits chained straight into a second appearance at a new spot.
export const SORCERER_APPEAR = 11;   // ticks (captured 10-12; 40 frames)
export const SORCERER_RED = 17;      // ticks (61 frames)
export const SORCERER_FIRE_AT = 7;   // ticks into red (captured 7-8)
export const SORCERER_VANISH = 13;   // ticks (captured 13-14; 46 frames)
export function sorcererAppearPose(t: number): number { return t < 6 ? 0 : t < 9 ? 1 : 2; }
export function sorcererVanishPose(t: number): number { return t < 6 ? -1 : t < 10 ? 2 : 1; } // -1 = body
// Legacy 2-frame array kept for the debug view; frame 0 is the real body.
export const SORCERER_SPRITES: number[][] = [SORCERER_BODY, SORCERER_BODY];

// The Sinister Serpent — ROM $5C9E/$5CAE, 2 frames (8×16 each), green
export const SERPENT_SPRITES: number[][] = [
  [// frame 0 — $5C9E
    0x10, 0x10, 0x6D, 0x3E, 0x7F, 0xF6, 0xF1, 0xD8,
    0x88, 0xA8, 0xA8, 0x88, 0xD8, 0xF1, 0xF6, 0x7F,
  ],
  [// frame 1 — $5CAE
    0x3E, 0x6D, 0x02, 0x25, 0x6E, 0x3F, 0x7C, 0xF4,
    0x98, 0x98, 0xA8, 0xAA, 0x8D, 0x7A, 0xBF, 0x1E,
  ],
];

// Fireball — captured from the live GRAM card of the sorcerer's projectile
// MOB (8×16): three bitmaps cycling every 4 frames, colour alternating
// yellow (6) / orange (10). (The earlier "$5C4E" 8×8 frames were wrong data.)
export const FIREBALL_FRAMES: number[][] = [
  [0x00, 0x24, 0x11, 0x3A, 0xAE, 0x7B, 0x6E, 0xFE, 0x7F, 0x7C, 0xFE, 0x5C, 0x88, 0x24, 0x00, 0x00],
  [0x00, 0x01, 0x54, 0x1E, 0x7F, 0xFA, 0x7F, 0x7B, 0xFE, 0x7E, 0xB6, 0x5D, 0x24, 0x40, 0x10, 0x00],
  [0x10, 0x00, 0x20, 0x1C, 0x5F, 0x7E, 0x7E, 0xFB, 0x5E, 0x7B, 0xBE, 0x7C, 0x8A, 0x10, 0x00, 0x00],
];

// Spawn effect — ROM $5AE6, 2 frames (8×16 each), red/yellow palette
export const SPAWN_EFFECT: number[][] = [
  [// frame 0, cards 0-1
    0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x18, 0x24,
    0x3C, 0x66, 0x66, 0x3C, 0x24, 0x18, 0x00, 0x00,
  ],
  [// frame 1, cards 2-3
    0x00, 0x00, 0x00, 0x00, 0x00, 0x42, 0x18, 0x24,
    0x24, 0x5A, 0x5A, 0x24, 0x24, 0x18, 0x42, 0x00,
  ],
];

// Item sprites (8×8, 1bpp)
export const ITEM_SPRITES: Record<ItemKind, number[]> = {
  key:    [0x03, 0x02, 0x3e, 0x22, 0x3e, 0x20, 0x18, 0x00],
  potion: [0x1c, 0x3e, 0x3e, 0x3e, 0x7f, 0x7f, 0x7f, 0x2a],
  scroll: [0x3c, 0x24, 0x3c, 0x24, 0x3c, 0x24, 0x3c, 0x00],
  crown:  [0x00, 0x81, 0xA5, 0xFF, 0x7E, 0x7E, 0xFF, 0x00],
};
