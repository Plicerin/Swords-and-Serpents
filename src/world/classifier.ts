// The ROM's background-collision classifier L_65FC (docs/HANDOVER.md
// findings #10 and #12).  When the STIC reports the player's MOB touching
// ANY background foreground pixel, the ROM scans the 2×2 tile block under
// the sprite — top-left, top-right, bottom-left, bottom-right (L_6054) —
// and ORs one code per tile from four quadrant tables ($6632/$6639/$6640/
// $6647).  It never looks at which pixel was touched.
//
//   bit 0 ($01)  push EAST      bit 1 ($02)  push WEST   (bit 0 wins)
//   bit 2 ($04)  push SOUTH     bit 3 ($08)  push NORTH  (bit 2 wins)
//   $10  DOWN stairs (card 9)   $20  UP stairs (card 10)
//   $40  door contact (cards 1/2) — a knight-sword-grade hit, then the push
//
// Dispatch (L_6679): 0 nothing; <$10 push; ==$10 level+1; $11-$3F level-1;
// >=$40 hit then push by (code ^ $40).  Verified live: a blank (open) door
// card in the block still bites when a wall pixel is touched (code $43).

// [card5, card4, card3, card9, card10, card2, card1] per quadrant
const TABLE: Record<number, number[]> = {
  0: [0x05, 0x04, 0x01, 0x10, 0x20, 0x41, 0x41], // TL
  1: [0x06, 0x04, 0x02, 0x10, 0x20, 0x42, 0x42], // TR
  2: [0x09, 0x08, 0x01, 0x10, 0x20, 0x41, 0x41], // BL
  3: [0x0A, 0x08, 0x02, 0x10, 0x20, 0x42, 0x42], // BR
};
const CARD_INDEX: Record<number, number> = { 5: 0, 4: 1, 3: 2, 9: 3, 10: 4, 2: 5, 1: 6 };

/** Code contributed by a GRAM card in quadrant q (0 TL, 1 TR, 2 BL, 3 BR). */
export function quadrantCode(q: number, card: number): number {
  const i = CARD_INDEX[card];
  return i === undefined ? 0 : TABLE[q][i];
}

// Push-back as captured: G_0108/G_010C = ±40 for G_034D = 10 frames moved
// the Prince 3 px (walking speed 50 = 0.5 px/frame), input ignored and the
// MOB's collision flag off for the duration.
export const PUSH_FRAMES = 10;
export const PUSH_SPEED = 0.3;

export function pushVector(code: number): { vx: number; vy: number } {
  const bits = code & 0x0F;
  const vx = bits & 1 ? PUSH_SPEED : bits & 2 ? -PUSH_SPEED : 0;
  const vy = bits & 4 ? PUSH_SPEED : bits & 8 ? -PUSH_SPEED : 0;
  return { vx, vy };
}
