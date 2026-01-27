"""Unified evaluation runner for OSWorld and OSWorld-MCP."""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from sca.metrics.schema import AggregateMetrics, EvalReport, TaskMetrics


@dataclass
class EvalConfig:
    """Configuration for evaluation run."""

    benchmark: str = "osworld"  # osworld or osworld-mcp
    task_ids: list[str] = field(default_factory=list)
    max_steps: int = 30
    timeout_seconds: int = 300
    output_dir: Path = Path("reports")
    save_trajectories: bool = True


class EvalRunner:
    """Unified evaluation runner."""

    def __init__(self, config: EvalConfig) -> None:
        """Initialize runner."""
        self.config = config
        self.results: list[TaskMetrics] = []

    def run_task(self, task_id: str) -> TaskMetrics:
        """Run single task evaluation (stub)."""
        return TaskMetrics(task_id=task_id, success=False, steps=0, total_reward=0.0)

    def run_all(self) -> EvalReport:
        """Run evaluation on all configured tasks."""
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        task_ids = self.config.task_ids or self._get_default_tasks()

        for task_id in task_ids:
            self.results.append(self.run_task(task_id))

        return self._aggregate_results()

    def _get_default_tasks(self) -> list[str]:
        """Get default task list for benchmark."""
        if self.config.benchmark == "osworld-mcp":
            return ["mcp_task_1", "mcp_task_2"]
        return ["task_1", "task_2"]

    def _aggregate_results(self) -> EvalReport:
        """Aggregate task results into report."""
        total = len(self.results)
        successes = sum(1 for r in self.results if r.success)
        total_reward = sum(r.total_reward for r in self.results)

        aggregate = AggregateMetrics(
            total_tasks=total,
            success_count=successes,
            success_rate=successes / total if total else 0.0,
            avg_steps=sum(r.steps for r in self.results) / total if total else 0.0,
            avg_reward=total_reward / total if total else 0.0,
        )

        config = {
            "benchmark": self.config.benchmark,
            "max_steps": self.config.max_steps,
        }

        return EvalReport(
            run_id=str(uuid.uuid4())[:8],
            timestamp=datetime.now().isoformat(),
            config=config,
            aggregate=aggregate,
            tasks=self.results,
        )

    def save_report(self, report: EvalReport, path: Path | None = None) -> Path:
        """Save report to JSON."""
        output_path = path or self.config.output_dir / "eval_report.json"
        data: dict[str, Any] = {
            "run_id": report.run_id,
            "timestamp": report.timestamp,
            "config": report.config,
            "aggregate": report.aggregate.to_dict(),
            "tasks": [t.to_dict() for t in report.tasks],
        }
        output_path.write_text(json.dumps(data, indent=2))
        return output_path
