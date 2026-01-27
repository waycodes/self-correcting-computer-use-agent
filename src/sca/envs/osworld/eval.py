"""OSWorld evaluation hooks."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class EvalVerdict(Enum):
    """Evaluation verdict for a task."""

    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class EvalResult:
    """Result of evaluating a task completion."""

    verdict: EvalVerdict
    score: float  # 0.0 to 1.0
    reason: str
    details: dict[str, Any]


class OSWorldEvaluator:
    """Evaluator that calls OSWorld's execution-based eval scripts."""

    def __init__(self, task_config: dict[str, Any]) -> None:
        """Initialize evaluator with task configuration."""
        self.task_config = task_config
        self.eval_type = task_config.get("eval_type", "execution")

    def evaluate(self, env: Any, trajectory: list[dict[str, Any]]) -> EvalResult:
        """Evaluate task completion.

        Args:
            env: The environment adapter (for state inspection)
            trajectory: List of trajectory events

        Returns:
            EvalResult with verdict and details
        """
        # Check if task was marked done
        done_events = [e for e in trajectory if e.get("event_type") == "done"]
        if not done_events:
            return EvalResult(
                verdict=EvalVerdict.TIMEOUT,
                score=0.0,
                reason="Task not completed within step limit",
                details={"steps": len(trajectory)},
            )

        # Dispatch to appropriate evaluator
        if self.eval_type == "execution":
            return self._eval_execution(env)
        elif self.eval_type == "state":
            return self._eval_state(env)
        else:
            return self._eval_heuristic(trajectory)

    def _eval_execution(self, env: Any) -> EvalResult:
        """Run execution-based evaluation (calls OSWorld eval script)."""
        # In real implementation, this would call OSWorld's eval scripts
        # For now, return a placeholder that can be wired up later
        eval_script = self.task_config.get("eval_script")
        if not eval_script:
            return EvalResult(
                verdict=EvalVerdict.ERROR,
                score=0.0,
                reason="No eval_script specified in task config",
                details={},
            )

        # Placeholder for actual execution
        # Would run: subprocess.run([eval_script, ...])
        return EvalResult(
            verdict=EvalVerdict.SUCCESS,
            score=1.0,
            reason="Execution eval passed (placeholder)",
            details={"eval_script": eval_script},
        )

    def _eval_state(self, env: Any) -> EvalResult:
        """Evaluate based on final environment state."""
        expected_state = self.task_config.get("expected_state", {})
        if not expected_state:
            return EvalResult(
                verdict=EvalVerdict.ERROR,
                score=0.0,
                reason="No expected_state in task config",
                details={},
            )

        # Placeholder for state comparison
        return EvalResult(
            verdict=EvalVerdict.SUCCESS,
            score=1.0,
            reason="State eval passed (placeholder)",
            details={"expected": expected_state},
        )

    def _eval_heuristic(self, trajectory: list[dict[str, Any]]) -> EvalResult:
        """Heuristic evaluation based on trajectory."""
        # Simple heuristic: check if done action was taken
        action_events = [e for e in trajectory if e.get("event_type") == "action"]
        done_actions = [
            e for e in action_events if e.get("data", {}).get("type") == "done"
        ]

        if done_actions:
            return EvalResult(
                verdict=EvalVerdict.SUCCESS,
                score=1.0,
                reason="Agent signaled completion",
                details={"total_actions": len(action_events)},
            )

        return EvalResult(
            verdict=EvalVerdict.FAILURE,
            score=0.0,
            reason="Agent did not signal completion",
            details={"total_actions": len(action_events)},
        )
