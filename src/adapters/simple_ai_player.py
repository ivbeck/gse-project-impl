from core.ports import PlayerInput
from core.types import Move


class SimpleAiPlayer(PlayerInput):
    def request_move(self, player_id: int, legal_moves: list[Move]) -> Move | None:
        if not legal_moves:
            return None
        sorted_moves = sorted(
            legal_moves,
            key=lambda m: (m.row, m.col, m.piece_id, m.orientation_index)
        )
        return sorted_moves[0]