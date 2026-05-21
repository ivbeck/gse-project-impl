from core.piece_catalog import PieceCatalog
from core.types import ConfigVO, PlayerScore


MONOMINO_SQUARE_COUNT = 1


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


class DuoScoring:
    def __init__(self, catalog: PieceCatalog):
        self.catalog = catalog

    def rank(self, remaining: dict[int, list[int]], last_placed_piece=None) -> list[PlayerScore]:
        last_placed_piece = last_placed_piece or {}
        scores = []
        for player_id, piece_ids in remaining.items():
            remaining_squares = sum(piece_square_count(self.catalog, pid) for pid in piece_ids)
            score = -remaining_squares
            if remaining_squares == 0:
                score += 15
                last = last_placed_piece.get(player_id)
                if last is not None and piece_square_count(self.catalog, last) == MONOMINO_SQUARE_COUNT:
                    score += 5
            scores.append(PlayerScore(player_id=player_id, score=score, is_winner=False))

        max_score = max(s.score for s in scores)
        scores = [
            PlayerScore(player_id=s.player_id, score=s.score, is_winner=(s.score == max_score))
            for s in scores
        ]
        return sorted(scores, key=lambda s: -s.score)


def build_scoring(config: ConfigVO, catalog: PieceCatalog):
    if config.scoring_rule == "duo":
        return DuoScoring(catalog)
    return Scoring(catalog)
