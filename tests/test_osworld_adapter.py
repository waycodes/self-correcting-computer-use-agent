"""Tests for OSWorld environment adapter."""

from typing import Any

from sca.envs.osworld.adapter import OSWorldEnvAdapter
from sca.types import Action


class MockDesktopEnv:
    """Mock OSWorld DesktopEnv for testing."""

    def __init__(self) -> None:
        self.reset_called = False
        self.step_called = False
        self.close_called = False
        self.last_action: str | None = None

    def reset(self, task_config: dict[str, Any] | None = None) -> dict[str, Any]:
        self.reset_called = True
        return {"screenshot": b"fake_png_data", "accessibility_tree": {"root": {}}}

    def step(self, action: str) -> tuple[dict[str, Any], float, bool, dict[str, Any]]:
        self.step_called = True
        self.last_action = action
        return {"screenshot": b"new_png"}, 0.0, False, {}

    def close(self) -> None:
        self.close_called = True


def test_adapter_reset() -> None:
    """Test adapter reset returns Observation."""
    mock_env = MockDesktopEnv()
    adapter = OSWorldEnvAdapter(mock_env)

    obs = adapter.reset()

    assert mock_env.reset_called
    assert obs.screenshot == b"fake_png_data"
    assert obs.a11y_tree == {"root": {}}


def test_adapter_step_click() -> None:
    """Test adapter converts click action."""
    mock_env = MockDesktopEnv()
    adapter = OSWorldEnvAdapter(mock_env)
    adapter.reset()

    action = Action.click(100, 200)
    result = adapter.step(action)

    assert mock_env.step_called
    assert "click(100, 200" in mock_env.last_action
    assert result.observation.screenshot == b"new_png"


def test_adapter_step_type() -> None:
    """Test adapter converts type action."""
    mock_env = MockDesktopEnv()
    adapter = OSWorldEnvAdapter(mock_env)
    adapter.reset()

    action = Action.type_text("hello world")
    adapter.step(action)

    assert "type('hello world')" in mock_env.last_action


def test_adapter_step_hotkey() -> None:
    """Test adapter converts hotkey action."""
    mock_env = MockDesktopEnv()
    adapter = OSWorldEnvAdapter(mock_env)
    adapter.reset()

    action = Action.hotkey("ctrl", "c")
    adapter.step(action)

    assert "hotkey('ctrl', 'c')" in mock_env.last_action


def test_adapter_close() -> None:
    """Test adapter close calls underlying env."""
    mock_env = MockDesktopEnv()
    adapter = OSWorldEnvAdapter(mock_env)

    adapter.close()

    assert mock_env.close_called
