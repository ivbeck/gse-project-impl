# Software Requirements Specification

## Blokus Configurable Game Engine

### Generative Software Engineering Project

---

**Document Version:** 1.0
**Status:** Draft for Review
**Classification:** Academic Project Specification

---

## 1. Introduction

### 1.1 Purpose

This document constitutes the formal Software Requirements Specification (SRS) for the Blokus Configurable Game Engine, developed as part of a university-level Generative Software Engineering project. The specification establishes the baseline requirements for implementing a configurable engine supporting both Blokus Classic (four-player) and Blokus Duo (two-player) game modes.

### 1.2 Scope

The engine shall provide a complete implementation of the Blokus board game, including move validation, legal move enumeration, move application, state serialization, and an evaluation harness. The system shall support both human players and simple automated computer players through a minimal command-line interface.

### 1.3 Definitions, Acronyms, and Abbreviations

| Term | Definition |
|------|------------|
| Blokus Classic | Four-player variant played on a 20×20 board |
| Blokus Duo | Two-player variant played on a 14×14 board |
| SRS | Software Requirements Specification |
| CLI | Command Line Interface |
| JSON | JavaScript Object Notation (state serialization format) |
| LLM | Large Language Model |

---

## 2. Functional Requirements

### 2.1 Core Engine Specifications

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | The engine shall implement all game rules for Blokus Classic (4 players). | Mandatory |
| FR-1.2 | The engine shall implement all game rules for Blokus Duo (2 players) via configuration. | Mandatory |
| FR-1.3 | The engine shall support configurable game parameters including board dimensions, player count, and starting positions. | Mandatory |
| FR-1.4 | The engine shall maintain accurate game state including piece ownership, board occupancy, and turn progression. | Mandatory |
| FR-1.5 | The engine shall enforce the Blokus piece placement rules: orthogonal adjacency constraints and color continuity rules. | Mandatory |

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
| FR-3.4 | Simple AI players shall select moves using a deterministic heuristic (e.g., largest available piece, first valid placement). | Mandatory |

### 2.4 Game Rules Implementation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | The engine shall implement the complete Blokus rule book for Classic mode. | Mandatory |
| FR-4.2 | The engine shall implement the complete Blokus rule book for Duo mode. | Mandatory |
| FR-4.3 | The engine shall enforce first-move corner placement constraints for each color. | Mandatory |
| FR-4.4 | The engine shall detect and handle game termination conditions. | Mandatory |
| FR-4.5 | The engine shall calculate and report final scores upon game completion. | Mandatory |

### 2.5 Evaluation and Testing

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.1 | The system shall provide an automated test suite covering core game rules. | Mandatory |
| FR-5.2 | The system shall provide an evaluation harness for assessing engine correctness. | Mandatory |
| FR-5.3 | The test suite shall include tests for legality checkers. | Mandatory |
| FR-5.4 | The test suite shall include tests for move application transformations. | Mandatory |
| FR-5.5 | The evaluation harness shall support both Classic and Duo modes. | Mandatory |

---

## 3. Non-Functional Requirements

### 3.1 Performance Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1.1 | Move validation shall complete within 100ms for any legal position. | ≤ 100ms |
| NFR-1.2 | Legal move enumeration shall complete within 500ms for any game state. | ≤ 500ms |
| NFR-1.3 | State serialization and deserialization shall complete within 200ms. | ≤ 200ms |

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
| NFR-3.3 | Configuration-driven design shall minimize code changes when switching between game modes. | Mandatory |

---

## 4. System Constraints

| ID | Constraint | Rationale |
|----|------------|-----------|
| SC-1 | The system shall use JSON for all state serialization and deserialization. | Ensures interoperability and human readability for testing. |
| SC-2 | The system shall operate without network connectivity. | Offline operation is required for controlled academic evaluation. |
| SC-3 | The system shall provide reproducible build and execution via scripts. | Academic evaluation requires deterministic reproducibility. |

---

## 5. Milestone 1: Classic Baseline

### 5.1 Objectives

Deliver a fully functional Blokus Classic implementation (4 players) establishing the baseline engine architecture.

### 5.2 Deliverables

| ID | Deliverable | Acceptance Criteria |
|----|-------------|---------------------|
| M1-D1 | Legality Checker | Correctly validates all piece placements per Blokus rules |
| M1-D2 | Move Application | Successfully applies legal moves and updates game state |
| M1-D3 | State Serialization | Full round-trip JSON serialization/deserialization |
| M1-D4 | Core Rule Tests | Automated tests covering key rules and state transformations |
| M1-D5 | CLI Interface | Functional command-line interface for game play |
| M1-D6 | Player Implementation | Human and simple computer player implementations |

### 5.3 Acceptance Criteria

1. All 21 Blokus pieces (per color) shall be correctly represented and placeable.
2. The legality checker shall enforce orthogonal adjacency constraints.
3. The legality checker shall enforce color continuity rules.
4. State serialization shall preserve complete game state across round-trip operations.
5. The automated test suite shall achieve ≥90% coverage of core game logic.
6. The system shall correctly detect game termination and calculate final scores.

---

## 6. Milestone 2: Configuration Change (Duo Extension)

### 6.1 Objectives

Extend the baseline engine to support Blokus Duo via configuration-driven design without fundamental architectural changes.

### 6.2 Delta Requirements

| ID | Requirement | Details |
|----|-------------|---------|
| M2-R1 | Board Dimensions | 14×14 grid (reduced from 20×20) |
| M2-R2 | Player Count | 2 players (reduced from 4) |
| M2-R3 | Starting Corners | Duo-specific corner positions (diagonal symmetry) |
| M2-R4 | Piece Subset | 21 pieces per player (same as Classic) |

### 6.3 Deliverables

| ID | Deliverable | Acceptance Criteria |
|----|-------------|---------------------|
| M2-D1 | Duo Configuration | Engine shall initialize in Duo mode via configuration |
| M2-D2 | Adapted Legality | Checker shall respect Duo board boundaries |
| M2-D3 | Updated Tests | Test suite shall cover both Classic and Duo modes |
| M2-D4 | Evaluation Harness Update | Harness shall evaluate engine correctness in both modes |

### 6.4 Acceptance Criteria

1. The engine shall switch between Classic and Duo modes via configuration parameters.
2. No code duplication shall occur between Classic and Duo implementations.
3. The test suite shall validate both game modes with shared test infrastructure.
4. The evaluation harness shall generate mode-specific performance metrics.

---

## 7. Academic Reporting Constraints

### 7.1 Evidence-Based Analysis

The final project report shall include:

| ID | Requirement | Description |
|----|-------------|-------------|
| AR-1.1 | Guideline Application | Document each software engineering guideline applied |
| AR-1.2 | Counterexamples | Present failed cases and refinements made during development |
| AR-1.3 | Trade-off Analysis | Analyze design decisions and their implications |

### 7.2 LLM Usage Disclosure

The final project report shall explicitly disclose:

| ID | Requirement | Description |
|----|-------------|-------------|
| AR-2.1 | Tool Identification | State the specific LLM tools/models used |
| AR-2.2 | Application Areas | Document where LLMs were applied in the development process |
| AR-2.3 | Output Validation | Describe the validation methods employed for LLM-generated outputs |

### 7.3 Requirements Evolution Case Study

The report shall treat the Milestone 1 to Milestone 2 transition as a requirements evolution case study, analyzing:

| ID | Requirement | Description |
|----|-------------|-------------|
| AR-3.1 | Breaking Points | Identify requirements that broke or required modification |
| AR-3.2 | LLM Suggestions | Document recommendations provided by LLM assistants |
| AR-3.3 | Applied Solutions | Report actual implementation approaches that succeeded |
| AR-3.4 | Friction Analysis | Quantify the effort delta between expected and actual changes |

---

## 8. Infrastructure Requirements

### 8.1 Repository Structure

| ID | Requirement | Description |
|----|-------------|-------------|
| IR-1.1 | Version Control | Git repository with structured branching strategy |
| IR-1.2 | Build Scripts | Reproducible installation scripts |
| IR-1.3 | Test Scripts | Automated test execution scripts |
| IR-1.4 | Run Scripts | Application execution scripts |

### 8.2 Build Management

| ID | Requirement | Description |
|----|-------------|-------------|
| IR-2.1 | Dependency Management | Automated dependency resolution via build tool |
| IR-2.2 | Testing Integration | Test execution via build tool (e.g., `mvn test`, `uv run pytest`) |
| IR-2.3 | Executable Packaging | Single-command application launch via build tool |

### 8.3 Supported Build Tools

| Language | Build Tool | Invocation |
|----------|------------|------------|
| Java | Maven | `mvn install`, `mvn test`, `mvn exec:java` |
| Python | uv | `uv sync`, `uv run pytest`, `uv run python -m app` |

---

## 9. Exclusions (Out of Scope)

The following features are explicitly excluded from the project requirements:

| ID | Exclusion | Rationale |
|----|-----------|-----------|
| EX-1 | Heavy Graphical User Interface | Out of scope; CLI is the mandated interface |
| EX-2 | Strong AI Opponents | Out of scope; simple heuristic players only |
| EX-3 | Online Multiplayer | Out of scope; local play only |

---

## 10. Traceability Matrix

| Requirement ID | Milestone | Validation Method |
|----------------|-----------|-------------------|
| FR-1.1, FR-1.5, FR-4.1, FR-4.3 | M1 | Automated unit tests |
| FR-1.2, FR-1.3, FR-4.2 | M2 | Configuration-based validation |
| FR-2.1 – FR-2.7 | M1 | CLI integration tests |
| FR-3.1 – FR-3.4 | M1 | Player interaction tests |
| FR-5.1 – FR-5.5 | M1, M2 | Test suite execution |
| NFR-1.1 – NFR-1.3 | M1 | Performance benchmark tests |
| NFR-2.1 – NFR-3.3 | M1, M2 | Code review and architectural inspection |
| AR-1.1 – AR-3.4 | Report | Final project report |

---

**End of Software Requirements Specification**