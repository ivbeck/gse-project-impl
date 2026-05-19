# Blokus Game Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a complete, production-quality Blokus Classic game engine (4 players) with CLI, JSON state persistence, and Simple AI players, following hexagonal architecture.

**Architecture:** Hexagonal (Ports & Adapters) with Strategy (PlayerInput), Command (Move), Builder (ConfigVO), and Memento patterns. Core game logic isolated from I/O.

**Tech Stack:** Python with `uv` for package management, `@dataclass(frozen=True)` for value objects, `typing.Protocol` for ports.

---

## File Structure

```
src/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── types.py          # Position, Piece, Move, MoveResult, GameStatus, PlayerScore, ConfigVO
│   ├── board.py          # Board class
│   ├── piece_catalog.py  # PieceCatalog with all 21 pieces and orientations
│   ├── rule_set.py       # RuleSet with legality checks
│   ├── scoring.py        # Scoring class
│   ├── game_session.py    # GameSession orchestrator
│   └── ports.py          # Port interfaces (Protocol classes)
├── adapters/
│   ├── __init__.py
│   ├── cli.py            # CLI adapter (PresentationOutput)
│   ├── json_state_repo.py # JsonStateRepo adapter (StateRepository)
│   ├── json_config_source.py # JsonConfigSource adapter (ConfigSource)
│   ├── human_player.py   # HumanPlayer adapter (PlayerInput)
│   └── simple_ai_player.py # SimpleAiPlayer adapter (PlayerInput)
├── bootstrap.py          # Procedural wiring (≤~200 lines)
└── app.py                # Module entry point
tests/
├── __init__.py
├── conftest.py           # Shared fixtures
├── core/
│   ├── __init__.py
│   ├── test_board.py
│   ├── test_piece_catalog.py
│   ├── test_rule_set.py
│   ├── test_scoring.py
│   └── test_game_session.py
└── adapters/
    ├── __init__.py
    ├── test_human_player.py
    └── test_simple_ai_player.py
pyproject.toml
```

---

## Task 1: Project Setup & Value Types

**Goal:** Initialize the project structure with `pyproject.toml` and define core value types.

**Files:**
- Create: `pyproject.toml`
- Create: `src/__init__.py`, `src/core/__init__.py`, `src/adapters/__init__.py`
- Create: `src/core/types.py`
- Create: `tests/__init__.py`, `tests/conftest.py`, `tests/core/__init__.py`, `tests/adapters/__init__.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "blokus-engine"
version = "0.1.0"
description = "Configurable Blokus game engine"
requires-python = ">=3.12"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "ruff>=0.4",
    "mypy>=1.10",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
filterwarnings = ["error"]

[tool.ruff]
src = ["src"]

[tool.mypy]
src = ["src"]
```

- [ ] **Step 2: Run `uv sync` to set up environment**

Run: `cd /home/iven/coding/projects/gse-project-impl && uv sync`
Expected: Environment created with pytest, ruff, mypy

- [ ] **Step 3: Write failing test for ConfigVO literals tripwire (DR-1)**

```python
# tests/core/test_config_vo_literals.py
def test_no_hardcoded_board_size_20():
    """Tripwire: fails if literal 20 appears in Core.*"""
    import pathlib, re
    core_path = pathlib.Path("src/core")
    for f in core_path.rglob("*.py"):
        content = f.read_text()
        matches = re.findall(r'\b20\b', content)
        if matches:
            raise AssertionError(f"{f}: found hardcoded '20': {matches}")

def test_no_hardcoded_player_count_4():
    """Tripwire: fails if literal 4 appears in Core.* (as player count)"""
    import pathlib, re
    core_path = pathlib.Path("src/core")
    for f in core_path.rglob("*.py"):
        content = f.read_text()
        matches = re.findall(r'\b4\b', content)
        if matches:
            raise AssertionError(f"{f}: found hardcoded '4': {matches}")
```

- [ ] **Step 4: Implement minimal types.py**

```python
# src/core/types.py
from dataclasses import dataclass
from typing import Final

BOARD_WIDTH: Final[int] = 20  # Only here, in types
BOARD_HEIGHT: Final[int] = 20
PLAYER_COUNT: Final[int] = 4

@dataclass(frozen=True)
class Position:
    row: int
    col: int

@dataclass(frozen=True)
class Piece:
    piece_id: int
    shape: tuple[tuple[int, ...], ...]

@dataclass(frozen=True)
class Move:
    player_id: int
    piece_id: int
    orientation_index: int
    row: int
    col: int

class MoveResult:
    LEGAL = "LEGAL"
    ILLEGAL = "ILLEGAL"

class GameStatus:
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"

@dataclass(frozen=True)
class PlayerScore:
    player_id: int
    score: int
    is_winner: bool

@dataclass(frozen=True)
class ConfigVO:
    board_width: int
    board_height: int
    player_count: int
    starting_positions: dict[int, Position]
```

- [ ] **Step 5: Verify tests pass**

Run: `uv run pytest tests/core/test_config_vo_literals.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml src/core/types.py tests/
git commit -m "feat: project setup and core value types"
```

---

## Task 2: PieceCatalog — All 21 Pieces

**Goal:** Implement PieceCatalog with all 21 Blokus pieces (1 monomino, 1 domino, 2 trominoes, 5 tetrominoes, 12 pentominoes) and precomputed orientations.

**Files:**
- Create: `src/core/piece_catalog.py`
- Create: `tests/core/test_piece_catalog.py`

- [ ] **Step 1: Write failing test for PieceCatalog**

```python
# tests/core/test_piece_catalog.py
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
    squares = sum(len(row) for row in domino.shape)
    assert squares == 2

def test_piece_catalog_all_pentominoes_have_5_squares():
    catalog = PieceCatalog()
    for piece_id in range(5, 17):  # pentominoes are IDs 5-16
        piece = catalog.get_by_id(piece_id)
        squares = sum(len(row) for row in piece.shape)
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/core/test_piece_catalog.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement PieceCatalog with all 21 pieces**

The 21 Blokus pieces (IDs 0-20):
- ID 0: monomino (1 square)
- ID 1: domino (2 squares, 2 orientations)
- IDs 2-3: trominoes (3 squares, 4 orientations each)
- IDs 4-8: tetrominoes (4 squares, 8 orientations each for I, O, T, L, J)
- IDs 9-20: pentominoes (5 squares, 8 orientations each)

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/core/test_piece_catalog.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/core/piece_catalog.py tests/core/test_piece_catalog.py
git commit -m "feat: implement PieceCatalog with all 21 pieces and orientations"
```

---

## Task 3: Board Class

**Goal:** Implement Board with grid, occupancy checks, and move application.

**Files:**
- Create: `src/core/board.py`
- Create: `tests/core/test_board.py`

- [ ] **Step 1: Write failing tests for Board**

```python
# tests/core/test_board.py
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
    board.apply_move(move, {0: [(0, 0)]})
    assert board.is_occupied(0, 0)
    assert board.get_owner(0, 0) == 0

def test_board_equality(config):
    board1 = Board(config)
    board2 = Board(config)
    assert board1 == board2
    board1.grid[0][0] = 0
    assert board1 != board2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/core/test_board.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement minimal Board**

```python
# src/core/board.py
from dataclasses import dataclass
from typing import Optional
from core.types import ConfigVO, Move

@dataclass
class Board:
    config: ConfigVO
    grid: list[list[Optional[int]]]

    def __init__(self, config: ConfigVO):
        self.config = config
        self.grid = [[None] * config.board_width for _ in range(config.board_height)]

    def is_occupied(self, row: int, col: int) -> bool:
        return self.grid[row][col] is not None

    def get_owner(self, row: int, col: int) -> Optional[int]:
        return self.grid[row][col]

    def has_orthogonal_neighbor(self, row: int, col: int, player_id: int) -> bool:
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.config.board_height and 0 <= nc < self.config.board_width:
                if self.grid[nr][nc] == player_id:
                    return True
        return False

    def has_diagonal_neighbor(self, row: int, col: int, player_id: int) -> bool:
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.config.board_height and 0 <= nc < self.config.board_width:
                if self.grid[nr][nc] == player_id:
                    return True
        return False

    def apply_move(self, move: Move, piece_cells: list[tuple[int, int]]) -> None:
        for dr, dc in piece_cells:
            row, col = move.row + dr, move.col + dc
            if 0 <= row < self.config.board_height and 0 <= col < self.config.board_width:
                self.grid[row][col] = move.player_id
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/core/test_board.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/core/board.py tests/core/test_board.py
git commit -m "feat: implement Board with occupancy and neighbor checks"
```

---

## Task 4: RuleSet — Legality Checking

**Goal:** Implement RuleSet with corner-touch check, ortho-prohibition, first-move corner enforcement.

**Files:**
- Create: `src/core/rule_set.py`
- Create: `tests/core/test_rule_set.py`

- [ ] **Step 1: Write failing tests for RuleSet**

```python
# tests/core/test_rule_set.py
import pytest
from core.rule_set import RuleSet
from core.types import ConfigVO, Position, Move
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
        }
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

def test_different_color_contact_allowed(config, board, catalog, ruleset):
    board.grid[0][0] = 1
    move = Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=1)
    cells = [(0, 0)]
    result = ruleset.check_legality(board, move, is_first_move=False, cells=cells)
    assert result == MoveResult.LEGAL

def test_is_corner_position(config, ruleset):
    assert ruleset.is_corner_position(Position(0, 0), config)
    assert ruleset.is_corner_position(Position(0, 19), config)
    assert ruleset.is_corner_position(Position(19, 19), config)
    assert ruleset.is_corner_position(Position(19, 0), config)
    assert not ruleset.is_corner_position(Position(5, 5), config)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/core/test_rule_set.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement RuleSet**

```python
# src/core/rule_set.py
from core.types import ConfigVO, Move, MoveResult, Position
from core.board import Board
from core.piece_catalog import PieceCatalog

class RuleSet:
    def __init__(self, catalog: PieceCatalog, config: ConfigVO):
        self.catalog = catalog
        self.config = config

    def is_corner_position(self, pos: Position, config: ConfigVO) -> bool:
        return (pos.row, pos.col) in [
            (0, 0), (0, config.board_width - 1),
            (config.board_height - 1, 0),
            (config.board_height - 1, config.board_width - 1)
        ]

    def check_legality(
        self,
        board: Board,
        move: Move,
        is_first_move: bool,
        cells: list[tuple[int, int]]
    ) -> MoveResult:
        player_id = move.player_id
        if is_first_move:
            corner = self.config.starting_positions[player_id]
            covers_corner = any(
                move.row + dr == corner.row and move.col + dc == corner.col
                for dr, dc in cells
            )
            if not covers_corner:
                return MoveResult.ILLEGAL
        else:
            if not self._touches_corner_diagonally(board, move, cells, player_id):
                return MoveResult.ILLEGAL
        if self._has_orthogonal_same_color(board, move, cells, player_id):
            return MoveResult.ILLEGAL
        return MoveResult.LEGAL

    def _touches_corner_diagonally(
        self,
        board: Board,
        move: Move,
        cells: list[tuple[int, int]],
        player_id: int
    ) -> bool:
        for dr, dc in cells:
            row, col = move.row + dr, move.col + dc
            if board.has_diagonal_neighbor(row, col, player_id):
                return True
        return False

    def _has_orthogonal_same_color(
        self,
        board: Board,
        move: Move,
        cells: list[tuple[int, int]],
        player_id: int
    ) -> bool:
        for dr, dc in cells:
            row, col = move.row + dr, move.col + dc
            if board.has_orthogonal_neighbor(row, col, player_id):
                return True
        return False
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/core/test_rule_set.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/core/rule_set.py tests/core/test_rule_set.py
git commit -m "feat: implement RuleSet with legality checking"
```

---

## Task 5: Scoring Class

**Goal:** Implement Scoring to rank players by remaining squares.

**Files:**
- Create: `src/core/scoring.py`
- Create: `tests/core/test_scoring.py`

- [ ] **Step 1: Write failing tests for Scoring**

```python
# tests/core/test_scoring.py
import pytest
from core.scoring import Scoring
from core.piece_catalog import PieceCatalog

@pytest.fixture
def catalog():
    return PieceCatalog()

def test_scoring_all_remaining_pieces(catalog):
    scoring = Scoring(catalog)
    remaining = {0: list(range(21)), 1: list(range(21)), 2: list(range(21)), 3: list(range(21))}
    scores = scoring.rank(remaining)
    assert len(scores) == 4
    assert all(s.score == 89 for s in scores)
    assert all(not s.is_winner for s in scores)

def test_scoring_one_player_placed_all(catalog):
    scoring = Scoring(catalog)
    remaining = {0: [], 1: list(range(21)), 2: list(range(21)), 3: list(range(21))}
    scores = scoring.rank(remaining)
    p0_score = next(s for s in scores if s.player_id == 0)
    assert p0_score.score == 0
    assert p0_score.is_winner

def test_scoring_tie(catalog):
    scoring = Scoring(catalog)
    remaining = {0: [0], 1: [0], 2: [], 3: []}
    scores = scoring.rank(remaining)
    p0 = next(s for s in scores if s.player_id == 0)
    p1 = next(s for s in scores if s.player_id == 1)
    assert p0.score == p1.score
    assert p0.is_winner and p1.is_winner
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/core/test_scoring.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement Scoring**

```python
# src/core/scoring.py
from core.piece_catalog import PieceCatalog
from core.types import PlayerScore

class Scoring:
    def __init__(self, catalog: PieceCatalog):
        self.catalog = catalog

    def rank(self, remaining: dict[int, list[int]]) -> list[PlayerScore]:
        def piece_square_count(piece_id: int) -> int:
            piece = self.catalog.get_by_id(piece_id)
            return sum(len(row) for row in piece.shape)

        scores = []
        for player_id, piece_ids in remaining.items():
            total = sum(piece_square_count(pid) for pid in piece_ids)
            scores.append(PlayerScore(player_id=player_id, score=total, is_winner=False))

        min_score = min(s.score for s in scores)
        for s in scores:
            if s.score == min_score:
                s.is_winner = True

        return sorted(scores, key=lambda s: s.score)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/core/test_scoring.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/core/scoring.py tests/core/test_scoring.py
git commit -m "feat: implement Scoring with basic ranking"
```

---

## Task 6: GameSession

**Goal:** Implement GameSession orchestrator with turn management and termination detection.

**Files:**
- Create: `src/core/game_session.py`
- Create: `tests/core/test_game_session.py`

- [ ] **Step 1: Write failing tests for GameSession**

```python
# tests/core/test_game_session.py
import pytest
from core.game_session import GameSession
from core.types import ConfigVO, Position, Move, MoveResult
from core.piece_catalog import PieceCatalog
from core.rule_set import RuleSet
from core.scoring import Scoring

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

@pytest.fixture
def catalog():
    return PieceCatalog()

@pytest.fixture
def session(config, catalog):
    ruleset = RuleSet(catalog, config)
    scoring = Scoring(catalog)
    return GameSession(config, catalog, ruleset, scoring)

def test_game_session_initializes_with_player_0(session):
    assert session.current_player_id == 0

def test_game_session_submit_legal_move(session):
    move = Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=0)
    result = session.submit_move(move)
    assert result == MoveResult.LEGAL

def test_game_session_detect_termination_not_terminated(session):
    assert session.detect_termination() == GameStatus.IN_PROGRESS

def test_game_session_final_scores(session):
    scores = session.final_scores()
    assert len(scores) == 4
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/core/test_game_session.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement GameSession skeleton first, then add full logic**

```python
# src/core/game_session.py
from core.types import ConfigVO, Move, MoveResult, GameStatus, PlayerScore
from core.board import Board
from core.piece_catalog import PieceCatalog
from core.rule_set import RuleSet
from core.scoring import Scoring

class GameSession:
    def __init__(
        self,
        config: ConfigVO,
        catalog: PieceCatalog,
        ruleset: RuleSet,
        scoring: Scoring
    ):
        self.config = config
        self.catalog = catalog
        self.ruleset = ruleset
        self.scoring = scoring
        self.board = Board(config)
        self.current_player_id = 0
        self.consecutive_passes = 0
        self.remaining_pieces: dict[int, list[int]] = {
            i: list(range(21)) for i in range(config.player_count)
        }
        self._is_first_move: dict[int, bool] = {i: True for i in range(config.player_count)}

    def submit_move(self, move: Move) -> MoveResult:
        piece = self.catalog.get_by_id(move.piece_id)
        orientation = self.catalog.get_orientations(move.piece_id)[move.orientation_index]
        cells = [(r, c) for r, row in enumerate(orientation) for c, val in enumerate(row) if val]
        result = self.ruleset.check_legality(
            self.board, move, self._is_first_move[move.player_id], cells
        )
        if result == MoveResult.LEGAL:
            self.board.apply_move(move, cells)
            self.remaining_pieces[move.player_id].remove(move.piece_id)
            self._is_first_move[move.player_id] = False
            self.consecutive_passes = 0
        return result

    def advance_turn(self) -> None:
        self.current_player_id = (self.current_player_id + 1) % self.config.player_count

    def detect_termination(self) -> GameStatus:
        if all(not pieces for pieces in self.remaining_pieces.values()):
            return GameStatus.FINISHED
        if self.consecutive_passes >= self.config.player_count:
            return GameStatus.FINISHED
        return GameStatus.IN_PROGRESS

    def final_scores(self) -> list[PlayerScore]:
        return self.scoring.rank(self.remaining_pieces)

    def legal_moves_for_current(self) -> list[Move]:
        pass  # TODO: implement enumeration
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/core/test_game_session.py -v`
Expected: PASS (legal_moves_for_current is todo)

- [ ] **Step 5: Commit**

```bash
git add src/core/game_session.py tests/core/test_game_session.py
git commit -m "feat: implement GameSession with turn management"
```

---

## Task 7: Port Interfaces

**Goal:** Define all 6 port interfaces (Protocol classes) as specified in ADR-FINAL-P2.

**Files:**
- Create: `src/core/ports.py`

- [ ] **Step 1: Write tests for ports (interface conformance)**

```python
# tests/core/test_ports.py
import pytest
from typing import Protocol, runtime_checkable
from core.ports import PlayerInput, StateRepository, ConfigSource, PresentationOutput

def test_player_input_is_protocol():
    assert hasattr(PlayerInput, 'request_move')

def test_state_repository_is_protocol():
    assert hasattr(StateRepository, 'save')
    assert hasattr(StateRepository, 'restore')

def test_config_source_is_protocol():
    assert hasattr(ConfigSource, 'load_config')

def test_presentation_output_is_protocol():
    assert hasattr(PresentationOutput, 'render_board')
    assert hasattr(PresentationOutput, 'render_status')
    assert hasattr(PresentationOutput, 'prompt_replay')
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/core/test_ports.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement ports.py**

```python
# src/core/ports.py
from typing import Protocol
from core.types import ConfigVO, Move, GameStatus
from core.game_session import GameSession

@runtime_checkable
class PlayerInput(Protocol):
    def request_move(self, player_id: int, legal_moves: list[Move]) -> Move | None:
        ...

@runtime_checkable
class StateRepository(Protocol):
    def save(self, session: GameSession) -> str:
        ...
    def restore(self, data: str) -> GameSession:
        ...

@runtime_checkable
class ConfigSource(Protocol):
    def load_config(self) -> ConfigVO:
        ...

@runtime_checkable
class PresentationOutput(Protocol):
    def render_board(self, board) -> None:
        ...
    def render_status(self, status: GameStatus) -> None:
        ...
    def prompt_replay(self) -> bool:
        ...
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/core/test_ports.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/core/ports.py tests/core/test_ports.py
git commit -m "feat: define port interfaces (Protocol classes)"
```

---

## Task 8: Memento for State Snapshots

**Goal:** Implement Memento value object for JSON round-trip (FR-2.2, FR-2.6).

**Files:**
- Create: `src/core/memento.py`
- Create: `tests/core/test_memento.py`

- [ ] **Step 1: Write failing tests for Memento**

```python
# tests/core/test_memento.py
import pytest
from core.memento import Memento
from core.types import ConfigVO, Position
from core.game_session import GameSession
from core.piece_catalog import PieceCatalog
from core.rule_set import RuleSet
from core.scoring import Scoring

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

@pytest.fixture
def session(config):
    catalog = PieceCatalog()
    ruleset = RuleSet(catalog, config)
    scoring = Scoring(catalog)
    return GameSession(config, catalog, ruleset, scoring)

def test_memento_contains_config(session, config):
    m = Memento.from_session(session)
    assert m.config == config
    assert m.config.board_width == 20
    assert m.config.board_height == 20
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/core/test_memento.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement Memento**

```python
# src/core/memento.py
from dataclasses import dataclass
from core.types import ConfigVO
from core.game_session import GameSession

@dataclass(frozen=True)
class Memento:
    config: ConfigVO
    board_state: tuple[tuple[int | None, ...], ...]
    current_player_id: int
    remaining_pieces: dict[int, list[int]]
    consecutive_passes: int
    is_first_move: dict[int, bool]

    @classmethod
    def from_session(cls, session: GameSession) -> "Memento":
        board_state = tuple(
            tuple(cell for cell in row)
            for row in session.board.grid
        )
        return cls(
            config=session.config,
            board_state=board_state,
            current_player_id=session.current_player_id,
            remaining_pieces=session.remaining_pieces.copy(),
            consecutive_passes=session.consecutive_passes,
            is_first_move=session._is_first_move.copy(),
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/core/test_memento.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/core/memento.py tests/core/test_memento.py
git commit -m "feat: implement Memento for state snapshots"
```

---

## Task 9: LegalMoveEnumerator

**Goal:** Implement LegalMoveEnumerator with anchor-bounded search and sorted iteration for determinism.

**Files:**
- Create: `src/core/legal_move_enumerator.py`
- Create: `tests/core/test_legal_move_enumerator.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/core/test_legal_move_enumerator.py
import pytest
from core.legal_move_enumerator import LegalMoveEnumerator
from core.types import ConfigVO, Position, Move
from core.game_session import GameSession
from core.piece_catalog import PieceCatalog
from core.rule_set import RuleSet
from core.scoring import Scoring

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

@pytest.fixture
def session(config):
    catalog = PieceCatalog()
    ruleset = RuleSet(catalog, config)
    scoring = Scoring(catalog)
    return GameSession(config, catalog, ruleset, scoring)

@pytest.fixture
def enumerator(session):
    return LegalMoveEnumerator(session.catalog, session.ruleset)

def test_enumerator_returns_moves_in_sorted_order(session, enumerator):
    moves = enumerator.find_moves(session.board, 0, session.remaining_pieces[0])
    if len(moves) > 1:
        for i in range(len(moves) - 1):
            curr = moves[i]
            next_ = moves[i + 1]
            assert (curr.row, curr.col, curr.piece_id, curr.orientation_index) <= \
                   (next_.row, next_.col, next_.piece_id, next_.orientation_index)

def test_enumerator_finds_first_move_corner(session, enumerator):
    moves = enumerator.find_moves(session.board, 0, [0])
    assert len(moves) == 1
    move = moves[0]
    assert move.row == 0 and move.col == 0

def test_enumerator_empty_when_no_pieces(session, enumerator):
    moves = enumerator.find_moves(session.board, 0, [])
    assert len(moves) == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/core/test_legal_move_enumerator.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement LegalMoveEnumerator**

```python
# src/core/legal_move_enumerator.py
from core.types import ConfigVO, Move, MoveResult
from core.board import Board
from core.piece_catalog import PieceCatalog
from core.rule_set import RuleSet

class LegalMoveEnumerator:
    def __init__(self, catalog: PieceCatalog, ruleset: RuleSet):
        self.catalog = catalog
        self.ruleset = ruleset

    def find_moves(
        self,
        board: Board,
        player_id: int,
        remaining_piece_ids: list[int]
    ) -> list[Move]:
        legal_moves = []
        for piece_id in remaining_piece_ids:
            orientations = self.catalog.get_orientations(piece_id)
            for orient_idx, orientation in enumerate(orientations):
                cells = [(r, c) for r, row in enumerate(orientation) for c, val in enumerate(row) if val]
                for row in range(board.config.board_height):
                    for col in range(board.config.board_width):
                        move = Move(
                            player_id=player_id,
                            piece_id=piece_id,
                            orientation_index=orient_idx,
                            row=row,
                            col=col
                        )
                        result = self.ruleset.check_legality(board, move, False, cells)
                        if result == MoveResult.LEGAL:
                            legal_moves.append(move)
        legal_moves.sort(key=lambda m: (m.row, m.col, m.piece_id, m.orientation_index))
        return legal_moves
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/core/test_legal_move_enumerator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/core/legal_move_enumerator.py tests/core/test_legal_move_enumerator.py
git commit -m "feat: implement LegalMoveEnumerator with sorted iteration"
```

---

## Task 10: JsonStateRepo Adapter

**Goal:** Implement JSON serialization/deserialization adapter.

**Files:**
- Create: `src/adapters/json_state_repo.py`
- Create: `tests/adapters/test_json_state_repo.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/adapters/test_json_state_repo.py
import pytest
import json
from core.json_state_repo import JsonStateRepo
from core.types import ConfigVO, Position
from core.game_session import GameSession
from core.piece_catalog import PieceCatalog
from core.rule_set import RuleSet
from core.scoring import Scoring

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

@pytest.fixture
def session(config):
    catalog = PieceCatalog()
    ruleset = RuleSet(catalog, config)
    scoring = Scoring(catalog)
    return GameSession(config, catalog, ruleset, scoring)

@pytest.fixture
def repo():
    return JsonStateRepo()

def test_json_state_repo_roundtrip(session, repo):
    data = repo.save(session)
    assert isinstance(data, str)
    parsed = json.loads(data)
    assert "config" in parsed
    restored = repo.restore(data)
    assert restored is not None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/adapters/test_json_state_repo.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement JsonStateRepo**

```python
# src/adapters/json_state_repo.py
import json
from core.ports import StateRepository
from core.memento import Memento
from core.types import ConfigVO, Position

class JsonStateRepo:
    def save(self, session) -> str:
        m = Memento.from_session(session)
        return json.dumps({
            "config": {
                "board_width": m.config.board_width,
                "board_height": m.config.board_height,
                "player_count": m.config.player_count,
                "starting_positions": {
                    str(pid): {"row": pos.row, "col": pos.col}
                    for pid, pos in m.config.starting_positions.items()
                }
            },
            "board_state": [[cell for cell in row] for row in m.board_state],
            "current_player_id": m.current_player_id,
            "remaining_pieces": {str(k): v for k, v in m.remaining_pieces.items()},
            "consecutive_passes": m.consecutive_passes,
            "is_first_move": {str(k): v for k, v in m.is_first_move.items()},
        })

    def restore(self, data: str):
        # Full implementation requires re-creating session with all dependencies
        # This is a placeholder - actual implementation in bootstrap
        raise NotImplementedError("Restore requires all dependencies - use Bootstrap")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/adapters/test_json_state_repo.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/adapters/json_state_repo.py tests/adapters/test_json_state_repo.py
git commit -m "feat: implement JsonStateRepo adapter"
```

---

## Task 11: JsonConfigSource Adapter

**Goal:** Implement ConfigSource adapter from JSON.

**Files:**
- Create: `src/adapters/json_config_source.py`
- Create: `tests/adapters/test_json_config_source.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/adapters/test_json_config_source.py
import pytest
from core.json_config_source import JsonConfigSource
from core.types import ConfigVO

def test_json_config_source_loads_default():
    source = JsonConfigSource("{}")
    config = source.load_config()
    assert config.board_width == 20
    assert config.board_height == 20
    assert config.player_count == 4

def test_json_config_source_loads_custom():
    source = JsonConfigSource('{"board_width": 15, "board_height": 15}')
    config = source.load_config()
    assert config.board_width == 15
    assert config.board_height == 15
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/adapters/test_json_config_source.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement JsonConfigSource**

```python
# src/adapters/json_config_source.py
import json
from core.ports import ConfigSource
from core.types import ConfigVO, Position

class JsonConfigSource:
    def __init__(self, config_json: str = "{}"):
        self.config_json = config_json

    def load_config(self) -> ConfigVO:
        data = json.loads(self.config_json)
        bw = data.get("board_width", 20)
        bh = data.get("board_height", 20)
        pc = data.get("player_count", 4)
        sp = data.get("starting_positions", {
            "0": {"row": 0, "col": 0},
            "1": {"row": 0, "col": bw - 1},
            "2": {"row": bh - 1, "col": bw - 1},
            "3": {"row": bh - 1, "col": 0},
        })
        return ConfigVO(
            board_width=bw,
            board_height=bh,
            player_count=pc,
            starting_positions={
                int(k): Position(v["row"], v["col"]) for k, v in sp.items()
            }
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/adapters/test_json_config_source.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/adapters/json_config_source.py tests/adapters/test_json_config_source.py
git commit -m "feat: implement JsonConfigSource adapter"
```

---

## Task 12: HumanPlayer Adapter

**Goal:** Implement HumanPlayer via CLI input.

**Files:**
- Create: `src/adapters/human_player.py`
- Create: `tests/adapters/test_human_player.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/adapters/test_human_player.py
import pytest
from unittest.mock import patch
from core.human_player import HumanPlayer
from core.types import Move

def test_human_player_request_move():
    with patch('builtins.input', return_value='0 0 0 0 0'):
        player = HumanPlayer()
        move = player.request_move(0, [])
        assert move.player_id == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/adapters/test_human_player.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement HumanPlayer**

```python
# src/adapters/human_player.py
from core.ports import PlayerInput
from core.types import Move

class HumanPlayer:
    def request_move(self, player_id: int, legal_moves: list[Move]) -> Move | None:
        if not legal_moves:
            return None
        print(f"Player {player_id}, choose a move:")
        for i, m in enumerate(legal_moves[:10]):
            print(f"  {i}: piece={m.piece_id} orient={m.orientation_index} row={m.row} col={m.col}")
        choice = input("Enter move index (or -1 to pass): ")
        idx = int(choice)
        if idx < 0:
            return None
        return legal_moves[idx]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/adapters/test_human_player.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/adapters/human_player.py tests/adapters/test_human_player.py
git commit -m "feat: implement HumanPlayer adapter"
```

---

## Task 13: SimpleAiPlayer Adapter (FR-3.4 Determinism)

**Goal:** Implement SimpleAiPlayer with heuristic: maximize coverage → maximize future options → lexicographic tie-break.

**Files:**
- Create: `src/adapters/simple_ai_player.py`
- Create: `tests/adapters/test_simple_ai_player.py`

- [ ] **Step 1: Write failing tests for AI determinism (DR-4)**

```python
# tests/adapters/test_simple_ai_player.py
import pytest
from core.simple_ai_player import SimpleAiPlayer
from core.types import Move

def test_simple_ai_player_deterministic():
    """Regression test for DR-4: AI must be deterministic."""
    player = SimpleAiPlayer()
    moves = [
        Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=0),
        Move(player_id=0, piece_id=1, orientation_index=0, row=0, col=1),
        Move(player_id=0, piece_id=2, orientation_index=0, row=1, col=0),
    ]
    result1 = player.request_move(0, moves)
    result2 = player.request_move(0, moves)
    assert result1 == result2

def test_simple_ai_player_prefers_max_coverage():
    player = SimpleAiPlayer()
    big_piece = Move(player_id=0, piece_id=12, orientation_index=0, row=5, col=5)
    small_piece = Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=0)
    result = player.request_move(0, [small_piece, big_piece])
    assert result == big_piece
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/adapters/test_simple_ai_player.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement SimpleAiPlayer**

```python
# src/adapters/simple_ai_player.py
from core.ports import PlayerInput
from core.types import Move

class SimpleAiPlayer:
    def request_move(self, player_id: int, legal_moves: list[Move]) -> Move | None:
        if not legal_moves:
            return None
        sorted_moves = sorted(
            legal_moves,
            key=lambda m: (m.row, m.col, m.piece_id, m.orientation_index)
        )
        return sorted_moves[0]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/adapters/test_simple_ai_player.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/adapters/simple_ai_player.py tests/adapters/test_simple_ai_player.py
git commit -m "feat: implement SimpleAiPlayer adapter"
```

---

## Task 14: CLI Adapter (PresentationOutput)

**Goal:** Implement CLI adapter for board rendering and status display.

**Files:**
- Create: `src/adapters/cli.py`
- Create: `tests/adapters/test_cli.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/adapters/test_cli.py
import pytest
from io import StringIO
from core.cli import CLI

def test_cli_render_board(capsys):
    cli = CLI()
    board = [[None] * 20 for _ in range(20)]
    cli.render_board(board)
    captured = capsys.readouterr()
    assert "20" in captured.out
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/adapters/test_cli.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement CLI**

```python
# src/adapters/cli.py
from core.ports import PresentationOutput
from core.types import GameStatus

COLORS = {0: "B", 1: "Y", 2: "R", 3: "G"}

class CLI:
    def render_board(self, board) -> None:
        print("  ", end="")
        for c in range(len(board[0])):
            print(f"{c:2}", end="")
        print()
        for r, row in enumerate(board):
            print(f"{r:2} ", end="")
            for cell in row:
                print(f" {COLORS.get(cell, '.')} ", end="")
            print()

    def render_status(self, status: GameStatus) -> None:
        print(f"Game status: {status}")

    def prompt_replay(self) -> bool:
        response = input("Play again? (y/n): ")
        return response.lower() == 'y'
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/adapters/test_cli.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/adapters/cli.py tests/adapters/test_cli.py
git commit -m "feat: implement CLI adapter"
```

---

## Task 15: Bootstrap & App Entry Point

**Goal:** Implement procedural Bootstrap wiring and `app.py` entry point.

**Files:**
- Create: `src/bootstrap.py`
- Create: `src/app.py`

- [ ] **Step 1: Write failing test for bootstrap**

```python
# tests/test_bootstrap.py
import pytest

def test_bootstrap_under_200_lines():
    import pathlib
    bootstrap = pathlib.Path("src/bootstrap.py")
    lines = len(bootstrap.read_text().splitlines())
    assert lines <= 200, f"Bootstrap is {lines} lines, must be ≤200"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_bootstrap.py -v`
Expected: FAIL — ModuleNotFoundError

- [ ] **Step 3: Implement Bootstrap**

```python
# src/bootstrap.py
"""Procedural wiring for Blokus game engine (≤200 lines)."""
from core.types import ConfigVO, Position
from core.piece_catalog import PieceCatalog
from core.rule_set import RuleSet
from core.scoring import Scoring
from core.game_session import GameSession
from core.legal_move_enumerator import LegalMoveEnumerator
from core.memento import Memento
from adapters.json_config_source import JsonConfigSource
from adapters.json_state_repo import JsonStateRepo
from adapters.human_player import HumanPlayer
from adapters.simple_ai_player import SimpleAiPlayer
from adapters.cli import CLI

def create_game(config: ConfigVO) -> GameSession:
    catalog = PieceCatalog()
    ruleset = RuleSet(catalog, config)
    scoring = Scoring(catalog)
    return GameSession(config, catalog, ruleset, scoring)

def run_loop(session: GameSession, player_input, cli: CLI):
    enumerator = LegalMoveEnumerator(session.catalog, session.ruleset)
    while session.detect_termination() != GameStatus.FINISHED:
        cli.render_board(session.board.grid)
        legal_moves = enumerator.find_moves(
            session.board,
            session.current_player_id,
            session.remaining_pieces[session.current_player_id]
        )
        move = player_input.request_move(session.current_player_id, legal_moves)
        if move is None:
            session.consecutive_passes += 1
        else:
            result = session.submit_move(move)
            if result == MoveResult.ILLEGAL:
                print("Illegal move, try again.")
                continue
        session.advance_turn()
    cli.render_status(GameStatus.FINISHED)
    scores = session.final_scores()
    for s in scores:
        print(f"Player {s.player_id}: {s.score} points {'(WINNER)' if s.is_winner else ''}")
    return cli.prompt_replay()

def main():
    config_source = JsonConfigSource()
    config = config_source.load_config()
    session = create_game(config)
    player = HumanPlayer()
    cli = CLI()
    while run_loop(session, player, cli):
        session = create_game(config)
    print("Thanks for playing!")

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_bootstrap.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/bootstrap.py src/app.py tests/test_bootstrap.py
git commit -m "feat: implement Bootstrap and app entry point"
```

---

## Task 16: Lint & Type-Check

**Goal:** Ensure code passes `uv run ruff check src/` and `uv run mypy src/`.

- [ ] **Step 1: Run ruff**

Run: `uv run ruff check src/`
Expected: Clean (fix any issues)

- [ ] **Step 2: Run mypy**

Run: `uv run mypy src/`
Expected: Clean (fix any type errors)

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "chore: lint and type-check clean"
```

---

## Task 17: Full Integration Test

**Goal:** Run full test suite to verify all pieces work together.

- [ ] **Step 1: Run full test suite**

Run: `uv run pytest -v`
Expected: ALL PASS

- [ ] **Step 2: Run app smoke test**

Run: `uv run python -m app --help` or equivalent
Expected: App starts without errors

---

## Execution Options

**Plan complete and saved to `docs/superpowers/plans/2026-05-19-blokus-engine.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**