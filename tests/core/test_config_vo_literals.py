def test_no_hardcoded_board_size_20():
    """Tripwire: fails if literal 20 appears in Core.* except PieceCatalog."""
    import pathlib, re
    core_path = pathlib.Path("src/core")
    for f in core_path.rglob("*.py"):
        if f.name == "piece_catalog.py":
            continue
        content = f.read_text()
        matches = re.findall(r'\b20\b', content)
        if matches:
            raise AssertionError(f"{f}: found hardcoded '20': {matches}")


def test_no_hardcoded_player_count_4():
    """Tripwire: fails if literal 4 appears in Core.* except PieceCatalog."""
    import pathlib, re
    core_path = pathlib.Path("src/core")
    for f in core_path.rglob("*.py"):
        if f.name == "piece_catalog.py":
            continue
        content = f.read_text()
        matches = re.findall(r'\b4\b', content)
        if matches:
            raise AssertionError(f"{f}: found hardcoded '4': {matches}")


def test_config_defaults_to_classic_scoring_rule():
    from core.types import ConfigVO, Position
    config = ConfigVO(
        board_width=20, board_height=20, player_count=4,
        starting_positions={0: Position(0, 0)},
    )
    assert config.scoring_rule == "classic"


def test_config_builder_sets_scoring_rule():
    from core.types import ConfigBuilder, Position
    config = (
        ConfigBuilder()
        .with_board_dimensions(14, 14)
        .with_player_count(2)
        .with_starting_positions({0: Position(4, 4), 1: Position(9, 9)})
        .with_scoring_rule("duo")
        .build()
    )
    assert config.scoring_rule == "duo"


def test_config_builder_rejects_unknown_scoring_rule():
    import pytest
    from core.types import ConfigBuilder, Position
    builder = (
        ConfigBuilder()
        .with_board_dimensions(14, 14)
        .with_player_count(2)
        .with_starting_positions({0: Position(4, 4), 1: Position(9, 9)})
        .with_scoring_rule("nonsense")
    )
    with pytest.raises(ValueError):
        builder.build()
