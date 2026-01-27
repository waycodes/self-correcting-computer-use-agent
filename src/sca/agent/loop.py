"""Agent loop state machine."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol

from sca.types import Action, EventType, Observation, TrajectoryEvent


class AgentState(Enum):
    """States in the agent loop."""

    IDLE = "idle"
    OBSERVING = "observing"
    DECIDING = "deciding"
    ACTING = "acting"
    REFLECTING = "reflecting"
    DONE = "done"
    ERROR = "error"


class PolicyProtocol(Protocol):
    """Protocol for agent policies."""

    def decide(
        self, observation: Observation, history: list[TrajectoryEvent]
    ) -> Action:
        """Decide next action given observation and history."""
        ...


@dataclass
class LoopConfig:
    """Configuration for agent loop."""

    max_steps: int = 100
    reflect_every: int = 0  # 0 = never auto-reflect
    log_screenshots: bool = True


@dataclass
class AgentLoop:
    """State machine for agent execution loop."""

    policy: PolicyProtocol
    config: LoopConfig = field(default_factory=LoopConfig)
    state: AgentState = AgentState.IDLE
    step_count: int = 0
    history: list[TrajectoryEvent] = field(default_factory=list)

    def reset(self) -> None:
        """Reset loop state."""
        self.state = AgentState.IDLE
        self.step_count = 0
        self.history = []

    def run(
        self, env: Any, task_config: dict[str, Any] | None = None
    ) -> list[TrajectoryEvent]:
        """Run the agent loop until done or max steps."""
        self.reset()

        # Initial observation
        self.state = AgentState.OBSERVING
        obs = env.reset(task_config)
        self._log_event(EventType.RESET, {"task_config": task_config or {}})

        done = False
        while not done and self.step_count < self.config.max_steps:
            # Decide
            self.state = AgentState.DECIDING
            action = self.policy.decide(obs, self.history)
            self._log_event(
                EventType.ACTION,
                {"type": action.type.value, "params": action.params},
            )

            # Act
            self.state = AgentState.ACTING
            result = env.step(action)
            self.step_count += 1

            # Log observation
            self._log_event(EventType.OBSERVATION, {"step": self.step_count})

            # Check for reflection
            if self._should_reflect():
                self.state = AgentState.REFLECTING
                # Reflection would be handled by policy in future

            # Update state
            obs = result.observation
            done = result.done

            if result.reward != 0:
                self._log_event(EventType.REWARD, {"reward": result.reward})

        # Final state
        self.state = AgentState.DONE if done else AgentState.ERROR
        self._log_event(
            EventType.DONE,
            {"steps": self.step_count, "completed": done},
        )

        return self.history

    def _should_reflect(self) -> bool:
        """Check if agent should reflect."""
        if self.config.reflect_every <= 0:
            return False
        return self.step_count % self.config.reflect_every == 0

    def _log_event(self, event_type: EventType, data: dict[str, Any]) -> None:
        """Log a trajectory event."""
        event = TrajectoryEvent(
            event_type=event_type,
            step=self.step_count,
            data=data,
        )
        self.history.append(event)
