from __future__ import annotations
from typing import Protocol, runtime_checkable, TYPE_CHECKING
from core.types import ConfigVO, GameStatus, Move, MoveResult, PlayerScore

if TYPE_CHECKING:
    from core.memento import Memento
    from core.board import Board


@runtime_checkable
class GameSession(Protocol):
    def submit_move(self, move: Move) -> MoveResult:
        ...
    def submit_pass(self) -> None:
        ...
    def advance_turn(self) -> None:
        ...
    def detect_termination(self) -> GameStatus:
        ...
    def final_scores(self) -> list[PlayerScore]:
        ...


@runtime_checkable
class MoveValidator(Protocol):
    def check_legality(
        self,
        board: Board,
        move: Move,
        is_first_move: bool,
        cells: list[tuple[int, int]],
    ) -> MoveResult:
        ...


@runtime_checkable
class LegalMoveEnumerator(Protocol):
    def find_moves(
        self,
        board: Board,
        player_id: int,
        remaining_piece_ids: list[int],
        is_first_move: bool = False,
    ) -> list[Move]:
        ...


@runtime_checkable
class PlayerInput(Protocol):
    def request_move(self, player_id: int, legal_moves: list[Move]) -> Move | None:
        ...


@runtime_checkable
class StateRepository(Protocol):
    def save(self, memento: Memento) -> str:
        ...
    def restore(self, data: str) -> Memento:
        ...


@runtime_checkable
class ConfigSource(Protocol):
    def load_config(self) -> ConfigVO:
        ...


@runtime_checkable
class PresentationOutput(Protocol):
    def render_board(self, board: Board) -> None:
        ...
    def render_status(self, status: GameStatus) -> None:
        ...
    def prompt_replay(self) -> bool:
        ...
