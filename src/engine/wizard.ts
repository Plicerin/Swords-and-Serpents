// Nilrem the Wizard — the second player of games 2 and 3, captured from the
// ROM with real left-controller input in the Intellijsd oracle
// (docs/HANDOVER.md ROM finding #23). Everything here is ROM behaviour; the
// CPU "brain" at the bottom is the port's own addition (the ROM has no such
// thing — the Wizard is always a human on the left controller).
//
// ROM facts used here:
//  * MOB 2 is his body (light blue, fg 13; BLUE fg 1 once injured), MOB 3 his
//    spell bolt. He spawns 12 px below the Prince. Five body frames W0..W4
//    (E, ENE, NE, NNE, N) with the Prince's own flip scheme; no walk cycle,
//    no sword.
//  * L_5749/L_577A: his disc sets an EXEC velocity of magnitude 25 (12 after
//    the halving) → 24/64 px/frame on cardinals, (17,17)/64 on diagonals;
//    his "backs up" button uses 20 → 20/64 (the Prince: 50 / 40).
//  * Walls: a background collision snaps the pushed axis back to the tile
//    boundary (x 100→104 walking W, 89→88 walking E, y 29→32 walking N) and
//    that axis stays dead until the disc code changes. Objects (chest,
//    treasures, scrolls, the stairs) are not walls for him.
//  * He lives in SCREEN space: when the maze scrolls him past the visible
//    window (x < 8, x > 167, y < 8, y > 104) he is parked at that world tile
//    (G_0197/G_0198, G_019A = 1) and re-materialises at the tile's screen
//    position when it scrolls back in. Levels: he keeps his screen position.
//  * Spells (L_608B): keypad 1-9 with the disc released. 1 (FREEZE) is free,
//    2-9 need a use in $018E-$0195 (game 2: none; game 3: FIREBALL, HEAL,
//    FAST FEET ×3; a spell scroll read by the Wizard SETS its spell to 10).
//    Nothing casts while a spell is active (G_018D ≠ 0). Keys 1-6 launch a
//    bolt from his own position in his facing direction at 64/64 px/frame
//    (45/64 per axis on diagonals) that flies through walls, dies when it
//    leaves the screen window or touches any body; effects: 1 freezes a
//    knight (its re-aim timer $0351 = 240 frames, velocity 0); 2 kills a
//    knight or HURTS the Prince (a knight-grade hit); 3 heals the Prince;
//    4 = Prince speed 126 (from 50) for 349 frames ($034E); 5 = Prince
//    invincible AND immobile for 432 frames, colour cycling ($0325 bit 13);
//    6 erases the first wall tile the bolt touches (BACKTAB only). Sorcerers
//    ignore every bolt. 7 (TO CHEST) = level 1, camera (2,26), both keep
//    their screen positions. 8 = the Wizard invincible/immobile 600 frames
//    ($034F). 9 (TO KNIGHT) = a parked Wizard reappears on the Prince's tile
//    (does nothing for a dead one).
//  * Injuries: same as the Prince (40-tick colour-cycling stun, light blue →
//    blue, then the $5B94 burst, $017D--, the fallen script, revive on disc
//    release); at 0 lives the burst ends with him removed for good.
import { PlayerState, createInitialState } from './state';

export const WIZARD_FRAMES: number[][] = [
  [0x6d, 0x3e, 0x7f, 0xf6, 0xf1, 0xd8, 0x88, 0xa8, 0xa8, 0x88, 0xd8, 0xf1, 0xf6, 0x7f, 0x3e, 0x6d], // W0 E
  [0x02, 0x25, 0x6e, 0x3f, 0x7c, 0xf4, 0x98, 0x98, 0xa8, 0xaa, 0x8d, 0x7a, 0xbf, 0x1e, 0x34, 0x00], // W1 ENE
  [0x05, 0x0e, 0x16, 0x3e, 0x1c, 0xf8, 0x50, 0x8a, 0xad, 0xaa, 0xca, 0xff, 0xff, 0x9e, 0x0e, 0x18], // W2 NE
  [0x50, 0x70, 0x38, 0x70, 0x3a, 0xf5, 0x72, 0xfb, 0xde, 0xce, 0xd6, 0xd7, 0x47, 0xfd, 0x30, 0x00], // W3 NNE
  [0xa5, 0x42, 0x42, 0xf7, 0xf7, 0xe3, 0x66, 0x7e, 0xe3, 0xe3, 0xeb, 0xeb, 0xe7, 0xbd, 0x3c, 0x3c], // W4 N
];

// Spell bolt (card 54): the three "spark" frames only rewrite rows 0-7 (the
// FIREBALL writes all 16 rows), so a spark bolt keeps the lower half of the
// last fireball frame — a ROM quirk the port reproduces via `card54Lower`.
export const SPARK_FRAMES: number[][] = [
  [0x00, 0x00, 0x00, 0x10, 0x38, 0x10, 0x00, 0x00],
  [0x00, 0x00, 0x08, 0x10, 0x54, 0x10, 0x20, 0x00],
  [0x00, 0x00, 0x28, 0x92, 0x44, 0x92, 0x28, 0x00],
];

export const WIZARD_SPEED = 24 / 64;        // px/frame forward (captured: $012A = 24)
export const WIZARD_BACK_SPEED = 20 / 64;   // px/frame backing up (speed 20)
export const WIZARD_DIAG = 17 / 64;         // per axis on diagonals (EXEC trig of 12)
export const BOLT_SPEED = 64 / 64;          // px/frame (captured: $012C = ±64)
export const BOLT_DIAG = 45 / 64;
export const FREEZE_FRAMES = 240;           // $0351 ← 240
export const FAST_FEET_FRAMES = 349;        // $034E ← 349
export const FAST_FEET_SPEED = 126 / 50;    // Prince speed 126 instead of 50
export const INVINCIBLE_FRAMES = 432;       // $034E ← 432 (Prince)
export const INVINC_WIZ_FRAMES = 600;       // $034F ← 600 (Wizard)
export const SPELL_SCROLL_USES = 10;        // a read spell scroll SETS the count to 10
export const SPELL_NAMES = ['', 'FREEZE', 'FIREBALL', 'HEAL', 'FAST FEET', 'INVINCIBLE', 'DESTROY WALLS', 'TO CHEST', 'INVINC-WIZ', 'TO KNIGHT'];

export interface Bolt {
  x: number;
  y: number;
  dx: number;         // px/frame
  dy: number;
  kind: number;       // spell 1-6
  age: number;        // frames (animation clock)
}

export interface WizardState {
  p: PlayerState;                 // position, facing, injury/death model (shared with the Prince)
  active: boolean;                // games 2 and 3 only
  gone: boolean;                  // removed for good (burst at 0 lives)
  parked: { col: number; row: number; level: number } | null; // off-screen: remembered world tile (G_0197/8, G_0199)
  vx: number;                     // latched velocity, px/frame
  vy: number;
  deadX: boolean;                 // axis killed by a wall until the disc changes
  deadY: boolean;
  lastDisc: string;               // last disc code seen (movement re-arms on change)
  spells: number[];               // uses left, index 1-9 (index 1 unused: FREEZE is free)
  activeSpell: number;            // G_018D: 0 or the spell whose bolt is in flight
  bolt: Bolt | null;
  fastFeet: number;               // frames left ($034E)
  invincible: number;             // frames left, Prince ($034E)
  invincWiz: number;              // frames left, Wizard ($034F)
  card54Lower: number[];          // rows 8-15 of the bolt card (fireball residue)
  cpu: boolean;                   // port option: the CPU drives him
  cpuTimer: number;               // brain re-think countdown (ticks)
  cpuDisc: { dx: number; dy: number };
}

export function createWizard(mode: number, px: number, py: number, cpu: boolean): WizardState {
  const p = createInitialState();
  p.x = px;
  p.y = py + 12;                  // captured: MOB 2 at (88,68) under the Prince's (88,56)
  p.faceDx = 1; p.faceDy = 0;     // captured: first bolt with no disc yet flies EAST
  const spells = new Array(10).fill(0);
  if (mode === 3) { spells[2] = 3; spells[3] = 3; spells[4] = 3; }   // $018E-$0190 = 3 in game 3
  return {
    p, active: mode >= 2, gone: false, parked: null, vx: 0, vy: 0, deadX: false, deadY: false, lastDisc: '',
    spells, activeSpell: 0, bolt: null, fastFeet: 0, invincible: 0, invincWiz: 0,
    card54Lower: [0, 0, 0, 0, 0, 0, 0, 0], cpu, cpuTimer: 0, cpuDisc: { dx: 0, dy: 0 },
  };
}

/** Bolt bitmap for this frame: sparks (or fireball frames) on card 54. */
export function boltBitmap(bolt: Bolt, fireballFrames: number[][], lower: number[]): number[] {
  const step = Math.floor(bolt.age / 4) % 3;
  if (bolt.kind === 2) {
    const f = fireballFrames[step];
    for (let i = 0; i < 8; i++) lower[i] = f[8 + i];   // the residue the sparks keep
    return f;
  }
  return SPARK_FRAMES[step].concat(lower);
}

// ---------------------------------------------------------------------------
// CPU brain (port addition). Once per tick it picks a disc direction and,
// when it makes sense, a spell — within the ROM's own rules (the disc must
// be released to cast, one spell at a time, uses are consumed).
export interface BrainView {
  prince: PlayerState;
  princeMoving: boolean;
  wizard: WizardState;
  foes: { x: number; y: number; type: string; alive: boolean; dying: number; frozen: number }[];
  delta: (a: number, b: number, size: number) => number;              // shortest signed delta
  W: number;
  H: number;
  canWalkTo: (x: number, y: number) => boolean;                       // wall test for a wizard step
}

export interface BrainOutput { dx: number; dy: number; backUp: boolean; spell: number | null }

const sign = (v: number, dead = 2) => (v > dead ? 1 : v < -dead ? -1 : 0);

// Nearest 8-way unit vector to (dx,dy) and how far the point sits off that ray.
function ray(dx: number, dy: number): { ax: number; ay: number; off: number; along: number } {
  const s = Math.round(Math.atan2(dy, dx) / (Math.PI / 4));
  const ax = Math.round(Math.cos(s * Math.PI / 4)), ay = Math.round(Math.sin(s * Math.PI / 4));
  const n = Math.hypot(ax, ay);
  return { ax, ay, off: Math.abs(dx * ay - dy * ax) / n, along: (dx * ax + dy * ay) / n };
}

export function wizardBrain(v: BrainView): BrainOutput {
  const w = v.wizard;
  const out: BrainOutput = { dx: 0, dy: 0, backUp: false, spell: null };
  if (w.p.dead || w.gone || w.parked) return out;
  const pdx = v.delta(v.prince.x, w.p.x, v.W);
  const pdy = v.delta(v.prince.y, w.p.y, v.H);
  const pd = Math.hypot(pdx, pdy);

  // 1) Threat: a live knight nearby on one of the 8 lines of fire. Turn to
  //    face it and shoot — FIREBALL if we have one (never through the
  //    Prince, it would hurt him), otherwise the free FREEZE.
  if (w.activeSpell === 0) {
    let best: { frozen: number; d: number; ax: number; ay: number } | null = null;
    for (const f of v.foes) {
      if (!f.alive || f.dying > 0 || f.type !== 'phantom_knight') continue;
      const dx = v.delta(f.x, w.p.x, v.W), dy = v.delta(f.y, w.p.y, v.H);
      const d = Math.hypot(dx, dy);
      if (d > 80 || d < 4) continue;
      const r = ray(dx, dy);
      if (r.off > 5) continue;
      if (!best || d < best.d) best = { frozen: f.frozen, d, ax: r.ax, ay: r.ay };
    }
    if (best) {
      const pr = ray(pdx, pdy);
      const princeOnRay = pr.ax === best.ax && pr.ay === best.ay && pr.off < 8 && pd < best.d;
      const fire = w.spells[2] > 0 && !princeOnRay;
      if (w.p.faceDx === best.ax && w.p.faceDy === best.ay) {
        if (fire) out.spell = 2;
        else if (best.frozen === 0) out.spell = 1;
        return out;   // disc released: casting
      }
      out.dx = best.ax; out.dy = best.ay;   // turn toward it (one tick of movement)
      return out;
    }
  }

  // 2) Support: heal a gray Prince, or speed him up while knights are about,
  //    when he is on a line of fire.
  const knightNear = v.foes.some(f => f.alive && f.dying === 0 && f.type === 'phantom_knight' && Math.hypot(v.delta(f.x, v.prince.x, v.W), v.delta(f.y, v.prince.y, v.H)) < 70);
  if (w.activeSpell === 0 && pd < 60 && pd > 6) {
    const want = v.prince.injured && w.spells[3] > 0 ? 3
      : (w.spells[4] > 0 && w.fastFeet === 0 && !v.prince.dead && v.princeMoving && knightNear ? 4 : 0);
    if (want) {
      const r = ray(pdx, pdy);
      if (r.off < 4) {
        if (w.p.faceDx === r.ax && w.p.faceDy === r.ay) { out.spell = want; return out; }
        out.dx = r.ax; out.dy = r.ay;
        return out;
      }
    }
  }

  // 3) Follow: stay ~12-22 px from the Prince; slip round walls by dropping
  //    the blocked axis.
  if (pd > 22) {
    out.dx = sign(pdx, 3); out.dy = sign(pdy, 3);
    if (!v.canWalkTo(w.p.x + out.dx * 3, w.p.y + out.dy * 3)) {
      if (out.dx && v.canWalkTo(w.p.x + out.dx * 3, w.p.y)) out.dy = 0;
      else if (out.dy && v.canWalkTo(w.p.x, w.p.y + out.dy * 3)) out.dx = 0;
    }
  } else if (pd < 10) {
    out.dx = -sign(pdx, 0); out.dy = -sign(pdy, 0);   // give him room
  }
  // A wall killed an axis (ROM rule: it stays dead until the disc changes):
  // drop that axis, or let go for a tick so the next press re-arms it.
  if (w.deadX && out.dx !== 0) { if (out.dy !== 0) out.dx = 0; else { out.dx = 0; out.dy = w.cpuTimer++ % 2 ? sign(pdy, 0) || 1 : 0; } }
  if (w.deadY && out.dy !== 0) { if (out.dx !== 0) out.dy = 0; else { out.dy = 0; out.dx = w.cpuTimer++ % 2 ? sign(pdx, 0) || 1 : 0; } }
  return out;
}