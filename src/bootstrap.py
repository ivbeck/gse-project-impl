"""Procedural wiring for Blokus game engine (≤200 lines)."""

from core.types import ConfigVO, MoveResult, GameStatus
from core.piece_catalog import PieceCatalog
from core.rule_set import RuleSet
from core.scoring import build_scoring
from core.game_session import GameSession
from core.legal_move_enumerator import LegalMoveEnumerator
from core.ports import PlayerInput
from adapters.json_config_source import JsonConfigSource, DUO_CONFIG_JSON
from adapters.human_player import HumanPlayer
from adapters.simple_ai_player import SimpleAiPlayer
from adapters.cli import CLI


def create_game(config: ConfigVO) -> GameSession:
    catalog = PieceCatalog()
    ruleset = RuleSet(catalog, config)
    scoring = build_scoring(config, catalog)
    return GameSession(config, catalog, ruleset, scoring)


def create_player_inputs(
    session: GameSession, human_player_count: int
) -> dict[int, PlayerInput]:
    if not 1 <= human_player_count <= session.config.player_count:
        raise ValueError("human_player_count must match the configured player range")
    human_player = HumanPlayer()
    ai_player = SimpleAiPlayer(session.catalog, session.board)
    return {
        player_id: human_player if player_id < human_player_count else ai_player
        for player_id in range(session.config.player_count)
    }


def run_turn(
    session: GameSession,
    player_inputs: dict[int, PlayerInput],
    enumerator: LegalMoveEnumerator,
) -> bool:
    player_id = session.current_player_id
    player_input = player_inputs[player_id]
    legal_moves = enumerator.find_moves(
        session.board,
        player_id,
        session.remaining_pieces[player_id],
        session.is_first_move(player_id),
    )
    move = player_input.request_move(player_id, legal_moves)
    if move is None:
        session.submit_pass()
        if isinstance(player_input, SimpleAiPlayer):
            print(f"AI player {player_id} passes.")
    else:
        result = session.submit_move(move)
        if result == MoveResult.ILLEGAL:
            print("Illegal move, try again.")
            return False
        if isinstance(player_input, SimpleAiPlayer):
            print(
                f"AI player {player_id} places piece {move.piece_id} "
                f"at row {move.row}, col {move.col}, orientation {move.orientation_index}."
            )
    session.advance_turn()
    return True


def run_loop(session: GameSession, player_inputs: dict[int, PlayerInput], cli: CLI):
    enumerator = LegalMoveEnumerator(session.catalog, session.ruleset)
    while session.detect_termination() != GameStatus.FINISHED:
        cli.render_board(session.board.grid)
        run_turn(session, player_inputs, enumerator)
    cli.render_status(GameStatus.FINISHED)
    scores = session.final_scores()
    for s in scores:
        print(
            f"Player {s.player_id}: {s.score} points {'(WINNER)' if s.is_winner else ''}"
        )
    return cli.prompt_replay()


def main(mode: str = "classic"):
    config_json = DUO_CONFIG_JSON if mode == "duo" else "{}"
    config_source = JsonConfigSource(config_json)
    config = config_source.load_config()
    cli = CLI()
    human_player_count = cli.prompt_human_player_count(config.player_count)
    session = create_game(config)
    player_inputs = create_player_inputs(session, human_player_count)
    while run_loop(session, player_inputs, cli):
        session = create_game(config)
        player_inputs = create_player_inputs(session, human_player_count)
    print("Thanks for playing!")


if __name__ == "__main__":
    main()
