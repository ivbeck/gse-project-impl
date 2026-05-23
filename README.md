# Blokus Project

A Python implementation of the Blokus game engine following the project's Hexagonal (Ports & Adapters) architecture.

**Implementation language:** Python (managed with [`uv`](https://docs.astral.sh/uv/)). See [AGENTS.md](AGENTS.md) for coding-agent context and developer commands.

## Quick start

Prerequisites

- Python 3.12 or newer (see `requires-python` in `pyproject.toml`).
- `uv` for environment & task management — install via the official guide: https://docs.astral.sh/uv/ (example using `pipx` shown below).

Install & sync project dependencies

```bash
# (optional) install uv if you don't have it
pipx install uv

# sync environment and install dependencies defined in pyproject.toml
uv sync
```

Run the test suite

```bash
uv run pytest
```

Run the application

The project exposes a module entry point; run it with:

```bash
uv run python -m app
# or run the installable script entrypoint (if registered in your environment):
uv run blokus-engine
```

Notes

- The repository uses `uv` for all development tasks (installing, running, testing). Do not introduce alternative environment managers without agreement.
- No network access is allowed at runtime for the core engine (see project constraints in [AGENTS.md](AGENTS.md)).

## Development workflow

- Feature branch per feature. Merge to `main` via Pull Request; delete feature branch after merge.
- Follow the project's Architectural invariants in [AGENTS.md](AGENTS.md) and design documents in the `design/` folder.

## Architecture & resources

- Design & architecture decisions: [design/ADR.md](design/ADR.md)
- Project spec: [specifications/SPEC_M1.md](specifications/SPEC_M1.md)
- Agent/context notes: [AGENTS.md](AGENTS.md)

## Useful commands

```bash
# Install uv (optional)
pipx install uv

# Install / sync deps
uv sync

# Run tests
uv run pytest

# Run the app
uv run python -m app
```

## Tasks & Responsibilities

- Requirements: All
- Design: Richard + Denis
- Coding: Petar + Iven
- Testing: Petar + Iven
- Debugging: Denis + Iven
- Reviewing : Richard
