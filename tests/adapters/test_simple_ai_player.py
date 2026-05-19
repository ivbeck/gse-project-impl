import pytest
import json
from adapters.simple_ai_player import SimpleAiPlayer
from core.types import ConfigVO, Move, Position
from core.board import Board
from core.game_session import GameSession
from core.legal_move_enumerator import LegalMoveEnumerator
from core.piece_catalog import PieceCatalog
from core.scoring import Scoring
from adapters.json_state_repo import JsonStateRepo


@pytest.fixture
def config():
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


def test_simple_ai_player_prefers_larger_coverage(config):
    catalog = PieceCatalog()
    board = Board(config)
    player = SimpleAiPlayer(catalog, board)
    moves = [
        Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=0),
        Move(player_id=0, piece_id=1, orientation_index=0, row=0, col=0),
    ]
    result = player.request_move(0, moves)
    assert result.piece_id == 1


def test_simple_ai_player_golden_from_json_state():
    state_json = json.dumps({
        "config": {
            "board_width": 20,
            "board_height": 20,
            "player_count": 4,
            "starting_positions": {
                "0": {"row": 0, "col": 0},
                "1": {"row": 0, "col": 19},
                "2": {"row": 19, "col": 19},
                "3": {"row": 19, "col": 0},
            },
        },
        "board_state": [[None for _ in range(20)] for _ in range(20)],
        "current_player_id": 0,
        "remaining_pieces": [[0, [0, 1]], [1, []], [2, []], [3, []]],
        "consecutive_passes": 0,
        "is_first_move": [[0, True], [1, True], [2, True], [3, True]],
    })
    repo = JsonStateRepo()
    memento = repo.restore(state_json)
    catalog = PieceCatalog()
    session = GameSession.from_memento(memento, catalog, Scoring(catalog))
    enumerator = LegalMoveEnumerator(session.catalog, session.ruleset)
    legal_moves = enumerator.find_moves(
        session.board,
        session.current_player_id,
        session.remaining_pieces[session.current_player_id],
        session.is_first_move(session.current_player_id),
    )
    result = SimpleAiPlayer(catalog, session.board).request_move(session.current_player_id, legal_moves)
    assert result == Move(player_id=0, piece_id=1, orientation_index=0, row=0, col=0)
