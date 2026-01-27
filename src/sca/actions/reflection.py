"""Reflection action schema for self-correction."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DiagnosisType(Enum):
    """Types of failure diagnosis."""

    GROUNDING_ERROR = "grounding_error"  # Wrong element targeted
    FOCUS_ERROR = "focus_error"  # Wrong window/app focused
    TOOL_MISUSE = "tool_misuse"  # Incorrect tool usage
    STALLED = "stalled"  # No progress being made
    UNEXPECTED_STATE = "unexpected_state"  # Environment in unexpected state
    UNKNOWN = "unknown"


@dataclass
class Diagnosis:
    """Diagnosis of what went wrong."""

    diagnosis_type: DiagnosisType
    description: str
    confidence: float = 0.5  # 0.0 to 1.0
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.diagnosis_type.value,
            "description": self.description,
            "confidence": self.confidence,
            "evidence": self.evidence,
        }


@dataclass
class PlanStep:
    """A single step in a revised plan."""

    action_type: str  # "click", "type", "tool_call", etc.
    description: str
    params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_type": self.action_type,
            "description": self.description,
            "params": self.params,
        }


@dataclass
class ReflectionAction:
    """Reflection action for self-correction."""

    diagnosis: Diagnosis
    revised_plan: list[PlanStep] = field(default_factory=list)
    should_retry: bool = True
    reasoning: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "reflect",
            "diagnosis": self.diagnosis.to_dict(),
            "revised_plan": [s.to_dict() for s in self.revised_plan],
            "should_retry": self.should_retry,
            "reasoning": self.reasoning,
        }


def parse_reflection(data: dict[str, Any]) -> ReflectionAction:
    """Parse a reflection action from dictionary."""
    diag_data = data.get("diagnosis", {})
    diagnosis = Diagnosis(
        diagnosis_type=DiagnosisType(diag_data.get("type", "unknown")),
        description=diag_data.get("description", ""),
        confidence=diag_data.get("confidence", 0.5),
        evidence=diag_data.get("evidence", []),
    )

    plan_data = data.get("revised_plan", [])
    revised_plan = [
        PlanStep(
            action_type=s.get("action_type", ""),
            description=s.get("description", ""),
            params=s.get("params", {}),
        )
        for s in plan_data
    ]

    return ReflectionAction(
        diagnosis=diagnosis,
        revised_plan=revised_plan,
        should_retry=data.get("should_retry", True),
        reasoning=data.get("reasoning", ""),
    )
