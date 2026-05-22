# Portfolio_Petar.md

> **Individual Student Portfolio**
> *Documenting my contributions, guideline applications, and counterexamples for the Blokus Game Engine project.*

---

## Student Information

**Student Name:** Petar Malamov

**Team Name:** Team 2 - Coding
**Project:** Blokus Game Engine (Classic + Duo integration)

---

## 1. Owned Package Contributions

### Package: Requirements Input

**Description:**
I contributed early requirements documentation based on the provided personas and project constraints. This package was evaluated through human review and comparison against the team's requirements baseline.

**Responsibilities:**
- Convert persona-driven Blokus requirements into functional and non-functional requirement documentation.
- Reformat requirements into a table structure for easier review.
- Compare similar requirements outputs and remove discrepancies by keeping the first requirements document as the baseline because it covered the main points.

**Evidence Links:**
- **Commits:** `e0755b4` added the requirements prompt log to the repository.
- **Files/Documentation:** `prompts/petar_requirements_response.json`.
- **Validation:** Human review of persona influence, table completeness, and consistency with the selected requirements baseline.

**Key Contributions:**
- Produced persona-driven requirements influenced by learnability, fast setup, save/load expectations, accessibility, and readable GUI needs.
- Requested functional and non-functional requirements in table format.
- Documented how each persona influenced the resulting requirements.
- Resolved small discrepancies between similar requirements files by using the first file as the main baseline.

---

### Package: Milestone 1 Implementation Remediation and Web GUI Gameplay

**Description:**
I used a structured remediation session to check the existing Milestone 1 implementation for correctness issues, then owned several web GUI gameplay improvements and bug fixes after the initial FastAPI/browser interface existed. This included core move-safety fixes, Simple AI ranking, turn progression, canonical piece rendering, rotate/flip correctness, hover placement preview, human/AI setup, end-game output, no-move skipping, and returning to the main menu.

**Responsibilities:**
- Review existing `src/` game logic against `AGENTS.md`, `SPEC_M1.md`, `ADR.md`, and `CODING_PROMPT_v1.md`.
- Fix correctness defects in move validation, board mutation, memento restore, and Simple AI ranking without adding Duo/M2 behavior during the M1 remediation session.
- Keep GUI behavior in adapters/static/template files and prevent GUI code from entering `Core.*`.
- Preserve the existing visual theme while adding start, gameplay, and end-game flows.
- Add focused tests for each behavior and run the test suite after fixes.

**Evidence Links:**
- **Commits:** `e0755b4` M1 remediation and GUI refactoring, `d094b9a` prompt log for turn bug, `d2fa623` turn-flow fix, `1aca6cb` canonical piece mismatch fix, `ed41478` rotate/flip preview fix, `618972f` hover placement preview, `5348e95` human-player selection, `8b68253` end-game table and no-move skipping.
- **Files/Prompt logs:** `prompts/petar_gui_refactor.json`, `prompts/petar_debugging_players_turn.json`, `prompts/petar_debugging_correct_piece_in_gui.json`, `prompts/petar_debugging_rotation_in_preview_not_working.json`, `prompts/petar_coding+debugging_adding_placement_preview.json`, `prompts/petar_coding_player_amout_selection.json`, `prompts/petar_coding_gui_result_table.json`.
- **Tests:** `tests/core/test_board.py`, `tests/core/test_rule_set.py`, `tests/core/test_game_session.py`, `tests/adapters/test_simple_ai_player.py`, `tests/adapters/test_web_orchestrator.py`, `tests/adapters/test_web_gui_hover_preview_static.py`.

**Key Contributions:**
- Added board-level safety checks so invalid placements do not silently mutate the board (`Board.in_bounds`, overlap and out-of-bounds rejection).
- Strengthened `RuleSet` and `GameSession` checks for wrong turn, invalid orientation, reused pieces, occupied cells, and finished-game submissions.
- Improved `SimpleAiPlayer` from a lexicographic-only chooser into a deterministic heuristic: maximize coverage, then future corner points, then lexicographic tie-break.
- Added a golden JSON-state regression for deterministic AI selection.
- Fixed web turns so legal `/move` and `/pass` requests advance the session and illegal moves keep the current player.
- Exposed backend-canonical `/piece-catalog` data so the tray, preview, submitted `piece_id`, and backend `PieceCatalog` stay consistent.
- Added backend-derived `rotate_to` and `flip_to` transition maps and corrected piece definitions so pieces `6`, `9`, `11`, and `15` flip correctly and pieces `11` and `15` are distinct.
- Added delegated hover preview rendering that uses the same orientation submitted to the backend.
- Added a themed start screen and `/start` flow for choosing 1-4 human players; remaining seats are controlled by `SimpleAiPlayer`.
- Added end-game result table, winner display, skipped-player event banner, and `/reset` main-menu flow.

---

### Package: CLI Integration and Validation

**Description:**
I extended the CLI startup flow to support human-vs-AI player counts and fixed CLI board label alignment.

**Responsibilities:**
- Keep CLI-specific behavior in adapters/bootstrap and keep `Bootstrap` procedural.
- Add tests for CLI prompting, AI pass/move behavior, and board formatting.

**Evidence Links:**
- **Commits:** `520cc70` CLI grid alignment, `5348e95` CLI/Web player-count selection.
- **Files/Prompt logs:** `prompts/petar_debugging_fixed_cli_grid_view.json`, `prompts/petar_coding_player_amout_selection.json`.
- **Tests:** `tests/adapters/test_cli.py`, `tests/test_bootstrap.py`.

**Key Contributions:**
- Added `CLI.prompt_human_player_count(max_players)` with retry validation.
- Added `create_player_inputs()` and `run_turn()` wiring so CLI games can mix human and AI players deterministically.
- Fixed row/column label alignment for rectangular, single-digit, and double-digit CLI boards.

---

### Package: Merge Conflict Resolution and Duo Integration Merge

**Description:**
I resolved the final merge conflict between the GUI work and the Duo branch, preserving both valid feature sets and validating the integrated result.

**Responsibilities:**

- Inspect conflicted files and identify which behavior came from each branch.
- Preserve GUI lifecycle behavior, AI skip handling, Duo config/scoring/start-position data, and existing tests.
- Validate the resolved merge before it was committed.

**Evidence Links:**

- **Commits:** `8cc89d4` merge conflict resolution.
- **Files/Prompt logs:** `prompts/petar_merge_conflict_resolve.json`.
- **Tests/Validation:** `uv build`, `uv run pytest` with `176 passed`, `git diff --cached --check`, `tests/adapters/test_web_orchestrator.py`, `tests/test_bootstrap.py`.

**Key Contributions:**

- Resolved conflicts in `src/adapters/web_orchestrator.py`, `src/bootstrap.py`, `src/static/gui.js`, `src/static/style.css`, `src/web_main.py`, and related tests.
- Preserved the existing GUI start/end-game lifecycle and AI skip behavior.
- Preserved Duo mode wiring, starting-position state payloads, and scoring-rule behavior.
- Validated the integrated branch with build, full test suite, and diff checks.

---

## 2. Guideline Applications

### Application 1: **Detailed Personas for Human-Centric Requirements** - Requirements Team 4, Guideline 2

**Guideline Description:**
Use detailed personas during requirements elicitation to surface accessibility, learnability, speed, and usability needs that a purely technical prompt may miss.

**Context:**
The requirements prompt used personas such as Ethan, Priya, and George to shape GUI-focused Blokus requirements.

**Application Process:**
1. Asked the LLM to generate functional and non-functional requirements from persona context and raw project constraints.
2. Requested table-format requirements to make the output easier to review and compare.
3. Asked the LLM to explain how each persona influenced the generated requirements.

**Outcome:**
- **What worked:** Ethan influenced learnability and invalid-move feedback, Priya influenced fast setup and save/load expectations, and George influenced readable GUI and accessibility needs.
- **What did not work:** Persona pressure leaned strongly toward GUI features even though architecture and milestone constraints still had to be checked manually.
- **Evidence:** `prompts/petar_requirements_response.json`.

**Reflection:**
I would reuse persona prompting, but only with an explicit architecture/spec gate in the same prompt. Personas helped capture human needs, but they cannot decide scope. Because the two requirements files were similar in most regards but still slightly different, we removed discrepancies by using the first one as the baseline because it covered the main points.

---

### Application 2: **Context-Aware Grounding + Interactive TDD Validation** - Coding Team 2, Guidelines 1 and 2

> **Note:** This guideline package was created by my own team. I include it here only so all guidelines that I actually used are documented.

**Guideline Description:**
Ground coding tasks in repository-specific context and provide human-verified tests or test targets so the LLM has a checkable specification.

**Context:**
All major coding prompts referenced `AGENTS.md`, `design/ADR.md`, `SPEC_M1.md`, and `guidelines/CODING_PROMPT_v1.md`. The prompts also listed exact files, constraints, and test expectations.

**Application Process:**
1. Prompted the model with stable architectural constraints: Python/uv, no desktop GUI libraries, no adapter imports in `Core.*`, and procedural bootstrap.
2. Broke features into adapter-level implementation tasks, such as `/start`, AI turn resolution, hover preview, `/piece-catalog`, and `/reset`.
3. Added focused pytest coverage for each feature before accepting the change.

**Outcome:**
- **What worked:** The model mostly stayed within adapters/static/template files for GUI work and added regression tests alongside feature work.
- **What did not work:** The prompt still gave the model enough freedom to refactor more than necessary and sometimes move code toward its own preferred style which was even more evident if the prior model was a different one. Some helper methods improved readability, but not every refactoring was required for the requested feature. Tests were also often written inside the same implementation prompt, which made it harder to cleanly separate this from the dedicated testing guidelines.
- **Evidence:** `prompts/petar_coding_player_amout_selection.json`, `prompts/petar_coding+debugging_adding_placement_preview.json`, `tests/adapters/test_web_orchestrator.py`, `tests/adapters/test_web_gui_hover_preview_static.py`.

**Reflection:**
The minimal context discipline was essential. The strongest prompts were the ones that named exact files, non-goals, and validation commands. In future prompts I would also add an explicit "do not refactor unrelated working code" constraint.

---

### Application 3: **Explain-Then-Fix Debugging** - Debugging Team 6, Guideline 1

**Guideline Description:**
Before asking the LLM to fix a bug, first ask it to explain the current code line by line and compare the explanation to the intended behavior. Only after the explanation step should the fix be generated.

**Context:**
I applied this to the web GUI selected-piece mismatch and rotate/flip preview bugs, where the failure was visible in the UI but the underlying data flow had to be understood first.

**Application Process:**
1. Asked the LLM to explain the current selected-piece or orientation flow before editing.
2. Compared that explanation against the intended behavior: selected tray piece, preview piece, submitted `piece_id`, and backend placement must match.
3. Used the explanation to identify drift between frontend state and backend catalog data, then required tests after the patch.

**Outcome:**
- **What worked:** The explanation step exposed that the GUI had its own piece catalog and orientation logic that could drift from the backend.
- **What did not work:** Explain-Then-Fix alone did not catch every transform edge case. The first fix solved the obvious preview issue, but another less visible bug appeared afterward. When I continued without applying the same guideline as strictly, the new bug was not fixed until I re-focused the prompt.
- **Evidence:** `prompts/petar_debugging_correct_piece_in_gui.json`, `prompts/petar_debugging_rotation_in_preview_not_working.json`, commit `1aca6cb`, commit `ed41478`.

**Reflection:**
The explanation-first step was useful for localizing state-flow bugs. For visual transform bugs, however, explanation was not enough; it had to be paired with backend-canonical tests.  
---

### Application 4: **AutoSD Scientific Debugging** - Debugging Team 6, Guideline 2

**Guideline Description:**
Use the LLM as a reasoning partner through a scientific debugging loop: hypothesis, prediction, experiment, observation, conclusion, and repeated validation until the root cause is supported.

**Context:**
I applied this to the web turn-flow bug, CLI grid alignment issue, hover-preview visibility bug, and end-game/no-move behavior.

**Application Process:**
1. Stated the observed bug and the intended behavior.
2. Asked for a hypothesis and prediction before the patch.
3. Used test output, focused source inspection, or static UI checks as the observation before accepting the fix.

**Outcome:**
- **What worked:** AutoSD worked well for observable behavior bugs. The turn-flow bug was reduced to two endpoint omissions: `/move` and `/pass` did not call `session.advance_turn()`.
- **What did not work:** The method depends on good experiments. For hover preview, static checks alone were not enough to prove real browser behavior.
- **Evidence:** `prompts/petar_debugging_players_turn.json`, `prompts/petar_debugging_fixed_cli_grid_view.json`, `prompts/petar_coding+debugging_adding_placement_preview.json`.

**Reflection:**
AutoSD worked best when I had a concrete observable failure and a focused test to run. It was less complete for frontend behavior that would ideally need browser-level tests.

Compared to Guideline 2 of Team 6, Guideline 1 was a bit slower and had a slightly higher token usage, but those results are to be further tested since the context in both was different.  

A test was conducted without any of those guideline, just a simple "fix the error prompt", and it resulted into no change at all. Overall, both guidelines were helpful and should be used when debugging.

---

### Application 5: **Staged Maintenance Pipeline** - Maintenance Team 7, Guideline 1

**Guideline Description:**
Structure LLM-assisted maintenance as a staged pipeline: identify the target files, generate focused changes, validate with automated checks, and then review the result instead of asking for a complete maintenance change in one step.

**Context:**
The final merge from `origin/change/duo` into `main` conflicted with the GUI work in web orchestration, bootstrap, frontend state, and tests.

**Application Process:**
1. **Target:** Identified the conflicted files and inspected which features each side introduced.
2. **Generate:** Resolved each conflict by keeping both compatible changes instead of blindly choosing one side.
3. **Validate:** Ran the build, full tests, and diff checks before considering the merge ready.

**Outcome:**
- **What worked:** The resolved merge preserved GUI lifecycle/AI skip behavior and Duo config/scoring/start-position data.
- **What did not work:** A one-shot merge could not be trusted because many conflicts were semantic, not just textual.
- **Evidence:** `prompts/petar_merge_conflict_resolve.json`, commit `8cc89d4`. Validation recorded in the prompt log: `uv build`, `uv run pytest` with `176 passed`, and `git diff --cached --check`.

**Reflection:**
For merge conflicts, the staged pipeline is the right model: target the affected files, resolve intent file by file, then run the full validation cascade. Nonetheless an user test should be conducted to ensure that everything is working correctly.

Because of the refactoring and preferences of different models, are merge conflicts very likely to happen. This means that a strong merge model will become an increasingly necessary and widely used tool as LLMs play a larger role in software engineering.

---

## 3. Counterexamples

### Counterexample 1: Rotate/Flip Debugging Was Incomplete After the First Fix

**Failure Description:**
The first rotation/preview debugging pass improved preview behavior, but the bug was not fully fixed. A follow-up prompt was required because pieces `6`, `9`, `11`, and `15` still did not flip correctly from orientations `0` or `2`, and pieces `11` and `15` appeared identical in the GUI. This showed that fixing the initially visible bug was not enough; a second, less obvious defect remained in the piece catalog and transform mapping.

**Diagnosis:**
- **Root Cause:** Frontend transform logic and duplicated/incorrect piece definitions diverged from the backend catalog. The LLM also mixed up some pieces and effectively allowed duplicate/invalid definitions.
- **Why the Guideline Failed:** **Debugging Team 6 Guideline 1** explained the visible flow but did not force exhaustive orientation-equivalence testing. When I did not continue the same guideline discipline for the follow-up bug, the fix was weaker.
- **Boundary Condition:** Symmetric and near-symmetric polyominoes where a horizontal flip maps to the same grid and a vertical flip must be considered.

**Refinement:**
- **Updated Guideline:** For visual transform bugs, add a canonical backend contract and tests that verify transition maps for every orientation.
- **How It Was Tested:** Added `/piece-catalog` tests for distinct pieces, targeted flip transitions, transition index ranges, and transform correctness.
- **Evidence:** `prompts/petar_debugging_rotation_in_preview_not_working.json`, commit `ed41478`, `tests/adapters/test_web_orchestrator.py`.

**Prompt/Context Used:**
```text
Bug cluster:
1. In the web GUI, pieces 6, 9, 11, and 15 do not flip correctly from orientation 0 or orientation 2.
2. Pieces 11 and 15 appear to be the same piece in the GUI, but they should be distinct Blokus pieces.
```

**AI Output:**
```text
Implemented the fix.
Changed: corrected duplicated/invalid piece definitions; exposed backend orientations, rotate_to, and flip_to; added focused endpoint tests.
```

---

### Counterexample 2: Hover Preview Was Functionally Implemented but Invisible

**Failure Description:**
The hover placement preview was added, but it did not appear when the mouse was over the board and a piece was selected.

**Diagnosis:**
- **Root Cause:** The first implementation depended on fragile per-cell hover behavior and board redraws cleared the transient state.
- **Why the Guideline Failed:** **Coding Team 2 Guideline 2** and **Testing Team 3 Guideline 1** produced code and static checks, but the success criteria did not fully capture browser event flow.
- **Boundary Condition:** Dynamic DOM rendering where cells are recreated and event listeners/transient classes must survive redraws.

**Refinement:**
- **Updated Guideline:** For frontend interaction work, include event-delegation and redraw-state criteria in the test objective.
- **How It Was Tested:** Switched to delegated `#board` `mouseover`/`mousemove`, retained `hoverAnchor`, cleared previews on board leave and move success, and added static regression tests.
- **Evidence:** `prompts/petar_coding+debugging_adding_placement_preview.json`, commit `618972f`, `tests/adapters/test_web_gui_hover_preview_static.py`.

**Prompt/Context Used:**
```text
Bug: The newly added board hover preview does not appear. When the mouse is over the board grid and a piece is selected, the GUI does not show where the selected piece would be placed.
```

**AI Output:**
```text
Replaced per-cell mouseenter dependency with delegated #board mouseover and mousemove handlers. Keeps hoverAnchor updated and redraws preview after board refresh, rotate, and flip.
```

---

### Counterexample 3: End-Game and No-Move States Were Missing from the GUI Acceptance Criteria

**Failure Description:**
The GUI could play moves, but nothing visible happened when the game ended. Players with no legal moves could also create a deadlock-like experience unless the system skipped them automatically. The LLM understood how to implement mechanics, but it did not initially understand what a complete playable board game should look like for the user: there was no result screen and no clear way to start another game.

**Diagnosis:**
- **Root Cause:** Earlier GUI tests focused on move submission and state rendering, not terminal states or no-legal-move control flow.
- **Why the Guideline Failed:** **Testing Team 3 Guideline 1** says to define scope boundaries and success criteria. My earlier criteria did not include terminal UX or no-move edge cases.
- **Boundary Condition:** Game lifecycle states that are rare in manual smoke testing but critical for a complete game loop.

**Refinement:**
- **Updated Guideline:** Every game-loop UI task needs explicit acceptance criteria for start, normal turn, pass/no-move, finished state, and restart.
- **How It Was Tested:** Added final-score/winner state, skipped-player banner, automatic no-move skipping, all-no-moves finish behavior, and `/reset` tests.
- **Evidence:** `prompts/petar_coding_gui_result_table.json`, commit `8b68253`, `tests/adapters/test_web_orchestrator.py`, `tests/adapters/test_web_gui_hover_preview_static.py`.

**Prompt/Context Used:**
```text
Task: Debug why nothing visible happens when the web GUI game ends. If end-game handling already exists, fix it. If it does not exist, implement it. Also add clear identification when a player has no possible moves, then automatically skip/pass that player's turn afterward.
```

**AI Output:**
```text
Implemented the finished-game Main Menu flow and added skipped-player handling, final-score rendering, reset/session-factory support, and focused restart/reset tests.
```

---

### Counterexample 4: Broad Prompts Led to Over-Refactoring and Partially Wired Features

**Failure Description:**
During the early remediation session, the agent changed more code than strictly necessary. Some changes improved readability, such as extracting helper methods, but other changes were closer to style normalization than required bug fixes. At one point, AI-player functionality existed in the codebase but was not yet exposed through a clear player-selection flow, so the implementation was technically present but not useful to a player.

**Diagnosis:**
- **Root Cause:** The remediation prompt was broad: it asked the model to check the game logic setup and fix correctness issues. That gave the LLM room to refactor working code, introduce helper methods, and align files with its own preferred coding style.
- **Why the Guideline Failed:** **Coding Team 2 Guidelines 1 and 2** gave the model context and tests, but they did not constrain scope tightly enough. TDD confirmed many behaviors, but it did not prevent unnecessary structural changes.
- **Boundary Condition:** Broad cleanup or remediation prompts where "improve the code" is mixed with concrete bug fixes.

**Refinement:**
- **Updated Guideline:** For remediation prompts, explicitly state: do not refactor unrelated working code, do not introduce new helper methods or Builder-style rewrites unless required by the failing behavior, and ensure every new feature is connected to a user-visible flow.
- **How It Was Tested:** Later prompts became narrower and file/function scoped. The AI-player functionality was eventually made user-visible through CLI and web human-player count selection, and the game lifecycle was completed with a result table and main-menu reset.
- **Evidence:** `prompts/petar_gui_refactor.json`, `prompts/petar_coding_player_amout_selection.json`, `prompts/petar_coding_gui_result_table.json`, commits `e0755b4`, `5348e95`, and `8b68253`.

**Prompt/Context Used:**
```text
Task: Check the current game logic setup in src/, fix correctness issues, and then propose or implement an interactive UI only if it does not violate the project constraints.
```

**AI Output:**
```text
Implemented Milestone 1-only remediation. Files changed included core board, rule set, game session, memento, ports, adapters, bootstrap, and related tests.
```

---

## 4. AI Usage Disclosure

### Tools and Models Used

| Tool/Model | Usage | Validation Method |
|---|---|---|
| OpenCode build agent with GPT-5.5 (`openai/gpt-5.5`) | Requirements documentation, coding, debugging, GUI changes, CLI changes, merge conflict resolution | `uv run pytest`, targeted pytest files, code review, `uv build`, `git diff --cached --check`, manual review of persona mappings |

### Evaluation Methods

1. **Correctness Testing:** Used `uv run pytest` and focused pytest files after feature and debugging changes.
2. **Regression Tests:** Added tests for turn advancement, invalid move behavior, canonical piece catalog, rotate/flip transitions, hover preview structure, CLI alignment, AI/human setup, no-move skips, and restart/reset behavior.
3. **Architecture Review:** Checked that GUI and CLI behavior stayed in adapters/static/templates/bootstrap and did not import adapters into `Core.*`.
4. **Static/Build Checks:** Prompt logs record `uv run ruff check src/`, `uv run mypy src/`, `uv build`, and `git diff --cached --check` in relevant sessions.
5. **Manual Diff Review:** Git history was reviewed commit-by-commit for Petar/YxesRatep work before writing this portfolio.

### Time Investment

Approximate hours:
- AI prompting and refinement: **7 h**
- Reviewing AI outputs and diffs: **5 h**
- Testing and validation: **8 h**
- Documentation and portfolio evidence collection: **3 h**

---

## 5. Reflections

### What I Learned

- **Human-in-the-loop review is essential.** LLM agents can produce convincing output, but a developer still has to inspect scope, correctness, and whether the result actually matches the intended user experience.
- **The codebase should be familiar before using an agent.** Without understanding the existing architecture and behavior, it is too easy to accept unnecessary refactorings or miss subtle regressions.
- **I learned how to integrate agents into a project workflow.** The useful part was not just asking for code, but tracking prompt logs, reviewing diffs, tying changes to commits, and validating the result with tests or manual review.
- **I learned how LLMs can support all subparts of a software engineering task.** In this project I used them for requirements, coding, debugging, testing support, documentation, and merge/integration work instead of only treating them as code generators.
- **UI and UX need human evaluation.** They are subjective and hard to fully capture in automated tests, so LLM-generated UI work can be functionally correct while still missing important user-facing expectations.

### Skills Developed

- Writing constrained implementation prompts for an existing Hexagonal Python codebase.
- Turning GUI bug reports into focused adapter/static tests without moving behavior into the core.
- Using LLMs as debugging partners through hypothesis, prediction, observation, and validation cycles.
- Resolving semantic merge conflicts while preserving both feature branches.

### Future Improvements

- Add browser-level or DOM-level tests for hover preview and start/end flows instead of relying only on static JS checks.
- Define lifecycle acceptance criteria at the start of every game UI task: setup, legal move, illegal move, pass/no-move, finish, restart.
- Separate test-generation guideline evidence from implementation prompts when possible, because combining TDD tests and implementation in one prompt made the testing guideline harder to document cleanly.
- For any piece-transform work, make backend canonical data the source of truth from the beginning.

---

*Submitted by Petar Malamov - Team 2 (Coding), Generative Software Engineering, May 2026.*
