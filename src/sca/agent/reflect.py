"""Always-reflect policy that reflects every K steps."""

from sca.actions.reflection import Diagnosis, DiagnosisType, ReflectionAction
from sca.agent.policy import Policy
from sca.types import Action, ActionType, Observation, TrajectoryEvent


class AlwaysReflectPolicy(Policy):
    """Policy that reflects every K steps.

    This policy wraps another policy and injects reflection actions
    at regular intervals to encourage self-correction behavior.
    """

    def __init__(
        self,
        base_policy: Policy,
        reflect_every: int = 5,
        max_actions: int = 100,
    ) -> None:
        """Initialize always-reflect policy."""
        self.base_policy = base_policy
        self.reflect_every = reflect_every
        self.max_actions = max_actions
        self.action_count = 0
        self.last_reflection: ReflectionAction | None = None

    def reset(self) -> None:
        """Reset policy state."""
        self.action_count = 0
        self.last_reflection = None
        self.base_policy.reset()

    def decide(
        self, observation: Observation, history: list[TrajectoryEvent]
    ) -> Action:
        """Decide next action, injecting reflections every K steps."""
        self.action_count += 1

        # Check if we should stop
        if self.action_count >= self.max_actions:
            return Action.done()

        # Check if it's time to reflect
        if self._should_reflect():
            reflection = self._generate_reflection(observation, history)
            self.last_reflection = reflection
            return Action(
                type=ActionType.REFLECT,
                params=reflection.to_dict(),
            )

        # Otherwise, delegate to base policy
        return self.base_policy.decide(observation, history)

    def _should_reflect(self) -> bool:
        """Check if it's time to reflect."""
        return (
            self.reflect_every > 0
            and self.action_count % self.reflect_every == 0
        )

    def _generate_reflection(
        self, observation: Observation, history: list[TrajectoryEvent]
    ) -> ReflectionAction:
        """Generate a reflection based on recent history.

        In a real implementation, this would analyze the trajectory
        to diagnose issues and revise the plan.
        """
        # Analyze recent actions for patterns
        recent_actions = [
            e for e in history[-10:] if e.event_type.value == "action"
        ]

        # Simple heuristic: check for repeated actions
        diagnosis_type = DiagnosisType.UNKNOWN
        description = "Periodic reflection checkpoint"

        if len(recent_actions) >= 3:
            # Check if last 3 actions are similar (potential loop)
            action_types = [e.data.get("type") for e in recent_actions[-3:]]
            if len(set(action_types)) == 1:
                diagnosis_type = DiagnosisType.STALLED
                description = "Detected repeated actions, may be stuck"

        diagnosis = Diagnosis(
            diagnosis_type=diagnosis_type,
            description=description,
            confidence=0.5,
        )

        return ReflectionAction(
            diagnosis=diagnosis,
            should_retry=True,
            reasoning="Periodic reflection to assess progress",
        )
