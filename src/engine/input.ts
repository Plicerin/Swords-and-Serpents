// Input handling for Swords & Serpents.
//
// Maps the keyboard to the Intellivision hand-controller scheme documented in
// the game manual ("HAND CONTROLLERS", p.2). For the Right Knight / Warrior
// Prince (the 1-player character):
//   Disc                      -> Move Prince (movement + facing)
//   "Warrior Prince backs up" -> walk backward (move opposite facing, no turn)
//   "Pick up/store; open"     -> interact with treasures/doors
//   "Stairs; use Lantern"     -> descend stairs / use Lantern of Life
//   "Read Scroll"             -> read a scroll
//   "Call up Status Screen"   -> show status
//   "Enter" / game-select     -> title-screen menu (1 / 2 / 2-Magic players)
// NOTE: combat has NO button — the Warrior attacks by MOVING INTO an enemy.

import { Direction } from './state';

export interface InputState {
  direction: Direction;   // disc -> move + face (4-way, legacy)
  dx: number;             // movement vector X: -1 / 0 / 1 (for 8-way facing)
  dy: number;             // movement vector Y: -1 / 0 / 1
  backUp: boolean;        // "Warrior Prince backs up": move opposite facing, keep facing
  pickup: boolean;        // "Pick up/store Treasures; open"
  stairs: boolean;        // "Stairs; use Lantern of Life"
  readScroll: boolean;    // "Read Scroll"
  status: boolean;        // "Call up Status Screen"
  enter: boolean;         // "Enter" (menu confirm)
  select: number | null;  // title-screen game select: 1, 2, or 3 (edge-triggered)
}

// Disc directions (movement + facing). Arrow keys and WASD.
const KEY_MAP: Record<string, Direction> = {
  ArrowUp: 'up', ArrowDown: 'down', ArrowLeft: 'left', ArrowRight: 'right',
  w: 'up', W: 'up',
  s: 'down', S: 'down',
  a: 'left', A: 'left',
  d: 'right', D: 'right',
};

// Held action buttons -> InputState boolean field name.
const ACTION_KEYS: Record<string, string> = {
  b: 'backUp', B: 'backUp',          // Warrior Prince backs up
  ' ': 'pickup',                     // Pick up / store / open (= ENTER on the real pad)
  f: 'stairs', F: 'stairs',          // Stairs; use Lantern of Life
  r: 'readScroll', R: 'readScroll',  // Read Scroll
  Tab: 'status', '0': 'status',      // Call up Status Screen (captured: keypad 0)
  Enter: 'enter',                    // ENTER: pick up / store / open
};

export class InputHandler {
  private keys: Set<Direction> = new Set();
  private actions: Record<string, boolean> = {};
  private selectKey: number | null = null;

  constructor() {
    if (typeof window !== 'undefined') {
      window.addEventListener('keydown', this.onKeyDown);
      window.addEventListener('keyup', this.onKeyUp);
    }
  }

  private onKeyDown = (e: KeyboardEvent): void => {
    const dir = KEY_MAP[e.key];
    if (dir) { this.keys.add(dir); e.preventDefault(); return; }

    const action = ACTION_KEYS[e.key];
    if (action) { this.actions[action] = true; e.preventDefault(); return; }

    if (e.key === '1' || e.key === '2' || e.key === '3') {
      this.selectKey = Number(e.key);
      e.preventDefault();
    }
  };

  private onKeyUp = (e: KeyboardEvent): void => {
    const dir = KEY_MAP[e.key];
    if (dir) { this.keys.delete(dir); return; }

    const action = ACTION_KEYS[e.key];
    if (action) { this.actions[action] = false; }
  };

  // Snapshot the current input. `select` is edge-triggered (consumed once).
  getInput(): InputState {
    let direction: Direction = 'none';
    // Priority order when multiple held (no diagonals yet): up > down > left > right.
    if (this.keys.has('up')) direction = 'up';
    else if (this.keys.has('down')) direction = 'down';
    else if (this.keys.has('left')) direction = 'left';
    else if (this.keys.has('right')) direction = 'right';

    // 8-way movement vector from held keys (allows diagonals).
    let dx = 0;
    let dy = 0;
    if (this.keys.has('left')) dx -= 1;
    if (this.keys.has('right')) dx += 1;
    if (this.keys.has('up')) dy -= 1;
    if (this.keys.has('down')) dy += 1;

    const select = this.selectKey;
    this.selectKey = null;

    return {
      direction,
      dx,
      dy,
      backUp: !!this.actions['backUp'],
      pickup: !!this.actions['pickup'],
      stairs: !!this.actions['stairs'],
      readScroll: !!this.actions['readScroll'],
      status: !!this.actions['status'],
      enter: !!this.actions['enter'],
      select,
    };
  }

  isHeld(direction: Direction): boolean {
    return this.keys.has(direction);
  }

  clear(): void {
    this.keys.clear();
    this.actions = {};
    this.selectKey = null;
  }
}
