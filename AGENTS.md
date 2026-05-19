# AGENTS.md

Minimal context for coding agents working in this repository. Read first; do not re-derive from the codebase.

## Authoritative sources

- Requirements: [specifications/SPEC_M1.md](specifications/SPEC_M1.md). Open ambiguities: [specifications/AMBIGUITY_LOG.md](specifications/AMBIGUITY_LOG.md).
- Architecture & design: [design/ADR.md](design/ADR.md) (binding decision is `ADR-FINAL-P2`). UML: [design/blokus_core_mermaid_uml_class_diagram_v2.html](design/blokus_core_mermaid_uml_class_diagram_v2.html) — **v2 only**, ignore v1.
- Milestone 2 (Duo) is out of scope for current work. Do not add Duo-named paths.

## Language & build / test / run

**Python is the chosen implementation language.** Use `uv` for all package and environment management — do not introduce `pip`, `poetry`, `conda`, or `setup.py` workflows. NFR-2.1 permits Java/Maven *or* Python/uv; this project has committed to the Python/uv branch.

The following commands must work end-to-end (IR-1.2 – IR-1.4, IR-2.1 – IR-2.3):

- Install / sync deps: `uv sync`
- Run tests: `uv run pytest`
- Run the app: `uv run python -m app` (or the equivalent module entry point chosen at bootstrap)

No network access at runtime (SC-2). No GUI libraries (Tk, Qt, PyGame, etc.) — CLI only (EX-1).

## Architectural invariants (do not violate)

The system is Hexagonal (Ports & Adapters) with four patterns: Strategy, Command, Builder, Memento. In Python this maps to: ports → `typing.Protocol` (or `abc.ABC`); value objects (`ConfigVO`, `Memento`, move `Command`) → `@dataclass(frozen=True)`; Strategy → plain classes implementing the `PlayerInput` Protocol.

- `Core.*` must not import from any adapter or I/O module. The core has zero knowledge of CLI or JSON.
- Six ports exist: `GameSession`, `MoveValidator`, `LegalMoveEnumerator`, `ConfigSource` (inbound); `PlayerInput`, `StateRepository`, `PresentationOutput` (outbound). Do not introduce new ports without an ADR update.
- All state I/O is JSON via `Memento` + `Adapter.JsonStateRepo` (SC-1). No other persistence formats.
- `Bootstrap` stays procedural — no DI framework, no annotations, no reflective lookup, ≤ ~200 lines.

## Configuration is data, not constants (FR-1.2)

Board dimensions, player count, and starting-corner map live in `Core.ConfigVO`, constructed via Builder, supplied by `ConfigSource`.

- Do not write the literal `20` (board side) or `4` (player count) anywhere in `Core.*` except inside `Core.PieceCatalog`.
- `Memento` carries `ConfigVO` as a field — on reload, the engine uses the **Memento's** config, not a separately injected one. This is the single source of truth for restored games.

## Determinism contract (FR-3.4)

The Simple-AI heuristic is deterministic. Two preconditions must hold:

1. `LegalMoveEnumerator` returns moves in a fixed, sorted order. Never iterate over an unordered set/map when assembling the result.
2. Tie-break is lexicographic on `(row, column, piece ID, rotation, flip)` — applied after the two heuristic ranks (max coverage, then max new corner-touch points).

Add a regression test that loads a fixed JSON state and asserts the chosen move equals a recorded golden value.

## Performance budgets (NFR-1.x, reference laptop)

- `validateMove` ≤ 100 ms.
- `enumerateLegalMoves` ≤ 500 ms — assume anchor-bounded search over precomputed piece orientations cached in `Core.PieceCatalog`.
- JSON round-trip ≤ 200 ms.

## Git workflow (IR-1.1)

Feature branch per feature; merge to `main` via pull request; delete the branch after merge. No direct commits to `main`.

## When extending

- New player type → new adapter implementing `Port.PlayerInput`; wire in `Bootstrap`. Do not touch `Core.*`.
- New rule clarification → update `Core.RuleSet` plus the legality tests; rules are fixed per Mattel BJV44 (AMB-01), so changes must cite the rulebook.
- New config knob → extend `ConfigVO` and its Builder; thread it through `ConfigSource`; do not introduce a parallel global.
