from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUI_JS = ROOT / "src" / "static" / "gui.js"
GAME_HTML = ROOT / "src" / "templates" / "game.html"
STYLE_CSS = ROOT / "src" / "static" / "style.css"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def test_template_brand_name_has_id_for_mode_label():
    html = _read(GAME_HTML)
    assert 'id="brand-name"' in html


def test_gui_adds_duo_suffix_to_title_from_state():
    gui = _read(GUI_JS)
    assert "function updateModeLabels(state)" in gui
    assert "updateModeLabels(state)" in gui
    # Title in the left corner reflects Duo mode.
    assert "state.scoring_rule === 'duo'" in gui
    assert "'Blokus Duo'" in gui


def test_gui_disables_seat_buttons_beyond_player_count():
    gui = _read(GUI_JS)
    # Seat-count buttons above the configured player count are disabled, so
    # Duo (2 players) greys out the three- and four-human options.
    assert "maxHumanSeats" in gui
    assert "function refreshStartOptions()" in gui
    assert "Number(button.dataset.humanPlayers) > maxHumanSeats" in gui


def test_disabled_seat_button_has_unavailable_style():
    css = _read(STYLE_CSS)
    assert ".start-option.disabled" in css
