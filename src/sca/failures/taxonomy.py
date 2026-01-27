"""Failure taxonomy v1 for self-correcting agents."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FailureCategory(Enum):
    """Top-level failure categories."""

    GUI_GROUNDING = "gui_grounding"  # Wrong element targeted
    FOCUS_ERROR = "focus_error"  # Wrong window/app focused
    TOOL_MISUSE = "tool_misuse"  # Incorrect tool usage
    ACTION_LOOP = "action_loop"  # Repeated ineffective actions
    STALLED = "stalled"  # No progress being made
    TIMEOUT = "timeout"  # Exceeded step limit
    CRASH = "crash"  # Environment or agent crash
    UNKNOWN = "unknown"


class FailureSeverity(Enum):
    """Severity levels for failures."""

    LOW = "low"  # Minor, may self-correct
    MEDIUM = "medium"  # Significant, needs intervention
    HIGH = "high"  # Critical, task likely failed
    FATAL = "fatal"  # Unrecoverable


@dataclass
class FailureCode:
    """Specific failure code within a category."""

    category: FailureCategory
    code: str
    description: str
    severity: FailureSeverity = FailureSeverity.MEDIUM


# Failure code registry
FAILURE_CODES: dict[str, FailureCode] = {
    # GUI Grounding failures
    "GUI_MISS": FailureCode(
        FailureCategory.GUI_GROUNDING, "GUI_MISS",
        "Click missed target element", FailureSeverity.LOW
    ),
    "GUI_WRONG_ELEMENT": FailureCode(
        FailureCategory.GUI_GROUNDING, "GUI_WRONG_ELEMENT",
        "Clicked wrong element", FailureSeverity.MEDIUM
    ),
    # Focus errors
    "FOCUS_WRONG_WINDOW": FailureCode(
        FailureCategory.FOCUS_ERROR, "FOCUS_WRONG_WINDOW",
        "Actions sent to wrong window", FailureSeverity.MEDIUM
    ),
    "FOCUS_WRONG_APP": FailureCode(
        FailureCategory.FOCUS_ERROR, "FOCUS_WRONG_APP",
        "Wrong application focused", FailureSeverity.MEDIUM
    ),
    # Tool misuse
    "TOOL_INVALID_ARGS": FailureCode(
        FailureCategory.TOOL_MISUSE, "TOOL_INVALID_ARGS",
        "Invalid tool arguments", FailureSeverity.LOW
    ),
    "TOOL_WRONG_TOOL": FailureCode(
        FailureCategory.TOOL_MISUSE, "TOOL_WRONG_TOOL",
        "Used wrong tool for task", FailureSeverity.MEDIUM
    ),
    "TOOL_REPEATED_ERROR": FailureCode(
        FailureCategory.TOOL_MISUSE, "TOOL_REPEATED_ERROR",
        "Same tool error repeated", FailureSeverity.HIGH
    ),
    # Action loops
    "LOOP_SAME_ACTION": FailureCode(
        FailureCategory.ACTION_LOOP, "LOOP_SAME_ACTION",
        "Same action repeated multiple times", FailureSeverity.MEDIUM
    ),
    "LOOP_ACTION_CYCLE": FailureCode(
        FailureCategory.ACTION_LOOP, "LOOP_ACTION_CYCLE",
        "Cycling through same actions", FailureSeverity.HIGH
    ),
    # Stalled
    "STALLED_NO_CHANGE": FailureCode(
        FailureCategory.STALLED, "STALLED_NO_CHANGE",
        "No visual change after actions", FailureSeverity.MEDIUM
    ),
    "STALLED_NO_PROGRESS": FailureCode(
        FailureCategory.STALLED, "STALLED_NO_PROGRESS",
        "No task progress detected", FailureSeverity.HIGH
    ),
}


@dataclass
class FailureEvent:
    """A detected failure event."""

    code: str
    category: FailureCategory
    severity: FailureSeverity
    step: int
    description: str
    evidence: dict[str, Any] = field(default_factory=dict)
    recovered: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "category": self.category.value,
            "severity": self.severity.value,
            "step": self.step,
            "description": self.description,
            "evidence": self.evidence,
            "recovered": self.recovered,
        }


def get_failure_code(code: str) -> FailureCode | None:
    """Get failure code by name."""
    return FAILURE_CODES.get(code)
