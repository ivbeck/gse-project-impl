let selectedPiece = null;
let currentOrientation = 0;
let legalMoves = [];

async function loadState() {
    try {
        const resp = await fetch('/state');
        const state = await resp.json();
        renderBoard(state.board);
        renderTray(state.players[state.current_player_id]);
        renderDashboard(state);
        document.getElementById('current-player').textContent = state.players[state.current_player_id].color;
    } catch (e) {
        console.error('Failed to load state:', e);
    }
}

function renderBoard(board) {
    const container = document.getElementById('board');
    container.innerHTML = '';
    container.style.gridTemplateColumns = `repeat(${board[0].length}, 28px)`;
    board.forEach((row, ri) => {
        row.forEach((cell, ci) => {
            const div = document.createElement('div');
            div.className = 'cell';
            if (cell !== null) {
                div.classList.add(PLAYER_COLORS[cell]);
            }
            div.dataset.row = ri;
            div.dataset.col = ci;
            div.onclick = () => onCellClick(ri, ci);
            container.appendChild(div);
        });
    });
}

function renderTray(player) {
    const tray = document.getElementById('player-tray');
    tray.innerHTML = '';
    player.remaining_pieces.forEach(pid => {
        const div = document.createElement('div');
        div.className = 'piece';
        div.dataset.pieceId = pid;
        div.onclick = () => selectPiece(pid);
        div.style.color = PLAYER_COLORS[player.id];
        renderPieceDiv(pid, div);
        tray.appendChild(div);
    });
}

function renderDashboard(state) {
    const dash = document.getElementById('dashboard');
    let html = '<table><tr><th>Player</th><th>Score</th><th>Pieces</th></tr>';
    state.players.forEach(p => {
        const score = state.scores.find(s => s.player_id === p.id);
        html += `<tr><td style="color:${PLAYER_COLORS[p.id]}">${p.color}</td><td>${score ? score.score : 0}</td><td>${p.remaining_pieces.length}</td></tr>`;
    });
    html += '</table>';
    dash.innerHTML = html;
}

function selectPiece(pieceId) {
    selectedPiece = pieceId;
    currentOrientation = 0;
    document.querySelectorAll('.piece').forEach(p => p.classList.remove('selected'));
    document.querySelector(`[data-piece-id="${pieceId}"]`).classList.add('selected');
}

function onCellClick(row, col) {
    if (!selectedPiece) return;
    submitMove({
        player_id: 0,
        piece_id: selectedPiece,
        orientation_index: currentOrientation,
        row: row,
        col: col,
    });
}

async function submitMove(move) {
    try {
        const resp = await fetch('/move', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(move)
        });
        const result = await resp.json();
        if (result.ok) {
            loadState();
        } else {
            alert(result.error || 'Illegal move');
        }
    } catch (e) {
        console.error('Failed to submit move:', e);
    }
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'r' || e.key === 'R') {
        currentOrientation = (currentOrientation + 1) % 4;
    }
    if (e.key === 'f' || e.key === 'F') {
        currentOrientation += 2;
        currentOrientation %= 4;
    }
});

setInterval(loadState, 2000);
loadState();