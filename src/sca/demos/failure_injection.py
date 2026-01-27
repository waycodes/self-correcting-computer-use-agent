"""Failure injection for demo purposes."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class InjectionType(Enum):
    """Types of failures to inject."""

    CLICK_MISS = "click_miss"  # Click wrong location
    TOOL_ERROR = "tool_error"  # Tool returns error
    TIMEOUT = "timeout"  # Action times out
    WRONG_WINDOW = "wrong_window"  # Focus wrong window


@dataclass
class InjectionConfig:
    """Configuration for failure injection."""

    injection_type: InjectionType
    trigger_step: int = 3  # Inject at this step
    recovery_enabled: bool = True


class FailureInjector:
    """Inject failures mid-task for demo purposes."""

    def __init__(self, config: InjectionConfig) -> None:
        """Initialize injector."""
        self.config = config
        self.injected = False
        self.step_count = 0

    def should_inject(self) -> bool:
        """Check if failure should be injected this step."""
        return self.step_count == self.config.trigger_step and not self.injected

    def inject(self, action: dict[str, Any]) -> dict[str, Any]:
        """Inject failure into action result."""
        self.injected = True

        if self.config.injection_type == InjectionType.CLICK_MISS:
            return {"success": False, "error": "click_missed_target"}
        elif self.config.injection_type == InjectionType.TOOL_ERROR:
            return {"success": False, "error": "tool_execution_failed"}
        elif self.config.injection_type == InjectionType.TIMEOUT:
            return {"success": False, "error": "action_timeout"}
        elif self.config.injection_type == InjectionType.WRONG_WINDOW:
            return {"success": False, "error": "wrong_window_focused"}

        return {"success": False, "error": "unknown_injection"}

    def process_step(
        self, action: dict[str, Any], result: dict[str, Any]
    ) -> dict[str, Any]:
        """Process step, potentially injecting failure."""
        self.step_count += 1

        if self.should_inject():
            return self.inject(action)

        return result

    def reset(self) -> None:
        """Reset injector state."""
        self.injected = False
        self.step_count = 0
