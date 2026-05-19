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

    return app