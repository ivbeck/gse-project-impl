from core.types import ConfigVO, Move, MoveResult, Position
from core.board import Board
from core.piece_catalog import PieceCatalog


class RuleSet:
    def __init__(self, catalog: PieceCatalog, config: ConfigVO):
        self.catalog = catalog
        self.config = config

    def is_corner_position(self, pos: Position, config: ConfigVO) -> bool:
        return (pos.row, pos.col) in [
            (0, 0),
            (0, config.board_width - 1),
            (config.board_height - 1, 0),
            (config.board_height - 1, config.board_width - 1),
        ]

    def check_legality(
        self,
        board: Board,
        move: Move,
        is_first_move: bool,
        cells: list[tuple[int, int]],
    ) -> MoveResult:
        player_id = move.player_id
        if player_id not in self.config.starting_positions:
            return MoveResult.ILLEGAL
        if not self._cells_fit_empty_board_spaces(board, move, cells):
            return MoveResult.ILLEGAL
        if is_first_move:
            corner = self.config.starting_positions[player_id]
            covers_corner = any(
                move.row + dr == corner.row and move.col + dc == corner.col
                for dr, dc in cells
            )
            if not covers_corner:
                return MoveResult.ILLEGAL
        else:
            if not self._touches_corner_diagonally(board, move, cells, player_id):
                return MoveResult.ILLEGAL
        if self._has_orthogonal_same_color(board, move, cells, player_id):
            return MoveResult.ILLEGAL
        return MoveResult.LEGAL

    def _cells_fit_empty_board_spaces(
        self,
        board: Board,
        move: Move,
        cells: list[tuple[int, int]],
    ) -> bool:
        for dr, dc in cells:
            row, col = move.row + dr, move.col + dc
            if not board.in_bounds(row, col):
                return False
            if board.is_occupied(row, col):
                return False
        return True

    def _touches_corner_diagonally(
        self,
        board: Board,
        move: Move,
        cells: list[tuple[int, int]],
        player_id: int,
    ) -> bool:
        for dr, dc in cells:
            row, col = move.row + dr, move.col + dc
            if board.has_diagonal_neighbor(row, col, player_id):
                return True
        return False

    def _has_orthogonal_same_color(
        self,
        board: Board,
        move: Move,
        cells: list[tuple[int, int]],
        player_id: int,
    ) -> bool:
        for dr, dc in cells:
            row, col = move.row + dr, move.col + dc
            if board.has_orthogonal_neighbor(row, col, player_id):
                return True
        return False
