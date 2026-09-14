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
  // facing (unit-ish vector toward the player) — knights hold their sword
  // 8 px ahead along this; captured behaviour is axis-locked movement.
  faceDx: number;
  faceDy: number;
  dying: number;            // >0: death-flash frames remaining (still drawn, harmless)
  // sorcerer-specific state
  visibleTimer: number;     // frames until vanish (sorcerer)
  fireTimer: number;        // frames until next fireball
  phase: 'hidden' | 'appearing' | 'active' | 'vanishing';
  phaseTimer: number;
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
//  * Knights walk at 0.5 px/frame — the same speed as the player. They hold
//    a black sword MOB 8 px ahead of the body in their facing direction.
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
const KNIGHT_SPEED = 0.5;
const STUN_FRAMES = 40;
const RESPAWN_FRAMES = 75;         // not yet captured (death → reappear)
const HIT_GRACE_FRAMES = 30;
const KNIGHT_DEATH_FRAMES = 24;    // death-flash length (captured 20-65; median)
// Sword MOB is 8×16 at 2× vertical resolution: reach is ~8 px along the
// facing axis; the blade is 1 px thick on the perpendicular axis (a single
// row/column) so the perpendicular tolerance is small.
const SWORD_REACH = 8;
const SWORD_HALF_WIDTH = 3;

export const RESPAWN_INVULN = 120;

const SORCERER_APPEAR_DELAY = 300;   // frames between wizard appearances
const SORCERER_VISIBLE_FRAMES = 180; // how long wizard stays visible
const SORCERER_FIRE_INTERVAL = 60;   // frames between fireballs
const SORCERER_APPEAR_TIME = 30;     // frames for appear animation
const FIREBALL_SPEED = 0.8;        // vs player 0.25 — dodgeable but dangerous

const SERPENT_HP = 6;
const SERPENT_FIRE_INTERVAL = 80;
const SERPENT_FIRST_SHOT = 15;      // fires almost immediately on aggro
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
    dying: 0,
    visibleTimer: 0,
    fireTimer: type === 'serpent' ? SERPENT_FIRST_SHOT : SORCERER_FIRE_INTERVAL,
    phase: isSorcerer ? 'hidden' : 'active',
    phaseTimer: isSorcerer ? Math.floor(Math.random() * 180) : 0,
  };
}

export function createItem(x: number, y: number, kind: ItemKind): GameItem {
  return { x, y, kind, collected: false };
}

// Fireballs fly 4-way along the dominant axis (like the ROM's MOB fireballs) —
// free-angle shots die instantly in the 1-tile-wide corridors. Spawned at the
// shooter's own position, which is known-walkable.
function aimedFireball(ex: number, ey: number, player: PlayerState, speed: number): Fireball {
  const ddx = player.x - ex;
  const ddy = player.y - ey;
  let dx = 0;
  let dy = 0;
  if (Math.abs(ddx) >= Math.abs(ddy)) dx = Math.sign(ddx) || 1;
  else dy = Math.sign(ddy) || 1;
  return { x: ex, y: ey, dx, dy, speed, alive: true, age: 0 };
}

// Enemies do NOT collide with walls. In the ROM, only the two player slots run
// the movement wall test (L_63F5 selects G_01AB/G_01AC by player index before
// calling L_6054); enemy MOBs are driven by animation-script velocities with
// no BACKTAB lookup — phantom knights chase straight through walls.

export function updateEnemy(enemy: Enemy, player: PlayerState, canWalk: CanWalkFn): Fireball | null {
  if (!enemy.alive) return null;
  if (enemy.dying > 0) {
    // Death flash plays out, then the knight is removed.
    enemy.dying--;
    if (enemy.dying === 0) enemy.alive = false;
    return null;
  }
  if (enemy.hitCd > 0) enemy.hitCd--;

  if (enemy.type === 'phantom_knight') {
    // Captured: knights move axis-locked along the dominant axis toward the
    // player at 0.5 px/frame, sword held ahead in the facing direction.
    const dx = player.x - enemy.x;
    const dy = player.y - enemy.y;
    if (Math.abs(dx) >= Math.abs(dy)) { enemy.faceDx = Math.sign(dx) || 1; enemy.faceDy = 0; }
    else { enemy.faceDx = 0; enemy.faceDy = Math.sign(dy) || 1; }
    enemy.x += enemy.faceDx * KNIGHT_SPEED;
    enemy.y += enemy.faceDy * KNIGHT_SPEED;
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
    if (enemy.phase === 'hidden') {
      if (enemy.phaseTimer <= 0) {
        // Warp near the player — onto a walkable tile.
        for (let attempt = 0; attempt < 12; attempt++) {
          const angle = Math.random() * Math.PI * 2;
          const dist = 40 + Math.random() * 30;
          const wx = player.x + Math.cos(angle) * dist;
          const wy = player.y + Math.sin(angle) * dist;
          if (canWalk(wx + 4, wy + 4)) {
            enemy.x = wx;
            enemy.y = wy;
            enemy.phase = 'appearing';
            enemy.phaseTimer = SORCERER_APPEAR_TIME;
            enemy.fireTimer = SORCERER_FIRE_INTERVAL;
            enemy.visibleTimer = SORCERER_VISIBLE_FRAMES;
            break;
          }
        }
        if (enemy.phase === 'hidden') enemy.phaseTimer = 60; // no spot found, retry soon
      } else {
        enemy.phaseTimer--;
      }
      return null;
    }

    if (enemy.phase === 'appearing') {
      enemy.phaseTimer--;
      if (enemy.phaseTimer <= 0) {
        enemy.phase = 'active';
      }
      return null;
    }

    if (enemy.phase === 'active') {
      enemy.visibleTimer--;
      if (enemy.visibleTimer <= 0) {
        enemy.phase = 'vanishing';
        enemy.phaseTimer = 15;
        return null;
      }
      if (enemy.fireTimer > 0) {
        enemy.fireTimer--;
      }
      if (enemy.fireTimer <= 0) {
        enemy.fireTimer = SORCERER_FIRE_INTERVAL;
        return aimedFireball(enemy.x, enemy.y, player, FIREBALL_SPEED);
      }
    }

    if (enemy.phase === 'vanishing') {
      enemy.phaseTimer--;
      if (enemy.phaseTimer <= 0) {
        enemy.phase = 'hidden';
        enemy.phaseTimer = SORCERER_APPEAR_DELAY;
      }
    }

    return null;
  }

  return null;
}

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

export function resolveContact(player: PlayerState, enemy: Enemy): CombatEvent {
  if (!enemy.alive || enemy.dying > 0 || player.dead) return null;
  // Sorcerers can only be fought while materialized.
  if (enemy.type === 'sorcerer' && enemy.phase !== 'active') return null;
  if (enemy.hitCd > 0) return null;

  const bw = enemy.type === 'serpent' ? SERPENT_W : 8;
  const bh = enemy.type === 'serpent' ? SERPENT_H : 8;

  // 1) Player's sword on the enemy body → the enemy is struck. Captured:
  //    this wins ties with the enemy's own strike on the same frame.
  const pfx = player.faceDx || (player.faceDy ? 0 : 1);
  const pfy = player.faceDy;
  if (!player.dead && swordHitsBody(player.x, player.y, pfx, pfy, enemy.x, enemy.y, bw, bh)) {
    enemy.hp--;
    enemy.hitCd = HIT_GRACE_FRAMES;
    if (enemy.hp <= 0) {
      enemy.dying = KNIGHT_DEATH_FRAMES;
      return 'enemy_slain';
    }
    return 'player_strikes';
  }

  // 2) Enemy's sword on the player body → the player is hit. Only knights
  //    carry a sword; the Serpent bites at close range; sorcerers use fire.
  if (enemy.type === 'phantom_knight') {
    if (swordHitsBody(enemy.x, enemy.y, enemy.faceDx, enemy.faceDy, player.x, player.y, 8, 8)) return 'player_injured';
    return null;
  }
  if (enemy.type === 'serpent') {
    const ex = Math.max(enemy.x, Math.min(player.x, enemy.x + SERPENT_W - 8));
    const ey = Math.max(enemy.y, Math.min(player.y, enemy.y + SERPENT_H - 8));
    if (Math.max(Math.abs(player.x - ex), Math.abs(player.y - ey)) <= 5) return 'player_injured';
  }
  return null;
}

// Captured injury model: 40-frame stun with palette-cycling flash (movement
// locked), then white → GRAY on the first hit. A hit while gray costs a
// reincarnation: the Prince FALLS in place (script $5B9A — sword removed,
// movement locked) and revives, white, on the same spot once the disc is
// released. No natural recovery from gray. At 0 reincarnations the fall is
// final (game over).
export function injurePlayer(player: PlayerState): void {
  if (player.dead || player.stunned > 0) return;

  player.stunned = STUN_FRAMES;
  if (!player.injured) {
    player.injured = true;
  } else {
    player.injured = false;
    player.reincarnations = Math.max(0, player.reincarnations - 1);
    player.dead = true;                 // fallen
    player.respawnTimer = RESPAWN_FRAMES; // minimum fallen time before a release revives
  }
}

// `discReleased` must be true for the revive to happen (captured: holding
// a direction keeps the player fallen indefinitely).
export function tickPlayerCombat(player: PlayerState, discReleased = true): boolean {
  if (player.stunned > 0) player.stunned--;
  if (player.invuln > 0) player.invuln--;

  if (player.dead && player.reincarnations > 0) {
    if (player.respawnTimer > 0) player.respawnTimer--;
    if (player.respawnTimer <= 0 && discReleased) {
      player.dead = false;
      player.injured = false;
      player.stunned = 0;
      return true;
    }
  }
  return false;
}

export function isGameOver(player: PlayerState): boolean {
  return player.reincarnations <= 0 && player.dead;
}

// --- Sprite data (ROM-extracted, verified against binary) ---

// Phantom Knights use the PLAYER's own 5-frame knight figure, rendered in
// BLACK (fg 0), plus a separate axis-aligned 8-px sword MOB — captured live
// from the running game (traces/capture_attack_anim_out.txt): enemy MOB A
// registers = cards 52/56 fg 0, whose runtime GRAM bytes are byte-identical
// to player_sprites frames 4 and 0; companion sword MOBs are a $FF row
// (horizontal) or $10 column (vertical). The old "$5C1C walk frames" were
// wrong data and have been removed.

// Red Sorcerer — ROM $6677/$6687, 2 frames (8×16 each); the scattered pixels
// read as the manual's "puffs of sulphuric smoke"
export const SORCERER_SPRITES: number[][] = [
  [// frame 0 — $6677
    0xB0, 0xB7, 0x75, 0x04, 0x64, 0xFC, 0x89, 0x04,
    0x4A, 0x79, 0x10, 0x05, 0x15, 0x0E, 0x02, 0x00,
  ],
  [// frame 1 — $6687
    0x8F, 0x79, 0x40, 0x0D, 0x02, 0x00, 0x8D, 0x41,
    0x8C, 0x04, 0x64, 0x13, 0x81, 0x8C, 0xF9, 0x40,
  ],
];

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

// Fireball — ROM $5C4E, 4 frames (8×8 each), yellow palette
export const FIREBALL_FRAMES: number[][] = [
  [0x84, 0x56, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
  [0x00, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x06],
  [0x0C, 0x30, 0x60, 0xC0, 0x00, 0x00, 0x00, 0x00],
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
