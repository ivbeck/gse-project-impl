from core.ports import PresentationOutput
from core.types import GameStatus

COLORS = {0: "B", 1: "Y", 2: "R", 3: "G"}


class CLI(PresentationOutput):
    def render_board(self, board) -> None:
        print("  ", end="")
        for c in range(len(board[0])):
            print(f"{c:2}", end="")
        print()
        for r, row in enumerate(board):
            print(f"{r:2} ", end="")
            for cell in row:
                print(f" {COLORS.get(cell, '.')} ", end="")
            print()

    def render_status(self, status: GameStatus) -> None:
        print(f"Game status: {status}")

    def prompt_replay(self) -> bool:
        response = input("Play again? (y/n): ")
        return response.lower() == 'y'