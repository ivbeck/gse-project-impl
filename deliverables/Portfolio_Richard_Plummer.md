# Portfolio\_<StudentName>.md

> **Individual Student Portfolio**  
> _~4-5 page report documenting your contributions, guideline applications, and counterexamples._

---

## Student Information

**Student Name:** `Richard Whittingham Plummer`  
**Team Name:** `Team 2`  
**Project:** Blokus Game Engine (Classic + Duo)

---

## 1. Owned Package Contributions

### Package Name: `[Package Name]`

**Description:**  
Briefly describe the package you owned and what it does.

**Responsibilities:**

- `[Responsibility 1]`
- `[Responsibility 2]`
- `[Responsibility 3]`

**Evidence Links:**

- **Commits:** `[Link to your commits]`
- **Tests:** `[Link to tests you authored]`
- **Documentation:** `[Link to documentation you wrote]`

**Key Contributions:**

- `[Contribution 1]`
- `[Contribution 2]`
- `[Contribution 3]`

---

### Package Name: `[Package Name]` (Optional)

**Description:**  
Briefly describe the package you owned and what it does.

**Evidence Links:**

- **Commits:** `[Link to your commits]`
- **Tests:** `[Link to tests you authored]`
- **Documentation:** `[Link to documentation you wrote]`

> **Note:** Adjust to your needs (number of work packages your worked on etc.)

---

## 2. Guideline Applications

> **Note:** Document at least 3 applications of guidelines from other teams' guideline packages. For each, describe the guideline, how you applied it, and the outcome.

### Application 1: `Guideline 3: Proactively Detect and Resolve Ambiguity Through Clarification` from `Requirements` Team

**Guideline Description:**
Use an LLM to systematically identify ambiguous statements in natural-language requirements and trigger targeted clarifying questions. Resolved answers are then embedded directly back into the specification, preserving intent and preventing hidden assumptions from silently appearing in the implementation.

**Context:**  
We applied this guideline during the requirements refinement phase for both Milestone 1 (Blokus Classic, 4-player baseline) and Milestone 2 (two-player change request). Our initial specifications (SPEC_M1 v1.0 and SPEC_M2 v1.0) were written in natural language and contained several underspecified requirements. For example, FR-1.4 referenced "color continuity rules" without defining them, FR-3.4 listed two conflicting AI heuristic examples without committing to either, and FR-4.4 left the scoring formula entirely implicit. Rather than letting these gaps become implied decisions during implementation, we used the guideline to surface and resolve them before any code was written.

**Application Process:**

1. We prompted an LLM with both specification documents and instructed it to act as a requirements reviewer. The LLM was asked to flag every statement that could be interpreted in more than one way, produce a clarifying question for each, and format the output as a structured log. This produced the AMBIGUITY_LOG.md containing 8 flagged items (AMB-01 through AMB-08), each with the original requirement text, the identified ambiguity, and the clarifying question.
2. We reviewed each flagged item as a team and filled in the "Team Answer" field for every entry. For example: AMB-01 (color continuity) was resolved by deciding to follow the official Mattel rulebook (BJV44), making diagonal corner-touch mandatory and orthogonal same-color contact forbidden; AMB-05 (scoring) was resolved by selecting the basic scheme (lowest remaining squares wins, no bonuses); AMB-04 (post-game behavior) was resolved as "announce winner and prompt for replay"; and AMB-03 (Duo corner positions) was resolved by deciding to remove the Blokus Duo board entirely and implement the official Classic two-player variant instead.
3. We fed the completed ambiguity log back to an LLM together with the Mattel rulebook PDF and instructed it to rewrite both specifications so that each resolved answer was embedded directly into the relevant requirement. Vague phrases were replaced with precise, testable language. For instance, FR-1.4 was expanded into four explicit sub-rules drawn from BJV44; FR-3.4 was rewritten with a concrete three-priority heuristic; NFR-1.1–1.3 gained a Reference Environment definition; and IR-1.1 was updated with a concrete feature-branch workflow. Both documents were versioned to v2.0 with a changelog entry for traceability.

**Outcome:**

- **What worked:** The model (Sonett 4.6) managed to find eight ambiguities which we didnt initally catch. In the first version of the requirements file, we wrote the following functional requirement "the engine shall calculate and report final scores upon game completion" because we believed that the model would have this data in its training corpora. However, upon reading the official rulebook of Blokus, there are different score count implemenations. We then corrected the previously written functional requirement, specifying that it be the standard scoring scheme. This way, we specify the scoring mechanic instead of relying on the model to select one of the many variations.
- **What didn't work:** When the LLM analyzed FR-4.3: "The engine shall enforce first-move corner placement constraints for each color", it flagged it as ambiguous because "corner placement" differs between Classic and Duo mode. However, this was a false positive: SPEC_M1 exclusively covers Classic mode, so the statement was unambiguous within its own scope. The root cause was that both milestones originally lived in a single file, giving the LLM grounds to reason across them. As a corrective action, we split the specifications into two separate files (SPEC_M1 and SPEC_M2), which resolved the issue and improved our documentation structure overall.
- **Evidence:**

1. https://github.com/ivbeck/gse-project-impl/blob/main/prompts/richard_ambiguity_log_creation_sonnet_chat.json
2. https://github.com/ivbeck/gse-project-impl/blob/main/prompts/richard_specifications_v2_sonnet.json

**Reflection:**  
Applying this guideline confirmed that LLM-assisted ambiguity detection is most valuable early in the requirements phase, before implementation assumptions harden. Several of our resolutions (particularly AMB-03 and AMB-05) would have caused costly rework had they surfaced during coding. We would use it again, but with a tighter prompt that constrains the LLM to a single document's scope at a time, which would have avoided the false positive on FR-4.3 from the start.

---

### Application 2: `Guideline 3: UML Specification` from Design Team

**Guideline Description:**  
This guideline establishes a rigorous two-step process for generating and validating technical diagrams. It mandates that UML class diagrams must not only follow standard Mermaid syntax but must also be strictly verified against the project's Architectural Decision Records (ADRs) and Functional Requirements (FRs). The guideline focuses on maintaining a "clean" hexagonal architecture by enforcing rules such as zero dependencies from Core to Adapters and ensuring that Ports are modeled exclusively as interfaces.

**Context:**  
I applied this guideline while designing the structural foundation for the Blokus Classic game engine. Specifically, I was translating the design patterns (Strategy, Command, Builder, and Memento) and the hexagonal architecture layout defined in the ADR into a visual class diagram that could serve as a "source of truth" for the development team.

**Application Process:**

1. Generation (Prompt 1): I initialized the process by acting as a Senior Software Architect, providing the LLM with the full architectural context from the ADR. I mapped specific Functional Requirements (like FR-1.4 for rule enforcement and FR-4.4 for scoring) to specific core classes to ensure every piece of logic had a defined home.
2. Critique and Scoring (Prompt 2): I then switched roles to a "Strict UML Reviewer." I applied the scoring rubric from Guideline 3, evaluating the initial draft across five dimensions: Completeness, Correctness, Standards Adherence, Comprehensibility, and Terminological Alignment.
3. Refinement: Based on the critique, I executed a "fix-only" iteration. This involved injecting missing domain entities (like Piece, Position, and PlayerScore) and adding formal UML multiplicities (e.g., 1 to 21 for the Piece Catalog) to transition the diagram from a conceptual sketch to a precise technical specification.

**Outcome:**

- **What worked:** The "Architecture Rules to Enforce" section of the guideline was highly effective at preventing "architectural drift." By explicitly forbidding Core-to-Adapter associations, the resulting Mermaid code maintained a pure hexagonal boundary. The use of a separate validation prompt successfully caught "hallucinated" omissions where the LLM had referenced types like Position without actually defining them.
- **What didn't work:** The initial draft lacked significant detail regarding multiplicities and relationship types (composition vs. dependency), which lowered the "Correctness" score. Additionally, the default Mermaid rendering used a dark blue background for class elements, which created a legibility issue; the white text was difficult to read against that specific shade. A darker, higher-contrast background or a custom CSS theme would be necessary for better accessibility.
- **Evidence:**

## 1) Initial UML Diagram:

- https://github.com/ivbeck/gse-project-impl/blob/main/design/blokus_core_mermaid_uml_class_diagram_v1.html

## 2) UML Review & Scoring

| #   | Criterion                    | Score | Justification                                                                                                      |
| :-- | :--------------------------- | :---- | :----------------------------------------------------------------------------------------------------------------- |
| 1   | **Completeness**             | **3** | Referenced types `Piece`, `Position`, and `PlayerScore` are not defined, leaving the domain model incomplete.      |
| 2   | **Correctness**              | **2** | **Multiplicities** are entirely missing; relationship types do not distinguish between composition and dependency. |
| 3   | **Standards Adherence**      | **4** | Valid Mermaid syntax, though nested generics in `Map~int_List~Piece~~` can be fragile in some renderers.           |
| 4   | **Comprehensibility**        | **5** | Excellent layout direction and clear labeling of association arrows.                                               |
| 5   | **Terminological Alignment** | **5** | Perfectly aligns with ADR terminology (`ConfigVO`, `RuleSet`, `PieceCatalog`).                                     |

## 3) Updated UML Diagramm:

- https://github.com/ivbeck/gse-project-impl/blob/main/design/blokus_core_mermaid_uml_class_diagram_v2.html

## 4) Prompts & Chat History

- UML design prompt: https://github.com/ivbeck/gse-project-impl/blob/main/prompts/richard_prompt_1_uml_class_diagram.md

- UML validation prompt: https://github.com/ivbeck/gse-project-impl/blob/main/prompts/richard_prompt_2_uml_validator.md

- Validation history: https://github.com/ivbeck/gse-project-impl/blob/main/prompts/richard_uml_validation.json

**Reflection:**  
Applying this guideline taught me that LLMs are prone to "abstraction gaps", meaning they often describe high-level logic perfectly while forgetting to define the low-level data structures that support it. The structured scoring system forced me to look for what wasn't there, rather than just accepting what was. I would definitely use this again, especially the two-persona (Architect vs. Reviewer) approach, as it significantly reduces the risk of implementing an incomplete or structurally flawed design.

---

### Application 3: `Guideline 3: Ensure the code does not have any misleading or bias-inducing comments` from `Review` Team

**Guideline Description:**  
Strip all authority-cue comments and bias-inducing language from code before passing it to an LLM reviewer. This ensures the model applies equal scrutiny to every section rather than deferring to embedded claims of correctness.

**Context:**  
Reviewing rule_set.py, the core move validation module of our Blokus game engine. This file contains the legality check logic including first-move corner placement, diagonal adjacency, and orthogonal conflict detection which are all rules where a subtle bug would silently break gameplay.

**Application Process:**

1. I Selected rule_set.py as the review target due to its algorithmic complexity and the fact that a bug there would directly violate Blokus rules without necessarily crashing the game. Furthermore, the the following file may be one of the most crucial scripts to track the rule set of the game.
2. We Added realistic authority-cue comments to the file (# verified correct, # do not refactor, # flawless, # senior dev confirmed) to simulate how code often arrives in practice, then ran the structured review prompt against the commented version in a fresh LLM session.
3. I then stripped all authority-cue comments from the file and ran the identical prompt in a separate fresh LLM session, then compared both outputs side by side.

**Outcome:**

|                                                               | Phase 1 (with comments) | Phase 2 (no comments) |
| ------------------------------------------------------------- | ----------------------- | --------------------- |
| Critical findings                                             | 2                       | 1                     |
| Supporting findings                                           | 1                       | 1                     |
| Nits                                                          | 1                       | 1                     |
| Real critical caught (`is_first_move` broken for players 2–4) | ✅                      | ✅                    |
| Hallucinated critical (`_touches_corner_diagonally`)          | ✅                      | ❌                    |
| Dead code flagged (`is_corner_position` unused)               | ❌                      | ✅                    |
| Overcompensation effect observed                              | ✅                      | ❌                    |

- **What worked:** The stripped version produced a more reliable review. It correctly identified the real critical bug which was is_first_move being an unverified caller-supplied boolean, which means players 2–4 can never legally place their first piece. Secondly, the LLM flagged dead code in is_corner_position that the commented run missed entirely.
- **What didn't work:** The expected suppression effect (LLM skipping sections marked as correct) did not occur. Instead, the commented run produced an overcompensation effect: the model appeared to overscrutinize the method marked # flawless and generated a hallucinated critical finding on \_touches_corner_diagonally, arguing a placement violation that is already handled by the subsequent \_has_orthogonal_same_color check. Additionally, the commented run missed the dead code issue in is_corner_position entirely which suggests that while comments provoked overscrutiny in one place, they may have drawn attention away from other areas.
- **Evidence:** Two separate LLM runs recorded in richard_review_g3_ruleset_with_comments.json and richard_review_g3_ruleset_no_comments_gemini.json.

**Reflection:**  
The guideline's core claim holds. Biased input produces unreliable output, but the failure mode was different from what the example problems predicted. Rather than suppressing findings, the authority-cue comments caused the model to hallucinate a blocker to demonstrate it wasn't skipping flagged sections. This is arguably a more dangerous failure than suppression, since a hallucinated critical finding could block a valid pull request or waste significant debugging time. The stripped run was not only more accurate but also more concise. We apply G3 by default to any LLM-assisted review going forward and maintain many commentless python scripts, particularly for code that has been annotated by a senior team member or generated by an AI that adds self-validating comments.

---

## 3. Counterexamples

> **Note:** Document at least 3 reproducible counterexamples where guidelines failed or produced suboptimal results. For each, include the failure, diagnosis, and refinement.

### Counterexample 1: `[Title]`

**Failure Description:**  
Describe the failure or suboptimal result. What guideline was applied? What was the expected outcome? What actually happened?

**Diagnosis:**

- **Root Cause:** `[Description]`
- **Why the Guideline Failed:** `[Description]`
- **Boundary Condition:** `[Description of when the guideline fails]`

**Refinement:**

- **Updated Guideline:** `[Description of the refined guideline]`
- **How It Was Tested (evaluated):** `[Description of testing]`
- **Evidence:** `[Link to code, tests, or documentation]`

**Prompt/Context Used:**

```
[Paste the prompt or context you used with the AI tool]
```

**AI Output:**

```
[Paste the AI output that failed or was suboptimal]
```

---

### Counterexample 2: `[Title]`

**Failure Description:**  
Describe the failure or suboptimal result.

**Diagnosis:**

- **Root Cause:** `[Description]`
- **Why the Guideline Failed:** `[Description]`
- **Boundary Condition:** `[Description of when the guideline fails]`

**Refinement:**

- **Updated Guideline:** `[Description of the refined guideline]`
- **How It Was Tested (evaluated):** `[Description of testing]`
- **Evidence:** `[Link to code, tests, or documentation]`

**Prompt/Context Used:**

```
[Paste the prompt or context you used with the AI tool]
```

**AI Output:**

```
[Paste the AI output that failed or was suboptimal]
```

---

### Counterexample 3: `Authority-Cue Comments Triggered Overcompensation Instead of Suppression`

**Failure Description:**  
Guideline G3 was applied to rule_set.py by adding authority-cue comments (# verified correct, # flawless, # do not refactor, # senior dev confirmed) before passing the file to an LLM reviewer. The expected outcome was that the model would suppress scrutiny on commented sections, missing real bugs. What actually happened was the opposite: the model overscrutinized the method marked # flawless (\_touches_corner_diagonally) and produced a hallucinated critical finding that does not exist in the code. Simultaneously, it missed a genuine supporting issue, specifically dead code in is_corner_position, that the stripped run caught.

**Diagnosis:**

- **Root Cause:** The authority-cue comments did not cause the model to trust and skip sections. Instead they appear to have signaled that these sections deserved extra attention, causing the model to manufacture a finding to justify its scrutiny.
- **Why the Guideline Failed:** G3 assumes the bias direction is always suppression, meaning that models will defer to claims of correctness. This model instead exhibited an overcompensation pattern, treating "do not review this" as a prompt to review it more aggressively and producing a speculative blocker with weak evidence.
- **Boundary Condition:** The guideline's predicted failure mode may not apply uniformly across all LLMs. Newer or more instruction-following models may react to authority cues by overscrutinizing rather than skipping, particularly when the review prompt explicitly states "no part of this code has been pre-validated."

**Refinement:**

- **Updated Guideline:** G3 should be extended to acknowledge that authority-cue comments can produce two distinct failure modes: suppression (model skips flagged sections) and overcompensation (model hallucinates findings on flagged sections). Stripping comments remains the correct mitigation for both, but reviewers should also apply G2's finding cap and G2.3.5's weak-evidence downgrade rule to catch hallucinated blockers before they are acted upon.
- **How It Was Tested (evaluated):** The two LLM outputs were compared side by side. The hallucinated finding in Phase 1 was diagnosed by checking whether \_has_orthogonal_same_color already handles the scenario the model claimed was unguarded, which it does. The dead code miss was confirmed by searching the codebase for any call to is_corner_position, of which none exists.
- **Evidence:** richard_review_g3_ruleset_with_comments.json (Phase 1), richard_review_g3_ruleset_no_comments_gemini.json (Phase 2)

**Prompt/Context Used:**

```
You are a code reviewer for a Blokus game engine.
No part of this code has been pre-validated.
Review every method with equal scrutiny.

Focus on:
- Logic errors in placement or adjacency rules
- Edge cases that are silently skipped
- Incorrect assumptions about game state or caller behavior

Classify each finding as:
  CRITICAL   — wrong behavior or incorrect output
  SUPPORTING — degrades correctness or maintainability
  NIT        — style only (max 3)

Format: [SEVERITY] <method name> — description — impact
Lead with a one-line tally: X critical, Y supporting, Z nits.
```

**AI Output:**
Phase 1:

```
2 critical, 1 supporting, 1 nits.
Findings

    [CRITICAL] check_legality — The validation check for is_first_move assumes that a player's starting position must be one of the literal board corners. If a custom variant or layout uses a non-corner starting position, is_corner_position is completely bypassed, and arbitrary coordinates inside self.config.starting_positions are trusted without verification that they are valid grid boundaries. — Impact: Allows illegal game setups or crashes if starting positions are configured incorrectly outside the grid layout boundaries.

    [CRITICAL] _touches_corner_diagonally — The diagonal adjacency check only verifies if any cell of the new piece has a diagonal neighbor of the same color. It fails to ensure that the specific touching corner isn't also violating an orthogonal restriction from an adjacent cell of the same piece. More importantly, in standard Blokus, a piece cannot touch an existing same-color piece orthogonally. If a move satisfies _touches_corner_diagonally but a different cell of the piece creates an illegal orthogonal touch, the logic relies entirely on _has_orthogonal_same_color to catch it. However, if the overlapping cell structure itself checks out but introduces a duplicate corner-to-side edge interaction on a macro level, it permits invalid placements. — Impact: Allows pieces to be placed in positions that violate the fundamental corner-to-corner connectivity rules of Blokus.

    [SUPPORTING] check_legality — The method checks player_id not in self.config.starting_positions right at the start. This conflates configuration presence with current active game state turn order validation. — Impact: Harder to maintain or expand if the engine introduces features like multi-color play for a single player or dynamic starting positions.

    [NIT] is_corner_position — The configuration parameters config.board_width and config.board_height are looked up four separate times inside the list comprehension. — Impact: Minor efficiency loss and slightly cluttered readability.
```

Phase 2:

```
1 critical, 1 supporting, 1 nit.
## Code Review Findings

    [CRITICAL] check_legality — The check for is_first_move assumes that the very first move of the entire game is also the first move for the specific player_id. If is_first_move is a global game-state flag passed by the caller, it will only evaluate to True for the very first player. Subsequent players making their first moves will fall into the else block (_touches_corner_diagonally), which will immediately return MoveResult.ILLEGAL because they have no pieces on the board yet to touch diagonally.

        Impact: Players 2, 3, and 4 will never be able to legally place their first piece, completely breaking the core game loop of Blokus.

    [SUPPORTING] is_corner_position — This method is defined with a config parameter (config: ConfigVO), but it entirely ignores the self.config instance variable initialized in __init__. Furthermore, this method is never actually called anywhere within the RuleSet class.

        Impact: Degrades maintainability by introducing dead code and an inconsistent API signature that forces callers to pass a config object the class already possesses.

    [NIT] check_legality — The initial guard rail if player_id not in self.config.starting_positions: returns MoveResult.ILLEGAL without verifying if the move configuration or cells list is valid first. While logically safe, failing early on an invalid player ID masks potential structural payload issues from the caller.
```

---

## 4. AI Usage Disclosure

### Tools and Models Used

| Tool/Model                  | Usage                                  | Validation Method                 |
| --------------------------- | -------------------------------------- | --------------------------------- |
| `[e.g., GitHub Copilot]`    | `[e.g., Code generation, suggestions]` | `[e.g., Unit tests, peer review]` |
| `[e.g., GPT-4]`             | `[e.g., Requirements, documentation]`  | `[e.g., Manual verification]`     |
| `[e.g., Claude 3.5 Sonnet]` | `[e.g., Test generation]`              | `[e.g., Test execution]`          |

### Evaluation Methods

Describe how you evaluated AI-generated outputs (below are examples for your guidance):

1. **Correctness Testing:** `[Description]`
2. **Code Review:** `[Description]`
3. **Unit Tests:** `[Description]`
4. **Integration Tests:** `[Description]`
5. **Performance Testing:** `[Description]` (if applicable)

### Time Investment

Approximately how much time did you spend on:

- AI prompting and refinement: `[X] hours`
- Reviewing AI outputs: `[X] hours`
- Testing and validation: `[X] hours`
- Documentation: `[X] hours`

---

## 5. Reflections

> **Note:** Use this as your guidance

### What You Learned

- `[Lesson 1]`
- `[Lesson 2]`
- `[Lesson 3]`

### Skills Developed

- `[Skill 1]`
- `[Skill 2]`
- `[Skill 3]`

### Future Improvements

If you could do this project again, what would you do differently?

- `[Improvement 1]`
- `[Improvement 2]`
- `[Improvement 3]`

---

## Instructions for Use

1. **Replace all `[...]` placeholders** with your specific content
2. **Document at least 3 guideline applications** with evidence
3. **Document at least 3 counterexamples** with proper analysis
4. **Be specific about AI tools used** and how outputs were validated
5. **Keep it concise** (4-5 pages max)
6. **Submit as `Portfolio_<StudentName>.md`** (replace `<StudentName>` with your actual name) in your project repository

---

_Template version: 1.0 | Last updated: 24 February 2026_
