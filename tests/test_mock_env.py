"""Tests for mock desktop environment."""

from sca.envs.osworld.mock import MockDesktopEnv
from sca.types import Action


def test_mock_env_reset() -> None:
    """Test mock environment reset."""
    env = MockDesktopEnv()
    obs = env.reset()

    assert obs.screenshot is not None
    assert len(obs.screenshot) > 0
    assert obs.a11y_tree is not None


def test_mock_env_step() -> None:
    """Test mock environment step."""
    env = MockDesktopEnv()
    env.reset()

    action = Action.click(100, 100)
    result = env.step(action)

    assert result.observation is not None
    assert result.done is False
    assert env.step_count == 1


def test_mock_env_done_action() -> None:
    """Test mock environment done action."""
    env = MockDesktopEnv()
    env.reset()

    action = Action.done()
    result = env.step(action)

    assert result.done is True
    assert result.reward == 1.0


def test_mock_env_max_steps() -> None:
    """Test mock environment max steps."""
    env = MockDesktopEnv(max_steps=3)
    env.reset()

    for _ in range(3):
        result = env.step(Action.click(0, 0))

    assert result.done is True
    assert env.step_count == 3


def test_mock_env_tracks_actions() -> None:
    """Test mock environment tracks actions."""
    env = MockDesktopEnv()
    env.reset()

    env.step(Action.click(10, 20))
    env.step(Action.type_text("hello"))

    assert len(env.actions) == 2
