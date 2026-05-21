from fastapi.testclient import TestClient
from unittest.mock import Mock
from adapters.web_orchestrator import create_web_orchestrator
from bootstrap import create_game
from core.piece_catalog import PieceCatalog
from core.types import MoveResult, ConfigVO, Position


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


def _real_client():
    session = create_game(_config())
    app = create_web_orchestrator(session, None, Mock())
    return TestClient(app)


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
    mock_session.config = _config()

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
    assert "starting_positions" in data
    assert "scoring_rule" in data


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


def test_web_orchestrator_pass_changes_current_player_id():
    client = _real_client()

    response = client.post("/pass")

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert client.get("/state").json()["current_player_id"] == 1


def test_state_exposes_duo_starting_positions_and_rule():
    from adapters.json_config_source import JsonConfigSource, DUO_CONFIG_JSON
    session = create_game(JsonConfigSource(DUO_CONFIG_JSON).load_config())
    app = create_web_orchestrator(session, None, Mock())
    client = TestClient(app)
    data = client.get("/state").json()
    assert data["scoring_rule"] == "duo"
    assert data["starting_positions"] == {"0": {"row": 4, "col": 4}, "1": {"row": 9, "col": 9}}
    assert len(data["players"]) == 2
