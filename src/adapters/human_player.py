from core.ports import PlayerInput
from core.types import Move


class HumanPlayer(PlayerInput):
    def request_move(self, player_id: int, legal_moves: list[Move]) -> Move | None:
        if not legal_moves:
            return None
        print(f"Player {player_id}, choose a move:")
        for i, m in enumerate(legal_moves[:10]):
            print(
                f"  {i}: piece={m.piece_id} orient={m.orientation_index} row={m.row} col={m.col}"
            )
        if len(legal_moves) > 10:
            print(f"  ... and {len(legal_moves) - 10} more moves")
        while True:
            choice = input("Enter move index (or -1 to pass): ")
            try:
                idx = int(choice)
            except ValueError:
                print("Please enter a number.")
                continue
            if idx < 0:
                return None
            if idx >= len(legal_moves):
                print("Move index out of range.")
                continue
            return legal_moves[idx]
