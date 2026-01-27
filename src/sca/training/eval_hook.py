"""Evaluation hook for comparing baseline vs SFT model."""

from dataclasses import dataclass, field
from typing import Any

from sca.metrics.schema import AggregateMetrics, TaskMetrics, compute_aggregate


@dataclass
class ModelEvalResult:
    """Evaluation result for a single model."""

    model_name: str
    metrics: AggregateMetrics
    task_results: list[TaskMetrics] = field(default_factory=list)


@dataclass
class ComparisonResult:
    """Comparison between baseline and trained model."""

    baseline: ModelEvalResult
    trained: ModelEvalResult

    @property
    def success_improvement(self) -> float:
        """Improvement in success rate."""
        return self.trained.metrics.success_rate - self.baseline.metrics.success_rate

    @property
    def step_improvement(self) -> float:
        """Improvement in average steps (negative is better)."""
        return self.baseline.metrics.avg_steps - self.trained.metrics.avg_steps

    def to_dict(self) -> dict[str, Any]:
        return {
            "baseline": {
                "model": self.baseline.model_name,
                "success_rate": self.baseline.metrics.success_rate,
                "avg_steps": self.baseline.metrics.avg_steps,
            },
            "trained": {
                "model": self.trained.model_name,
                "success_rate": self.trained.metrics.success_rate,
                "avg_steps": self.trained.metrics.avg_steps,
            },
            "improvement": {
                "success_rate": self.success_improvement,
                "avg_steps": self.step_improvement,
            },
        }


class EvaluationHook:
    """Hook for running model comparisons."""

    def __init__(self) -> None:
        """Initialize evaluation hook."""
        self.results: dict[str, ModelEvalResult] = {}

    def record_result(
        self,
        model_name: str,
        task_results: list[TaskMetrics],
    ) -> ModelEvalResult:
        """Record evaluation results for a model."""
        metrics = compute_aggregate(task_results)
        result = ModelEvalResult(
            model_name=model_name,
            metrics=metrics,
            task_results=task_results,
        )
        self.results[model_name] = result
        return result

    def compare(
        self, baseline_name: str, trained_name: str
    ) -> ComparisonResult | None:
        """Compare baseline vs trained model."""
        baseline = self.results.get(baseline_name)
        trained = self.results.get(trained_name)

        if baseline is None or trained is None:
            return None

        return ComparisonResult(baseline=baseline, trained=trained)
