import pytest
from core.memento import Memento
from core.types import ConfigVO, Position
from core.game_session import GameSession
from core.piece_catalog import PieceCatalog
from core.rule_set import RuleSet
from core.scoring import Scoring


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
        },
    )


@pytest.fixture
def session(config):
    catalog = PieceCatalog()
    ruleset = RuleSet(catalog, config)
    scoring = Scoring(catalog)
    return GameSession(config, catalog, ruleset, scoring)


def test_memento_contains_config(session, config):
    m = Memento.from_session(session)
    assert m.config == config
    assert m.config.board_width == 20
    assert m.config.board_height == 20


def test_memento_contains_board_state(session):
    m = Memento.from_session(session)
    assert len(m.board_state) == 20
    assert len(m.board_state[0]) == 20


def test_memento_contains_remaining_pieces(session):
    m = Memento.from_session(session)
    assert len(m.remaining_pieces) == 4
    assert all(len(pieces) == 21 for _, pieces in m.remaining_pieces)


def test_memento_captures_last_placed_piece(session):
    from core.types import Move

    session.submit_move(
        Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=0)
    )
    m = Memento.from_session(session)
    assert (0, 0) in m.last_placed_piece
    assert (1, None) in m.last_placed_piece
