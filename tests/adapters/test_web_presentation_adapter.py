from adapters.web_presentation_adapter import WebPresentationAdapter
from core.types import GameStatus

def test_web_presentation_adapter_render_board_stores_state():
    adapter = WebPresentationAdapter(None)
    board = [[None]*20 for _ in range(20)]
    adapter.render_board(board)
    assert adapter.get_last_board() == board

def test_web_presentation_adapter_render_status_stores_status():
    adapter = WebPresentationAdapter(None)
    adapter.render_status(GameStatus.IN_PROGRESS)
    assert adapter.get_last_status() == GameStatus.IN_PROGRESS

def test_web_presentation_adapter_render_board_with_pieces():
    adapter = WebPresentationAdapter(None)
    board = [[None]*20 for _ in range(20)]
    board[0][0] = 0
    board[0][1] = 0
    adapter.render_board(board)
    last = adapter.get_last_board()
    assert last[0][0] == 0
    assert last[0][1] == 0