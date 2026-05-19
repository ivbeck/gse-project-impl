import asyncio
import pytest
from adapters.web_player_adapter import WebPlayerAdapter
from core.types import Move


def test_web_player_adapter_request_move_returns_none_when_no_response():
    adapter = WebPlayerAdapter()
    result = asyncio.run(adapter.request_move(0, []))
    assert result is None


def test_submit_move_resolves_future():
    adapter = WebPlayerAdapter()
    move = Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=0)

    async def submit_and_request():
        async def submit_after_delay():
            await asyncio.sleep(0.05)
            adapter.submit_move(move)

        submit_task = asyncio.create_task(submit_after_delay())
        result = await adapter.request_move(0, [move])
        return result

    result = asyncio.run(submit_and_request())
    assert result == move


def test_request_move_times_out():
    adapter = WebPlayerAdapter()
    move = Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=0)

    async def request_with_short_timeout():
        async def never_submit():
            await asyncio.sleep(10)

        submit_task = asyncio.create_task(never_submit())
        try:
            result = await asyncio.wait_for(adapter.request_move(0, [move]), timeout=0.1)
        except asyncio.TimeoutError:
            result = None
        submit_task.cancel()
        try:
            await submit_task
        except asyncio.CancelledError:
            pass
        return result

    result = asyncio.run(request_with_short_timeout())
    assert result is None