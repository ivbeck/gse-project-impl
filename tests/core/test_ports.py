from core.ports import (
    ConfigSource,
    GameSession,
    LegalMoveEnumerator,
    MoveValidator,
    PlayerInput,
    PresentationOutput,
    StateRepository,
)


def test_game_session_is_protocol():
    assert hasattr(GameSession, 'submit_move')
    assert hasattr(GameSession, 'submit_pass')
    assert hasattr(GameSession, 'advance_turn')
    assert hasattr(GameSession, 'detect_termination')
    assert hasattr(GameSession, 'final_scores')


def test_move_validator_is_protocol():
    assert hasattr(MoveValidator, 'check_legality')


def test_legal_move_enumerator_is_protocol():
    assert hasattr(LegalMoveEnumerator, 'find_moves')


def test_player_input_is_protocol():
    assert hasattr(PlayerInput, 'request_move')


def test_state_repository_is_protocol():
    assert hasattr(StateRepository, 'save')
    assert hasattr(StateRepository, 'restore')


def test_config_source_is_protocol():
    assert hasattr(ConfigSource, 'load_config')


def test_presentation_output_is_protocol():
    assert hasattr(PresentationOutput, 'render_board')
    assert hasattr(PresentationOutput, 'render_status')
    assert hasattr(PresentationOutput, 'prompt_replay')
