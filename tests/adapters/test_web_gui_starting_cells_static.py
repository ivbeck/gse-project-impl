from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUI_JS = ROOT / "src" / "static" / "gui.js"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def test_gui_marks_configured_starting_cells_not_fixed_corners():
    gui = _read(GUI_JS)
    assert "state.starting_positions" in gui
    assert "startingCells" in gui
    # The old fixed four-corner detection is gone.
    assert "ri === 0 && ci === 0" not in gui
