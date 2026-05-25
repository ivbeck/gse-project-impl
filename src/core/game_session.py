from typing import TYPE_CHECKING
from core.types import ConfigVO, Move, MoveResult, GameStatus, PlayerScore
from core.board import Board
from core.piece_catalog import PieceCatalog
from core.rule_set import RuleSet
from core.scoring import build_scoring

if TYPE_CHECKING:
    from core.memento import Memento


class GameSession:
    def __init__(
        self, config: ConfigVO, catalog: PieceCatalog, ruleset: RuleSet, scoring
    ):
        self.config = config
        self.catalog = catalog
        self.ruleset = ruleset
        self.scoring = scoring
        self.board = Board(config)
        self.current_player_id = 0
        self.consecutive_passes = 0
        piece_ids = [piece.piece_id for piece in catalog.get_all_pieces()]
        self.remaining_pieces: dict[int, list[int]] = {
            i: list(piece_ids) for i in range(config.player_count)
        }
        self._is_first_move: dict[int, bool] = {
            i: True for i in range(config.player_count)
        }
        self.last_placed_piece: dict[int, int | None] = {
            i: None for i in range(config.player_count)
        }

    @classmethod
    def from_memento(cls, memento: "Memento", catalog: PieceCatalog) -> "GameSession":
        ruleset = RuleSet(catalog, memento.config)
        scoring = build_scoring(memento.config, catalog)
        session = cls(memento.config, catalog, ruleset, scoring)
        if len(memento.board_state) != memento.config.board_height:
            raise ValueError("memento board height does not match config")
        if any(len(row) != memento.config.board_width for row in memento.board_state):
            raise ValueError("memento board width does not match config")
        session.board.grid = [list(row) for row in memento.board_state]
        session.current_player_id = memento.current_player_id
        session.remaining_pieces = {
            player_id: list(pieces) for player_id, pieces in memento.remaining_pieces
        }
        session.consecutive_passes = memento.consecutive_passes
        session._is_first_move = {
            player_id: flag for player_id, flag in memento.is_first_move
        }
        session.last_placed_piece = {
            i: None for i in range(memento.config.player_count)
        }
        session.last_placed_piece.update(
            {player_id: piece_id for player_id, piece_id in memento.last_placed_piece}
        )
        return session

    def is_first_move(self, player_id: int) -> bool:
        return self._is_first_move.get(player_id, False)

    def submit_move(self, move: Move) -> MoveResult:
        if self.detect_termination() == GameStatus.FINISHED:
            return MoveResult.ILLEGAL
        if move.player_id != self.current_player_id:
            return MoveResult.ILLEGAL
        if move.piece_id not in self.remaining_pieces.get(move.player_id, []):
            return MoveResult.ILLEGAL
        orientations = self.catalog.get_orientations(move.piece_id)
        if not 0 <= move.orientation_index < len(orientations):
            return MoveResult.ILLEGAL
        orientation = orientations[move.orientation_index]
        result = self.ruleset.check_legality(
            self.board, move, self._is_first_move[move.player_id], orientation
        )
        if result == MoveResult.LEGAL:
            self.board.apply_move(move, orientation)
            self.remaining_pieces[move.player_id].remove(move.piece_id)
            self._is_first_move[move.player_id] = False
            self.last_placed_piece[move.player_id] = move.piece_id
            self.consecutive_passes = 0
        return result

    def submit_pass(self) -> None:
        self.consecutive_passes += 1

    def advance_turn(self) -> None:
        self.current_player_id = (self.current_player_id + 1) % self.config.player_count

    def detect_termination(self) -> GameStatus:
        if all(not pieces for pieces in self.remaining_pieces.values()):
            return GameStatus.FINISHED
        if self.consecutive_passes >= self.config.player_count:
            return GameStatus.FINISHED
        return GameStatus.IN_PROGRESS

    def final_scores(self) -> list[PlayerScore]:
        return self.scoring.rank(self.remaining_pieces, self.last_placed_piece)
