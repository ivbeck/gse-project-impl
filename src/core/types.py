from dataclasses import dataclass
from typing import Final

BOARD_WIDTH: Final[int] = 20
BOARD_HEIGHT: Final[int] = 20
PLAYER_COUNT: Final[int] = 4


@dataclass(frozen=True)
class Position:
    row: int
    col: int


@dataclass(frozen=True)
class Piece:
    piece_id: int
    shape: tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class Move:
    player_id: int
    piece_id: int
    orientation_index: int
    row: int
    col: int


class MoveResult:
    LEGAL = "LEGAL"
    ILLEGAL = "ILLEGAL"


class GameStatus:
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"


@dataclass(frozen=True)
class PlayerScore:
    player_id: int
    score: int
    is_winner: bool


@dataclass(frozen=True)
class ConfigVO:
    board_width: int
    board_height: int
    player_count: int
    starting_positions: dict[int, Position]