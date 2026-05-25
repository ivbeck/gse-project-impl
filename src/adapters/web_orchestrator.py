from __future__ import annotations
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from adapters.simple_ai_player import SimpleAiPlayer
from core.legal_move_enumerator import LegalMoveEnumerator
from core.types import GameStatus, Move, MoveResult


PLAYER_COLORS = ["Blue", "Yellow", "Red", "Green"]


def create_web_orchestrator(
    session,
    player_adapter,
    presenter,
    ai_player=None,
    legal_move_enumerator=None,
    session_factory=None,
) -> FastAPI:
    app = FastAPI(title="Blokus Web GUI")
    setup_started = False
    human_player_count = 0
    last_event: dict | None = None
    recent_skipped_players: list[dict] = []
    provided_ai_player = ai_player is not None
    provided_legal_move_enumerator = legal_move_enumerator is not None

    base_path = Path(__file__).parent.parent
    templates_path = base_path / "templates"
    static_path = base_path / "static"

    def player_ids() -> list[int]:
        if session is None:
            return []
        return sorted(session.remaining_pieces)

    def player_count() -> int:
        config = getattr(session, "config", None)
        config_player_count = getattr(config, "player_count", None)
        if isinstance(config_player_count, int):
            return config_player_count
        if session is not None and hasattr(session, "remaining_pieces"):
            return len(session.remaining_pieces)
        return len(PLAYER_COLORS)

    def controller_type(player_id: int) -> str:
        if not setup_started:
            return "human"
        return "human" if player_id < human_player_count else "ai"

    def player_color(player_id: int) -> str:
        if 0 <= player_id < len(PLAYER_COLORS):
            return PLAYER_COLORS[player_id]
        return f"Player {player_id}"

    def game_status_value():
        status = session.detect_termination()
        return getattr(status, "name", status)

    def is_finished() -> bool:
        return game_status_value() == GameStatus.FINISHED

    def render_board() -> None:
        if presenter is not None:
            presenter.render_board(session.board.grid)

    def get_enumerator():
        nonlocal legal_move_enumerator
        if legal_move_enumerator is None:
            legal_move_enumerator = LegalMoveEnumerator(
                session.catalog, session.ruleset
            )
        return legal_move_enumerator

    def get_ai_player():
        nonlocal ai_player
        if ai_player is None:
            ai_player = SimpleAiPlayer(session.catalog, session.board)
        return ai_player

    def player_controller_payload() -> list[dict]:
        return [
            {
                "id": player_id,
                "color": player_color(player_id),
                "controller_type": controller_type(player_id),
            }
            for player_id in player_ids()
        ]

    def score_payload() -> list[dict]:
        return [
            {
                "player_id": score.player_id,
                "color": player_color(score.player_id),
                "score": score.score,
                "is_winner": score.is_winner,
            }
            for score in session.final_scores()
        ]

    def legal_moves_for(player_id: int) -> list[Move]:
        return get_enumerator().find_moves(
            session.board,
            player_id,
            session.remaining_pieces[player_id],
            session.is_first_move(player_id),
        )

    def skipped_payload(player_id: int) -> dict:
        color = player_color(player_id)
        return {
            "player_id": player_id,
            "color": color,
            "controller_type": controller_type(player_id),
            "action": "pass",
            "reason": "no_legal_moves",
            "message": f"{color} has no legal moves and was skipped.",
        }

    def set_last_event(event: dict | None) -> None:
        nonlocal last_event
        last_event = event

    def reset_runtime_state() -> None:
        nonlocal session, setup_started, human_player_count, last_event
        nonlocal recent_skipped_players, ai_player, legal_move_enumerator
        if session_factory is not None:
            session = session_factory()
        setup_started = False
        human_player_count = 0
        last_event = None
        recent_skipped_players = []
        if not provided_ai_player:
            ai_player = None
        if not provided_legal_move_enumerator:
            legal_move_enumerator = None

    def resolve_automatic_turns(
        clear_previous_skips: bool = False,
    ) -> tuple[list[dict], bool | None]:
        nonlocal recent_skipped_players
        if session is None or not setup_started:
            return [], None
        if clear_previous_skips:
            recent_skipped_players = []
        actions = []
        skips_this_run = []
        max_turns = (
            sum(len(pieces) for pieces in session.remaining_pieces.values())
            + player_count()
        )
        turns = 0
        while turns < max_turns and not is_finished():
            player_id = session.current_player_id
            legal_moves = legal_moves_for(player_id)
            if not legal_moves:
                session.submit_pass()
                skipped = skipped_payload(player_id)
                actions.append({"player_id": player_id, "action": "pass"})
                skips_this_run.append(skipped)
                set_last_event({"type": "player_skipped", **skipped})
                session.advance_turn()
                turns += 1
                continue

            if controller_type(player_id) != "ai":
                if skips_this_run:
                    recent_skipped_players = skips_this_run
                return actions, True

            move = get_ai_player().request_move(player_id, legal_moves)
            if move is None:
                set_last_event(
                    {
                        "type": "ai_no_move",
                        "player_id": player_id,
                        "color": player_color(player_id),
                        "message": f"{player_color(player_id)} AI did not choose from available legal moves.",
                    }
                )
                if skips_this_run:
                    recent_skipped_players = skips_this_run
                return actions, True

            result = session.submit_move(move)
            if result == MoveResult.ILLEGAL:
                set_last_event(
                    {
                        "type": "ai_illegal_move",
                        "player_id": player_id,
                        "color": player_color(player_id),
                        "message": f"{player_color(player_id)} AI selected an illegal move.",
                    }
                )
                if skips_this_run:
                    recent_skipped_players = skips_this_run
                return actions, True

            actions.append(
                {
                    "player_id": player_id,
                    "action": "move",
                    "piece_id": move.piece_id,
                }
            )
            set_last_event(
                {
                    "type": "ai_move",
                    "player_id": player_id,
                    "color": player_color(player_id),
                    "piece_id": move.piece_id,
                    "message": f"{player_color(player_id)} AI placed piece {move.piece_id}.",
                }
            )
            session.advance_turn()
            turns += 1

        if skips_this_run:
            recent_skipped_players = skips_this_run
        if is_finished():
            set_last_event(
                {
                    "type": "game_finished",
                    "message": "Game finished. Final scores are available.",
                }
            )
            return actions, False
        set_last_event(
            {
                "type": "automatic_turn_limit",
                "message": "Automatic turn resolution stopped before reaching a playable turn.",
            }
        )
        return actions, None

    def reject_finished_response() -> dict:
        return {
            "ok": False,
            "error": "Game is finished",
            "game_status": GameStatus.FINISHED,
        }

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
        _, current_player_has_legal_moves = resolve_automatic_turns()
        board = session.board.grid
        current = session.current_player_id
        remaining = session.remaining_pieces
        scores = score_payload()
        status = game_status_value()
        return {
            "started": setup_started,
            "human_players": human_player_count if setup_started else None,
            "board": [
                [cell if cell is not None else None for cell in row] for row in board
            ],
            "current_player_id": current,
            "players": [
                {
                    "id": pid,
                    "color": player_color(pid),
                    "controller_type": controller_type(pid),
                    "remaining_pieces": list(pieces),
                }
                for pid, pieces in sorted(remaining.items())
            ],
            "scores": scores,
            "winner_ids": [
                score["player_id"] for score in scores if score["is_winner"]
            ],
            "game_status": status,
            "consecutive_passes": session.consecutive_passes,
            "last_event": last_event,
            "skipped_players": recent_skipped_players,
            "current_player_has_legal_moves": current_player_has_legal_moves,
            "starting_positions": {
                str(pid): {"row": pos.row, "col": pos.col}
                for pid, pos in session.config.starting_positions.items()
            },
            "scoring_rule": session.config.scoring_rule,
        }

    @app.post("/start")
    def start(start_data: dict):
        nonlocal setup_started, human_player_count
        requested_humans = start_data.get("human_players")
        if isinstance(requested_humans, bool) or not isinstance(requested_humans, int):
            return JSONResponse(
                {"ok": False, "error": "human_players must be an integer"},
                status_code=400,
            )
        max_humans = player_count()
        if requested_humans < 1 or requested_humans > max_humans:
            return JSONResponse(
                {
                    "ok": False,
                    "error": f"human_players must be between 1 and {max_humans}",
                },
                status_code=400,
            )
        if setup_started or is_finished():
            reset_runtime_state()
        setup_started = True
        human_player_count = requested_humans
        ai_actions, _ = resolve_automatic_turns(clear_previous_skips=True)
        render_board()
        return {
            "ok": True,
            "started": setup_started,
            "human_players": human_player_count,
            "players": player_controller_payload(),
            "ai_actions": ai_actions,
        }

    @app.post("/reset")
    def reset():
        reset_runtime_state()
        return {"ok": True, "started": False}

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
                grid_key(grid): index for index, grid in enumerate(orientation_grids)
            }
            rotate_to = []
            flip_to = []
            for index, grid in enumerate(orientation_grids):
                rotate_to.append(
                    find_orientation_index(orientation_indexes, rotate_grid(grid))
                )
                horizontal = find_orientation_index(
                    orientation_indexes, reflect_horizontal(grid)
                )
                if horizontal != index:
                    flip_to.append(horizontal)
                    continue
                vertical = find_orientation_index(
                    orientation_indexes, reflect_vertical(grid)
                )
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
                piece_payload(piece) for piece in session.catalog.get_all_pieces()
            ]
        }

    @app.get("/pieces/{player_id}")
    def pieces(player_id: int):
        return {"pieces": list(session.remaining_pieces[player_id])}

    @app.post("/move")
    def move(move_data: dict):
        if is_finished():
            return reject_finished_response()
        automatic_actions, _ = resolve_automatic_turns(clear_previous_skips=True)
        if is_finished():
            return {**reject_finished_response(), "ai_actions": automatic_actions}
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
        if setup_started and controller_type(move.player_id) != "human":
            return {"ok": False, "error": "Player is controlled by AI"}
        result = session.submit_move(move)
        render_board()
        if result == MoveResult.ILLEGAL:
            return {"ok": False, "error": "Illegal move"}
        set_last_event(
            {
                "type": "human_move",
                "player_id": move.player_id,
                "color": player_color(move.player_id),
                "piece_id": move.piece_id,
                "message": f"{player_color(move.player_id)} placed piece {move.piece_id}.",
            }
        )
        session.advance_turn()
        ai_actions, _ = resolve_automatic_turns(clear_previous_skips=True)
        render_board()
        return {"ok": True, "ai_actions": ai_actions}

    @app.post("/pass")
    def pass_turn():
        if is_finished():
            return reject_finished_response()
        automatic_actions, _ = resolve_automatic_turns(clear_previous_skips=True)
        if is_finished():
            return {**reject_finished_response(), "ai_actions": automatic_actions}
        if setup_started and controller_type(session.current_player_id) != "human":
            return {"ok": False, "error": "Player is controlled by AI"}
        player_id = session.current_player_id
        session.submit_pass()
        set_last_event(
            {
                "type": "human_pass",
                "player_id": player_id,
                "color": player_color(player_id),
                "message": f"{player_color(player_id)} passed.",
            }
        )
        session.advance_turn()
        ai_actions, _ = resolve_automatic_turns(clear_previous_skips=True)
        render_board()
        return {"ok": True, "ai_actions": ai_actions}

    return app
