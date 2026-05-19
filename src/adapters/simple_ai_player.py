from core.ports import PlayerInput
from core.types import Move
from core.board import Board
from core.piece_catalog import PieceCatalog


class SimpleAiPlayer(PlayerInput):
    def __init__(self, catalog: PieceCatalog | None = None, board: Board | None = None):
        self.catalog = catalog
        self.board = board

    def request_move(self, player_id: int, legal_moves: list[Move]) -> Move | None:
        if not legal_moves:
            return None
        ranked_moves = sorted(
            legal_moves,
            key=lambda m: (
                -self._coverage(m),
                -self._future_corner_points(player_id, m),
                m.row,
                m.col,
                m.piece_id,
                m.orientation_index,
            )
        )
        return ranked_moves[0]

    def _coverage(self, move: Move) -> int:
        if self.catalog is None:
            return 0
        return len(self.catalog.get_orientations(move.piece_id)[move.orientation_index])

    def _future_corner_points(self, player_id: int, move: Move) -> int:
        if self.catalog is None or self.board is None:
            return 0
        orientation = self.catalog.get_orientations(move.piece_id)[move.orientation_index]
        placed_cells = {(move.row + dr, move.col + dc) for dr, dc in orientation}
        corner_points: set[tuple[int, int]] = set()
        for row, col in placed_cells:
            for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                anchor = (row + dr, col + dc)
                if self._is_new_corner_point(player_id, anchor, placed_cells):
                    corner_points.add(anchor)
        return len(corner_points)

    def _is_new_corner_point(
        self,
        player_id: int,
        anchor: tuple[int, int],
        placed_cells: set[tuple[int, int]],
    ) -> bool:
        if self.board is None:
            return False
        row, col = anchor
        if not self.board.in_bounds(row, col):
            return False
        if anchor in placed_cells or self.board.is_occupied(row, col):
            return False
        if self.board.has_diagonal_neighbor(row, col, player_id):
            return False
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (row + dr, col + dc)
            if neighbor in placed_cells:
                return False
            if self.board.get_owner(*neighbor) == player_id:
                return False
        return True
