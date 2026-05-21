let selectedPiece = null;
let currentOrientation = 0;
let legalMoves = [];
let currentPlayerId = 0;
let roundCounter = 1;
let currentBoard = [];
let hoverAnchor = null;
let gameStarted = false;
let gameFinished = false;
let currentControllerType = 'human';
let currentPlayerHasLegalMoves = null;

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
        gameFinished = state.game_status === 'FINISHED';
        currentPlayerHasLegalMoves = state.current_player_has_legal_moves;
        updateSessionVisibility(state);
        if (!gameStarted) {
            currentControllerType = 'human';
            renderEventBanner(state);
            renderEndGamePanel(state);
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
        renderEventBanner(state);
        renderEndGamePanel(state);
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
    const finished = state ? state.game_status === 'FINISHED' : gameFinished;
    const hasLegalMoves = state && Object.prototype.hasOwnProperty.call(state, 'current_player_has_legal_moves')
        ? state.current_player_has_legal_moves !== false
        : currentPlayerHasLegalMoves !== false;
    return gameStarted && !finished && hasLegalMoves && currentControllerType === 'human';
}

function setSessionStatus(label, finished) {
    const statusLabel = document.querySelector('.status-label');
    if (statusLabel) statusLabel.textContent = label;
    const statusPill = document.querySelector('.status-pill');
    if (statusPill) statusPill.classList.toggle('finished', finished);
}

function showStartScreen() {
    const startScreen = document.getElementById('start-screen');
    const gameScreen = document.getElementById('game-screen');
    if (startScreen) startScreen.classList.remove('hidden');
    if (gameScreen) gameScreen.classList.add('hidden');
    setSessionStatus('Setup', false);
}

function showGameScreen() {
    const startScreen = document.getElementById('start-screen');
    const gameScreen = document.getElementById('game-screen');
    if (startScreen) startScreen.classList.add('hidden');
    if (gameScreen) gameScreen.classList.remove('hidden');
    setSessionStatus('Live Session', false);
}

function showEndGameScreen(state) {
    showGameScreen();
    gameFinished = true;
    setSessionStatus('Finished', true);
    renderEndGamePanel(state);
}

function updateSessionVisibility(state) {
    if (!state.started) {
        showStartScreen();
        return;
    }
    if (state.game_status === 'FINISHED') {
        showEndGameScreen(state);
        return;
    }
    showGameScreen();
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
    const suffix = document.querySelector('.turn-suffix');
    if (suffix) suffix.textContent = state.game_status === 'FINISHED' ? 'game finished' : 'to move';
    const hints = document.querySelector('.turn-hints');
    if (hints) hints.innerHTML = state.game_status === 'FINISHED'
        ? 'Final scores are locked'
        : '<kbd>R</kbd> rotate &middot; <kbd>F</kbd> flip &middot; click cell to place';
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
    container.classList.toggle('is-locked', gameFinished);
    container.onmouseover = renderHoverPreviewFromEvent;
    container.onmousemove = renderHoverPreviewFromEvent;
    container.onmouseleave = clearHoverPreview;
    if (gameFinished) {
        container.onmouseover = null;
        container.onmousemove = null;
    }
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

function skippedPlayerMessage(skippedPlayers) {
    if (!skippedPlayers || skippedPlayers.length === 0) return '';
    if (skippedPlayers.length === 1) {
        return skippedPlayers[0].message || `${skippedPlayers[0].color} has no legal moves and was skipped.`;
    }
    const names = skippedPlayers.map(player => player.color || `Player ${player.player_id}`);
    return `${names.join(', ')} have no legal moves and were skipped.`;
}

function renderEventBanner(state) {
    const banner = document.getElementById('event-banner');
    if (!banner) return;
    const message = skippedPlayerMessage(state.skipped_players);
    banner.textContent = message;
    banner.classList.toggle('hidden', !message);
}

function renderEndGamePanel(state) {
    const panel = document.getElementById('endgame-panel');
    if (!panel) return;
    if (state.game_status !== 'FINISHED') {
        panel.classList.add('hidden');
        panel.innerHTML = '';
        return;
    }

    const scores = (state.scores || []).slice().sort((a, b) => {
        if (a.score !== b.score) return a.score - b.score;
        return a.player_id - b.player_id;
    });
    const winnerIds = state.winner_ids || scores.filter(score => score.is_winner).map(score => score.player_id);
    const winnerNames = winnerIds.map(playerId => {
        const player = playerForId(state, playerId);
        return player ? player.color : `Player ${playerId}`;
    });
    const winnerText = winnerNames.length > 1
        ? `${winnerNames.join(', ')} share the win`
        : (winnerNames[0] ? `${winnerNames[0]} wins` : 'No winner recorded');

    let html = '<div class="endgame-kicker">Game Complete</div>';
    html += `<h2>${winnerText}</h2>`;
    html += '<p>Final score uses remaining unplaced squares. Lower is better.</p>';
    html += '<table><thead><tr><th>Rank</th><th>Player</th><th class="right">Score</th><th>Result</th></tr></thead><tbody>';
    scores.forEach((score, index) => {
        const player = playerForId(state, score.player_id);
        const colorKey = ((player && player.color) || score.color || PLAYER_COLORS[score.player_id]).toLowerCase();
        const colorHex = PLAYER_HEX[colorKey] || '#14151a';
        const playerLabel = (player && player.color) || score.color || `Player ${score.player_id}`;
        const result = score.is_winner ? '<span class="winner-badge">Winner</span>' : '';
        html += '<tr>';
        html += `<td>${String(index + 1).padStart(2, '0')}</td>`;
        html += `<td><span class="player-swatch" style="background:${colorHex}"></span>${playerLabel}</td>`;
        html += `<td class="right">${score.score}</td>`;
        html += `<td>${result}</td>`;
        html += '</tr>';
    });
    html += '</tbody></table>';
    html += '<div class="endgame-actions"><button class="endgame-menu-button" id="main-menu-button" type="button">Main Menu</button></div>';

    panel.innerHTML = html;
    const menuButton = document.getElementById('main-menu-button');
    if (menuButton) menuButton.addEventListener('click', returnToMainMenu);
    panel.classList.remove('hidden');
}

function clearTransientPanels() {
    const eventBanner = document.getElementById('event-banner');
    if (eventBanner) {
        eventBanner.textContent = '';
        eventBanner.classList.add('hidden');
    }
    const endGamePanel = document.getElementById('endgame-panel');
    if (endGamePanel) {
        endGamePanel.innerHTML = '';
        endGamePanel.classList.add('hidden');
    }
}

function clearFrontendGameState() {
    selectedPiece = null;
    currentOrientation = 0;
    currentPlayerId = 0;
    roundCounter = 1;
    currentBoard = [];
    hoverAnchor = null;
    gameStarted = false;
    gameFinished = false;
    currentControllerType = 'human';
    currentPlayerHasLegalMoves = null;
    setStartError('');
    clearHoverPreview();
    clearTransientPanels();
    renderPreview(null);
    const tray = document.getElementById('player-tray');
    if (tray) tray.innerHTML = '';
    const dashboard = document.getElementById('dashboard');
    if (dashboard) dashboard.innerHTML = '';
    const board = document.getElementById('board');
    if (board) {
        board.innerHTML = '';
        board.classList.remove('is-locked');
    }
    const counter = document.getElementById('round-counter');
    if (counter) counter.textContent = '01';
    updatePassButton({ started: false, game_status: 'IN_PROGRESS' });
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

async function returnToMainMenu() {
    try {
        const resp = await fetch('/reset', { method: 'POST' });
        const result = await resp.json();
        if (!resp.ok || !result.ok) {
            throw new Error(result.error || 'Unable to reset session');
        }
        clearFrontendGameState();
        showStartScreen();
    } catch (e) {
        console.error('Failed to return to menu:', e);
        setStartError('Unable to return to menu');
        clearFrontendGameState();
        showStartScreen();
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
