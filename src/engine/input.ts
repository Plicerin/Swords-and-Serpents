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
//
// The LEFT controller (Nilrem the Wizard, games 2 and 3) is the second
// keyboard cluster / second gamepad: see `getInput2`.

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

// The Wizard's controller (left overlay): disc, side buttons, keypad.
export interface InputState2 {
  dx: number;
  dy: number;
  backUp: boolean;        // "Wizard backs up"
  enter: boolean;         // pick up / store / open the stairs
  readScroll: boolean;    // "Read Scrolls / acquire Spells"
  status: boolean;
  spell: number | null;   // keypad 1-9 = FREEZE, FIREBALL, HEAL, FAST FEET, INVINCIBLE,
                          // DESTROY WALLS, TO CHEST, INVINC-WIZ, TO KNIGHT (edge-triggered)
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

// Wizard (left controller) on the keyboard: I/J/K/L disc, U backs up,
// O = ENTER, P = read scroll, numpad 0 = status, numpad 1-9 (or F1-F9) = spells.
const KEY_MAP2: Record<string, Direction> = {
  i: 'up', I: 'up', k: 'down', K: 'down', j: 'left', J: 'left', l: 'right', L: 'right',
};
const ACTION_KEYS2: Record<string, string> = {
  u: 'backUp', U: 'backUp',
  o: 'enter', O: 'enter',
  p: 'readScroll', P: 'readScroll',
};

export class InputHandler {
  private keys: Set<Direction> = new Set();
  private actions: Record<string, boolean> = {};
  private selectKey: number | null = null;
  private keys2: Set<Direction> = new Set();
  private actions2: Record<string, boolean> = {};
  private spellKey: number | null = null;

  constructor() {
    if (typeof window !== 'undefined') {
      window.addEventListener('keydown', this.onKeyDown);
      window.addEventListener('keyup', this.onKeyUp);
    }
  }

  private onKeyDown = (e: KeyboardEvent): void => {
    // Wizard keypad first: numpad digits and F-keys (e.code is layout-proof)
    const np = /^Numpad(\d)$/.exec(e.code) ?? /^F(\d)$/.exec(e.code);
    if (np) {
      const n = Number(np[1]);
      if (n === 0) this.actions2['status'] = true; else this.spellKey = n;
      e.preventDefault();
      return;
    }
    const dir = KEY_MAP[e.key];
    if (dir) { this.keys.add(dir); e.preventDefault(); return; }
    const dir2 = KEY_MAP2[e.key];
    if (dir2) { this.keys2.add(dir2); e.preventDefault(); return; }

    const action = ACTION_KEYS[e.key];
    if (action) { this.actions[action] = true; e.preventDefault(); return; }
    const action2 = ACTION_KEYS2[e.key];
    if (action2) { this.actions2[action2] = true; e.preventDefault(); return; }

    if (e.key === '1' || e.key === '2' || e.key === '3') {
      this.selectKey = Number(e.key);
      e.preventDefault();
    }
  };

  private onKeyUp = (e: KeyboardEvent): void => {
    const np = /^Numpad(\d)$/.exec(e.code) ?? /^F(\d)$/.exec(e.code);
    if (np) { if (Number(np[1]) === 0) this.actions2['status'] = false; return; }
    const dir = KEY_MAP[e.key];
    if (dir) { this.keys.delete(dir); return; }
    const dir2 = KEY_MAP2[e.key];
    if (dir2) { this.keys2.delete(dir2); return; }

    const action = ACTION_KEYS[e.key];
    if (action) { this.actions[action] = false; }
    const action2 = ACTION_KEYS2[e.key];
    if (action2) { this.actions2[action2] = false; }
  };

  // Gamepads (standard mapping), polled on every snapshot and merged with
  // the keyboard. Disc = left stick or d-pad (8-way). Buttons:
  //   A (0) = ENTER (pick up / store / open the stairs)
  //   B (1) = back up            X (2) = read scroll (keypad C)
  //   Y (3) = status (keypad 0)  Start (9) = ENTER too
  // The first connected pad is the Prince, the second the Wizard; the
  // Wizard's pad also casts: LB (4) FREEZE, RB (5) FIREBALL, LT (6) HEAL,
  // RT (7) FAST FEET.
  private padState(which: number): { dx: number; dy: number; enter: boolean; backUp: boolean; readScroll: boolean; status: boolean; spell: number | null } {
    const none = { dx: 0, dy: 0, enter: false, backUp: false, readScroll: false, status: false, spell: null };
    if (typeof navigator === 'undefined' || !navigator.getGamepads) return none;
    const pads = Array.from(navigator.getGamepads()).filter(p => p && p.connected);
    const pad = pads[which];
    if (!pad) return none;
    const b = (i: number) => !!pad.buttons[i] && pad.buttons[i].pressed;
    const ax = pad.axes[0] ?? 0, ay = pad.axes[1] ?? 0;
    const DEAD = 0.4;
    let dx = ax > DEAD ? 1 : ax < -DEAD ? -1 : 0;
    let dy = ay > DEAD ? 1 : ay < -DEAD ? -1 : 0;
    if (b(12)) dy = -1; if (b(13)) dy = 1; if (b(14)) dx = -1; if (b(15)) dx = 1;
    const spell = b(4) ? 1 : b(5) ? 2 : b(6) ? 3 : b(7) ? 4 : null;
    return { dx, dy, enter: b(0) || b(9), backUp: b(1), readScroll: b(2), status: b(3), spell };
  }
  private padSpellHeld = false;

  // Snapshot the current input. `select` is edge-triggered (consumed once).
  getInput(): InputState {
    const pad = this.padState(0);
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

  /** The Wizard's controller. `spell` is edge-triggered (consumed once). */
  getInput2(): InputState2 {
    const pad = this.padState(1);
    const held = (d: Direction) => this.keys2.has(d);
    const kdx = (held('right') ? 1 : 0) - (held('left') ? 1 : 0);
    const kdy = (held('down') ? 1 : 0) - (held('up') ? 1 : 0);
    const keyboardHeld = held('left') || held('right') || held('up') || held('down');
    let spell = this.spellKey;
    this.spellKey = null;
    if (pad.spell !== null && !this.padSpellHeld) spell = pad.spell;
    this.padSpellHeld = pad.spell !== null;
    return {
      dx: keyboardHeld ? kdx : pad.dx,
      dy: keyboardHeld ? kdy : pad.dy,
      backUp: !!this.actions2['backUp'] || pad.backUp,
      enter: !!this.actions2['enter'] || pad.enter,
      readScroll: !!this.actions2['readScroll'] || pad.readScroll,
      status: !!this.actions2['status'] || pad.status,
      spell,
    };
  }

  isHeld(direction: Direction): boolean {
    return this.keys.has(direction);
  }

  clear(): void {
    this.keys.clear();
    this.actions = {};
    this.selectKey = null;
    this.keys2.clear();
    this.actions2 = {};
    this.spellKey = null;
  }
}