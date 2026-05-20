from adapters.cli import CLI
from core.types import GameStatus


def test_cli_render_board(capsys):
    cli = CLI()
    board = [[None] * 20 for _ in range(20)]
    board[0][0] = 0  # Blue at (0,0)
    cli.render_board(board)
    captured = capsys.readouterr()
    assert "B" in captured.out or "0" in captured.out


def test_cli_render_board_aligns_rectangular_board_labels(capsys):
    cli = CLI()
    board = [[None] * 12 for _ in range(3)]
    board[0][0] = 0
    board[1][10] = 2
    board[2][11] = 3

    cli.render_board(board)

    assert capsys.readouterr().out.splitlines() == [
        "    0  1  2  3  4  5  6  7  8  9 10 11 ",
        " 0  B  .  .  .  .  .  .  .  .  .  .  . ",
        " 1  .  .  .  .  .  .  .  .  .  .  R  . ",
        " 2  .  .  .  .  .  .  .  .  .  .  .  G ",
    ]


def test_cli_render_board_aligns_double_digit_row_labels(capsys):
    cli = CLI()
    board = [[None] * 3 for _ in range(12)]
    board[10][2] = 1

    cli.render_board(board)

    lines = capsys.readouterr().out.splitlines()

    assert lines[0] == "    0  1  2 "
    assert lines[10] == " 9  .  .  . "
    assert lines[11] == "10  .  .  Y "
    assert len(lines[10]) == len(lines[11])


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
