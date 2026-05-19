from core.types import Move, MoveResult
from core.board import Board
from core.piece_catalog import PieceCatalog
from core.rule_set import RuleSet


class LegalMoveEnumerator:
    def __init__(self, catalog: PieceCatalog, ruleset: RuleSet):
        self.catalog = catalog
        self.ruleset = ruleset

    def find_moves(
        self,
        board: Board,
        player_id: int,
        remaining_piece_ids: list[int],
        is_first_move: bool = False
    ) -> list[Move]:
        legal_moves = []
        for piece_id in remaining_piece_ids:
            orientations = self.catalog.get_orientations(piece_id)
            for orient_idx, orientation in enumerate(orientations):
                for row in range(board.config.board_height):
                    for col in range(board.config.board_width):
                        move = Move(
                            player_id=player_id,
                            piece_id=piece_id,
                            orientation_index=orient_idx,
                            row=row,
                            col=col
                        )
                        result = self.ruleset.check_legality(
                            board, move, is_first_move, orientation
                        )
                        if result == MoveResult.LEGAL:
                            legal_moves.append(move)
        legal_moves.sort(key=lambda m: (
            m.row, m.col, m.piece_id, m.orientation_index
        ))
        return legal_moves