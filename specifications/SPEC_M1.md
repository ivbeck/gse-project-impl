# Software Requirements Specification

## Blokus Configurable Game Engine (Baseline)

### Generative Software Engineering Project

---

**Document Version:** 2.0
**Status:** Updated — Ambiguity-Resolved Baseline
**Classification:** Academic Project Specification
**Changelog:** AMB-01, AMB-02, AMB-04, AMB-05, AMB-06, AMB-08 resolved; official Blokus rules (Mattel BJV44) embedded into FR-1.4, FR-4.1–FR-4.4, and NFR-1.x.

---

## 1. Introduction

### 1.1 Purpose

This document constitutes the formal Software Requirements Specification (SRS) for the Blokus Configurable Game Engine, developed as part of a university-level Generative Software Engineering project. The specification establishes the baseline requirements for implementing a configurable engine supporting the Blokus Classic (four-player) game mode.

### 1.2 Scope

The engine shall provide a complete implementation of the Blokus board game, including move validation, legal move enumeration, move application, state serialization, and an evaluation harness. The system shall support both human players and simple automated computer players through a minimal command-line interface.

### 1.3 Definitions, Acronyms, and Abbreviations

| Term | Definition |
|------|------------|
| Blokus Classic | Four-player variant played on a 20×20 board |
| SRS | Software Requirements Specification |
| CLI | Command Line Interface |
| JSON | JavaScript Object Notation (state serialization format) |
| LLM | Large Language Model |
| Corner Square | One of the four corner cells of the board (positions (0,0), (0,19), (19,0), (19,19) on the 20×20 grid) |
| Orthogonal Adjacency | Sharing a full edge (up, down, left, right) between two cells |
| Diagonal Adjacency | Touching at exactly one corner point between two cells |

---

## 2. Functional Requirements

### 2.1 Core Engine Specifications

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | The engine shall implement all game rules for Blokus Classic (4 players). | Mandatory |
| FR-1.2 | The engine shall support configurable game parameters including board dimensions, player count, and starting positions to allow future extensibility. | Mandatory |
| FR-1.3 | The engine shall maintain accurate game state including piece ownership, board occupancy, and turn progression. | Mandatory |
| FR-1.4 | The engine shall enforce the following official Blokus piece placement rules (per Mattel rulebook BJV44): **(a) Corner-touch requirement:** each new piece placed by a player must touch at least one previously placed piece of the same color at a corner (diagonally), not along a side. **(b) Orthogonal prohibition:** pieces of the same color may never share an edge. **(c) Different-color contact:** there are no restrictions on how pieces of different colors may contact each other — they may share edges or corners freely. **(d) Immovability:** once a piece has been placed on the board it cannot be moved or removed. | Mandatory |

### 2.2 Interface and State Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | The system shall provide a minimal Command Line Interface (CLI) for game interaction. | Mandatory |
| FR-2.2 | The system shall support loading game state from JSON format. | Mandatory |
| FR-2.3 | The system shall validate moves against established legal move criteria before application. | Mandatory |
| FR-2.4 | The system shall apply validated moves to the current game state. | Mandatory |
| FR-2.5 | The system shall enumerate and list all legal moves for a given player state. | Mandatory |
| FR-2.6 | The system shall serialize the current game state to JSON format. | Mandatory |
| FR-2.7 | The system shall print human-readable game state representations via the CLI. | Mandatory |

### 2.3 Player Archetypes

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | The system shall support human players via CLI input. | Mandatory |
| FR-3.2 | The system shall implement simple automated computer players with basic decision logic. | Mandatory |
| FR-3.3 | The system shall provide an abstraction layer for player implementations to enable extensibility. | Mandatory |
| FR-3.4 | Simple AI players shall select moves using a deterministic, situation-aware heuristic designed to improve the likelihood of winning. The heuristic shall evaluate candidate moves against the following prioritized criteria, applied in order: **(1) Maximize board coverage** — prefer the piece placement that occupies the greatest number of squares; **(2) Maximize future options** — among equally large placements, prefer the placement that creates the greatest number of new valid corner-touch points for future moves; **(3) Tie-breaking** — if multiple placements remain equal, select the lexicographically first placement by (row, column, piece ID, rotation, flip). The implemented heuristic shall be documented in the project report. | Mandatory |

### 2.4 Game Rules Implementation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | The engine shall implement the complete Blokus rule book for Classic mode as specified in Mattel rulebook BJV44. The following rules apply: **(a) Piece set:** each of the 4 players begins with the complete set of 21 pieces (1 monomino, 1 domino, 2 trominoes, 5 tetrominoes, 12 pentominoes). **(b) Turn order:** starting from the first player, play proceeds clockwise. **(c) Pass rule:** whenever a player is unable to legally place any piece, that player must pass their turn. **(d) Simultaneous exhaustion:** the game continues until no player can place any further piece. | Mandatory |
| FR-4.2 | The engine shall enforce first-move corner placement for each color: each player's very first piece must cover one of the four corner squares of the 20×20 board — (0,0), (0,19), (19,0), or (19,19). Each corner is exclusively assigned to one player: Blue → (0,0), Yellow → (0,19), Red → (19,19), Green → (19,0). The first-move corner rule is a special case; the general corner-touch and orthogonal-prohibition rules of FR-1.4 still apply from the second move onward. | Mandatory |
| FR-4.3 | The engine shall detect the game termination condition: the game ends when all active players have passed consecutively in a single round (i.e., no player was able to place a piece during that round). Upon detecting termination, the engine shall: **(1)** stop accepting new move inputs; **(2)** calculate and display the final score for each player per FR-4.4; **(3)** announce the winner; **(4)** prompt all players to choose whether to start a new game or exit. | Mandatory |
| FR-4.4 | The engine shall calculate and report final scores upon game completion using the **basic scoring scheme**: each player's score is the total number of squares remaining in their unplaced pieces (lower is better). The player with the lowest score is declared the winner. In the event of a tie, all tied players share the win. The score shall be displayed in a ranked results table via the CLI. | Mandatory |

### 2.5 Evaluation and Testing

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.1 | The system shall provide an automated test suite covering core game rules. | Mandatory |
| FR-5.2 | The system shall provide an evaluation harness for assessing engine correctness. | Mandatory |
| FR-5.3 | The test suite shall include tests for legality checkers. | Mandatory |
| FR-5.4 | The test suite shall include tests for move application transformations. | Mandatory |

---

## 3. Non-Functional Requirements

### 3.1 Performance Requirements

> **Reference Environment:** All performance targets below are defined relative to a standard-issue modern laptop (e.g., a consumer-grade machine with a multi-core CPU ≥ 2.0 GHz, ≥ 8 GB RAM, SSD storage) running the supported operating systems listed in NFR-2.2. Performance measured on significantly underpowered or shared CI hardware is informative only and does not constitute a pass/fail determination.

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1.1 | Move validation shall complete within 100ms for any legal position, measured on the reference environment. | ≤ 100ms |
| NFR-1.2 | Legal move enumeration shall complete within 500ms for any game state, measured on the reference environment. | ≤ 500ms |
| NFR-1.3 | State serialization and deserialization shall complete within 200ms, measured on the reference environment. | ≤ 200ms |

### 3.2 Portability Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-2.1 | The system shall be implemented in a language with established build management tools (e.g., Java/Maven, Python/uv). | Mandatory |
| NFR-2.2 | The system shall execute identically across supported operating systems (Windows, macOS, Linux). | Mandatory |

### 3.3 Maintainability Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-3.1 | The codebase shall follow industry-standard coding conventions appropriate to the implementation language. | Mandatory |
| NFR-3.2 | The system architecture shall clearly separate game logic from interface concerns. | Mandatory |

---

## 4. System Constraints

| ID | Constraint | Rationale |
|----|------------|-----------| 
| SC-1 | The system shall use JSON for all state serialization and deserialization. | Ensures interoperability and human readability for testing. |
| SC-2 | The system shall operate without network connectivity. | Offline operation is required for controlled academic evaluation. |
| SC-3 | The system shall provide reproducible build and execution via scripts. | Academic evaluation requires deterministic reproducibility. |

---

## 5. Core Deliverables (Milestone 1)

### 5.1 Objectives

Deliver a fully functional Blokus Classic implementation (4 players) establishing the baseline engine architecture.

### 5.2 Deliverables

| ID | Deliverable | Acceptance Criteria |
|----|-------------|---------------------|
| D-1 | Legality Checker | Correctly validates all piece placements per Blokus rules (FR-1.4, FR-4.1, FR-4.2) |
| D-2 | Move Application | Successfully applies legal moves and updates game state |
| D-3 | State Serialization | Full round-trip JSON serialization/deserialization |
| D-4 | Core Rule Tests | Automated tests covering key rules and state transformations |
| D-5 | CLI Interface | Functional command-line interface for game play including post-game replay prompt |
| D-6 | Player Implementation | Human and simple computer player implementations |

### 5.3 Acceptance Criteria

1. All 21 Blokus pieces (per color) shall be correctly represented and placeable.
2. The legality checker shall enforce the orthogonal adjacency prohibition (same-color pieces may never share an edge).
3. The legality checker shall enforce the corner-touch (diagonal) requirement: each new piece must touch at least one same-color piece diagonally.
4. The legality checker shall enforce first-move corner placement: each player's first piece must cover their assigned board corner.
5. State serialization shall preserve complete game state across round-trip operations.
6. The automated test suite shall achieve ≥90% coverage of core game logic.
7. The system shall correctly detect game termination (all players passing in a round) and calculate final scores using the basic scoring scheme (lowest remaining squares wins).
8. Upon game termination, the system shall display final scores, announce the winner, and prompt players to replay or exit.

---

## 6. Academic Reporting Constraints

### 6.1 Evidence-Based Analysis

The final project report shall include:

| ID | Requirement | Description |
|----|-------------|-------------|
| AR-1.1 | Guideline Application | Document each software engineering guideline applied |
| AR-1.2 | Counterexamples | Present failed cases and refinements made during development |
| AR-1.3 | Trade-off Analysis | Analyze design decisions and their implications |

### 6.2 LLM Usage Disclosure

The final project report shall explicitly disclose:

| ID | Requirement | Description |
|----|-------------|-------------|
| AR-2.1 | Tool Identification | State the specific LLM tools/models used |
| AR-2.2 | Application Areas | Document where LLMs were applied in the development process |
| AR-2.3 | Output Validation | Describe the validation methods employed for LLM-generated outputs |

---

## 7. Infrastructure Requirements

### 7.1 Repository Structure

| ID | Requirement | Description |
|----|-------------|-------------|
| IR-1.1 | Version Control | Git repository using a feature-branch strategy: create a dedicated branch per feature being implemented; merge completed feature branches into `main` via pull request; delete feature branches after successful merge. | 
| IR-1.2 | Build Scripts | Reproducible installation scripts |
| IR-1.3 | Test Scripts | Automated test execution scripts |
| IR-1.4 | Run Scripts | Application execution scripts |

### 7.2 Build Management

| ID | Requirement | Description |
|----|-------------|-------------|
| IR-2.1 | Dependency Management | Automated dependency resolution via build tool |
| IR-2.2 | Testing Integration | Test execution via build tool (e.g., `mvn test`, `uv run pytest`) |
| IR-2.3 | Executable Packaging | Single-command application launch via build tool |

### 7.3 Supported Build Tools

| Language | Build Tool | Invocation |
|----------|------------|------------|
| Java | Maven | `mvn install`, `mvn test`, `mvn exec:java` |
| Python | uv | `uv sync`, `uv run pytest`, `uv run python -m app` |

---

## 8. Exclusions (Out of Scope)

The following features are explicitly excluded from the project requirements:

| ID | Exclusion | Rationale |
|----|-----------|-----------| 
| EX-1 | Heavy Graphical User Interface | Out of scope; CLI is the mandated interface |
| EX-2 | Strong AI Opponents | Out of scope; simple heuristic players only |
| EX-3 | Online Multiplayer | Out of scope; local play only |

---

## 9. Traceability Matrix

| Requirement ID | Milestone | Validation Method |
|----------------|-----------|-------------------|
| FR-1.1 – FR-1.4 | Baseline | Automated unit tests |
| FR-2.1 – FR-2.7 | Baseline | CLI integration tests |
| FR-3.1 – FR-3.4 | Baseline | Player interaction tests |
| FR-4.1 – FR-4.4 | Baseline | Automated unit tests |
| FR-5.1 – FR-5.4 | Baseline | Test suite execution |
| NFR-1.1 – NFR-1.3 | Baseline | Performance benchmark tests on reference environment |
| NFR-2.1 – NFR-3.2 | Baseline | Code review and architectural inspection |
| AR-1.1 – AR-2.3 | Report | Final project report |

---

**End of Software Requirements Specification**
