// The ROM's object system — captured from the disassembly and verified live in
// the Intellijsd oracle (docs/HANDOVER.md ROM finding #10).
//
//   $64DE  16 (column,row) records per level              → assets/objects.json
//   $6580  5-bit object TYPE per record (packed pairs)
//   $655E  BACKTAB word per type: the card that gets drawn
//
// L_6377 overlays every on-screen record onto BACKTAB after each scroll; types
// 0-7 are only drawn while their bit in G_0180[level] is set (cleared on
// pickup).  L_63F5 is the ENTER handler: it scans the 2×2 tile block under
// the player's sprite (L_6054: top-left tile, then right, below, below-right)
// for the first card in 12..22 and acts on it:
//   card 12  chest        → store treasures (level 0 only)
//   card 13  marker       → if the level's KEY was taken (G_019D bit 7):
//                           write $084B (GRAM card 9 = DOWN stairs) into the
//                           BACKTAB word AFTER the marker (one column right)
//   card 14  lantern      → player colour ← white (cure)  [from L_64CB]
//   card 15-21 treasure   → tile ← $1600, G_019D |= bit, G_0180 &= ~bit,
//                           in-hand++ (max 6: refused when G_01A8 ≥ 6)
//   card 22  KEY          → same, but never counted against the 6 in hand
// The stairs tile is a plain BACKTAB write: it survives scroll shifts but is
// lost as soon as its column/row scrolls off and is regenerated from map data.
// Walking so that the 2×2 block holds card 9 (with any background collision)
// → level+1; card 10 (UP stairs, a normal object of type 12) → level-1.  The
// player keeps the SAME world coordinates on the new level.

import { TILE } from './maze';

export interface RomObject { col: number; row: number; type: number; word: number; }
export interface ObjectTables { typeWord: number[]; levels: RomObject[][]; }

export const TYPE_KEY = 7;
export const TYPE_LANTERN = 8;
export const TYPE_CHEST = 9;
export const TYPE_MARKER = 10;
export const TYPE_UP_STAIRS = 12;

export const CARD_DOWN_STAIRS = 9;
export const CARD_UP_STAIRS = 10;
export const CARD_CHEST = 12;
export const CARD_MARKER = 13;
export const CARD_LANTERN = 14;
export const CARD_TREASURE_FIRST = 15;   // types 0-6 → cards 15-21
export const CARD_KEY = 22;              // type 7

export const WORD_DOWN_STAIRS = 0x084B;  // GRAM card 9, fg 3 (tan) on black
export const WORD_TAKEN = 0x1600;        // GROM blank on the olive floor
export const MAX_IN_HAND = 6;            // G_01A8 limit in L_643C

// Per-level pickup state — G_0180[level] (present) and G_019D[level] (taken).
export interface LevelObjectState {
  present: boolean[];   // index = type 0-7
  taken: boolean[];
}

export function createObjectState(): LevelObjectState {
  return { present: Array(8).fill(true), taken: Array(8).fill(false) };
}

/** The 2×2 tile block L_6054 derives from a sprite's top-left world pixel. */
export function tileBlock(x: number, y: number, w: number, h: number): { col: number; row: number }[] {
  const c = Math.floor(x / TILE);
  const r = Math.floor(y / TILE);
  const wr = (v: number, n: number) => ((v % n) + n) % n;
  return [
    { col: wr(c, w),     row: wr(r, h) },
    { col: wr(c + 1, w), row: wr(r, h) },
    { col: wr(c, w),     row: wr(r + 1, h) },
    { col: wr(c + 1, w), row: wr(r + 1, h) },
  ];
}

/** Type of a treasure/key card (15..22 → 0..7), else -1. */
export function pickupType(card: number): number {
  return card >= CARD_TREASURE_FIRST && card <= CARD_KEY ? card - CARD_TREASURE_FIRST : -1;
}
