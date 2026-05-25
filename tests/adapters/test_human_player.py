from unittest.mock import patch
from adapters.human_player import HumanPlayer
from core.types import Move

def test_human_player_request_move():
    with patch('builtins.input', return_value='0'):
        player = HumanPlayer()
        move = player.request_move(0, [
            Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=0)
        ])
        assert move is not None
        assert move.player_id == 0

def test_human_player_pass_when_no_moves():
    with patch('builtins.input', return_value='-1'):
        player = HumanPlayer()
        move = player.request_move(0, [
            Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=0)
        ])
        assert move is None

def test_human_player_invalid_index_reprompts():
    with patch('builtins.input', side_effect=['999', '0']):
        player = HumanPlayer()
        legal_moves = [Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=0)]
        move = player.request_move(0, legal_moves)
        assert move == legal_moves[0]


def test_human_player_invalid_text_reprompts():
    with patch('builtins.input', side_effect=['abc', '-1']):
        player = HumanPlayer()
        legal_moves = [Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=0)]
        move = player.request_move(0, legal_moves)
        assert move is None

def test_human_player_empty_moves_returns_none():
    player = HumanPlayer()
    move = player.request_move(0, [])
    assert move is None
