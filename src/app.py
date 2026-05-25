"""Entry point for Blokus game engine."""

import argparse
from bootstrap import main as cli_main


def main():
    parser = argparse.ArgumentParser(description="Blokus Game")
    parser.add_argument("--gui", action="store_true", help="Start web GUI")
    parser.add_argument(
        "--duo", action="store_true", help="Play Blokus Duo (14x14, 2 players)"
    )
    args = parser.parse_args()

    mode = "duo" if args.duo else "classic"
    if args.gui:
        from web_main import run_web

        run_web(mode)
    else:
        cli_main(mode)


if __name__ == "__main__":
    main()
