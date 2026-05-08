# Ambiguity Log — Blokus Configurable Game Engine

**Based on:** SPEC.md v1.0  
**Purpose:** Track ambiguous requirements, team-resolved answers, and resulting spec updates.  
**Process:** Fill in the "Team Answer" column for each item, then embed resolved answers back into SPEC.md.

---

## How to Use This File

1. Review each flagged ambiguity below.
2. Discuss as a team and write your answer in the **Team Answer** field.
3. Once resolved, update the corresponding requirement in SPEC.md to embed the answer.
4. Mark the item **Status** as `Resolved`.

This log also serves as evidence for **AR-1.1** (Guideline Application) and **AR-1.2** (Counterexamples) in your final report.

---

## Ambiguity Items

---

### AMB-01

| Field | Content |
|-------|---------|
| **Requirement ID** | FR-1.5 |
| **Original Text** | "The engine shall enforce the Blokus piece placement rules: orthogonal adjacency constraints and color continuity rules." |
| **Ambiguity** | "Color continuity rules" is undefined. Does it mean (a) same-color pieces must connect corner-to-corner (diagonal touch required for each new placement), or (b) same-color pieces must never touch orthogonally but diagonal touch is optional? |
| **Clarifying Question** | Must each new piece of a color touch an existing piece of the same color diagonally (corner-to-corner), or is diagonal contact merely allowed but not required? |
| **Team Answer** | *(fill in)* |
| **Status** | 🔴 Open |
| **SPEC.md Update** | Rewrite FR-1.5 to explicitly state diagonal corner-touch requirement (or lack thereof). |

---

### AMB-02

| Field | Content |
|-------|---------|
| **Requirement ID** | FR-3.4 |
| **Original Text** | "Simple AI players shall select moves using a deterministic heuristic (e.g., largest available piece, first valid placement)." |
| **Ambiguity** | The two examples suggest different strategies — "largest available piece" and "first valid placement" are not the same heuristic. It is unclear which one is actually required, or if the team can freely choose. |
| **Clarifying Question** | Is the AI heuristic fixed (e.g., always pick the largest piece), or can the team choose any deterministic heuristic as long as it is documented? |
| **Team Answer** | *(fill in)* |
| **Status** | 🔴 Open |
| **SPEC.md Update** | Replace the "(e.g., ...)" with the specific heuristic the team will implement. |

---

### AMB-03

| Field | Content |
|-------|---------|
| **Requirement ID** | FR-4.3 |
| **Original Text** | "The engine shall enforce first-move corner placement constraints for each color." |
| **Ambiguity** | "Corner placement" means different things in Classic vs Duo. In Classic, each color starts in one of the four board corners. In Duo, the starting positions are specific interior squares, not the literal board corners. Does this requirement apply to both modes, and what exactly counts as a "corner" in Duo? |
| **Clarifying Question** | In Duo mode, does "corner placement" refer to the standard Duo starting squares (e.g., (5,5) and (9,9) on a 14×14 board), or to the literal corners of the 14×14 grid? |
| **Team Answer** | *(fill in)* |
| **Status** | 🔴 Open |
| **SPEC.md Update** | Clarify FR-4.3 to specify exact starting positions for each mode, or reference the rule book explicitly for each. |

---

### AMB-04

| Field | Content |
|-------|---------|
| **Requirement ID** | FR-4.4 |
| **Original Text** | "The engine shall detect and handle game termination conditions." |
| **Ambiguity** | "Handle" is vague. Does it mean (a) simply stop accepting moves and display a result, (b) prompt the user to start a new game, (c) exit the program, or (d) something else? |
| **Clarifying Question** | When the game ends, what should the system do after reporting the result — exit, prompt for replay, or return to a menu? |
| **Team Answer** | *(fill in)* |
| **Status** | 🔴 Open |
| **SPEC.md Update** | Extend FR-4.4 to specify the exact post-termination behavior. |

---

### AMB-05

| Field | Content |
|-------|---------|
| **Requirement ID** | FR-4.5 |
| **Original Text** | "The engine shall calculate and report final scores upon game completion." |
| **Ambiguity** | The scoring method is not defined. In standard Blokus, the score is the sum of squares in unplayed pieces (lower is better), with bonuses for playing all pieces. It is unclear whether the bonus rules (+15 for all pieces placed, +5 if the last piece was the monomino) are included. |
| **Clarifying Question** | Should scoring follow the official Blokus rules including placement bonuses (+15 / +5), or is it simply the count of remaining unplaced squares? |
| **Team Answer** | *(fill in)* |
| **Status** | 🔴 Open |
| **SPEC.md Update** | Add scoring formula to FR-4.5 explicitly. |

---

### AMB-06

| Field | Content |
|-------|---------|
| **Requirement ID** | NFR-1.1, NFR-1.2, NFR-1.3 |
| **Original Text** | Performance targets: move validation ≤100ms, enumeration ≤500ms, serialization ≤200ms. |
| **Ambiguity** | No hardware baseline is specified. These targets are meaningless without knowing the reference machine (e.g., a modern laptop vs a CI server). A pass on one machine could be a fail on another. |
| **Clarifying Question** | What is the reference hardware or environment for measuring these performance targets (e.g., a standard university lab machine, a CI runner, the developer's laptop)? |
| **Team Answer** | *(fill in)* |
| **Status** | 🔴 Open |
| **SPEC.md Update** | Add a "Reference Environment" note to Section 3.1 specifying the hardware/OS baseline. |

---

### AMB-07

| Field | Content |
|-------|---------|
| **Requirement ID** | M1-AC-5 (Section 5.3, item 5) |
| **Original Text** | "The automated test suite shall achieve ≥90% coverage of core game logic." |
| **Ambiguity** | "Core game logic" is not defined. Does 90% coverage apply to all code, or only a specific subset of modules (e.g., the legality checker and move application)? Also, which coverage metric is meant — line, branch, or statement coverage? |
| **Clarifying Question** | Which modules count as "core game logic" for the 90% coverage target, and is the metric line coverage, branch coverage, or another? |
| **Team Answer** | *(fill in)* |
| **Status** | 🔴 Open |
| **SPEC.md Update** | Specify the coverage metric and which modules are in scope in Section 5.3. |

---

### AMB-08

| Field | Content |
|-------|---------|
| **Requirement ID** | M2-R3 |
| **Original Text** | "Duo-specific corner positions (diagonal symmetry)" |
| **Ambiguity** | The exact coordinates of the Duo starting positions are not specified. "Diagonal symmetry" describes the pattern but not the actual squares. Implementation teams may choose different coordinates. |
| **Clarifying Question** | What are the exact board coordinates (row, column) of the two starting positions in Duo mode on the 14×14 grid? |
| **Team Answer** | *(fill in)* |
| **Status** | 🔴 Open |
| **SPEC.md Update** | Replace "diagonal symmetry" with explicit coordinates (e.g., (4,4) and (9,9) using 0-indexed or 1-indexed notation — also clarify indexing). |

---

### AMB-09

| Field | Content |
|-------|---------|
| **Requirement ID** | M2-AC-2 (Section 6.4, item 2) |
| **Original Text** | "No code duplication shall occur between Classic and Duo implementations." |
| **Ambiguity** | "No code duplication" is an absolute statement that is practically unachievable (e.g., shared constants, test fixtures). Does this mean zero literal duplication, or is it a design intent that configuration-driven design should be used instead of copy-pasted logic? |
| **Clarifying Question** | Does "no code duplication" mean no copy-pasted game logic (acceptable standard), or is it a strict zero-tolerance rule including shared utility code? |
| **Team Answer** | *(fill in)* |
| **Status** | 🔴 Open |
| **SPEC.md Update** | Soften or clarify the wording to distinguish design intent from a strict zero-duplication rule. |

---

### AMB-10

| Field | Content |
|-------|---------|
| **Requirement ID** | IR-1.1 |
| **Original Text** | "Git repository with structured branching strategy" |
| **Ambiguity** | "Structured branching strategy" is not defined. This could mean Gitflow, trunk-based development, feature branches, or something else entirely. |
| **Clarifying Question** | Is a specific branching strategy required (e.g., Gitflow with main/develop/feature branches), or is any documented and consistently applied strategy acceptable? |
| **Team Answer** | *(fill in)* |
| **Status** | 🔴 Open |
| **SPEC.md Update** | Either name the required strategy or clarify that any documented strategy is acceptable. |

---

## Summary Table

| ID | Requirement | Status |
|----|-------------|--------|
| AMB-01 | FR-1.5 — Color continuity definition | 🔴 Open |
| AMB-02 | FR-3.4 — AI heuristic specification | 🔴 Open |
| AMB-03 | FR-4.3 — Corner placement in Duo mode | 🔴 Open |
| AMB-04 | FR-4.4 — Post-termination behavior | 🔴 Open |
| AMB-05 | FR-4.5 — Scoring formula and bonuses | 🔴 Open |
| AMB-06 | NFR-1.x — Performance reference environment | 🔴 Open |
| AMB-07 | M1-AC-5 — Coverage metric and scope | 🔴 Open |
| AMB-08 | M2-R3 — Exact Duo starting coordinates | 🔴 Open |
| AMB-09 | M2-AC-2 — Definition of "no code duplication" | 🔴 Open |
| AMB-10 | IR-1.1 — Branching strategy definition | 🔴 Open |

---

*Generated as part of Guideline 3 application: Proactively Detect and Resolve Ambiguity Through Clarification.*
