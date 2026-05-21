# Web GUI Design — Blokus Configurable Game Engine

**Document Version:** 1.0
**Date:** 2026-05-19
**Status:** Approved — pending implementation
**Scope:** Add web-based GUI to existing Blokus CLI engine

---

## 1. Overview

Add a web-based graphical user interface to the existing Blokus game engine. The GUI is an additional interface alongside the existing CLI, not a replacement. The game engine core remains unchanged.

**Architecture:** Hexagonal (Ports & Adapters). New adapters implement existing ports (`PresentationOutput`, `PlayerInput`). No new ports required.

---

## 2. Architecture

### 2.1 Design Pattern

Adopt **Approach B** from the design proposal:
- New `WebPresentationAdapter` implements `PresentationOutput`
- New `WebPlayerAdapter` implements `PlayerInput`
- `WebOrchestrator` wires FastAPI routes to adapters

This keeps the GUI as a first-class citizen alongside `CLI` and `HumanPlayer`, following the existing hexagonal pattern.

### 2.2 New Components

| Component | Type | Responsibility |
|-----------|------|----------------|
| `WebPresentationAdapter` | Adapter | Implements `PresentationOutput`; renders board, trays, dashboard to HTML |
| `WebPlayerAdapter` | Adapter | Implements `PlayerInput`; serves legal moves via HTTP, receives player's chosen move |
| `WebOrchestrator` | Adapter | Wires FastAPI routes to adapters; manages session lifecycle and turn loop |
| `templates/` | Static assets | Jinja2 HTML templates with vanilla JS |
| `static/` | Static assets | CSS, SVG piece representations |

### 2.3 Data Flow

```
Bootstrap
  └── WebOrchestrator
        ├── FastAPI (routes: /, /move, /pass, /state, /pieces)
        ├── WebPresentationAdapter (PresentationOutput port)
        └── WebPlayerAdapter (PlayerInput port)

Browser (separate process)
  └── HTML/JS UI
        ├── GET / → renders game board + dashboard
        ├── GET /state → returns current game state JSON
        ├── GET /pieces/{player_id} → returns player's remaining pieces
        ├── POST /move → submits selected move
        └── POST /pass → submits pass
```

**Turn Flow:**
1. `GameSession` calls `WebPlayerAdapter.request_move(player_id, legal_moves)`
2. `WebPlayerAdapter` blocks (await) on an `asyncio.Future` populated by HTTP handler
3. Browser: player clicks piece (select), presses keys (rotate/flip preview), clicks board (place)
4. Browser POSTs to `/move` with move data
5. `WebOrchestrator` resolves the `Future`, returns `Move` to `GameSession`
6. `GameSession` processes move, calls `WebPresentationAdapter.render_board()`
7. Browser polls `/state` or receives push update (WebSocket/SSE) with new board state
8. Auto-advance highlights next player's tray

---

## 3. UI Layout

### 3.1 Main View

```
+------------------+---------------------------+------------------+
|   Player Info    |                           |   Dashboard      |
|   (current +     |                           |   - Scores      |
|    opponents)    |      20x20 Board          |   - Piece counts|
|                  |                           |   - Turn history|
|   Player Tray    |                           |   - Pass/skips  |
|   (remaining     |                           |                  |
|    pieces)       |                           |   Piece Preview |
|                  |                           |   (when selected|
+------------------+---------------------------+------------------+
```

### 3.2 Interaction Model (Hybrid)

1. **Select piece:** Click piece in player tray → piece becomes "selected", shows in Piece Preview panel
2. **Preview orientation:** Use keyboard (R=rotate, F=flip) → Piece Preview updates to show current orientation
3. **Place piece:** Click board cell → places selected piece orientation with corner-0 at clicked cell
4. **Confirm:** Auto-advances after valid placement; if illegal, shows error and prompts re-selection

### 3.3 Visual Style

- **Theme:** "Sexy schmexy" — modern, dark, with neon accents per player color
- **Player colors:** Blue (#0000FF), Yellow (#FFFF00), Red (#FF0000), Green (#00FF00)
- **Board:** Dark grid with subtle lines, placed pieces filled with player color + glow
- **Piece Preview:** Shows selected piece with all orientation options accessible via R/F keys
- **Auto-advance:** After placement, 500ms highlight animation on next player's tray

---

## 4. Functional Requirements

### 4.1 GUI Adapter Requirements

| ID | Requirement |
|----|-------------|
| GUI-FR-1 | GUI shall display the current 20x20 board with all placed pieces |
| GUI-FR-2 | GUI shall display each player's remaining pieces in their tray |
| GUI-FR-3 | GUI shall highlight the current player's tray |
| GUI-FR-4 | GUI shall display scores for all players |
| GUI-FR-5 | GUI shall display piece counts (number of pieces remaining) |
| GUI-FR-6 | GUI shall display a turn history log |
| GUI-FR-7 | GUI shall indicate when a player has passed or is skipped |
| GUI-FR-8 | GUI shall allow piece selection via click |
| GUI-FR-9 | GUI shall show piece preview with rotation (R key) and flip (F key) |
| GUI-FR-10 | GUI shall allow piece placement via board cell click |
| GUI-FR-11 | GUI shall auto-advance to next player after valid placement |
| GUI-FR-12 | GUI shall display error messages for illegal move attempts |
| GUI-FR-13 | GUI shall show final scores and winner announcement at game end |
| GUI-FR-14 | GUI shall offer "New Game" and "Exit" options at game end |

### 4.2 Performance Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| GUI-NFR-1 | Board render update after move | < 100ms |
| GUI-NFR-2 | Move submission response | < 200ms |
| GUI-NFR-3 | Full page load | < 2s |

---

## 5. Interface Design

### 5.1 HTTP API Endpoints

| Method | Path | Request Body | Response | Description |
|--------|------|--------------|----------|-------------|
| GET | `/` | — | HTML | Main game UI |
| GET | `/state` | — | JSON | Current game state |
| GET | `/pieces/{player_id}` | — | JSON | Player's remaining pieces |
| POST | `/move` | `{move: MoveJSON}` | `{ok: bool, error?: string}` | Submit a move |
| POST | `/pass` | — | `{ok: bool}` | Submit pass |
| GET | `/history` | — | JSON | Turn history log |

### 5.2 WebSocket (optional enhancement)

- Path: `/ws`
- Events: `board_updated`, `turn_changed`, `game_over`
- Eliminates polling; browser receives real-time updates

---

## 6. Implementation Notes

### 6.1 Suggested File Structure

```
src/
  adapters/
    web_presentation_adapter.py   # PresentationOutput impl
    web_player_adapter.py         # PlayerInput impl
    web_orchestrator.py           # FastAPI app + routes
    human_player.py               # Existing - unchanged
    cli.py                        # Existing - unchanged
    ...
  templates/
    game.html                     # Main Jinja2 template
  static/
    style.css
    pieces.js                     # Piece SVG data + rendering
    gui.js                        # UI interaction logic
```

### 6.3 Bootstrap Extension

New `run_web()` function in `bootstrap.py` or `web_main.py` entry point:
```python
def run_web():
    config = JsonConfigSource().load_config()
    session = create_game(config)
    player = WebPlayerAdapter()
    presenter = WebPresentationAdapter(session)
    orchestrator = WebOrchestrator(session, player, presenter)
    uvicorn.run(orchestrator.app, host="127.0.0.1", port=8000)
```

New command: `uv run python -m app --gui` or `uv run python -m app_web`.

### 6.4 Constraints

- `Core.*` remains untouched — zero imports from web adapters
- All existing tests continue to pass
- SC-2 (no network access) is preserved — server runs on localhost only
- JSON round-trip via Memento remains the only state persistence format

---

## 7. Out of Scope

- Online multiplayer (EX-3 still applies)
- Drag-and-drop (click-click selected; keyboard for rotation)
- Mobile-responsive design (desktop browser target)
- Piece animation beyond highlight transitions

---

## 8. Acceptance Criteria

1. `uv run python -m app --gui` starts the web UI without errors
2. Browser shows the board, all 4 player trays, dashboard with scores/history
3. Clicking a piece selects it and shows preview
4. R/F keys change preview orientation
5. Clicking board places piece (corner-0 at clicked cell)
6. Invalid moves show error, board remains unchanged
7. After valid placement, turn auto-advances and next player tray highlights
8. Scores update correctly as pieces are placed
9. Game end shows winner announcement with final scores
10. "New Game" resets the board; "Exit" terminates the server
11. All existing `uv run pytest` tests pass

---

**End of Design**
