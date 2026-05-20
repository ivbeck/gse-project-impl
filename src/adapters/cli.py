from core.ports import PresentationOutput
from core.types import GameStatus

COLORS = {0: "B", 1: "Y", 2: "R", 3: "G"}


class CLI(PresentationOutput):
    def render_board(self, board) -> None:
        column_count = len(board[0]) if board else 0
        row_label_width = max(2, len(str(max(len(board) - 1, 0))))
        cell_width = max(3, len(str(max(column_count - 1, 0))))

        header = " " * (row_label_width + 1)
        header += "".join(f"{c:^{cell_width}}" for c in range(column_count))
        print(header)
        for r, row in enumerate(board):
            cells = "".join(f"{COLORS.get(cell, '.'):^{cell_width}}" for cell in row)
            print(f"{r:>{row_label_width}} {cells}")

    def render_status(self, status: GameStatus) -> None:
        print(f"Game status: {status}")

    def prompt_replay(self) -> bool:
        response = input("Play again? (y/n): ")
        return response.lower() == 'y'
