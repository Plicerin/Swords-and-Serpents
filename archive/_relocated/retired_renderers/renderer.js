/**
 * Swords & Serpents JavaScript Port - Core Renderer
 * Implements the Intellivision STIC FG/BG mode rendering pipeline.
 */

// -- Intellivision Palette (jzIntv verified) -----------------------------------
const PALETTE = [
    [0x00, 0x00, 0x00],  // 0 black
    [0x14, 0x38, 0xFF],  // 1 blue
    [0xE3, 0x5B, 0x0E],  // 2 red
    [0xCB, 0xF1, 0x68],  // 3 tan
    [0x26, 0x94, 0x28],  // 4 dark green
    [0x07, 0xC2, 0x00],  // 5 green
    [0xFF, 0xFF, 0x01],  // 6 yellow
    [0xFF, 0xFF, 0xFF],  // 7 white
];

const PASTEL_PALETTE = [
    [0xC8, 0xC8, 0xC8],  // 0 pastel black (light gray)
    [0x23, 0xB8, 0xFF],  // 1 pastel blue (light cyan)
    [0xFD, 0x99, 0x18],  // 2 pastel red (orange)
    [0x3A, 0x8A, 0x00],  // 3 pastel tan (dark olive green)
    [0xF0, 0x46, 0x3C],  // 4 pastel dark green (pinkish red)
    [0xD3, 0x83, 0xFF],  // 5 pastel green (lavender)
    [0x48, 0xF6, 0x01],  // 6 pastel yellow (bright green)
    [0xB8, 0x11, 0x78],  // 7 pastel white (magenta)
];

const DEFAULT_BG = [0, 0, 0];

// -- GRAM reconstruction from ROM RLE -----------------------------------------
function reconstructDungeonGram(romData, rleAddr = 0x61E7) {
    const gramMem = {};
    
    // Read DECLE (16-bit word) from ROM
    const readDecle = (addr) => {
        const off = (addr - 0x5000) * 2;
        if (off + 1 < romData.length) {
            return (romData[off] << 8) | romData[off + 1];
        }
        return 0;
    };
    
    let a = rleAddr;
    const startOff = readDecle(a); a += 1;
    const count = readDecle(a); a += 1;
    
    let addr = 0x3800 + startOff;
    for (let i = 0; i < count; i++) {
        const w = readDecle(a); a += 1;
        const rep = ((w >> 8) & 3) + 1;
        const byte = w & 0xFF;
        for (let j = 0; j < rep; j++) {
            gramMem[addr] = byte;
            addr += 1;
        }
    }
    
    return gramMem;
}

// -- BACKTAB decoding ----------------------------------------------------------
function decodeFgbgWord(word) {
    /**
     * Decode a BACKTAB word in STIC Foreground/Background mode.
     * Returns {card_index, is_gram, fg_color, bg_color}
     */
    const grIdx = word & 0x9F8;
    const card = (grIdx >> 3) & 0x3F;
    const isGram = (grIdx & 0x800) !== 0;
    const fg = word & 0x7;
    const bg = ((word >> 9) & 0xB) | ((word >> 11) & 0x4);
    return { card, isGram, fg, bg };
}

// -- GROM loading --------------------------------------------------------------
class GROM {
    constructor(data) {
        // GROM is 256 cards × 8 bytes each
        this.cards = [];
        for (let i = 0; i < 256; i++) {
            const base = i * 8;
            this.cards[i] = data.slice(base, base + 8);
        }
    }
    
    getCard(cardIndex) {
        return this.cards[cardIndex & 0xFF] || new Uint8Array(8);
    }
}

// -- Room Renderer -------------------------------------------------------------
class RoomRenderer {
    constructor(grom, gramMem) {
        this.grom = grom;
        this.gramMem = gramMem;
        this.tileSize = 8;
        this.zoom = 4;
        this.cols = 20;
        this.rows = 12;
    }
    
    renderCanvas(canvas, backtabGrid) {
        const ctx = canvas.getContext('2d');
        const w = canvas.width;
        const h = canvas.height;
        
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, w, h);
        
        for (let row = 0; row < this.rows; row++) {
            for (let col = 0; col < this.cols; col++) {
                const word = backtabGrid[row][col];
                const { card, isGram, fg, bg } = decodeFgbgWord(word);
                
                const fgColor = PALETTE[fg & 0x7];
                const bgColor = PALETTE[bg & 0x7];
                
                // Get tile bitmap
                let tileBytes;
                if (isGram) {
                    const base = 0x3800 + (card & 0x3F) * 8;
                    tileBytes = [];
                    for (let r = 0; r < 8; r++) {
                        tileBytes[r] = this.gramMem[base + r] & 0xFF;
                    }
                } else {
                    tileBytes = this.grom.getCard(card);
                }
                
                // Draw tile
                const x0 = col * this.tileSize * this.zoom;
                const y0 = row * this.tileSize * this.zoom;
                
                for (let y = 0; y < this.tileSize; y++) {
                    const byte = tileBytes[y] || 0;
                    for (let x = 0; x < this.tileSize; x++) {
                        const color = ((byte >> (7 - x)) & 1) ? fgColor : bgColor;
                        for (let dy = 0; dy < this.zoom; dy++) {
                            for (let dx = 0; dx < this.zoom; dx++) {
                                ctx.fillStyle = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
                                ctx.fillRect(x0 + x * this.zoom + dx, y0 + y * this.zoom + dy, 1, 1);
                            }
                        }
                    }
                }
            }
        }
    }
}

// -- Main API ----------------------------------------------------------------
class SSGameEngine {
    constructor() {
        this.grom = null;
        this.gramMem = null;
        this.currentRoom = 0;
        this.renderer = null;
    }
    
    async loadROMs(romUrl, gromUrl) {
        const romResponse = await fetch(romUrl);
        const romData = new Uint8Array(await romResponse.arrayBuffer());
        
        const gromResponse = await fetch(gromUrl);
        const gromData = new Uint8Array(await gromResponse.arrayBuffer());
        
        this.grom = new GROM(gromData);
        this.gramMem = reconstructDungeonGram(romData);
        this.renderer = new RoomRenderer(this.grom, this.gramMem);
        
        return true;
    }
    
    renderRoom(canvas, roomIndex, backtabGrid) {
        if (!this.renderer) {
            throw new Error('ROMs not loaded');
        }
        this.currentRoom = roomIndex;
        this.renderer.renderCanvas(canvas, backtabGrid);
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SSGameEngine, RoomRenderer, GROM, reconstructDungeonGram, decodeFgbgWord };
}