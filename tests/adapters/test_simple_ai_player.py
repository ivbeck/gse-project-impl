import pytest
from adapters.simple_ai_player import SimpleAiPlayer
from core.types import Move


def test_simple_ai_player_deterministic():
    """Regression test for DR-4: AI must be deterministic."""
    player = SimpleAiPlayer()
    moves = [
        Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=0),
        Move(player_id=0, piece_id=1, orientation_index=0, row=0, col=1),
        Move(player_id=0, piece_id=2, orientation_index=0, row=1, col=0),
    ]
    result1 = player.request_move(0, moves)
    result2 = player.request_move(0, moves)
    assert result1 == result2


def test_simple_ai_player_returns_none_when_no_moves():
    player = SimpleAiPlayer()
    result = player.request_move(0, [])
    assert result is None


def test_simple_ai_player_chooses_lexicographically_first():
    """Lexicographic tie-break: sorted by (row, col, piece_id, orientation_index)."""
    player = SimpleAiPlayer()
    moves = [
        Move(player_id=0, piece_id=5, orientation_index=0, row=2, col=3),
        Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=0),
        Move(player_id=0, piece_id=10, orientation_index=0, row=0, col=0),
    ]
    result = player.request_move(0, moves)
    assert result.row == 0
    assert result.col == 0
    assert result.piece_id == 0