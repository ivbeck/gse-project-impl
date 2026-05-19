import pytest
from core.board import Board
from core.types import ConfigVO, Position


@pytest.fixture
def config():
    return ConfigVO(
        board_width=20,
        board_height=20,
        player_count=4,
        starting_positions={
            0: Position(0, 0),
            1: Position(0, 19),
            2: Position(19, 19),
            3: Position(19, 0),
        }
    )


def test_board_initializes_with_empty_grid(config):
    board = Board(config)
    for row in range(config.board_height):
        for col in range(config.board_width):
            assert not board.is_occupied(row, col)
            assert board.get_owner(row, col) is None


def test_board_is_occupied(config):
    board = Board(config)
    assert not board.is_occupied(0, 0)
    board.grid[0][0] = 0
    assert board.is_occupied(0, 0)


def test_board_get_owner(config):
    board = Board(config)
    assert board.get_owner(0, 0) is None
    board.grid[0][0] = 0
    assert board.get_owner(0, 0) == 0


def test_board_has_orthogonal_neighbor(config):
    board = Board(config)
    assert not board.has_orthogonal_neighbor(1, 1, 0)
    board.grid[0][1] = 0
    assert board.has_orthogonal_neighbor(1, 1, 0)
    board.grid[1][0] = 0
    assert board.has_orthogonal_neighbor(1, 1, 0)


def test_board_has_diagonal_neighbor(config):
    board = Board(config)
    assert not board.has_diagonal_neighbor(1, 1, 0)
    board.grid[0][0] = 0
    assert board.has_diagonal_neighbor(1, 1, 0)


def test_board_apply_move(config):
    from core.types import Move
    board = Board(config)
    move = Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=0)
    board.apply_move(move, [(0, 0)])
    assert board.is_occupied(0, 0)
    assert board.get_owner(0, 0) == 0


def test_board_equality(config):
    board1 = Board(config)
    board2 = Board(config)
    assert board1 == board2
    board1.grid[0][0] = 0
    assert board1 != board2


def test_is_occupied_out_of_bounds(config):
    board = Board(config)
    assert board.is_occupied(-1, 0) is False
    assert board.is_occupied(0, -1) is False
    assert board.is_occupied(20, 0) is False
    assert board.is_occupied(0, 20) is False


def test_get_owner_out_of_bounds(config):
    board = Board(config)
    assert board.get_owner(-1, 0) is None
    assert board.get_owner(0, -1) is None
    assert board.get_owner(20, 0) is None
    assert board.get_owner(0, 20) is None