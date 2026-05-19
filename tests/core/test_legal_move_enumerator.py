import pytest
from core.legal_move_enumerator import LegalMoveEnumerator
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
        }
    )


@pytest.fixture
def session(config):
    catalog = PieceCatalog()
    ruleset = RuleSet(catalog, config)
    scoring = Scoring(catalog)
    return GameSession(config, catalog, ruleset, scoring)


@pytest.fixture
def enumerator(session):
    return LegalMoveEnumerator(session.catalog, session.ruleset)


def test_enumerator_returns_moves_in_sorted_order(session, enumerator):
    moves = enumerator.find_moves(session.board, 0, session.remaining_pieces[0])
    if len(moves) > 1:
        for i in range(len(moves) - 1):
            curr = moves[i]
            next_ = moves[i + 1]
            assert (curr.row, curr.col, curr.piece_id, curr.orientation_index) <= \
                   (next_.row, next_.col, next_.piece_id, next_.orientation_index)


def test_enumerator_finds_first_move_corner(session, enumerator):
    moves = enumerator.find_moves(session.board, 0, [0], is_first_move=True)
    assert len(moves) == 1
    move = moves[0]
    assert move.row == 0 and move.col == 0


def test_enumerator_empty_when_no_pieces(session, enumerator):
    moves = enumerator.find_moves(session.board, 0, [])
    assert len(moves) == 0