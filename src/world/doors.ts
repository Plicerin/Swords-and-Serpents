// The chomping doors — captured from the Intellijsd oracle (docs/HANDOVER.md
// ROM finding #9).  A door is a vertical pair of tiles using GRAM cards 1
// (upper jaw) and 2 (lower jaw); the BACKTAB words never change — the ROM
// animates by rewriting the two GRAM cards themselves, so EVERY door on the
// level chomps in lockstep.
//
// Timing (re-measured 2026-09-15 over 17 consecutive phases from a fresh
// boot with no knights active — the owner reported the first 148-frame
// figure as too fast, and it was): the animated-card scheduler ($5270)
// keeps a per-card word at $02F2/$02F3 — low nibble = frame index 0..3
// (open, half, closed, half → tables $62D6/$62DE/$62E6/$62EE and
// $62F8/$6300/$6308/$6310), high byte = a countdown reloaded to $16 and
// stepped by 2, i.e. 11 steps per phase at ~5 frames a step: phases of
// 48-60 frames, mean 55 (period ≈ 220 frames ≈ 3.7 s). Card 2 is served one
// frame after card 1 (round-robin G_0104). With knights hunting, the steps
// slow with the game tick and phases stretch to 60-73 frames — not modelled.
//
//   frame   card 1                card 2
//     0     open   (blank)        open   (blank)
//    55     half   f0f0702020000000  (+1) half   00008080d0d0f0f0
//   110     closed f0f0f0707020a0a0  (+1) closed a0a080d0d0f0f0f0
//   165     half                      (+1) half
//   220     open                      (+1) open      (cycle repeats)
//
// A door bites when the player's MOB pixels overlap the jaw pixels: that is a
// plain STIC MOB-vs-background collision, which the player's collision handler
// classifies (L_65FC codes $41/$42 → L_668E) into exactly the same hit as a
// Phantom Knight's sword — white→gray, gray→reincarnation lost (life lost at
// $68D4) — with the same 40-frame stun flash.

export const DOOR_PERIOD = 220;
const PHASE = 55;

const OPEN: number[] = [0, 0, 0, 0, 0, 0, 0, 0];
const C1_HALF   = [0xf0, 0xf0, 0x70, 0x20, 0x20, 0x00, 0x00, 0x00];
const C1_CLOSED = [0xf0, 0xf0, 0xf0, 0x70, 0x70, 0x20, 0xa0, 0xa0];
const C2_HALF   = [0x00, 0x00, 0x80, 0x80, 0xd0, 0xd0, 0xf0, 0xf0];
const C2_CLOSED = [0xa0, 0xa0, 0x80, 0xd0, 0xd0, 0xf0, 0xf0, 0xf0];

// [frame, bitmap] keyframes within one period, per card.
const KEY_C1: [number, number[]][] = [[0, OPEN], [PHASE, C1_HALF], [2 * PHASE, C1_CLOSED], [3 * PHASE, C1_HALF]];
const KEY_C2: [number, number[]][] = [[1, OPEN], [PHASE + 1, C2_HALF], [2 * PHASE + 1, C2_CLOSED], [3 * PHASE + 1, C2_HALF]];

function at(keys: [number, number[]][], t: number): number[] {
  let cur = keys[0][1];
  for (const [f, bm] of keys) if (t >= f) cur = bm;
  return cur;
}

/** Bitmaps of cards 1 and 2 at door-cycle frame `t`. */
export function doorCards(t: number): { c1: number[]; c2: number[] } {
  const p = ((t % DOOR_PERIOD) + DOOR_PERIOD) % DOOR_PERIOD;
  return { c1: at(KEY_C1, p), c2: at(KEY_C2, p) };
}
