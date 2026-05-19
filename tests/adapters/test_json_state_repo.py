import pytest
import json
from adapters.json_state_repo import JsonStateRepo
from core.types import ConfigVO, Position
from core.game_session import GameSession
from core.piece_catalog import PieceCatalog
from core.rule_set import RuleSet
from core.scoring import Scoring
from core.memento import Memento


@pytest.fixture
def config():
    return ConfigVO(
        board_width=20,
        board_height=20,
        player_count=4,
        starting_positions={
            0: Position(0, 0),
            1: Position(0, 19),
            2: Position(19, 19),
            3: Position(19, 0),
        }
    )


@pytest.fixture
def session(config):
    catalog = PieceCatalog()
    ruleset = RuleSet(catalog, config)
    scoring = Scoring(catalog)
    return GameSession(config, catalog, ruleset, scoring)


@pytest.fixture
def memento(session):
    return Memento.from_session(session)


@pytest.fixture
def repo():
    return JsonStateRepo()


def test_json_state_repo_save(repo, memento):
    data = repo.save(memento)
    assert isinstance(data, str)
    parsed = json.loads(data)
    assert "config" in parsed
    assert "board_state" in parsed
    assert "remaining_pieces" in parsed


def test_json_state_repo_restore(repo, memento):
    data = repo.save(memento)
    restored = repo.restore(data)
    assert restored is not None
    assert isinstance(restored, Memento)
    assert restored.config == memento.config
    assert restored.board_state == memento.board_state
    assert restored.current_player_id == memento.current_player_id
    assert restored.remaining_pieces == memento.remaining_pieces
    assert restored.consecutive_passes == memento.consecutive_passes
    assert restored.is_first_move == memento.is_first_move


def test_json_state_repo_roundtrip_player_pieces(session, repo):
    memento = Memento.from_session(session)
    data = repo.save(memento)
    restored = repo.restore(data)
    assert dict(restored.remaining_pieces) == dict(memento.remaining_pieces)
    assert restored.is_first_move == memento.is_first_move