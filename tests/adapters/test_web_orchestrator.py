from pathlib import Path
from fastapi.testclient import TestClient
import pytest
from unittest.mock import Mock
from adapters.web_orchestrator import create_web_orchestrator
from bootstrap import create_game
from core.piece_catalog import PieceCatalog
from core.types import Move, MoveResult, ConfigVO, Position


def _config():
    return ConfigVO(
        board_width=20,
        board_height=20,
        player_count=4,
        starting_positions={
            0: Position(0, 0),
            1: Position(0, 19),
            2: Position(19, 19),
            3: Position(19, 0),
        }
    )


def _real_client(ai_player=None, legal_move_enumerator=None):
    session = create_game(_config())
    app = create_web_orchestrator(
        session,
        None,
        Mock(),
        ai_player=ai_player,
        legal_move_enumerator=legal_move_enumerator,
    )
    return TestClient(app)


class _FirstLegalMoveAi:
    def request_move(self, player_id: int, legal_moves: list[Move]) -> Move | None:
        return legal_moves[0] if legal_moves else None


class _ScriptedEnumerator:
    def __init__(self, moves_by_player: dict[int, Move]):
        self.moves_by_player = moves_by_player
        self.calls: list[int] = []

    def find_moves(self, board, player_id, remaining_piece_ids, is_first_move=False):
        self.calls.append(player_id)
        move = self.moves_by_player.get(player_id)
        return [move] if move is not None else []


class _NoLegalMovesEnumerator:
    def __init__(self):
        self.calls: list[int] = []

    def find_moves(self, board, player_id, remaining_piece_ids, is_first_move=False):
        self.calls.append(player_id)
        return []


def _orientation_grid(orientation):
    rows = max(r for r, _ in orientation) + 1
    cols = max(c for _, c in orientation) + 1
    grid = [[0] * cols for _ in range(rows)]
    for row, col in orientation:
        grid[row][col] = 1
    return grid


def _grid_key(grid):
    return "/".join("".join(str(cell) for cell in row) for row in grid)


def _rotate_grid(grid):
    rows = len(grid)
    cols = len(grid[0])
    result = [[0] * rows for _ in range(cols)]
    for row_index, row in enumerate(grid):
        for col_index, cell in enumerate(row):
            result[col_index][rows - 1 - row_index] = cell
    return result


def _reflect_horizontal(grid):
    return [list(reversed(row)) for row in grid]


def _reflect_vertical(grid):
    return list(reversed([list(row) for row in grid]))


def _orientation_transitions(orientation_grids):
    orientation_indexes = {
        _grid_key(grid): index
        for index, grid in enumerate(orientation_grids)
    }
    rotate_to = []
    flip_to = []
    for index, grid in enumerate(orientation_grids):
        rotate_to.append(orientation_indexes[_grid_key(_rotate_grid(grid))])
        horizontal = orientation_indexes[_grid_key(_reflect_horizontal(grid))]
        vertical = orientation_indexes[_grid_key(_reflect_vertical(grid))]
        flip_to.append(horizontal if horizontal != index else vertical)
    return rotate_to, flip_to


def test_web_orchestrator_health_check():
    app = create_web_orchestrator(None, None, None)
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_web_orchestrator_index_returns_html():
    app = create_web_orchestrator(None, None, None)
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "<html" in response.text
    assert "id=\"start-screen\"" in response.text


@pytest.mark.parametrize("human_players", [1, 2, 3, 4])
def test_web_orchestrator_start_accepts_valid_human_player_counts(human_players):
    client = _real_client()

    response = client.post("/start", json={"human_players": human_players})

    assert response.status_code == 200
    assert response.json()["ok"] is True
    state = client.get("/state").json()
    assert state["started"] is True
    assert state["human_players"] == human_players


@pytest.mark.parametrize("human_players", [0, 5, "2", 2.0, None, True])
def test_web_orchestrator_start_rejects_invalid_human_player_counts(human_players):
    client = _real_client()

    response = client.post("/start", json={"human_players": human_players})

    assert response.status_code == 400
    assert response.json()["ok"] is False


@pytest.mark.parametrize(
    ("human_players", "expected_controllers"),
    [
        (1, ["human", "ai", "ai", "ai"]),
        (2, ["human", "human", "ai", "ai"]),
        (4, ["human", "human", "human", "human"]),
    ],
)
def test_web_orchestrator_state_maps_human_count_to_controller_types(
    human_players,
    expected_controllers,
):
    client = _real_client()

    client.post("/start", json={"human_players": human_players})
    state = client.get("/state").json()

    assert [player["controller_type"] for player in state["players"]] == expected_controllers


def test_web_orchestrator_state_returns_game_data():
    mock_session = Mock()
    mock_session.board.grid = [[None]*20 for _ in range(20)]
    mock_session.current_player_id = 0
    mock_session.remaining_pieces = {0: list(range(21)), 1: list(range(21)), 2: list(range(21)), 3: list(range(21))}
    mock_session.final_scores.return_value = [
        Mock(player_id=0, score=0, is_winner=False),
        Mock(player_id=1, score=0, is_winner=False),
        Mock(player_id=2, score=0, is_winner=False),
        Mock(player_id=3, score=0, is_winner=False),
    ]
    mock_session.detect_termination.return_value = type('GameStatus', (), {'name': 'IN_PROGRESS'})()
    mock_session.consecutive_passes = 0

    app = create_web_orchestrator(mock_session, None, None)
    client = TestClient(app)
    response = client.get("/state")
    assert response.status_code == 200
    data = response.json()
    assert "board" in data
    assert "current_player_id" in data
    assert "players" in data
    assert "scores" in data
    assert "game_status" in data
    assert "consecutive_passes" in data
    assert "started" in data
    assert all("controller_type" in player for player in data["players"])


def test_web_orchestrator_piece_catalog_exposes_core_shapes():
    client = _real_client()
    catalog = PieceCatalog()

    response = client.get("/piece-catalog")

    assert response.status_code == 200
    expected = [
        _piece_catalog_payload(catalog, piece)
        for piece in catalog.get_all_pieces()
    ]
    assert response.json() == {"pieces": expected}


def _piece_catalog_payload(catalog, piece):
    orientations = [
        _orientation_grid(orientation)
        for orientation in catalog.get_orientations(piece.piece_id)
    ]
    rotate_to, flip_to = _orientation_transitions(orientations)
    return {
        "piece_id": piece.piece_id,
        "shape": [list(row) for row in piece.shape],
        "orientations": orientations,
        "rotate_to": rotate_to,
        "flip_to": flip_to,
    }


def test_web_orchestrator_piece_catalog_exposes_symmetric_orientation_once():
    client = _real_client()

    response = client.get("/piece-catalog")

    assert response.status_code == 200
    monomino = response.json()["pieces"][0]
    assert monomino["orientations"] == [[[1]]]


def test_web_orchestrator_piece_catalog_flip_changes_symmetric_axis_when_possible():
    client = _real_client()

    response = client.get("/piece-catalog")

    assert response.status_code == 200
    t_tetromino = response.json()["pieces"][6]
    assert t_tetromino["flip_to"][0] == 2
    assert t_tetromino["flip_to"][2] == 0


def test_web_orchestrator_piece_catalog_distinguishes_pieces_11_and_15():
    client = _real_client()

    response = client.get("/piece-catalog")

    assert response.status_code == 200
    pieces = {piece["piece_id"]: piece for piece in response.json()["pieces"]}
    assert pieces[11]["shape"] != pieces[15]["shape"]
    assert {_grid_key(grid) for grid in pieces[11]["orientations"]} != {
        _grid_key(grid) for grid in pieces[15]["orientations"]
    }


def test_web_orchestrator_piece_catalog_has_unique_orientation_sets():
    client = _real_client()

    response = client.get("/piece-catalog")

    assert response.status_code == 200
    signatures = [
        tuple(sorted(_grid_key(grid) for grid in piece["orientations"]))
        for piece in response.json()["pieces"]
    ]
    assert len(signatures) == len(set(signatures))


def test_web_orchestrator_piece_catalog_targeted_flips_are_visible():
    client = _real_client()

    response = client.get("/piece-catalog")

    assert response.status_code == 200
    pieces = {piece["piece_id"]: piece for piece in response.json()["pieces"]}
    for piece_id in (6, 9, 11, 15):
        piece = pieces[piece_id]
        for orientation_index in (0, 2):
            target_index = piece["flip_to"][orientation_index]
            assert target_index != orientation_index
            assert piece["orientations"][target_index] != piece["orientations"][orientation_index]


def test_web_orchestrator_piece_catalog_transition_indexes_are_in_range():
    client = _real_client()

    response = client.get("/piece-catalog")

    assert response.status_code == 200
    for piece in response.json()["pieces"]:
        orientation_count = len(piece["orientations"])
        assert len(piece["rotate_to"]) == orientation_count
        assert len(piece["flip_to"]) == orientation_count
        assert all(0 <= index < orientation_count for index in piece["rotate_to"])
        assert all(0 <= index < orientation_count for index in piece["flip_to"])


def test_web_orchestrator_piece_catalog_transitions_match_grid_transforms():
    client = _real_client()

    response = client.get("/piece-catalog")

    assert response.status_code == 200
    for piece in response.json()["pieces"]:
        orientations = piece["orientations"]
        for index, grid in enumerate(orientations):
            assert orientations[piece["rotate_to"][index]] == _rotate_grid(grid)
            horizontal = _reflect_horizontal(grid)
            vertical = _reflect_vertical(grid)
            if horizontal != grid:
                expected_flip = horizontal
            elif vertical != grid:
                expected_flip = vertical
            else:
                expected_flip = grid
            assert orientations[piece["flip_to"][index]] == expected_flip


def test_web_orchestrator_move_submits_to_session():
    mock_session = Mock()
    mock_session.submit_move.return_value = MoveResult.LEGAL
    mock_session.board.grid = [[None]*20 for _ in range(20)]
    mock_session.current_player_id = 0
    mock_session.remaining_pieces = {0: list(range(21)), 1: list(range(21)), 2: list(range(21)), 3: list(range(21))}
    mock_session.final_scores.return_value = [
        Mock(player_id=0, score=0, is_winner=False),
        Mock(player_id=1, score=0, is_winner=False),
        Mock(player_id=2, score=0, is_winner=False),
        Mock(player_id=3, score=0, is_winner=False),
    ]
    mock_session.detect_termination.return_value = type('GameStatus', (), {'name': 'IN_PROGRESS'})()
    mock_session.consecutive_passes = 0
    mock_presenter = Mock()

    app = create_web_orchestrator(mock_session, None, mock_presenter)
    client = TestClient(app)

    response = client.post("/move", json={
        "player_id": 0,
        "piece_id": 7,
        "orientation_index": 0,
        "row": 0,
        "col": 0,
    })

    assert response.status_code == 200
    assert response.json()["ok"] == True
    mock_session.submit_move.assert_called_once()
    assert mock_session.submit_move.call_args.args[0].piece_id == 7
    mock_session.advance_turn.assert_called_once()
    mock_presenter.render_board.assert_called()


def test_web_orchestrator_move_returns_error_on_illegal():
    mock_session = Mock()
    mock_session.submit_move.return_value = MoveResult.ILLEGAL
    mock_session.board.grid = [[None]*20 for _ in range(20)]
    mock_session.current_player_id = 0
    mock_session.remaining_pieces = {0: list(range(21)), 1: list(range(21)), 2: list(range(21)), 3: list(range(21))}
    mock_session.final_scores.return_value = [
        Mock(player_id=0, score=0, is_winner=False),
        Mock(player_id=1, score=0, is_winner=False),
        Mock(player_id=2, score=0, is_winner=False),
        Mock(player_id=3, score=0, is_winner=False),
    ]
    mock_session.detect_termination.return_value = type('GameStatus', (), {'name': 'IN_PROGRESS'})()
    mock_session.consecutive_passes = 0
    mock_presenter = Mock()

    app = create_web_orchestrator(mock_session, None, mock_presenter)
    client = TestClient(app)

    response = client.post("/move", json={
        "player_id": 0,
        "piece_id": 0,
        "orientation_index": 0,
        "row": 0,
        "col": 0,
    })

    assert response.status_code == 200
    assert response.json()["ok"] == False
    assert "error" in response.json()
    mock_session.advance_turn.assert_not_called()


def test_web_orchestrator_pass_submits_to_session():
    mock_session = Mock()
    mock_session.submit_pass.return_value = None
    mock_session.board.grid = [[None]*20 for _ in range(20)]
    mock_session.current_player_id = 0
    mock_session.remaining_pieces = {0: list(range(21)), 1: list(range(21)), 2: list(range(21)), 3: list(range(21))}
    mock_session.final_scores.return_value = [
        Mock(player_id=0, score=0, is_winner=False),
        Mock(player_id=1, score=0, is_winner=False),
        Mock(player_id=2, score=0, is_winner=False),
        Mock(player_id=3, score=0, is_winner=False),
    ]
    mock_session.detect_termination.return_value = type('GameStatus', (), {'name': 'IN_PROGRESS'})()
    mock_session.consecutive_passes = 0
    mock_presenter = Mock()

    app = create_web_orchestrator(mock_session, None, mock_presenter)
    client = TestClient(app)

    response = client.post("/pass")

    assert response.status_code == 200
    assert response.json()["ok"] == True
    mock_session.submit_pass.assert_called_once()
    mock_session.advance_turn.assert_called_once()


def test_web_orchestrator_legal_move_changes_current_player_id():
    client = _real_client()

    response = client.post("/move", json={
        "player_id": 0,
        "piece_id": 0,
        "orientation_index": 0,
        "row": 0,
        "col": 0,
    })

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert client.get("/state").json()["current_player_id"] == 1


def test_web_orchestrator_illegal_move_keeps_current_player_id():
    client = _real_client()

    response = client.post("/move", json={
        "player_id": 1,
        "piece_id": 0,
        "orientation_index": 0,
        "row": 0,
        "col": 19,
    })

    assert response.status_code == 200
    assert response.json()["ok"] is False
    assert client.get("/state").json()["current_player_id"] == 0


def test_web_orchestrator_auto_resolves_ai_players_after_human_move():
    enumerator = _ScriptedEnumerator({
        1: Move(player_id=1, piece_id=0, orientation_index=0, row=0, col=19),
        2: Move(player_id=2, piece_id=0, orientation_index=0, row=19, col=19),
        3: Move(player_id=3, piece_id=0, orientation_index=0, row=19, col=0),
    })
    client = _real_client(
        ai_player=_FirstLegalMoveAi(),
        legal_move_enumerator=enumerator,
    )
    client.post("/start", json={"human_players": 1})

    response = client.post("/move", json={
        "player_id": 0,
        "piece_id": 0,
        "orientation_index": 0,
        "row": 0,
        "col": 0,
    })

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert response.json()["ai_actions"] == [
        {"player_id": 1, "action": "move", "piece_id": 0},
        {"player_id": 2, "action": "move", "piece_id": 0},
        {"player_id": 3, "action": "move", "piece_id": 0},
    ]
    state = client.get("/state").json()
    assert state["current_player_id"] == 0
    assert [len(player["remaining_pieces"]) for player in state["players"]] == [20, 20, 20, 20]
    assert enumerator.calls == [1, 2, 3]


def test_web_orchestrator_human_move_then_ai_turns_end_on_next_human():
    enumerator = _ScriptedEnumerator({
        2: Move(player_id=2, piece_id=0, orientation_index=0, row=19, col=19),
        3: Move(player_id=3, piece_id=0, orientation_index=0, row=19, col=0),
    })
    client = _real_client(
        ai_player=_FirstLegalMoveAi(),
        legal_move_enumerator=enumerator,
    )
    client.post("/start", json={"human_players": 2})
    first_response = client.post("/move", json={
        "player_id": 0,
        "piece_id": 0,
        "orientation_index": 0,
        "row": 0,
        "col": 0,
    })

    second_response = client.post("/move", json={
        "player_id": 1,
        "piece_id": 0,
        "orientation_index": 0,
        "row": 0,
        "col": 19,
    })

    assert first_response.json()["ai_actions"] == []
    assert second_response.json()["ai_actions"] == [
        {"player_id": 2, "action": "move", "piece_id": 0},
        {"player_id": 3, "action": "move", "piece_id": 0},
    ]
    assert client.get("/state").json()["current_player_id"] == 0


def test_web_orchestrator_ai_passes_when_no_legal_move_exists():
    enumerator = _NoLegalMovesEnumerator()
    client = _real_client(legal_move_enumerator=enumerator)
    client.post("/start", json={"human_players": 1})

    response = client.post("/move", json={
        "player_id": 0,
        "piece_id": 0,
        "orientation_index": 0,
        "row": 0,
        "col": 0,
    })

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert response.json()["ai_actions"] == [
        {"player_id": 1, "action": "pass"},
        {"player_id": 2, "action": "pass"},
        {"player_id": 3, "action": "pass"},
    ]
    state = client.get("/state").json()
    assert state["current_player_id"] == 0
    assert state["consecutive_passes"] == 3
    assert enumerator.calls == [1, 2, 3]


def test_web_orchestrator_pass_changes_current_player_id():
    client = _real_client()

    response = client.post("/pass")

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert client.get("/state").json()["current_player_id"] == 1


def test_web_orchestrator_ai_processing_does_not_import_adapters_from_core():
    core_path = Path(__file__).resolve().parents[2] / "src" / "core"

    for path in core_path.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "from adapters" not in source
        assert "import adapters" not in source
