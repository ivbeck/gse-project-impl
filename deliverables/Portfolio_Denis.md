# Portfolio_Denis.md

> **Individual Student Portfolio**
> *Documenting contributions, guideline applications, and counterexamples for the Blokus Game Engine project.*

---

## Student Information

**Student Name:** Denis Maxheimer
**Team Name:** Team 2 — Coding *(guideline-package author; project roles: Architecture/Design co-lead + Blokus Duo / Milestone 2 implementation)*
**Project:** Blokus Game Engine (Classic + Duo)

> **Guideline-highlighting convention used throughout this report:** every contribution and step names the guideline it applied, highlighted as **`[Topic — Team N · Gx]`**. Guidelines authored by my own team (Coding, Team 2) are marked *(own team)*; all Section 2 applications are from **other** teams.

---

## 1. Owned Package Contributions

### Package: Blokus Duo — Milestone 2 vertical (flagship)

**Description:**
End-to-end implementation of the configurable Blokus **Duo** variant on top of the Milestone 1 Hexagonal core — without forking the engine. Duo is expressed as *data* (`scoring_rule="duo"`, 14×14 board, `player_count=2`, interior starting cells) flowing through the existing Strategy/Builder/Memento seams, so Classic and Duo share one code path. Spans `Core`, adapters, bootstrap, the CLI/web entry points, the browser GUI, and the test suite.

**Guideline(s) applied:**
- **`[Coding — Team 2 · G4]`** Atomic Task Decomposition *(own team)* — the work was decomposed into a written plan of atomic, individually-testable steps before any code (`docs/superpowers/plans/2026-05-21-blokus-duo.md`).
- **`[Coding — Team 2 · G2/G3]`** TDD-LLM + Iterative Remediation *(own team)* — each step landed test-first with a RED→GREEN→full-suite loop.
- **`[Testing — Team 3 · G1]`** Define the Testing Objective *(other team — see Section 2, Application 2)*.

**Responsibilities:**
- Author the Duo engine-extension design and implementation plan (`docs/superpowers/specs/2026-05-21-blokus-duo-design.md`, `docs/superpowers/plans/2026-05-21-blokus-duo.md`).
- Add the `scoring_rule` configuration knob through `ConfigVO` + Builder + `ConfigSource` without hard-coding Duo anywhere in `Core`.
- Implement `DuoScoring` as a Strategy behind a `build_scoring` factory; thread `last_placed_piece` through `GameSession`, `Memento`, and the JSON state round-trip.
- Expose the mode to the outside world (`--duo` flag for CLI + web; `scoring_rule`/`starting_positions` in `/state`) and reflect it in the GUI (mode-aware title, interior starting-cell markers).

**Evidence Links:**
- **Commits (≈17 on 2026-05-21):** `71997b7` (scoring_rule config field + Builder), `331dabd` (parse `scoring_rule` + Duo preset in `json_config_source`), `dba1ca6` (`DuoScoring` + `build_scoring` factory), `df2d0bd` (track last placed piece → scoring), `274141e` (carry `last_placed_piece` in `Memento`), `4b13163` (round-trip `scoring_rule` + `last_placed_piece` in JSON state), `c2354cd` (derive scoring from memento config), `969203d` (select scoring in `bootstrap.main`), `521f0b3` (`--duo` flag, CLI + web), `a3b47b4` (`/state` exposes `starting_positions` + `scoring_rule`), `453c308` (GUI starting cells for Duo interior starts), `e781623` (Duo determinism + AI-vs-AI integration tests), `89d2a61` (Duo tie co-winner + no-bonus-with-remainder tests), `8f03767` (mode-aware GUI title + grid caption), `6111767` (Duo-mode GUI guardrails).
- **Tests:** `tests/core/test_scoring.py`, `tests/core/test_duo_game.py`, `tests/core/test_memento.py`, `tests/core/test_config_vo_literals.py`, `tests/adapters/test_json_config_source.py`, `tests/adapters/test_json_state_repo.py`, `tests/adapters/test_web_orchestrator.py`, `tests/adapters/test_web_gui_*_static.py`, `tests/test_app_cli.py`, `tests/test_bootstrap.py`.
- **Documentation:** `docs/superpowers/specs/2026-05-21-blokus-duo-design.md` (`ae8d78d`), `docs/superpowers/plans/2026-05-21-blokus-duo.md` (`3e5e4e5`), `prompts/denis_coding_duo_mode_gui.json`.

**Key Contributions:**
- **No-fork Duo:** the only difference between Classic and Duo is configuration data + a swapped `Scoring` Strategy — honouring AMB-07 / DR-1 ("configuration is data, not constants"). `Core` never learns the word "Duo".
- **Memento as single source of truth on reload:** `last_placed_piece` was added to the frozen `Memento` and the JSON round-trip so a restored Duo game scores identically (SC-1).
- **Deterministic, contract-tested Duo:** AI-vs-AI determinism and the Duo bonus/tie rules are pinned by tests (`test_duo_game.py`, `test_scoring.py`), not prose.
- **UX guardrails derived from data:** seat buttons and the title are driven off `/state` (`players.length`, `scoring_rule`) rather than hard-coded — see `prompts/denis_coding_duo_mode_gui.json`.

---

### Package: Architecture & Architecture Decision Record (co-owned with Richard Plummer)

**Description:**
Design-track work for Milestone 1: a reusable, three-persona LLM prompt that drives the full *Decision → Validated ADR* workflow, and the resulting binding ADR. Co-owned by the project's Design pairing (Richard + Denis); I authored the prompt and the ADR document committed in `5b8aaee`. The ADR selects **Hexagonal (Ports & Adapters)** with **Strategy + Command + Builder + Memento** (`ADR-FINAL-P2`), which is the foundation the entire engine — and my Duo work above — is built on.

**Guideline(s) applied:**
- **`[Design — Team 5 · G1]`** Architecture Selection / ADR *(other team — Section 2, Application 1)*.
- **`[Design — Team 5 · G2 & G4]`** Refined-ADR (GoF) + Architecture/Design Validation *(other team — Section 2, Application 3)*.
- **`[Requirements — Team 4 · G3]`** embed resolved ambiguities downstream *(other team)*.

**Evidence Links:**
- **Commits:** `5b8aaee` (Created ADR prompt and ADR specifications).
- **Artifacts:** `guidelines/ARCHITECTURE_PROMPT_v1.md`, `design/ADR.md` (binding `ADR-FINAL-P2`; originally committed as `specifications/ADR.md` in `5b8aaee`, since relocated to `design/`).
- **Prompt logs:** `prompts/denis_adr_prompt.json` (prompt authoring), `prompts/denis_ard_implementation.json` (ADR generation).

**Note on ownership:** Architecture/ADR was a Design-track collaboration with Richard Plummer; Iven's portfolio also references this ADR as a downstream consumer. The commit and the two prompt logs above are mine; the *decision* was a shared Design-team responsibility.

---

### Package: `AGENTS.md` — repository context engineering

**Description:**
The repository-level, manually-written context file that every coding agent reads first. It encodes only the non-obvious constraints an agent would otherwise get wrong (the `Core.*` import boundary, the no-literal-`20`/`4` rule, Memento-as-source-of-truth, the lexicographic determinism contract, the procedural-`Bootstrap` rule) and points at the SPEC/ADR rather than re-explaining them.

**Guideline(s) applied:**
- **`[Coding — Team 2 · G1]`** Context-Aware Grounding via Minimal Manual Documentation *(own team)*.

**Evidence Links:**
- **Commits:** `f1d1bd0` (Created AGENTS.md applying Coding Guideline #1).
- **Artifacts:** `AGENTS.md`, `README.md` (language-choice line).
- **Prompt log:** `prompts/denis_agents_md_creation.json`.

> **Note:** This package is intentionally small but high-leverage — it is the file that propagated the architectural invariants into every later coding session (including the Duo work). It is also the source of Counterexamples 1 and 2 below.

---

## 2. Guideline Applications

> Documenting three applications of guidelines authored by **other** teams (I co-author the Coding/Team-2 package, so Coding guidelines are excluded here and noted as *own team* in Section 1).

### Application 1: *Architecture Selection — Phased ADR Workflow* **`[Design — Team 5 · G1]`**

**Guideline Description:**
Run architecture selection as a chained, multi-stage workflow — *Frame the Decision → Generate & preserve ≥2 alternatives → Critique explicitly → conclude with an ADR* — keeping intermediate artifacts so the reasoning stays inspectable, and never picking a winner before the critique completes. Human review is mandatory before acceptance.

**Context:**
Choosing the engine architecture before Milestone 1 implementation. The decision had to support a future configurable Duo variant *by configuration only*, and would be expensive to reverse — exactly the "real architectural scope" case the guideline targets.

**Application Process:**
1. Authored `guidelines/ARCHITECTURE_PROMPT_v1.md`, encoding the four stages as three explicit personas (Solution Architect → Development Architect → Senior Reviewing Architect) so an LLM cannot collapse them into a single summary, with one named output artifact per phase.
2. Ran the prompt against the binding `SPEC_M1.md`; generated three distinct candidates (Layered, Hexagonal, Plugin/Rule-Module) and kept all three alive through an 8-criterion comparison table (Phase-1 score 36 vs 31 vs 26).
3. Selected Hexagonal, then refined to `DS-hexagonal-2` (Strategy + Command + Builder + Memento) via a 9-row architecture×design rating table (41/45). A Senior-Architect critique pass produced five remediations that became drift-risk tripwires DR-1…DR-7.

**Outcome:**
- **What worked:** Rejected alternatives stayed documented in `design/ADR.md`, so later contributors could trace *why* Plugin-Module was dropped. DR-1 ("configuration is data, not constants") later became the literal-scanning test that protected my Duo work from hard-coded board sizes.
- **What didn't work:** The architecture was left language-neutral ("Java or Python" per NFR-2.1) — defensible for an ADR, but it deferred a real decision that bit downstream (see **Counterexample 2**). I also flagged the 6-port count as "Questionable" rather than resolving it.
- **Evidence:** `design/ADR.md` (`ADR-FINAL-P2`), `guidelines/ARCHITECTURE_PROMPT_v1.md`, `prompts/denis_adr_prompt.json`.

**Reflection:**
Would reuse. Forcing three personas with named artifacts is what stopped the LLM from rationalising its first idea. The one thing I would change: treat "human review before acceptance" as the moment to *close* deferred decisions (like language), not just to approve the analysis.

---

### Application 2: *Define the Testing Objective + Structured Test Prompts* **`[Testing — Team 3 · G1 + G2]`**

**Guideline Description:**
Before generating tests, anchor an explicit, verifiable testing objective in concrete sources (requirements, scope boundaries, edge/negative cases). Then prompt for the tests with a structured role/context/constraints/output skeleton so the generated tests are relevant and executable.

**Context:**
The whole Duo vertical, and specifically the Duo-mode GUI guardrails (`prompts/denis_coding_duo_mode_gui.json`): when launched in Duo (2 players), the start-screen buttons for 3–4 players must be disabled and the title must read "Blokus Duo".

**Application Process:**
1. Stated a precise, verifiable objective per unit *before* coding — e.g. "DuoScoring awards the all-pieces-placed bonus only when a player has *zero* remaining squares; ties produce co-winners" (`tests/core/test_scoring.py`), and "Duo runs are deterministic across AI-vs-AI" (`tests/core/test_duo_game.py`).
2. Followed the repo's existing **static GUI test** convention (assert on the text of `gui.js` / `game.html` / `style.css`) and wrote 4 failing tests first in `tests/adapters/test_web_gui_mode_labels_static.py`.
3. Ran the RED→GREEN→full-suite loop (`uv run pytest`); confirmed the runtime contract independently with a FastAPI `TestClient` probe of `/state` (Duo → `scoring_rule="duo"`, 2 players; Classic → `"classic"`, 4).

**Outcome:**
- **What worked:** The objective-first discipline kept the full suite green (180 passing) across the Duo work, and the determinism objective produced a regression test that pins AI behaviour rather than trusting prose.
- **What didn't work:** The repo's static-text tests verify the *file content*, not rendered behaviour — a green test does not prove a button is actually un-clickable in a browser (see **Counterexample 3**).
- **Evidence:** `tests/core/test_scoring.py`, `tests/core/test_duo_game.py`, `tests/adapters/test_web_gui_mode_labels_static.py`, `prompts/denis_coding_duo_mode_gui.json` (`verification` block: RED 4/4 → GREEN 4/4 → 180 passed).

**Reflection:**
Defining the objective in terms of *the rule* ("co-winners on a tie") rather than *the code* ("function returns X") is what made the tests double as living documentation of Duo's scoring. I would extend the testing objective to require a behavioural check for any *interactive* UI guardrail, not just a static-text assertion.

---

### Application 3: *Validate the Decision + Refine with Patterns* **`[Design — Team 5 · G4 (with G2)]`**

**Guideline Description:**
After an architecture is selected, validate it against its own decision basis: re-check that the rationale's assumptions/trade-offs are explicit, formulate quality-attribute scenarios, contrast the choice with rejected alternatives, and surface possible decision violations — with the LLM as analytical assistant and a human making the final call. (G2 adds the refinement step: propose multiple GoF-pattern design solutions in a strict, comparable output format and rate them.)

**Context:**
The same ADR effort, Phases 2–3. Having selected Hexagonal, I needed to (a) refine it into a concrete pattern-based design and (b) show the decision still held under scrutiny — not just assert it.

**Application Process:**
1. **Refine (G2):** generated nine design solutions (3 architectures × 3 designs) as strict JSON with a per-design human-review checklist and a 9-row rating table, so successive runs were structurally comparable; selected `DS-hexagonal-2`.
2. **Validate (G4):** ran a Decision Basis Audit, then one quality-attribute scenario per attribute (testability, configurability, performance, portability, maintainability, reproducibility), each *contrasted with the rejected alternative*.
3. Recorded a 7-row Drift Risk register with concrete tripwires (e.g. FR-3.4 lexicographic tie-break → determinism tripwire DR-3; Memento-carries-ConfigVO → DR-4) and a Final Review Brief split into Valid / Questionable / Follow-up.

**Outcome:**
- **What worked:** The drift-risk tripwires turned an architectural decision into *executable* checks — DR-1 and DR-3 are now real tests (`test_config_vo_literals.py`, the golden-move determinism test). The "rejected alternatives" survived as citable IDs.
- **What didn't work:** Scope was deliberately narrowed ("ignore Milestone 2 / Duo") to keep M1 focused — correct at the time, but it meant the ADR's decision basis did *not* anticipate the Duo work I later built on it, and the boundary note leaked into `AGENTS.md` and went stale (see **Counterexample 1**).
- **Evidence:** `design/ADR.md` (Phase 2 JSON design set + Phase 3 audit/scenarios/Drift-Risk register), `prompts/denis_ard_implementation.json` (`scope_adjustment` + `decisions_made_in_authoring`).

**Reflection:**
Validating against quality-attribute scenarios *contrasted with rejected options* is far stronger than a "this looks good" review — it forced me to defend the choice, not restate it. Would reuse, and would re-open the ADR (rather than rely on a stale scope note) the moment Duo became in-scope.

---

> **Additional applications (own team / supporting):**
> **`[Requirements — Team 4 · G3]`** *Proactively detect and resolve ambiguity, embedding resolved intent downstream* — `ARCHITECTURE_PROMPT_v1.md` consumed `AMBIGUITY_LOG.md` and translated the 8 closed ambiguities into a binding "architectural implications" table (most notably AMB-07 → no-fork configurability), so resolved intent propagated into the architecture rather than being re-litigated.
> **`[Coding — Team 2 · G1 / G4]`** *(own team)* — `AGENTS.md` minimal context grounding, and atomic task decomposition for the Duo plan, as described in Section 1.

---

## 3. Counterexamples

### Counterexample 1: Minimal context file goes stale — `AGENTS.md` still says "Duo is out of scope" after Duo shipped

**Failure Description:**
**Applied guideline: `[Coding — Team 2 · G1]`** (Context-Aware Grounding via Minimal Manual Documentation). The expected outcome is a small, authoritative file that an agent can trust. `AGENTS.md` line 9 states *"Milestone 2 (Duo) is out of scope for current work. Do not add Duo-named paths."* and line 21 states *"No GUI libraries … CLI only (EX-1)."* Both are now false: the repository ships a full Duo mode (`--duo`, `DUO_CONFIG_JSON`, `DuoScoring`) and a FastAPI web GUI. An agent that obeyed `AGENTS.md` literally would refuse to do the very work that has already been merged.

**Diagnosis:**
- **Root Cause:** The guideline optimises for *minimal + manual*, which is exactly what makes the file cheap to write — and cheap to forget. There is no mechanism tying a hand-written constraint to the code that would invalidate it.
- **Why the Guideline Failed:** "Minimal manual documentation" assumes a human updates the file when reality changes. Across a fast Duo milestone (≈17 commits in a day) the code moved and the prose didn't. My own Duo-GUI session log explicitly notes the contradiction and proceeds anyway because the user's instruction outranks the stale note.
- **Boundary Condition:** Manual context files drift whenever a scope/constraint statement is not co-located with (or checked against) the artifact that would falsify it.

**Refinement:**
- **Updated Guideline:** Constraints that are *falsifiable by code* must either (a) be expressed as a test/tripwire (as DR-1 was), or (b) carry a "valid-as-of `<commit>`/milestone" stamp and be reviewed at every milestone boundary. Scope notes ("X is out of scope") should be deleted the moment X is implemented, in the same PR.
- **How It Was Tested (evaluated):** A 1-line grep tripwire could assert that if `src/**` contains `scoring_rule == "duo"`, then `AGENTS.md` must not claim Duo is out of scope. (Proposed; not yet committed.)
- **Evidence:** `AGENTS.md:9`, `AGENTS.md:21`; `src/core/scoring.py` (`DuoScoring`), `src/app.py` (`--duo`); `prompts/denis_coding_duo_mode_gui.json` → `notes[0]`.

**Prompt/Context Used:**
```
Based on Topic-2_Guidelines.md Guideline 1, create an AGENTS.md.
Use design/ and specifications/ to produce the instructions file.
[ADR scope at the time: Milestone 2 (Duo) excluded — DR-6 forbids Duo-named paths]
```

**AI Output (the line that later went stale):**
```markdown
- Milestone 2 (Duo) is out of scope for current work. Do not add Duo-named paths.
```

---

### Counterexample 2: Language-neutral ADR → dual-toolchain context an agent can follow into the wrong stack

**Failure Description:**
**Applied guideline: `[Design — Team 5 · G1]`** (Architecture Selection / ADR). NFR-2.1 permits "Java/Maven *or* Python/uv", and the ADR faithfully kept the architecture language-neutral. Propagated into `AGENTS.md`, this produced a context file listing **both** Java/Maven and Python/uv build commands. An agent grounding on that file had a 50/50 chance of scaffolding the wrong toolchain — the opposite of what a grounding file is for.

**Diagnosis:**
- **Root Cause:** A genuine project decision (which language) was deferred at ADR time and then encoded as *ambiguity* in a downstream artifact that is supposed to be unambiguous.
- **Why the Guideline Failed:** The ADR guideline correctly separates "architecture" from "implementation tech", so leaving language open is *correct for the ADR*. The failure is at the seam: a language-neutral decision must not be copied verbatim into an operational grounding file without a chosen branch.
- **Boundary Condition:** Any not-yet-made implementation decision that is allowed to flow unchanged into agent-facing operational docs.

**Refinement:**
- **Updated Guideline:** When an ADR intentionally defers an implementation choice, record it as an explicit "decision pending" item with an owner; operational/grounding docs must commit to a single branch (or be blocked) rather than mirror the open choice. I subsequently committed the repo to Python/uv and rewrote the build section accordingly (`prompts/denis_agents_md_creation.json`, turn 4) — and deliberately did *not* retro-edit the baseline ADR/SPEC, flagging that trade-off instead.
- **How It Was Tested (evaluated):** After the fix, `AGENTS.md` carries a single Python/uv build/test/run section; `uv sync && uv run pytest` is the one supported path. The dual-language branch is gone.
- **Evidence:** `prompts/denis_agents_md_creation.json` (turns 3–4: "The python is chosen now … Update everything"); `AGENTS.md:11-19` (Python/uv only); `README.md` ("Implementation language: Python (uv)").

**Prompt/Context Used:**
```
The python is chosen now as the programming language for the project.
Update everything to clearly state this.
```

**AI Output (initial defect — pre-fix `AGENTS.md`):**
```markdown
## Build / test / run
NFR-2.1 permits Java/Maven OR Python/uv.
- Java:   mvn test ; mvn package
- Python: uv sync ; uv run pytest
```

---

### Counterexample 3: Static GUI tests pass but prove nothing about behaviour

**Failure Description:**
**Applied guideline: `[Testing — Team 3 · G1]`** (Define the Testing Objective). The repo's GUI testing convention asserts on the *text* of `gui.js`/`game.html`/`style.css` (no headless browser). For the Duo seat-button guardrail, the objective "disable seats 3–4 in Duo" was met by a green static test that checks the JS *contains* `refreshStartOptions`/`maxHumanSeats` and the CSS *defines* `.start-option.disabled`. None of that proves the rendered button is actually un-clickable — a CSS class can be present while `pointer-events`/`disabled` is never wired, and the test stays green.

**Diagnosis:**
- **Root Cause:** The testing objective was anchored to a *static artifact* ("the file mentions the right symbol") instead of an *observable behaviour* ("clicking seat 4 in Duo does nothing").
- **Why the Guideline Failed:** Team 3's "anchor success criteria in concrete, verifiable sources" was satisfied at the file level; the criterion was concrete but at the wrong layer for an interactive guardrail. I even discovered, while implementing, that an existing `.start-option:disabled` rule used `cursor: wait`, so I had to add a *distinct* `.start-option.disabled` class — a behavioural nuance a static test cannot exercise.
- **Boundary Condition:** Any UI guardrail whose success is *experiential* (the user cannot do X) rather than textual (the file says X).

**Refinement:**
- **Updated Guideline:** For interactive guardrails, the testing objective must include at least one behavioural check (headless DOM or `TestClient`-driven runtime assertion) in addition to the static-text assert. As a partial mitigation I verified the *data contract* at runtime with a FastAPI `TestClient` probe of `/state` (Duo → 2 players / `scoring_rule="duo"`), which is closer to behaviour than file text.
- **How It Was Tested (evaluated):** Static tests RED 4/4 → GREEN 4/4; full suite 180 passed; `/state` runtime probe confirmed Duo vs Classic. A true DOM-level "seat 4 is non-interactive" assertion is still **not** present and is the recommended follow-up.
- **Evidence:** `tests/adapters/test_web_gui_mode_labels_static.py`; `prompts/denis_coding_duo_mode_gui.json` → `investigation_findings` (static-test convention) and `verification`.

**Prompt/Context Used:**
```
Make the 3-4 player seat buttons disabled in duo mode, and add a "Duo"
suffix to the title in the left corner when the gui is launched in duo mode.
[followed the repo's existing static GUI test convention, test-first]
```

**AI Output (passing static test that does not assert behaviour):**
```python
def test_gui_caps_seats_by_mode():
    js = read("src/static/gui.js")
    assert "maxHumanSeats" in js
    assert "refreshStartOptions" in js   # asserts the symbol exists,
                                          # NOT that seat 4 is un-clickable
```

---

## 4. AI Usage Disclosure

### Tools and Models Used

| Tool/Model | Usage | Validation Method |
|---|---|---|
| Claude Opus 4.7 — Claude Code (VS Code extension) | Authoring `ARCHITECTURE_PROMPT_v1.md` + `design/ADR.md` (`prompts/denis_adr_prompt.json`, `prompts/denis_ard_implementation.json`); `AGENTS.md` (`prompts/denis_agents_md_creation.json`); full Blokus Duo implementation via brainstorm → plan → execute; Duo-GUI guardrails (`prompts/denis_coding_duo_mode_gui.json`) | `uv run pytest` (180 tests), TDD RED→GREEN, FastAPI `TestClient` runtime probes, human review of every diff before commit |
| `superpowers` skills (Claude Code) — TDD, brainstorming, writing-plans, executing-plans | Test-first discipline for the Duo work; design spec + implementation plan (`docs/superpowers/specs/…`, `docs/superpowers/plans/…`) | Plan reviewed before execution; each plan step gated by its own tests |
| Downstream LLM (per Design G1 — Opus/Sonnet class) | Intended consumer of `ARCHITECTURE_PROMPT_v1.md` to produce ADR analysis | Human architect (Richard / Denis) makes the final call; LLM output treated as analytical scaffolding |

### Evaluation Methods

1. **Test-Driven Validation:** New behaviour landed test-first (RED→GREEN). The Duo-GUI change went RED 4/4 → GREEN 4/4; the full suite was 180 passing (`uv run pytest`).
2. **Runtime Contract Probes:** FastAPI `TestClient` hit `/state` before game start to confirm Duo (`scoring_rule="duo"`, 2 players) vs Classic (`"classic"`, 4) — verifying behaviour the static tests cannot.
3. **Executable Architecture Tripwires:** ADR drift risks were converted to tests where possible (DR-1 literal scan, DR-3 golden-move determinism), so architectural claims are checked, not just asserted.
4. **Human-in-the-Loop Review:** The three-persona ADR workflow ends in a human architect decision; every LLM diff was read before commit.

### Time Investment

- AI prompting and refinement: **~4 h**
- Reviewing AI outputs: **~8 h**
- Testing and validation: **~5 h**
- Documentation (ADR prompt, ADR, AGENTS.md, Duo design/plan, this portfolio): **~4 h**

---

## 5. Reflections

### What I Learned

- **Configuration over forking is an architectural superpower.** Because the ADR locked in "configuration is data, not constants" (DR-1), adding the entire Duo variant meant adding *data* + one Strategy, not a parallel engine. The discipline I paid for at ADR time refunded itself completely during Milestone 2.
- **A grounding document is only as good as its freshness.** `AGENTS.md` was my highest-leverage artifact *and* the source of two of my three counterexamples — minimal manual docs drift, and a deferred decision copied into one becomes a live hazard.
- **"Tests pass" is layer-specific.** Static-text GUI tests answered "does the file say the right thing?" — not "can the user still click the wrong button?". The objective has to name the layer where success is actually observable.

### Skills Developed

- Authoring reusable, multi-persona prompts that force inspectable reasoning (the three-stage ADR prompt) instead of a one-shot answer.
- Extending a Hexagonal core through its existing seams (Strategy/Builder/Memento) without leaking a new concept into the domain — the no-fork Duo implementation.
- Turning architectural decisions into executable tripwires (DR-1/DR-3 as tests) so design intent survives in CI.

### Future Improvements

- **Close deferred decisions at the review gate.** The language-neutral ADR was defensible, but I should have forced the Java-vs-Python commitment before it propagated into operational docs (Counterexample 2).
- **Tie scope/constraint notes to code.** Either express them as tripwires or stamp them with a milestone and delete them in the same PR that invalidates them (Counterexample 1).
- **Add a behavioural check for every interactive UI guardrail**, not only a static-text assertion (Counterexample 3).
- **Re-open the ADR instead of relying on a stale "out of scope" note** the moment a deferred milestone (Duo) becomes active.

---

*Submitted by Denis Maxheimer — Team 2 (Coding); Architecture/Design + Blokus Duo, Generative Software Engineering, May 2026.*
