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

function renderPieceDiv(pieceId, container) {
    const shape = PIECES[pieceId];
    if (!shape) return;
    container.innerHTML = '';
    container.style.display = 'grid';
    container.style.gridTemplateRows = `repeat(${shape.length}, 20px)`;
    container.style.gridTemplateColumns = `repeat(${shape[0].length}, 20px)`;
    shape.forEach(row => {
        row.forEach(cell => {
            const div = document.createElement('div');
            div.style.width = '20px';
            div.style.height = '20px';
            div.style.background = cell ? 'currentColor' : 'transparent';
            container.appendChild(div);
        });
    });
}