"""GUI action schema definitions."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MouseButton(Enum):
    """Mouse button types."""

    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


class ScrollDirection(Enum):
    """Scroll direction."""

    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


@dataclass
class ClickAction:
    """Click at screen coordinates."""

    x: int
    y: int
    button: MouseButton = MouseButton.LEFT
    clicks: int = 1  # 1=single, 2=double

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "click",
            "x": self.x,
            "y": self.y,
            "button": self.button.value,
            "clicks": self.clicks,
        }


@dataclass
class TypeAction:
    """Type text at current cursor position."""

    text: str
    interval: float = 0.0  # Delay between keystrokes

    def to_dict(self) -> dict[str, Any]:
        return {"type": "type", "text": self.text, "interval": self.interval}


@dataclass
class ScrollAction:
    """Scroll at screen coordinates."""

    x: int
    y: int
    direction: ScrollDirection = ScrollDirection.DOWN
    amount: int = 3  # Number of scroll units

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "scroll",
            "x": self.x,
            "y": self.y,
            "direction": self.direction.value,
            "amount": self.amount,
        }


@dataclass
class HotkeyAction:
    """Press a keyboard shortcut."""

    keys: list[str] = field(default_factory=list)  # e.g., ["ctrl", "c"]

    def to_dict(self) -> dict[str, Any]:
        return {"type": "hotkey", "keys": self.keys}


@dataclass
class DragAction:
    """Drag from one point to another."""

    start_x: int
    start_y: int
    end_x: int
    end_y: int
    button: MouseButton = MouseButton.LEFT

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "drag",
            "start_x": self.start_x,
            "start_y": self.start_y,
            "end_x": self.end_x,
            "end_y": self.end_y,
            "button": self.button.value,
        }


# Type alias for any GUI action
GUIAction = ClickAction | TypeAction | ScrollAction | HotkeyAction | DragAction


def parse_gui_action(data: dict[str, Any]) -> GUIAction:
    """Parse a GUI action from dictionary."""
    action_type = data.get("type")

    if action_type == "click":
        return ClickAction(
            x=data["x"],
            y=data["y"],
            button=MouseButton(data.get("button", "left")),
            clicks=data.get("clicks", 1),
        )
    elif action_type == "type":
        return TypeAction(text=data["text"], interval=data.get("interval", 0.0))
    elif action_type == "scroll":
        return ScrollAction(
            x=data["x"],
            y=data["y"],
            direction=ScrollDirection(data.get("direction", "down")),
            amount=data.get("amount", 3),
        )
    elif action_type == "hotkey":
        return HotkeyAction(keys=data.get("keys", []))
    elif action_type == "drag":
        return DragAction(
            start_x=data["start_x"],
            start_y=data["start_y"],
            end_x=data["end_x"],
            end_y=data["end_y"],
            button=MouseButton(data.get("button", "left")),
        )
    else:
        raise ValueError(f"Unknown action type: {action_type}")
