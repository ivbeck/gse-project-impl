# Change Request: Configuration Change (Duo Extension)

## Blokus Configurable Game Engine (Milestone 2)

---

**Document Version:** 2.0
**Target Document:** `SPEC_M1.md` v2.0
**Classification:** Academic Project Change Request
**Changelog:** AMB-03 resolved (two-player variant is the Classic 4-player game with a two-player twist, not Blokus Duo); AMB-07 resolved (code reuse policy clarified); official two-player rules from Mattel rulebook BJV44 embedded into FR-1.1b, FR-4.1b, and CR-R2–CR-R3.

---

## 1. Introduction

### 1.1 Purpose of Change Request

This document outlines an extension to the baseline Blokus Engine specifications (Milestone 1). The goal of this change request is to extend the baseline engine to support the **Blokus two-player variant** as defined in the official Mattel rulebook (BJV44) via configuration-driven design, without fundamental architectural changes.

> **Scope clarification (resolves AMB-03):** This milestone implements the official two-player variant of Blokus Classic, in which each human player controls **two colors** on the standard 20×20 board — not the separate "Blokus Duo" product (14×14 board). The starting positions, piece sets, and board dimensions are those of Classic mode; only the player-count and color-assignment model changes. The term "corner" in this document refers to the four literal board corners of the 20×20 grid, consistent with FR-4.2 in SPEC_M1.

### 1.2 Added Definitions

| Term | Definition |
|------|------------|
| Two-Player Variant | The official two-player mode of Blokus Classic in which each player controls two colors (blue + red or yellow + green) on the standard 20×20 board, per Mattel rulebook BJV44. |
| Color Pair | The two colors assigned to a single player in the two-player variant (Player 1: Blue + Red; Player 2: Yellow + Green). |

---

## 2. Delta Requirements (Functional Additions)

The following requirements are added to the base specification under Sections 2.1, 2.4, and 2.5:

| ID | Sub-System | Requirement | Priority |
|----|------------|-------------|----------|
| FR-1.1b | Core Engine | The engine shall implement the official two-player variant of Blokus Classic via configuration: each of the two human (or AI) players controls two colors, with turn order and scoring as specified in FR-4.1b. | Mandatory |
| FR-4.1b | Game Rules | The engine shall implement the complete Blokus rule book for the two-player variant per Mattel rulebook BJV44. Specifically: **(a) Color assignment:** Player 1 controls Blue and Red; Player 2 controls Yellow and Green. **(b) Turn order:** the play sequence is Blue → Yellow → Red → Green, cycling repeatedly regardless of which human player controls each color. Each color is treated as an independent actor for placement purposes. **(c) Placement rules:** all placement rules from FR-1.4 apply independently per color — a Blue piece must touch a prior Blue piece diagonally, a Red piece must touch a prior Red piece diagonally, and so on. **(d) Pass rule:** a player passes a color's turn only when no legal placement exists for that color; the other color(s) they control are unaffected. **(e) Scoring:** at game end, each player's total score is the combined square-count of remaining unplaced pieces across both of their colors (lower is better); the player with the lower combined count wins. | Mandatory |
| FR-5.5 | Evaluation | The evaluation harness shall be updated to support and evaluate both Classic (4-player) and two-player variant modes. | Mandatory |

---

## 3. Configuration Parameters

The engine's configuration system must support the following parameters to switch between Classic and two-player variant modes:

| ID | Requirement | Details |
|----|-------------|---------|
| CR-R1 | Board Dimensions | 20×20 grid (unchanged from Classic) |
| CR-R2 | Player Count | 2 human/AI players (each controlling 2 colors), reduced from 4 independent players |
| CR-R3 | Starting Corners | Same four board corners as Classic mode — Blue → (0,0), Yellow → (0,19), Red → (19,19), Green → (19,0) — since the board is unchanged |
| CR-R4 | Piece Subset | 21 pieces per color, 42 pieces per player (same piece set as Classic) |
| CR-R5 | Turn Sequence | Fixed order Blue → Yellow → Red → Green; the engine maps colors to players via configuration |

---

## 4. Deliverables and Acceptance Criteria (Milestone 2)

### 4.1 Deliverables

| ID | Deliverable | Acceptance Criteria |
|----|-------------|---------------------|
| M2-D1 | Two-Player Configuration | Engine shall initialize in two-player variant mode via configuration parameters with no code changes |
| M2-D2 | Color-to-Player Mapping | Engine shall correctly assign Blue+Red to Player 1 and Yellow+Green to Player 2, enforcing the fixed turn order Blue → Yellow → Red → Green |
| M2-D3 | Combined Scoring | Scoring module shall aggregate square-counts across both colors per player and produce a ranked result |
| M2-D4 | Updated Tests | Test suite shall be expanded to cover both Classic (4-player) and two-player variant modes using shared test infrastructure |
| M2-D5 | Evaluation Harness Update | Harness shall evaluate engine correctness and metrics in both modes |

### 4.2 Acceptance Criteria

1. The engine shall switch between Classic and two-player variant modes strictly via configuration parameters (no hardcoded modes).
2. **Code reuse policy (resolves AMB-07):** No game-logic function or module shall be duplicated. If equivalent logic already exists from Milestone 1, it shall be reused or extended — not rewritten. New code shall only be introduced where no comparable implementation already exists. This policy applies to placement validation, move enumeration, state serialization, and scoring. Developers shall document in the report any case where reuse was not possible and justify why.
3. The test suite shall validate both game modes using shared test infrastructure.
4. The evaluation harness shall generate mode-specific performance metrics.

---

## 5. Academic Reporting Constraints (Evolution Case Study)

*This section supplements Section 6 of the baseline SRS.*

The final project report shall treat the Milestone 1 to Milestone 2 transition as a **requirements evolution case study**, analyzing how the codebase adapted to the change request:

| ID | Requirement | Description |
|----|-------------|-------------|
| AR-3.1 | Breaking Points | Identify requirements/architectural choices from M1 that broke or required modification |
| AR-3.2 | LLM Suggestions | Document recommendations provided by LLM assistants in handling this change request |
| AR-3.3 | Applied Solutions | Report actual implementation approaches that succeeded in addressing the configuration extension |
| AR-3.4 | Friction Analysis | Quantify the effort delta between expected and actual changes required for the extension |

---

## 6. Traceability Updates

| Requirement ID | Milestone | Validation Method |
|----------------|-----------|-------------------|
| FR-1.1b, FR-4.1b | M2 (Change Request) | Configuration-based validation; automated unit tests for color-pair rules and combined scoring |
| CR-R1 – CR-R5 | M2 (Change Request) | Automated unit & integration tests |
| FR-5.5 | M2 (Change Request) | Test suite & harness execution |
| AR-3.1 – AR-3.4 | Report Extension | Final project report |

---

**End of Change Request**
