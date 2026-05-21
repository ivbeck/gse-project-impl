# Pyproject.toml CLI argument usage
_Exported on 5/20/2026 at 14:41:11 GMT+2 from Cursor (3.4.20)_

---

**User**

@pyproject.toml (35-37) 
please make this use cli with args

---

**Cursor**

I’ll check how `src.app` currently parses arguments, then update the `pyproject` script entry so the CLI command routes through the args-based entrypoint.

I found `src.app:main` already supports `--gui`, so I’m updating `project.scripts` to expose a single args-based CLI entrypoint instead of a separate web script.

Updated `pyproject.toml` to use a single CLI entrypoint with args parsing:

- Replaced separate script entries with:
  - `blokus-engine = "src.app:main"`

This now routes everything through `src.app:main`, which already supports flags like `--gui`.

Use it like:
- `uv run blokus-engine` (CLI mode)
- `uv run blokus-engine --gui` (web mode)

If your environment was already synced, run `uv sync` once so the updated script entry is installed.

---

**User**

❯ uv run blokus-engine --gui
error: Failed to spawn: `blokus-engine`
  Caused by: No such file or directory (os error 2)
❯ uv sync
Resolved 31 packages in 225ms
      Built blokus-engine @ file:///home/iven
Prepared 1 package in 938ms
Installed 1 package in 1ms
 + blokus-engine==0.1.0 (from file:///home/iven/coding/projects/gse-project-impl)
❯ uv run blokus-engine --gui
Traceback (most recent call last):
  File "/home/iven/coding/projects/gse-project-impl/.venv/bin/blokus-engine", line 4, in <module>
    from src.app import main
ModuleNotFoundError: No module named 'src'

…ding/projects/gs

---

**Cursor**

That traceback means the console script is trying to import `src.app` as a Python package, but `src` isn’t an importable package in this layout. I’ll inspect the project structure and fix the script target to a real import path.

I found the packaging layout issue: installed modules are top-level (`app`, `bootstrap`, etc.), not under `src.*`. I’m updating the script target to `app:main` and quickly verifying with `--help`.

Fixed — the script entrypoint was pointing to the wrong module path for your package layout.

### What I changed
In `pyproject.toml`:
- `blokus-engine = "src.app:main"` → `blokus-engine = "app:main"`

### Why this works
Your package build installs modules as top-level (`app`, `bootstrap`, `core`, etc.), not under a `src` package namespace. So `src.app` is not importable in the installed environment.

### Verified
Ran:

- `uv sync`
- `uv run blokus-engine --help`

and it now resolves correctly, showing the CLI options (including `--gui`).

You should now be able to run:

- `uv run blokus-engine --gui`

---

**User**

what other build systems are available

---

**Cursor**

For `pyproject.toml` in Python, the main alternatives to `setuptools.build_meta` are:

- `hatchling.build` (Hatch) — modern, simple packaging backend
- `poetry.core.masonry.api` (Poetry backend)
- `flit_core.buildapi` (Flit) — lightweight for pure Python packages
- `pdm.backend` (PDM backend)
- `mesonpy` (Meson Python) — good for compiled/native extensions
- `maturin` (Rust/PyO3 projects)
- `scikit_build_core.build` (CMake-based native builds)

`uv` works with standard PEP 517 build backends, so you can use any of these as long as `[build-system]` is configured correctly.

If you want, I can suggest the best one for this repo specifically (pure Python CLI + tests) and give you the exact `pyproject.toml` snippet.

---

**User**

hatchling it is

---

**Cursor**

Perfect — I’ll switch the build backend to Hatchling and add the minimal Hatch config so your current `src` layout still installs the same top-level modules (`app`, `core`, `adapters`, etc.).

I’m going to patch `pyproject.toml` to use Hatchling and add source mapping so `src/` is treated as import root (keeping `app:main` valid). Then I’ll run `uv sync` + a CLI smoke test.

Switched to Hatchling and verified it works.

### Updated `pyproject.toml`
- `[build-system]`
  - `requires = ["hatchling"]`
  - `build-backend = "hatchling.build"`
- Added Hatch wheel config to preserve your `src/` import-root behavior:
  - `[tool.hatch.build.targets.wheel]`
  - `only-include = ["src"]`
  - `sources = ["src"]`

This keeps `blokus-engine = "app:main"` working with your current module layout.

### Verification
I ran:

- `uv sync`
- `uv run blokus-engine --help`

and the CLI resolves correctly.

