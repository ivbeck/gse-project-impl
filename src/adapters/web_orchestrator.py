from __future__ import annotations
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from core.types import Move, MoveResult


def create_web_orchestrator(session, player_adapter, presenter) -> FastAPI:
    app = FastAPI(title="Blokus Web GUI")

    base_path = Path(__file__).parent.parent
    templates_path = base_path / "templates"
    static_path = base_path / "static"

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/")
    def index():
        with open(templates_path / "game.html") as f:
            return HTMLResponse(f.read())

    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

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
                for pid, pieces in remaining.items()
            ],
            "scores": [{"player_id": s.player_id, "score": s.score, "is_winner": s.is_winner} for s in scores],
            "game_status": str(session.detect_termination()),
            "consecutive_passes": session.consecutive_passes,
        }

    @app.get("/piece-catalog")
    def piece_catalog():
        def orientation_grid(orientation):
            rows = max(r for r, _ in orientation) + 1
            cols = max(c for _, c in orientation) + 1
            grid = [[0] * cols for _ in range(rows)]
            for row, col in orientation:
                grid[row][col] = 1
            return grid

        def grid_key(grid):
            return "/".join("".join(str(cell) for cell in row) for row in grid)

        def rotate_grid(grid):
            rows = len(grid)
            cols = len(grid[0])
            result = [[0] * rows for _ in range(cols)]
            for row_index, row in enumerate(grid):
                for col_index, cell in enumerate(row):
                    result[col_index][rows - 1 - row_index] = cell
            return result

        def reflect_horizontal(grid):
            return [list(reversed(row)) for row in grid]

        def reflect_vertical(grid):
            return list(reversed([list(row) for row in grid]))

        def find_orientation_index(orientation_indexes, grid):
            return orientation_indexes[grid_key(grid)]

        def orientation_transitions(orientation_grids):
            orientation_indexes = {
                grid_key(grid): index
                for index, grid in enumerate(orientation_grids)
            }
            rotate_to = []
            flip_to = []
            for index, grid in enumerate(orientation_grids):
                rotate_to.append(find_orientation_index(orientation_indexes, rotate_grid(grid)))
                horizontal = find_orientation_index(orientation_indexes, reflect_horizontal(grid))
                if horizontal != index:
                    flip_to.append(horizontal)
                    continue
                vertical = find_orientation_index(orientation_indexes, reflect_vertical(grid))
                flip_to.append(vertical)
            return rotate_to, flip_to

        def piece_payload(piece):
            orientation_grids = [
                orientation_grid(orientation)
                for orientation in session.catalog.get_orientations(piece.piece_id)
            ]
            rotate_to, flip_to = orientation_transitions(orientation_grids)
            return {
                "piece_id": piece.piece_id,
                "shape": [list(row) for row in piece.shape],
                "orientations": orientation_grids,
                "rotate_to": rotate_to,
                "flip_to": flip_to,
            }

        return {
            "pieces": [
                piece_payload(piece)
                for piece in session.catalog.get_all_pieces()
            ]
        }

    @app.get("/pieces/{player_id}")
    def pieces(player_id: int):
        return {"pieces": list(session.remaining_pieces[player_id])}

    @app.post("/move")
    def move(move_data: dict):
        try:
            move = Move(
                player_id=move_data["player_id"],
                piece_id=move_data["piece_id"],
                orientation_index=move_data["orientation_index"],
                row=move_data["row"],
                col=move_data["col"],
            )
        except (KeyError, TypeError, ValueError) as e:
            return {"ok": False, "error": f"Invalid move data: {e}"}
        result = session.submit_move(move)
        presenter.render_board(session.board.grid)
        if result == MoveResult.ILLEGAL:
            return {"ok": False, "error": "Illegal move"}
        session.advance_turn()
        return {"ok": True}

    @app.post("/pass")
    def pass_turn():
        session.submit_pass()
        session.advance_turn()
        presenter.render_board(session.board.grid)
        return {"ok": True}

    return app
