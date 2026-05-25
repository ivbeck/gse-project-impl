# GitHub Actions testing suite setup
_Exported on 5/25/2026 at 17:14:40 GMT+2 from Cursor (3.4.20)_

---

**User**

You are a senior CI/CD devops developer. Setup a comprehensive testing suite using github actions on each push

---

**Cursor**

I’ll inspect the current Python project setup first (test commands, dependency manager, and any existing workflows), then I’ll propose a concrete GitHub Actions plan for push-based comprehensive testing.

I found no existing GitHub workflow yet, so I’m now checking the project’s tooling (`uv`, pytest, lint/type tools) to shape the pipeline stages accurately.

I have enough context to draft the workflow structure, but two choices will materially change the plan: Python version matrix scope and strictness gates (coverage threshold / fail-on-warning). I’ll ask those now so the plan matches your expectations exactly.

**CI Scope Preferences**

> **Which Python version strategy should the GitHub Actions test suite use?**
> - Single version (3.12 only, fastest) — default aligned with current project requirement ✔
> - Matrix 3.12 + 3.13 (broader compatibility)
> - Matrix 3.11 + 3.12 + 3.13 (maximum coverage)

> **Which quality gates should fail CI on each push?**
> - Tests only (`uv run pytest`) ✔
> - Lint (`uv run ruff check .`) ✔
> - Formatting check (`uv run ruff format --check .`) ✔
> - Type checking (`uv run mypy src tests`) ✔
> - Coverage threshold enforcement (e.g., >=85%) ✔

---

**User**

Implement the plan as specified, it is attached for your reference. Do NOT edit the plan file itself.

To-do's from the plan have already been created. Do not create them again. Mark them as in_progress as you work, starting with the first one. Don't stop until you have completed all the to-dos.

---

**Cursor**

I’m starting implementation now and will work through each todo in order, beginning with dev-tooling updates in `pyproject.toml` before creating the workflow.

I’ve applied the `pytest-cov` and coverage threshold config in `pyproject.toml`; next I’ll add the GitHub Actions workflow with the selected push-only Python 3.12 pipeline and gates.

The workflow file is in place; I’m now validating and finalizing the quality-gate and coverage-artifact todos, then I’ll update README and run the full local verification commands.

All todos are implemented in files; I’m now running the same local CI command chain (`uv sync`, lint, format-check, mypy, pytest) to verify everything end-to-end.

The new CI pipeline is correct, but local verification exposed pre-existing Ruff issues in tests; I’m applying minimal lint-only cleanups so the push workflow is truly green.

I’ve done the minimal lint cleanups in affected tests and excluded local `build/` artifacts from Ruff checks; next I’ll finish the remaining lint fixes and rerun the full CI command chain.

Implemented the full push-based CI suite from your plan, without modifying the plan file.

### What I changed

- Added GitHub Actions workflow at `.github/workflows/ci.yml`:
  - Triggers on every `push`
  - Uses Python `3.12`
  - Uses `uv` with cache
  - Installs deps via `uv sync --all-extras --dev`
  - Runs gates in order:
    - `uv run ruff check .`
    - `uv run ruff format --check .`
    - `uv run mypy src tests`
    - `uv run pytest`
  - Uploads `coverage.xml` as artifact (`coverage-xml`) on every run (`if: always()`)

- Updated `pyproject.toml`:
  - Added `pytest-cov` to dev tooling
  - Added pytest coverage options:
    - `--cov=src`
    - `--cov-report=term-missing`
    - `--cov-report=xml`
    - `--cov-fail-under=85`
  - Added Ruff `extend-exclude = ["build"]` to avoid local build artifact noise

- Updated `README.md`:
  - Added a `CI checks (push)` section with the exact local reproduction commands.

- Fixed minimal pre-existing Ruff issues in tests so lint is cleaner:
  - `tests/adapters/test_cli.py`
  - `tests/adapters/test_human_player.py`
  - `tests/adapters/test_json_config_source.py`
  - `tests/adapters/test_web_player_adapter.py`
  - `tests/adapters/test_web_presentation_adapter.py`
  - `tests/core/test_config_vo_literals.py`
  - `tests/core/test_piece_catalog.py`
  - `tests/core/test_ports.py`

### Verification run

Executed locally:

- `uv run ruff check .` ✅ passed
- `uv run ruff format --check .` ❌ fails due existing repo-wide formatting baseline (40 files would be reformatted)
- `uv run mypy src tests` ✅ passed
- `uv run pytest` ✅ passed (`180 passed`, coverage `90.72%`, threshold `85%` satisfied)

All plan todos are completed and marked completed.

### Important note

Because you selected **format check as a hard gate**, CI will currently fail on pushes until the repository formatting baseline is normalized. Fastest fix is to run and commit:

- `uv run ruff format .`

If you want, I can do that formatting pass next as a single mechanical cleanup commit candidate.

