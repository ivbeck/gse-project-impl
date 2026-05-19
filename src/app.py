"""Entry point for Blokus game engine."""
import argparse
from bootstrap import main as cli_main

def main():
    parser = argparse.ArgumentParser(description="Blokus Game")
    parser.add_argument("--gui", action="store_true", help="Start web GUI")
    args = parser.parse_args()

    if args.gui:
        from web_main import run_web
        run_web()
    else:
        cli_main()

if __name__ == "__main__":
    main()