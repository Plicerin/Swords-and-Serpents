// Extract the ROM's per-level object tables into assets/objects.json.
//
// Ground truth (docs/HANDOVER.md ROM finding #10):
//   $64DE  16 records per level × 4 levels, 2 words each: (column, row)
//   $6580  object TYPE, 5-bit packed two per word (low field = even object,
//          high field (>>5) = odd object), indexed by global object number
//   $655E  BACKTAB word per type, 2 bytes per type (little-endian, SDBD read)
// The ROM image is 16-bit big-endian words starting at $5000.
import { readFileSync, writeFileSync } from 'node:fs';

const rom = readFileSync(new URL('../Swords and Serpents.bin', import.meta.url));
const word = (addr) => { const i = (addr - 0x5000) * 2; return (rom[i] << 8) | rom[i + 1]; };
const sdbd = (addr) => (word(addr) & 0xFF) | ((word(addr + 1) & 0xFF) << 8);

const TYPES = 18;
const typeWord = Array.from({ length: TYPES }, (_, t) => sdbd(0x655E + t * 2));
const levels = [];
for (let L = 0; L < 4; L++) {
  const objects = [];
  for (let i = 0; i < 16; i++) {
    const k = L * 16 + i;
    const packed = word(0x6580 + (k >> 1));
    const type = (k & 1) ? (packed >> 5) & 0x1F : packed & 0x1F;
    objects.push({ col: word(0x64DE + k * 2), row: word(0x64DF + k * 2), type, word: typeWord[type] });
  }
  levels.push(objects);
}

const out = {
  source: 'Swords and Serpents.bin — tables at $64DE (positions), $6580 (types), $655E (BACKTAB words)',
  types: {
    '0-6': 'treasures (GRAM cards 15-21); G_0180 bit = present, G_019D bit = collected',
    '7': 'KEY (card 22) — sets G_019D bit 7 of its level; opens that level\'s stairs',
    '8': 'Lantern of Life (card 14) — ENTER cures (player colour -> white)',
    '9': 'treasure chest (card 12, level 0 only) — ENTER stores what is in hand',
    '10': 'locked stairway marker (card 13, checkered) — ENTER with the key writes $084B (card 9, DOWN stairs) one column to the RIGHT',
    '11': 'DOWN stairs (card 9) — never in the table; only ever written by the ENTER above',
    '12': 'UP stairs (card 10) — walk onto it: level-1',
    '13-16': 'card 11 with bits 14-15 varying (four per level; purpose not yet captured)',
  },
  typeWord,
  levels,
};
writeFileSync(new URL('../assets/objects.json', import.meta.url), JSON.stringify(out, null, 1));
console.log('wrote assets/objects.json', levels.map(l => l.length));
