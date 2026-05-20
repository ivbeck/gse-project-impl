const PIECES = {};
let pieceCatalogPromise = null;

async function loadPieceCatalog() {
    if (pieceCatalogPromise) return pieceCatalogPromise;
    pieceCatalogPromise = fetch('/piece-catalog')
        .then(resp => resp.json())
        .then(data => {
            data.pieces.forEach(piece => {
                PIECES[piece.piece_id] = piece.shape;
            });
        });
    return pieceCatalogPromise;
}

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
