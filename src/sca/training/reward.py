"""Reward function v1 for SCoRe RL training."""

from dataclasses import dataclass
from typing import Any


@dataclass
class RewardConfig:
    """Configuration for reward function."""

    # Primary rewards
    success_reward: float = 10.0
    failure_penalty: float = -1.0

    # Shaping rewards
    step_penalty: float = -0.01  # Per-step cost
    tool_success_bonus: float = 0.5
    tool_failure_penalty: float = -0.2

    # Recovery rewards (SCoRe-specific)
    recovery_bonus: float = 5.0  # Bonus for recovering from failure
    reflection_cost: float = -0.1  # Small cost for reflection


class RewardFunction:
    """Reward function for SCoRe training."""

    def __init__(self, config: RewardConfig | None = None) -> None:
        """Initialize reward function."""
        self.config = config or RewardConfig()

    def compute_step_reward(
        self,
        action: dict[str, Any],
        result: dict[str, Any],
        is_correction: bool = False,
    ) -> float:
        """Compute reward for a single step."""
        reward = self.config.step_penalty

        action_type = action.get("type", "")

        # Tool call rewards
        if action_type == "tool_call":
            if result.get("tool_success", False):
                reward += self.config.tool_success_bonus
            else:
                reward += self.config.tool_failure_penalty

        # Reflection cost
        if action_type == "reflect":
            reward += self.config.reflection_cost

        return reward

    def compute_episode_reward(
        self,
        success: bool,
        recovered: bool = False,
        steps: int = 0,
    ) -> float:
        """Compute final episode reward."""
        reward = 0.0

        # Task outcome
        if success:
            reward += self.config.success_reward
        else:
            reward += self.config.failure_penalty

        # Recovery bonus (key for SCoRe)
        if recovered:
            reward += self.config.recovery_bonus

        # Step penalty already applied per-step
        return reward

    def compute_trajectory_reward(
        self,
        trajectory: list[dict[str, Any]],
        success: bool,
        recovered: bool = False,
    ) -> list[float]:
        """Compute rewards for entire trajectory."""
        rewards = []
        for i, step in enumerate(trajectory):
            action = step.get("action", {})
            result = step.get("result", {})
            is_correction = step.get("is_correction", False)

            r = self.compute_step_reward(action, result, is_correction)

            # Add episode reward to last step
            if i == len(trajectory) - 1:
                r += self.compute_episode_reward(success, recovered, len(trajectory))

            rewards.append(r)

        return rewards
