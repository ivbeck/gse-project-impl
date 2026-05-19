import pytest
from core.scoring import Scoring
from core.piece_catalog import PieceCatalog


@pytest.fixture
def catalog():
    return PieceCatalog()


def test_scoring_all_remaining_pieces(catalog):
    scoring = Scoring(catalog)
    remaining = {0: list(range(21)), 1: list(range(21)), 2: list(range(21)), 3: list(range(21))}
    scores = scoring.rank(remaining)
    assert len(scores) == 4
    assert all(s.score == 129 for s in scores)
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