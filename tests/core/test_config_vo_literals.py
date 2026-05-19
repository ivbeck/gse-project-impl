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
