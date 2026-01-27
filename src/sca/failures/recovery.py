"""Recovery metrics: recovery rate, time-to-recover, success-after-failure."""

from dataclasses import dataclass, field
from typing import Any

from sca.failures.taxonomy import FailureEvent


@dataclass
class RecoveryMetrics:
    """Metrics for failure recovery."""

    total_failures: int = 0
    recovered_failures: int = 0
    unrecovered_failures: int = 0
    total_recovery_steps: int = 0
    successes_after_failure: int = 0
    failures_by_category: dict[str, int] = field(default_factory=dict)
    recovery_by_category: dict[str, int] = field(default_factory=dict)

    def record_failure(self, failure: FailureEvent) -> None:
        """Record a failure event."""
        self.total_failures += 1
        cat = failure.category.value
        self.failures_by_category[cat] = self.failures_by_category.get(cat, 0) + 1

    def record_recovery(
        self, failure: FailureEvent, steps_to_recover: int
    ) -> None:
        """Record a recovery from failure."""
        self.recovered_failures += 1
        self.total_recovery_steps += steps_to_recover
        cat = failure.category.value
        self.recovery_by_category[cat] = self.recovery_by_category.get(cat, 0) + 1

    def record_task_success_after_failure(self) -> None:
        """Record task success after experiencing failures."""
        self.successes_after_failure += 1

    @property
    def recovery_rate(self) -> float:
        """Rate of recovered failures."""
        if self.total_failures == 0:
            return 0.0
        return self.recovered_failures / self.total_failures

    @property
    def avg_time_to_recover(self) -> float:
        """Average steps to recover from failure."""
        if self.recovered_failures == 0:
            return 0.0
        return self.total_recovery_steps / self.recovered_failures

    @property
    def success_after_failure_rate(self) -> float:
        """Rate of task success after experiencing failures."""
        if self.total_failures == 0:
            return 0.0
        return self.successes_after_failure / self.total_failures

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_failures": self.total_failures,
            "recovered_failures": self.recovered_failures,
            "unrecovered_failures": self.total_failures - self.recovered_failures,
            "recovery_rate": self.recovery_rate,
            "avg_time_to_recover": self.avg_time_to_recover,
            "success_after_failure_rate": self.success_after_failure_rate,
            "failures_by_category": self.failures_by_category,
            "recovery_by_category": self.recovery_by_category,
        }


class RecoveryTracker:
    """Track failures and recoveries during execution."""

    def __init__(self) -> None:
        """Initialize tracker."""
        self.metrics = RecoveryMetrics()
        self.active_failures: list[tuple[FailureEvent, int]] = []  # (failure, step)

    def on_failure(self, failure: FailureEvent, step: int) -> None:
        """Called when a failure is detected."""
        self.metrics.record_failure(failure)
        self.active_failures.append((failure, step))

    def on_recovery(self, failure: FailureEvent, current_step: int) -> None:
        """Called when a failure is recovered."""
        for i, (f, start_step) in enumerate(self.active_failures):
            if f.code == failure.code:
                steps = current_step - start_step
                self.metrics.record_recovery(failure, steps)
                self.active_failures.pop(i)
                break

    def on_task_success(self) -> None:
        """Called when task succeeds."""
        if self.metrics.total_failures > 0:
            self.metrics.record_task_success_after_failure()

    def get_metrics(self) -> RecoveryMetrics:
        """Get recovery metrics."""
        return self.metrics

    def reset(self) -> None:
        """Reset tracker."""
        self.metrics = RecoveryMetrics()
        self.active_failures = []
