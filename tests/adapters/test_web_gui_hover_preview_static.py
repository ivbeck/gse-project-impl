from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GUI_JS = ROOT / "src" / "static" / "gui.js"
STYLE_CSS = ROOT / "src" / "static" / "style.css"
GAME_HTML = ROOT / "src" / "templates" / "game.html"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def test_hover_preview_uses_same_catalog_orientation_as_submitted_move():
    gui = _read(GUI_JS)

    assert "function getSelectedOrientationCells()" in gui
    assert "getPieceOrientation(selectedPiece, currentOrientation)" in gui
    assert "function renderHoverPreview(anchorRow, anchorCol)" in gui
    assert "row: anchorRow + cell.rowOffset" in gui
    assert "col: anchorCol + cell.colOffset" in gui
    assert "orientation_index: currentOrientation" in gui


def test_hover_preview_has_distinct_valid_invalid_and_occupied_styles():
    gui = _read(GUI_JS)
    css = _read(STYLE_CSS)

    for class_name in (
        "hover-preview-valid",
        "hover-preview-invalid",
        "hover-preview-occupied",
    ):
        assert class_name in gui
        assert f".cell.{class_name}::before" in css
    assert ".cell.hover-preview-occupied::before" in css
    assert "background: transparent" in css


def test_hover_preview_uses_delegated_board_hover_handlers():
    gui = _read(GUI_JS)

    assert "container.onmouseover = renderHoverPreviewFromEvent" in gui
    assert "container.onmousemove = renderHoverPreviewFromEvent" in gui
    assert "function renderHoverPreviewFromEvent(event)" in gui
    assert "event.target.closest('.cell')" in gui
    assert "renderHoverPreview(row, col)" in gui


def test_hover_preview_is_cleared_on_board_leave_and_successful_move():
    gui = _read(GUI_JS)

    assert "container.onmouseleave = clearHoverPreview" in gui
    assert "if (result.ok)" in gui
    assert "deselectPiece();" in gui


def test_piece_deselection_clears_hover_preview():
    gui = _read(GUI_JS)

    assert "function deselectPiece()" in gui
    assert "clearHoverPreview();" in gui
    assert "if (selectedPiece === pieceId)" in gui


def test_hover_anchor_is_kept_even_before_piece_selection():
    gui = _read(GUI_JS)

    render_start = gui.index("function renderHoverPreview(anchorRow, anchorCol)")
    anchor_assignment = gui.index(
        "hoverAnchor = { row: anchorRow, col: anchorCol }", render_start
    )
    selection_guard = gui.index(
        "if (selectedPiece === null || selectedPiece === undefined) return",
        render_start,
    )
    assert anchor_assignment < selection_guard


def test_endgame_panel_is_rendered_from_finished_state():
    gui = _read(GUI_JS)
    css = _read(STYLE_CSS)
    html = _read(GAME_HTML)

    assert 'id="endgame-panel"' in html
    assert "function renderEndGamePanel(state)" in gui
    assert "state.game_status !== 'FINISHED'" in gui
    assert "main-menu-button" in gui
    assert "function returnToMainMenu()" in gui
    assert "fetch('/reset'" in gui
    assert "state.winner_ids" in gui
    assert ".endgame-panel" in css
    assert ".endgame-menu-button" in css
    assert "#board.is-locked" in css


def test_skipped_player_banner_is_rendered_from_state():
    gui = _read(GUI_JS)
    css = _read(STYLE_CSS)
    html = _read(GAME_HTML)

    assert 'id="event-banner"' in html
    assert "function skippedPlayerMessage(skippedPlayers)" in gui
    assert "has no legal moves and was skipped" in gui
    assert "state.skipped_players" in gui
    assert ".event-banner" in css
