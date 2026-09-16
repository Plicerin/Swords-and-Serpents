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
  c: 'readScroll', C: 'readScroll',  // keypad C = Read Scroll (captured)
  r: 'readScroll', R: 'readScroll',  // alias
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

  // Gamepad (standard mapping), polled on every snapshot and merged with
  // the keyboard. Disc = left stick or d-pad (8-way). Buttons:
  //   A (0) = ENTER (pick up / store / open the stairs)
  //   B (1) = back up            X (2) = read scroll (keypad C)
  //   Y (3) = status (keypad 0)  Start (9) = ENTER too
  private padState(): { dx: number; dy: number; enter: boolean; backUp: boolean; readScroll: boolean; status: boolean } {
    const none = { dx: 0, dy: 0, enter: false, backUp: false, readScroll: false, status: false };
    if (typeof navigator === 'undefined' || !navigator.getGamepads) return none;
    const pad = Array.from(navigator.getGamepads()).find(p => p && p.connected);
    if (!pad) return none;
    const b = (i: number) => !!pad.buttons[i] && pad.buttons[i].pressed;
    const ax = pad.axes[0] ?? 0, ay = pad.axes[1] ?? 0;
    const DEAD = 0.4;
    let dx = ax > DEAD ? 1 : ax < -DEAD ? -1 : 0;
    let dy = ay > DEAD ? 1 : ay < -DEAD ? -1 : 0;
    if (b(12)) dy = -1; if (b(13)) dy = 1; if (b(14)) dx = -1; if (b(15)) dx = 1;
    return { dx, dy, enter: b(0) || b(9), backUp: b(1), readScroll: b(2), status: b(3) };
  }

  // Snapshot the current input. `select` is edge-triggered (consumed once).
  getInput(): InputState {
    const pad = this.padState();
    const held = (d: Direction) => this.keys.has(d);

    // 8-way movement vector: keyboard when any key is held (opposites
    // cancel, as before), otherwise the pad.
    const kdx = (held('right') ? 1 : 0) - (held('left') ? 1 : 0);
    const kdy = (held('down') ? 1 : 0) - (held('up') ? 1 : 0);
    const keyboardHeld = held('left') || held('right') || held('up') || held('down');
    const dx = keyboardHeld ? kdx : pad.dx;
    const dy = keyboardHeld ? kdy : pad.dy;

    let direction: Direction = 'none';
    // Priority order when multiple held: up > down > left > right.
    if (dy < 0) direction = 'up';
    else if (dy > 0) direction = 'down';
    else if (dx < 0) direction = 'left';
    else if (dx > 0) direction = 'right';

    const select = this.selectKey;
    this.selectKey = null;

    return {
      direction,
      dx,
      dy,
      backUp: !!this.actions['backUp'] || pad.backUp,
      pickup: !!this.actions['pickup'],
      stairs: !!this.actions['stairs'],
      readScroll: !!this.actions['readScroll'] || pad.readScroll,
      status: !!this.actions['status'] || pad.status,
      enter: !!this.actions['enter'] || pad.enter,
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
