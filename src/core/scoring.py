from core.piece_catalog import PieceCatalog
from core.types import ConfigVO, PlayerScore


def piece_square_count(catalog: PieceCatalog, piece_id: int) -> int:
    piece = catalog.get_by_id(piece_id)
    return sum(cell for row in piece.shape for cell in row)


class Scoring:
    def __init__(self, catalog: PieceCatalog):
        self.catalog = catalog

    def rank(self, remaining: dict[int, list[int]], last_placed_piece=None) -> list[PlayerScore]:
        scores = []
        for player_id, piece_ids in remaining.items():
            total = sum(piece_square_count(self.catalog, pid) for pid in piece_ids)
            scores.append(PlayerScore(player_id=player_id, score=total, is_winner=False))

        min_score = min(s.score for s in scores)
        scores = [
            PlayerScore(player_id=s.player_id, score=s.score, is_winner=(s.score == min_score))
            for s in scores
        ]
        return sorted(scores, key=lambda s: s.score)


class DuoScoring(Scoring):
    """Duo mode uses the same basic scoring scheme as Classic.

    Per the scoring requirement and the team's decision recorded as AMB-05,
    both modes score by the total remaining unplaced squares (lower is better,
    lowest wins); the optional placement bonuses were explicitly rejected. This
    subclass exists only as a distinct strategy type for ``build_scoring``; it
    inherits Classic's ``rank`` so the two modes stay consistent and avoid
    duplication.
    """


def build_scoring(config: ConfigVO, catalog: PieceCatalog):
    if config.scoring_rule == "duo":
        return DuoScoring(catalog)
    return Scoring(catalog)
