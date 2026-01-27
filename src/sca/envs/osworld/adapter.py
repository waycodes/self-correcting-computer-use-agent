"""OSWorld environment adapter."""

from abc import ABC, abstractmethod
from typing import Any, Protocol

from sca.types import Action, ActionType, Observation, StepResult


class DesktopEnvProtocol(Protocol):
    """Protocol for OSWorld DesktopEnv interface."""

    def reset(self, task_config: dict[str, Any] | None = None) -> dict[str, Any]: ...

    def step(
        self, action: str
    ) -> tuple[dict[str, Any], float, bool, dict[str, Any]]: ...

    def close(self) -> None: ...


class EnvAdapter(ABC):
    """Abstract base for environment adapters."""

    @abstractmethod
    def reset(self, task_config: dict[str, Any] | None = None) -> Observation:
        """Reset environment and return initial observation."""

    @abstractmethod
    def step(self, action: Action) -> StepResult:
        """Execute action and return result."""

    @abstractmethod
    def close(self) -> None:
        """Clean up environment resources."""


class OSWorldEnvAdapter(EnvAdapter):
    """Adapter wrapping OSWorld DesktopEnv."""

    def __init__(self, env: DesktopEnvProtocol) -> None:
        """Initialize adapter with OSWorld environment."""
        self._env = env

    def reset(self, task_config: dict[str, Any] | None = None) -> Observation:
        """Reset environment and return initial observation."""
        raw_obs = self._env.reset(task_config)
        return self._convert_observation(raw_obs)

    def step(self, action: Action) -> StepResult:
        """Execute action and return result."""
        osworld_action = self._convert_action(action)
        raw_obs, reward, done, info = self._env.step(osworld_action)
        obs = self._convert_observation(raw_obs)
        return StepResult(observation=obs, reward=reward, done=done, info=info)

    def close(self) -> None:
        """Clean up environment resources."""
        self._env.close()

    def _convert_observation(self, raw: dict[str, Any]) -> Observation:
        """Convert OSWorld observation to our Observation type."""
        screenshot = raw.get("screenshot", b"")
        if isinstance(screenshot, str):
            # Handle base64 encoded screenshots
            import base64

            screenshot = base64.b64decode(screenshot)

        return Observation(
            screenshot=screenshot,
            a11y_tree=raw.get("accessibility_tree"),
            metadata={"raw_keys": list(raw.keys())},
        )

    def _convert_action(self, action: Action) -> str:
        """Convert our Action to OSWorld action string format."""
        if action.type == ActionType.CLICK:
            x, y = action.params["x"], action.params["y"]
            btn = action.params.get("button", "left")
            return f"click({x}, {y}, button='{btn}')"

        if action.type == ActionType.TYPE:
            text = action.params["text"]
            return f"type('{text}')"

        if action.type == ActionType.SCROLL:
            x, y = action.params["x"], action.params["y"]
            dy = action.params.get("dy", 0)
            return f"scroll({x}, {y}, clicks={dy})"

        if action.type == ActionType.HOTKEY:
            keys = action.params["keys"]
            keys_str = ", ".join(f"'{k}'" for k in keys)
            return f"hotkey({keys_str})"

        if action.type == ActionType.DONE:
            return "done()"

        return "noop()"
