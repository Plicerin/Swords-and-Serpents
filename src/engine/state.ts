// Player state for Swords & Serpents
// Matches emulator addresses:
//   $0325 = Player X (16-bit, low byte = pixel X)
//   $032D = Player Y (16-bit, low byte = pixel Y)
//   $019C = Current level (0-13)
//   $02F4 = Data pointer (incremented on stair descent)

export interface PlayerState {
  // Position (pixel coordinates, 0-159 for X, 0-95 for Y)
  x: number;        // $0325 low byte (0-159)
  y: number;        // $032D low byte, masked 0x7F (0-95)

  // Level state
  level: number;    // $019C (0-13)
  dataPtr: number;  // $02F4 (incremented on stair descent)

  // Movement state
  facing: Direction;       // 'none' when no key is held THIS frame
  lastFacing: Direction;   // persists after release (4-way, legacy/HUD)
  moving: boolean;

  // 8-way facing vector (signs -1/0/1), persists after release. Used to pick the
  // warrior rotation frame: 5 frames cover N→E→S; the W side is the H-mirror.
  faceDx: number;
  faceDy: number;

  // Post-transition lock — analogous to ROM's G_01AB ($01AB).
  // Set to 2 after any room transition fires; decremented each frame.
  // Boundary checks are suppressed while > 0, preventing the spawn
  // position in the new room from immediately re-triggering a transition.
  transitionCooldown: number;

  // --- Combat state (manual: "Injuries, Cures & Reincarnations", p.10) ---
  reincarnations: number;  // "lives" — start at 9; quest ends when these run out
  injured: boolean;        // lost half a life this reincarnation (white -> gray)
  stunned: number;         // frames remaining stunned after a hit ("cannot move")
  invuln: number;          // i-frames: no new injury while > 0 (escape window)
  dead: boolean;           // currently in death/respawn pause (flashing X)
  respawnTimer: number;    // frames until reappear after a death

  // --- Inventory (captured: status screen INHAND / STORED / VALUE) ---
  keys: number;            // keys collected
  potions: number;         // treasures IN HAND (max 6)
  scrolls: number;         // scrolls carried
  stored: number;          // treasures stored in the level-1 chest
  storedValue: number;     // manual: 50/100/150/200 per treasure by level found
}

export type Direction = 'up' | 'down' | 'left' | 'right' | 'none';

export const TILE_SIZE = 8;
export const SCREEN_WIDTH = 160;
export const SCREEN_HEIGHT = 96;
export const GRID_COLS = 20;
export const GRID_ROWS = 12;

// Player starting position (center of room 0)
export const START_X = 0x58;
export const START_Y = 0x38;
export const START_LEVEL = 0;
export const START_DATA_PTR = 0x65B8; // Initial value from emulator

export function createInitialState(): PlayerState {
  return {
    x: START_X,
    y: START_Y,
    level: START_LEVEL,
    dataPtr: START_DATA_PTR,
    facing: 'down',
    lastFacing: 'down',
    moving: false,
    faceDx: 0,
    faceDy: 1,   // facing down at spawn
    transitionCooldown: 0,
    reincarnations: 9,   // manual: "begin their quest with nine lives each"
    injured: false,
    stunned: 0,
    invuln: 0,
    dead: false,
    respawnTimer: 0,
    keys: 0,
    potions: 0,
    scrolls: 0,
    stored: 0,
    storedValue: 0,
  };
}

// Convert pixel position to grid coordinates
export function pixelToGrid(x: number, y: number): { col: number; row: number } {
  return {
    col: Math.floor(x / TILE_SIZE),
    row: Math.floor(y / TILE_SIZE),
  };
}

// Convert grid coordinates to BACKTAB address
export function gridToBacktabAddr(col: number, row: number): number {
  // BACKTAB starts at $0200, each row has 20 words
  return 0x0200 + row * GRID_COLS + col;
}

// Check if position is within screen bounds
export function isInBounds(x: number, y: number): boolean {
  return x >= 0 && x < SCREEN_WIDTH && y >= 0 && y < SCREEN_HEIGHT;
}