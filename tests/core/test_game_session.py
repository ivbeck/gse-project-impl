import pytest
from core.game_session import GameSession
from core.types import ConfigVO, Position, Move, MoveResult, GameStatus
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
def catalog():
    return PieceCatalog()


@pytest.fixture
def session(config, catalog):
    ruleset = RuleSet(catalog, config)
    scoring = Scoring(catalog)
    return GameSession(config, catalog, ruleset, scoring)


def test_game_session_initializes_with_player_0(session):
    assert session.current_player_id == 0


def test_game_session_submit_legal_move(session):
    move = Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=0)
    result = session.submit_move(move)
    assert result == MoveResult.LEGAL


def test_game_session_detect_termination_not_terminated(session):
    assert session.detect_termination() == GameStatus.IN_PROGRESS


def test_game_session_final_scores(session):
    scores = session.final_scores()
    assert len(scores) == 4


def test_game_session_advance_turn(session):
    session.advance_turn()
    assert session.current_player_id == 1