"""Batch task runner for OSWorld."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class BatchResult:
    """Results from a batch run."""

    total_tasks: int = 0
    completed: int = 0
    success: int = 0
    failed: int = 0
    total_steps: int = 0
    total_reward: float = 0.0
    task_results: list[dict[str, Any]] = field(default_factory=list)

    def add_result(self, result: dict[str, Any]) -> None:
        """Add a task result."""
        self.task_results.append(result)
        self.completed += 1
        self.total_steps += result.get("steps", 0)
        self.total_reward += result.get("total_reward", 0.0)
        if result.get("success", False):
            self.success += 1
        else:
            self.failed += 1

    def to_summary(self) -> dict[str, Any]:
        """Generate summary statistics.

        ``success_rate`` divides by ``total_tasks``, the number of tasks the batch
        was asked to run, not by ``completed``. A task lost to a crash is a task
        the agent did not complete, so excluding it from the denominator inflates
        the reported rate by an amount that grows with harness flakiness.

        ``avg_steps`` keeps the ``completed`` denominator on purpose: it is a
        per-attempt cost, and a task that never ran contributed no steps, so
        averaging it over requested tasks would understate cost rather than
        correct a bias. ``not_run`` is reported so the gap is visible instead of
        inferred from the difference between two other fields.
        """
        attempted = max(self.total_tasks, self.completed)
        return {
            "total_tasks": self.total_tasks,
            "completed": self.completed,
            "not_run": max(attempted - self.completed, 0),
            "success": self.success,
            "failed": self.failed,
            "success_rate": self.success / attempted if attempted else 0,
            "avg_steps": self.total_steps / self.completed if self.completed else 0,
            "total_reward": self.total_reward,
        }


class BatchRunner:
    """Runs multiple OSWorld tasks and aggregates results."""

    def __init__(self, output_dir: Path, seed: int = 42) -> None:
        """Initialize batch runner."""
        self.output_dir = output_dir
        self.seed = seed
        self.results = BatchResult()

    def run(
        self,
        task_ids: list[str],
        policy_fn: Any,
        env_factory: Any,
        max_steps: int = 100,
    ) -> BatchResult:
        """Run batch of tasks."""
        from sca.envs.osworld.runner import TaskRunner

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results.total_tasks = len(task_ids)

        results_file = self.output_dir / "results.jsonl"

        with results_file.open("w") as f:
            for i, task_id in enumerate(task_ids):
                task_dir = self.output_dir / task_id
                runner = TaskRunner(task_dir, task_id, seed=self.seed + i)

                env = env_factory()
                try:
                    result = runner.run(policy_fn, env, max_steps)
                    self.results.add_result(result)
                    f.write(json.dumps(result) + "\n")
                finally:
                    env.close()

        # Save summary
        summary = self.results.to_summary()
        summary_path = self.output_dir / "summary.json"
        summary_path.write_text(json.dumps(summary, indent=2))

        return self.results
