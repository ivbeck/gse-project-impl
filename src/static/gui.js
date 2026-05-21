let selectedPiece = null;
let currentOrientation = 0;
let legalMoves = [];
let currentPlayerId = 0;
let roundCounter = 1;
let currentBoard = [];
let hoverAnchor = null;
let gameStarted = false;
let currentControllerType = 'human';

const HOVER_PREVIEW_CLASSES = [
    'hover-preview-valid',
    'hover-preview-invalid',
    'hover-preview-occupied',
];

const COLOR_LABEL = { blue: 'Blue', yellow: 'Yellow', red: 'Red', green: 'Green' };

async function loadState() {
    try {
        const resp = await fetch('/state');
        const state = await resp.json();
        gameStarted = Boolean(state.started);
        updateSessionVisibility(state);
        if (!gameStarted) {
            currentControllerType = 'human';
            updatePassButton(state);
            return;
        }
        await loadPieceCatalog();
        currentPlayerId = state.current_player_id;
        const currentPlayer = playerForId(state, currentPlayerId);
        currentControllerType = (currentPlayer && currentPlayer.controller_type) || 'human';
        renderBoard(state.board);
        renderTray(currentPlayer);
        renderDashboard(state);
        updateTurnBanner(state);
        updatePassButton(state);
    } catch (e) {
        console.error('Failed to load state:', e);
    }
}

function playerForId(state, playerId) {
    return state.players.find(player => player.id === playerId) || state.players[playerId];
}

function controllerLabel(controllerType) {
    return controllerType === 'ai' ? 'AI' : 'Human';
}

function currentPlayerCanAct(state) {
    return gameStarted && currentControllerType === 'human' && (!state || state.game_status !== 'FINISHED');
}

function updateSessionVisibility(state) {
    const startScreen = document.getElementById('start-screen');
    const gameScreen = document.getElementById('game-screen');
    if (startScreen) startScreen.classList.toggle('hidden', Boolean(state.started));
    if (gameScreen) gameScreen.classList.toggle('hidden', !state.started);
    const statusLabel = document.querySelector('.status-label');
    if (statusLabel) statusLabel.textContent = state.started ? 'Live Session' : 'Setup';
}

function updatePassButton(state) {
    const passButton = document.getElementById('pass-button');
    if (!passButton) return;
    passButton.disabled = !currentPlayerCanAct(state);
}

function updateTurnBanner(state) {
    const player = playerForId(state, state.current_player_id);
    const colorKey = player.color.toLowerCase();
    const label = COLOR_LABEL[colorKey] || player.color;
    document.getElementById('current-player').textContent = label;
    const controller = document.getElementById('current-controller');
    if (controller) controller.textContent = controllerLabel(player.controller_type || 'human');
    const swatch = document.getElementById('turn-swatch');
    if (swatch) swatch.style.background = PLAYER_HEX[colorKey] || '#14151a';
    /* Round counter: estimate from total placed pieces */
    const totalPlayers = state.players.length || 4;
    const used = state.players.reduce((acc, p) => acc + (21 - p.remaining_pieces.length), 0);
    const round = Math.floor(used / totalPlayers) + 1;
    const counter = document.getElementById('round-counter');
    if (counter) counter.textContent = String(round).padStart(2, '0');
}

function renderBoard(board) {
    const container = document.getElementById('board');
    currentBoard = board.map(row => row.slice());
    container.innerHTML = '';
    const cols = board[0].length;
    container.style.gridTemplateColumns = `repeat(${cols}, 26px)`;
    container.onmouseover = renderHoverPreviewFromEvent;
    container.onmousemove = renderHoverPreviewFromEvent;
    container.onmouseleave = clearHoverPreview;
    board.forEach((row, ri) => {
        row.forEach((cell, ci) => {
            const div = document.createElement('div');
            div.className = 'cell';
            if (cell !== null && cell !== undefined) {
                div.classList.add(PLAYER_COLORS[cell]);
            }
            /* Mark corner cells subtly */
            const lastRow = board.length - 1;
            const lastCol = cols - 1;
            const isCorner = (ri === 0 && ci === 0) ||
                             (ri === 0 && ci === lastCol) ||
                             (ri === lastRow && ci === 0) ||
                             (ri === lastRow && ci === lastCol);
            if (isCorner && cell === null) div.classList.add('corner-marker');
            div.dataset.row = ri;
            div.dataset.col = ci;
            div.onclick = () => onCellClick(ri, ci);
            container.appendChild(div);
        });
    });
    if (hoverAnchor && selectedPiece !== null && selectedPiece !== undefined) {
        renderHoverPreview(hoverAnchor.row, hoverAnchor.col);
    }
}

function clearHoverPreviewClasses() {
    document.querySelectorAll('#board .cell').forEach(cell => {
        HOVER_PREVIEW_CLASSES.forEach(className => cell.classList.remove(className));
        cell.style.removeProperty('--preview-color');
    });
}

function clearHoverPreview() {
    hoverAnchor = null;
    clearHoverPreviewClasses();
}

function renderHoverPreviewFromEvent(event) {
    const cell = event.target.closest('.cell');
    const board = document.getElementById('board');
    if (!cell || !board.contains(cell)) return;

    const row = Number(cell.dataset.row);
    const col = Number(cell.dataset.col);
    if (Number.isNaN(row) || Number.isNaN(col)) return;

    renderHoverPreview(row, col);
}

function getSelectedOrientationCells() {
    if (selectedPiece === null || selectedPiece === undefined) return [];
    const shape = getPieceOrientation(selectedPiece, currentOrientation);
    if (!shape) return [];

    const cells = [];
    shape.forEach((row, rowOffset) => {
        row.forEach((cell, colOffset) => {
            if (cell) cells.push({ rowOffset, colOffset });
        });
    });
    return cells;
}

function isPreviewCellOnBoard(row, col) {
    return row >= 0 &&
        col >= 0 &&
        row < currentBoard.length &&
        currentBoard[row] !== undefined &&
        col < currentBoard[row].length;
}

function getBoardCell(row, col) {
    return document.querySelector(`#board .cell[data-row="${row}"][data-col="${col}"]`);
}

function renderHoverPreview(anchorRow, anchorCol) {
    clearHoverPreviewClasses();
    hoverAnchor = { row: anchorRow, col: anchorCol };
    if (selectedPiece === null || selectedPiece === undefined) return;

    const selectedCells = getSelectedOrientationCells();
    if (selectedCells.length === 0) return;

    const previewCells = selectedCells.map(cell => ({
        row: anchorRow + cell.rowOffset,
        col: anchorCol + cell.colOffset,
    }));
    const hasOffBoardCell = previewCells.some(cell => !isPreviewCellOnBoard(cell.row, cell.col));
    const hasOccupiedCell = previewCells.some(cell =>
        isPreviewCellOnBoard(cell.row, cell.col) &&
        currentBoard[cell.row][cell.col] !== null &&
        currentBoard[cell.row][cell.col] !== undefined
    );
    const placementClass = hasOffBoardCell || hasOccupiedCell
        ? 'hover-preview-invalid'
        : 'hover-preview-valid';
    const colorHex = PLAYER_HEX[PLAYER_COLORS[currentPlayerId]] || '#14151a';

    previewCells.forEach(cell => {
        if (!isPreviewCellOnBoard(cell.row, cell.col)) return;
        const cellElement = getBoardCell(cell.row, cell.col);
        if (!cellElement) return;
        cellElement.style.setProperty('--preview-color', colorHex);
        cellElement.classList.add(placementClass);
        if (currentBoard[cell.row][cell.col] !== null && currentBoard[cell.row][cell.col] !== undefined) {
            cellElement.classList.add('hover-preview-occupied');
        }
    });
}

function renderTray(player) {
    const tray = document.getElementById('player-tray');
    tray.innerHTML = '';
    if (!player) return;
    const colorKey = player.color.toLowerCase();
    const colorHex = PLAYER_HEX[colorKey] || '#14151a';
    const canSelect = currentPlayerCanAct() && (player.controller_type || 'human') === 'human';
    if (selectedPiece !== null && selectedPiece !== undefined && !player.remaining_pieces.includes(selectedPiece)) {
        deselectPiece();
    }
    player.remaining_pieces.forEach(pid => {
        const div = document.createElement('div');
        div.className = 'piece';
        div.dataset.pieceId = pid;
        if (canSelect) {
            div.onclick = () => selectPiece(pid, colorHex);
        } else {
            div.classList.add('disabled');
        }
        renderPieceGrid(pid, div, { cellSize: 6, colorHex });
        if (pid === selectedPiece) div.classList.add('selected');
        tray.appendChild(div);
    });
}

function renderDashboard(state) {
    const dash = document.getElementById('dashboard');
    let html = '<table>';
    html += '<thead><tr>';
    html += '<th>Player</th>';
    html += '<th class="right">Score</th>';
    html += '<th class="right">Left</th>';
    html += '</tr></thead><tbody>';
    state.players.forEach(p => {
        const score = state.scores.find(s => s.player_id === p.id);
        const colorKey = (p.color || PLAYER_COLORS[p.id]).toLowerCase();
        const colorHex = PLAYER_HEX[colorKey] || '#14151a';
        const label = COLOR_LABEL[colorKey] || p.color;
        const controllerType = p.controller_type || 'human';
        const activeClass = (p.id === state.current_player_id) ? ' class="active"' : '';
        html += `<tr${activeClass}>`;
        html += `<td><div class="player-cell"><span class="player-swatch" style="background:${colorHex}"></span>${label}<span class="controller-badge">${controllerLabel(controllerType)}</span></div></td>`;
        html += `<td class="right">${score ? score.score : 0}</td>`;
        html += `<td class="right">${p.remaining_pieces.length}</td>`;
        html += '</tr>';
    });
    html += '</tbody></table>';
    dash.innerHTML = html;
}

function renderPreview(pieceId, colorHex) {
    const preview = document.getElementById('piece-preview');
    preview.innerHTML = '';
    if (pieceId === null || pieceId === undefined) {
        const empty = document.createElement('div');
        empty.className = 'empty-preview';
        empty.textContent = 'No piece selected';
        preview.appendChild(empty);
        return;
    }
    const meta = document.createElement('div');
    meta.className = 'preview-meta';
    meta.textContent = `Piece ${String(pieceId).padStart(2, '0')}`;
    preview.appendChild(meta);

    const wrap = document.createElement('div');
    renderPieceGrid(pieceId, wrap, {
        cellSize: 18,
        colorHex,
        className: 'preview-grid',
        orientationIndex: currentOrientation,
    });
    preview.appendChild(wrap);

    const orient = document.createElement('div');
    orient.className = 'preview-orient';
    orient.textContent = `Orient ${currentOrientation}`;
    preview.appendChild(orient);
}

function deselectPiece() {
    selectedPiece = null;
    currentOrientation = 0;
    document.querySelectorAll('#player-tray .piece').forEach(p => p.classList.remove('selected'));
    clearHoverPreview();
    renderPreview(null);
}

function selectPiece(pieceId, colorHex) {
    if (selectedPiece === pieceId) {
        deselectPiece();
        return;
    }
    selectedPiece = pieceId;
    currentOrientation = 0;
    document.querySelectorAll('#player-tray .piece').forEach(p => p.classList.remove('selected'));
    const el = document.querySelector(`#player-tray .piece[data-piece-id="${pieceId}"]`);
    if (el) el.classList.add('selected');
    renderPreview(pieceId, colorHex || '#14151a');
    if (hoverAnchor) renderHoverPreview(hoverAnchor.row, hoverAnchor.col);
}

function onCellClick(row, col) {
    if (!currentPlayerCanAct()) return;
    if (selectedPiece === null || selectedPiece === undefined) return;
    submitMove({
        player_id: currentPlayerId,
        piece_id: selectedPiece,
        orientation_index: currentOrientation,
        row: row,
        col: col,
    });
}

async function submitMove(move) {
    if (!currentPlayerCanAct()) return;
    try {
        const resp = await fetch('/move', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(move)
        });
        const result = await resp.json();
        if (result.ok) {
            deselectPiece();
            await loadState();
        } else {
            alert(result.error || 'Illegal move');
        }
    } catch (e) {
        console.error('Failed to submit move:', e);
    }
}

async function submitPass() {
    if (!currentPlayerCanAct()) return;
    try {
        const resp = await fetch('/pass', { method: 'POST' });
        const result = await resp.json();
        if (result.ok) {
            deselectPiece();
            await loadState();
        } else {
            alert(result.error || 'Unable to pass');
        }
    } catch (e) {
        console.error('Failed to pass turn:', e);
    }
}

function setStartError(message) {
    const error = document.getElementById('start-error');
    if (error) error.textContent = message || '';
}

function setStartBusy(isBusy) {
    document.querySelectorAll('[data-human-players]').forEach(button => {
        button.disabled = isBusy;
    });
}

async function startGame(humanPlayers) {
    setStartError('');
    setStartBusy(true);
    try {
        const resp = await fetch('/start', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ human_players: humanPlayers })
        });
        const result = await resp.json();
        if (!resp.ok || !result.ok) {
            setStartError(result.error || 'Unable to start session');
            return;
        }
        deselectPiece();
        await loadState();
    } catch (e) {
        console.error('Failed to start game:', e);
        setStartError('Unable to start session');
    } finally {
        setStartBusy(false);
    }
}

function bindSetupControls() {
    document.querySelectorAll('[data-human-players]').forEach(button => {
        button.addEventListener('click', () => {
            startGame(Number(button.dataset.humanPlayers));
        });
    });
    const passButton = document.getElementById('pass-button');
    if (passButton) passButton.addEventListener('click', submitPass);
}

document.addEventListener('keydown', (e) => {
    if (!currentPlayerCanAct()) return;
    if (selectedPiece === null || selectedPiece === undefined) return;

    if (e.key === 'r' || e.key === 'R') {
        currentOrientation = rotateOrientationIndex(selectedPiece, currentOrientation);
        const colorHex = PLAYER_HEX[PLAYER_COLORS[currentPlayerId]] || '#14151a';
        renderPreview(selectedPiece, colorHex);
        if (hoverAnchor) renderHoverPreview(hoverAnchor.row, hoverAnchor.col);
    }
    if (e.key === 'f' || e.key === 'F') {
        currentOrientation = flipOrientationIndex(selectedPiece, currentOrientation);
        const colorHex = PLAYER_HEX[PLAYER_COLORS[currentPlayerId]] || '#14151a';
        renderPreview(selectedPiece, colorHex);
        if (hoverAnchor) renderHoverPreview(hoverAnchor.row, hoverAnchor.col);
    }
});

bindSetupControls();
setInterval(loadState, 2000);
loadState();
