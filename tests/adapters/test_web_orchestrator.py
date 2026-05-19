import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock
from adapters.web_orchestrator import create_web_orchestrator

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
    assert "<html>" in response.text


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