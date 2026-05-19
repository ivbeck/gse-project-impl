from dataclasses import dataclass
from typing import Optional
from core.types import ConfigVO, Move


@dataclass
class Board:
    config: ConfigVO
    grid: list[list[Optional[int]]]

    def __init__(self, config: ConfigVO):
        self.config = config
        self.grid = [[None] * config.board_width for _ in range(config.board_height)]

    def is_occupied(self, row: int, col: int) -> bool:
        return self.grid[row][col] is not None

    def get_owner(self, row: int, col: int) -> Optional[int]:
        return self.grid[row][col]

    def has_orthogonal_neighbor(self, row: int, col: int, player_id: int) -> bool:
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.config.board_height and 0 <= nc < self.config.board_width:
                if self.grid[nr][nc] == player_id:
                    return True
        return False

    def has_diagonal_neighbor(self, row: int, col: int, player_id: int) -> bool:
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.config.board_height and 0 <= nc < self.config.board_width:
                if self.grid[nr][nc] == player_id:
                    return True
        return False

    def apply_move(self, move: Move, piece_cells: list[tuple[int, int]]) -> None:
        for dr, dc in piece_cells:
            row, col = move.row + dr, move.col + dc
            if 0 <= row < self.config.board_height and 0 <= col < self.config.board_width:
                self.grid[row][col] = move.player_id