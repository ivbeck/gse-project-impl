def test_bootstrap_under_200_lines():
    import pathlib
    bootstrap = pathlib.Path("src/bootstrap.py")
    if bootstrap.exists():
        lines = len(bootstrap.read_text().splitlines())
        assert lines <= 200, f"Bootstrap is {lines} lines, must be ≤200"
