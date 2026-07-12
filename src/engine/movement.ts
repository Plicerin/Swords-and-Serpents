// Player movement for Swords & Serpents.
//
// Per DUNGEON_MAP_DOCUMENTATION.md the dungeon is a linear vertical sequence
// (0 -> 1 -> 2 -> ... -> N-1). Walking north at a doorway advances to the next
// level; walking south goes back. There are no east/west room transitions.
//
// NOTE (honest status): MOVE_SPEED and the wall-sliding / spawn-snapping below
// are pragmatic placeholders, not extracted from the ROM. The real movement
// physics live in the game's per-frame movement code — port it (and confirm
// MOVE_SPEED against a trace) per docs/PORT_RUNBOOK.md §P1.

import { PlayerState, Direction, SCREEN_HEIGHT, TILE_SIZE } from './state';
import { canMoveTo, checkBoundary, getTileAt, isStair } from './collision';
import { getRoomConnections } from '../world/rooms';

export interface MovementResult {
  newX: number;
  newY: number;
  transition: RoomTransition | null;
  steppedOnStair: boolean;
}

export interface RoomTransition {
  direction: 'north' | 'south';
  newLevel: number;
  newX: number;
  newY: number;
}

// Movement speed (pixels per frame). ROM constant G_017F = 0x32 = 50 in
// fixed-point EXEC-ROM units (÷16 ≈ 3.1 px/frame). Placeholder; correct value
// must be measured via jzintv oracle — see docs/HANDOVER.md BUG-4.
const MOVE_SPEED = 0.25;

// Direction vectors
const DIR_DX: Record<Direction, number> = {
  'up': 0,
  'down': 0,
  'left': -1,
  'right': 1,
  'none': 0,
};

const DIR_DY: Record<Direction, number> = {
  'up': -1,
  'down': 1,
  'left': 0,
  'right': 0,
  'none': 0,
};

// Opposite direction — used by the "Warrior Prince backs up" control, which
// moves the Prince backward (opposite his facing) WITHOUT turning him.
const OPPOSITE: Record<Direction, Direction> = {
  'up': 'down',
  'down': 'up',
  'left': 'right',
  'right': 'left',
  'none': 'none',
};

// Spawn Y when entering a new room from the opposite (vertical) edge.
const NORTH_SPAWN_Y = SCREEN_HEIGHT - 2 * TILE_SIZE;   // 80 (enter new room from bottom)
const SOUTH_SPAWN_Y = 2 * TILE_SIZE;                    // 16 (enter new room from top)

// All dungeon rooms are 20×12 (160×96 px) per the disassembly. No scrolling.
const DEFAULT_ROOM_COLS = 20;
const DEFAULT_ROOM_ROWS = 12;

export function getRoomDims(_level: number): { cols: number; rows: number } {
  return { cols: DEFAULT_ROOM_COLS, rows: DEFAULT_ROOM_ROWS };
}

// Process player movement for one frame.
// Side-effects on `state`: updates `facing`/`lastFacing`/`moving`; the caller
// applies `newX`/`newY`/`transition`/`steppedOnStair` to its own state copy.
export function processMovement(
  state: PlayerState,
  backtab: number[],
  direction: Direction,
  currentLevel: number,
  backUp: boolean = false
): MovementResult {
  let newX = state.x;
  let newY = state.y;
  let transition: RoomTransition | null = null;
  let steppedOnStair = false;

  const dims = getRoomDims(currentLevel);
  const roomCols = dims.cols;
  const roomRows = dims.rows;

  // Resolve the movement direction and facing (tank-style, per the manual):
  //   - The disc both MOVES and FACES the Prince forward.
  //   - "Warrior Prince backs up" moves OPPOSITE the current facing without turning.
  let moveDir: Direction;
  if (backUp && state.lastFacing !== 'none') {
    moveDir = OPPOSITE[state.lastFacing];
    state.facing = state.lastFacing;   // keep facing while retreating
    state.moving = true;
  } else if (direction !== 'none') {
    moveDir = direction;
    state.facing = direction;
    state.lastFacing = direction;
    state.moving = true;
  } else {
    state.facing = 'none';
    state.moving = false;
    return { newX, newY, transition, steppedOnStair };
  }

  const dx = DIR_DX[moveDir];
  const dy = DIR_DY[moveDir];

  // Try to move in the requested direction (with wall sliding)
  const result = tryMoveWithSliding(state.x, state.y, dx, dy, backtab, roomCols);
  newX = result.x;
  newY = result.y;

  // Clamp to room bounds (0 ≤ X < 160, 0 ≤ Y < 96 for 20×12).
  if (newX < 0) newX = 0;
  if (newY < 0) newY = 0;
  if (newX > roomCols * TILE_SIZE - TILE_SIZE) newX = roomCols * TILE_SIZE - TILE_SIZE;
  if (newY > roomRows * TILE_SIZE - TILE_SIZE) newY = roomRows * TILE_SIZE - TILE_SIZE;

  // Boundary check: fires when player walks into a doorway at the room edge.
  // Suppressed while transitionCooldown > 0 — prevents the spawn position in
  // a freshly-entered room from immediately re-triggering (analogue of G_01AB).
  if (state.transitionCooldown > 0) {
    state.transitionCooldown--;
  } else {
    const boundary = checkBoundary(backtab, newX, newY, roomCols);
    if (boundary.direction) {
      transition = calculateTransition(boundary.direction, newX, currentLevel);
      if (transition) {
        newX = transition.newX;
        newY = transition.newY;
      }
    }
  }

  // Stair detection (caller decides what to do with it)
  if (isStair(getTileAt(backtab, newX, newY, roomCols))) {
    steppedOnStair = true;
  }

  return { newX, newY, transition, steppedOnStair };
}

// Try to move with wall sliding
function tryMoveWithSliding(
  x: number,
  y: number,
  dx: number,
  dy: number,
  backtab: number[],
  roomCols: number = 20
): { x: number; y: number } {
  // First try direct movement
  if (canMoveTo(backtab, x + dx * MOVE_SPEED, y + dy * MOVE_SPEED, roomCols)) {
    return { x: x + dx * MOVE_SPEED, y: y + dy * MOVE_SPEED };
  }

  // Try horizontal component only (wall sliding)
  if (dx !== 0 && canMoveTo(backtab, x + dx * MOVE_SPEED, y, roomCols)) {
    return { x: x + dx * MOVE_SPEED, y };
  }

  // Try vertical component only
  if (dy !== 0 && canMoveTo(backtab, x, y + dy * MOVE_SPEED, roomCols)) {
    return { x, y: y + dy * MOVE_SPEED };
  }

  // Completely blocked
  return { x, y };
}

// Calculate the destination room for a vertical doorway crossing.
// Reads the linear-room graph from world/rooms.ts; returns null if there is
// no room in that direction.
function calculateTransition(
  direction: 'north' | 'south',
  x: number,
  currentLevel: number
): RoomTransition | null {
  const conns = getRoomConnections(currentLevel);
  if (!conns) return null;

  if (direction === 'north') {
    if (conns.north === null) return null;
    return { direction: 'north', newLevel: conns.north, newX: clampX(x), newY: NORTH_SPAWN_Y };
  }

  // south
  if (conns.south === null) return null;
  return { direction: 'south', newLevel: conns.south, newX: clampX(x), newY: SOUTH_SPAWN_Y };
}

// Clamp X to the screen so a doorway spawn doesn't land half-off-screen.
function clampX(x: number): number {
  const MIN = TILE_SIZE;             // 8
  const MAX = 160 - 2 * TILE_SIZE;   // 144 (one tile margin on each side)
  if (x < MIN) return MIN;
  if (x > MAX) return MAX;
  return x;
}

// Find the nearest walkable position to (x, y) on `backtab`. Used after a room
// transition so the player doesn't spawn inside a wall pocket. PLACEHOLDER
// heuristic (expanding-ring search) — the real game places the player via the
// room's entry data; revisit when `L_6054` is ported.
export function findWalkableSpawn(
  backtab: number[],
  x: number,
  y: number
): { x: number; y: number } {
  if (canMoveTo(backtab, x, y)) return { x, y };

  const cx = Math.round(x);
  const cy = Math.round(y);
  for (let r = 1; r < 24; r++) {
    for (let dy = -r; dy <= r; dy++) {
      for (let dx = -r; dx <= r; dx++) {
        if (Math.abs(dx) !== r && Math.abs(dy) !== r) continue; // ring only
        const nx = cx + dx;
        const ny = cy + dy;
        if (canMoveTo(backtab, nx, ny)) return { x: nx, y: ny };
      }
    }
  }
  return { x: 80, y: 48 };
}
