"""Policy interface and adapters."""

from abc import ABC, abstractmethod
from typing import Any

from sca.types import Action, Observation, TrajectoryEvent


class Policy(ABC):
    """Abstract base class for agent policies."""

    @abstractmethod
    def decide(
        self, observation: Observation, history: list[TrajectoryEvent]
    ) -> Action:
        """Decide next action given observation and history."""

    def reset(self) -> None:  # noqa: B027
        """Reset policy state (optional, override if needed)."""


class RandomPolicy(Policy):
    """Random policy for testing."""

    def __init__(self, seed: int = 42) -> None:
        import random

        self.rng = random.Random(seed)
        self.action_count = 0

    def decide(
        self, observation: Observation, history: list[TrajectoryEvent]
    ) -> Action:
        """Return random action."""
        self.action_count += 1
        if self.action_count > 5:
            return Action.done()

        x = self.rng.randint(0, 1920)
        y = self.rng.randint(0, 1080)
        return Action.click(x, y)


class APIPolicy(Policy):
    """Policy that calls a remote API (stub for future implementation)."""

    def __init__(self, endpoint: str, api_key: str | None = None) -> None:
        self.endpoint = endpoint
        self.api_key = api_key

    def decide(
        self, observation: Observation, history: list[TrajectoryEvent]
    ) -> Action:
        """Call API to get action (stub)."""
        # In real implementation, would:
        # 1. Encode observation (screenshot, a11y tree)
        # 2. Send to API endpoint
        # 3. Parse response into Action
        raise NotImplementedError("API policy not yet implemented")


class LocalModelPolicy(Policy):
    """Policy using a local HuggingFace model (stub for future implementation)."""

    def __init__(self, model_name: str, device: str = "cuda") -> None:
        self.model_name = model_name
        self.device = device
        self.model: Any = None

    def load(self) -> None:
        """Load model (stub)."""
        # Would load HF model here
        pass

    def decide(
        self, observation: Observation, history: list[TrajectoryEvent]
    ) -> Action:
        """Run local model to get action (stub)."""
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() first.")
        raise NotImplementedError("Local model policy not yet implemented")
