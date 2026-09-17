// Renders the game's own ROM art (GRAM cards, player frames, the Wizard)
// as crisp SVGs for the landing page (public/img). Run: node scripts/render_page_art.mjs
import fs from 'node:fs';
const gram = JSON.parse(fs.readFileSync('assets/gram_tiles.json', 'utf8'));   // 512 bytes, 8 per card
const warrior = JSON.parse(fs.readFileSync('assets/player_sprites.json', 'utf8')).warrior;
const WIZARD = [0x6d,0x3e,0x7f,0xf6,0xf1,0xd8,0x88,0xa8,0xa8,0x88,0xd8,0xf1,0xf6,0x7f,0x3e,0x6d];
const SORCERER = [0x50,0x70,0x38,0x70,0x3a,0xf5,0x72,0xfb,0xde,0xce,0xd6,0xd7,0x47,0xfd,0x30,0x00];
const OLIVE = '#546E00', GREEN = '#00A756', RED = '#FF3D10', TAN = '#C9D464', WHITE = '#FFFCFF', LBLUE = '#5ACBFF', BLACK = '#0C0005';

function rects(bytes, x0, y0, w, rowH, color, mirror = false) {
  let out = '';
  bytes.forEach((b, r) => { for (let c = 0; c < w; c++) { const bit = mirror ? (b >> c) & 1 : (b >> (7 - c)) & 1; if (bit) out += `<rect x="${x0 + c}" y="${y0 + r * rowH}" width="1" height="${rowH}" fill="${color}"/>`; } });
  return out;
}
const card = (n) => gram.slice(n * 8, n * 8 + 8);
const svg = (w, h, body, bg = 'none') => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" shape-rendering="crispEdges">${bg !== 'none' ? `<rect width="${w}" height="${h}" fill="${bg}"/>` : ''}${body}</svg>`;

// The Serpent: 6×3 cards (finding #16), belly (card 29) on red.
const layout = [[null, null, 24, 25, 26, null], [27, 28, 29, 29, 29, 30], [null, null, 31, 32, 33, null]];
let serp = '';
layout.forEach((row, r) => row.forEach((n, c) => { if (n === null) return; if (n === 29) serp += `<rect x="${c * 8}" y="${r * 8}" width="8" height="8" fill="${RED}"/>`; serp += rects(card(n), c * 8, r * 8, 8, 1, GREEN); }));
fs.writeFileSync('public/img/serpent.svg', svg(48, 24, serp, OLIVE));

// The Prince (frame 0, east) with his sword; a Phantom Knight (black); Nilrem; a Red Sorcerer.
const prince = rects(warrior[0], 0, 0, 8, 0.5, WHITE) + `<rect x="8" y="3.5" width="8" height="0.5" fill="#5ACBFF"/>`;
fs.writeFileSync('public/img/prince.svg', svg(16, 8, prince));
fs.writeFileSync('public/img/knight.svg', svg(16, 8, rects(warrior[0], 0, 0, 8, 0.5, BLACK) + `<rect x="8" y="3.5" width="8" height="0.5" fill="${BLACK}"/>`));
fs.writeFileSync('public/img/wizard.svg', svg(8, 8, rects(WIZARD, 0, 0, 8, 0.5, LBLUE)));
fs.writeFileSync('public/img/sorcerer.svg', svg(8, 8, rects(SORCERER, 0, 0, 8, 0.5, RED)));
fs.writeFileSync('public/img/key.svg', svg(8, 8, rects(card(22), 0, 0, 8, 1, TAN)));
fs.writeFileSync('public/img/scroll.svg', svg(8, 8, rects(card(11), 0, 0, 8, 1, TAN)));
fs.writeFileSync('public/img/chest.svg', svg(8, 8, rects(card(12), 0, 0, 8, 1, TAN)));
console.log('wrote public/img/*.svg');