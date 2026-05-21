from dataclasses import dataclass
from core.types import ConfigVO
from core.game_session import GameSession


@dataclass(frozen=True)
class Memento:
    config: ConfigVO
    board_state: tuple[tuple[int | None, ...], ...]
    current_player_id: int
    remaining_pieces: tuple[tuple[int, tuple[int, ...]], ...]
    consecutive_passes: int
    is_first_move: tuple[tuple[int, bool], ...]
    last_placed_piece: tuple[tuple[int, int | None], ...] = ()

    @classmethod
    def from_session(cls, session: GameSession) -> "Memento":
        board_state = tuple(
            tuple(cell for cell in row)
            for row in session.board.grid
        )
        remaining_pieces = tuple(
            (player_id, tuple(pieces))
            for player_id, pieces in sorted(session.remaining_pieces.items())
        )
        is_first_move = tuple(
            (player_id, flag)
            for player_id, flag in sorted(session._is_first_move.items())
        )
        last_placed_piece = tuple(
            (player_id, piece_id)
            for player_id, piece_id in sorted(session.last_placed_piece.items())
        )
        return cls(
            config=session.config,
            board_state=board_state,
            current_player_id=session.current_player_id,
            remaining_pieces=remaining_pieces,
            consecutive_passes=session.consecutive_passes,
            is_first_move=is_first_move,
            last_placed_piece=last_placed_piece,
        )
