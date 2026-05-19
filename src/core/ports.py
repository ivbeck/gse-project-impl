from __future__ import annotations
from typing import Protocol, runtime_checkable, TYPE_CHECKING
from core.types import ConfigVO, Move, GameStatus

if TYPE_CHECKING:
    from core.memento import Memento
    from core.board import Board


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