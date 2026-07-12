/**
 * Swords & Serpents Game Engine
 * Handles player state, movement, collision, and game loop
 */

class Player {
    constructor() {
        this.x = 10; // Tile coordinates
        this.y = 6;
        this.speed = 1; // Tiles per frame
        this.direction = 0; // 0=N, 1=E, 2=S, 3=W
        this.frame = 0;
    }
    
    move(direction, backtabGrid) {
        const moves = {
            'ArrowLeft': [-1, 0],
            'a': [-1, 0],
            'ArrowRight': [1, 0],
            'd': [1, 0],
            'ArrowUp': [0, -1],
            'w': [0, -1],
            'ArrowDown': [0, 1],
            's': [0, 1]
        };
        
        const move = moves[direction];
        if (!move) return false;
        
        const newX = this.x + move[0];
        const newY = this.y + move[1];
        
        // Check bounds
        if (newX < 0 || newX >= 20 || newY < 0 || newY >= 12) {
            return false;
        }
        
        // Check collision with wall
        const tileValue = backtabGrid[newY][newX];
        if (tileValue !== 0 && tileValue !== 0x1603) {
            return false;
        }
        
        this.x = newX;
        this.y = newY;
        this.direction = ['ArrowLeft', 'a'].includes(direction) ? 3 :
                         ['ArrowRight', 'd'].includes(direction) ? 1 :
                         ['ArrowUp', 'w'].includes(direction) ? 0 : 2;
        this.frame = (this.frame + 1) % 2;
        return true;
    }
}

class GameEngine {
    constructor() {
        this.player = new Player();
        this.background = null;
        this.currentRoom = 0;
        this.renderer = null;
        this.keys = {};
    }
    
    loadRoom(roomIndex, backtabGrid, gramMem, grom) {
        this.background = backtabGrid;
        this.currentRoom = roomIndex;
        if (!this.renderer) {
            this.renderer = new RoomRenderer(grom, gramMem);
        }
    }
    
    update() {
        // Handle input
        if (this.keys['ArrowLeft'] || this.keys['a']) {
            this.player.move('ArrowLeft', this.background);
        } else if (this.keys['ArrowRight'] || this.keys['d']) {
            this.player.move('ArrowRight', this.background);
        } else if (this.keys['ArrowUp'] || this.keys['w']) {
            this.player.move('ArrowUp', this.background);
        } else if (this.keys['ArrowDown'] || this.keys['s']) {
            this.player.move('ArrowDown', this.background);
        }
    }
    
    render(ctx) {
        // Clear canvas
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Render room
        if (this.background && this.renderer) {
            this.renderer.renderCanvas(ctx, this.background);
        }
        
        // Render player (simple colored square for now)
        ctx.fillStyle = '#FFF';
        ctx.fillRect(
            this.player.x * 32 + 4,
            this.player.y * 32 + 4,
            24, 24
        );
    }
}

// Room Renderer for GameEngine
class RoomRenderer {
    constructor(grom, gramMem) {
        this.grom = grom;
        this.gramMem = gramMem;
    }
    
    renderCanvas(ctx, backtabGrid) {
        const tileSize = 8;
        const zoom = 4;
        
        for (let row = 0; row < 12; row++) {
            for (let col = 0; col < 20; col++) {
                const word = backtabGrid[row][col];
                const { card, isGram, fg, bg } = decodeFgbgWord(word);
                
                const fgColor = PALETTE[fg & 0x7];
                const bgColor = PALETTE[bg & 0x7];
                
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
                
                const x0 = col * tileSize * zoom;
                const y0 = row * tileSize * zoom;
                
                for (let y = 0; y < tileSize; y++) {
                    const byte = tileBytes[y] || 0;
                    for (let x = 0; x < tileSize; x++) {
                        const color = ((byte >> (7 - x)) & 1) ? fgColor : bgColor;
                        ctx.fillStyle = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
                        ctx.fillRect(x0 + x * zoom, y0 + y * zoom, zoom, zoom);
                    }
                }
            }
        }
    }
}

// Palette data
const PALETTE = [
    [0x00, 0x00, 0x00],  // black
    [0x14, 0x38, 0xFF],  // blue
    [0xE3, 0x5B, 0x0E],  // red
    [0xCB, 0xF1, 0x68],  // tan
    [0x26, 0x94, 0x28],  // dark green
    [0x07, 0xC2, 0x00],  // green
    [0xFF, 0xFF, 0x01],  // yellow
    [0xFF, 0xFF, 0xFF],  // white
];

// BACKTAB decoding
function decodeFgbgWord(word) {
    const grIdx = word & 0x9F8;
    const card = (grIdx >> 3) & 0x3F;
    const isGram = (grIdx & 0x800) !== 0;
    const fg = word & 0x7;
    const bg = ((word >> 9) & 0xB) | ((word >> 11) & 0x4);
    return { card, isGram, fg, bg };
}

// GROM class
class GROM {
    constructor(data) {
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

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { GameEngine, Player, RoomRenderer, GROM, decodeFgbgWord };
}