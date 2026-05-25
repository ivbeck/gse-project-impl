import pytest

from adapters.human_player import HumanPlayer
from adapters.simple_ai_player import SimpleAiPlayer
from bootstrap import create_game, create_player_inputs, run_turn
from core.types import ConfigVO, Move, Position


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
        },
    )


class _FixedEnumerator:
    def __init__(self, moves):
        self.moves = moves
        self.calls = []

    def find_moves(self, board, player_id, remaining_piece_ids, is_first_move=False):
        self.calls.append((player_id, list(remaining_piece_ids), is_first_move))
        return list(self.moves)


def test_bootstrap_under_200_lines():
    import pathlib

    bootstrap = pathlib.Path("src/bootstrap.py")
    if bootstrap.exists():
        lines = len(bootstrap.read_text().splitlines())
        assert lines <= 200, f"Bootstrap is {lines} lines, must be ≤200"


def test_create_player_inputs_maps_one_human_then_ai_players():
    session = create_game(_config())

    player_inputs = create_player_inputs(session, 1)

    assert isinstance(player_inputs[0], HumanPlayer)
    assert isinstance(player_inputs[1], SimpleAiPlayer)
    assert isinstance(player_inputs[2], SimpleAiPlayer)
    assert isinstance(player_inputs[3], SimpleAiPlayer)


def test_create_player_inputs_maps_four_humans():
    session = create_game(_config())

    player_inputs = create_player_inputs(session, 4)

    assert all(
        isinstance(player_inputs[player_id], HumanPlayer) for player_id in range(4)
    )


@pytest.mark.parametrize("human_player_count", [0, 5])
def test_create_player_inputs_rejects_counts_outside_configured_range(
    human_player_count,
):
    session = create_game(_config())

    with pytest.raises(ValueError):
        create_player_inputs(session, human_player_count)


def test_run_turn_uses_ai_player_to_submit_selected_move(capsys):
    session = create_game(_config())
    session.current_player_id = 1
    player_inputs = create_player_inputs(session, 1)
    move = Move(player_id=1, piece_id=0, orientation_index=0, row=0, col=19)
    enumerator = _FixedEnumerator([move])

    advanced = run_turn(session, player_inputs, enumerator)

    assert advanced is True
    assert session.board.grid[0][19] == 1
    assert 0 not in session.remaining_pieces[1]
    assert session.current_player_id == 2
    assert enumerator.calls[0][0] == 1
    assert "AI player 1 places piece 0" in capsys.readouterr().out


def test_run_turn_ai_passes_when_no_legal_moves(capsys):
    session = create_game(_config())
    session.current_player_id = 1
    player_inputs = create_player_inputs(session, 1)
    enumerator = _FixedEnumerator([])

    advanced = run_turn(session, player_inputs, enumerator)

    assert advanced is True
    assert session.consecutive_passes == 1
    assert session.current_player_id == 2
    assert "AI player 1 passes." in capsys.readouterr().out


def test_create_game_uses_duo_scoring_for_duo_config():
    from bootstrap import create_game
    from adapters.json_config_source import JsonConfigSource, DUO_CONFIG_JSON
    from core.scoring import DuoScoring

    config = JsonConfigSource(DUO_CONFIG_JSON).load_config()
    session = create_game(config)
    assert isinstance(session.scoring, DuoScoring)
    assert session.config.player_count == 2


def test_create_game_uses_classic_scoring_by_default():
    from bootstrap import create_game
    from adapters.json_config_source import JsonConfigSource
    from core.scoring import Scoring

    session = create_game(JsonConfigSource().load_config())
    assert isinstance(session.scoring, Scoring)
