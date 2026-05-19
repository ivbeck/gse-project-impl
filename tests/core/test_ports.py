import pytest
from typing import Protocol, runtime_checkable
from core.ports import PlayerInput, StateRepository, ConfigSource, PresentationOutput


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