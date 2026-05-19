from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING
from core.ports import PlayerInput
from core.types import Move

if TYPE_CHECKING:
    from core.game_session import GameSession

class WebPlayerAdapter(PlayerInput):
    def __init__(self) -> None:
        self._move_future: asyncio.Future[Move | None] | None = None

    def request_move(self, player_id: int, legal_moves: list[Move]) -> Move | None:
        if not legal_moves:
            return None
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
        self._move_future = loop.create_future()
        async def wait_for_move() -> Move | None:
            try:
                return await asyncio.wait_for(self._move_future, timeout=300)
            except asyncio.TimeoutError:
                return None
        return wait_for_move().__await__()

    def submit_move(self, move: Move | None) -> None:
        if self._move_future and not self._move_future.done():
            self._move_future.set_result(move)