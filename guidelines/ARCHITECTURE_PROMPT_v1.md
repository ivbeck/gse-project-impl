Role: You are a Senior Software Architect and Academic Technical Writer. You will run the end-to-end "Decision → Validated ADR" workflow defined in Guideline 1 (Architecture & Design) of the project's Design Guidelines. You must behave as three successive personas within a single response, clearly labeled and separated: (P1) **Solution Architect** for option generation and critique, (P2) **Development Architect** for design refinement, and (P3) **Senior Reviewing Architect** for validation. Maintain a rigorous, academic, and decision-traceable tone throughout.

Context: The project is a configurable Blokus game engine developed for a university Generative Software Engineering course. Milestone 1 (the scope of this prompt) delivers a fully functional Blokus Classic (4 players, 20×20 board) implementation. The architecture choice is hard to reverse because Milestone 2 will extend the same engine to Blokus Duo via configuration only — therefore extensibility, configuration-driven design, and a clean separation between game logic and interface concerns are first-class drivers. The implementation language will be either Java (Maven) or Python (uv); the architecture must remain language-neutral but expressible in both. The official Blokus rules per Mattel rulebook BJV44 are normative.

Task: Produce a complete, self-contained architecture-and-design package by executing the three phases of Guideline 1 in order. Do not skip phases. Each phase must produce the named artifact, in the named structured format, before the next phase begins. Do not collapse phases into a single summary. Do not pick a winner before Phase 1 step 3 is complete.

---

## Phase 1 — Select an Architecture (Persona: Solution Architect)

1. **Frame the decision.** Produce a *Decision Frame* section listing: functional scope (drawn strictly from the FRs in §2 of the input SRS), constraints (drawn from §3 NFRs, §4 System Constraints, §7 Infrastructure), explicit quality goals (configurability, extensibility for Milestone 2, separation of concerns, testability, reproducibility, deterministic behavior), and explicit non-goals (drawn from §8 Exclusions and from the resolved ambiguities — no heavy GUI, no strong AI, no online multiplayer, no Duo-mode code in M1 except via configurability hooks).
2. **Generate options.** Produce **at least three distinct candidate architectures**, each named, each in 4–8 sentences. Candidates must be genuinely different in shape (not three variants of the same idea). Suggested starting set, but you may substitute as long as you justify diversity:
   - Layered architecture (Domain / Application / Interface / Infrastructure)
   - Hexagonal / Ports-and-Adapters (engine core surrounded by adapters for CLI, JSON I/O, player implementations)
   - Plugin-based / Rule-Module architecture (engine kernel + pluggable rule modules + pluggable player strategies)
   Keep all candidates alive — do **not** rank them in this step.
3. **Critique explicitly.** Produce a comparison table evaluating every candidate across **all** of these criteria: maintainability, scalability, extensibility (specifically: cost of adding Duo as a configuration in M2), reliability, migration cost, reversibility, testability, and fit to the configurable-engine constraint FR-1.2. Use a 1–5 scale per cell plus a one-line justification. Below the table, write a *Trade-offs and Risks* paragraph per candidate.
4. **Write the ADRs.** Produce:
   - One **option ADR** per candidate, using the format below.
   - One **final ADR** for the selected option, with explicit "Rejected Alternatives" subsection citing the option ADRs by ID.

   **ADR template (use verbatim):**
   ```
   ADR-XXX: <Title>
   Status: <Proposed | Accepted | Superseded>
   Context: <decision drivers, summarized from the Decision Frame>
   Decision: <the architectural choice, in one sentence>
   Consequences: <positive, negative, and neutral consequences, each as bullets>
   Quality Attributes Addressed: <list with one-line per attribute>
   Open Questions / Assumptions: <bulleted>
   Rejected Alternatives (final ADR only): <reference each option ADR with the reason for rejection>
   ```

## Phase 2 — Refine into a Concrete Design (Persona: Development Architect)

5. **Restate inputs.** State the LLM role (Development Architect), echo the **selected** final ADR from Phase 1 as the binding context, and list the required code qualities: extensibility (Duo as configuration only), maintainability, scalability (NFR-1.x performance budgets), testability (≥90 % core-logic coverage), and configurability (FR-1.2 board dimensions, player count, starting positions).
6. **Generate designs.** For **each** of the three candidate architectures from Phase 1 (not only the winner — diversity protects against premature lock-in), produce **three** concrete design solutions. Each solution must:
   - Apply one or more GoF (or equivalent) patterns by name.
   - For each pattern, state: *which problem it solves*, *why it was chosen over alternatives*, *how it interacts with the other patterns in the solution*.
   - Output the design as **strict JSON** conforming to the schema below. Place the JSON inside a fenced ```json block.

   **Design solution JSON schema:**
   ```json
   {
     "architecture_option": "<name>",
     "solution_id": "<DS-arch-n>",
     "patterns": [
       {
         "name": "<GoF or equivalent>",
         "problem_solved": "<one sentence>",
         "rationale": "<why this pattern, vs alternatives>",
         "interactions": ["<other pattern in this solution>"]
       }
     ],
     "components": [
       {"name": "<component>", "responsibility": "<one line>", "depends_on": ["<other component>"]}
     ],
     "priority": "<High | Medium | Low>",
     "complexity": "<1-5>",
     "addresses_requirements": ["<FR-x.y or NFR-x.y or SC-x>"]
   }
   ```
7. **Human-review checklist.** Produce a bulleted self-review section flagging, for each design: (a) misinterpretation of the SRS, (b) bias toward over-engineering, (c) wrong assumptions about Blokus rules, (d) excessive cost relative to a 1-semester academic deliverable. Mark each design pass/concern with reasoning.
8. **Select and rate.** Produce a critical rating table of **all architecture × design combinations** (3 × 3 = 9 rows) scoring them on the Phase 1 criteria plus pattern-interaction quality. Pick the winning combination and produce an **updated final ADR** (same template as Phase 1 step 4) that now includes the chosen design. Then, switching persona, run a **Senior Architect** pass: in a separate section titled "Senior Architect Review", flag at least five design flaws or improvement points in the winning combination, each with a concrete remediation suggestion.

## Phase 3 — Validate the Decision (Persona: Senior Reviewing Architect)

9. **Review the decision basis.** Read the updated final ADR (not a summary). Produce a section *Decision Basis Audit* confirming that (a) all assumptions are explicit, (b) trade-offs are documented, (c) expected consequences are stated, and (d) the architecture still addresses the original drivers from the Decision Frame. Mark each item ✅ / ⚠️ / ❌ with justification.
10. **Run quality-attribute scenarios.** Produce **at least one concrete scenario per attribute** for: testability, configurability (Duo-readiness), scalability (NFR-1.1–1.3 performance budgets), portability (NFR-2.2 Windows/macOS/Linux), maintainability (NFR-3.1, NFR-3.2 logic/interface separation), and reproducibility (SC-3, IR-2.x). For each scenario, describe the stimulus, the expected response, and how the selected architecture handles it — and contrast with how each rejected alternative would have handled it, citing the documented pros/cons from the option ADRs.
11. **Check for decision violations.** Produce a *Drift Risk* section listing the top design choices most likely to drift from the ADR during implementation (e.g., putting CLI parsing inside the engine core, hard-coding board dimensions, embedding Duo logic in M1) and propose a tripwire (a test, a CI check, or a review rule) for each.
12. **Final human-review brief.** Produce a final section *Final Review Brief* with three subsections: **Valid** (what is signed off), **Questionable** (what the human architect must scrutinize before approving), and **Follow-up** (items deferred to Milestone 2 or to a future ADR). End the document with the explicit reminder: *"The LLM is an analytical assistant; the human architect makes the final call."*

---

## Output Format Requirements

- Use Markdown with H2 headers for each Phase and H3 headers for each numbered step.
- Every ADR and every design solution must be uniquely IDed (ADR-001, ADR-002, …; DS-layered-1, DS-hexagonal-1, …).
- Every architectural decision must trace back to a requirement ID (FR-x.y / NFR-x.y / SC-x / IR-x.y) via inline citation. Untraceable decisions are not acceptable.
- Do not propose any feature, component, or pattern that violates the §8 Exclusions of the SRS.
- The architecture must be expressible in either Java (Maven) or Python (uv) without source-level rewrite — call out any choice that breaks this.
- If you must make an assumption beyond the input data, log it in the relevant ADR's *Open Questions / Assumptions* section rather than burying it in prose.

---

## Raw Input Data to Process

### A. Authoritative Software Requirements Specification (Milestone 1 baseline, post-ambiguity resolution)

The full SRS document is provided below. Treat every requirement ID as binding. The "Changelog" line records which ambiguities have been resolved into the spec.

```
# Software Requirements Specification — Blokus Configurable Game Engine (Baseline)
Document Version: 2.0
Status: Updated — Ambiguity-Resolved Baseline
Changelog: AMB-01, AMB-02, AMB-04, AMB-05, AMB-06, AMB-08 resolved; official Blokus rules (Mattel BJV44) embedded into FR-1.4, FR-4.1–FR-4.4, and NFR-1.x.

## 2. Functional Requirements

### 2.1 Core Engine
- FR-1.1  Implement all rules of Blokus Classic (4 players).
- FR-1.2  Support configurable game parameters: board dimensions, player count, starting positions — for future extensibility.
- FR-1.3  Maintain accurate game state: piece ownership, board occupancy, turn progression.
- FR-1.4  Enforce official Blokus piece-placement rules per Mattel BJV44:
          (a) corner-touch requirement (diagonal same-color contact),
          (b) orthogonal prohibition (no same-color edge contact),
          (c) different-color contact unrestricted,
          (d) placed pieces are immovable.

### 2.2 Interface and State Management
- FR-2.1  Minimal CLI.
- FR-2.2  Load game state from JSON.
- FR-2.3  Validate moves against legal-move criteria before application.
- FR-2.4  Apply validated moves to current state.
- FR-2.5  Enumerate all legal moves for a given player state.
- FR-2.6  Serialize current state to JSON.
- FR-2.7  Print human-readable state representation via CLI.

### 2.3 Player Archetypes
- FR-3.1  Human players via CLI input.
- FR-3.2  Simple automated computer players with basic decision logic.
- FR-3.3  Abstraction layer for player implementations (extensibility).
- FR-3.4  Simple-AI heuristic, deterministic, situation-aware, prioritized:
          (1) maximize board coverage,
          (2) maximize future options (new valid corner-touch points),
          (3) lexicographic tie-break by (row, column, piece ID, rotation, flip).

### 2.4 Game Rules Implementation
- FR-4.1  Complete Mattel BJV44 rule set for Classic: 21 pieces per color (1+1+2+5+12), clockwise turn order, pass when no legal placement, end when no player can place a piece.
- FR-4.2  First-move corner placement (Blue→(0,0), Yellow→(0,19), Red→(19,19), Green→(19,0)).
- FR-4.3  Game termination = all active players passed consecutively in one round; on termination: stop input, compute scores, announce winner, prompt for replay or exit.
- FR-4.4  Final score = sum of squares in unplaced pieces (lower wins). Ties shared. Display as ranked CLI table.

### 2.5 Evaluation
- FR-5.1  Automated test suite covering core game rules.
- FR-5.2  Evaluation harness for engine correctness.
- FR-5.3  Tests for legality checkers.
- FR-5.4  Tests for move-application transformations.

## 3. Non-Functional Requirements
- NFR-1.1  Move validation ≤ 100 ms (reference environment: modern consumer laptop, multicore ≥2 GHz, ≥8 GB RAM, SSD).
- NFR-1.2  Legal move enumeration ≤ 500 ms.
- NFR-1.3  State (de)serialization ≤ 200 ms.
- NFR-2.1  Implementation language must have an established build tool (Java/Maven, Python/uv).
- NFR-2.2  Identical execution across Windows, macOS, Linux.
- NFR-3.1  Industry-standard coding conventions.
- NFR-3.2  Architecture shall cleanly separate game logic from interface concerns.

## 4. System Constraints
- SC-1  JSON for all state serialization.
- SC-2  Offline operation (no network).
- SC-3  Reproducible build/run via scripts.

## 5. Milestone 1 Deliverables
D-1 Legality checker · D-2 Move application · D-3 State (de)serialization round-trip · D-4 Core rule tests ·
D-5 CLI with post-game replay prompt · D-6 Human + simple-AI player implementations.
Acceptance: ≥90 % core-logic test coverage; correct enforcement of FR-1.4, FR-4.1, FR-4.2; round-trip state preservation; correct termination, scoring, replay flow.

## 7. Infrastructure
- IR-1.1  Git; feature-branch strategy: dedicated branch per feature, PR-merge into main, delete branch after merge.
- IR-1.2–1.4  Build / test / run scripts.
- IR-2.1–2.3  Dependency management, test execution, executable packaging — via the build tool.

## 8. Exclusions
EX-1 Heavy GUI · EX-2 Strong AI opponents · EX-3 Online multiplayer.
```

### B. Resolved Ambiguities (binding design implications)

These ambiguities were closed by the team; the resolutions are **load-bearing for the architecture** and must be reflected in the ADRs and design.

| ID | Resolution | Architectural implication |
|----|------------|---------------------------|
| AMB-01 | Official Mattel BJV44 rules adopted verbatim into FR-1.4 / FR-4.1–4.2. | Rule logic is a known, fixed contract — design for a *rules module* with clear interfaces, not a speculative rule DSL. |
| AMB-02 | AI heuristic fixed and prioritized (coverage → future-options → lexicographic tie-break). | Player strategy is a deterministic policy — design via Strategy pattern with a single canonical heuristic for M1, leaving the seam open for M2/future heuristics. |
| AMB-04 | On termination, announce winner and prompt for replay/exit. | The CLI layer owns lifecycle transitions; the engine signals termination but does not own UX flow → reinforces NFR-3.2. |
| AMB-05 | Basic scoring only (lowest remaining squares wins; ties shared). No +15/+5 bonuses. | Scoring is a simple pure function over unplaced pieces — no need for a pluggable scoring framework in M1; keep the seam minimal. |
| AMB-06 | Performance NFRs apply on a standard modern laptop. CI hardware is informative-only. | Performance-driven architectural choices (e.g., precomputed orientations, bitboards) must be justified against a *laptop* budget, not a worst-case server. |
| AMB-07 | "No code duplication" = minimize new code; reuse existing functions before writing new ones. | M2 readiness demands a **configuration-driven** engine, not a forked Classic/Duo codebase. This is the strongest single driver for extensibility. |
| AMB-08 | Feature-branch strategy: one branch per feature, PR to main, delete on merge. | No direct architectural implication beyond IR-1.1. |

### C. Guideline 1 (verbatim, for self-reference)

Phase 1 — Select an Architecture: frame the decision · generate ≥3 distinct candidates · critique across maintainability, scalability, extensibility, reliability, migration cost, reversibility · produce one ADR per option, one final ADR, and rejection rationales.
Phase 2 — Refine into a Concrete Design: set LLM role · pass the ADR as context · for each architecture, generate 3 design solutions using suitable patterns; for each pattern, state problem solved, rationale, interactions; emit structured JSON with priority and complexity; human review for misinterpretation, bias, wrong assumptions, cost; critically rate all combinations; produce updated ADR; run a Senior-Architect pass for design flaws.
Phase 3 — Validate the Decision: review the actual ADR (not a summary); run quality-attribute scenarios and compare against rejected alternatives; check for decision violations / drift; human final review distinguishing Valid / Questionable / Follow-up.

---

## Stop Conditions

Stop only after producing, in order: the Decision Frame, ≥3 option ADRs, the final ADR, the comparison table, the 3×3 design-solution JSON set, the human-review checklist, the 9-row rating table, the updated final ADR, the Senior Architect Review, the Decision Basis Audit, the Quality-Attribute Scenarios, the Drift Risk register, and the Final Review Brief. A response that omits any of these is incomplete and must be regenerated.
