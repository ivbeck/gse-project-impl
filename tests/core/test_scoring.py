import pytest
from core.scoring import Scoring
from core.piece_catalog import PieceCatalog
from core.scoring import DuoScoring, build_scoring
from core.types import ConfigVO, Position


@pytest.fixture
def catalog():
    return PieceCatalog()


def test_scoring_all_remaining_pieces(catalog):
    scoring = Scoring(catalog)
    remaining = {0: list(range(21)), 1: list(range(21)), 2: list(range(21)), 3: list(range(21))}
    scores = scoring.rank(remaining)
    assert len(scores) == 4
    assert all(s.score == 89 for s in scores)
    assert all(s.is_winner for s in scores)


def test_scoring_one_player_placed_all(catalog):
    scoring = Scoring(catalog)
    remaining = {0: [], 1: list(range(21)), 2: list(range(21)), 3: list(range(21))}
    scores = scoring.rank(remaining)
    p0_score = next(s for s in scores if s.player_id == 0)
    assert p0_score.score == 0
    assert p0_score.is_winner


def test_scoring_tie(catalog):
    scoring = Scoring(catalog)
    remaining = {0: [0], 1: [0], 2: list(range(21)), 3: list(range(21))}
    scores = scoring.rank(remaining)
    p0 = next(s for s in scores if s.player_id == 0)
    p1 = next(s for s in scores if s.player_id == 1)
    p2 = next(s for s in scores if s.player_id == 2)
    p3 = next(s for s in scores if s.player_id == 3)
    assert p0.score == p1.score
    assert p0.is_winner and p1.is_winner
    assert not p2.is_winner and not p3.is_winner


def test_duo_all_placed_ending_on_monomino_scores_20(catalog):
    duo = DuoScoring(catalog)
    scores = duo.rank({0: [], 1: list(range(21))}, last_placed_piece={0: 0, 1: None})
    p0 = next(s for s in scores if s.player_id == 0)
    assert p0.score == 20  # 0 remaining + 15 all-placed + 5 monomino-last
    assert p0.is_winner


def test_duo_all_placed_not_monomino_last_scores_15(catalog):
    duo = DuoScoring(catalog)
    scores = duo.rank({0: [], 1: list(range(21))}, last_placed_piece={0: 5, 1: None})
    p0 = next(s for s in scores if s.player_id == 0)
    assert p0.score == 15


def test_duo_remaining_squares_are_negative_and_highest_wins(catalog):
    duo = DuoScoring(catalog)
    # piece 2 is a 3-square piece, piece 4 a 4-square piece -> 10 squares remaining
    scores = duo.rank({0: [2, 2, 4], 1: []}, last_placed_piece={0: None, 1: 7})
    p0 = next(s for s in scores if s.player_id == 0)
    p1 = next(s for s in scores if s.player_id == 1)
    assert p0.score == -10
    assert p1.score == 15
    assert p1.is_winner and not p0.is_winner
    assert scores[0].player_id == 1  # sorted highest-first


def test_duo_tie_yields_co_winners(catalog):
    duo = DuoScoring(catalog)
    scores = duo.rank({0: [], 1: []}, last_placed_piece={0: 0, 1: 0})
    assert all(s.score == 20 for s in scores)
    assert all(s.is_winner for s in scores)


def test_duo_no_bonus_if_remaining_despite_monomino_last(catalog):
    duo = DuoScoring(catalog)
    # 1 square remaining; monomino-last must NOT grant the +5 (or +15) bonus.
    scores = duo.rank({0: [0], 1: []}, last_placed_piece={0: 0, 1: None})
    p0 = next(s for s in scores if s.player_id == 0)
    assert p0.score == -1


def test_build_scoring_selects_strategy_by_config(catalog):
    classic = ConfigVO(board_width=20, board_height=20, player_count=4,
                       starting_positions={0: Position(0, 0)}, scoring_rule="classic")
    duo = ConfigVO(board_width=14, board_height=14, player_count=2,
                   starting_positions={0: Position(4, 4)}, scoring_rule="duo")
    assert isinstance(build_scoring(classic, catalog), Scoring)
    assert isinstance(build_scoring(duo, catalog), DuoScoring)
