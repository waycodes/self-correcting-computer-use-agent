"""Smoke task suite for quick iteration testing."""

from dataclasses import dataclass
from typing import Any


@dataclass
class TaskDefinition:
    """Definition of a single task."""

    task_id: str
    name: str
    description: str
    eval_type: str = "heuristic"
    max_steps: int = 50
    config: dict[str, Any] | None = None


# Smoke suite: minimal tasks for quick iteration
SMOKE_TASKS: list[TaskDefinition] = [
    TaskDefinition(
        task_id="smoke_click",
        name="Click Test",
        description="Click on a specific location",
        max_steps=5,
    ),
    TaskDefinition(
        task_id="smoke_type",
        name="Type Test",
        description="Type text into a field",
        max_steps=10,
    ),
    TaskDefinition(
        task_id="smoke_navigate",
        name="Navigation Test",
        description="Navigate to a specific window",
        max_steps=20,
    ),
]


def get_smoke_suite() -> list[TaskDefinition]:
    """Get the smoke test suite."""
    return SMOKE_TASKS.copy()


def get_task_ids(suite: list[TaskDefinition]) -> list[str]:
    """Extract task IDs from a suite."""
    return [t.task_id for t in suite]
