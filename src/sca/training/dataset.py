"""Dataset builder: trajectories → supervised examples."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sca.logging.trajectory import load_trajectory


@dataclass
class SupervisedExample:
    """A single supervised training example."""

    observation_path: str  # Path to screenshot
    action: dict[str, Any]  # Action taken
    task_id: str
    step: int
    success: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_path": self.observation_path,
            "action": self.action,
            "task_id": self.task_id,
            "step": self.step,
            "success": self.success,
        }


@dataclass
class DatasetConfig:
    """Configuration for dataset building."""

    include_failures: bool = False  # Include failed trajectories
    max_steps_per_traj: int = 100
    filter_actions: list[str] = field(default_factory=list)  # Action types to exclude


class DatasetBuilder:
    """Build supervised dataset from trajectories."""

    def __init__(self, config: DatasetConfig | None = None) -> None:
        """Initialize builder."""
        self.config = config or DatasetConfig()
        self.examples: list[SupervisedExample] = []

    def add_trajectory(
        self,
        trajectory_dir: Path,
        task_id: str,
        success: bool,
    ) -> int:
        """Add examples from a trajectory directory."""
        if not success and not self.config.include_failures:
            return 0

        events = load_trajectory(trajectory_dir / "trajectory.jsonl")
        screenshots_dir = trajectory_dir / "screenshots"
        added = 0

        for event in events:
            if event.event_type.value != "action":
                continue

            if event.step > self.config.max_steps_per_traj:
                break

            action_type = event.data.get("type", "")
            if action_type in self.config.filter_actions:
                continue

            # Find corresponding screenshot
            screenshot_path = screenshots_dir / f"screenshot_{event.step:04d}.png"
            if not screenshot_path.exists():
                continue

            example = SupervisedExample(
                observation_path=str(screenshot_path),
                action=event.data,
                task_id=task_id,
                step=event.step,
                success=success,
            )
            self.examples.append(example)
            added += 1

        return added

    def save(self, output_path: Path) -> None:
        """Save dataset to JSONL file."""
        with output_path.open("w") as f:
            for example in self.examples:
                f.write(json.dumps(example.to_dict()) + "\n")

    def get_stats(self) -> dict[str, Any]:
        """Get dataset statistics."""
        tasks = set(e.task_id for e in self.examples)
        return {
            "total_examples": len(self.examples),
            "unique_tasks": len(tasks),
            "successful_examples": sum(1 for e in self.examples if e.success),
        }


def load_dataset(path: Path) -> list[SupervisedExample]:
    """Load dataset from JSONL file."""
    examples = []
    with path.open() as f:
        for line in f:
            data = json.loads(line)
            examples.append(SupervisedExample(**data))
    return examples
