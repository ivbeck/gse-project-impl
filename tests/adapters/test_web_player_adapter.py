import threading
import time
from adapters.web_player_adapter import WebPlayerAdapter
from core.types import Move


def test_web_player_adapter_request_move_returns_none_when_no_response():
    adapter = WebPlayerAdapter()
    result = adapter.request_move(0, [])
    assert result is None


def test_submit_move_resolves_future():
    adapter = WebPlayerAdapter()
    move = Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=0)

    def submit_after_delay():
        time.sleep(0.05)
        adapter.submit_move(move)

    thread = threading.Thread(target=submit_after_delay)
    thread.start()
    result = adapter.request_move(0, [move])
    thread.join()
    assert result == move


def test_request_move_times_out():
    adapter = WebPlayerAdapter()
    move = Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=0)

    result = adapter.request_move(0, [move])
    assert result is None
