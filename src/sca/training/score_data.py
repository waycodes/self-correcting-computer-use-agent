"""SCoRe-style data generator: attempt → failure → reflect → correction."""

from dataclasses import dataclass, field
from typing import Any

from sca.failures.taxonomy import FailureEvent
from sca.types import Action, TrajectoryEvent


@dataclass
class CorrectionAttempt:
    """A correction attempt after failure detection."""

    failure: FailureEvent
    reflection: dict[str, Any]  # Reflection action data
    correction_actions: list[Action]
    success: bool = False


@dataclass
class MultiTurnTrajectory:
    """Multi-turn trajectory with correction attempts."""

    task_id: str
    initial_attempt: list[TrajectoryEvent]
    corrections: list[CorrectionAttempt] = field(default_factory=list)
    final_success: bool = False

    @property
    def num_corrections(self) -> int:
        return len(self.corrections)

    @property
    def recovered(self) -> bool:
        return self.final_success and self.num_corrections > 0


class SCoReDataGenerator:
    """Generate multi-turn correction data for SCoRe training."""

    def __init__(self, max_corrections: int = 3) -> None:
        """Initialize generator."""
        self.max_corrections = max_corrections

    def generate_correction_trace(
        self,
        initial_trajectory: list[TrajectoryEvent],
        failure: FailureEvent,
        policy: Any,  # Policy to generate corrections
        env: Any,  # Environment adapter
    ) -> CorrectionAttempt:
        """Generate a correction attempt after failure.

        This is the core SCoRe loop:
        1. Detect failure
        2. Generate reflection
        3. Execute correction actions
        4. Check if recovered
        """
        # Generate reflection based on failure
        reflection = self._generate_reflection(failure, initial_trajectory)

        # Generate correction actions from reflection
        correction_actions = self._generate_corrections(reflection, policy, env)

        # Check if correction succeeded
        success = self._check_recovery(env)

        return CorrectionAttempt(
            failure=failure,
            reflection=reflection,
            correction_actions=correction_actions,
            success=success,
        )

    def _generate_reflection(
        self,
        failure: FailureEvent,
        trajectory: list[TrajectoryEvent],
    ) -> dict[str, Any]:
        """Generate reflection based on failure (stub)."""
        return {
            "failure_code": failure.code,
            "diagnosis": failure.description,
            "plan": "Retry with corrected approach",
        }

    def _generate_corrections(
        self,
        reflection: dict[str, Any],
        policy: Any,
        env: Any,
    ) -> list[Action]:
        """Generate correction actions (stub)."""
        # In real implementation, policy would generate actions
        return []

    def _check_recovery(self, env: Any) -> bool:
        """Check if recovery succeeded (stub)."""
        return False


@dataclass
class SCoReExample:
    """Training example for SCoRe RL."""

    observation: bytes  # Screenshot
    action: dict[str, Any]
    reward: float
    is_correction: bool = False
    turn: int = 0  # 0 = initial, 1+ = correction turns
