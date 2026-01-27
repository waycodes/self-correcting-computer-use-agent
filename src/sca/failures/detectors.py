"""Failure detectors for identifying issues during execution."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from sca.failures.taxonomy import (
    FailureCategory,
    FailureEvent,
    FailureSeverity,
)
from sca.types import TrajectoryEvent


class FailureDetector(ABC):
    """Abstract base for failure detectors."""

    @abstractmethod
    def detect(
        self, events: list[TrajectoryEvent], step: int
    ) -> FailureEvent | None:
        """Detect failure from trajectory events."""


class StalledProgressDetector(FailureDetector):
    """Detect stalled progress via action repetition."""

    def __init__(self, window_size: int = 5, threshold: int = 3) -> None:
        """Initialize detector."""
        self.window_size = window_size
        self.threshold = threshold

    def detect(
        self, events: list[TrajectoryEvent], step: int
    ) -> FailureEvent | None:
        """Detect repeated actions indicating stalled progress."""
        actions = [
            e for e in events[-self.window_size:]
            if e.event_type.value == "action"
        ]

        if len(actions) < self.threshold:
            return None

        # Check for repeated identical actions
        action_strs = [str(a.data) for a in actions]
        if len(set(action_strs[-self.threshold:])) == 1:
            return FailureEvent(
                code="LOOP_SAME_ACTION",
                category=FailureCategory.ACTION_LOOP,
                severity=FailureSeverity.MEDIUM,
                step=step,
                description="Same action repeated multiple times",
                evidence={"repeated_action": actions[-1].data},
            )

        return None


class WrongFocusDetector(FailureDetector):
    """Detect wrong window/app focus from UI cues."""

    def __init__(self, expected_app: str | None = None) -> None:
        """Initialize detector."""
        self.expected_app = expected_app

    def detect(
        self, events: list[TrajectoryEvent], step: int
    ) -> FailureEvent | None:
        """Detect wrong focus from observation metadata."""
        # Look for recent observations with window info
        for event in reversed(events[-3:]):
            if event.event_type.value == "observation":
                metadata = event.data.get("metadata", {})
                active_app = metadata.get("active_app", "")

                if (
                    self.expected_app
                    and active_app
                    and self.expected_app.lower() not in active_app.lower()
                ):
                    return FailureEvent(
                        code="FOCUS_WRONG_APP",
                        category=FailureCategory.FOCUS_ERROR,
                        severity=FailureSeverity.MEDIUM,
                        step=step,
                        description="Wrong application focused",
                        evidence={
                            "expected": self.expected_app,
                            "actual": active_app,
                        },
                    )
        return None


class ToolMisuseDetector(FailureDetector):
    """Detect tool misuse patterns."""

    def __init__(self, error_threshold: int = 2) -> None:
        """Initialize detector."""
        self.error_threshold = error_threshold
        self.recent_errors: list[dict[str, Any]] = []

    def detect(
        self, events: list[TrajectoryEvent], step: int
    ) -> FailureEvent | None:
        """Detect repeated tool errors."""
        # Look for tool call errors in recent events
        for event in events[-5:]:
            if event.event_type.value == "action":
                data = event.data
                if data.get("type") == "tool_call" and data.get("error"):
                    self.recent_errors.append(data)

        if len(self.recent_errors) >= self.error_threshold:
            # Check for same error repeated
            error_msgs = [e.get("error") for e in self.recent_errors]
            if len(set(error_msgs[-self.error_threshold:])) == 1:
                return FailureEvent(
                    code="TOOL_REPEATED_ERROR",
                    category=FailureCategory.TOOL_MISUSE,
                    severity=FailureSeverity.HIGH,
                    step=step,
                    description="Same tool error repeated",
                    evidence={"errors": self.recent_errors[-self.error_threshold:]},
                )

        return None

    def reset(self) -> None:
        """Reset detector state."""
        self.recent_errors = []


@dataclass
class DetectorResult:
    """Result from running all detectors."""

    failures: list[FailureEvent]
    step: int

    @property
    def has_failures(self) -> bool:
        return len(self.failures) > 0


class FailureDetectorPipeline:
    """Pipeline of failure detectors."""

    def __init__(self) -> None:
        """Initialize pipeline with default detectors."""
        self.detectors: list[FailureDetector] = [
            StalledProgressDetector(),
            ToolMisuseDetector(),
        ]

    def add_detector(self, detector: FailureDetector) -> None:
        """Add a detector to the pipeline."""
        self.detectors.append(detector)

    def run(
        self, events: list[TrajectoryEvent], step: int
    ) -> DetectorResult:
        """Run all detectors and collect failures."""
        failures = []
        for detector in self.detectors:
            failure = detector.detect(events, step)
            if failure:
                failures.append(failure)
        return DetectorResult(failures=failures, step=step)
