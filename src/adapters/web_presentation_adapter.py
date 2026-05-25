from __future__ import annotations
from typing import TYPE_CHECKING
from core.ports import PresentationOutput
from core.types import GameStatus

if TYPE_CHECKING:
    from core.game_session import GameSession


class WebPresentationAdapter(PresentationOutput):
    def __init__(self, session: GameSession | None) -> None:
        self._last_board = None
        self._last_status: GameStatus | None = None
        self._session = session

    def render_board(self, board) -> None:
        self._last_board = board

    def render_status(self, status: GameStatus) -> None:
        self._last_status = status

    def prompt_replay(self) -> bool:
        return False

    def get_last_board(self):
        return self._last_board

    def get_last_status(self):
        return self._last_status
