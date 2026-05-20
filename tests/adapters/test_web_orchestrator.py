from fastapi.testclient import TestClient
from unittest.mock import Mock
from adapters.web_orchestrator import create_web_orchestrator
from bootstrap import create_game
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
        "piece_id": 0,
        "orientation_index": 0,
        "row": 0,
        "col": 0,
    })

    assert response.status_code == 200
    assert response.json()["ok"] == True
    mock_session.submit_move.assert_called_once()
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
