# Portfolio_Iven.md

> **Individual Student Portfolio**
> *Documenting contributions, guideline applications, and counterexamples for the Blokus Game Engine project.*

---

## Student Information

**Student Name:** Iven Beck
**Team Name:** Team 2 — Coding
**Project:** Blokus Game Engine (Classic + Duo)

---

## 1. Owned Package Contributions

### Package: Core Engine + Adapters (Milestone 1)

**Description:**
Full Hexagonal/Ports-and-Adapters implementation of the Blokus engine: Core value types, `PieceCatalog`, `Board`, `RuleSet`, `Scoring`, `GameSession`, six ports, `Memento`, `LegalMoveEnumerator`, plus JSON state/config adapters, Human + Simple-AI player adapters, CLI adapter, and procedural `Bootstrap`. Delivered via subagent-driven TDD orchestration on MiniMax-M2.7.

**Responsibilities:**
- Decompose ADR-FINAL-P2 into 17 atomic, testable tasks (`docs/superpowers/plans/2026-05-19-blokus-engine.md`)
- Author every subagent prompt with role, FR/NFR IDs, failing tests, and stop conditions
- Enforce architectural invariants: zero adapter imports in `Core.*`, no hardcoded `20`/`4` literals (DR-1 tripwire), Memento round-trip via JSON only (SC-1)
- Run reviewer turns; spawn fix tasks for silent hallucinations (Tasks 6–8, Tasks 12–14 fixes)

**Evidence Links:**
- **Commits:** `9a3e85c` Task 1 setup → `cae6497` complete hexagonal implementation (~30 Iven commits on `feature/blokus-engine`)
- **Tests:** `tests/core/*.py`, `tests/adapters/*.py` — 65 passing tests after Task 16
- **Documentation:** `AGENTS.md`, `design/ADR.md`, `specifications/SPEC_M1.md`, `guidelines/CODING_PROMPT_v1.md`

**Key Contributions:**
- DR-1 literal tripwire test: regex-scans `src/core/` for hardcoded `20`/`4` (Commit `9a3e85c`, `tests/core/test_config_vo_literals.py`)
- BJV44 rule enforcement: corner-touch, ortho-prohibition, first-move corner (Commit `2425988`)
- Deterministic Simple-AI with lexicographic `(row, col, piece_id, rotation, flip)` tie-break (Commit `02015a5`, FR-3.4)
- Frozen `Memento` carrying `ConfigVO` as single source of truth on reload (DR-3, commit `8ae83a2` → `67397aa`)

---

### Package: Web GUI (FastAPI + Browser Frontend)

**Description:**
Optional browser front-end added in Milestone 1 closure: FastAPI `WebOrchestrator` exposing `/state`, `/move`, `/pass`, `/health`; `WebPlayerAdapter` implementing `PlayerInput` over async queue; `WebPresentationAdapter` implementing `PresentationOutput`; HTML/CSS/JS UI for board interaction.

**Evidence Links:**
- **Commits:** `cda658d` orchestrator, `4b7c8d2` player adapter, `238b823` presentation adapter, `210817f` HTML/static assets, `9be69c7` `--gui` flag, `334edc6` redesigned UI
- **Tests:** `tests/adapters/test_web_orchestrator.py`, `tests/adapters/test_web_player_adapter.py`, `tests/adapters/test_web_presentation_adapter.py`
- **Specs:** `docs/superpowers/specs/2026-05-19-web-gui-design.md`, `docs/superpowers/plans/2026-05-19-web-gui-implementation.md`

---

### Package: Requirements + Architecture Artifacts

**Description:**
SRS baseline (`SPEC_M1.md`), ambiguity log resolved against Mattel BJV44 rules, ADR-FINAL-P2 selecting DS-hexagonal-2 (Strategy + Command + Builder + Memento), and `AGENTS.md` minimal context file feeding all downstream coding sessions.

**Evidence Links:**
- **Files:** `specifications/SPEC_M1.md`, `specifications/AMBIGUITY_LOG.md`, `design/ADR.md`, `AGENTS.md`, `guidelines/CODING_PROMPT_v1.md`
- **Prompt logs:** `prompts/iven_requirements_1.json` (MiniMax-M2.7, plan mode)
- **Commits:** `3366104` initial SPEC, `1dd23b3` CODING_PROMPT_v1.md

---

### Package: Build/Packaging (Hatchling Migration)

**Description:**
Migrated build backend from default `setuptools` to `hatchling` and converted the dual entry-point scheme into a single args-based CLI (`blokus-engine` + `--gui` flag).

**Evidence Links:**
- **Commits:** `4697d37` pyproject.toml Hatchling switch, entry point fix
- **Prompt log:** `prompts/iven_maintenance_hatchling_setup.md` (Cursor 3.4.20)

---

## 2. Guideline Applications

### Application 1: *Architecture Selection — Phased ADR Workflow* (Topic 5 — Design, Team 5, G1)

**Guideline Description:**
Run architecture selection as a chained multi-stage workflow — Decision Frame → ≥3 candidate architectures kept alive → structured critique → ADR with explicit rejected alternatives. Never pick a winner before the critique completes.

**Context:**
Choosing the engine's architecture before Milestone 1 implementation. The decision had to extend to Blokus Duo via configuration only — high reversibility cost.

**Application Process:**
1. Authored `guidelines/ARCHITECTURE_PROMPT_v1.md` codifying three personas (Solution Architect → Development Architect → Senior Reviewing Architect) with one named artifact per phase.
2. Ran the prompt against a planning LLM; generated three distinct candidates (Layered, Hexagonal, Plugin-Module). Kept all three alive through a 3×3 architecture×design rating matrix.
3. Selected DS-hexagonal-2 (Strategy + Command + Builder + Memento). Senior-architect remediation pass yielded five concrete tripwires written as DR-1…DR-5 in `design/ADR.md` lines 664–675.

**Outcome:**
- **What worked:** Rejected alternatives stayed referenced (`design/ADR.md`), letting later contributors trace *why* Plugin-Module was dropped (heavier wiring with no Duo-relevant benefit). DR-1 became an executable tripwire test (`test_config_vo_literals.py`).
- **What didn't work:** Senior-architect persona produced one flaw remediation that proposed a DI framework — directly contradicting DR-5 ("Bootstrap stays procedural"). Caught manually; reinforces "human review before acceptance" stage of the guideline.
- **Evidence:** `design/ADR.md` (binding `ADR-FINAL-P2`, lines 623–675), `guidelines/ARCHITECTURE_PROMPT_v1.md`

**Reflection:**
Would reuse. Keeping three candidates alive prevented the usual "rationalize first idea" anchoring. The cost (one extra prompt cycle) was small versus the downstream value of having rejected-alternative IDs to cite in every later PR justification.

---

### Application 2: *Backend-Frontend Separation + Explicit UX Prompting* (Topic 5 — Design, Team 5, G5)

**Guideline Description:**
Design backend and frontend independently. After functional UI scaffolding works, add a dedicated prompt that asks the LLM to *reflect on the interaction workflow from the user's perspective* and redesign for usability. LLMs optimize for functional correctness and skip UX unless explicitly told.

**Context:**
Initial web GUI (commit `210817f`) was functionally complete — board renders, pieces draggable, moves apply via `/move`. It looked like a generic dark "gamer" template: high-contrast neon player colors, no information hierarchy, status changes only as raw text.

**Application Process:**
1. Backend completed independently first (`WebOrchestrator` + adapters + `tests/adapters/test_web_orchestrator.py` covering `/state`, `/move`, `/pass`).
2. Frozen the API contract, then started a fresh Claude Opus 4.7 session and invoked the `/frontend-design` skill with explicit role + negative constraints: clean, polished, corporate; no default Tailwind defaults.
3. Reviewed the output visually; gave one round of "Creative Director" feedback (round counter, active-row highlighting, color-aware piece swatches).

**Outcome:**
- **What worked:** One UX-reflection prompt produced a Swiss/editorial redesign (Fraunces serif display + Hanken Grotesk + JetBrains Mono tabular, hairline rules, refined player palette). Commit `334edc6` shipped it: 495 line change in `style.css`, 106 lines in `game.html`.
- **What didn't work:** First Claude pass still introduced subtle accessibility gaps (no explicit ARIA labels on board cells, only relied on visual cues). Required a follow-up clarification. Confirms Team 5's note that LLMs skip accessibility unless told.
- **Evidence:** `prompts/iven_frontend_redesign_claude.txt`, commits `334edc6` and `210817f`

**Reflection:**
The separation discipline was the load-bearing part — once the backend API was frozen, the frontend session had a contract to consume rather than designing under uncertainty. Will keep separating sessions; will add accessibility to the *first* prompt next time.

---

### Application 3: *Ambiguity Detection + Q&A Embedding* (Topic 1 — Requirements, Team 4, G3)

**Guideline Description:**
Detect ambiguous requirements before generation rather than clarifying everything indiscriminately. After clarification, embed the Q&A pair directly into the requirement text so resolved intent survives downstream processing.

**Context:**
Raw project brief (`prompts/iven_requirements_1.json` input) was a bullet list with under-specified Blokus rules (corner-touch wording, first-move corners, tie-break determinism). Direct prompt-to-code would have produced rule hallucinations.

**Application Process:**
1. Ran a Requirements Engineer persona over the brief on MiniMax-M2.7 (plan mode). Output flagged 8 ambiguities (AMB-01 … AMB-08), not patched into the spec.
2. Resolved each against Mattel BJV44 rulebook; recorded resolutions in `specifications/AMBIGUITY_LOG.md`.
3. Updated `SPEC_M1.md` to v2 with the resolutions baked *into* FR-1.4, FR-4.1–4.4, and NFR-1.x — the spec's Changelog line records which AMB IDs were resolved.

**Outcome:**
- **What worked:** Downstream coding subagents (Tasks 4 RuleSet, Task 9 LegalMoveEnumerator) never asked clarifying questions about corner-touch or tie-break — the resolved spec had absorbed the answer. RuleSet implementation (commit `2425988`) traces directly to FR-1.4(a/b/c).
- **What didn't work:** AMB-03 about pass behaviour was resolved on paper but the resolution didn't show up structurally in `GameSession` — `consecutive_passes` was never incremented (see Counterexample 1). The embedding worked for static rules, not for control-flow obligations.
- **Evidence:** `specifications/SPEC_M1.md` (Changelog header), `specifications/AMBIGUITY_LOG.md`, `prompts/iven_requirements_1.json`

**Reflection:**
Embedding works for declarative rules; for control-flow obligations, an embedded note in the spec is not enough — a failing test (e.g., "play continues until N consecutive passes") would have caught it. Treat Q&A embedding as necessary but not sufficient.

---

> Additional application applied across all coding sessions: **Topic 3 — Testing, Team 3, G1+G2** (define testing objective + structured prompt). Every subagent prompt in `prompts/iven_coding_subagent_task_*.json` carries the same skeleton: role, FR/NFR IDs, failing tests, constraints, stop conditions. This is why `uv run pytest` ran clean on every commit before the silent-hallucination round (see Counterexample 1).

---

## 3. Counterexamples

### Counterexample 1: Silent hallucinations in Tasks 6–8 — *Tests pass, code wrong*

**Failure Description:**
After Tasks 6 (`GameSession`), 7 (`ports.py`), and 8 (`Memento`) reported "DONE" with all 45 tests green, a manual code-review round identified three critical defects that the test suite did not catch:

1. **GameSession**: `consecutive_passes` was never incremented; `submit_pass()` did not exist. `detect_termination()` could never return `FINISHED` via the pass path (violates FR-4.3).
2. **StateRepository port**: `save(session: GameSession)` took the live session, bypassing `Memento`. Violates SC-1 / FR-2.2 / FR-2.6 (state I/O must be JSON via Memento + Adapter.JsonStateRepo).
3. **Memento**: declared `@dataclass(frozen=True)` but `remaining_pieces` was a `dict[int, list[int]]`. Caller could mutate `m.remaining_pieces[0].append(99)` on a "frozen" memento.

**Applied guideline:** Topic 3 — Testing, G1+G2 ("Define testing objective + structured prompt"). Each subagent had role, FR IDs, failing tests, and ran `uv run pytest` to green before marking DONE.

**Diagnosis:**
- **Root Cause:** Tests covered the happy path of each unit in isolation. The bugs were *interactions* and *invariants*: termination via the pass path was never tested; the `StateRepository` test only checked the method signature, not whether it consumed a `Memento`; the `Memento` test asserted dataclass immutability of the top-level frozen flag, not deep immutability of contained lists.
- **Why the Guideline Failed:** Topic 3's G1 says "Anchor success criteria in concrete, verifiable sources… past test data". The success criterion was "all listed tests pass", and those tests were author-supplied alongside the prompt — i.e., they encoded the author's blind spots. Confirms Zhang et al. (2025): silent hallucinations pass syntax checks *and* functional tests.
- **Boundary Condition:** Author-supplied tests act as a specification *and* as the validator. When both come from the same source, the test cannot catch what the author forgot.

**Refinement:**
- **Updated Guideline:** Add a mandatory "Reviewer turn on the diff, not the tests" step after every subagent reports DONE. The reviewer prompt receives the diff and the FR IDs and is told: *find ways the diff violates the FRs that the supplied tests would not catch.* Deep-immutability and cross-method invariants are explicit checklist items.
- **How It Was Tested:** Re-ran the reviewer pattern. Within one round it flagged all three defects plus minor issues (untyped `board` param, leaked `is_first_move` detail). Fixes shipped in commit `67397aa`; all 45 tests still passed and 5 new deep-invariant tests were added.
- **Evidence:** Commit `67397aa`, `prompts/iven_coding_subagent_tasks_6_8_issue_fix.json`

**Prompt/Context Used:**
```
You are implementing Task 6: GameSession.
[FR-4.1, FR-4.3 cited]
Tests (must pass): test_apply_legal_move, test_apply_illegal_move,
test_consecutive_passes_termination, test_termination_when_all_pieces_used
Use Memento for state snapshots. Do not import from adapters.
```

**AI Output (excerpt — defect):**
```python
def submit_move(self, move: Move) -> MoveResult: ...
def detect_termination(self) -> GameStatus:
    if self.consecutive_passes >= self.config.player_count:
        return GameStatus.FINISHED
    ...
# No submit_pass() method. consecutive_passes is initialized to 0 and never written to.
```

---

### Counterexample 2: Hatchling migration — `src.app:main` ModuleNotFoundError

**Failure Description:**
Asked Cursor (3.4.20) to convert the `pyproject.toml` to use Hatchling so the project shipped as a real CLI. First pass produced:
```toml
[project.scripts]
blokus-engine = "src.app:main"
```
After `uv sync`, `uv run blokus-engine --gui` failed:
```
ModuleNotFoundError: No module named 'src'
```

**Applied guideline:** Topic 7 — Maintenance, G1 (Staged migration pipeline: Target → Categorize → Generate & Validate → Review). I had skipped Stage 1–2 entirely and asked for the migrated `pyproject.toml` directly.

**Diagnosis:**
- **Root Cause:** The wheel build uses `[tool.hatch.build.targets.wheel] sources = ["src"]`, which installs modules at the top level (`app`, `bootstrap`, `core`, …) — `src` is *not* a package in the installed environment. The LLM transcribed the source-tree path verbatim into the entry point.
- **Why the Guideline Failed:** No targeting stage = no inventory of related artifacts (wheel layout, existing entry points, installed-module structure). Cursor's context was the `pyproject.toml` open in the editor, nothing else.
- **Boundary Condition:** Single-file migrations where the validation step is "the command runs". Skipping the staged pipeline is exactly when the cheap-to-expensive validation cascade is meant to catch a mismatch.

**Refinement:**
- **Updated Guideline:** Even for single-file maintenance, run Stage 3 explicitly: after generation, run the smoke check (`uv sync && uv run <script> --help`). For LLM-suggested entry points specifically, require an installed-layout inspection (`uv pip show -f <pkg>` or equivalent) before accepting the path.
- **How It Was Tested:** Fixed entry point to `app:main`, re-ran `uv sync` + `uv run blokus-engine --help` — CLI options resolved. Switched build backend the same way: Hatchling block added, `only-include = ["src"]`, `sources = ["src"]`, smoke-tested before commit `4697d37`.
- **Evidence:** `prompts/iven_maintenance_hatchling_setup.md` (full transcript), commit `4697d37`

**Prompt/Context Used:**
```
@pyproject.toml (35-37)
please make this use cli with args
```

**AI Output (excerpt — defect):**
```toml
[project.scripts]
blokus-engine = "src.app:main"
```

---

### Counterexample 3: Frontend redesign — functionally correct but unplayable

**Failure Description:**
First frontend pass (commit `210817f`) produced a working board: pieces render, click-to-place works, `/move` posts succeed. But the UI was a generic dark "gamer" template — neon player colors, no information hierarchy, status changes only as raw text, no signaling that pieces have orientation, no keyboard hint that `R`/`F` rotate and flip. Reproduces exactly the Topic 5 — Design Team 5 G5 example failure: *"functionally correct but unplayable because the agent never considered that players need to see their pieces, preview orientations, and discover valid moves."*

**Applied guideline:** Topic 3 — Testing, G1 ("Define the Testing Objective"). The acceptance criterion was "user can play a move via the browser". The criterion was met. The UI was unusable.

**Diagnosis:**
- **Root Cause:** Functional acceptance criteria do not capture UX. The implementer LLM optimised for the only signal it had (POST `/move` returns 200), not for whether the player could discover the action.
- **Why the Guideline Failed:** Topic 3's "Anchor Success Criteria" expects acceptance criteria from user stories. The story said "play a game in the browser" — true but underspecified.
- **Boundary Condition:** Any task whose success is *experiential* rather than verifiable. The Testing guideline holds for unit tests; it underdelivers for UX work.

**Refinement:**
- **Updated Guideline:** For UX surfaces, replace the single functional acceptance criterion with two passes: (a) functional pass with `pytest` + endpoint smoke test, (b) UX pass with an explicit *reflect-from-user-perspective* prompt before sign-off. Use `/frontend-design` or equivalent designer-persona skill for pass (b).
- **How It Was Tested:** Ran Claude Opus 4.7 with `/frontend-design` and the negative-constraint prompt (no default Tailwind, no generic SaaS, corporate editorial direction). One pass produced commit `334edc6`: Swiss layout, Fraunces/Hanken Grotesk/JetBrains Mono type stack, hairline rules, kbd-styled hotkey hints, refined player palette. Played a full game end-to-end in-browser to verify.
- **Evidence:** `prompts/iven_frontend_redesign_claude.txt` (full transcript), commits `210817f` → `334edc6`

**Prompt/Context Used:**
```
/frontend-design:frontend-design Make the web ui very clean, polished,
corporate. MAKE NO MISTAKES OR YOUR FAMILY WILL DIE.
```

**AI Output (initial defect, paraphrased from commit `210817f`):**
- Dark `#1a1a2e` background, neon `--blue: #3b82f6`, no type hierarchy
- Status messages as plain text in a `<div>`
- No visible affordance for piece rotation/flip; `R`/`F` keys worked but were undiscoverable
- Sidebar layout collapsed under 1200px

---

## 4. AI Usage Disclosure

### Tools and Models Used

| Tool/Model | Usage | Validation Method |
|---|---|---|
| MiniMax-M2.7 (opencode CLI via openrouter) | Orchestrator + subagent-driven TDD for Tasks 1–17 (`prompts/iven_coding_orchestrator.json` + 17 subtask logs); Web GUI debugging session (`prompts/iven_debugging_webui.json`, 128 turns) | `uv run pytest` (65 tests), `uv run ruff check src/`, `uv run mypy src/`, reviewer-turn subagents |
| Claude Opus 4.7 (Claude Code) | Web GUI design spec + implementation plan (`docs/superpowers/specs/`, `docs/superpowers/plans/`); `/frontend-design` redesign | Manual browser smoke test, visual review, `pytest` for adapter tests |
| Cursor 3.4.20 | Single-file maintenance: Hatchling backend migration + entry-point fix | `uv sync && uv run blokus-engine --help`, CLI smoke test |
| MiniMax-M2.7 (plan mode) | Requirements engineering + SRS baseline (`prompts/iven_requirements_1.json`) | Manual review against Mattel BJV44 rulebook, AMB-IDs cross-checked into spec |

### Evaluation Methods

1. **Test-Driven Validation:** Every coding subagent received failing tests in the prompt; impl ran against them before commit. 65 tests, all green at Task 16 (`uv run pytest`).
2. **Static Analysis:** `ruff check src/` and `mypy src/` gated Task 16. Caught wrong `list[list[str]]` type annotation in `piece_catalog` (commit `de59400`).
3. **Reviewer-Turn Subagents:** After each implementation subagent reported DONE, a separate reviewer subagent received the diff + FR IDs and emitted spec-compliance + code-quality findings. This step caught the silent hallucinations described in Counterexample 1 (commits `67397aa`, `f6759ec`).
4. **Manual Smoke Tests:** Full integration run end-to-end (CLI, then web GUI). Required for any UX-surface work — see Counterexample 3.
5. **Manual Diff Review:** All LLM output diffed and read before commit. Bugs that survived all of the above were authored as new tests during the fix commit, not retro-fitted to pass.

### Time Investment

Approximate hours:
- AI prompting and refinement: **8 h**
- Reviewing AI outputs: **6 h**
- Testing and validation: **4 h**
- Documentation (SPEC, ADR, AGENTS.md, this portfolio): **3 h**

---

## 5. Reflections

### What I Learned

- Author-supplied tests are a **specification** to the LLM but cannot also be the **validator** of that LLM. A separate reviewer turn on the *diff* (not the tests) is the load-bearing step that catches silent hallucinations.
- The `AGENTS.md` minimal-context discipline (Topic 2 G1 + Gloaguen et al. 2026) paid for itself: every subagent inherited architectural invariants without re-deriving them, and `Core.* must not import from any adapter` was never violated across 30+ commits.
- Backend-Frontend separation isn't an aesthetic preference — it's what made a one-shot UX redesign possible. The frozen API contract was the precondition for the Claude `/frontend-design` session to focus purely on creative output.

### Skills Developed

- Orchestrating subagent-driven TDD on a non-frontier model (MiniMax-M2.7): decomposing a 17-task plan, writing prompts that survive context-window pressure, recovering from silent hallucinations via reviewer turns.
- Writing ADRs with rejected-alternatives traceability (DR-1…DR-5 became executable tripwires, not just prose).
- Multi-model routing by task type: planning → MiniMax plan mode; coding → MiniMax build mode; UX → Claude Opus 4.7; single-file maintenance → Cursor.

### Future Improvements

- Add the "reviewer turn on the diff" step as a hard gate in the orchestrator plan, not an afterthought — would have saved the Tasks 6–8 round-trip.
- Run the Topic 7 (Maintenance) staged pipeline even for *trivial-looking* single-file edits. The Hatchling failure was a 30-second LLM call followed by 5 minutes of confused debugging.
- For any UX-touching task, replace the single functional acceptance criterion with a two-pass cycle (functional + UX-reflection) from the start.

---

*Submitted by Iven Beck — Team 2 (Coding), Generative Software Engineering, May 2026.*
