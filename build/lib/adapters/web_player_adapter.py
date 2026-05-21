from __future__ import annotations
import asyncio
import threading
from typing import TYPE_CHECKING
from core.ports import PlayerInput
from core.types import Move

if TYPE_CHECKING:
    from core.game_session import GameSession


class WebPlayerAdapter(PlayerInput):
    def __init__(self) -> None:
        self._move_future: asyncio.Future[Move | None] | None = None
        self._event_loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None

    def request_move(self, player_id: int, legal_moves: list[Move]) -> Move | None:
        if not legal_moves:
            return None
        self._event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._event_loop)
        self._move_future = self._event_loop.create_future()

        def run_loop():
            self._event_loop.run_until_complete(self._move_future)

        self._thread = threading.Thread(target=run_loop)
        self._thread.start()
        self._thread.join(timeout=5)

        if self._thread.is_alive():
            if self._event_loop and self._move_future:
                self._event_loop.call_soon_threadsafe(self._move_future.cancel)
            self._event_loop = None
            return None
        else:
            result = self._move_future.result() if self._move_future else None
            self._event_loop.close()
            self._event_loop = None
            return result

    def submit_move(self, move: Move | None) -> None:
        if self._event_loop and self._move_future and not self._move_future.done():
            self._event_loop.call_soon_threadsafe(self._move_future.set_result, move)