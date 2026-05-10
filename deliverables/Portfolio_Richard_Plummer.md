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
Applying this guideline confirmed that LLM-assisted ambiguity detection is most valuable early in the requirements phase, before implementation assumptions harden — several of our resolutions (particularly AMB-03 and AMB-05) would have caused costly rework had they surfaced during coding. We would use it again, but with a tighter prompt that constrains the LLM to a single document's scope at a time, which would have avoided the false positive on FR-4.3 from the start.

---

### Application 2: `[Guideline Name]` from `[Topic]` Team

**Guideline Description:**  
Briefly describe the guideline you applied.

**Context:**  
What task or feature were you working on when you applied this guideline?

**Application Process:**

1. `[Step 1]`
2. `[Step 2]`
3. `[Step 3]`

**Outcome:**

- **What worked:** `[Description]`
- **What didn't work:** `[Description]`
- **Evidence:** `[Link to prompt, code, tests, or documentation]`

**Reflection:**  
What did you learn from applying this guideline? Would you use it again in a similar context?

---

### Application 3: `[Guideline Name]` from `[Topic]` Team

**Guideline Description:**  
Briefly describe the guideline you applied.

**Context:**  
What task or feature were you working on when you applied this guideline?

**Application Process:**

1. `[Step 1]`
2. `[Step 2]`
3. `[Step 3]`

**Outcome:**

- **What worked:** `[Description]`
- **What didn't work:** `[Description]`
- **Evidence:** `[Link to prompt, code, tests, or documentation]`

**Reflection:**  
What did you learn from applying this guideline? Would you use it again in a similar context?

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

### Counterexample 3: `[Title]`

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
