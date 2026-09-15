// The chomping doors — captured from the Intellijsd oracle (docs/HANDOVER.md
// ROM finding #9).  A door is a vertical pair of tiles using GRAM cards 1
// (upper jaw) and 2 (lower jaw); the BACKTAB words never change — the ROM
// animates by rewriting the two GRAM cards themselves, so EVERY door on the
// level chomps in lockstep.  Captured GRAM bytes, 148-frame period, keyframes
// measured over two full cycles (card 1 / card 2 switch a few frames apart):
//
//   frame   card 1                card 2
//     0     open   (blank)        open   (blank)
//    36                           half   00008080d0d0f0f0
//    39     half   f0f0702020000000
//    75     closed f0f0f0707020a0a0
//    76                           closed a0a080d0d0f0f0f0
//   111     half
//   112                           half
//   148     open                  open      (cycle repeats)
//
// A door bites when the player's MOB pixels overlap the jaw pixels: that is a
// plain STIC MOB-vs-background collision, which the player's collision handler
// classifies (L_65FC codes $41/$42 → L_668E) into exactly the same hit as a
// Phantom Knight's sword — white→gray, gray→reincarnation lost (life lost at
// $68D4) — with the same 40-frame stun flash.

export const DOOR_PERIOD = 148;

const OPEN: number[] = [0, 0, 0, 0, 0, 0, 0, 0];
const C1_HALF   = [0xf0, 0xf0, 0x70, 0x20, 0x20, 0x00, 0x00, 0x00];
const C1_CLOSED = [0xf0, 0xf0, 0xf0, 0x70, 0x70, 0x20, 0xa0, 0xa0];
const C2_HALF   = [0x00, 0x00, 0x80, 0x80, 0xd0, 0xd0, 0xf0, 0xf0];
const C2_CLOSED = [0xa0, 0xa0, 0x80, 0xd0, 0xd0, 0xf0, 0xf0, 0xf0];

// [frame, bitmap] keyframes within one period, per card.
const KEY_C1: [number, number[]][] = [[0, OPEN], [39, C1_HALF], [75, C1_CLOSED], [111, C1_HALF]];
const KEY_C2: [number, number[]][] = [[0, OPEN], [36, C2_HALF], [76, C2_CLOSED], [112, C2_HALF]];

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
