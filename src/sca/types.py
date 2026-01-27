"""Core type definitions for the agent system."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ActionType(Enum):
    """Types of actions the agent can take."""

    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    HOTKEY = "hotkey"
    DRAG = "drag"
    TOOL_CALL = "tool_call"
    REFLECT = "reflect"
    DONE = "done"


@dataclass
class Action:
    """An action to execute in the environment."""

    type: ActionType
    params: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def click(cls, x: int, y: int, button: str = "left") -> "Action":
        """Create a click action."""
        return cls(ActionType.CLICK, {"x": x, "y": y, "button": button})

    @classmethod
    def type_text(cls, text: str) -> "Action":
        """Create a type action."""
        return cls(ActionType.TYPE, {"text": text})

    @classmethod
    def scroll(cls, x: int, y: int, dx: int = 0, dy: int = 0) -> "Action":
        """Create a scroll action."""
        return cls(ActionType.SCROLL, {"x": x, "y": y, "dx": dx, "dy": dy})

    @classmethod
    def hotkey(cls, *keys: str) -> "Action":
        """Create a hotkey action."""
        return cls(ActionType.HOTKEY, {"keys": list(keys)})

    @classmethod
    def done(cls) -> "Action":
        """Create a done action to signal task completion."""
        return cls(ActionType.DONE)


@dataclass
class Observation:
    """Observation from the environment at a single timestep."""

    screenshot: bytes  # PNG image data
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    a11y_tree: dict[str, Any] | None = None  # Accessibility tree
    tool_state: dict[str, Any] | None = None  # MCP tool state
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StepResult:
    """Result of executing a single step."""

    observation: Observation
    reward: float = 0.0
    done: bool = False
    truncated: bool = False
    info: dict[str, Any] = field(default_factory=dict)


class EventType(Enum):
    """Types of trajectory events."""

    RESET = "reset"
    ACTION = "action"
    OBSERVATION = "observation"
    REWARD = "reward"
    DONE = "done"
    ERROR = "error"


@dataclass
class TrajectoryEvent:
    """A single event in a trajectory log."""

    event_type: EventType
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    step: int = 0
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "step": self.step,
            "data": self.data,
        }
