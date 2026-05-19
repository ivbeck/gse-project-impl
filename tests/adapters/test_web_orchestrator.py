import pytest
from fastapi.testclient import TestClient
from adapters.web_orchestrator import create_web_orchestrator

def test_web_orchestrator_health_check():
    app = create_web_orchestrator(None, None, None)
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_web_orchestrator_state_returns_game_data():
    app = create_web_orchestrator(None, None, None)
    client = TestClient(app)
    response = client.get("/state")
    assert response.status_code == 200
    data = response.json()
    assert "board" in data
    assert "current_player_id" in data
    assert "players" in data
    assert len(data["players"]) == 4