from __future__ import annotations
from dataclasses import dataclass


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
    scoring_rule: str = "classic"


class ConfigBuilder:
    def __init__(self) -> None:
        self._board_width: int | None = None
        self._board_height: int | None = None
        self._player_count: int | None = None
        self._starting_positions: dict[int, Position] = {}
        self._scoring_rule: str = "classic"

    def with_board_dimensions(self, width: int, height: int) -> ConfigBuilder:
        self._board_width = width
        self._board_height = height
        return self

    def with_player_count(self, player_count: int) -> ConfigBuilder:
        self._player_count = player_count
        return self

    def with_starting_positions(self, positions: dict[int, Position]) -> ConfigBuilder:
        self._starting_positions = dict(positions)
        return self

    def with_scoring_rule(self, scoring_rule: str) -> ConfigBuilder:
        self._scoring_rule = scoring_rule
        return self

    def build(self) -> ConfigVO:
        if self._board_width is None or self._board_height is None:
            raise ValueError("board dimensions are required")
        if self._player_count is None:
            raise ValueError("player count is required")
        if self._board_width <= 0 or self._board_height <= 0:
            raise ValueError("board dimensions must be positive")
        if self._player_count <= 0:
            raise ValueError("player count must be positive")
        if set(self._starting_positions) != set(range(self._player_count)):
            raise ValueError("starting positions must cover every player")
        for position in self._starting_positions.values():
            if not (
                0 <= position.row < self._board_height
                and 0 <= position.col < self._board_width
            ):
                raise ValueError("starting positions must be on the board")
        if self._scoring_rule not in {"classic", "duo"}:
            raise ValueError("scoring_rule must be 'classic' or 'duo'")
        return ConfigVO(
            board_width=self._board_width,
            board_height=self._board_height,
            player_count=self._player_count,
            starting_positions=dict(self._starting_positions),
            scoring_rule=self._scoring_rule,
        )
