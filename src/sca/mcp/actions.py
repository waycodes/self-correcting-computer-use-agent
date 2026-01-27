"""MCP tool-call Action schema and AgentLoop integration."""

from dataclasses import dataclass, field
from typing import Any

from sca.types import Action, ActionType


@dataclass
class ToolCallAction:
    """Action to call an MCP tool."""

    tool_name: str
    arguments: dict[str, Any] = field(default_factory=dict)

    def to_action(self) -> Action:
        """Convert to generic Action."""
        return Action(
            type=ActionType.TOOL_CALL,
            params={"tool_name": self.tool_name, "arguments": self.arguments},
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": "tool_call",
            "tool_name": self.tool_name,
            "arguments": self.arguments,
        }

    @classmethod
    def from_action(cls, action: Action) -> "ToolCallAction":
        """Create from generic Action."""
        if action.type != ActionType.TOOL_CALL:
            raise ValueError(f"Expected TOOL_CALL action, got {action.type}")
        return cls(
            tool_name=action.params["tool_name"],
            arguments=action.params.get("arguments", {}),
        )


@dataclass
class ToolCallResult:
    """Result of an MCP tool call."""

    tool_name: str
    success: bool
    result: Any = None
    error: str | None = None
    latency_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tool_name": self.tool_name,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "latency_ms": self.latency_ms,
        }


def is_tool_call(action: Action) -> bool:
    """Check if an action is a tool call."""
    return action.type == ActionType.TOOL_CALL


def parse_tool_call(data: dict[str, Any]) -> ToolCallAction:
    """Parse a tool call from dictionary."""
    return ToolCallAction(
        tool_name=data["tool_name"],
        arguments=data.get("arguments", {}),
    )
