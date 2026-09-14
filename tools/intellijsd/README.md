# Intellijsd — scriptable browser oracle

A local copy of **Intellijsd** (Paul Vern's pure-JS Intellivision emulator,
https://paulvern.free.nf/intellijsd.html — CP1610 + STIC + AY-3-8914, zero
dependencies, single HTML file). Saved here because the host sits behind a
JS cookie challenge that blocks plain fetches, and because we patch it.

**Why it matters:** jzIntv has no debugger-level input injection, so every
player-input-gated behaviour (facing, speed, pickups, stairs, title flow)
was unobservable. Intellijsd's controller goes through `psg.setController`
with the real port encodings, and the whole machine is plain JS — so a
script can boot the game legitimately, hold the disc, and read memory every
frame. First result: the player facing map, walking speed and sword
geometry (HANDOVER.md ROM finding #6), all of which corrected knight-derived
guesses.

## Local patch

The upstream page exposes no globals. `intellijsd.html` here adds
`window.ijsd` at the end of the script (grep `oracle hook`):

| member | purpose |
|---|---|
| `memory, psg, cpu, display, state` | the live core objects |
| `read(addr)` | read a word (honours cart windows) |
| `snapshot()` | copy of the whole 64K word space |
| `runFrames(n)` | run exactly n frames (VBLANK IRQ + 14934 cycles each), synchronous |
| `setPad(sector, keys)` | controller 1 — disc sector 0..15 (0=N,2=NE,4=E,6=SE,8=S,10=SW,12=W,14=NW) or `null`; keys from `'0'..'9','C','E','L','T','R'` |
| `loadBytes(kind, u8)` | load `'exec' | 'grom' | 'cart'` from a Uint8Array |
| `discMasks, controllerMasks, discNames` | the port-byte tables |

## Recipe (run inside the page via the Browser pane's javascript tool)

```js
// serve the project root (Vite dev server, port 4040) and open
// http://localhost:4040/tools/intellijsd/intellijsd.html
const u8 = async u => new Uint8Array(await (await fetch(u)).arrayBuffer());
await ijsd.loadBytes('exec', await u8('/exec.bin'));
await ijsd.loadBytes('grom', await u8('/grom.bin'));
await ijsd.loadBytes('cart', await u8('/Swords and Serpents.bin'));
document.getElementById('power-btn').click();   // power on
document.getElementById('reset-btn').click();   // reset → CPU runs from $1000
ijsd.runFrames(240);                            // title screen
const press = (k) => { ijsd.setPad(null, [k]); ijsd.runFrames(8); ijsd.setPad(null, []); ijsd.runFrames(30); };
press('1'); press('E');                         // "1 PLAYER" → ENTER → in the dungeon
ijsd.setPad(6, []); ijsd.runFrames(40);         // hold disc SE for 40 frames
ijsd.read(0x325) & 0xFF;                        // player X
```

Screen text can be decoded from BACKTAB (`$0200`, 20×12): GROM card
`c` → `String.fromCharCode(c + 32)`.

## Caveats

- `runFrames` is independent of `requestAnimationFrame`, so it works in a
  hidden tab; the on-page canvas only refreshes when the tab is visible.
- MOB X (`$0000+i`) is a *screen* position (player is camera-centred and
  oscillates 81–88 as the camera snaps); use per-frame deltas of `$0325` /
  `$032D` for speed, not absolute values.
- Fidelity is Intellijsd's own; its MOB A-register for the player (`$0987`)
  matches our jzIntv captures exactly, but treat it as a second oracle, not
  a replacement — cross-check anything surprising against jzIntv.
- This is a third-party work; keep it under `tools/` unmodified apart from
  the hook, and credit the author if it is redistributed.
