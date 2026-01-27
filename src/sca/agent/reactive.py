"""Reactive baseline policy: vision → short plan → GUI action."""

from sca.agent.policy import Policy
from sca.types import Action, Observation, TrajectoryEvent


class ReactivePolicy(Policy):
    """Simple reactive policy that generates actions based on current observation.

    This is a baseline policy that:
    1. Looks at the current screenshot
    2. Generates a short plan (1-3 steps)
    3. Executes the first action

    In a real implementation, this would use a VLM to process the screenshot.
    For now, it's a stub that demonstrates the interface.
    """

    def __init__(self, max_actions: int = 50) -> None:
        """Initialize reactive policy."""
        self.max_actions = max_actions
        self.action_count = 0
        self.plan: list[Action] = []

    def reset(self) -> None:
        """Reset policy state."""
        self.action_count = 0
        self.plan = []

    def decide(
        self, observation: Observation, history: list[TrajectoryEvent]
    ) -> Action:
        """Decide next action based on observation."""
        self.action_count += 1

        # Check if we should stop
        if self.action_count >= self.max_actions:
            return Action.done()

        # If we have a plan, execute next step
        if self.plan:
            return self.plan.pop(0)

        # Generate new plan based on observation
        self.plan = self._generate_plan(observation, history)

        if self.plan:
            return self.plan.pop(0)

        # Default: signal done
        return Action.done()

    def _generate_plan(
        self, observation: Observation, history: list[TrajectoryEvent]
    ) -> list[Action]:
        """Generate a short plan based on observation.

        In a real implementation, this would:
        1. Encode the screenshot with a vision model
        2. Generate a plan using an LLM
        3. Parse the plan into actions

        For now, returns an empty plan (stub).
        """
        # Stub: In real implementation, would call VLM here
        # Example plan generation:
        # - Analyze screenshot to find UI elements
        # - Determine what action to take
        # - Return list of actions

        # For testing, return a simple click action
        return [Action.click(100, 100)]
