"""Procedural wiring for Blokus game engine (≤200 lines)."""
from core.types import ConfigVO, MoveResult, GameStatus
from core.piece_catalog import PieceCatalog
from core.rule_set import RuleSet
from core.scoring import build_scoring
from core.game_session import GameSession
from core.legal_move_enumerator import LegalMoveEnumerator
from adapters.json_config_source import JsonConfigSource, DUO_CONFIG_JSON
from adapters.human_player import HumanPlayer
from adapters.cli import CLI


def create_game(config: ConfigVO) -> GameSession:
    catalog = PieceCatalog()
    ruleset = RuleSet(catalog, config)
    scoring = build_scoring(config, catalog)
    return GameSession(config, catalog, ruleset, scoring)


def run_loop(session: GameSession, player_input, cli: CLI):
    enumerator = LegalMoveEnumerator(session.catalog, session.ruleset)
    while session.detect_termination() != GameStatus.FINISHED:
        cli.render_board(session.board.grid)
        legal_moves = enumerator.find_moves(
            session.board,
            session.current_player_id,
            session.remaining_pieces[session.current_player_id],
            session.is_first_move(session.current_player_id),
        )
        move = player_input.request_move(session.current_player_id, legal_moves)
        if move is None:
            session.submit_pass()
        else:
            result = session.submit_move(move)
            if result == MoveResult.ILLEGAL:
                print("Illegal move, try again.")
                continue
        session.advance_turn()
    cli.render_status(GameStatus.FINISHED)
    scores = session.final_scores()
    for s in scores:
        print(f"Player {s.player_id}: {s.score} points {'(WINNER)' if s.is_winner else ''}")
    return cli.prompt_replay()


def main(mode: str = "classic"):
    config_json = DUO_CONFIG_JSON if mode == "duo" else "{}"
    config_source = JsonConfigSource(config_json)
    config = config_source.load_config()
    session = create_game(config)
    player = HumanPlayer()
    cli = CLI()
    while run_loop(session, player, cli):
        session = create_game(config)
    print("Thanks for playing!")


if __name__ == "__main__":
    main()
