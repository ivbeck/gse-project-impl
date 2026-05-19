import pytest
from adapters.web_player_adapter import WebPlayerAdapter

def test_web_player_adapter_request_move_returns_none_when_no_response():
    adapter = WebPlayerAdapter()
    result = adapter.request_move(0, [])
    assert result is None