const PIECES = {};
const PIECE_ORIENTATIONS = {};
const PIECE_ROTATIONS = {};
const PIECE_FLIPS = {};
let pieceCatalogPromise = null;

async function loadPieceCatalog() {
    if (pieceCatalogPromise) return pieceCatalogPromise;
    pieceCatalogPromise = fetch('/piece-catalog')
        .then(resp => resp.json())
        .then(data => {
            data.pieces.forEach(piece => {
                PIECES[piece.piece_id] = piece.shape;
                PIECE_ORIENTATIONS[piece.piece_id] = piece.orientations || [piece.shape];
                PIECE_ROTATIONS[piece.piece_id] = piece.rotate_to || [];
                PIECE_FLIPS[piece.piece_id] = piece.flip_to || [];
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
    const hasOrientation = Object.prototype.hasOwnProperty.call(opts, 'orientationIndex');
    const shape = hasOrientation ? getPieceOrientation(pieceId, opts.orientationIndex) : PIECES[pieceId];
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

function getPieceOrientation(pieceId, orientationIndex) {
    const orientations = PIECE_ORIENTATIONS[pieceId];
    if (orientationIndex !== undefined && orientations && orientations[orientationIndex]) return orientations[orientationIndex];
    return PIECES[pieceId];
}

function rotateOrientationIndex(pieceId, orientationIndex) {
    const rotations = PIECE_ROTATIONS[pieceId];
    if (rotations && rotations[orientationIndex] !== undefined) return rotations[orientationIndex];
    const shape = getPieceOrientation(pieceId, orientationIndex);
    if (!shape) return 0;
    const rotated = rotateGrid90(shape);
    return findOrientationIndex(pieceId, rotated, orientationIndex);
}

function flipOrientationIndex(pieceId, orientationIndex) {
    const flips = PIECE_FLIPS[pieceId];
    if (flips && flips[orientationIndex] !== undefined) return flips[orientationIndex];
    const shape = getPieceOrientation(pieceId, orientationIndex);
    if (!shape) return 0;
    const flipped = shape.map(row => row.slice().reverse());
    const horizontalIndex = findOrientationIndex(pieceId, flipped, orientationIndex);
    if (horizontalIndex !== orientationIndex) return horizontalIndex;
    const vertical = shape.slice().reverse();
    return findOrientationIndex(pieceId, vertical, orientationIndex);
}

function rotateGrid90(grid) {
    const rows = grid.length;
    const cols = grid[0].length;
    const result = Array.from({ length: cols }, () => Array(rows).fill(0));
    grid.forEach((row, r) => {
        row.forEach((cell, c) => {
            result[c][rows - 1 - r] = cell;
        });
    });
    return result;
}

function findOrientationIndex(pieceId, shape, fallbackIndex) {
    const orientations = PIECE_ORIENTATIONS[pieceId] || [];
    const key = gridKey(shape);
    const index = orientations.findIndex(orientation => gridKey(orientation) === key);
    return index >= 0 ? index : fallbackIndex;
}

function gridKey(grid) {
    return grid.map(row => row.join('')).join('/');
}

/* Legacy alias used by gui.js render path */
function renderPieceDiv(pieceId, container) {
    renderPieceGrid(pieceId, container, { cellSize: 6, colorHex: 'currentColor' });
}
