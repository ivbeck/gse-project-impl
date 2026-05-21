# Blokus Duo — Engine Extension Design

**Date:** 2026-05-21
**Branch:** `change/duo`
**Status:** Approved design (pre-implementation)

## 1. Purpose & target

Extend the existing Blokus Classic engine to support **Blokus Duo**, the official
two-player Blokus variant as defined in `docs/rules/duo_rulebook.pdf` (Mattel
FWG43).

> **Scope decision.** The user explicitly chose the *physical Blokus Duo product*
> (14×14 board, two single-color players) as the target. This **overrides** the
> interpretation in `specifications/SPEC_M2.md`, which resolved "duo" as the
> two-colors-per-player variant of Classic on a 20×20 board. Where this document
> and `SPEC_M2.md` disagree, **this document and the PDF win**.

Duo is added as a **configuration preset plus a scoring strategy**. Classic
4-player behavior remains unchanged. The feature reaches all three surfaces:
**core engine, CLI, and web GUI**.

## 2. Duo rules (authoritative, from the PDF)

- **Board:** 14×14 (196 squares).
- **Players:** 2, each controlling one color, 21 pieces each (the standard
  polyomino set, identical to Classic).
- **Starting points:** two interior cells, **`{player 0: (4, 4), player 1: (9, 9)}`**
  (0-indexed; symmetric about the board center, the 5th cell in from a corner).
  *Confirmed with the user.*
- **Placement (unchanged from Classic, applied per color):**
  - The first piece must cover the player's starting cell.
  - Every later piece must touch a same-color piece **diagonally** (corner contact).
  - A piece may **not** share a flat edge with a same-color piece.
  - There are no restrictions on contact between differently-colored pieces.
- **Passing:** a player passes only when they have no legal placement.
- **Termination:** the game ends when both players are blocked (or have placed all
  pieces).
- **Scoring (this is the behavioral difference from Classic):**
  - −1 point per unit square in remaining (unplaced) pieces.
  - **+15** if the player placed all 21 pieces.
  - **+5 additional** if the player placed all pieces *and* their last placed piece
    was the monomino (the single-square piece).
  - **The highest score wins.** Ties yield co-winners.
  - Worked examples from the PDF: all pieces placed ending on the monomino = **+20**;
    10 squares left unplaced = **−10**.

## 3. Why this is a small change

The current engine already models each color as an independent actor (`player_id`
`0..player_count-1`) with its own starting position, piece set, first-move flag, and
per-color diagonal/edge rules. Board size, player count, and starting positions are
**already config-driven** (`ConfigVO`). The move validator (`RuleSet`) already enforces
"first piece covers the configured starting cell" generically — it does not assume the
start is a board corner — so **interior starts already work**. The legal-move enumerator
and termination logic are already parameterized by `player_count`.

Therefore the only genuinely new behavior is:

1. **Scoring** (bonuses + highest-wins) — Classic's scoring is a simplified
   "sum remaining, lowest wins" with no bonuses and must stay that way.
2. **Tracking each player's last placed piece** — required for the +5 monomino bonus.
3. **A way to select Duo** — a config preset and a `--duo` launch flag.
4. **Minor GUI generalizations** — mark configured start cells instead of the four
   literal corners.

## 4. Architecture (chosen approach: config-as-data + scoring Strategy)

This honors the repository's stated invariants: configuration is data (not hardcoded
modes), scoring is a Strategy, no game-logic duplication, and the Memento's config is
the single source of truth on reload.

### 4.1 Configuration — `core/types.py`, `adapters/json_config_source.py`

- `ConfigVO` gains a field **`scoring_rule: str = "classic"`**. It is plain data, not a
  branch condition scattered through the core.
- `ConfigBuilder` gains **`with_scoring_rule(rule: str)`**. `build()` validates the rule
  is one of the known values (`"classic"`, `"duo"`) and raises `ValueError` otherwise.
- Default is `"classic"`, so every existing `ConfigVO`/`ConfigBuilder` construction and
  test is unaffected.
- **Duo preset** is expressed as configuration data: a bundled JSON document with
  `board_width=14`, `board_height=14`, `player_count=2`,
  `starting_positions={0:(4,4), 1:(9,9)}`, `scoring_rule="duo"`.
- `JsonConfigSource` is extended to read the optional `scoring_rule` key (default
  `"classic"`). It is otherwise unchanged and reused for both modes.

### 4.2 Scoring Strategy — `core/scoring.py`

- The existing `Scoring` class is retained as the **Classic** rule (sum of remaining
  squares, lowest wins, no bonuses) — **untouched**.
- A new **`DuoScoring`** implements:
  `score = −remaining_squares (+15 if all placed) (+5 if all placed and last piece is the monomino)`;
  **highest score wins**; results sorted descending; ties produce multiple winners.
- The monomino is identified by **square-count == 1 via `PieceCatalog`**, not by a magic
  `piece_id`, keeping piece assumptions inside the catalog.
- A shared square-counting helper is used by both rules (no duplication).
- A small factory **`build_scoring(config, catalog)`** maps `config.scoring_rule` to the
  correct strategy instance.
- Both rules expose a common signature **`rank(remaining, last_placed_piece=None)`**.
  Classic ignores `last_placed_piece`, so the existing scoring tests pass verbatim.

### 4.3 Session, Memento & persistence — `core/game_session.py`, `core/memento.py`, `adapters/json_state_repo.py`

- `GameSession` tracks **`last_placed_piece: dict[int, int | None]`**, initialized to
  `None` per player and set to the placed `piece_id` on each LEGAL move.
- `final_scores()` passes `last_placed_piece` to the scoring strategy.
- Turn cycling and termination (`consecutive_passes >= player_count`) already work for 2
  players — no change.
- **`GameSession.from_memento`** builds its scoring via `build_scoring(memento.config, …)`,
  making the Memento's config the single source of truth for the scoring rule on reload.
  This removes the `scoring` parameter from `from_memento`; its callers and tests are
  updated accordingly.
- `Memento` carries `last_placed_piece` (and `scoring_rule` via its `config`).
- `JsonStateRepo` serializes/deserializes both new pieces of state. **Restore is
  backward-compatible:** absent `scoring_rule` defaults to `"classic"` and absent
  `last_placed_piece` defaults to all-`None`, so previously saved states still load.

### 4.4 Launch wiring — `app.py`, `bootstrap.py`, `web_main.py`

- New **`--duo`** flag in `app.py`. `--duo` selects the Duo preset; `--gui --duo` runs the
  web GUI in Duo mode; bare `--gui` and the no-flag default remain Classic.
- The mode threads through `cli_main(mode)` and `run_web(mode)`, which choose the preset
  config; everything downstream is fully config-driven.

### 4.5 Web GUI — `adapters/web_orchestrator.py`, `static/gui.js`, `static/style.css`

- `/state` additionally exposes **`starting_positions`** (and `scoring_rule`). Board
  dimensions and the player list are already rendered dynamically, so two players display
  correctly.
- `gui.js` marks the **configured starting cells** rather than the four literal board
  corners. This unifies both modes: Classic marks the four corners (which equal its start
  cells), Duo marks the two interior cells.
- Players 0/1 render with the existing first two palette colors (blue/yellow) and
  "Player 1/2" labels. Faithful black/white theming is optional polish, out of scope here.
- The winner highlight already keys off `is_winner`, which the core now sets by
  highest-score in Duo — no scoring logic lives in the GUI. The hardcoded `repeat(20, …)`
  CSS fallback is removed in favor of the JS-driven column count.

## 5. Testing (shared infrastructure, both modes)

- **DuoScoring** unit tests using the PDF numbers: +20 (all placed, monomino last),
  +15 (all placed, not monomino last), −10 (10 squares remaining), highest-wins ordering,
  and tie co-winners.
- **Config** tests: `scoring_rule` parsing and validation; the Duo preset yields 14×14,
  2 players, interior starts.
- **Session** tests: `last_placed_piece` updates on placement and is preserved across
  save/restore; 2-player termination via consecutive passes.
- **Persistence** tests: round-trip of the new fields; backward-compatible load of legacy
  JSON without them.
- **Determinism / golden** test: a fixed Duo board state yields a recorded chosen move and
  recorded final scores (per the determinism contract).
- **Web** tests: `/state` Duo shape including `starting_positions`; correct highest-wins
  `is_winner`; `run_web(mode="duo")` builds a 14×14 / 2-player session; start-cell marker
  rendering.
- Where it adds value, parametrize tests over `{classic, duo}` to share infrastructure.

## 6. Non-goals

- The SPEC_M2 two-colors-per-player variant (explicitly rejected in favor of the PDF).
- Any change to Classic scoring or behavior.
- Duo-specific AI tuning — the existing generic Simple-AI works unchanged.
- Timers and faithful black/white GUI theming beyond distinguishable colors.

## 7. Notable breaking points (to capture in the evolution report)

- The scoring interface gained `last_placed_piece` and a configurable win direction.
- `GameSession.from_memento` now derives scoring from `memento.config` rather than an
  injected instance.
- The Memento/JSON schema was extended (`scoring_rule`, `last_placed_piece`) with
  backward-compatible restore.
- `/state`'s hardcoded color list and the GUI's fixed-corner marker logic were
  generalized to be config-driven.

## 8. Files touched (summary)

| Area | Files | Change |
|------|-------|--------|
| Config | `core/types.py`, `adapters/json_config_source.py` | add `scoring_rule` field + builder method + validation + parse |
| Scoring | `core/scoring.py` | add `DuoScoring`, shared helper, `build_scoring` factory |
| Session | `core/game_session.py` | track `last_placed_piece`; pass to scoring; config-driven `from_memento` |
| Persistence | `core/memento.py`, `adapters/json_state_repo.py` | round-trip new fields, backward-compatible restore |
| Launch | `app.py`, `bootstrap.py`, `web_main.py` | `--duo` flag, mode threading, Duo preset selection |
| Web GUI | `adapters/web_orchestrator.py`, `static/gui.js`, `static/style.css` | expose `starting_positions`; mark configured starts; drop hardcoded 20-col CSS |
| Duo preset | new config JSON (bundled) | 14×14 / 2 players / interior starts / `scoring_rule="duo"` |
| Tests | `tests/core/*`, `tests/adapters/*` | scoring, config, session, persistence, determinism, web, parametrized over modes |
