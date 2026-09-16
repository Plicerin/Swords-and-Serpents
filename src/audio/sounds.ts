// The ROM's sound effects as per-frame PSG register images — captured from
// the Intellijsd oracle by snapshotting the 14 PSG registers every frame
// (docs/HANDOVER.md finding #18). Everything plays on channel B. Register
// order: A_lo B_lo C_lo E_lo A_hi B_hi C_hi E_hi enable noise shape volA volB volC.
// `shape: true` marks a frame in which the ROM wrote the envelope-shape
// register (which restarts the envelope).

export interface PsgFrame { regs: number[]; shape?: boolean; }
export type Sound = PsgFrame[];

const R = (o: Partial<Record<number, number>>): number[] => {
  const r = [0, 0, 0, 0, 0, 0, 0, 0, 0x38, 0, 0, 0, 0, 0];
  for (const k in o) r[+k] = o[k as unknown as number]!;
  return r;
};
const SILENT = R({});
const rep = (f: PsgFrame, n: number): PsgFrame[] => Array.from({ length: n }, () => f);

// Footstep: every 8 ticks while walking. Two frames of enveloped noise
// (E period $080, shape 0), noise period 0 then 1, then off.
export const FOOTSTEP: Sound = [
  { regs: R({ 3: 0x80, 8: 0x2F, 9: 0x00, 10: 0x00, 12: 0x30 }), shape: true },
  { regs: R({ 3: 0x80, 8: 0x2F, 9: 0x01, 10: 0x00, 12: 0x30 }) },
  { regs: SILENT },
];

// Red Sorcerer materialising: 33 frames of enveloped noise, E period $CF8,
// shape $F (continuous attack+hold), noise period $F.
export const SORCERER_APPEAR: Sound = [
  { regs: R({ 3: 0xF8, 7: 0x0C, 8: 0x2F, 9: 0x0F, 10: 0x0F, 12: 0x30 }), shape: true },
  ...rep({ regs: R({ 3: 0xF8, 7: 0x0C, 8: 0x2F, 9: 0x0F, 10: 0x0F, 12: 0x30 }) }, 32),
  { regs: SILENT },
];

// Fireball in flight: fixed-volume noise, period $1F for 7 frames then one
// lower each frame; runs while the fireball lives (cut when it dies).
export function fireballFrame(age: number): number[] {
  const p = Math.max(0, 0x1F - Math.max(0, age - 7));
  return R({ 8: 0x2F, 9: p, 12: 0x0F });
}

// Knight-sword / door hit (ROM sound 7, L_67AE): tone B + noise B, envelope
// $A00 shape 0, noise $B, tone period alternating $20/$40. 32 frames.
const HIT_T = (period: number): PsgFrame => ({ regs: R({ 1: period, 7: 0x0A, 8: 0x2D, 9: 0x0B, 10: 0x00, 12: 0x30 }) });
export const HIT: Sound = [
  { ...HIT_T(0x20), shape: true }, ...rep(HIT_T(0x20), 16),
  ...rep(HIT_T(0x40), 8), ...rep(HIT_T(0x20), 2), ...rep(HIT_T(0x40), 5),
  { regs: SILENT },
];

// Death burst — the Prince's fall, a slain knight, a fireball that lands:
// enveloped noise, shape $E, E period $200 for 9 frames then $F00,
// noise period 0 then 1. 74 frames.
const D = (ehi: number, noise: number): PsgFrame => ({ regs: R({ 7: ehi, 8: 0x2F, 9: noise, 10: 0x0E, 12: 0x30 }) });
export const DEATH: Sound = [
  { ...D(0x02, 0), shape: true }, ...rep(D(0x02, 1), 8), ...rep(D(0x0F, 1), 65), { regs: SILENT },
];
