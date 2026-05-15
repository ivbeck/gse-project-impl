# Architecture & Design Decision Record — Blokus Configurable Game Engine (Milestone 1)

**Document Version:** 1.0
**Status:** Proposed — for human-architect review
**Scope:** Milestone 1 (Blokus Classic, 4 players, 20×20). Milestone 2 (Blokus Duo) is *explicitly out of scope of this ADR* and is referenced only insofar as the SRS itself (FR-1.2) requires configurable game parameters.
**Authors (personas):** P1 Solution Architect · P2 Development Architect · P3 Senior Reviewing Architect
**Inputs:** [SPEC_M1.md](SPEC_M1.md), [AMBIGUITY_LOG.md](AMBIGUITY_LOG.md), [ARCHITECTURE_PROMPT_v1.md](../guidelines/ARCHITECTURE_PROMPT_v1.md)

> Reading note. This document follows the three phases of *Guideline 1 (Architecture & Design)*. Each phase is a distinct persona pass; no phase is collapsed into another. Every architectural decision traces to a requirement ID from [SPEC_M1.md](SPEC_M1.md).

---

## Phase 1 — Select an Architecture (Persona: Solution Architect)

### 1. Decision Frame

#### 1.1 Functional scope (from §2 SRS)
- Core engine: rules of Blokus Classic with 4 players on a 20×20 board (FR-1.1); configurable board dimensions, player count, starting positions (FR-1.2); accurate state of piece ownership, board occupancy, turn progression (FR-1.3); enforcement of the Mattel BJV44 rule set — corner-touch, orthogonal prohibition, free different-color contact, immovability (FR-1.4).
- Interface & state: minimal CLI (FR-2.1); JSON load/save with full round-trip (FR-2.2, FR-2.6); legality check before application (FR-2.3); move application (FR-2.4); legal-move enumeration (FR-2.5); human-readable CLI rendering (FR-2.7).
- Players: human via CLI (FR-3.1); deterministic simple-AI (FR-3.2, FR-3.4) behind a player abstraction (FR-3.3).
- Rules: full BJV44 piece set & turn order (FR-4.1); first-move corner placement (FR-4.2); termination by consecutive all-pass round, then score/announce/replay-prompt (FR-4.3); basic scoring = remaining squares, lower wins, ties shared (FR-4.4).
- Evaluation: automated rule tests (FR-5.1), evaluation harness (FR-5.2), legality-checker tests (FR-5.3), move-application tests (FR-5.4).

#### 1.2 Constraints
- Non-functional: ≤100 ms validation (NFR-1.1), ≤500 ms legal-move enumeration (NFR-1.2), ≤200 ms (de)serialization (NFR-1.3) on the reference laptop (AMB-06).
- Portability: established build tool — Java/Maven or Python/uv (NFR-2.1); identical behavior on Windows, macOS, Linux (NFR-2.2).
- Maintainability: industry-standard conventions (NFR-3.1); architectural separation of game logic from interface (NFR-3.2).
- System: JSON for all state I/O (SC-1); fully offline (SC-2); reproducible build/run scripts (SC-3).
- Infrastructure: feature-branch Git workflow (IR-1.1); build/test/run scripts (IR-1.2–1.4); dependency, test, packaging through build tool (IR-2.1–2.3).

#### 1.3 Explicit quality goals (driving the choice)
1. **Separation of concerns** — game logic must be independently testable from CLI/JSON layers (NFR-3.2, AMB-04).
2. **Testability** — ≥90 % core-logic coverage (Acceptance §5.3, FR-5.1–5.4) demands seams that let tests bypass I/O.
3. **Configurability of game parameters** — board size, player count, starting positions are first-class inputs (FR-1.2). *Note: required by the SRS itself; not driven by Milestone 2 in this ADR.*
4. **Deterministic, reproducible behavior** — AI heuristic is deterministic (FR-3.4); build/run reproducible (SC-3, IR-2.x).
5. **Performance fit** — laptop budget; must not preclude precomputed orientations or bitboard-like checks (NFR-1.x).
6. **Language neutrality** — expressible in either Java (Maven) or Python (uv) without source-level rewrite (NFR-2.1, NFR-2.2).

#### 1.4 Explicit non-goals (from §8 Exclusions and resolved ambiguities)
- No heavy GUI (EX-1).
- No strong AI (EX-2); only the prioritized heuristic of FR-3.4.
- No online multiplayer (EX-3); offline only (SC-2).
- No Blokus Duo logic, Duo board, or Duo-specific code paths in this ADR (per user direction; FR-1.2 covers only generic configurability of board/players/starts).
- No pluggable scoring framework — basic scoring is a pure function (AMB-05).
- No speculative rule DSL — the BJV44 contract is fixed (AMB-01).

### 2. Candidate Options

The three candidates are shape-distinct: a vertical-stack layered split, a core-with-adapters hub-and-spokes, and a kernel-with-plugin-modules registry. They differ in *where the engine boundary sits*, *how interface I/O attaches*, and *what is replaceable at runtime*.

#### Option A — Layered Architecture (Domain / Application / Interface / Infrastructure)
A vertical four-layer stack. The **Domain** layer owns pieces, board, rules, and pure state. The **Application** layer orchestrates use cases (apply move, enumerate moves, run turn, end game). The **Interface** layer is the CLI renderer and prompt loop. The **Infrastructure** layer provides JSON (de)serialization, file I/O, and script entry points. Dependencies flow strictly downward. Configuration is a plain DTO read at the Application layer (FR-1.2). The Domain layer has no knowledge of CLI or JSON, satisfying NFR-3.2.

#### Option B — Hexagonal / Ports-and-Adapters
A pure **engine core** (rules, board, pieces, state, scoring) is surrounded by **inbound ports** (e.g., `GameSession`, `MoveValidator`, `LegalMoveEnumerator`, `Scorer`) and **outbound ports** (e.g., `StateRepository`, `PlayerInput`, `PresentationOutput`). Adapters implement these ports: a CLI adapter for input/output (FR-2.1, FR-2.7), a JSON adapter for state I/O (FR-2.2, FR-2.6, SC-1), and player adapters for human (FR-3.1) and simple-AI (FR-3.2). The engine has zero dependency on adapters; adapters depend on engine interfaces. Configuration is supplied via an outbound port resolved at startup (FR-1.2).

#### Option C — Plugin-based / Rule-Module Architecture
A small **engine kernel** owns only the board representation, turn loop, and dispatch. Rule logic, scoring, and player strategies are loaded as **modules** through a registry (e.g., a `RuleSet`, a `ScoringRule`, a `PlayerStrategy`). The kernel emits events; modules subscribe. Configuration files (SC-1, FR-1.2) name which modules to load. New variants (e.g., alternative scoring or a different first-move rule) require only writing a new module — no kernel change. The kernel is intentionally rule-agnostic and could in principle host non-Blokus games.

### 3. Critique — Comparison Table (Phase 1, do not yet pick a winner)

Scale: 1 (poor) – 5 (excellent). Each cell carries a one-line justification.

| Criterion | A. Layered | B. Hexagonal | C. Plugin/Module |
|---|---|---|---|
| **Maintainability (NFR-3.1, NFR-3.2)** | **4** — familiar shape; juniors onboard quickly; some risk of leakage between layers. | **5** — explicit ports make boundaries unambiguous; adapter swaps don't touch core. | **3** — registry indirection raises the cost of "follow the code". |
| **Scalability (perf, NFR-1.1–1.3)** | **4** — direct calls; no extra indirection on hot path. | **4** — port calls are direct interface dispatches; no overhead worth mentioning on laptop budget. | **3** — event/registry dispatch adds overhead and complicates profiling. |
| **Extensibility — cost of adding *configurable* parameters per FR-1.2** | **3** — config DTO at Application layer is straightforward but board/player constants tend to leak into Domain types. | **5** — config arrives through a port; engine receives validated config as a single value object. | **5** — config selects which modules are mounted; trivially extensible by construction. |
| **Reliability (FR-1.4, FR-4.x correctness)** | **4** — fewer moving parts; bugs are localized to a layer. | **5** — engine core is testable in isolation, so rule bugs are caught with no I/O scaffolding. | **3** — distributed rules across modules raise integration-error risk; harder to prove BJV44 conformance. |
| **Migration cost (from no code today)** | **5** — least friction to start. | **4** — requires defining port interfaces up front but they are small in M1. | **2** — registry, plugin discovery, and event bus are work that doesn't ship a feature. |
| **Reversibility** | **4** — refactoring into ports later is mechanical. | **3** — once committed, ports become a contract; reversing into a flat structure is awkward. | **2** — plugin contracts are sticky; collapsing modules back is costly. |
| **Testability (FR-5.x, ≥90 % coverage)** | **4** — Domain layer testable; CLI tests need a harness. | **5** — engine core is testable without CLI/JSON; adapters tested in isolation. | **3** — needs a fake registry per test; setup overhead is real. |
| **Fit to FR-1.2 (configurable engine)** | **3** — works, but config tends to be passed positionally and tempts hard-coded constants. | **5** — config is a value object behind a port; substitution is trivial. | **5** — config *is* the wiring. |
| **Total (informative)** | **31** | **36** | **26** |

#### 3.1 Trade-offs and Risks per Candidate

- **Option A (Layered).** The lowest-friction choice for a one-semester academic deliverable; the layered shape is the default mental model for the team and the conventions of both Java/Maven and Python/uv. *Risk:* layer leakage — particularly hard-coding `20` or `4` in Domain types — which would directly violate FR-1.2; mitigated by reviewer discipline but not by structure. Reversibility into ports later is mechanical, which keeps options open.
- **Option B (Hexagonal).** Pays a small up-front cost (defining ports) and earns it back twice: in test isolation (FR-5.1–5.4 against an engine with no CLI/JSON loaded) and in clean substitution of player and persistence implementations (FR-3.3, FR-2.2, FR-2.6). *Risk:* over-engineering port surfaces — solved by keeping ports few and small in M1; the SRS only needs ~5 of them. Performance impact under the laptop budget (NFR-1.x) is negligible.
- **Option C (Plugin/Module).** Maximally flexible and the most "elegant" — but the SRS gives us *zero* in-scope variability that justifies a plugin contract: the rule set is fixed (AMB-01), the scoring scheme is fixed and simple (AMB-05), the heuristic is fixed (AMB-02), and Milestone 2 is *out of scope of this ADR*. The flexibility purchased here is paid for in registry indirection, event wiring, and harder-to-trace bugs — a net loss against FR-5.1 / FR-1.4 reliability and the one-semester budget.

### 4. ADRs

#### ADR-001: Layered Architecture (option, Rejected in favor of ADR-002)

```
ADR-001: Layered Architecture (Domain / Application / Interface / Infrastructure)
Status: Proposed (option) — Rejected in favor of ADR-002
Context: Drivers — clean separation of game logic and interface (NFR-3.2); ≥90% core test coverage (FR-5.x); JSON I/O (SC-1, FR-2.2, FR-2.6); configurable parameters (FR-1.2); language-neutral build (NFR-2.1, NFR-2.2); offline reproducibility (SC-2, SC-3).
Decision: Adopt a four-layer top-down stack — Domain (rules, board, pieces, state), Application (use cases / orchestration), Interface (CLI), Infrastructure (JSON, scripts) — with strict downward dependencies.
Consequences:
  Positive:
   - Familiar shape; lowest onboarding cost.
   - Straightforward in both Java/Maven and Python/uv (NFR-2.1).
   - Domain remains testable in isolation (FR-5.x).
  Negative:
   - No structural defense against Interface/Infrastructure types leaking into Domain (NFR-3.2 risk).
   - Configurable parameters (FR-1.2) tend to drift into Domain constants unless reviewed.
   - No dedicated seam for swapping player implementations (FR-3.3) beyond a plain interface.
  Neutral:
   - Layers can be reorganized into ports later if needed.
Quality Attributes Addressed:
   - Maintainability — clear, conventional layering (NFR-3.1).
   - Testability — Domain has no I/O dependencies (FR-5.x).
   - Portability — pure layering trivial in Java/Python (NFR-2.2).
Open Questions / Assumptions:
   - Assumes reviewers will catch Domain-layer constant leaks during PR (IR-1.1).
   - Assumes the team accepts heavier convention discipline in place of structural enforcement.
```

#### ADR-002: Hexagonal / Ports-and-Adapters Architecture (option — *Accepted as final*)

```
ADR-002: Hexagonal / Ports-and-Adapters Architecture
Status: Accepted
Context: Drivers — clean separation of engine logic from CLI and JSON (NFR-3.2, AMB-04); ≥90% core test coverage (FR-5.x); pluggable player implementations (FR-3.3, FR-3.1, FR-3.2); state round-trip via JSON (FR-2.2, FR-2.6, SC-1); configurable game parameters as first-class input (FR-1.2); deterministic, reproducible behavior (FR-3.4, SC-3, IR-2.x); language-neutral, Java-or-Python (NFR-2.1, NFR-2.2).
Decision: Adopt a Hexagonal (Ports-and-Adapters) architecture: a pure engine core (rules, board, pieces, state, scoring) is surrounded by a small set of inbound and outbound ports, with adapters for CLI presentation, JSON state I/O, and player input — human and simple-AI.
Consequences:
  Positive:
   - Engine core has zero dependency on CLI or JSON, structurally enforcing NFR-3.2.
   - Core is testable without I/O scaffolding (FR-5.1–5.4), simplifying ≥90% coverage.
   - Player implementations (FR-3.3) and persistence (FR-2.2/2.6) are adapter swaps.
   - Configuration enters through a single port → FR-1.2 satisfied by construction.
   - Maps cleanly to both Java (interfaces) and Python (Protocols/abstract base classes), preserving NFR-2.1/2.2.
  Negative:
   - Requires defining ~5 port interfaces before functional code; small up-front design tax.
   - Risk of over-engineering port surfaces (e.g., inventing ports for needs the SRS does not state).
  Neutral:
   - Ports do not by themselves dictate performance characteristics; NFR-1.x is governed by representation choices in the core, not by the architecture.
Quality Attributes Addressed:
   - Separation of concerns (NFR-3.2): structural, not conventional.
   - Testability (FR-5.x): mockable adapters; core has no I/O.
   - Configurability (FR-1.2): configuration is a value object behind an inbound port.
   - Maintainability (NFR-3.1): explicit boundaries; small ports.
   - Portability (NFR-2.1, NFR-2.2): port/adapter pattern is language-agnostic.
Open Questions / Assumptions:
   - Assumes ≤6 ports in M1: GameSession (inbound), MoveValidator (inbound), LegalMoveEnumerator (inbound), PlayerInput (outbound), StateRepository (outbound), PresentationOutput (outbound). To be confirmed in Phase 2.
   - Assumes the team accepts a brief upfront design step before code.
Rejected Alternatives: see ADR-001, ADR-003 (rationales recorded in the final ADR below).
```

#### ADR-003: Plugin / Rule-Module Architecture (option, Rejected)

```
ADR-003: Plugin-Based / Rule-Module Architecture
Status: Proposed (option) — Rejected
Context: Same drivers as ADR-001/002, with additional emphasis on whether a plugin contract is justified by in-scope variability.
Decision: Adopt a small engine kernel with a registry of pluggable rule, scoring, and player modules selected by configuration.
Consequences:
  Positive:
   - Highest theoretical flexibility — every rule, scoring scheme, and strategy is replaceable without kernel change.
   - Configuration trivially controls behavior (FR-1.2).
  Negative:
   - The SRS in-scope rule set is fixed (AMB-01); scoring is fixed (AMB-05); heuristic is fixed (AMB-02). Plugin flexibility purchases nothing the SRS asks for.
   - Registry/event indirection raises cost of "follow the code" and complicates reliability proofs for FR-1.4.
   - Up-front cost (registry, discovery, event wiring) is not recoverable in the one-semester academic budget.
  Neutral:
   - Could be retro-fitted onto a hexagonal core later, if and when variability appears.
Quality Attributes Addressed:
   - Extensibility — at a cost.
   - Configurability (FR-1.2) — but the same is achieved more simply in ADR-002.
Open Questions / Assumptions:
   - No in-scope requirement justifies a plugin contract beyond what a port already provides.
```

#### ADR-FINAL (Phase 1): Adopt the Hexagonal Architecture

```
ADR-FINAL-P1: Adopt Hexagonal / Ports-and-Adapters as the Milestone-1 architecture
Status: Accepted (Phase 1 close; will be superseded by ADR-FINAL-P2 at end of Phase 2)
Context: The Milestone-1 SRS requires structural separation of game logic and interface (NFR-3.2, AMB-04), ≥90% core coverage (Acceptance §5.3, FR-5.x), JSON state round-trip (FR-2.2, FR-2.6, SC-1), configurable game parameters (FR-1.2), a clean player abstraction (FR-3.3), and language-neutral execution on Java/Maven or Python/uv (NFR-2.1, NFR-2.2). The rule set, scoring, and AI heuristic are fixed (AMB-01, AMB-02, AMB-05), so flexibility is needed at the *interface* (CLI, JSON, player I/O, configuration), not in the rules.
Decision: Implement the engine as a Hexagonal (Ports-and-Adapters) system — a pure engine core surrounded by inbound and outbound ports, with adapters for CLI, JSON, configuration, and players (human + simple-AI).
Consequences:
  Positive:
   - Structural enforcement of NFR-3.2.
   - Core is independently testable (FR-5.x).
   - FR-1.2 satisfied through a configuration port; FR-3.3 through a PlayerInput port; FR-2.2/2.6 through a StateRepository port.
   - Implementable identically in Java and Python (NFR-2.1, NFR-2.2).
  Negative:
   - Small up-front design step to define the ports.
   - Risk of port-surface bloat — controlled by keeping the M1 port set ≤6.
  Neutral:
   - Performance characteristics depend on representation choices inside the core, not on the port boundary.
Quality Attributes Addressed:
   - Separation of concerns, testability, configurability, maintainability, portability — see ADR-002.
Open Questions / Assumptions:
   - Port count and exact signatures finalized in Phase 2.
   - Internal representation (e.g., precomputed piece orientations) for NFR-1.x deferred to Phase 2.
Rejected Alternatives:
   - ADR-001 (Layered): functionally adequate but provides no structural defense for NFR-3.2 and no first-class seam for FR-3.3 or FR-1.2 — relies on convention rather than structure.
   - ADR-003 (Plugin/Rule-Module): in-scope variability is too small to justify a plugin contract; the rule set (AMB-01), scoring (AMB-05), and heuristic (AMB-02) are fixed; the registry/event machinery is unrecoverable cost in a one-semester academic project.
```

---

## Phase 2 — Refine into a Concrete Design (Persona: Development Architect)

### 5. Restated Inputs

- **LLM role.** Development Architect.
- **Binding context.** ADR-FINAL-P1 above (Hexagonal). All design solutions are to be evaluated *under* this architectural choice. Per the prompt's diversity rule, designs for Options A and C are still produced — but as comparators, not candidates for adoption.
- **Required code qualities.**
  - **Extensibility** — limited to FR-1.2 (board dimensions, player count, starting positions). *Not driven by Duo in this ADR.*
  - **Maintainability** — industry conventions (NFR-3.1), separation of game logic from interface (NFR-3.2).
  - **Performance** — within NFR-1.1 (≤100 ms validation), NFR-1.2 (≤500 ms enumeration), NFR-1.3 (≤200 ms (de)serialization).
  - **Testability** — ≥90 % core-logic coverage (Acceptance §5.3, FR-5.1–5.4).
  - **Configurability** — FR-1.2 as a value object behind an inbound port.
  - **Reproducibility / determinism** — SC-3, IR-2.x; AI heuristic deterministic (FR-3.4).

### 6. Design Solutions (3 × 3 = 9)

Each solution is presented as strict JSON and bound to one of the three architectures. Pattern names follow GoF nomenclature where applicable.

#### 6.1 Designs for Option A — Layered

```json
{
  "architecture_option": "Layered",
  "solution_id": "DS-layered-1",
  "patterns": [
    {
      "name": "Strategy",
      "problem_solved": "Make the player decision policy interchangeable between Human and Simple-AI without touching the turn loop.",
      "rationale": "FR-3.3 requires an abstraction layer for players; Strategy is the minimal pattern that supplies it. State or Template Method would over-fit the fixed turn structure.",
      "interactions": ["Command", "Facade"]
    },
    {
      "name": "Command",
      "problem_solved": "Represent a move as a value object that can be validated, applied, logged, and serialized uniformly.",
      "rationale": "FR-2.3/FR-2.4/FR-2.5 all act on the same notion of a move; encoding it as a Command keeps validation and application symmetric. Memento is a sibling — used for state snapshots, not move dispatch.",
      "interactions": ["Strategy", "Facade"]
    },
    {
      "name": "Facade",
      "problem_solved": "Give the CLI layer a single Application-layer entry point hiding rule, board, and turn details.",
      "rationale": "Keeps the Interface layer from reaching into Domain types and protects NFR-3.2. Chosen over Mediator because we have one client (CLI) not many peers.",
      "interactions": ["Strategy", "Command"]
    }
  ],
  "components": [
    {"name": "Domain.Board", "responsibility": "Grid state and same-color adjacency queries.", "depends_on": []},
    {"name": "Domain.Piece", "responsibility": "Piece geometry, orientations, immovability after placement.", "depends_on": []},
    {"name": "Domain.Rules", "responsibility": "BJV44 enforcement (corner-touch, ortho-prohibition, first-move corner).", "depends_on": ["Domain.Board", "Domain.Piece"]},
    {"name": "Application.MoveService", "responsibility": "Validate, apply, enumerate moves.", "depends_on": ["Domain.Rules", "Domain.Board"]},
    {"name": "Application.GameLoop", "responsibility": "Turn order, pass detection, termination.", "depends_on": ["Application.MoveService"]},
    {"name": "Interface.CLI", "responsibility": "Render state, accept input, post-game prompt.", "depends_on": ["Application.GameLoop"]},
    {"name": "Infrastructure.JsonIO", "responsibility": "Serialize/deserialize state per SC-1.", "depends_on": ["Domain.Board", "Domain.Piece"]}
  ],
  "priority": "Medium",
  "complexity": "2",
  "addresses_requirements": ["FR-1.1", "FR-1.3", "FR-1.4", "FR-2.1", "FR-2.3", "FR-2.4", "FR-2.5", "FR-2.7", "FR-3.1", "FR-3.2", "FR-3.3", "FR-4.1", "FR-4.2", "FR-4.3", "FR-4.4", "NFR-3.2"]
}
```

```json
{
  "architecture_option": "Layered",
  "solution_id": "DS-layered-2",
  "patterns": [
    {
      "name": "Template Method",
      "problem_solved": "Fix the turn-cycle skeleton (begin-turn → request-move → validate → apply → check-pass → check-end) while letting subclasses customize 'request-move' for Human vs AI.",
      "rationale": "The turn cycle is fixed by FR-4.1–4.3; only the move-request step varies by player. Template Method captures this precisely; Strategy would be acceptable but pushes the loop structure outward.",
      "interactions": ["Memento", "Builder"]
    },
    {
      "name": "Memento",
      "problem_solved": "Capture/restore game state for JSON round-trip (SC-1, FR-2.2/2.6) without exposing Domain internals.",
      "rationale": "Memento is the textbook fit for round-trip serialization across a boundary. A bare DTO would force the Domain to expose its fields directly, weakening NFR-3.2.",
      "interactions": ["Template Method"]
    },
    {
      "name": "Builder",
      "problem_solved": "Construct a configured initial game state from the FR-1.2 parameter set without a sprawling constructor.",
      "rationale": "FR-1.2 has multiple optional/grouped parameters (dimensions, count, starts); Builder beats overloaded constructors or telescoping factory functions, and reads naturally in both Java and Python.",
      "interactions": ["Template Method"]
    }
  ],
  "components": [
    {"name": "Domain.Board", "responsibility": "Grid state.", "depends_on": []},
    {"name": "Domain.PieceLibrary", "responsibility": "21-piece catalog and orientations.", "depends_on": []},
    {"name": "Domain.Rules", "responsibility": "BJV44 enforcement.", "depends_on": ["Domain.Board", "Domain.PieceLibrary"]},
    {"name": "Application.TurnTemplate", "responsibility": "Template-method turn cycle.", "depends_on": ["Domain.Rules"]},
    {"name": "Application.GameBuilder", "responsibility": "Configured game construction (FR-1.2).", "depends_on": ["Domain.Board", "Domain.PieceLibrary"]},
    {"name": "Application.StateMemento", "responsibility": "Encapsulated snapshot for JSON round-trip.", "depends_on": ["Domain.Board", "Domain.PieceLibrary"]},
    {"name": "Interface.CLI", "responsibility": "Rendering + prompts.", "depends_on": ["Application.TurnTemplate"]},
    {"name": "Infrastructure.JsonIO", "responsibility": "JSON encode/decode of mementos.", "depends_on": ["Application.StateMemento"]}
  ],
  "priority": "Medium",
  "complexity": "3",
  "addresses_requirements": ["FR-1.1", "FR-1.2", "FR-1.3", "FR-1.4", "FR-2.2", "FR-2.6", "FR-4.1", "FR-4.2", "FR-4.3", "FR-4.4", "NFR-3.2", "SC-1"]
}
```

```json
{
  "architecture_option": "Layered",
  "solution_id": "DS-layered-3",
  "patterns": [
    {
      "name": "Observer",
      "problem_solved": "Notify CLI rendering and a future logger of state changes without coupling the Domain to either.",
      "rationale": "Decouples Domain from Interface (NFR-3.2). Chosen over passing the CLI as a callback because Observer makes the subscriber list explicit and supports multiple listeners (e.g., a test recorder).",
      "interactions": ["Iterator", "Singleton"]
    },
    {
      "name": "Iterator",
      "problem_solved": "Enumerate legal moves lazily (FR-2.5) without materializing the full set when the AI only needs the best one.",
      "rationale": "Lazy enumeration helps NFR-1.2 by allowing short-circuit evaluation in the heuristic. A returned list would always be O(N) and would waste effort.",
      "interactions": ["Observer"]
    },
    {
      "name": "Singleton",
      "problem_solved": "Provide a single shared piece-orientation cache (precomputed rotations/flips).",
      "rationale": "The piece catalog is immutable and shared by all players. Singleton is the simplest correct choice and aids NFR-1.1/1.2 by amortizing orientation cost.",
      "interactions": ["Observer", "Iterator"]
    }
  ],
  "components": [
    {"name": "Domain.Board", "responsibility": "Grid + change notifications.", "depends_on": []},
    {"name": "Domain.PieceCatalog", "responsibility": "Singleton orientation cache.", "depends_on": []},
    {"name": "Domain.Rules", "responsibility": "Legality checks.", "depends_on": ["Domain.Board", "Domain.PieceCatalog"]},
    {"name": "Application.LegalMoveIterator", "responsibility": "Lazy enumerator.", "depends_on": ["Domain.Rules"]},
    {"name": "Application.GameLoop", "responsibility": "Turn loop + observers.", "depends_on": ["Application.LegalMoveIterator"]},
    {"name": "Interface.CLIObserver", "responsibility": "Render on notify.", "depends_on": ["Application.GameLoop"]},
    {"name": "Infrastructure.JsonIO", "responsibility": "Round-trip state.", "depends_on": ["Domain.Board"]}
  ],
  "priority": "Low",
  "complexity": "4",
  "addresses_requirements": ["FR-1.4", "FR-2.5", "FR-2.7", "NFR-1.1", "NFR-1.2", "NFR-3.2"]
}
```

#### 6.2 Designs for Option B — Hexagonal (the selected architecture)

```json
{
  "architecture_option": "Hexagonal",
  "solution_id": "DS-hexagonal-1",
  "patterns": [
    {
      "name": "Strategy",
      "problem_solved": "Plug a Human or Simple-AI policy behind the PlayerInput outbound port without the core learning anything about either.",
      "rationale": "FR-3.3 demands a player abstraction; Strategy is the cleanest expression in a hexagonal layout (each implementation is an adapter). State would be wrong — the player isn't a state machine.",
      "interactions": ["Factory Method", "Command"]
    },
    {
      "name": "Factory Method",
      "problem_solved": "Construct the configured game (FR-1.2) and the wired-up port adapters at startup.",
      "rationale": "Factory Method beats Abstract Factory here because we don't have *families* of adapters — only one Human adapter, one Simple-AI adapter, one CLI adapter, one JSON adapter. Builder is reserved for richer config in DS-hexagonal-2.",
      "interactions": ["Strategy"]
    },
    {
      "name": "Command",
      "problem_solved": "Represent a move as a value object that crosses the port boundary intact (validation in, application in, JSON out).",
      "rationale": "A Command carries the data needed for FR-2.3 (validate), FR-2.4 (apply), FR-2.5 (enumerate as commands), and FR-2.6 (serialize). Memento is reserved for whole-state snapshots, not moves.",
      "interactions": ["Strategy"]
    }
  ],
  "components": [
    {"name": "Core.Board", "responsibility": "Grid representation; same-color adjacency checks.", "depends_on": []},
    {"name": "Core.PieceCatalog", "responsibility": "21 pieces × precomputed orientations.", "depends_on": []},
    {"name": "Core.RuleSet", "responsibility": "BJV44 legality + first-move corner.", "depends_on": ["Core.Board", "Core.PieceCatalog"]},
    {"name": "Core.GameSession (inbound port)", "responsibility": "Start, take turn, end, score.", "depends_on": ["Core.RuleSet"]},
    {"name": "Port.PlayerInput (outbound)", "responsibility": "Request a move command.", "depends_on": []},
    {"name": "Port.StateRepository (outbound)", "responsibility": "Save/load whole state.", "depends_on": []},
    {"name": "Port.PresentationOutput (outbound)", "responsibility": "Emit human-readable state and prompts.", "depends_on": []},
    {"name": "Adapter.CLI", "responsibility": "Implements PresentationOutput + drives input loop.", "depends_on": ["Port.PresentationOutput", "Core.GameSession"]},
    {"name": "Adapter.JsonStateRepo", "responsibility": "Implements StateRepository over JSON.", "depends_on": ["Port.StateRepository"]},
    {"name": "Adapter.HumanPlayer", "responsibility": "Strategy impl reading from CLI.", "depends_on": ["Port.PlayerInput"]},
    {"name": "Adapter.SimpleAiPlayer", "responsibility": "Deterministic FR-3.4 heuristic.", "depends_on": ["Port.PlayerInput", "Core.GameSession"]}
  ],
  "priority": "High",
  "complexity": "3",
  "addresses_requirements": ["FR-1.1", "FR-1.2", "FR-1.3", "FR-1.4", "FR-2.1", "FR-2.2", "FR-2.3", "FR-2.4", "FR-2.5", "FR-2.6", "FR-2.7", "FR-3.1", "FR-3.2", "FR-3.3", "FR-3.4", "FR-4.1", "FR-4.2", "FR-4.3", "FR-4.4", "NFR-3.2", "SC-1"]
}
```

```json
{
  "architecture_option": "Hexagonal",
  "solution_id": "DS-hexagonal-2",
  "patterns": [
    {
      "name": "Strategy",
      "problem_solved": "Interchangeable player decision policies behind PlayerInput.",
      "rationale": "Same rationale as DS-hexagonal-1; carried forward because no alternative is competitive for FR-3.3.",
      "interactions": ["Command", "Builder", "Memento"]
    },
    {
      "name": "Command",
      "problem_solved": "Move as a uniform value object across validation, application, enumeration, and JSON I/O.",
      "rationale": "Symmetry between FR-2.3, FR-2.4, FR-2.5, FR-2.6.",
      "interactions": ["Strategy", "Memento"]
    },
    {
      "name": "Builder",
      "problem_solved": "Construct an FR-1.2 configuration value object — board dimensions, player count, starting-position map — without telescoping constructors and with validation per FR-4.2.",
      "rationale": "Multiple optional/grouped fields make Builder the right fit; chosen over Factory Method (used in DS-hexagonal-1) because the *config object itself* — not the engine — is what needs assembly here.",
      "interactions": ["Strategy", "Memento"]
    },
    {
      "name": "Memento",
      "problem_solved": "Whole-game snapshot for JSON round-trip (FR-2.2, FR-2.6, SC-1) without exposing core internals.",
      "rationale": "Memento preserves NFR-3.2 by handing the JSON adapter an opaque snapshot rather than core types.",
      "interactions": ["Strategy", "Command", "Builder"]
    }
  ],
  "components": [
    {"name": "Core.Board", "responsibility": "Grid; ortho/diag neighbor checks (FR-1.4).", "depends_on": []},
    {"name": "Core.PieceCatalog", "responsibility": "Precomputed orientations of 21 pieces.", "depends_on": []},
    {"name": "Core.RuleSet", "responsibility": "BJV44 legality + first-move corner (FR-4.1–4.2).", "depends_on": ["Core.Board", "Core.PieceCatalog"]},
    {"name": "Core.Scoring", "responsibility": "Pure function: remaining-squares → ranked table (FR-4.4).", "depends_on": []},
    {"name": "Core.GameSession (inbound port)", "responsibility": "Run a turn, detect termination (FR-4.3).", "depends_on": ["Core.RuleSet", "Core.Scoring"]},
    {"name": "Core.ConfigVO", "responsibility": "Immutable value object for FR-1.2 parameters.", "depends_on": []},
    {"name": "Port.ConfigSource (inbound)", "responsibility": "Supply Core.ConfigVO at startup.", "depends_on": ["Core.ConfigVO"]},
    {"name": "Port.PlayerInput (outbound)", "responsibility": "Request a move Command for a given turn context.", "depends_on": []},
    {"name": "Port.StateRepository (outbound)", "responsibility": "Persist/restore a Memento.", "depends_on": []},
    {"name": "Port.PresentationOutput (outbound)", "responsibility": "Render state + post-game prompt (FR-2.7, FR-4.3).", "depends_on": []},
    {"name": "Adapter.CLI", "responsibility": "PresentationOutput + drives the loop.", "depends_on": ["Port.PresentationOutput"]},
    {"name": "Adapter.JsonStateRepo", "responsibility": "Memento ⇄ JSON.", "depends_on": ["Port.StateRepository"]},
    {"name": "Adapter.JsonConfigSource", "responsibility": "Read FR-1.2 config from JSON or defaults.", "depends_on": ["Port.ConfigSource"]},
    {"name": "Adapter.HumanPlayer", "responsibility": "PlayerInput reading from CLI (FR-3.1).", "depends_on": ["Port.PlayerInput"]},
    {"name": "Adapter.SimpleAiPlayer", "responsibility": "PlayerInput using FR-3.4 heuristic.", "depends_on": ["Port.PlayerInput", "Core.GameSession"]},
    {"name": "Bootstrap", "responsibility": "Wire ports to adapters using ConfigBuilder.", "depends_on": ["Core.ConfigVO", "Adapter.CLI", "Adapter.JsonStateRepo", "Adapter.JsonConfigSource", "Adapter.HumanPlayer", "Adapter.SimpleAiPlayer"]}
  ],
  "priority": "High",
  "complexity": "4",
  "addresses_requirements": ["FR-1.1", "FR-1.2", "FR-1.3", "FR-1.4", "FR-2.1", "FR-2.2", "FR-2.3", "FR-2.4", "FR-2.5", "FR-2.6", "FR-2.7", "FR-3.1", "FR-3.2", "FR-3.3", "FR-3.4", "FR-4.1", "FR-4.2", "FR-4.3", "FR-4.4", "NFR-1.1", "NFR-1.2", "NFR-1.3", "NFR-3.2", "SC-1", "SC-3", "IR-2.1", "IR-2.2", "IR-2.3"]
}
```

```json
{
  "architecture_option": "Hexagonal",
  "solution_id": "DS-hexagonal-3",
  "patterns": [
    {
      "name": "Observer",
      "problem_solved": "Push state-change events from the core out to CLI rendering and an evaluation-harness recorder (FR-5.2).",
      "rationale": "Observer cleanly serves two listeners (CLI + harness) without coupling the core to either. Chosen over direct callbacks because the listener set is plural.",
      "interactions": ["Strategy", "Command"]
    },
    {
      "name": "Strategy",
      "problem_solved": "Pluggable player policies behind PlayerInput.",
      "rationale": "Carried forward; no alternative is competitive for FR-3.3.",
      "interactions": ["Observer"]
    },
    {
      "name": "Command",
      "problem_solved": "Uniform move object for validate/apply/enumerate.",
      "rationale": "Carried forward for FR-2.3/2.4/2.5 symmetry.",
      "interactions": ["Observer", "Strategy"]
    }
  ],
  "components": [
    {"name": "Core.Board", "responsibility": "Grid + emits change events.", "depends_on": []},
    {"name": "Core.RuleSet", "responsibility": "BJV44 legality.", "depends_on": ["Core.Board"]},
    {"name": "Core.GameSession (inbound port)", "responsibility": "Drive turns and termination.", "depends_on": ["Core.RuleSet"]},
    {"name": "Port.Subscriber (outbound)", "responsibility": "Receive state-change events.", "depends_on": []},
    {"name": "Port.PlayerInput (outbound)", "responsibility": "Request a move.", "depends_on": []},
    {"name": "Adapter.CLI", "responsibility": "Subscriber + input.", "depends_on": ["Port.Subscriber", "Port.PlayerInput"]},
    {"name": "Adapter.EvalHarness", "responsibility": "Records events for FR-5.2.", "depends_on": ["Port.Subscriber"]},
    {"name": "Adapter.SimpleAiPlayer", "responsibility": "FR-3.4 heuristic.", "depends_on": ["Port.PlayerInput"]}
  ],
  "priority": "Medium",
  "complexity": "4",
  "addresses_requirements": ["FR-1.3", "FR-1.4", "FR-2.3", "FR-2.4", "FR-2.5", "FR-2.7", "FR-3.1", "FR-3.2", "FR-3.3", "FR-3.4", "FR-5.1", "FR-5.2", "NFR-3.2"]
}
```

#### 6.3 Designs for Option C — Plugin / Rule-Module

```json
{
  "architecture_option": "Plugin",
  "solution_id": "DS-plugin-1",
  "patterns": [
    {
      "name": "Chain of Responsibility",
      "problem_solved": "Decompose legality into independently registered checks (first-move-corner → ortho-prohibition → corner-touch → immovability).",
      "rationale": "Lets each rule be a module; failures short-circuit. Chosen over a monolithic checker for plugin-style decomposition.",
      "interactions": ["Abstract Factory", "Strategy"]
    },
    {
      "name": "Abstract Factory",
      "problem_solved": "Manufacture coordinated module families (rule chain + scoring + start-position policy) consistent with a configuration.",
      "rationale": "When multiple sibling modules must be consistent, Abstract Factory beats Factory Method.",
      "interactions": ["Chain of Responsibility", "Strategy"]
    },
    {
      "name": "Strategy",
      "problem_solved": "Player policies as modules.",
      "rationale": "Same justification as in DS-hexagonal-1.",
      "interactions": ["Chain of Responsibility", "Abstract Factory"]
    }
  ],
  "components": [
    {"name": "Kernel.Board", "responsibility": "Grid + dispatch.", "depends_on": []},
    {"name": "Kernel.Registry", "responsibility": "Resolve modules from config.", "depends_on": []},
    {"name": "Module.RuleChain", "responsibility": "Chain-of-responsibility checks.", "depends_on": ["Kernel.Board"]},
    {"name": "Module.Scoring", "responsibility": "Pure function FR-4.4.", "depends_on": []},
    {"name": "Module.PlayerStrategy", "responsibility": "FR-3.x player module.", "depends_on": ["Kernel.Board"]},
    {"name": "Interface.CLI", "responsibility": "Frontend.", "depends_on": ["Kernel.Registry"]},
    {"name": "Infrastructure.JsonIO", "responsibility": "State (de)ser.", "depends_on": ["Kernel.Board"]}
  ],
  "priority": "Low",
  "complexity": "5",
  "addresses_requirements": ["FR-1.2", "FR-1.4", "FR-3.3", "FR-3.4", "FR-4.4", "NFR-3.2"]
}
```

```json
{
  "architecture_option": "Plugin",
  "solution_id": "DS-plugin-2",
  "patterns": [
    {
      "name": "Observer (Pub/Sub kernel)",
      "problem_solved": "Modules react to kernel events without the kernel knowing them.",
      "rationale": "Required by a plugin design but adds wiring that isn't needed for in-scope SRS variability.",
      "interactions": ["Strategy", "Decorator"]
    },
    {
      "name": "Decorator",
      "problem_solved": "Layer optional checks (e.g., debug logging) on top of the rule chain.",
      "rationale": "Plugin shape encourages stacking — Decorator gives orderable composition; chosen over inheritance to avoid an exploding class tree.",
      "interactions": ["Observer"]
    },
    {
      "name": "Strategy",
      "problem_solved": "Player module.",
      "rationale": "Carried forward.",
      "interactions": ["Observer", "Decorator"]
    }
  ],
  "components": [
    {"name": "Kernel.EventBus", "responsibility": "Pub/sub.", "depends_on": []},
    {"name": "Kernel.Board", "responsibility": "Grid.", "depends_on": ["Kernel.EventBus"]},
    {"name": "Module.RuleChain", "responsibility": "Legality.", "depends_on": ["Kernel.EventBus"]},
    {"name": "Module.LoggingDecorator", "responsibility": "Optional log wrapper.", "depends_on": ["Module.RuleChain"]},
    {"name": "Module.PlayerStrategy", "responsibility": "Player policy.", "depends_on": ["Kernel.EventBus"]}
  ],
  "priority": "Low",
  "complexity": "5",
  "addresses_requirements": ["FR-1.2", "FR-1.4", "FR-3.3", "NFR-3.2"]
}
```

```json
{
  "architecture_option": "Plugin",
  "solution_id": "DS-plugin-3",
  "patterns": [
    {
      "name": "Prototype",
      "problem_solved": "Spawn module instances per game from registered prototypes.",
      "rationale": "Useful in plugin systems; not in scope for the SRS.",
      "interactions": ["Strategy", "Mediator"]
    },
    {
      "name": "Mediator",
      "problem_solved": "Coordinate plugin modules without N×M direct links.",
      "rationale": "Helpful only once module count is large — not the case in M1.",
      "interactions": ["Prototype", "Strategy"]
    },
    {
      "name": "Strategy",
      "problem_solved": "Player module.",
      "rationale": "Carried forward.",
      "interactions": ["Prototype", "Mediator"]
    }
  ],
  "components": [
    {"name": "Kernel.Mediator", "responsibility": "Coordinate modules.", "depends_on": []},
    {"name": "Kernel.PrototypeRegistry", "responsibility": "Module spawn.", "depends_on": []},
    {"name": "Module.RuleSet", "responsibility": "Legality.", "depends_on": ["Kernel.Mediator"]},
    {"name": "Module.PlayerStrategy", "responsibility": "Player policy.", "depends_on": ["Kernel.Mediator"]}
  ],
  "priority": "Low",
  "complexity": "5",
  "addresses_requirements": ["FR-1.2", "FR-3.3", "NFR-3.2"]
}
```

### 7. Human-Review Checklist

For each design, four checks: (a) SRS misinterpretation, (b) over-engineering bias, (c) wrong Blokus-rules assumption, (d) cost vs one-semester academic deliverable.

| Solution | (a) SRS misinterpret | (b) Over-engineering | (c) Rule assumption | (d) Cost | Verdict |
|---|---|---|---|---|---|
| DS-layered-1 | ✅ Pass — uses FR-3.3/FR-2.x correctly. | ✅ Pass — three patterns, well-justified. | ✅ Pass — rules live in Domain.Rules per FR-1.4. | ✅ Pass — low complexity (2). | **Pass** |
| DS-layered-2 | ✅ Pass — explicit FR-1.2 Builder. | ⚠️ Concern — Memento is appropriate but the Template Method may be tighter than necessary; acceptable. | ✅ Pass. | ✅ Pass. | **Pass with note** |
| DS-layered-3 | ⚠️ Concern — Observer is justified for one listener (CLI) only; second listener is speculative. | ⚠️ Over-engineering — Singleton for piece cache is fine but Observer adds machinery without an SRS-stated second listener. | ✅ Pass. | ⚠️ Higher complexity (4) for the same SRS coverage. | **Concern** |
| DS-hexagonal-1 | ✅ Pass — every FR is addressable through a named component. | ✅ Pass — only three patterns; ports kept small. | ✅ Pass — BJV44 in Core.RuleSet. | ✅ Pass — complexity 3 is appropriate. | **Pass** |
| DS-hexagonal-2 | ✅ Pass — explicit FR-1.2 ConfigVO and ConfigSource port. | ✅ Pass — four patterns, each carries weight; complexity 4 justified. | ✅ Pass — first-move corner (FR-4.2) explicit in RuleSet; piece set (FR-4.1) explicit in PieceCatalog. | ✅ Pass — fits a one-semester budget; bootstrap is small. | **Pass — recommended** |
| DS-hexagonal-3 | ⚠️ Concern — second Subscriber (EvalHarness) is in scope (FR-5.2) but could be done without Observer. | ⚠️ Over-engineering — Observer pays off only if the harness genuinely needs streaming events; SRS is satisfied by reading final state. | ✅ Pass. | ⚠️ Higher complexity (4) for marginal benefit. | **Concern** |
| DS-plugin-1 | ⚠️ Concern — applies plugin shape to a fixed rule set (AMB-01). | ❌ Over-engineered — Chain-of-Responsibility + Abstract Factory for 4 fixed rules is excessive. | ✅ Pass on rules themselves. | ❌ Too costly — kernel/registry up-front cost. | **Fail on (b)/(d)** |
| DS-plugin-2 | ❌ Over-interprets — implies event-driven needs the SRS does not state. | ❌ Pub/sub kernel + Decorator stacking is plumbing without a user. | ✅ Pass on rules. | ❌ Too costly. | **Fail on (a)/(b)/(d)** |
| DS-plugin-3 | ❌ Over-interprets — Prototype/Mediator imply runtime module spawn the SRS doesn't call for. | ❌ Mediator helps only at scale. | ✅ Pass on rules. | ❌ Too costly. | **Fail on (a)/(b)/(d)** |

### 8. Select and Rate — 9-Row Critical Rating Table

Scale 1–5. Criteria from Phase 1 + pattern-interaction quality.

| # | Combination | Maintainability | Scalability (perf) | Extensibility (FR-1.2) | Reliability | Migration cost | Reversibility | Testability | Fit to FR-1.2 | Pattern interaction | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Layered + DS-layered-1 (Strategy/Command/Facade) | 4 | 4 | 3 | 4 | 5 | 4 | 4 | 3 | 4 | **35** |
| 2 | Layered + DS-layered-2 (Template Method/Memento/Builder) | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | **36** |
| 3 | Layered + DS-layered-3 (Observer/Iterator/Singleton) | 3 | 4 | 3 | 3 | 3 | 3 | 4 | 3 | 3 | **29** |
| 4 | Hexagonal + DS-hexagonal-1 (Strategy/Factory Method/Command) | 5 | 4 | 4 | 5 | 4 | 3 | 5 | 4 | 4 | **38** |
| 5 | **Hexagonal + DS-hexagonal-2 (Strategy/Command/Builder/Memento)** | **5** | **4** | **5** | **5** | **4** | **3** | **5** | **5** | **5** | **41** |
| 6 | Hexagonal + DS-hexagonal-3 (Observer/Strategy/Command) | 4 | 3 | 4 | 4 | 3 | 3 | 4 | 4 | 4 | **33** |
| 7 | Plugin + DS-plugin-1 (CoR/Abstract Factory/Strategy) | 3 | 3 | 5 | 3 | 2 | 2 | 3 | 5 | 3 | **29** |
| 8 | Plugin + DS-plugin-2 (Observer/Decorator/Strategy) | 3 | 3 | 5 | 3 | 2 | 2 | 3 | 5 | 3 | **29** |
| 9 | Plugin + DS-plugin-3 (Prototype/Mediator/Strategy) | 2 | 3 | 5 | 3 | 1 | 1 | 3 | 5 | 2 | **25** |

**Winner:** Row 5 — **Hexagonal + DS-hexagonal-2**. It is the only combination that scores ≥4 across every criterion *and* ties for the top pattern-interaction score. The runner-up (Row 4) is the same architecture with a leaner pattern set; it remains a viable fallback if Builder/Memento are judged premature.

#### Updated Final ADR (post-design)

```
ADR-FINAL-P2: Adopt Hexagonal Architecture with DS-hexagonal-2 design (Strategy + Command + Builder + Memento)
Status: Accepted — supersedes ADR-FINAL-P1
Context: Same drivers as ADR-FINAL-P1, refined with the concrete design surface: a fixed BJV44 rule set (AMB-01), a fixed AI heuristic (AMB-02), a fixed basic scoring rule (AMB-05), an offline reproducible execution model (SC-2, SC-3), and an SRS-stated configurability of board dimensions, player count, and starting positions (FR-1.2). Milestone 2 (Blokus Duo) is explicitly out of scope of this ADR.
Decision: Implement Milestone 1 as a Hexagonal (Ports-and-Adapters) system whose core uses:
  - Strategy behind PlayerInput for Human (FR-3.1) and Simple-AI (FR-3.2, FR-3.4);
  - Command as the move value object spanning validation, application, enumeration, and JSON I/O (FR-2.3–2.6);
  - Builder for the FR-1.2 configuration value object (board dims, player count, starting positions, first-move corners);
  - Memento for whole-game snapshots used by the JSON state-repository adapter (FR-2.2, FR-2.6, SC-1).
Six ports are exposed: GameSession (in), MoveValidator (in), LegalMoveEnumerator (in), ConfigSource (in), PlayerInput (out), StateRepository (out), PresentationOutput (out). Adapters: CLI (PresentationOutput), JsonStateRepo (StateRepository), JsonConfigSource (ConfigSource), HumanPlayer + SimpleAiPlayer (PlayerInput).
Consequences:
  Positive:
   - Engine core is testable with zero I/O scaffolding (Acceptance ≥90%, FR-5.x).
   - All interface concerns live in adapters; NFR-3.2 is structurally enforced.
   - FR-1.2 is satisfied through ConfigVO + Builder + ConfigSource — board dimensions, player count, and starting positions are not constants in the core.
   - Round-trip JSON via Memento preserves NFR-3.2 (no core types crossing into the JSON adapter).
   - Same shape compiles in Java (interfaces + records) and in Python (Protocols + dataclasses) — NFR-2.1/2.2.
  Negative:
   - Up-front cost of ~6 port interfaces and a bootstrap component.
   - Two value objects (ConfigVO, Memento) to keep in sync with core types.
  Neutral:
   - Performance (NFR-1.x) is governed by Core.PieceCatalog representation, not by the port boundary.
Quality Attributes Addressed:
   - NFR-3.2 (separation): structural.
   - FR-5.x / Acceptance ≥90%: core testable in isolation.
   - FR-1.2: ConfigVO + Builder + ConfigSource port.
   - FR-3.3: PlayerInput port with two Strategy adapters.
   - FR-2.2/2.6, SC-1: Memento + JsonStateRepo adapter.
   - NFR-1.x: precomputed piece orientations in Core.PieceCatalog.
   - NFR-2.1/2.2: pattern set is language-agnostic.
Open Questions / Assumptions:
   - Final port signatures (especially MoveValidator vs GameSession overlap) to be locked in implementation kickoff.
   - Whether legal-move enumeration should be eager (list) or lazy (iterator) — current design says eager for clarity; revisit if NFR-1.2 is in jeopardy.
   - Whether Bootstrap is itself a port-bearing component or a procedural script — defaulting to a procedural Bootstrap in M1.
Rejected Alternatives:
   - ADR-001 (Layered) and Rows 1–3 of the rating table — adequate but lack structural enforcement of NFR-3.2 and FR-3.3 seams.
   - ADR-003 (Plugin) and Rows 7–9 — over-engineered for an SRS whose rule set, scoring, and heuristic are all fixed (AMB-01, AMB-02, AMB-05).
   - Hexagonal + DS-hexagonal-1 (Row 4) — kept as a documented fallback if Builder/Memento are deferred.
   - Hexagonal + DS-hexagonal-3 (Row 6) — Observer adds machinery without an SRS-stated second subscriber.
```

### Senior Architect Review (DS-hexagonal-2)

A separate review pass before exiting Phase 2. Five concrete flaws / improvement points, each with remediation.

1. **Flaw — ConfigVO is the only thing standing between FR-1.2 and a hard-coded `20`.**
   *Remediation:* Add a static-analysis or unit-test tripwire that fails the build if `20` or `4` appears as a literal inside `Core.*` modules (see §11 Drift Risk DR-1).
2. **Flaw — Port surface drift risk: MoveValidator and GameSession can grow overlapping signatures.**
   *Remediation:* Treat MoveValidator and LegalMoveEnumerator as *projections* of GameSession; document their contracts as read-only views and require any new method on either to be justified in PR review.
3. **Flaw — Memento↔ConfigVO redundancy.** The configuration appears both inside the Memento (so a reload restores the board shape) and as a separate ConfigVO at startup. Drift between the two would silently break round-trip.
   *Remediation:* Define ConfigVO as a field *inside* Memento; the JsonConfigSource adapter is a convenience for first-start only, not a second source of truth.
4. **Flaw — Heuristic determinism (FR-3.4) is fragile under iteration order.** The lexicographic tie-break depends on `(row, column, piece ID, rotation, flip)` traversal order in the enumerator.
   *Remediation:* Lock the enumeration order in the core (sorted iteration) and add a regression test that fixes a known state and asserts the chosen move; document the order in the SimpleAiPlayer adapter.
5. **Flaw — Performance margin for NFR-1.2.** Eager legal-move enumeration on a near-empty board can be expensive on a 20×20 grid if naive.
   *Remediation:* Precompute piece orientations once in Core.PieceCatalog (Flyweight-like sharing); track per-color "anchor" cells (current valid corner-touch points) so enumeration is anchor-bounded rather than board-bounded. Add an NFR-1.2 benchmark test in the harness.

(Additional remediation worth noting: keep `Bootstrap` procedural and short; do not introduce a DI framework — Java constructor injection / Python plain function wiring are sufficient for M1 and preserve NFR-2.1/2.2.)

---

## Phase 3 — Validate the Decision (Persona: Senior Reviewing Architect)

### 9. Decision Basis Audit

Read the *actual* ADR-FINAL-P2 above, not a summary.

| Item | Status | Justification |
|---|---|---|
| (a) All assumptions explicit | ✅ | ADR-FINAL-P2's *Open Questions / Assumptions* records port signature lock-in, eager-vs-lazy enumeration, and Bootstrap form. |
| (b) Trade-offs documented | ✅ | *Negative* section lists port-interface upfront cost and ConfigVO/Memento sync cost. |
| (c) Expected consequences stated | ✅ | *Positive*, *Negative*, and *Neutral* sub-bullets cover testability, NFR-3.2 enforcement, FR-1.2 satisfaction, performance neutrality, and the Java/Python parity. |
| (d) Still addresses original drivers | ✅ | NFR-3.2 → structural; FR-5.x ≥90% → core-only tests; FR-1.2 → ConfigVO + Builder + ConfigSource; FR-3.3 → PlayerInput strategies; SC-1 → Memento + JsonStateRepo; NFR-2.1/2.2 → language-agnostic patterns. |
| (e) Milestone-2/Duo content excluded as instructed | ✅ | No Duo-specific code path, board, or rule appears; FR-1.2 is retained only because it is in the M1 SRS itself. |
| (f) Reversibility caveat acknowledged | ⚠️ | Hexagonal is harder to reverse than Layered (rated 3 in Phase 1); this is acknowledged but the human reviewer should confirm acceptance. |

### 10. Quality-Attribute Scenarios

One scenario per attribute. Each scenario records *Stimulus → Expected Response → How the chosen architecture handles it → Contrast with rejected alternatives*.

#### 10.1 Testability (FR-5.1–5.4, Acceptance ≥90%)
- **Stimulus.** Add a unit test that asserts the legal-move enumerator returns the empty set when a player has no anchors and no first-move corner available.
- **Expected response.** The test runs in <50 ms, imports only core types, and requires no CLI/JSON/file-system scaffolding.
- **Hexagonal (chosen).** Test imports `Core.RuleSet` + `Core.Board` directly; PlayerInput / StateRepository / PresentationOutput ports are not loaded.
- **Layered (ADR-001).** Test imports the Application use case; if `MoveService` holds a reference to a default `JsonIO` (a common drift), test setup also constructs that. Coverage achievable but with more scaffolding.
- **Plugin (ADR-003).** Test must construct a kernel registry and register the rule chain modules; setup cost dominates the test. Lower coverage per unit of test code.

#### 10.2 Configurability (FR-1.2)
- **Stimulus.** Run the engine with a non-default starting-position map for the four corners (e.g., swap Blue and Red).
- **Expected response.** A single config change flips first-move corners; no code changes; FR-4.2 still enforced under the new map.
- **Hexagonal.** Edit the JSON consumed by `Adapter.JsonConfigSource` → new `ConfigVO` → `Core.RuleSet.firstMoveCorner` is parameterized by the VO. Zero code change.
- **Layered.** Achievable but tempting to hard-code corner coordinates inside `Domain.Rules`. Without a config-VO discipline, the change is a code change.
- **Plugin.** Trivial (a different start-position module) but the cost was paid up front in registry plumbing.
*Note:* FR-1.2's intent is generic configurability per the M1 SRS; this scenario does not depend on Duo.

#### 10.3 Scalability — Performance (NFR-1.1, NFR-1.2, NFR-1.3)
- **Stimulus.** With a mid-game state (~40 pieces placed total), call `enumerateLegalMoves` for the player to move; measure on the reference laptop.
- **Expected response.** ≤500 ms (NFR-1.2). `validateMove` ≤100 ms (NFR-1.1). State (de)serialization ≤200 ms (NFR-1.3).
- **Hexagonal.** Enumeration runs against `Core.PieceCatalog` (precomputed orientations, Flyweight-like) and anchor-bounded search (Senior Architect remediation #5). Port boundary adds a single interface dispatch.
- **Layered.** Achievable; same internal techniques apply, but lack of an explicit `Core` boundary makes it easy for `Interface.CLI` to pull state on every iteration step, accidentally pushing past NFR-1.2.
- **Plugin.** Event-bus dispatch in pub/sub variants is a real, measurable per-move cost; harder to meet NFR-1.2 without surgical optimization.

#### 10.4 Portability (NFR-2.1, NFR-2.2)
- **Stimulus.** Re-implement the project in Python/uv after starting in Java/Maven (or vice versa).
- **Expected response.** Pattern set translates 1:1; no design rewrite, only language idioms.
- **Hexagonal.** Ports → Java `interface` / Python `typing.Protocol`. Strategy → subclasses or duck-typed callables. Builder → fluent in Java, dataclass-with-factory in Python. Memento → `record` in Java, `@dataclass(frozen=True)` in Python.
- **Layered.** Equally portable in principle, but cross-layer constants are more likely to leak language-specific idioms.
- **Plugin.** Plugin discovery mechanisms diverge sharply between Java (ServiceLoader) and Python (entry points), introducing real per-language work the SRS doesn't demand.

#### 10.5 Maintainability (NFR-3.1, NFR-3.2)
- **Stimulus.** A new contributor must add a third player adapter (e.g., a scripted-replay player for testing).
- **Expected response.** Implementation touches one new file; existing core/CLI/JSON modules are untouched.
- **Hexagonal.** New adapter implements `Port.PlayerInput`; Bootstrap wires it. Core unchanged.
- **Layered.** Achievable via the FR-3.3 abstraction, but the contributor must locate the Application-level dispatch; risk of touching `GameLoop`.
- **Plugin.** Equally easy by design — but the contributor first has to learn the module registry and event protocol.

#### 10.6 Reproducibility (SC-3, IR-2.x, FR-3.4 determinism)
- **Stimulus.** Run the same JSON-loaded game twice with the same Simple-AI seed; compare output transcripts.
- **Expected response.** Byte-identical transcripts; identical winner; identical score table.
- **Hexagonal.** Determinism rests on (i) `Core.RuleSet` purity, (ii) `SimpleAiPlayer` fixed lexicographic tie-break per FR-3.4, (iii) `JsonStateRepo` deterministic Memento ordering. All three are isolated and testable. Build/run scripts (IR-1.2/1.4) wrap `mvn`/`uv` to satisfy SC-3.
- **Layered.** Same logical guarantees but bigger blast radius if any layer accidentally relies on map/set iteration order.
- **Plugin.** Event-bus delivery order would need to be specified and tested — additional reproducibility surface.

### 11. Drift Risk Register

Top design choices most likely to drift from ADR-FINAL-P2 during implementation, each with a concrete tripwire.

| ID | Drift risk | Tripwire |
|---|---|---|
| **DR-1** | Hard-coding board dimensions (`20`) or player count (`4`) inside `Core.*`, violating FR-1.2. | CI lint rule (regex on `Core/**`) that fails the build on the literals `20` or `4` outside `Core.PieceCatalog`. Pair with a unit test that constructs a 10×10 board and asserts that nothing crashes inside the core. |
| **DR-2** | CLI parsing or rendering logic creeping into `Core.GameSession`. | Static check / module-level import policy: `Core.*` may not import from `Adapter.CLI`, `Adapter.JsonStateRepo`, or any I/O module. A Python ruff rule or Java ArchUnit test enforces this. |
| **DR-3** | Forgetting the determinism contract — using an unordered set/map for legal-move enumeration. | Determinism regression test: load a fixed JSON state, run `SimpleAiPlayer`, assert the chosen move equals a recorded golden value. |
| **DR-4** | Memento drifting from ConfigVO (the snapshot stores the dimensions but the runtime engine reads them from a separate ConfigVO). | Round-trip test that saves a Memento, mutates ConfigVO, reloads the Memento, and asserts the engine uses the *Memento's* dimensions — not the runtime ConfigVO. Pair with the Senior Architect remediation #3. |
| **DR-5** | Pulling in a heavy GUI library or a network dependency, violating EX-1 / EX-3 / SC-2. | Dependency-allowlist check in `pom.xml` / `pyproject.toml`: build fails if Swing/JavaFX/Qt/Tk/HTTP-client dependencies appear. |
| **DR-6** | Introducing Blokus Duo logic, board size, or rule paths into M1 (explicitly out of scope of this ADR). | Code-review rule + CI grep: any file mentioning "duo" inside `Core.*` or `Adapter.*` fails review. (FR-1.2 generic parameters are fine; *named* Duo paths are not.) |
| **DR-7** | `Bootstrap` quietly becoming a DI container with reflection and annotations. | PR-review rule: Bootstrap must remain procedural (≤200 lines, no annotations, no reflective lookup). |

### 12. Final Review Brief

#### 12.1 Valid (signed off by this analytical pass)
- The Hexagonal architecture (ADR-002) and the DS-hexagonal-2 design (Strategy + Command + Builder + Memento) are aligned with NFR-3.2, FR-3.3, FR-1.2, FR-2.2/2.6, SC-1, and FR-5.x.
- The choice of patterns is parsimonious (four patterns, each carrying weight, with documented interactions).
- The design is language-neutral — Java and Python implementations are 1:1 translations.
- Performance budgets (NFR-1.x) are not threatened by the port boundary; they are governed by the Core.PieceCatalog representation and the anchor-bounded enumeration strategy.
- Milestone 2 (Blokus Duo) has been excluded from the decision basis as instructed; FR-1.2 is retained as an SRS requirement only.

#### 12.2 Questionable (human architect must scrutinize before approval)
- **Reversibility cost.** Hexagonal is rated 3/5 for reversibility. If the team's confidence in the architecture is below ~80 %, ADR-001 (Layered) is the more conservative fallback because it can be refactored *into* hexagonal later.
- **Port count.** The proposed 6 ports may be too granular for M1. Consider merging `MoveValidator` + `LegalMoveEnumerator` into `GameSession` and reviewing whether `ConfigSource` is a port or a one-shot bootstrap call.
- **Builder + Memento at M1.** DS-hexagonal-1 (without Builder/Memento) is a smaller landing zone and may be preferable if the team is new to the patterns. The downgrade from DS-hexagonal-2 to DS-hexagonal-1 is mechanical.
- **Determinism guarantees.** FR-3.4's lexicographic tie-break must be specified and tested. Without DR-3's golden-output test, AI determinism is a verbal claim, not a verified property.
- **Performance evidence.** The ≤500 ms enumeration claim (NFR-1.2) is currently *argued*, not *measured*. A benchmark must be added in M1, not deferred.

#### 12.3 Follow-up (deferred items)
- Lock final port signatures during implementation kickoff; document them in a `PORTS.md` adjacent to the source.
- Decide eager vs lazy legal-move enumeration once a benchmark exists.
- Define the `Memento` JSON schema explicitly (a separate document) so SC-1 round-trip is contract-tested, not implementation-tested.
- Re-open this ADR (or supersede with a new one) before any future work on alternative game variants is undertaken — *that* decision will need its own option ADRs.

---

*The LLM is an analytical assistant; the human architect makes the final call.*
