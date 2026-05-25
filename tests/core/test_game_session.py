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
        },
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
    assert session.board.get_owner(0, 0) == 0
    assert 0 not in session.remaining_pieces[0]
    assert not session.is_first_move(0)


def test_game_session_rejects_wrong_turn(session):
    move = Move(player_id=1, piece_id=0, orientation_index=0, row=0, col=19)
    result = session.submit_move(move)
    assert result == MoveResult.ILLEGAL
    assert session.board.get_owner(0, 19) is None


def test_game_session_rejects_reused_piece(session):
    move = Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=0)
    assert session.submit_move(move) == MoveResult.LEGAL
    assert session.submit_move(move) == MoveResult.ILLEGAL


def test_game_session_rejects_invalid_orientation(session):
    move = Move(player_id=0, piece_id=0, orientation_index=99, row=0, col=0)
    assert session.submit_move(move) == MoveResult.ILLEGAL


def test_game_session_detect_termination_not_terminated(session):
    assert session.detect_termination() == GameStatus.IN_PROGRESS


def test_game_session_final_scores(session):
    scores = session.final_scores()
    assert len(scores) == 4


def test_game_session_advance_turn(session):
    session.advance_turn()
    assert session.current_player_id == 1


def test_game_session_restore_uses_memento_config(session):
    from core.memento import Memento

    session.submit_move(
        Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=0)
    )
    memento = Memento.from_session(session)
    catalog = PieceCatalog()
    restored = GameSession.from_memento(memento, catalog)
    assert restored.config == memento.config
    assert restored.board.config == memento.config
    assert restored.board.get_owner(0, 0) == 0
    assert restored.remaining_pieces == session.remaining_pieces


def test_last_placed_piece_starts_none(session):
    assert session.last_placed_piece == {0: None, 1: None, 2: None, 3: None}


def test_last_placed_piece_records_successful_move(session):
    session.submit_move(
        Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=0)
    )
    assert session.last_placed_piece[0] == 0
    assert session.last_placed_piece[1] is None


def test_from_memento_restores_scoring_and_last_placed(session):
    from core.memento import Memento
    from core.scoring import DuoScoring
    from core.types import ConfigBuilder, Position

    duo_config = (
        ConfigBuilder()
        .with_board_dimensions(14, 14)
        .with_player_count(2)
        .with_starting_positions({0: Position(4, 4), 1: Position(9, 9)})
        .with_scoring_rule("duo")
        .build()
    )
    catalog = PieceCatalog()
    ruleset = RuleSet(catalog, duo_config)
    duo_session = GameSession(duo_config, catalog, ruleset, Scoring(catalog))
    duo_session.submit_move(
        Move(player_id=0, piece_id=0, orientation_index=0, row=4, col=4)
    )
    memento = Memento.from_session(duo_session)
    restored = GameSession.from_memento(memento, catalog)
    assert isinstance(restored.scoring, DuoScoring)
    assert restored.last_placed_piece == {0: 0, 1: None}
