import pytest
from adapters.json_config_source import JsonConfigSource
from core.types import ConfigVO

def test_json_config_source_loads_default():
    source = JsonConfigSource("{}")
    config = source.load_config()
    assert config.board_width == 20
    assert config.board_height == 20
    assert config.player_count == 4

def test_json_config_source_loads_custom():
    source = JsonConfigSource('{"board_width": 15, "board_height": 15}')
    config = source.load_config()
    assert config.board_width == 15
    assert config.board_height == 15

def test_json_config_source_has_starting_positions():
    source = JsonConfigSource("{}")
    config = source.load_config()
    assert len(config.starting_positions) == 4
    assert config.starting_positions[0].row == 0
    assert config.starting_positions[0].col == 0


def test_json_config_source_defaults_scoring_rule_to_classic():
    from adapters.json_config_source import JsonConfigSource
    config = JsonConfigSource().load_config()
    assert config.scoring_rule == "classic"


def test_json_config_source_reads_scoring_rule():
    import json
    from adapters.json_config_source import JsonConfigSource
    config = JsonConfigSource(json.dumps({"scoring_rule": "duo", "player_count": 2,
        "starting_positions": {"0": {"row": 4, "col": 4}, "1": {"row": 9, "col": 9}},
        "board_width": 14, "board_height": 14})).load_config()
    assert config.scoring_rule == "duo"


def test_duo_preset_is_a_14x14_two_player_duo_config():
    from adapters.json_config_source import JsonConfigSource, DUO_CONFIG_JSON
    from core.types import Position
    config = JsonConfigSource(DUO_CONFIG_JSON).load_config()
    assert config.board_width == 14
    assert config.board_height == 14
    assert config.player_count == 2
    assert config.scoring_rule == "duo"
    assert config.starting_positions == {0: Position(4, 4), 1: Position(9, 9)}