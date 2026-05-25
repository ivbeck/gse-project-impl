import pytest
from core.rule_set import RuleSet
from core.types import ConfigVO, Position, Move, MoveResult
from core.board import Board
from core.piece_catalog import PieceCatalog


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
        },
    )


@pytest.fixture
def board(config):
    return Board(config)


@pytest.fixture
def catalog():
    return PieceCatalog()


@pytest.fixture
def ruleset(catalog, config):
    return RuleSet(catalog, config)


def test_first_move_corner_check_blue(config, board, catalog, ruleset):
    move = Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=0)
    cells = [(0, 0)]
    result = ruleset.check_legality(board, move, is_first_move=True, cells=cells)
    assert result == MoveResult.LEGAL


def test_first_move_corner_check_wrong_corner(config, board, catalog, ruleset):
    board.grid[0][0] = 1
    move = Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=1)
    cells = [(0, 0)]
    result = ruleset.check_legality(board, move, is_first_move=True, cells=cells)
    assert result == MoveResult.ILLEGAL


def test_corner_touch_required(config, board, catalog, ruleset):
    board.grid[0][0] = 0
    move = Move(player_id=0, piece_id=1, orientation_index=0, row=0, col=2)
    cells = [(0, 0), (0, 1)]
    result = ruleset.check_legality(board, move, is_first_move=False, cells=cells)
    assert result == MoveResult.ILLEGAL


def test_corner_touch_diagonal_is_valid(config, board, catalog, ruleset):
    board.grid[0][0] = 0
    move = Move(player_id=0, piece_id=1, orientation_index=0, row=1, col=1)
    cells = [(0, 0), (0, 1)]
    result = ruleset.check_legality(board, move, is_first_move=False, cells=cells)
    assert result == MoveResult.LEGAL


def test_orthogonal_prohibition_same_color(config, board, catalog, ruleset):
    board.grid[0][0] = 0
    board.grid[0][1] = 0
    move = Move(player_id=0, piece_id=1, orientation_index=0, row=0, col=2)
    cells = [(0, 0), (0, 1)]
    result = ruleset.check_legality(board, move, is_first_move=False, cells=cells)
    assert result == MoveResult.ILLEGAL


def test_out_of_bounds_move_is_illegal(config, board, catalog, ruleset):
    move = Move(player_id=0, piece_id=1, orientation_index=0, row=0, col=19)
    cells = [(0, 0), (0, 1)]
    result = ruleset.check_legality(board, move, is_first_move=True, cells=cells)
    assert result == MoveResult.ILLEGAL


def test_overlapping_move_is_illegal(config, board, catalog, ruleset):
    board.grid[0][0] = 1
    move = Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=0)
    cells = [(0, 0)]
    result = ruleset.check_legality(board, move, is_first_move=True, cells=cells)
    assert result == MoveResult.ILLEGAL


def test_different_color_contact_allowed(config, board, catalog, ruleset):
    board.grid[0][0] = 0
    board.grid[1][0] = 1
    move = Move(player_id=0, piece_id=1, orientation_index=0, row=1, col=1)
    cells = [(0, 0), (0, 1)]
    result = ruleset.check_legality(board, move, is_first_move=False, cells=cells)
    assert result == MoveResult.LEGAL


def test_is_corner_position(config, ruleset):
    assert ruleset.is_corner_position(Position(0, 0), config)
    assert ruleset.is_corner_position(Position(0, 19), config)
    assert ruleset.is_corner_position(Position(19, 19), config)
    assert ruleset.is_corner_position(Position(19, 0), config)
    assert not ruleset.is_corner_position(Position(5, 5), config)
