import { PlayerState, Direction } from './state';

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

// Manual p.8: "Since they are spirits, Phantom Knights move FASTER than the
// Wizard or the Warrior Prince." You cannot outrun them (player 0.25) — you
// must turn and strike (move INTO them while facing).
// Player = 0.5 px/frame (captured); knights stay a little faster.
const KNIGHT_SPEED = 0.56;
const CONTACT_DIST = 5;
const STUN_FRAMES = 24;
const INVULN_FRAMES = 90;
const RESPAWN_FRAMES = 75;
const HIT_GRACE_FRAMES = 30;

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
function flyStep(enemy: Enemy, tx: number, ty: number, speed: number): void {
  const dx = tx - enemy.x;
  const dy = ty - enemy.y;
  const len = Math.sqrt(dx * dx + dy * dy);
  if (len <= speed) {
    enemy.x = tx;
    enemy.y = ty;
    return;
  }
  enemy.x += (dx / len) * speed;
  enemy.y += (dy / len) * speed;
}

export function updateEnemy(enemy: Enemy, player: PlayerState, canWalk: CanWalkFn): Fireball | null {
  if (!enemy.alive) return null;
  if (enemy.hitCd > 0) enemy.hitCd--;

  if (enemy.type === 'phantom_knight') {
    flyStep(enemy, player.x, player.y, KNIGHT_SPEED);
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

export function resolveContact(player: PlayerState, enemy: Enemy): CombatEvent {
  if (!enemy.alive || player.dead) return null;
  // Sorcerers can only be fought while materialized.
  if (enemy.type === 'sorcerer' && enemy.phase !== 'active') return null;
  if (enemy.hitCd > 0) return null;

  // The Serpent is a 56×16 px body — measure against the nearest point of its
  // box, not its top-left corner. It can be struck at sword reach but only
  // bites back at close range.
  let ex = enemy.x;
  let ey = enemy.y;
  if (enemy.type === 'serpent') {
    ex = Math.max(enemy.x, Math.min(player.x, enemy.x + SERPENT_W - 8));
    ey = Math.max(enemy.y, Math.min(player.y, enemy.y + SERPENT_H - 8));
  }
  const strikePad = enemy.type === 'serpent' ? 4 : 0;
  const injurePad = enemy.type === 'serpent' ? 0 : 0;
  const dist = Math.max(Math.abs(player.x - ex), Math.abs(player.y - ey));
  if (dist > CONTACT_DIST + strikePad) return null;

  if (player.moving && player.stunned === 0 && facingToward(player.facing, player, ex, ey)) {
    enemy.hp--;
    enemy.hitCd = HIT_GRACE_FRAMES;
    if (enemy.hp <= 0) {
      enemy.alive = false;
      return 'enemy_slain';
    }
    return 'player_strikes';
  }
  if (dist > CONTACT_DIST + injurePad) return null;
  return 'player_injured';
}

function facingToward(facing: Direction, player: PlayerState, ex: number, ey: number): boolean {
  switch (facing) {
    case 'up':    return ey <= player.y;
    case 'down':  return ey >= player.y;
    case 'left':  return ex <= player.x;
    case 'right': return ex >= player.x;
    default:      return false;
  }
}

export function injurePlayer(player: PlayerState): void {
  if (player.dead || player.invuln > 0) return;

  if (!player.injured) {
    player.injured = true;
    player.stunned = STUN_FRAMES;
    player.invuln = INVULN_FRAMES;
  } else {
    player.dead = true;
    player.respawnTimer = RESPAWN_FRAMES;
    player.reincarnations = Math.max(0, player.reincarnations - 1);
  }
}

export function tickPlayerCombat(player: PlayerState): boolean {
  if (player.stunned > 0) player.stunned--;
  if (player.invuln > 0) player.invuln--;

  if (player.dead) {
    player.respawnTimer--;
    if (player.respawnTimer <= 0) {
      player.dead = false;
      player.injured = false;
      player.stunned = 0;
      player.invuln = RESPAWN_INVULN;
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
