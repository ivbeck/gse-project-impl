from dataclasses import dataclass
from core.types import ConfigVO
from core.game_session import GameSession


@dataclass(frozen=True)
class Memento:
    config: ConfigVO
    board_state: tuple[tuple[int | None, ...], ...]
    current_player_id: int
    remaining_pieces: dict[int, list[int]]
    consecutive_passes: int
    is_first_move: dict[int, bool]

    @classmethod
    def from_session(cls, session: GameSession) -> "Memento":
        board_state = tuple(
            tuple(cell for cell in row)
            for row in session.board.grid
        )
        return cls(
            config=session.config,
            board_state=board_state,
            current_player_id=session.current_player_id,
            remaining_pieces=session.remaining_pieces.copy(),
            consecutive_passes=session.consecutive_passes,
            is_first_move=session._is_first_move.copy(),
        )