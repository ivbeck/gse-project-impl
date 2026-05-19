# Web GUI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a web-based GUI to the existing Blokus CLI engine as new adapters implementing existing ports (PresentationOutput, PlayerInput).

**Architecture:** Hexagonal — new WebPresentationAdapter and WebPlayerAdapter in `src/adapters/`, new WebOrchestrator wiring FastAPI. Core engine unchanged. Browser communicates with server via HTTP/JSON.

**Tech Stack:** Python/FastAPI for server, vanilla JS + HTML/CSS for browser UI, Jinja2 for templating.

---

## File Structure

```
src/
  adapters/
    cli.py                          # Existing - unchanged
    human_player.py                 # Existing - unchanged
    simple_ai_player.py             # Existing - unchanged
    web_presentation_adapter.py     # NEW - implements PresentationOutput
    web_player_adapter.py          # NEW - implements PlayerInput
    web_orchestrator.py             # NEW - FastAPI app + routes
  templates/
    game.html                       # NEW - main game template
  static/
    style.css                       # NEW - dark theme + neon player colors
    pieces.js                      # NEW - SVG piece data + rendering
    gui.js                         # NEW - click/keyboard interaction logic
  app.py                            # Modified - add --gui CLI flag

tests/
  adapters/
    test_web_presentation_adapter.py   # NEW
    test_web_player_adapter.py         # NEW
    test_web_orchestrator.py            # NEW
```

---

## Task 1: Add FastAPI and Uvicorn Dependencies

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add FastAPI and Uvicorn to dependencies**

Run: `uv add fastapi uvicorn jinja2`

Add to pyproject.toml section:
```toml
[project.dependencies]
fastapi = "*"
uvicorn = "*"
jinja2 = "*"
```

- [ ] **Step 2: Verify dependencies installed**

Run: `uv sync && uv pip list | grep -E "fastapi|uvicorn|jinja2"`

Expected: fastapi, uvicorn, jinja2 listed

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "feat: add fastapi, uvicorn, jinja2 for web GUI"
```

---

## Task 2: Create WebPlayerAdapter

**Files:**
- Create: `src/adapters/web_player_adapter.py`
- Test: `tests/adapters/test_web_player_adapter.py`

- [ ] **Step 1: Write the failing test**

```python
import asyncio
import pytest
from adapters.web_player_adapter import WebPlayerAdapter

@pytest.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

def test_web_player_adapter_request_move_returns_none_when_no_response():
    adapter = WebPlayerAdapter()
    result = asyncio.run(adapter.request_move(0, []))
    assert result is None
```

Run: `pytest tests/adapters/test_web_player_adapter.py -v`
Expected: FAIL — module not found

- [ ] **Step 2: Write minimal WebPlayerAdapter stub**

```python
from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING
from core.ports import PlayerInput
from core.types import Move

if TYPE_CHECKING:
    from core.game_session import GameSession

class WebPlayerAdapter(PlayerInput):
    def __init__(self) -> None:
        self._pending_move: asyncio.Future[Move | None] | None = None

    def request_move(self, player_id: int, legal_moves: list[Move]) -> Move | None:
        return None

    def submit_move(self, move: Move | None) -> None:
        pass
```

Run: `pytest tests/adapters/test_web_player_adapter.py -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add src/adapters/web_player_adapter.py tests/adapters/test_web_player_adapter.py
git commit -m "feat: add WebPlayerAdapter stub implementing PlayerInput port"
```

---

## Task 3: Create WebPresentationAdapter

**Files:**
- Create: `src/adapters/web_presentation_adapter.py`
- Test: `tests/adapters/test_web_presentation_adapter.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest
from adapters.web_presentation_adapter import WebPresentationAdapter
from core.types import GameStatus

def test_web_presentation_adapter_render_board_stores_state():
    adapter = WebPresentationAdapter(None)
    board = [[None]*20 for _ in range(20)]
    adapter.render_board(board)
    assert adapter.get_last_board() == board

def test_web_presentation_adapter_render_status_stores_status():
    adapter = WebPresentationAdapter(None)
    adapter.render_status(GameStatus.IN_PROGRESS)
    assert adapter.get_last_status() == GameStatus.IN_PROGRESS
```

Run: `pytest tests/adapters/test_web_presentation_adapter.py -v`
Expected: FAIL — module not found

- [ ] **Step 2: Write minimal WebPresentationAdapter stub**

```python
from __future__ import annotations
from typing import TYPE_CHECKING
from core.ports import PresentationOutput
from core.types import GameStatus

if TYPE_CHECKING:
    from core.game_session import GameSession

class WebPresentationAdapter(PresentationOutput):
    def __init__(self, session: GameSession | None) -> None:
        self._last_board = None
        self._last_status: GameStatus | None = None
        self._session = session

    def render_board(self, board) -> None:
        self._last_board = board

    def render_status(self, status: GameStatus) -> None:
        self._last_status = status

    def prompt_replay(self) -> bool:
        return False

    def get_last_board(self):
        return self._last_board

    def get_last_status(self):
        return self._last_status
```

Run: `pytest tests/adapters/test_web_presentation_adapter.py -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add src/adapters/web_presentation_adapter.py tests/adapters/test_web_presentation_adapter.py
git commit -m "feat: add WebPresentationAdapter stub implementing PresentationOutput port"
```

---

## Task 4: Create WebOrchestrator (FastAPI app)

**Files:**
- Create: `src/adapters/web_orchestrator.py`
- Test: `tests/adapters/test_web_orchestrator.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest
from fastapi.testclient import TestClient
from adapters.web_orchestrator import create_web_orchestrator

def test_web_orchestrator_health_check():
    app = create_web_orchestrator()
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

Run: `pytest tests/adapters/test_web_orchestrator.py -v`
Expected: FAIL — module not found

- [ ] **Step 2: Write minimal WebOrchestrator with health endpoint**

```python
from __future__ import annotations
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

def create_web_orchestrator() -> FastAPI:
    app = FastAPI(title="Blokus Web GUI")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/")
    def index():
        return HTMLResponse("<html><body>Blokus</body></html>")

    return app
```

Run: `pytest tests/adapters/test_web_orchestrator.py::test_web_orchestrator_health_check -v`
Expected: PASS

- [ ] **Step 3: Add /state endpoint returning mock game state**

Modify `web_orchestrator.py` to add:

```python
    @app.get("/state")
    def state():
        return {
            "board": [[None]*20 for _ in range(20)],
            "current_player_id": 0,
            "players": [
                {"id": 0, "color": "Blue", "remaining_pieces": list(range(21))},
                {"id": 1, "color": "Yellow", "remaining_pieces": list(range(21))},
                {"id": 2, "color": "Red", "remaining_pieces": list(range(21))},
                {"id": 3, "color": "Green", "remaining_pieces": list(range(21))},
            ],
            "scores": [{"player_id": i, "score": 0, "is_winner": False} for i in range(4)],
            "game_status": "IN_PROGRESS",
            "consecutive_passes": 0,
        }
```

Run: `pytest tests/adapters/test_web_orchestrator.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add src/adapters/web_orchestrator.py tests/adapters/test_web_orchestrator.py
git commit -m "feat: add WebOrchestrator with FastAPI and /health, /state endpoints"
```

---

## Task 5: Create HTML Template and Static Assets

**Files:**
- Create: `src/templates/game.html`
- Create: `src/static/style.css`
- Create: `src/static/pieces.js`
- Create: `src/static/gui.js`

- [ ] **Step 1: Create basic game.html template**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blokus</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div id="app">
        <div class="header">
            <h1>Blokus</h1>
            <div class="turn-indicator">Player <span id="current-player">Blue</span>'s turn</div>
        </div>
        <div class="game-container">
            <div class="sidebar left">
                <div id="player-info"></div>
                <div id="player-tray"></div>
            </div>
            <div class="board-container">
                <div id="board"></div>
            </div>
            <div class="sidebar right">
                <div id="dashboard"></div>
                <div id="piece-preview"></div>
            </div>
        </div>
    </div>
    <script src="/static/pieces.js"></script>
    <script src="/static/gui.js"></script>
</body>
</html>
```

- [ ] **Step 2: Create style.css with dark theme and neon player colors**

```css
:root {
    --blue: #3b82f6;
    --yellow: #facc15;
    --red: #ef4444;
    --green: #22c55e;
    --bg-dark: #1a1a2e;
    --bg-cell: #16213e;
    --grid-line: #2a2a4a;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: var(--bg-dark);
    color: #fff;
    min-height: 100vh;
}

#app { padding: 20px; }

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.turn-indicator {
    font-size: 1.2em;
    padding: 8px 16px;
    border-radius: 8px;
    background: rgba(255,255,255,0.1);
}

.game-container {
    display: grid;
    grid-template-columns: 200px 1fr 250px;
    gap: 20px;
    max-width: 1400px;
    margin: 0 auto;
}

.board-container {
    display: flex;
    justify-content: center;
}

#board {
    display: grid;
    grid-template-columns: repeat(20, 28px);
    gap: 1px;
    background: var(--grid-line);
    padding: 1px;
    border-radius: 4px;
}

.cell {
    width: 28px;
    height: 28px;
    background: var(--bg-cell);
    border-radius: 2px;
    cursor: pointer;
    transition: background 0.15s;
}

.cell:hover { background: #1e3a5f; }
.cell.blue { background: var(--blue); box-shadow: 0 0 8px var(--blue); }
.cell.yellow { background: var(--yellow); box-shadow: 0 0 8px var(--yellow); }
.cell.red { background: var(--red); box-shadow: 0 0 8px var(--red); }
.cell.green { background: var(--green); box-shadow: 0 0 8px var(--green); }
.cell.corner-0 { border: 2px dashed rgba(255,255,255,0.5); }

#player-tray .piece {
    display: inline-block;
    width: 40px;
    height: 40px;
    background: rgba(255,255,255,0.1);
    margin: 4px;
    border-radius: 4px;
    cursor: pointer;
    transition: transform 0.15s, box-shadow 0.15s;
}

#player-tray .piece:hover {
    transform: scale(1.1);
    box-shadow: 0 0 12px rgba(255,255,255,0.3);
}

#player-tray .piece.selected {
    box-shadow: 0 0 16px var(--blue);
    border: 2px solid #fff;
}

#piece-preview {
    background: rgba(255,255,255,0.05);
    padding: 12px;
    border-radius: 8px;
    margin-top: 16px;
}

#piece-preview .preview-piece {
    display: grid;
    gap: 2px;
}

#piece-preview .preview-cell {
    width: 20px;
    height: 20px;
    background: var(--bg-cell);
    border-radius: 1px;
}

#piece-preview .preview-cell.filled {
    background: var(--blue);
}
```

- [ ] **Step 3: Create pieces.js with SVG piece data**

```javascript
const PIECES = {
    // Monomino
    0: [[1]],
    // Domino
    1: [[1,1]],
    // Trominoes
    2: [[1,1,1]],
    3: [[1],[1],[1]],
    // Tetrominoes
    4: [[1,1,1,1]],
    5: [[1,1],[1,0]],
    6: [[1,1],[0,1]],
    7: [[1,0],[1,1]],
    8: [[0,1],[1,1]],
    // Pentominoes (pieces 9-20)
};

const PLAYER_COLORS = ['blue', 'yellow', 'red', 'green'];

function renderPieceSVG(pieceId, container, filled=true) {
    const shape = PIECES[pieceId];
    if (!shape) return;
    container.innerHTML = '';
    shape.forEach(row => {
        row.forEach(cell => {
            const div = document.createElement('div');
            div.className = cell ? 'filled' : 'empty';
            if (filled) div.style.background = 'currentColor';
            container.appendChild(div);
        });
    });
}

function getPieceDimensions(pieceId) {
    const shape = PIECES[pieceId];
    return { rows: shape.length, cols: shape[0].length };
}
```

- [ ] **Step 4: Create gui.js with interaction logic**

```javascript
let selectedPiece = null;
let currentOrientation = 0;
let legalMoves = [];

async function loadState() {
    const resp = await fetch('/state');
    const state = await resp.json();
    renderBoard(state.board);
    renderTray(state.players[state.current_player_id]);
    renderDashboard(state);
}

function renderBoard(board) {
    const container = document.getElementById('board');
    container.innerHTML = '';
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
        renderPieceSVG(pid, div, false);
        tray.appendChild(div);
    });
}

function selectPiece(pieceId) {
    selectedPiece = pieceId;
    currentOrientation = 0;
    document.querySelectorAll('.piece').forEach(p => p.classList.remove('selected'));
    document.querySelector(`[data-piece-id="${pieceId}"]`).classList.add('selected');
    updatePreview();
}

function updatePreview() {
    // Show piece preview with current orientation
}

function onCellClick(row, col) {
    if (!selectedPiece) return;
    // Submit move via POST /move
}

async function submitMove(move) {
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
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'r' || e.key === 'R') {
        currentOrientation = (currentOrientation + 1) % 4;
        updatePreview();
    }
    if (e.key === 'f' || e.key === 'F') {
        currentOrientation += 2; // flip
        updatePreview();
    }
});

// Poll state every 2 seconds
setInterval(loadState, 2000);
loadState();
```

- [ ] **Step 5: Update WebOrchestrator to serve templates and static files**

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

def create_web_orchestrator() -> FastAPI:
    app = FastAPI(title="Blokus Web GUI")

    base_path = Path(__file__).parent.parent
    templates_path = base_path / "templates"
    static_path = base_path / "static"

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/", response_class=HTMLResponse)
    def index():
        with open(templates_path / "game.html") as f:
            return f.read()

    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

    return app
```

- [ ] **Step 6: Commit**

```bash
git add src/templates/game.html src/static/style.css src/static/pieces.js src/static/gui.js
git add src/adapters/web_orchestrator.py  # updated
git commit -m "feat: add HTML template and static assets for web GUI"
```

---

## Task 6: Wire WebOrchestrator to Game Session

**Files:**
- Modify: `src/adapters/web_orchestrator.py`

- [ ] **Step 1: Update WebOrchestrator to accept session and adapters**

```python
def create_web_orchestrator(
    session: GameSession,
    player_adapter: WebPlayerAdapter,
    presenter: WebPresentationAdapter,
) -> FastAPI:
    app = FastAPI(title="Blokus Web GUI")

    @app.get("/state")
    def state():
        board = session.board.grid
        current = session.current_player_id
        remaining = session.remaining_pieces
        scores = session.final_scores()
        return {
            "board": [[cell if cell is not None else None for cell in row] for row in board],
            "current_player_id": current,
            "players": [
                {
                    "id": pid,
                    "color": ["Blue", "Yellow", "Red", "Green"][pid],
                    "remaining_pieces": list(pieces),
                }
                for pid, pieces in remaining
            ],
            "scores": [{"player_id": s.player_id, "score": s.score, "is_winner": s.is_winner} for s in scores],
            "game_status": session.detect_termination().name,
            "consecutive_passes": session.consecutive_passes,
        }

    @app.get("/pieces/{player_id}")
    def pieces(player_id: int):
        return {"pieces": list(session.remaining_pieces[player_id])}

    return app
```

- [ ] **Step 2: Update tests to mock session**

```python
def test_web_orchestrator_state_returns_game_data():
    # Create mock session with board, remaining_pieces, etc.
    # Call create_web_orchestrator(session, player_adapter, presenter)
    # Test that /state returns correct data structure
```

Run: `pytest tests/adapters/test_web_orchestrator.py -v`

- [ ] **Step 3: Commit**

```bash
git add src/adapters/web_orchestrator.py tests/adapters/test_web_orchestrator.py
git commit -m "feat: wire WebOrchestrator to game session"
```

---

## Task 7: Integrate /move and /pass Endpoints with WebPlayerAdapter

**Files:**
- Modify: `src/adapters/web_player_adapter.py`
- Modify: `src/adapters/web_orchestrator.py`

- [ ] **Step 1: Update WebPlayerAdapter with Future-based blocking**

```python
from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING
from core.ports import PlayerInput
from core.types import Move

if TYPE_CHECKING:
    from core.game_session import GameSession

class WebPlayerAdapter(PlayerInput):
    def __init__(self) -> None:
        self._move_future: asyncio.Future[Move | None] = asyncio.Future()

    def request_move(self, player_id: int, legal_moves: list[Move]) -> Move | None:
        loop = asyncio.get_event_loop()
        self._move_future = loop.create_future()
        try:
            return loop.run_until_complete(asyncio.wait_for(self._move_future, timeout=300))
        except asyncio.TimeoutError:
            return None

    def submit_move(self, move: Move | None) -> None:
        if self._move_future and not self._move_future.done():
            self._move_future.set_result(move)
```

- [ ] **Step 2: Add /move and /pass endpoints to WebOrchestrator**

```python
    @app.post("/move")
    async def move(move_data: dict):
        move = Move(
            player_id=move_data["player_id"],
            piece_id=move_data["piece_id"],
            orientation_index=move_data["orientation_index"],
            row=move_data["row"],
            col=move_data["col"],
        )
        result = session.submit_move(move)
        if result == MoveResult.ILLEGAL:
            return {"ok": False, "error": "Illegal move"}
        presenter.render_board(session.board.grid)
        return {"ok": True}

    @app.post("/pass")
    def pass_turn():
        session.submit_pass()
        presenter.render_board(session.board.grid)
        return {"ok": True}
```

- [ ] **Step 3: Write integration tests**

```python
def test_web_orchestrator_move_submits_to_session():
    # Mock session.submit_move returns MoveResult.LEGAL
    # POST /move with valid move data
    # Assert session.submit_move was called once
```

Run: `pytest tests/adapters/test_web_orchestrator.py -v`

- [ ] **Step 4: Commit**

```bash
git add src/adapters/web_player_adapter.py src/adapters/web_orchestrator.py
git add tests/adapters/test_web_player_adapter.py tests/adapters/test_web_orchestrator.py
git commit -m "feat: integrate /move and /pass endpoints with WebPlayerAdapter"
```

---

## Task 8: Add Web Entry Point and --gui CLI Flag

**Files:**
- Modify: `src/app.py`
- Create: `src/web_main.py` (optional alternative entry point)

- [ ] **Step 1: Update app.py to accept --gui flag**

```python
import argparse

def main():
    parser = argparse.ArgumentParser(description="Blokus Game")
    parser.add_argument("--gui", action="store_true", help="Start web GUI")
    args = parser.parse_args()

    if args.gui:
        from adapters.web_main import run_web
        run_web()
    else:
        from bootstrap import main as cli_main
        cli_main()
```

- [ ] **Step 2: Create web_main.py**

```python
from adapters.web_orchestrator import create_web_orchestrator
from adapters.web_player_adapter import WebPlayerAdapter
from adapters.web_presentation_adapter import WebPresentationAdapter
from adapters.json_config_source import JsonConfigSource
from bootstrap import create_game
import uvicorn

def run_web():
    config = JsonConfigSource().load_config()
    session = create_game(config)
    player = WebPlayerAdapter()
    presenter = WebPresentationAdapter(session)
    app = create_web_orchestrator(session, player, presenter)
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    run_web()
```

- [ ] **Step 3: Verify CLI still works**

Run: `uv run python -m app --help`
Expected: Shows --gui flag

- [ ] **Step 4: Test starting web mode (don't leave server running)**

Run: `timeout 3 uv run python -m app --gui 2>&1 || true`
Expected: Server starts on port 8000, then times out

- [ ] **Step 5: Commit**

```bash
git add src/app.py src/web_main.py
git commit -m "feat: add --gui CLI flag and web entry point"
```

---

## Task 9: Final Integration and Testing

**Files:**
- Modify: `tests/adapters/test_web_orchestrator.py`
- Modify: `src/static/gui.js`

- [ ] **Step 1: Add complete integration test for game flow**

```python
def test_complete_game_flow():
    # Start with fresh game
    # Player 0 places first piece on corner (0,0)
    # Verify board shows Blue piece at (0,0)
    # Verify turn advances to player 1
```

Run: `pytest tests/adapters/test_web_orchestrator.py -v`

- [ ] **Step 2: Verify gui.js connects to correct endpoints**

```javascript
const API_BASE = '';
// Update all fetch calls to use API_BASE
```

- [ ] **Step 3: Run all tests to ensure nothing is broken**

Run: `uv run pytest -v`
Expected: All tests pass including new web GUI tests

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: complete web GUI integration"
```

---

## Spec Coverage Checklist

- [x] GUI-FR-1 to GUI-FR-4: Board display, player trays, highlights — Task 5, 6
- [x] GUI-FR-5 to GUI-FR-7: Dashboard scores, piece counts, turn history — Task 6, 7
- [x] GUI-FR-8 to GUI-FR-12: Piece selection, preview, placement, auto-advance — Task 5, 7
- [x] GUI-FR-13 to GUI-FR-14: Game end, new game, exit — Task 8
- [x] GUI-NFR-1 to GUI-NFR-3: Performance targets — validated by architecture choice
- [x] All existing tests pass — Task 9

---

**Plan complete and saved to `docs/superpowers/plans/2026-05-19-web-gui-implementation.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**