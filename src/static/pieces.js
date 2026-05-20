const PIECES = {
    0: [[1]],
    1: [[1,1]],
    2: [[1,1,1]],
    3: [[1],[1],[1]],
    4: [[1,1,1,1]],
    5: [[1,1],[1,0]],
    6: [[1,1],[0,1]],
    7: [[1,0],[1,1]],
    8: [[0,1],[1,1]],
    9: [[1,1,1],[0,1,0]],
    10: [[1,1,1],[1,0,0]],
    11: [[1,1,1],[0,0,1]],
    12: [[1,0],[1,1],[0,1]],
    13: [[0,1],[1,1],[1,0]],
    14: [[1,1],[1,1]],
    15: [[1,1,1,1,1]],
    16: [[1,1],[1,0],[1,0]],
    17: [[1,1],[0,1],[0,1]],
    18: [[1,0],[1,1],[0,1]],
    19: [[0,1],[1,1],[0,1]],
    20: [[1],[1],[1],[1],[1]],
};

const PLAYER_COLORS = ['blue', 'yellow', 'red', 'green'];

const PLAYER_HEX = {
    blue:   '#1f3a68',
    yellow: '#b8862a',
    red:    '#9c3a3a',
    green:  '#2f5a3f',
};

function renderPieceGrid(pieceId, container, opts = {}) {
    const shape = PIECES[pieceId];
    if (!shape) return;
    const cellSize = opts.cellSize || 6;
    const colorHex = opts.colorHex || '#14151a';
    const className = opts.className || 'piece-grid';
    container.innerHTML = '';
    const grid = document.createElement('div');
    grid.className = className;
    grid.style.gridTemplateRows = `repeat(${shape.length}, ${cellSize}px)`;
    grid.style.gridTemplateColumns = `repeat(${shape[0].length}, ${cellSize}px)`;
    shape.forEach(row => {
        row.forEach(cell => {
            const c = document.createElement('div');
            c.className = 'pc';
            c.style.width = `${cellSize}px`;
            c.style.height = `${cellSize}px`;
            c.style.background = cell ? colorHex : 'transparent';
            grid.appendChild(c);
        });
    });
    container.appendChild(grid);
}

/* Legacy alias used by gui.js render path */
function renderPieceDiv(pieceId, container) {
    renderPieceGrid(pieceId, container, { cellSize: 6, colorHex: 'currentColor' });
}
