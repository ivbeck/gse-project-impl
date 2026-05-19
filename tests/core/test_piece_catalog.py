import pytest
from core.piece_catalog import PieceCatalog


def test_piece_catalog_has_21_pieces():
    catalog = PieceCatalog()
    assert len(catalog.get_all_pieces()) == 21


def test_piece_catalog_piece_ids_range_0_to_20():
    catalog = PieceCatalog()
    ids = {p.piece_id for p in catalog.get_all_pieces()}
    assert ids == set(range(21))


def test_piece_catalog_get_by_id():
    catalog = PieceCatalog()
    piece = catalog.get_by_id(0)
    assert piece.piece_id == 0


def test_piece_catalog_all_pieces_have_shape():
    catalog = PieceCatalog()
    for piece in catalog.get_all_pieces():
        assert len(piece.shape) > 0
        for row in piece.shape:
            assert len(row) > 0


def test_piece_catalog_monomino_is_1_square():
    catalog = PieceCatalog()
    monomino = catalog.get_by_id(0)
    assert len(monomino.shape) == 1
    assert len(monomino.shape[0]) == 1


def test_piece_catalog_domino_is_2_squares():
    catalog = PieceCatalog()
    domino = catalog.get_by_id(1)
    squares = sum(cell for row in domino.shape for cell in row)
    assert squares == 2


def test_piece_catalog_all_pentominoes_have_5_squares():
    catalog = PieceCatalog()
    for piece_id in range(9, 21):
        piece = catalog.get_by_id(piece_id)
        squares = sum(cell for row in piece.shape for cell in row)
        assert squares == 5, f"Piece {piece_id} has {squares} squares, expected 5"


def test_piece_catalog_all_orientations_for_each_piece():
    catalog = PieceCatalog()
    for piece in catalog.get_all_pieces():
        orientations = catalog.get_orientations(piece.piece_id)
        assert len(orientations) > 0, f"Piece {piece.piece_id} has no orientations"
        for orientation in orientations:
            assert len(orientation) > 0


def test_piece_catalog_orientation_covers_valid_positions():
    catalog = PieceCatalog()
    for piece in catalog.get_all_pieces():
        for orientation in catalog.get_orientations(piece.piece_id):
            min_row = min(r for r, _ in orientation)
            min_col = min(c for _, c in orientation)
            assert min_row >= 0
            assert min_col >= 0