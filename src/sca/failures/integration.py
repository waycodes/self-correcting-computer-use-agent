"""Integration of failure detectors with AgentLoop."""

from dataclasses import dataclass, field
from typing import Any

from sca.failures.detectors import FailureDetectorPipeline
from sca.failures.recovery import RecoveryTracker
from sca.failures.taxonomy import FailureEvent
from sca.types import EventType, TrajectoryEvent


@dataclass
class FailureAwareLoopState:
    """State for failure-aware agent loop."""

    detector_pipeline: FailureDetectorPipeline = field(
        default_factory=FailureDetectorPipeline
    )
    recovery_tracker: RecoveryTracker = field(default_factory=RecoveryTracker)
    failure_events: list[FailureEvent] = field(default_factory=list)

    def check_for_failures(
        self, events: list[TrajectoryEvent], step: int
    ) -> list[FailureEvent]:
        """Run detectors and record any failures."""
        result = self.detector_pipeline.run(events, step)
        for failure in result.failures:
            self.failure_events.append(failure)
            self.recovery_tracker.on_failure(failure, step)
        return result.failures

    def mark_recovered(self, failure: FailureEvent, step: int) -> None:
        """Mark a failure as recovered."""
        failure.recovered = True
        self.recovery_tracker.on_recovery(failure, step)

    def on_task_complete(self, success: bool) -> None:
        """Called when task completes."""
        if success:
            self.recovery_tracker.on_task_success()

    def get_failure_summary(self) -> dict[str, Any]:
        """Get summary of failures and recovery."""
        return {
            "total_failures": len(self.failure_events),
            "failures": [f.to_dict() for f in self.failure_events],
            "recovery_metrics": self.recovery_tracker.get_metrics().to_dict(),
        }


def create_failure_event_log(failure: FailureEvent) -> TrajectoryEvent:
    """Create a trajectory event for a failure."""
    return TrajectoryEvent(
        event_type=EventType.ERROR,
        step=failure.step,
        data={
            "failure_code": failure.code,
            "category": failure.category.value,
            "severity": failure.severity.value,
            "description": failure.description,
            "evidence": failure.evidence,
        },
    )
