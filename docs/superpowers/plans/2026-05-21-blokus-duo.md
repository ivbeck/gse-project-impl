# Blokus Duo Engine Extension — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Blokus Duo (14×14 board, two single-color players, interior starting cells, bonus/highest-wins scoring per `docs/rules/duo_rulebook.pdf`) to the existing engine without changing Classic behavior.

**Architecture:** Duo is a configuration preset plus a scoring Strategy. `ConfigVO` carries a `scoring_rule` data field; a `build_scoring` factory maps it to either the existing Classic `Scoring` or a new `DuoScoring`. `GameSession` tracks each player's last-placed piece (for the monomino bonus); the Memento and JSON repository round-trip the new state with backward-compatible restore. A `--duo` flag selects the Duo preset for both CLI and web.

**Tech Stack:** Python 3.12, `uv`, pytest, FastAPI (web), vanilla JS/CSS (GUI). Run tests with `uv run pytest`. Source lives under `src/` (added to `sys.path` by `tests/conftest.py`), so test imports are `from core...`, `from adapters...`.

**Reference spec:** `docs/superpowers/specs/2026-05-21-blokus-duo-design.md`.

**Key facts the engine already provides (do not re-implement):**
- Board size, player count, and starting positions are config-driven (`ConfigVO`).
- `RuleSet` first-move logic requires covering the configured starting cell — it does **not** assume a board corner — so interior starts already work.
- The legal-move enumerator and termination (`consecutive_passes >= player_count`) are already parameterized by player count.
- The monomino is the single-square piece; identify it by **square-count == 1 via the catalog**, never by a hardcoded `piece_id`.

**Task order matters** — later tasks depend on earlier ones. Implement in order.

---

### Task 1: Add `scoring_rule` to ConfigVO and ConfigBuilder

**Files:**
- Modify: `src/core/types.py`
- Test: `tests/core/test_config_vo_literals.py` (add cases here; it already targets ConfigVO)

- [ ] **Step 1: Write failing tests**

Add to `tests/core/test_config_vo_literals.py`:

```python
def test_config_defaults_to_classic_scoring_rule():
    from core.types import ConfigVO, Position
    config = ConfigVO(
        board_width=20, board_height=20, player_count=4,
        starting_positions={0: Position(0, 0)},
    )
    assert config.scoring_rule == "classic"


def test_config_builder_sets_scoring_rule():
    from core.types import ConfigBuilder, Position
    config = (
        ConfigBuilder()
        .with_board_dimensions(14, 14)
        .with_player_count(2)
        .with_starting_positions({0: Position(4, 4), 1: Position(9, 9)})
        .with_scoring_rule("duo")
        .build()
    )
    assert config.scoring_rule == "duo"


def test_config_builder_rejects_unknown_scoring_rule():
    import pytest
    from core.types import ConfigBuilder, Position
    builder = (
        ConfigBuilder()
        .with_board_dimensions(14, 14)
        .with_player_count(2)
        .with_starting_positions({0: Position(4, 4), 1: Position(9, 9)})
        .with_scoring_rule("nonsense")
    )
    with pytest.raises(ValueError):
        builder.build()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/core/test_config_vo_literals.py -k scoring_rule -v`
Expected: FAIL (`ConfigVO` has no `scoring_rule`; `ConfigBuilder` has no `with_scoring_rule`).

- [ ] **Step 3: Implement**

In `src/core/types.py`, add the field to `ConfigVO` (it must be the **last** field since it has a default):

```python
@dataclass(frozen=True)
class ConfigVO:
    board_width: int
    board_height: int
    player_count: int
    starting_positions: dict[int, Position]
    scoring_rule: str = "classic"
```

In `ConfigBuilder.__init__` add:

```python
        self._scoring_rule: str = "classic"
```

Add the builder method (after `with_starting_positions`):

```python
    def with_scoring_rule(self, scoring_rule: str) -> ConfigBuilder:
        self._scoring_rule = scoring_rule
        return self
```

In `ConfigBuilder.build`, add validation before the `return` and pass the field through:

```python
        if self._scoring_rule not in {"classic", "duo"}:
            raise ValueError("scoring_rule must be 'classic' or 'duo'")
        return ConfigVO(
            board_width=self._board_width,
            board_height=self._board_height,
            player_count=self._player_count,
            starting_positions=dict(self._starting_positions),
            scoring_rule=self._scoring_rule,
        )
```

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/core/test_config_vo_literals.py -v`
Expected: PASS (new and existing cases).

- [ ] **Step 5: Commit**

```bash
git add src/core/types.py tests/core/test_config_vo_literals.py
git commit -m "feat: add scoring_rule config field and builder support"
```

---

### Task 2: Parse `scoring_rule` in JsonConfigSource and add the Duo preset

**Files:**
- Modify: `src/adapters/json_config_source.py`
- Test: `tests/adapters/test_json_config_source.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/adapters/test_json_config_source.py`:

```python
def test_json_config_source_defaults_scoring_rule_to_classic():
    from adapters.json_config_source import JsonConfigSource
    config = JsonConfigSource().load_config()
    assert config.scoring_rule == "classic"


def test_json_config_source_reads_scoring_rule():
    import json
    from adapters.json_config_source import JsonConfigSource
    config = JsonConfigSource(json.dumps({"scoring_rule": "duo", "player_count": 2,
        "starting_positions": {"0": {"row": 4, "col": 4}, "1": {"row": 9, "col": 9}},
        "board_width": 14, "board_height": 14})).load_config()
    assert config.scoring_rule == "duo"


def test_duo_preset_is_a_14x14_two_player_duo_config():
    from adapters.json_config_source import JsonConfigSource, DUO_CONFIG_JSON
    from core.types import Position
    config = JsonConfigSource(DUO_CONFIG_JSON).load_config()
    assert config.board_width == 14
    assert config.board_height == 14
    assert config.player_count == 2
    assert config.scoring_rule == "duo"
    assert config.starting_positions == {0: Position(4, 4), 1: Position(9, 9)}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/adapters/test_json_config_source.py -k "scoring_rule or duo_preset" -v`
Expected: FAIL (no `DUO_CONFIG_JSON`; `scoring_rule` not parsed).

- [ ] **Step 3: Implement**

In `src/adapters/json_config_source.py`, add the preset constant at module top (after the imports):

```python
DUO_CONFIG_JSON = """
{
  "board_width": 14,
  "board_height": 14,
  "player_count": 2,
  "starting_positions": {
    "0": {"row": 4, "col": 4},
    "1": {"row": 9, "col": 9}
  },
  "scoring_rule": "duo"
}
"""
```

In `load_config`, read the rule and thread it through the builder:

```python
        sp = data.get("starting_positions", {
            "0": {"row": 0, "col": 0},
            "1": {"row": 0, "col": bw - 1},
            "2": {"row": bh - 1, "col": bw - 1},
            "3": {"row": bh - 1, "col": 0},
        })
        scoring_rule = data.get("scoring_rule", "classic")
        return (
            ConfigBuilder()
            .with_board_dimensions(bw, bh)
            .with_player_count(pc)
            .with_starting_positions({
                int(k): Position(v["row"], v["col"]) for k, v in sp.items()
            })
            .with_scoring_rule(scoring_rule)
            .build()
        )
```

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/adapters/test_json_config_source.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/adapters/json_config_source.py tests/adapters/test_json_config_source.py
git commit -m "feat: parse scoring_rule and add Duo config preset"
```

---

### Task 3: Add DuoScoring strategy and build_scoring factory

**Files:**
- Modify: `src/core/scoring.py`
- Test: `tests/core/test_scoring.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/core/test_scoring.py`:

```python
from core.scoring import DuoScoring, build_scoring
from core.types import ConfigVO, Position


def test_duo_all_placed_ending_on_monomino_scores_20(catalog):
    duo = DuoScoring(catalog)
    scores = duo.rank({0: [], 1: list(range(21))}, last_placed_piece={0: 0, 1: None})
    p0 = next(s for s in scores if s.player_id == 0)
    assert p0.score == 20  # 0 remaining + 15 all-placed + 5 monomino-last
    assert p0.is_winner


def test_duo_all_placed_not_monomino_last_scores_15(catalog):
    duo = DuoScoring(catalog)
    scores = duo.rank({0: [], 1: list(range(21))}, last_placed_piece={0: 5, 1: None})
    p0 = next(s for s in scores if s.player_id == 0)
    assert p0.score == 15


def test_duo_remaining_squares_are_negative_and_highest_wins(catalog):
    duo = DuoScoring(catalog)
    # piece 2 is a 3-square piece, piece 4 a 4-square piece -> 10 squares remaining
    scores = duo.rank({0: [2, 2, 4], 1: []}, last_placed_piece={0: None, 1: 7})
    p0 = next(s for s in scores if s.player_id == 0)
    p1 = next(s for s in scores if s.player_id == 1)
    assert p0.score == -10
    assert p1.score == 15
    assert p1.is_winner and not p0.is_winner
    assert scores[0].player_id == 1  # sorted highest-first


def test_build_scoring_selects_strategy_by_config(catalog):
    from core.scoring import Scoring
    classic = ConfigVO(board_width=20, board_height=20, player_count=4,
                       starting_positions={0: Position(0, 0)}, scoring_rule="classic")
    duo = ConfigVO(board_width=14, board_height=14, player_count=2,
                   starting_positions={0: Position(4, 4)}, scoring_rule="duo")
    assert isinstance(build_scoring(classic, catalog), Scoring)
    assert isinstance(build_scoring(duo, catalog), DuoScoring)
```

Note: `piece 2 == [["1","1","1"]]` (3 squares); `piece 4 == [["1","1","1","1"]]` (4 squares); `2+2+... ` → `3+3+4 = 10`. `piece 5 == 2x2` (4 squares) is unrelated.

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/core/test_scoring.py -k "duo or build_scoring" -v`
Expected: FAIL (`DuoScoring`/`build_scoring` not defined).

- [ ] **Step 3: Implement**

Replace the contents of `src/core/scoring.py` with (this extracts a shared helper so the Classic and Duo rules do not duplicate square-counting; Classic behavior is unchanged):

```python
from core.piece_catalog import PieceCatalog
from core.types import ConfigVO, PlayerScore


MONOMINO_SQUARE_COUNT = 1


def piece_square_count(catalog: PieceCatalog, piece_id: int) -> int:
    piece = catalog.get_by_id(piece_id)
    return sum(cell for row in piece.shape for cell in row)


class Scoring:
    def __init__(self, catalog: PieceCatalog):
        self.catalog = catalog

    def rank(self, remaining: dict[int, list[int]], last_placed_piece=None) -> list[PlayerScore]:
        scores = []
        for player_id, piece_ids in remaining.items():
            total = sum(piece_square_count(self.catalog, pid) for pid in piece_ids)
            scores.append(PlayerScore(player_id=player_id, score=total, is_winner=False))

        min_score = min(s.score for s in scores)
        scores = [
            PlayerScore(player_id=s.player_id, score=s.score, is_winner=(s.score == min_score))
            for s in scores
        ]
        return sorted(scores, key=lambda s: s.score)


class DuoScoring:
    def __init__(self, catalog: PieceCatalog):
        self.catalog = catalog

    def rank(self, remaining: dict[int, list[int]], last_placed_piece=None) -> list[PlayerScore]:
        last_placed_piece = last_placed_piece or {}
        scores = []
        for player_id, piece_ids in remaining.items():
            remaining_squares = sum(piece_square_count(self.catalog, pid) for pid in piece_ids)
            score = -remaining_squares
            if remaining_squares == 0:
                score += 15
                last = last_placed_piece.get(player_id)
                if last is not None and piece_square_count(self.catalog, last) == MONOMINO_SQUARE_COUNT:
                    score += 5
            scores.append(PlayerScore(player_id=player_id, score=score, is_winner=False))

        max_score = max(s.score for s in scores)
        scores = [
            PlayerScore(player_id=s.player_id, score=s.score, is_winner=(s.score == max_score))
            for s in scores
        ]
        return sorted(scores, key=lambda s: -s.score)


def build_scoring(config: ConfigVO, catalog: PieceCatalog):
    if config.scoring_rule == "duo":
        return DuoScoring(catalog)
    return Scoring(catalog)
```

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/core/test_scoring.py -v`
Expected: PASS (new Duo cases plus the three original Classic cases, unchanged).

- [ ] **Step 5: Commit**

```bash
git add src/core/scoring.py tests/core/test_scoring.py
git commit -m "feat: add DuoScoring strategy and build_scoring factory"
```

---

### Task 4: Track last-placed piece in GameSession and feed it to scoring

**Files:**
- Modify: `src/core/game_session.py`
- Test: `tests/core/test_game_session.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/core/test_game_session.py` (it already imports `Move`, `PieceCatalog`, `RuleSet`, `Scoring` and has a `session` fixture):

```python
def test_last_placed_piece_starts_none(session):
    assert session.last_placed_piece == {0: None, 1: None, 2: None, 3: None}


def test_last_placed_piece_records_successful_move(session):
    session.submit_move(Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=0))
    assert session.last_placed_piece[0] == 0
    assert session.last_placed_piece[1] is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/core/test_game_session.py -k last_placed_piece -v`
Expected: FAIL (`GameSession` has no `last_placed_piece`).

- [ ] **Step 3: Implement**

In `src/core/game_session.py` `__init__`, after the `_is_first_move` line, add:

```python
        self.last_placed_piece: dict[int, int | None] = {i: None for i in range(config.player_count)}
```

In `submit_move`, inside the `if result == MoveResult.LEGAL:` block, after `self._is_first_move[move.player_id] = False`, add:

```python
            self.last_placed_piece[move.player_id] = move.piece_id
```

Change `final_scores` to pass the new state:

```python
    def final_scores(self) -> list[PlayerScore]:
        return self.scoring.rank(self.remaining_pieces, self.last_placed_piece)
```

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/core/test_game_session.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/core/game_session.py tests/core/test_game_session.py
git commit -m "feat: track last placed piece per player and pass to scoring"
```

---

### Task 5: Carry last-placed piece in the Memento

**Files:**
- Modify: `src/core/memento.py`
- Test: `tests/core/test_memento.py`

- [ ] **Step 1: Write failing test**

Add to `tests/core/test_memento.py`:

```python
def test_memento_captures_last_placed_piece(session):
    from core.types import Move
    session.submit_move(Move(player_id=0, piece_id=0, orientation_index=0, row=0, col=0))
    m = Memento.from_session(session)
    assert (0, 0) in m.last_placed_piece
    assert (1, None) in m.last_placed_piece
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/core/test_memento.py -k last_placed_piece -v`
Expected: FAIL (`Memento` has no `last_placed_piece`).

- [ ] **Step 3: Implement**

In `src/core/memento.py`, add the field to the dataclass (last, with a default for backward-safety):

```python
@dataclass(frozen=True)
class Memento:
    config: ConfigVO
    board_state: tuple[tuple[int | None, ...], ...]
    current_player_id: int
    remaining_pieces: tuple[tuple[int, tuple[int, ...]], ...]
    consecutive_passes: int
    is_first_move: tuple[tuple[int, bool], ...]
    last_placed_piece: tuple[tuple[int, int | None], ...] = ()
```

In `from_session`, build the tuple and pass it to `cls(...)`:

```python
        last_placed_piece = tuple(
            (player_id, piece_id)
            for player_id, piece_id in sorted(session.last_placed_piece.items())
        )
        return cls(
            config=session.config,
            board_state=board_state,
            current_player_id=session.current_player_id,
            remaining_pieces=remaining_pieces,
            consecutive_passes=session.consecutive_passes,
            is_first_move=is_first_move,
            last_placed_piece=last_placed_piece,
        )
```

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/core/test_memento.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/core/memento.py tests/core/test_memento.py
git commit -m "feat: carry last_placed_piece in Memento"
```

---

### Task 6: Round-trip new state through JsonStateRepo with backward-compat

**Files:**
- Modify: `src/adapters/json_state_repo.py`
- Test: `tests/adapters/test_json_state_repo.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/adapters/test_json_state_repo.py`:

```python
def test_json_state_repo_round_trips_scoring_rule_and_last_placed_piece():
    from core.memento import Memento
    from core.types import ConfigVO, Position
    from adapters.json_state_repo import JsonStateRepo
    config = ConfigVO(board_width=14, board_height=14, player_count=2,
                      starting_positions={0: Position(4, 4), 1: Position(9, 9)},
                      scoring_rule="duo")
    memento = Memento(
        config=config,
        board_state=tuple(tuple(None for _ in range(14)) for _ in range(14)),
        current_player_id=0,
        remaining_pieces=((0, (1, 2)), (1, ())),
        consecutive_passes=0,
        is_first_move=((0, True), (1, True)),
        last_placed_piece=((0, 5), (1, None)),
    )
    repo = JsonStateRepo()
    restored = repo.restore(repo.save(memento))
    assert restored.config.scoring_rule == "duo"
    assert restored.last_placed_piece == ((0, 5), (1, None))


def test_json_state_repo_restore_is_backward_compatible():
    import json
    from adapters.json_state_repo import JsonStateRepo
    legacy = json.dumps({
        "config": {"board_width": 20, "board_height": 20, "player_count": 1,
                   "starting_positions": {"0": {"row": 0, "col": 0}}},
        "board_state": [[None for _ in range(20)] for _ in range(20)],
        "current_player_id": 0,
        "remaining_pieces": [[0, [0, 1]]],
        "consecutive_passes": 0,
        "is_first_move": [[0, True]],
    })
    memento = JsonStateRepo().restore(legacy)
    assert memento.config.scoring_rule == "classic"
    assert memento.last_placed_piece == ()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/adapters/test_json_state_repo.py -k "round_trips or backward" -v`
Expected: FAIL (new fields not serialized/restored).

- [ ] **Step 3: Implement**

In `src/adapters/json_state_repo.py` `save`, add `scoring_rule` inside the `"config"` dict and a top-level `"last_placed_piece"` key:

```python
            "config": {
                "board_width": memento.config.board_width,
                "board_height": memento.config.board_height,
                "player_count": memento.config.player_count,
                "scoring_rule": memento.config.scoring_rule,
                "starting_positions": {
                    str(pid): {"row": pos.row, "col": pos.col}
                    for pid, pos in sorted(memento.config.starting_positions.items())
                }
            },
```

and (alongside the other top-level keys, before the closing `}, sort_keys=True)`):

```python
            "last_placed_piece": [
                [player_id, piece_id]
                for player_id, piece_id in memento.last_placed_piece
            ],
```

In `restore`, thread the rule through the builder and read the new key:

```python
        config = (
            ConfigBuilder()
            .with_board_dimensions(config_data["board_width"], config_data["board_height"])
            .with_player_count(config_data["player_count"])
            .with_starting_positions({
                int(pid): Position(pos["row"], pos["col"])
                for pid, pos in config_data["starting_positions"].items()
            })
            .with_scoring_rule(config_data.get("scoring_rule", "classic"))
            .build()
        )
```

and build the new field before constructing the `Memento`, then add it to the constructor call:

```python
        last_placed_piece = tuple(
            (item[0], item[1])
            for item in parsed.get("last_placed_piece", [])
        )
        return Memento(
            config=config,
            board_state=board_state,
            current_player_id=parsed["current_player_id"],
            remaining_pieces=remaining_pieces,
            consecutive_passes=parsed["consecutive_passes"],
            is_first_move=is_first_move,
            last_placed_piece=last_placed_piece,
        )
```

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/adapters/test_json_state_repo.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/adapters/json_state_repo.py tests/adapters/test_json_state_repo.py
git commit -m "feat: round-trip scoring_rule and last_placed_piece in JSON state"
```

---

### Task 7: Make GameSession.from_memento derive scoring from config and restore last-placed piece

**Files:**
- Modify: `src/core/game_session.py`
- Modify: `tests/core/test_game_session.py:87` (caller), `tests/adapters/test_simple_ai_player.py:95` (caller)
- Test: `tests/core/test_game_session.py`

- [ ] **Step 1: Write failing test**

Add to `tests/core/test_game_session.py`:

```python
def test_from_memento_restores_scoring_and_last_placed(session):
    from core.memento import Memento
    from core.scoring import DuoScoring
    from core.types import ConfigBuilder, Position
    duo_config = (ConfigBuilder().with_board_dimensions(14, 14).with_player_count(2)
                  .with_starting_positions({0: Position(4, 4), 1: Position(9, 9)})
                  .with_scoring_rule("duo").build())
    catalog = PieceCatalog()
    ruleset = RuleSet(catalog, duo_config)
    duo_session = GameSession(duo_config, catalog, ruleset, Scoring(catalog))
    duo_session.submit_move(Move(player_id=0, piece_id=0, orientation_index=0, row=4, col=4))
    memento = Memento.from_session(duo_session)
    restored = GameSession.from_memento(memento, catalog)
    assert isinstance(restored.scoring, DuoScoring)
    assert restored.last_placed_piece == {0: 0, 1: None}
```

Also update the **existing** caller in the same file (`test_game_session_restore_uses_memento_config`):

```python
    restored = GameSession.from_memento(memento, catalog)
```

- [ ] **Step 2: Run tests to verify failure**

Run: `uv run pytest tests/core/test_game_session.py -k "from_memento or restore_uses" -v`
Expected: FAIL (signature still requires `scoring`; `DuoScoring` not selected; `last_placed_piece` not restored).

- [ ] **Step 3: Implement**

In `src/core/game_session.py`, change the import line `from core.scoring import Scoring` to:

```python
from core.scoring import build_scoring
```

Replace the `from_memento` method header and scoring construction:

```python
    @classmethod
    def from_memento(cls, memento: "Memento", catalog: PieceCatalog) -> "GameSession":
        ruleset = RuleSet(catalog, memento.config)
        scoring = build_scoring(memento.config, catalog)
        session = cls(memento.config, catalog, ruleset, scoring)
```

Keep the existing board/remaining/passes/first-move restore lines, then before `return session` add:

```python
        session.last_placed_piece = {i: None for i in range(memento.config.player_count)}
        session.last_placed_piece.update(
            {player_id: piece_id for player_id, piece_id in memento.last_placed_piece}
        )
        return session
```

Also remove the now-unused `Scoring` parameter type from the constructor docstring/signature usage — the constructor `__init__` still takes a `scoring` object (built by `build_scoring` or `bootstrap`), so leave `__init__` unchanged.

Update the other caller, `tests/adapters/test_simple_ai_player.py:95`:

```python
    session = GameSession.from_memento(memento, catalog)
```

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/core/test_game_session.py tests/adapters/test_simple_ai_player.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/core/game_session.py tests/core/test_game_session.py tests/adapters/test_simple_ai_player.py
git commit -m "refactor: derive scoring from memento config and restore last_placed_piece"
```

---

### Task 8: Use build_scoring in bootstrap and add a mode parameter to main

**Files:**
- Modify: `src/bootstrap.py`
- Test: `tests/test_bootstrap.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/test_bootstrap.py`:

```python
def test_create_game_uses_duo_scoring_for_duo_config():
    from bootstrap import create_game
    from adapters.json_config_source import JsonConfigSource, DUO_CONFIG_JSON
    from core.scoring import DuoScoring
    config = JsonConfigSource(DUO_CONFIG_JSON).load_config()
    session = create_game(config)
    assert isinstance(session.scoring, DuoScoring)
    assert session.config.player_count == 2


def test_create_game_uses_classic_scoring_by_default():
    from bootstrap import create_game
    from adapters.json_config_source import JsonConfigSource
    from core.scoring import Scoring
    session = create_game(JsonConfigSource().load_config())
    assert isinstance(session.scoring, Scoring)
```

- [ ] **Step 2: Run tests to verify failure**

Run: `uv run pytest tests/test_bootstrap.py -k "duo_scoring or classic_scoring" -v`
Expected: FAIL (`create_game` always builds `Scoring`).

- [ ] **Step 3: Implement**

In `src/bootstrap.py`, change the imports and `create_game`:

```python
from core.scoring import build_scoring
```

(remove `from core.scoring import Scoring`)

```python
def create_game(config: ConfigVO) -> GameSession:
    catalog = PieceCatalog()
    ruleset = RuleSet(catalog, config)
    scoring = build_scoring(config, catalog)
    return GameSession(config, catalog, ruleset, scoring)
```

Change `main` to accept a mode and select the preset:

```python
from adapters.json_config_source import JsonConfigSource, DUO_CONFIG_JSON
```

```python
def main(mode: str = "classic"):
    config_json = DUO_CONFIG_JSON if mode == "duo" else "{}"
    config_source = JsonConfigSource(config_json)
    config = config_source.load_config()
    session = create_game(config)
    player = HumanPlayer()
    cli = CLI()
    while run_loop(session, player, cli):
        session = create_game(config)
    print("Thanks for playing!")
```

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/test_bootstrap.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/bootstrap.py tests/test_bootstrap.py
git commit -m "feat: select scoring via build_scoring and add Duo mode to bootstrap.main"
```

---

### Task 9: Add the `--duo` flag (CLI + web entry)

**Files:**
- Modify: `src/app.py`, `src/web_main.py`
- Test: `tests/test_app_cli.py` (new)

- [ ] **Step 1: Write failing test**

Create `tests/test_app_cli.py`:

```python
from unittest.mock import patch
import app


def test_app_passes_duo_mode_to_cli():
    with patch.object(app, "cli_main") as cli_main, \
         patch("sys.argv", ["blokus-engine", "--duo"]):
        app.main()
    cli_main.assert_called_once_with("duo")


def test_app_defaults_to_classic_cli():
    with patch.object(app, "cli_main") as cli_main, \
         patch("sys.argv", ["blokus-engine"]):
        app.main()
    cli_main.assert_called_once_with("classic")
```

- [ ] **Step 2: Run test to verify failure**

Run: `uv run pytest tests/test_app_cli.py -v`
Expected: FAIL (`cli_main` called with no args; no `--duo` flag).

- [ ] **Step 3: Implement**

Replace `src/app.py` `main` body:

```python
def main():
    parser = argparse.ArgumentParser(description="Blokus Game")
    parser.add_argument("--gui", action="store_true", help="Start web GUI")
    parser.add_argument("--duo", action="store_true", help="Play Blokus Duo (14x14, 2 players)")
    args = parser.parse_args()

    mode = "duo" if args.duo else "classic"
    if args.gui:
        from web_main import run_web
        run_web(mode)
    else:
        cli_main(mode)
```

Update `src/web_main.py` `run_web`:

```python
from adapters.json_config_source import JsonConfigSource, DUO_CONFIG_JSON
```

```python
def run_web(mode: str = "classic"):
    config_json = DUO_CONFIG_JSON if mode == "duo" else "{}"
    config = JsonConfigSource(config_json).load_config()
    session = create_game(config)
    player = WebPlayerAdapter()
    presenter = WebPresentationAdapter(session)
    app = create_web_orchestrator(session, player, presenter)
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/test_app_cli.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/app.py src/web_main.py tests/test_app_cli.py
git commit -m "feat: add --duo flag for CLI and web entry points"
```

---

### Task 10: Expose starting positions and scoring rule in /state

**Files:**
- Modify: `src/adapters/web_orchestrator.py`
- Test: `tests/adapters/test_web_orchestrator.py`

- [ ] **Step 1: Write failing tests**

In `tests/adapters/test_web_orchestrator.py`, update `test_web_orchestrator_state_returns_game_data` by adding (right after `mock_session.consecutive_passes = 0`):

```python
    mock_session.config = _config()
```

and add the field assertions at the end of that test:

```python
    assert "starting_positions" in data
    assert "scoring_rule" in data
```

Add a new test:

```python
def test_state_exposes_duo_starting_positions_and_rule():
    from adapters.json_config_source import JsonConfigSource, DUO_CONFIG_JSON
    session = create_game(JsonConfigSource(DUO_CONFIG_JSON).load_config())
    app = create_web_orchestrator(session, None, Mock())
    client = TestClient(app)
    data = client.get("/state").json()
    assert data["scoring_rule"] == "duo"
    assert data["starting_positions"] == {"0": {"row": 4, "col": 4}, "1": {"row": 9, "col": 9}}
    assert len(data["players"]) == 2
```

- [ ] **Step 2: Run tests to verify failure**

Run: `uv run pytest tests/adapters/test_web_orchestrator.py -k "state" -v`
Expected: FAIL (no `starting_positions`/`scoring_rule` in `/state`).

- [ ] **Step 3: Implement**

In `src/adapters/web_orchestrator.py`, inside the `/state` handler's returned dict, add two keys (after `"consecutive_passes": session.consecutive_passes,`):

```python
            "starting_positions": {
                str(pid): {"row": pos.row, "col": pos.col}
                for pid, pos in session.config.starting_positions.items()
            },
            "scoring_rule": session.config.scoring_rule,
```

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/adapters/test_web_orchestrator.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/adapters/web_orchestrator.py tests/adapters/test_web_orchestrator.py
git commit -m "feat: expose starting_positions and scoring_rule in /state"
```

---

### Task 11: Mark configured starting cells in the GUI (interior starts for Duo)

**Files:**
- Modify: `src/static/gui.js`, `src/static/style.css`
- Test: `tests/adapters/test_web_gui_starting_cells_static.py` (new)

- [ ] **Step 1: Write failing test**

Create `tests/adapters/test_web_gui_starting_cells_static.py`:

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUI_JS = ROOT / "src" / "static" / "gui.js"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def test_gui_marks_configured_starting_cells_not_fixed_corners():
    gui = _read(GUI_JS)
    assert "state.starting_positions" in gui
    assert "startingCells" in gui
    # The old fixed four-corner detection is gone.
    assert "ri === 0 && ci === 0" not in gui
```

- [ ] **Step 2: Run test to verify failure**

Run: `uv run pytest tests/adapters/test_web_gui_starting_cells_static.py -v`
Expected: FAIL (gui.js still uses fixed-corner detection).

- [ ] **Step 3: Implement**

In `src/static/gui.js`, add a module-level variable near the other `let` declarations at the top (after `let currentBoard = [];`):

```javascript
let startingCells = [];
```

In `loadState`, set it from the state before rendering the board. Change the body so `currentPlayerId` and `startingCells` are assigned before `renderBoard`:

```javascript
        currentPlayerId = state.current_player_id;
        startingCells = Object.values(state.starting_positions || {}).map(p => `${p.row},${p.col}`);
        renderBoard(state.board);
```

In `renderBoard`, replace the four-corner detection block:

```javascript
            /* Mark corner cells subtly */
            const lastRow = board.length - 1;
            const lastCol = cols - 1;
            const isCorner = (ri === 0 && ci === 0) ||
                             (ri === 0 && ci === lastCol) ||
                             (ri === lastRow && ci === 0) ||
                             (ri === lastRow && ci === lastCol);
            if (isCorner && cell === null) div.classList.add('corner-marker');
```

with:

```javascript
            /* Mark the configured starting cells subtly (corners in Classic, interior in Duo) */
            const isStart = startingCells.includes(`${ri},${ci}`);
            if (isStart && cell === null) div.classList.add('corner-marker');
```

In `src/static/style.css`, update the comment above `.cell.corner-marker::after` (line ~330) from `/* Starting corners — subtle markers */` to:

```css
/* Starting cells — subtle markers (board corners in Classic, interior cells in Duo) */
```

and update the `#board` rule's column line (line ~274) to document that JS drives it:

```css
    grid-template-columns: repeat(20, 26px); /* default; gui.js sets the real count per board width */
```

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/adapters/test_web_gui_starting_cells_static.py tests/adapters/test_web_gui_hover_preview_static.py -v`
Expected: PASS (new test passes; the existing hover-preview static test still passes since its assertions are untouched).

- [ ] **Step 5: Commit**

```bash
git add src/static/gui.js src/static/style.css tests/adapters/test_web_gui_starting_cells_static.py
git commit -m "feat: mark configured starting cells in GUI for Duo interior starts"
```

---

### Task 12: Duo end-to-end determinism and integration tests

**Files:**
- Test: `tests/core/test_duo_game.py` (new)

- [ ] **Step 1: Write the tests**

Create `tests/core/test_duo_game.py`:

```python
from adapters.json_config_source import JsonConfigSource, DUO_CONFIG_JSON
from adapters.simple_ai_player import SimpleAiPlayer
from bootstrap import create_game
from core.board import Board
from core.legal_move_enumerator import LegalMoveEnumerator
from core.piece_catalog import PieceCatalog
from core.rule_set import RuleSet
from core.types import GameStatus, Move


def _duo_config():
    return JsonConfigSource(DUO_CONFIG_JSON).load_config()


def test_duo_first_move_monomino_must_cover_interior_start():
    config = _duo_config()
    catalog = PieceCatalog()
    enumerator = LegalMoveEnumerator(catalog, RuleSet(catalog, config))
    board = Board(config)
    moves = enumerator.find_moves(board, 0, [0], is_first_move=True)
    # The monomino has one cell and one orientation; the only legal first move
    # is the one that lands it on player 0's interior starting cell (4, 4).
    assert moves == [Move(player_id=0, piece_id=0, orientation_index=0, row=4, col=4)]


def test_duo_ai_vs_ai_game_finishes_with_consistent_ranking():
    session = create_game(_duo_config())
    enumerator = LegalMoveEnumerator(session.catalog, session.ruleset)
    ai = SimpleAiPlayer(session.catalog, session.board)

    safety = 0
    while session.detect_termination() != GameStatus.FINISHED and safety < 2000:
        safety += 1
        pid = session.current_player_id
        legal = enumerator.find_moves(
            session.board, pid,
            session.remaining_pieces[pid],
            session.is_first_move(pid),
        )
        move = ai.request_move(pid, legal)
        if move is None:
            session.submit_pass()
        else:
            session.submit_move(move)
        session.advance_turn()

    assert session.detect_termination() == GameStatus.FINISHED
    scores = session.final_scores()
    assert len(scores) == 2
    # Highest score first; winner flag set exactly for the maximum score.
    assert scores == sorted(scores, key=lambda s: -s.score)
    top = scores[0].score
    assert all(s.is_winner == (s.score == top) for s in scores)
```

- [ ] **Step 2: Run the tests**

Run: `uv run pytest tests/core/test_duo_game.py -v`
Expected: PASS. (The AI-vs-AI game is deterministic and should finish in well under the safety bound.)

- [ ] **Step 3: Commit**

```bash
git add tests/core/test_duo_game.py
git commit -m "test: add Duo determinism and AI-vs-AI integration tests"
```

---

### Task 13: Full suite + manual smoke check

**Files:** none (verification only)

- [ ] **Step 1: Run the entire test suite**

Run: `uv run pytest`
Expected: PASS, no failures, no warnings-as-errors.

- [ ] **Step 2: Manual CLI smoke (optional, interactive)**

Run: `uv run blokus-engine --duo`
Expected: a 14×14 board renders; player 0's first piece must cover (4,4).

- [ ] **Step 3: Manual web smoke (optional, interactive)**

Run: `uv run blokus-engine --gui --duo`, open http://127.0.0.1:8000
Expected: a 14×14 board with the two interior start cells marked; two players in the dashboard.

- [ ] **Step 4: Commit (if any fixups were needed)**

```bash
git add -A
git commit -m "chore: finalize Blokus Duo support"
```

---

## Self-Review

**Spec coverage** (each spec section → task):
- §2 board 14×14 / 2 players / interior starts → Task 2 (preset) + Task 12 (verified).
- §2 placement rules (unchanged) → relied upon, verified by Task 12 first-move test.
- §2 scoring (−1/sq, +15, +5 monomino-last, highest wins) → Task 3 (`DuoScoring`).
- §4.1 config `scoring_rule` + Duo preset → Tasks 1, 2.
- §4.2 scoring Strategy + factory + shared helper + monomino-by-square-count → Task 3.
- §4.3 `last_placed_piece` tracking, `final_scores` wiring, config-driven `from_memento` → Tasks 4, 7.
- §4.3 Memento + persistence round-trip + backward-compat → Tasks 5, 6.
- §4.4 `--duo` launch wiring (CLI + web) → Tasks 8, 9.
- §4.5 `/state` exposes `starting_positions`/`scoring_rule`; GUI marks configured starts; CSS comment → Tasks 10, 11.
- §5 tests (DuoScoring, config, session, persistence, determinism, web, parametrized intent) → Tasks 1–12.
- §6 non-goals → respected (Classic `Scoring` untouched; no two-color variant; generic AI reused).

**Placeholder scan:** No TBD/TODO; every code step shows complete code; every command shows expected output. ✓

**Type/name consistency:** `scoring_rule` (str), `with_scoring_rule`, `build_scoring(config, catalog)`, `DuoScoring`, `piece_square_count(catalog, piece_id)`, `MONOMINO_SQUARE_COUNT`, `last_placed_piece` (dict in session, tuple-of-pairs in Memento/JSON), `DUO_CONFIG_JSON`, `from_memento(memento, catalog)`, `run_web(mode)`, `main(mode)` — used consistently across tasks. ✓
