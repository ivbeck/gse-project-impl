from unittest.mock import patch
import app


def test_app_passes_duo_mode_to_cli():
    with (
        patch.object(app, "cli_main") as cli_main,
        patch("sys.argv", ["blokus-engine", "--duo"]),
    ):
        app.main()
    cli_main.assert_called_once_with("duo")


def test_app_defaults_to_classic_cli():
    with (
        patch.object(app, "cli_main") as cli_main,
        patch("sys.argv", ["blokus-engine"]),
    ):
        app.main()
    cli_main.assert_called_once_with("classic")
