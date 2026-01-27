"""Metric schema definitions for evaluation."""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TaskMetrics:
    """Metrics for a single task run."""

    task_id: str
    success: bool
    steps: int
    total_reward: float
    eval_verdict: str = ""
    eval_score: float = 0.0
    tool_calls: int = 0
    tool_successes: int = 0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class AggregateMetrics:
    """Aggregated metrics across multiple tasks."""

    total_tasks: int
    success_count: int
    success_rate: float
    avg_steps: float
    avg_reward: float
    tool_invocation_rate: float = 0.0
    tool_success_rate: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class EvalReport:
    """Complete evaluation report."""

    run_id: str
    timestamp: str
    config: dict[str, Any]
    aggregate: AggregateMetrics
    tasks: list[TaskMetrics] = field(default_factory=list)

    def save(self, path: Path) -> None:
        """Save report to JSON file."""
        data = {
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "config": self.config,
            "aggregate": self.aggregate.to_dict(),
            "tasks": [t.to_dict() for t in self.tasks],
        }
        path.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path: Path) -> "EvalReport":
        """Load report from JSON file."""
        data = json.loads(path.read_text())
        aggregate = AggregateMetrics(**data["aggregate"])
        tasks = [TaskMetrics(**t) for t in data["tasks"]]
        return cls(
            run_id=data["run_id"],
            timestamp=data["timestamp"],
            config=data["config"],
            aggregate=aggregate,
            tasks=tasks,
        )


def compute_aggregate(tasks: list[TaskMetrics]) -> AggregateMetrics:
    """Compute aggregate metrics from task results."""
    if not tasks:
        return AggregateMetrics(
            total_tasks=0,
            success_count=0,
            success_rate=0.0,
            avg_steps=0.0,
            avg_reward=0.0,
        )

    n = len(tasks)
    success_count = sum(1 for t in tasks if t.success)
    total_steps = sum(t.steps for t in tasks)
    total_reward = sum(t.total_reward for t in tasks)
    total_tool_calls = sum(t.tool_calls for t in tasks)
    total_tool_successes = sum(t.tool_successes for t in tasks)

    return AggregateMetrics(
        total_tasks=n,
        success_count=success_count,
        success_rate=success_count / n,
        avg_steps=total_steps / n,
        avg_reward=total_reward / n,
        tool_invocation_rate=total_tool_calls / n if n else 0.0,
        tool_success_rate=(
            total_tool_successes / total_tool_calls if total_tool_calls else 0.0
        ),
    )
