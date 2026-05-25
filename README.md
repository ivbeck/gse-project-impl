# Blokus Project

A Python implementation of the Blokus game engine following the project's Hexagonal (Ports & Adapters) architecture. The project provides a console (CLI) player and an optional local web GUI powered by FastAPI + Uvicorn.

**Implementation language:** Python (managed with `uv`). See [AGENTS.md](AGENTS.md) for coding-agent context and developer commands.

## Getting started (summary)

These steps assume a fresh clone of the repository. Recommended: use a Python virtual environment.

1. Create and activate a virtual environment (Windows example):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # PowerShell
# or (cmd): .\.venv\Scripts\activate
```

Bootstrap `pip` in the venv (if needed)

Some Python installations or freshly created virtual environments may not include `pip` by default. If you see errors like "No module named pip" or later see "uv missing", bootstrap `pip` before installing other packages.

```bash
# In the activated venv, try ensurepip first (preferred)
python -m ensurepip --upgrade
python -m pip install --upgrade pip setuptools wheel

# If ensurepip is not available, use get-pip.py as a fallback
curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
rm get-pip.py

# Prefer 'python -m pip' so the pip used matches the active interpreter
python -m pip --version
```

2. Install `uv` (project task runner) and sync dependencies:

```bash
# Option A — install into the active venv
python -m pip install --upgrade pip
python -m pip install uv

# Option B — install uv with pipx (keeps it isolated from the venv)
pipx install uv

# Then sync project dependencies defined in pyproject.toml
uv sync
```

3. Verify tests run:

```bash
uv run pytest
```

## Run modes

CLI (console) mode — plays in the terminal

```bash
uv run python -m app
# or, if you have installed the package entrypoint in the active environment:
uv run blokus-engine
```

Web GUI mode — starts a local FastAPI server and serves the browser UI

```bash
uv run python -m app --gui
# or (installed entrypoint):
uv run blokus-engine --gui
```

Open your browser at: http://127.0.0.1:8000

Play Blokus Duo (14x14, 2 players) with the GUI or CLI by adding `--duo`:

```bash
uv run python -m app --gui --duo
```

Notes on commands

- The correct wrapper is `uv run ...`. Do NOT run `python -m uv run ...` — that invocation is incorrect and will fail. If the `blokus-engine` script entrypoint is not installed into your environment, use `uv run python -m app` instead.
- If you prefer to run the web server directly (without `uv`), you can run `python -m src.web_main` from a configured environment that puts `src/` on `PYTHONPATH`, but using `uv run python -m app --gui` is the supported, reproducible path.

## Troubleshooting

- I only see console output and no browser UI: you likely started the CLI (no `--gui` flag) or used the wrong `uv` invocation. Re-run with `uv run python -m app --gui`.
- Server not reachable at http://127.0.0.1:8000: check the terminal where you started the app — Uvicorn logs should show the server URL (look for "Uvicorn running on http://127.0.0.1:8000"). If port 8000 is in use, edit `src/web_main.py` and change the `port=` argument passed to `uvicorn.run(...)`, then restart.
- Missing dependencies / import errors: ensure `uv sync` completed successfully and that you activated the venv before running commands. If you installed `uv` globally with `pipx`, ensure you still activate the project venv when running Python module commands.
- Static UI not loading or template errors: verify `src/static/` and `src/templates/game.html` exist. The FastAPI orchestrator mounts `/static` and serves `game.html` at `/`.

If you still have issues, share the terminal output (copy the last ~100 lines) and I can help diagnose further.

## Development workflow

- Feature branch per feature. Merge to `main` via Pull Request; delete feature branch after merge.
- Follow the project's Architectural invariants in [AGENTS.md](AGENTS.md) and design documents in the `design/` folder.

## CI checks (push)

The GitHub Actions workflow runs on every push and enforces the same quality gates used locally.

Run these commands before pushing:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
```

## Architecture & resources

- Design & architecture decisions: [design/ADR.md](design/ADR.md)
- Project spec: [specifications/SPEC_M1.md](specifications/SPEC_M1.md)
- Agent/context notes: [AGENTS.md](AGENTS.md)

## Useful commands

```bash
# Create venv (Windows PowerShell shown)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install uv (either in venv or with pipx)
pip install uv
# or
pipx install uv

# Sync project deps
uv sync

# Run tests
uv run pytest

# Run CLI
uv run python -m app

# Run web GUI
uv run python -m app --gui
```

## Team & Individual MD Files

All relevant md files that are to be turned in and graded can be found in the _deliverables_ folder

## Tasks & Responsibilities

- Requirements: All
- Design: Richard + Denis
- Coding: Petar + Iven
- Testing: Petar + Iven
- Debugging: Denis + Iven
- Reviewing : Richard
