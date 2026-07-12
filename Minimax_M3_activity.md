# MiniMax-M3 Activity Log — Swords and Serpents JS Port

This document records everything done in this session on the
`C:\Users\vrock\Documents\Swords and Serpents` codebase. Date: 2026-06-10.

---

## 1. Initial Setup

- Started Vite dev server (`npm run dev`) on `http://localhost:4040/`.
- Confirmed all 4 assets load with HTTP 200:
  `/assets/gram_tiles.json`, `/assets/grom.bin`, `/assets/rooms.json`,
  `/assets/player_sprites.json`.
- Only console message was a cosmetic `favicon.ico` 404.
- Initial canvas state: 20×12 tile grid, ×4 scale, ×1.25 vertical aspect
  stretch, warrior at start position `(88, 56)`.
- HUD shows: `Level: 0 (Entrance Hall) · Pos: (88, 56) · Facing: North`.

---

## 2. Bug Fix: Warrior Movement

User reported "issues with warrior movement." Investigated and fixed:

### `src/engine/movement.ts`
- Removed hardcoded `ROOM_PARAM_TABLE` (4 bogus entries, levels 4–13 unreachable).
- `calculateTransition` no longer always increments the level; uses the
  linear room graph from `src/world/rooms.ts`.
- `lastFacing` field added (separate from per-frame `facing` so the
  sprite keeps its rotation after the key is released).
- Movement speed bumped from `0.3` to `0.5` px/frame.
- Added `findWalkableSpawn(backtab, x, y)` — expanding-ring search for
  the nearest walkable tile, used after a room transition to prevent
  spawning inside a wall pocket.

### `src/engine/collision.ts`
- `checkBoundary` only returns a non-null direction when the trigger tile
  is actually walkable (walking into a north wall no longer teleports).
- Initial 5-corner collision check was too strict; replaced with a
  single-point check at the sprite center `(px+3, py+3)` to match the
  original Intellivision MOB-collision model.

### `src/main.ts`
- Removed the duplicated/dead facing-mapping block.
- HUD now shows `Facing: <facing>  last: <lastFacing>  frame: <frameIdx>`
  so the in-browser state is visible.

### `index.html`
- Added `<div id="debug">` that mirrors live game state for headless
  inspection.

### `src/main.ts` (debug bridge)
- Installed `window.__renderRoom(level, scale)` returning a dataURL PNG
  of just the room (no warrior, no HUD), for the P0 pixel-diff.

---

## 3. P0 Validation — Pixel-Diff vs Oracle

`tools/diff_room.py` (new) — renders each level from the live assets
using the same `decode_fgbg_word` math as `src/platform/stic.ts`,
upsamples to 640×480, and pixel-diffs each against
`room_{N}_authoritative.png`. Saves `tools/room{N}_js_render.png`,
`tools/room{N}_diff.png` (red overlay), and `tools/diff_report.txt`.

**Result:** **100% exact pixel match** across rooms 0–3
(1,228,800 pixels per room, 0/240 tiles differ, mean diff = 0.0).
Rooms 4 and 5 still only reach ~60% (their traces were captured at
different gameplay states than the oracles — flagged as a follow-up).

---

## 4. Room Data Extraction (runbook §2.2)

`tools/extract_rooms.py` (new) — extracts the real 20×12 BACKTAB for
rooms 0–5 from the canonical jzIntv trace files via `parse_backtab()`:

| Room | Trace file                          | Result |
|------|-------------------------------------|--------|
| 0    | `traces/rooms/render_room_0_out.txt` | 240/240 non-zero words, 100% pixel match |
| 1    | `traces/rooms/render_room_1_out.txt` | 240/240 non-zero words, 100% pixel match |
| 2    | `traces/rooms/render_room_2_out.txt` | 240/240 non-zero words, 100% pixel match |
| 3    | `traces/rooms/render_room_3_out.txt` | 240/240 non-zero words, 100% pixel match |
| 4    | `traces/rooms/cap_room_4_out.txt`    | 240/240 non-zero words, 60% pixel match |
| 5    | `traces/rooms/cap_room_5_out.txt`    | 240/240 non-zero words, 65% pixel match |

Output: `assets/rooms.json` — `{rooms: [[240 words]×6]}` (flat int arrays).

---

## 5. Investigation: 32×64 vs 20×12 Scrolling

User repeatedly complained "dungeon does not scroll as it should" and
"the map scrolls continuously, there is no floor."

I went back and forth between 20×12 (per runbook §0.6 and disassembly)
and 32×64 (per `level0_backtab.json`):

- First, implemented 32×64 with a scrolling camera into
  `assets/rooms.json` (level 0) and added `computeCamera` in
  `src/platform/stic.ts`.
- Reverted to 20×12 per the runbook and disassembly of `L_6054`
  (player X is 8-bit / 0–255, Y is 7-bit / 0–127, BACKTAB is
  `$0200 + col + row*20` → 20×12).
- User insisted on scrolling; I re-implemented 32×64 with camera.
- User confirmed still wrong; I investigated the docs/disassembly
  more carefully and found the 32×64 `level0_backtab.json` is the
  **debug/title-screen BACKTAB before the dungeon renders**, not the
  in-game dungeon room. The actual dungeon BACKTAB is the
  20×12 capture (`render_room_0_out.txt`) that matches the
  `room_0_authoritative.png` oracle.

**Resolution:** the 20×12 model is correct for the actual game. The
"scrolling" the user wants is a smooth pan animation between rooms,
not a camera into a larger 32×64 world.

---

## 6. Current Implementation: 20×12 + Pan Animation

### `src/engine/collision.ts`
- `isWalkable`: `word == 0x1603` (tan floor) or `(word & 0x1000) != 0`
  (doorway/GRAM card family 0x1E00–0x1EFF).
- `checkBoundary`: 4 directions per `L_6677`:
  - `Y < 0x10` (rows 0–1) → `north`
  - `Y >= 0x40` (rows 8+) → `south`
  - `X < 0` or `X >= 0xA0` → `west`/`east` (only valid in the middle
    Y range 16–63)
- All functions accept `roomCols` / `roomRows` parameters (default 20/12).
- `pixelToBacktabIndex`, `getTileAt`, `canMoveTo` all updated.

### `src/engine/movement.ts`
- `getRoomDims()` returns 20×12 for all levels.
- `RoomTransition` interface supports all 4 directions
  (`'north' | 'south' | 'east' | 'west'`).
- `processMovement` uses 20×12 bounds.
- `calculateTransition` handles all 4 directions with proper spawn
  coordinates (`NORTH_SPAWN_Y`, `SOUTH_SPAWN_Y`, `EAST_SPAWN_X`,
  `WEST_SPAWN_X`).
- Added `clampY(y)` helper.
- Removed 32×64-specific logic.

### `src/main.ts`
- Removed the 32×64 viewport/camera code.
- Restored the simple 20×12 render path.
- **Added a 30-frame pan animation** in the new `PanState` interface:
  when a transition fires, the old room slides off-screen in the
  direction the player walked, and the new room slides in from the
  opposite direction. The sprite is hidden during the pan.
- `pendingTransition` deferred-state-update mechanism so the
  level/position only apply when the pan completes.
- HUD shows `Level: ... [PANNING <dir> <N>%]` during the pan.
- `__renderRoomView` bridge removed (no longer needed).

### `src/platform/stic.ts`
- `renderRoom` and `renderRoomToCanvas` keep their `camCol`/`camRow`
  parameters for backward compat but default to 0.
- `computeCamera` still available (unused for 20×12 but kept for the
  32×64 path that was removed).

---

## 7. Bug Found In-Game (and Fixed)

**User asked: "did you confirm this changes in game?"** I honestly
answered no — only the static pixel-diff was run.

**Browser test revealed:**
```
Uncaught ReferenceError: SCREEN_WIDTH is not defined
  at http://localhost:4040/
```

**Cause:** my new `clampY(y)` function in `src/engine/movement.ts`
referenced `SCREEN_WIDTH`, but I only imported `SCREEN_HEIGHT` from
`./state`.

**Fix:** added `SCREEN_WIDTH` to the import:
```ts
import { PlayerState, Direction, START_X, START_Y,
         SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE } from './state';
```

**Still not confirmed in-game** — needs a follow-up browser test to
verify the fix loads the game and movement + pan animation work
end-to-end.

---

## 8. Known Issues / Follow-Ups

1. **Stale parse-error log entry** in `dev_server.err.log` at
   `src/engine/movement.ts:210:1` (from an earlier duplicate
   `return null; }` — file content is now correct, Vite OXC cache
   needs a full reload to clear).
2. **Game not confirmed loading** after the `SCREEN_WIDTH` fix —
   need a hard-refresh browser test.
3. **Pan animation not confirmed visually** — need to walk into a
   doorway and see the scroll happen.
4. **Rooms 4 and 5 only reach ~60% pixel match** — the existing
   `cap_room_{4,5}_out.txt` traces were captured at a different
   gameplay state than the oracles. Re-capture via the input-driver
   (runbook §3.1).
5. **14 rooms in the linear sequence** (per
   `DUNGEON_MAP_DOCUMENTATION.md`) but only 6 captured. Rooms 6–13
   deferred to P6 per the runbook.

---

## 9. Files Created This Session

- `tools/extract_rooms.py` — extracts 20×12 BACKTABs from
  `traces/rooms/*.txt` into `assets/rooms.json`.
- `tools/diff_room.py` — pixel-diff each room against
  `room_{N}_authoritative.png` (P0 acceptance).
- `Minimax_M3_activity.md` — this document.

## 10. Files Modified This Session

- `src/main.ts` — camera/pan animation, debug bridge, HUD.
- `src/engine/movement.ts` — boundary, transitions, findWalkableSpawn.
- `src/engine/collision.ts` — isWalkable, checkBoundary, room dims.
- `src/engine/state.ts` — lastFacing, direction types.
- `src/platform/stic.ts` — camCol/camRow, computeCamera, room-aware render.
- `src/world/rooms.ts` — linear room graph.
- `assets/rooms.json` — 6 rooms × 240 words (20×12 flat arrays).
- `index.html` — `<div id="debug">` for headless state inspection.

## 11. Test Results

- **Pixel-diff (static render):** rooms 0–3 = 100% match,
  rooms 4–5 = ~60% (placeholder traces).
- **Browser:** game is currently broken with
  `ReferenceError: SCREEN_WIDTH is not defined` (just fixed in code,
  not yet re-tested in browser).
- **Pan animation:** not yet visually confirmed.
