// Debug menu — a port tool, nothing to do with the ROM. Toggle with the
// backquote key (`) or the "Debug menu" button; it talks to the game only
// through window.__game.debug (see the bridge in src/main.ts).

interface DebugApi {
  flags: { god: boolean; noclip: boolean; noSpawn: boolean };
  set: (k: 'god' | 'noclip' | 'noSpawn', v: boolean) => void;
  goLevel: (l: number) => void;
  goTile: (col: number, row: number) => void;
  objects: () => { col: number; row: number; type: number }[];
  level: () => number;
  levels: () => number;
  giveKey: () => void;
  fillHand: () => void;
  heal: () => void;
  setLives: (n: number) => void;
  killFoes: () => void;
  spawn: (type: 'phantom_knight' | 'sorcerer') => void;
  wizard: () => { active: boolean; cpu: boolean } | undefined;
  allSpells: () => void;
  reviveWizard: () => void;
  setCpuWizard: (on: boolean) => void;
  fastFeet: () => void;
  invincible: () => void;
  state: () => { x: number; y: number };
}

// ROM object types (assets/objects.json): 0-6 treasures, 7 key, 8 lantern,
// 9 chest, 10 checkered marker (down stairs), 11 up stairs, 13-16 scrolls.
const TYPE_LABELS: Record<number, string> = {
  7: 'Key', 8: 'Lantern', 9: 'Chest', 10: 'Stairs marker', 11: 'Up stairs',
  13: 'Scroll (move)', 14: 'Scroll (move)', 15: 'Scroll: Fireball', 16: 'Scroll: Heal',
};

export function installDebugMenu(getApi: () => DebugApi | undefined): void {
  const panel = document.createElement('div');
  panel.id = 'debug-menu';
  panel.style.cssText = 'display:none;position:fixed;top:12px;right:12px;width:300px;max-height:92vh;overflow:auto;background:#1b1b1b;color:#ddd;border:1px solid #555;padding:10px;font:12px monospace;z-index:10;box-shadow:0 0 12px #000';
  document.body.appendChild(panel);

  const button = document.createElement('button');
  button.textContent = 'Debug menu (`)';
  button.style.cssText = 'font:11px monospace;margin:4px';
  const controls = document.querySelector('.controls');
  (controls ?? document.body).appendChild(button);

  let open = false;
  const toggle = () => { open = !open; panel.style.display = open ? 'block' : 'none'; if (open) rebuild(); };
  button.addEventListener('click', toggle);
  window.addEventListener('keydown', e => { if (e.code === 'Backquote') { e.preventDefault(); toggle(); } });

  const row = (...els: Node[]) => { const d = document.createElement('div'); d.style.margin = '4px 0'; els.forEach(e => d.appendChild(e)); return d; };
  const btn = (label: string, fn: () => void) => { const b = document.createElement('button'); b.textContent = label; b.style.cssText = 'font:11px monospace;margin:2px'; b.addEventListener('click', () => { fn(); rebuild(); }); return b; };
  const check = (label: string, get: () => boolean, set: (v: boolean) => void) => {
    const l = document.createElement('label'); l.style.display = 'block';
    const c = document.createElement('input'); c.type = 'checkbox'; c.checked = get();
    c.addEventListener('change', () => set(c.checked));
    l.appendChild(c); l.appendChild(document.createTextNode(' ' + label));
    return l;
  };
  const h = (t: string) => { const e = document.createElement('div'); e.textContent = t; e.style.cssText = 'color:#9f9;margin:8px 0 2px;border-bottom:1px solid #333'; return e; };

  function rebuild() {
    panel.innerHTML = '';
    const api = getApi();
    if (!api) { panel.textContent = 'Start a game first (pick 1/2/3, then ENTER).'; return; }
    const f = api.flags;
    panel.appendChild(h('Cheats'));
    panel.appendChild(check('God mode (no injuries, Prince + Wizard)', () => f.god, v => api.set('god', v)));
    panel.appendChild(check('Noclip (walls and doors ignored; stairs still work)', () => f.noclip, v => api.set('noclip', v)));
    panel.appendChild(check('No spawns', () => f.noSpawn, v => api.set('noSpawn', v)));
    panel.appendChild(row(btn('Heal both', api.heal), btn('Lives = 9', () => api.setLives(9)), btn('Lives = 0', () => api.setLives(0))));
    panel.appendChild(row(btn('Give key', api.giveKey), btn('Fill hand (6)', api.fillHand)));
    panel.appendChild(row(btn('Fast feet', api.fastFeet), btn('Invincible', api.invincible)));

    panel.appendChild(h('Level'));
    const lv = document.createElement('div');
    for (let i = 0; i < api.levels(); i++) lv.appendChild(btn(`${i + 1}${api.level() === i ? ' *' : ''}`, () => api.goLevel(i)));
    panel.appendChild(lv);

    panel.appendChild(h('Go to (this level)'));
    const go = document.createElement('div');
    for (const o of api.objects().filter(o => o.type >= 7)) go.appendChild(btn(`${TYPE_LABELS[o.type] ?? 'type ' + o.type} (${o.col},${o.row})`, () => api.goTile(o.col, o.row)));
    panel.appendChild(go);
    const st = api.state();
    const pos = document.createElement('div'); pos.textContent = `Prince at tile (${Math.floor(st.x / 8)},${Math.floor(st.y / 8)})`; pos.style.color = '#888';
    panel.appendChild(pos);
    const inCol = document.createElement('input'); inCol.type = 'number'; inCol.style.width = '50px'; inCol.value = String(Math.floor(st.x / 8));
    const inRow = document.createElement('input'); inRow.type = 'number'; inRow.style.width = '50px'; inRow.value = String(Math.floor(st.y / 8));
    panel.appendChild(row(document.createTextNode('col '), inCol, document.createTextNode(' row '), inRow, btn('Go', () => api.goTile(Number(inCol.value), Number(inRow.value)))));

    panel.appendChild(h('Foes'));
    panel.appendChild(row(btn('Spawn knight', () => api.spawn('phantom_knight')), btn('Spawn sorcerer', () => api.spawn('sorcerer')), btn('Kill all', api.killFoes)));

    const w = api.wizard();
    if (w && w.active) {
      panel.appendChild(h('Wizard'));
      panel.appendChild(check('CPU plays the Wizard', () => w.cpu, v => api.setCpuWizard(v)));
      panel.appendChild(row(btn('All spells ×10', api.allSpells), btn('Revive / recall', api.reviveWizard)));
    }
  }
}