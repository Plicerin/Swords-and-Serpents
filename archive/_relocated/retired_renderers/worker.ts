import {
  renderRoom,
  RenderOptions,
  renderAnimatedDungeon,
  parseHexDump
} from './renderer.js';

type Message =
  | { type: 'renderRoom'; backtab: Uint8Array; grom: Uint8Array; gram: Uint8Array; opts: RenderOptions }
  | { type: 'renderAnim'; backtabs: Uint8Array[]; grom: Uint8Array; gram: Uint8Array; opts: RenderOptions };

self.onmessage = async (ev: MessageEvent<Message>) => {
  const msg = ev.data;
  if (msg.type === 'renderRoom') {
    const canvas = await renderRoom(msg.backtab, msg.grom, msg.gram, msg.opts);
    const bitmap = await createImageBitmap(canvas);
    // @ts-ignore – postMessage in worker
    (self as any).postMessage({ type: 'roomResult', bitmap }, [bitmap]);
  } else if (msg.type === 'renderAnim') {
    const blob = await renderAnimatedDungeon(
      msg.backtabs,
      msg.grom,
      msg.gram,
      msg.opts.referenceGif,
      msg.opts.mobInfo
    );
    // @ts-ignore
    (self as any).postMessage({ type: 'animResult', blob });
  }
};
