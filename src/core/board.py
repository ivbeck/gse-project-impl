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

    def in_bounds(self, row: int, col: int) -> bool:
        return (
            0 <= row < self.config.board_height and 0 <= col < self.config.board_width
        )

    def is_occupied(self, row: int, col: int) -> bool:
        if not self.in_bounds(row, col):
            return False
        return self.grid[row][col] is not None

    def get_owner(self, row: int, col: int) -> Optional[int]:
        if not self.in_bounds(row, col):
            return None
        return self.grid[row][col]

    def has_orthogonal_neighbor(self, row: int, col: int, player_id: int) -> bool:
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if self.in_bounds(nr, nc):
                if self.grid[nr][nc] == player_id:
                    return True
        return False

    def has_diagonal_neighbor(self, row: int, col: int, player_id: int) -> bool:
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nr, nc = row + dr, col + dc
            if self.in_bounds(nr, nc):
                if self.grid[nr][nc] == player_id:
                    return True
        return False

    def apply_move(self, move: Move, piece_cells: list[tuple[int, int]]) -> None:
        positions = [(move.row + dr, move.col + dc) for dr, dc in piece_cells]
        for row, col in positions:
            if not self.in_bounds(row, col):
                raise ValueError("move contains out-of-bounds cells")
            if self.is_occupied(row, col):
                raise ValueError("move overlaps an occupied cell")
        for dr, dc in piece_cells:
            row, col = move.row + dr, move.col + dc
            self.grid[row][col] = move.player_id
