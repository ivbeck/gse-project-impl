# Prompt 1 — Class Diagram Generation

---

You are a senior software architect.

## Architecture Context

The system is a **Blokus Classic game engine** using a **Hexagonal (Ports-and-Adapters)
architecture** with the following selected design patterns (DS-hexagonal-2):

- **Strategy** — interchangeable player decision policies (Human / Simple-AI) behind the
  `PlayerInput` outbound port. No core class knows which player type it is talking to.
- **Command** — a Move is a uniform value object that crosses the port boundary intact
  and is used for validation, application, enumeration, and JSON serialization.
- **Builder** — constructs the `ConfigVO` (board dimensions, player count,
  starting-position map) without telescoping constructors and with startup validation.
- **Memento** — whole-game snapshot for JSON round-trip without exposing core internals
  to the JSON adapter.

### Core structure (from ADR-002 / DS-hexagonal-2)

**Engine Core (no dependency on any adapter):**

- `Core.Board` — grid representation; orthogonal and diagonal neighbor checks (FR-1.4)
- `Core.PieceCatalog` — 21 pieces with precomputed orientations (FR-4.1)
- `Core.RuleSet` — BJV44 legality + first-move corner enforcement (FR-4.1, FR-4.2)
- `Core.Scoring` — pure function: remaining-squares → ranked result table (FR-4.4)
- `Core.GameSession` — inbound port: run a turn, detect termination (FR-4.3)
- `Core.ConfigVO` — immutable value object for configurable parameters (FR-1.2)

**Inbound Ports (driven by external actors into the core):**

- `Port.ConfigSource` — supplies `ConfigVO` at startup
- `Core.GameSession` (also the primary inbound port)

**Outbound Ports (driven by core outward to adapters):**

- `Port.PlayerInput` — requests a Move Command for a given turn context
- `Port.StateRepository` — persists and restores a Memento
- `Port.PresentationOutput` — renders board state and post-game prompts

**Adapters (depend on ports; core never depends on adapters):**

- `Adapter.CLI` — implements `PresentationOutput`; drives the input/output loop
- `Adapter.JsonStateRepo` — implements `StateRepository`; translates Memento ↔ JSON
- `Adapter.JsonConfigSource` — implements `ConfigSource`; reads FR-1.2 config from JSON
- `Adapter.HumanPlayer` — implements `PlayerInput` by reading from CLI (FR-3.1)
- `Adapter.SimpleAiPlayer` — implements `PlayerInput` using the FR-3.4 deterministic heuristic
- `Bootstrap` — wires all ports to their adapters using `ConfigBuilder` at startup

---

## Task

Think step-by-step:

(a) Extract entities and roles from the requirements and architecture context above.
(b) Define attributes with concrete types and visibility markers (`+`, `-`, `#`).
(c) Decide inheritance and interfaces — ports are interfaces; adapters implement them.
(d) Assign associations with multiplicities and direction labels.
(e) Sanity-check the Mermaid syntax before outputting.

Then output **ONLY valid Mermaid class diagram code**. No prose, no explanation outside
the code block.

---

## Constraints

- Use **concrete types only** — no `<Type>` placeholders.
- Do **NOT** include database tables, REST endpoints, file paths, or UI framework elements.
- Do **NOT** use generic setters — model state transitions as named methods
  (e.g., `confirmMove()`, `advanceTurn()`, not `setStatus()`).
- Use an **Enumeration** for `GameStatus` (e.g., IN_PROGRESS, FINISHED) and
  `MoveResult` (e.g., LEGAL, ILLEGAL). Do NOT also create subclasses for these.
- Do **NOT** model temporary method parameters as structural associations.
- **Start with a maximum of 8 core elements** (Core layer only) in this first pass.
  Do not include adapters yet — we will add them iteratively in the next prompt.
- For every class or interface, add an **inline Mermaid note** referencing the
  Requirement ID it satisfies (e.g., `note for Core.Board "FR-1.1, FR-1.4"`).
- For every method, add an **inline comment** with the Use Case ID and a short
  action description (e.g., `//FR-2.3 //action: check move legality before apply`).

---

## Functional Requirements

- **FR-1.1** — Implement rules of Blokus Classic: 4 players on a 20×20 board.
- **FR-1.2** — Support configurable board dimensions, player count, and starting positions
  (these are first-class inputs, not hard-coded constants).
- **FR-1.3** — Maintain accurate state of piece ownership, board occupancy, and turn
  progression at all times.
- **FR-1.4** — Enforce the Mattel BJV44 rule set: corner-touch required, orthogonal
  adjacency to own pieces prohibited, contact with different-color pieces is free,
  placed pieces are immovable.
- **FR-2.1** — Provide a minimal CLI for player interaction.
- **FR-2.2** — Support JSON load/save with full round-trip fidelity.
- **FR-2.3** — Perform a legality check before applying any move.
- **FR-2.4** — Apply a move to the board state.
- **FR-2.5** — Enumerate all legal moves for the current player.
- **FR-2.6** — Save and restore complete game state via JSON.
- **FR-2.7** — Render the board and game state in a human-readable CLI format.
- **FR-3.1** — Support a human player interacting via CLI.
- **FR-3.2** — Support a deterministic simple-AI player.
- **FR-3.3** — Both player types must sit behind a common player abstraction
  (the `PlayerInput` port).
- **FR-3.4** — The simple-AI heuristic must be deterministic (lexicographic tie-break).
- **FR-4.1** — Include the full BJV44 piece set (21 pieces) and enforce turn order.
- **FR-4.2** — Enforce first-move corner placement for each player.
- **FR-4.3** — Detect game termination by a consecutive all-pass round; then score,
  announce winner, and prompt for replay.
- **FR-4.4** — Score by remaining squares; lower score wins; ties are shared.
