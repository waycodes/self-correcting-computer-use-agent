"""Minimal trajectory inspector for debugging."""

from pathlib import Path
from typing import Any

from sca.logging.trajectory import load_trajectory


class TrajectoryInspector:
    """Simple trajectory inspector for step-by-step debugging."""

    def __init__(self, trajectory_dir: Path) -> None:
        """Initialize inspector."""
        self.trajectory_dir = trajectory_dir
        self.events = load_trajectory(trajectory_dir / "trajectory.jsonl")
        self.screenshots_dir = trajectory_dir / "screenshots"
        self.current_step = 0

    @property
    def total_steps(self) -> int:
        """Get total number of steps."""
        return max((e.step for e in self.events), default=0)

    def get_step(self, step: int) -> dict[str, Any]:
        """Get all events and data for a specific step."""
        step_events = [e for e in self.events if e.step == step]
        screenshot_path = self.screenshots_dir / f"screenshot_{step:04d}.png"

        ss_path = str(screenshot_path) if screenshot_path.exists() else None
        return {
            "step": step,
            "events": [e.to_dict() for e in step_events],
            "screenshot_exists": screenshot_path.exists(),
            "screenshot_path": ss_path,
        }

    def next_step(self) -> dict[str, Any]:
        """Move to and return next step."""
        self.current_step = min(self.current_step + 1, self.total_steps)
        return self.get_step(self.current_step)

    def prev_step(self) -> dict[str, Any]:
        """Move to and return previous step."""
        self.current_step = max(self.current_step - 1, 0)
        return self.get_step(self.current_step)

    def goto_step(self, step: int) -> dict[str, Any]:
        """Go to specific step."""
        self.current_step = max(0, min(step, self.total_steps))
        return self.get_step(self.current_step)

    def find_events(self, event_type: str) -> list[dict[str, Any]]:
        """Find all events of a specific type."""
        return [e.to_dict() for e in self.events if e.event_type.value == event_type]

    def summary(self) -> dict[str, Any]:
        """Get trajectory summary."""
        event_counts: dict[str, int] = {}
        for event in self.events:
            key = event.event_type.value
            event_counts[key] = event_counts.get(key, 0) + 1

        return {
            "total_steps": self.total_steps,
            "total_events": len(self.events),
            "event_counts": event_counts,
            "screenshots": len(list(self.screenshots_dir.glob("*.png"))),
        }

    def print_step(self, step: int | None = None) -> None:
        """Print step info to console (for debugging)."""
        if step is None:
            step = self.current_step

        data = self.get_step(step)
        print(f"\n=== Step {step} ===")
        for event in data["events"]:
            print(f"  [{event['event_type']}] {event.get('data', {})}")
        if data["screenshot_exists"]:
            print(f"  Screenshot: {data['screenshot_path']}")
