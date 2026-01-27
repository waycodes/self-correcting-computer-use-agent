"""Tests for core type definitions."""

from sca.types import (
    Action,
    ActionType,
    EventType,
    Observation,
    StepResult,
    TrajectoryEvent,
)


def test_action_click() -> None:
    """Test click action creation."""
    action = Action.click(100, 200)
    assert action.type == ActionType.CLICK
    assert action.params == {"x": 100, "y": 200, "button": "left"}


def test_action_type_text() -> None:
    """Test type action creation."""
    action = Action.type_text("hello")
    assert action.type == ActionType.TYPE
    assert action.params == {"text": "hello"}


def test_action_hotkey() -> None:
    """Test hotkey action creation."""
    action = Action.hotkey("ctrl", "c")
    assert action.type == ActionType.HOTKEY
    assert action.params == {"keys": ["ctrl", "c"]}


def test_observation_has_timestamp() -> None:
    """Test observation has auto-generated timestamp."""
    obs = Observation(screenshot=b"fake_png")
    assert obs.timestamp is not None
    assert "T" in obs.timestamp  # ISO format


def test_step_result_defaults() -> None:
    """Test step result default values."""
    obs = Observation(screenshot=b"fake_png")
    result = StepResult(observation=obs)
    assert result.reward == 0.0
    assert result.done is False
    assert result.truncated is False


def test_trajectory_event_to_dict() -> None:
    """Test trajectory event serialization."""
    event = TrajectoryEvent(
        event_type=EventType.ACTION,
        step=5,
        data={"action": "click"},
    )
    d = event.to_dict()
    assert d["event_type"] == "action"
    assert d["step"] == 5
    assert d["data"] == {"action": "click"}
