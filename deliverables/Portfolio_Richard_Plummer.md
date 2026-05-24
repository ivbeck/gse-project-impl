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
3. Refinement: Based on the critique, and as per the guideline, the model provides suggested fixes to the UML diagramm which make up the second updated version.

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

### Application 4: `Guideline 4: Approaches for Improving Comprehensive Reasoning for Complex Code` from `Review` Team

**Guideline Description:**  
Structure the review prompt to force the LLM to reason before judging. This involves assigning a domain-specific persona, requiring the model to restate the code as pseudocode before reviewing it, and demanding step-by-step chain-of-thought reasoning for each finding before a severity classification is assigned.

**Context:**  
Reviewing scoring.py, which contains the scoring logic for both the standard and Duo variants of the Blokus game engine. This file was chosen because it contains subtle algorithmic assumptions in bonus conditions, score calculations, and a factory function that could silently misconfigure the scoring system at runtime. Furthermore, I decided to not apply this guideline to rule_set.py as guideline three has already covered it and most likely would not uncover any new knowledge about the code quality.

**Application Process:**

1. I selected scoring.py as the review target because its scoring logic contains implicit assumptions about shape matrix values, conditional bonus eligibility, and opposite sorting contracts between Scoring and DuoScoring that a surface-level review would likely miss.
2. I constructed a G4 prompt assigning the persona of a senior game engine architect, mandating a pseudocode restatement of every function and class before any findings were produced, and requiring step-by-step reasoning before each severity classification.
3. Aftewards, I ran the prompt in a fresh LLM session with Gemini Flash with the full contents of scoring.py appended, then evaluated each finding against the actual source code to determine whether the reasoning chain produced real findings or speculative ones.

**Outcome:**

- **What worked:** The mandatory pseudocode step forced the model to demonstrate comprehension before judging. This directly surfaced the critical sorting bug in DuoScoring.rank, where negating an already-negative score and sorting ascending inverts the leaderboard, placing losers first. The chain-of-thought reasoning made the diagnosis traceable and easy to verify. The piece_square_count assumption about binary shape values was also caught through the reasoning step rather than pattern matching.
- **What didn't work:** Finding 3 (asymmetric sorting contracts across implementations in build_scoring) is a valid architectural observation but does not constitute a concrete bug. The model classified it as supporting rather than a nit, slightly inflating the severity profile. The persona and CoT prompting did not prevent this borderline classification, suggesting that G4 improves reasoning quality but does not fully eliminate imprecise severity judgement.
- **Evidence:** richard_review_g4_scoring_gemini.json.

**Reflection:**  
Guideline 4 produced a higher quality reasoning logic than a standard review prompt most likely would have. The pseudocode restatement in particular is a strong forcing function: a model that cannot correctly restate what a function does in plain language has no business classifying it as correct or broken. The critical finding in DuoScoring.rank is a real bug that would have been easy to miss in a quick read, and the step-by-step reasoning made it immediately verifiable without having to re-read the source code carefully. The main limitation is that guideline 4 adds a substantial prompt overhead and produces longer outputs, which makes it less suitable for quick reviews of simple utility functions. Going forward, this guideline is likely best reserved for algorithmically dense modules where silent logical errors are the primary risk, rather than applied uniformly across an entire codebase.

---

## 3. Counterexamples

> **Note:** Document at least 3 reproducible counterexamples where guidelines failed or produced suboptimal results. For each, include the failure, diagnosis, and refinement.

### Counterexample 1: `Cross-Document Scope Leakage Caused a False Positive Ambiguity Flag`

**Failure Description:**  
Guideline 3 (Proactively Detect and Resolve Ambiguity Through Clarification) was applied to the Blokus requirements specification by prompting Sonnet 4.6 to scan SPEC.md and flag ambiguous statements. The expected outcome was that all flagged items would represent genuine ambiguities within the document. Instead, the model flagged FR-4.3 ("The engine shall enforce first-move corner placement constraints for each color") as ambiguous, arguing that "corner placement" differs between Classic and Duo mode. This was a false positive: SPEC_M1 exclusively covers the Classic 4-player game, making the statement unambiguous within its own scope.

**Diagnosis:**

- **Root Cause:** At the time of the scan, both milestone specifications (SPEC_M1 and SPEC_M2) existed within a single combined file. The model reasoned across both documents simultaneously, treating Duo mode constraints defined in SPEC_M2 as relevant context for evaluating SPEC_M1 requirements.
- **Why the Guideline Failed:** The guideline does not specify that each document should be scanned in isolation. Feeding a multi-scope document to the model without constraining its reasoning to a single scope gave it grounds to generate cross-document comparisons that were not meaningful within either document alone.
- **Boundary Condition:** The guideline produces false positives when the input document contains requirements from multiple scopes or milestones, or when related documents are provided together without explicit scope boundaries in the prompt.

**Refinement:**

- **Updated Guideline:** Constrain the LLM to a single document's scope per scan by adding an explicit instruction such as "Only flag ambiguities that are unresolvable within this document alone. Do not flag statements that are clear within this document's defined scope, even if related documents use different conventions." Additionally, split multi-milestone specifications into separate files before scanning.
- **How It Was Tested (evaluated):** After splitting SPEC_M1 and SPEC_M2 into separate files, the ambiguity scan was re-run on each document individually. FR-4.3 was no longer flagged, confirming that the false positive was caused by cross-document scope leakage rather than genuine ambiguity in the requirement itself.
- **Evidence:** richard_ambiguity_log_creation_sonnet_chat.json, richard_specifications_v2_sonnet.json

**Prompt/Context Used:**

```
Guideline 3: Proactively Detect and Resolve Ambiguity Through Clarification

[uploaded SPEC.md containing both SPEC_M1 and SPEC_M2]

Scan the requirements file and flag every statement that could be
interpreted in more than one way. Produce a clarifying question for
each and format the output as a structured ambiguity log.
```

**AI Output:**

```
AMB-03 — FR-4.3: What 'corner placement' means in Duo mode

Original text: "The engine shall enforce first-move corner placement
constraints for each color."

Ambiguity: The term 'corner placement' differs between Classic and Duo
mode. In Classic, each of the four colors starts from one of the four
board corners. In Duo mode, starting positions are not the literal board
corners. It is unclear which convention applies here.

Clarifying question: Does 'corner placement' refer strictly to the four
physical corners of the 20x20 board, or to the designated starting
positions for each variant?
```

---

### Counterexample 2: `Single-Shot Generation Omitted Multiplicities and Undefined Referenced Types`

**Failure Description:**  
The UML Specification guideline (Guideline 3 of the design team) was applied to generate a Mermaid class diagram for the Blokus game engine core. The prompt followed the guideline's Stage 2 decomposition principle by starting with a maximum of 8 core elements (as per guideline 3) and providing explicit constraints on notation, visibility markers, and relationship types. The expected outcome was a diagram scoring 4 or above across all five criteria. What actually happened was that the generated diagram scored 2 on Correctness and 3 on Completeness: multiplicities were entirely absent from all associations, and referenced types Piece, Position, and PlayerScore were used in method signatures and relationships without being defined as diagram elements.

**Diagnosis:**

- **Root Cause:** The generation prompt focused heavily on enforcing architectural constraints (no Core-to-Adapter dependencies, named state transitions, enumerations) but did not explicitly require multiplicities on every association. The model satisfied the stated constraints and ignored everything else, including structural completeness of referenced types.
- **Why the Guideline Failed:** Stage 2 of the guideline instructs to "assign associations with multiplicities" but does not mandate that every referenced type must appear as a defined class or interface. The model interpreted the 8-element cap as permission to omit supporting domain types rather than as a starting point to expand from.
- **Boundary Condition:** The guideline's decomposition principle (start small, expand iteratively) creates a tension with completeness requirements. When the model is capped at 8 elements but the prompt references more types implicitly through method signatures, it will produce a diagram that is syntactically valid but semantically incomplete.

**Refinement:**

- **Updated Guideline:** Add an explicit rule to Stage 2: "Every type referenced in a method signature or association must be defined as a diagram element, even if it is a simple value object. If the element cap would be exceeded, promote the missing type to the next iteration explicitly." Additionally, add a constraint to the generation prompt: "For every association arrow, you must specify a multiplicity on both ends."
- **How It Was Tested (evaluated):** The validation prompt (Prompt 2) was run in a fresh session against the v1 diagram. The scoring table produced a Correctness score of 2 and Completeness score of 3, which triggered the corrected v2 diagram output per the validator's output instructions. The v2 diagram was then checked manually to confirm multiplicities and missing types were added.
- **Evidence:** richard_prompt_1_uml_class_diagram.md, richard_prompt_2_uml_validator.md, richard_uml_validation.json

**Prompt/Context Used:**

```
You are a senior software architect.

Think step-by-step:
(a) Extract entities and roles from the requirements and architecture context above.
(b) Define attributes with concrete types and visibility markers (+, -, #).
(c) Decide inheritance and interfaces — ports are interfaces; adapters implement them.
(d) Assign associations with multiplicities and direction labels.
(e) Sanity-check the Mermaid syntax before outputting.

Then output ONLY valid Mermaid class diagram code. No prose, no explanation
outside the code block.

Constraints:
- Start with a maximum of 8 core elements (Core layer only) in this first pass.
- Use concrete types only — no <Type> placeholders.
- For every class or interface, add an inline Mermaid note referencing the
  Requirement ID it satisfies.
- For every method, add an inline comment with the Use Case ID and a short
  action description.
```

**AI Output:**

```
## UML Review & Scoring

| #   | Criterion                    | Score | Justification                                                  |
| :-- | :--------------------------- | :---- | :------------------------------------------------------------- |
| 1   | Completeness                 | 3     | Referenced types like Piece and Position are not defined.      |
| 2   | Correctness                  | 2     | Multiplicities are missing; relationship types are vague.      |
| 3   | Standards Adherence          | 4     | Valid Mermaid syntax used.                                     |
| 4   | Comprehensibility            | 5     | Clear layout and labeling.                                     |
| 5   | Terminological Alignment     | 5     | Aligns with ADR terminology.                                   |
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

| Tool/Model          | Usage                                                                                                                    | Validation Method                                                                                |
| :------------------ | :----------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------- |
| `Claude Sonnet 4.6` | Ambiguity detection and log generation for requirements specification (Guideline 3 — Requirements)                       | Manual team review of each flagged ambiguity against the specification                           |
| `Claude Sonnet 4.6` | Prompt construction for G3 and G4 review guidelines                                                                      | Manual verification that prompts matched guideline intent before use                             |
| `Gemini 3 Flash`    | UML class diagram generation from architectural context (Guideline 3 — Design)                                           | LLM-as-Judge validation pass using a separate fresh session with a structured scoring rubric     |
| `Gemini 3 Flash`    | UML diagram validation and scoring against rubric (Guideline 3 — Design)                                                 | Human architect review of v2 diagram against ADR and functional requirements                     |
| `Gemini 3 Flash`    | Code review of `rule_set.py` with and without authority-cue comments (Guideline 3 — Review)                              | Manual cross-comparison of Phase 1 and Phase 2 outputs; findings verified against source code    |
| `Gemini 3 Flash`    | Code review of `scoring.py` using persona, pseudocode restatement, and chain-of-thought prompting (Guideline 4 — Review) | Each finding traced back to source code manually to distinguish real bugs from hallucinated ones |

### Evaluation Methods

1. **Correctness Verification:** All LLM findings from code reviews were manually verified
   against the actual source files. For each flagged issue, the relevant method was re-read
   to confirm whether the described behavior was real or hallucinated. For example, the
   critical finding on `_touches_corner_diagonally` in the guideline 3 review was diagnosed as a
   false positive by confirming that `_has_orthogonal_same_color` already handles the
   claimed edge case.

2. **Output Comparison:** The two-phase guideline 3 review (with and without comments) served as
   a structured comparison process. Outputs were compared side by side to identify bias
   effects and assess finding quality across both runs.

3. **Source Tracing:** The critical bug identified in `check_legality` (`is_first_move`
   being an unverified caller-supplied boolean) was confirmed by manually tracing the call
   chain to verify that no internal validation exists within `RuleSet` itself.

4. **Manual Simulation:** The sorting bug identified in `DuoScoring.rank` by the G4
   review was verified by manually tracing the score calculation for a player with remaining
   squares, confirming that negating an already-negative score and sorting ascending would
   invert the leaderboard.

5. **Diagram Validation:** UML diagrams were evaluated in two passes. First, the v1
   diagram was rendered in the Mermaid Live Editor to confirm syntactic correctness. Second,
   a structured LLM-as-Judge session scored the diagram against a five-criterion rubric
   covering completeness, correctness, standards adherence, comprehensibility, and
   terminological alignment. Any criterion scoring below 4 triggered a corrected v2 output,
   which was then reviewed manually against the ADR and functional requirements.

### Time Investment

Approximately how much time did you spend on:

- AI prompting and refinement: 3
- Reviewing AI outputs: 7.5
- Testing and validation: 6
- Documentation: 8

---

## 5. Reflections

> **Note:** Use this as your guidance

### What You Learned

- Structured prompting techniques like personas, pseudocode restatement, and
  chain-of-thought reasoning (Guideline 4) produce more traceable and verifiable outputs than
  classic review prompts. When the model is forced to explain its reasoning before
  classifying a finding, hallucinated critiques become easier to identify and discard.
- Feeding multiple documents or scopes into a single LLM session without specific
  boundary constraints can causes the model to lose focus. The false positive in the ambiguity
  detection exercise (AMB-03) would have been avoided entirely by scoping the prompt to
  one document at a time.
- The LLM-as-Judge pattern is effective for diagram validation but requires a tightly
  constrained prompt. Without explicit instructions to avoid redesigning the class
  hierarchy, the validator tends to overstep its role and suggest structural changes
  rather than just fixing errors.

### Skills Developed

- Critical evaluation of LLM outputs, specifically distinguishing between real findings
  and hallucinated ones by tracing claims back to source code or specification documents.
- Structured documentation of AI-assisted workflows, including how to record prompts,
  outputs, and validation steps in a reproducible format. For this project, we mainly used JSON as the go-to standard.
- Applying a two-phase review process (generate then validate in separate sessions) to
  reduce hallucinations and improve output reliability across different guideline
  applications.

### Future Improvements

If you could do this project again, what would you do differently?

- Re-validate corrected outputs such as the v2 UML diagram with a second scoring pass
  to confirm that fixes did not introduce new issues, even if Guideline 3 of the Design
  team does not explicitly require it.
- Apply Guideline 4 of the Review team's prompting techniques to the UML generation step
  as well, by requiring the model to restate the architectural constraints in plain
  language before generating diagram code. This would likely catch missing type
  definitions earlier than the separate validation pass did.
- Run Guideline 3 and Guideline 4 of the Review team on the same
  file in separate sessions to produce a direct comparison of what each technique
  surfaces, which would strengthen the argument for when to use each guideline.

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
