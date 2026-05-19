from core.piece_catalog import PieceCatalog
from core.types import PlayerScore


class Scoring:
    def __init__(self, catalog: PieceCatalog):
        self.catalog = catalog

    def rank(self, remaining: dict[int, list[int]]) -> list[PlayerScore]:
        def piece_square_count(piece_id: int) -> int:
            piece = self.catalog.get_by_id(piece_id)
            return sum(len(row) for row in piece.shape)

        scores = []
        for player_id, piece_ids in remaining.items():
            total = sum(piece_square_count(pid) for pid in piece_ids)
            scores.append(PlayerScore(player_id=player_id, score=total, is_winner=False))

        min_score = min(s.score for s in scores)
        scores = [
            PlayerScore(player_id=s.player_id, score=s.score, is_winner=(s.score == min_score))
            for s in scores
        ]
        return sorted(scores, key=lambda s: s.score)