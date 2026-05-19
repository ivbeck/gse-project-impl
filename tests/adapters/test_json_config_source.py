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