"""Mock desktop environment for testing."""

from typing import Any

from sca.envs.osworld.adapter import EnvAdapter
from sca.types import Action, ActionType, Observation, StepResult


class MockDesktopEnv(EnvAdapter):
    """Deterministic mock environment for CI testing."""

    def __init__(self, max_steps: int = 10) -> None:
        """Initialize mock environment."""
        self.max_steps = max_steps
        self.step_count = 0
        self.actions: list[Action] = []
        self._closed = False

    def reset(self, task_config: dict[str, Any] | None = None) -> Observation:
        """Reset mock environment."""
        self.step_count = 0
        self.actions = []
        return self._make_observation()

    def step(self, action: Action) -> StepResult:
        """Execute action in mock environment."""
        self.actions.append(action)
        self.step_count += 1

        done = action.type == ActionType.DONE or self.step_count >= self.max_steps
        reward = 1.0 if action.type == ActionType.DONE else 0.0

        return StepResult(
            observation=self._make_observation(),
            reward=reward,
            done=done,
            info={"step": self.step_count},
        )

    def close(self) -> None:
        """Close mock environment."""
        self._closed = True

    def _make_observation(self) -> Observation:
        """Create a deterministic mock observation."""
        # 1x1 red PNG (minimal valid PNG)
        png_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
            b"\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00"
            b"\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        return Observation(
            screenshot=png_data,
            a11y_tree={"root": {"name": "mock", "children": []}},
            metadata={"step": self.step_count, "mock": True},
        )
