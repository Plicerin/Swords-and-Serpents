// One-voice effect sequencer over the PSG model — the ROM's EXEC sound
// processor plays a single effect at a time and a new one cuts the old
// (captured: a fireball's flight noise stops the moment the hit sound
// starts). The fireball flight is the lowest priority: it only sounds when
// nothing else is playing and while a fireball is alive.
import { PsgPlayer } from './psg';
import { Sound, fireballFrame } from './sounds';

export class Sfx {
  private player = new PsgPlayer();
  private current: Sound | null = null;
  private frame = 0;
  private wasSilent = false;

  start(): Promise<void> { return this.player.start(); }

  play(sound: Sound): void {
    this.current = sound;
    this.frame = 0;
  }

  /** Call once per game frame. `fireballAge` = frames the oldest live fireball has flown, or -1. */
  tick(fireballAge: number): void {
    if (!this.player.isReady) return;
    if (this.current) {
      const f = this.current[this.frame++];
      this.player.write(f.regs, !!f.shape);
      this.wasSilent = false;
      if (this.frame >= this.current.length) this.current = null;
      return;
    }
    if (fireballAge >= 0) {
      this.player.write(fireballFrame(fireballAge), false);
      this.wasSilent = false;
      return;
    }
    if (!this.wasSilent) { this.player.silence(); this.wasSilent = true; }
  }
}
