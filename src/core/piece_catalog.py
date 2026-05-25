from core.types import Piece


_PIECE_DEFINITIONS: list[list[list[str]]] = [
    [["1"]],
    [["1", "1"]],
    [["1", "1", "1"]],
    [["1", "0"], ["1", "1"]],
    [["1", "1", "1", "1"]],
    [["1", "1"], ["1", "1"]],
    [["1", "1", "1"], ["0", "1", "0"]],
    [["1", "0", "0"], ["1", "1", "1"]],
    [["1", "1", "0"], ["0", "1", "1"]],
    [["1", "0", "1"], ["1", "1", "1"]],
    [["1", "1", "1", "1", "1"]],
    [["1", "1"], ["1", "1"], ["1", "0"]],
    [["0", "1", "1", "1"], ["1", "1", "0", "0"]],
    [["0", "1", "1"], ["1", "1", "0"], ["0", "1", "0"]],
    [["1", "0", "0"], ["1", "1", "0"], ["0", "1", "1"]],
    [["1", "1", "1"], ["0", "1", "0"], ["0", "1", "0"]],
    [["1", "1", "0"], ["0", "1", "0"], ["0", "1", "1"]],
    [["0", "1", "0"], ["1", "1", "1"], ["0", "1", "0"]],
    [["0", "0", "1", "0"], ["1", "1", "1", "1"]],
    [["1", "0", "0", "0"], ["1", "1", "1", "1"]],
    [["1", "0", "0"], ["1", "0", "0"], ["1", "1", "1"]],
]


def _grid_to_coords(grid: list[list[int]]) -> list[tuple[int, int]]:
    coords = []
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val:
                coords.append((r, c))
    return coords


def _rotate_90(grid: list[list[int]]) -> list[list[int]]:
    rows = len(grid)
    cols = len(grid[0])
    result = [[0] * rows for _ in range(cols)]
    for r in range(rows):
        for c in range(cols):
            result[c][rows - 1 - r] = grid[r][c]
    return result


def _reflect_h(grid: list[list[int]]) -> list[list[int]]:
    return [row[::-1] for row in grid]


def _normalize_coords(coords: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not coords:
        return []
    min_r = min(r for r, _ in coords)
    min_c = min(c for _, c in coords)
    return sorted((r - min_r, c - min_c) for r, c in coords)


def _generate_orientations(grid: list[list[int]]) -> list[list[tuple[int, int]]]:
    orientations: set[tuple[tuple[int, int], ...]] = set()
    current = grid
    num_rotations = len(grid[0]) + len(grid) if grid else 1
    for _ in range(num_rotations):
        current = _rotate_90(current)
        orientations.add(tuple(_normalize_coords(_grid_to_coords(current))))
        orientations.add(tuple(_normalize_coords(_grid_to_coords(_reflect_h(current)))))
    return [list(orient) for orient in sorted(orientations)]


class PieceCatalog:
    _pieces: list[Piece]
    _orientations: list[list[list[tuple[int, int]]]]

    def __init__(self) -> None:
        self._pieces = []
        self._orientations = []
        for piece_id, grid_strs in enumerate(_PIECE_DEFINITIONS):
            grid = [[1 if c == "1" else 0 for c in row] for row in grid_strs]
            self._pieces.append(
                Piece(piece_id=piece_id, shape=tuple(tuple(row) for row in grid))
            )
            self._orientations.append(_generate_orientations(grid))

    def get_all_pieces(self) -> list[Piece]:
        return list(self._pieces)

    def get_by_id(self, piece_id: int) -> Piece:
        return self._pieces[piece_id]

    def get_orientations(self, piece_id: int) -> list[list[tuple[int, int]]]:
        return list(self._orientations[piece_id])
