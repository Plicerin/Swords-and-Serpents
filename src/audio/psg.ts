// AY-3-8914 (Intellivision PSG) synthesiser — the port plays the ROM's
// sounds as the ROM does: as per-frame register scripts (docs/HANDOVER.md
// finding #18), fed to a register-level model of the chip.
//
// Chip model: 3 square-wave tone generators (f = clock / (16 × period)),
// one 17-bit LFSR noise generator (clock / (16 × period)), one envelope
// generator stepping at clock / (16 × period) through 16 levels (a full ramp
// takes 256 × period clocks) with the
// standard shape bits (continue/attack/alternate/hold), a mixer whose enable
// register masks tone (bits 0-2) and noise (bits 3-5) per channel, and a
// logarithmic 16-level DAC. Intellivision register order ($1F0-$1FD):
//   0 A lo  1 B lo  2 C lo  3 E lo  4 A hi  5 B hi  6 C hi  7 E hi
//   8 enable  9 noise  A env shape  B volA  C volB  D volC   (vol bit 4/5 = envelope)
export const PSG_CLOCK = 3579545 / 2;

const WORKLET = `
class Psg extends AudioWorkletProcessor {
  constructor(options) {
    super();
    this.r = new Uint8Array(16);
    this.r[8] = 0x3F;
    this.tone = [0, 0, 0]; this.toneOut = [0, 0, 0];
    this.noiseCnt = 0; this.lfsr = 1; this.noiseOut = 0;
    this.envCnt = 0; this.envStep = 0; this.envHold = false; this.envAlt = false; this.envAttack = false; this.envCont = false; this.envLevel = 0;
    this.port.onmessage = (e) => { const { regs, shapeWritten } = e.data; for (let i = 0; i < 14; i++) this.r[i] = regs[i]; if (shapeWritten) this.resetEnvelope(); };
    // 16-level log DAC (AY datasheet ratios, normalised)
    this.dac = [0, 0.0137, 0.0205, 0.0291, 0.0423, 0.0618, 0.0847, 0.1369, 0.1691, 0.2647, 0.3527, 0.4499, 0.5701, 0.7228, 0.8483, 1.0];
    this.clock = ${PSG_CLOCK};
    this.acc = 0;
    const init = options && options.processorOptions;
    if (init && init.regs) { for (let i = 0; i < 14; i++) this.r[i] = init.regs[i]; if (init.shapeWritten) this.resetEnvelope(); }
  }
  resetEnvelope() {
    const s = this.r[10] & 0x0F;
    this.envCont = !!(s & 8); this.envAttack = !!(s & 4); this.envAlt = !!(s & 2); this.envHold = !!(s & 1);
    this.envStep = 0; this.envCnt = 0; this.envFinished = false;
    this.envLevel = this.envAttack ? 0 : 15;
  }
  envTick() {
    if (this.envFinished) return;
    this.envStep++;
    if (this.envStep < 16) { this.envLevel = this.envAttack ? this.envStep : 15 - this.envStep; return; }
    // end of a 16-step ramp
    if (!this.envCont) { this.envLevel = 0; this.envFinished = true; return; }
    if (this.envHold) { if (this.envAlt) this.envLevel = this.envAttack ? 0 : 15; else this.envLevel = this.envAttack ? 15 : 0; this.envFinished = true; return; }
    if (this.envAlt) this.envAttack = !this.envAttack;
    this.envStep = 0; this.envLevel = this.envAttack ? 0 : 15;
  }
  process(inputs, outputs) {
    try { return this.render(outputs); } catch (e) { this.port.postMessage({ error: String(e && e.stack || e) }); return false; }
  }
  render(outputs) {
    const out = outputs[0][0];
    const r = this.r;
    const periods = [ (r[0] | (r[4] << 8)) & 0xFFF, (r[1] | (r[5] << 8)) & 0xFFF, (r[2] | (r[6] << 8)) & 0xFFF ];
    const noiseP = (r[9] & 0x1F) || 1;
    const envP = (r[3] | (r[7] << 8)) || 1;
    const step = this.clock / sampleRate;   // chip clocks per sample
    for (let i = 0; i < out.length; i++) {
      this.acc += step;
      const clocks = Math.floor(this.acc); this.acc -= clocks;
      // the chip divides its clock by 16 for tone, noise and envelope steps
      for (let c = 0; c < 3; c++) { const p = (periods[c] || 1) * 16; this.tone[c] += clocks; while (this.tone[c] >= p) { this.tone[c] -= p; this.toneOut[c] ^= 1; } }
      const np = noiseP * 16; this.noiseCnt += clocks;
      while (this.noiseCnt >= np) { this.noiseCnt -= np; const bit = ((this.lfsr ^ (this.lfsr >> 3)) & 1); this.lfsr = (this.lfsr >> 1) | (bit << 16); this.noiseOut = this.lfsr & 1; }
      const ep = envP * 16; this.envCnt += clocks;   // one envelope step per 16 × EP clocks (a 16-step ramp = 256 × EP)
      while (this.envCnt >= ep) { this.envCnt -= ep; this.envTick(); }
      let mix = 0;
      for (let c = 0; c < 3; c++) {
        const toneOn = !(r[8] & (1 << c)), noiseOn = !(r[8] & (8 << c));
        const on = (toneOn ? this.toneOut[c] : 1) & (noiseOn ? this.noiseOut : 1);
        if (!toneOn && !noiseOn) continue;
        const v = r[11 + c];
        const level = (v & 0x30) ? this.envLevel : (v & 0x0F);
        mix += on ? this.dac[level] : 0;
      }
      out[i] = mix * 0.25;
    }
    return true;
  }
}
registerProcessor('psg', Psg);
`;

/** Offline check for the bridge: render `regs` for `seconds` and return the RMS. */
export async function renderRms(regs: ArrayLike<number>, seconds = 0.1, shape = true): Promise<number> {
  const ctx = new OfflineAudioContext(1, Math.round(44100 * seconds), 44100);
  const blob = new Blob([WORKLET], { type: 'application/javascript' });
  await ctx.audioWorklet.addModule(URL.createObjectURL(blob));
  const node = new AudioWorkletNode(ctx, 'psg', { processorOptions: { regs: Array.from(regs, v => v & 0xFF), shapeWritten: shape } });
  node.connect(ctx.destination);
  let err = '';
  node.port.onmessage = (e) => { if (e.data && e.data.error) err = e.data.error; };
  node.port.postMessage({ regs: Array.from(regs, v => v & 0xFF), shapeWritten: shape });
  const buf = await ctx.startRendering();
  await new Promise(r => setTimeout(r, 50));
  if (err) throw new Error(err);
  const d = buf.getChannelData(0);
  let s = 0; for (let i = 0; i < d.length; i++) s += d[i] * d[i];
  return Math.sqrt(s / d.length);
}

export class PsgPlayer {
  private ctx: AudioContext | null = null;
  private node: AudioWorkletNode | null = null;
  private ready = false;
  private regs = new Uint8Array(16);

  /** Call from a user gesture (browser autoplay policy). */
  async start(): Promise<void> {
    if (this.ctx) return;
    this.ctx = new AudioContext();
    const blob = new Blob([WORKLET], { type: 'application/javascript' });
    await this.ctx.audioWorklet.addModule(URL.createObjectURL(blob));
    this.node = new AudioWorkletNode(this.ctx, 'psg');
    this.node.connect(this.ctx.destination);
    this.regs[8] = 0x3F;
    this.ready = true;
    if (this.ctx.state === 'suspended') void this.ctx.resume();
  }

  get isReady(): boolean { return this.ready; }

  /** Push a full register image for this frame (regs[10] written re-triggers the envelope). */
  write(regs: ArrayLike<number>, shapeWritten: boolean): void {
    if (!this.node) return;
    for (let i = 0; i < 14; i++) this.regs[i] = regs[i] & 0xFF;
    this.node.port.postMessage({ regs: Array.from(this.regs), shapeWritten });
  }

  silence(): void {
    const r = new Uint8Array(16); r[8] = 0x38;
    this.write(r, false);
  }
}
