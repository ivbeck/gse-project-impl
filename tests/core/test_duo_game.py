from adapters.json_config_source import JsonConfigSource, DUO_CONFIG_JSON
from adapters.simple_ai_player import SimpleAiPlayer
from bootstrap import create_game
from core.board import Board
from core.legal_move_enumerator import LegalMoveEnumerator
from core.piece_catalog import PieceCatalog
from core.rule_set import RuleSet
from core.types import GameStatus, Move


def _duo_config():
    return JsonConfigSource(DUO_CONFIG_JSON).load_config()


def test_duo_first_move_monomino_must_cover_interior_start():
    config = _duo_config()
    catalog = PieceCatalog()
    enumerator = LegalMoveEnumerator(catalog, RuleSet(catalog, config))
    board = Board(config)
    moves = enumerator.find_moves(board, 0, [0], is_first_move=True)
    # The monomino has one cell and one orientation; the only legal first move
    # is the one that lands it on player 0's interior starting cell (4, 4).
    assert moves == [Move(player_id=0, piece_id=0, orientation_index=0, row=4, col=4)]


def test_duo_ai_vs_ai_game_finishes_with_consistent_ranking():
    session = create_game(_duo_config())
    enumerator = LegalMoveEnumerator(session.catalog, session.ruleset)
    ai = SimpleAiPlayer(session.catalog, session.board)

    safety = 0
    while session.detect_termination() != GameStatus.FINISHED and safety < 2000:
        safety += 1
        pid = session.current_player_id
        legal = enumerator.find_moves(
            session.board, pid,
            session.remaining_pieces[pid],
            session.is_first_move(pid),
        )
        move = ai.request_move(pid, legal)
        if move is None:
            session.submit_pass()
        else:
            session.submit_move(move)
        session.advance_turn()

    assert session.detect_termination() == GameStatus.FINISHED
    scores = session.final_scores()
    assert len(scores) == 2
    # Basic scheme: lowest remaining-squares first; winner is the minimum.
    assert scores == sorted(scores, key=lambda s: s.score)
    best = scores[0].score
    assert all(s.is_winner == (s.score == best) for s in scores)
