from core.types import ConfigVO, Move, MoveResult, GameStatus, PlayerScore
from core.board import Board
from core.piece_catalog import PieceCatalog
from core.rule_set import RuleSet
from core.scoring import Scoring


class GameSession:
    def __init__(
        self,
        config: ConfigVO,
        catalog: PieceCatalog,
        ruleset: RuleSet,
        scoring: Scoring
    ):
        self.config = config
        self.catalog = catalog
        self.ruleset = ruleset
        self.scoring = scoring
        self.board = Board(config)
        self.current_player_id = 0
        self.consecutive_passes = 0
        self.remaining_pieces: dict[int, list[int]] = {
            i: list(range(21)) for i in range(config.player_count)
        }
        self._is_first_move: dict[int, bool] = {i: True for i in range(config.player_count)}

    def submit_move(self, move: Move) -> MoveResult:
        orientation = self.catalog.get_orientations(move.piece_id)[move.orientation_index]
        result = self.ruleset.check_legality(
            self.board, move, self._is_first_move[move.player_id], orientation
        )
        if result == MoveResult.LEGAL:
            self.board.apply_move(move, orientation)
            self.remaining_pieces[move.player_id].remove(move.piece_id)
            self._is_first_move[move.player_id] = False
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
        return self.scoring.rank(self.remaining_pieces)