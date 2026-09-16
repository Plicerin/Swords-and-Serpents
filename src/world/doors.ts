// Animated background cards — captured from the Intellijsd oracle
// (docs/HANDOVER.md findings #9 and #16).
//
// The ROM's animated-card scheduler ($5270) keeps one word per card at
// $02F1-$02F4 (low nibble = frame, high byte = countdown) and rewrites the
// GRAM card from a ROM frame table whenever the frame changes — so EVERY
// tile using that card animates in lockstep. The countdowns of all cards
// step at the same moments: every SECOND game tick (observed 4/6/8-frame
// intervals with ticks of 2/3/4 frames).
//
//   card 0  the flames (red, $1E02): 4 frames from $62B0/$62B8/$62C0/$62C8,
//           countdown 4 stepped by 2 → a new frame every 2 steps = 4 ticks
//           (8-12 frames); also the Serpent's fire in the ziggurat corridor.
//   card 1  door upper jaw, card 2 lower jaw: frames open/half/closed/half
//           from $62D6.. / $62F8.., countdown $16 stepped by 2 → 11 steps
//           per phase = 22 ticks (48-60 frames; 17 phases measured, mean 55).
//           Card 2 is served one frame after card 1 (G_0104 round-robin).
//
// A door bites (finding #12) on ANY background contact while a door card is
// in the 2×2 block under the Prince — the jaw pixels only matter for what
// can be touched.

const OPEN: number[] = [0, 0, 0, 0, 0, 0, 0, 0];
const C1_HALF   = [0xf0, 0xf0, 0x70, 0x20, 0x20, 0x00, 0x00, 0x00];
const C1_CLOSED = [0xf0, 0xf0, 0xf0, 0x70, 0x70, 0x20, 0xa0, 0xa0];
const C2_HALF   = [0x00, 0x00, 0x80, 0x80, 0xd0, 0xd0, 0xf0, 0xf0];
const C2_CLOSED = [0xa0, 0xa0, 0x80, 0xd0, 0xd0, 0xf0, 0xf0, 0xf0];
const DOOR_C1 = [OPEN, C1_HALF, C1_CLOSED, C1_HALF];
const DOOR_C2 = [OPEN, C2_HALF, C2_CLOSED, C2_HALF];

// Flame frames in ROM order ($62B0, $62B8, $62C0, $62C8).
const FLAMES: number[][] = [
  [0x00, 0x40, 0x1b, 0x3f, 0x7c, 0xff, 0x20, 0x10],
  [0x00, 0x28, 0x7f, 0x18, 0x2f, 0x0d, 0x10, 0x00],
  [0x90, 0x20, 0xfe, 0x3f, 0x78, 0x9f, 0x04, 0x20],
  [0x40, 0x20, 0xfd, 0x7f, 0x3b, 0x1e, 0x24, 0x08],
];

export const ANIM_STEP_TICKS = 2;
export const FLAME_STEPS = 2;
export const DOOR_STEPS = 11;

/** Bitmaps of cards 0, 1 and 2 after `ticks` game ticks. */
export function animatedCards(ticks: number): { c0: number[]; c1: number[]; c2: number[] } {
  const step = Math.floor(ticks / ANIM_STEP_TICKS);
  const doorPhase = Math.floor(step / DOOR_STEPS) % 4;
  return {
    c0: FLAMES[Math.floor(step / FLAME_STEPS) % 4],
    c1: DOOR_C1[doorPhase],
    c2: DOOR_C2[doorPhase],
  };
}

/** Kept for the bridge: door cycle length in ticks. */
export const DOOR_PERIOD_TICKS = ANIM_STEP_TICKS * DOOR_STEPS * 4;
