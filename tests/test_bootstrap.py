def test_bootstrap_under_200_lines():
    import pathlib
    bootstrap = pathlib.Path("src/bootstrap.py")
    if bootstrap.exists():
        lines = len(bootstrap.read_text().splitlines())
        assert lines <= 200, f"Bootstrap is {lines} lines, must be ≤200"


def test_create_game_uses_duo_scoring_for_duo_config():
    from bootstrap import create_game
    from adapters.json_config_source import JsonConfigSource, DUO_CONFIG_JSON
    from core.scoring import DuoScoring
    config = JsonConfigSource(DUO_CONFIG_JSON).load_config()
    session = create_game(config)
    assert isinstance(session.scoring, DuoScoring)
    assert session.config.player_count == 2


def test_create_game_uses_classic_scoring_by_default():
    from bootstrap import create_game
    from adapters.json_config_source import JsonConfigSource
    from core.scoring import Scoring
    session = create_game(JsonConfigSource().load_config())
    assert isinstance(session.scoring, Scoring)
