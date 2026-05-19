import pytest
from io import StringIO
from adapters.cli import CLI
from core.types import GameStatus


def test_cli_render_board(capsys):
    cli = CLI()
    board = [[None] * 20 for _ in range(20)]
    board[0][0] = 0  # Blue at (0,0)
    cli.render_board(board)
    captured = capsys.readouterr()
    assert "B" in captured.out or "0" in captured.out


def test_cli_render_status(capsys):
    cli = CLI()
    cli.render_status(GameStatus.IN_PROGRESS)
    captured = capsys.readouterr()
    assert "IN_PROGRESS" in captured.out


def test_cli_prompt_replay(monkeypatch):
    cli = CLI()
    monkeypatch.setattr('builtins.input', lambda _: 'n')
    result = cli.prompt_replay()
    assert result == False