from __future__ import annotations
from fastapi import FastAPI
from fastapi.responses import HTMLResponse


def create_web_orchestrator(session, player_adapter, presenter) -> FastAPI:
    app = FastAPI(title="Blokus Web GUI")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/")
    def index():
        return HTMLResponse("<html><body>Blokus</body></html>")

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
            "game_status": session.detect_termination().name,
            "consecutive_passes": session.consecutive_passes,
        }

    @app.get("/pieces/{player_id}")
    def pieces(player_id: int):
        return {"pieces": list(session.remaining_pieces[player_id])}

    return app