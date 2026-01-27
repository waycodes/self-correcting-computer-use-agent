"""Structured trajectory event logging."""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sca.types import EventType, TrajectoryEvent


@dataclass
class TrajectoryLogger:
    """Logger for trajectory events with artifact management."""

    output_dir: Path
    run_id: str
    events: list[TrajectoryEvent] = field(default_factory=list)
    screenshot_count: int = 0

    def __post_init__(self) -> None:
        """Create output directory structure."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "screenshots").mkdir(exist_ok=True)

    def log_event(
        self,
        event_type: EventType,
        step: int,
        data: dict[str, Any] | None = None,
    ) -> TrajectoryEvent:
        """Log a trajectory event."""
        event = TrajectoryEvent(
            event_type=event_type,
            step=step,
            data=data or {},
        )
        self.events.append(event)
        return event

    def log_screenshot(self, screenshot: bytes, step: int) -> str:
        """Save screenshot and return relative path."""
        filename = f"screenshot_{step:04d}.png"
        path = self.output_dir / "screenshots" / filename
        path.write_bytes(screenshot)
        self.screenshot_count += 1
        return f"screenshots/{filename}"

    def save(self) -> Path:
        """Save trajectory to JSONL file."""
        traj_path = self.output_dir / "trajectory.jsonl"
        with traj_path.open("w") as f:
            for event in self.events:
                f.write(json.dumps(event.to_dict()) + "\n")
        return traj_path

    def save_summary(self, extra: dict[str, Any] | None = None) -> Path:
        """Save run summary."""
        summary = {
            "run_id": self.run_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_events": len(self.events),
            "screenshot_count": self.screenshot_count,
            "event_counts": self._count_events(),
            **(extra or {}),
        }
        summary_path = self.output_dir / "summary.json"
        summary_path.write_text(json.dumps(summary, indent=2))
        return summary_path

    def _count_events(self) -> dict[str, int]:
        """Count events by type."""
        counts: dict[str, int] = {}
        for event in self.events:
            key = event.event_type.value
            counts[key] = counts.get(key, 0) + 1
        return counts


def load_trajectory(path: Path) -> list[TrajectoryEvent]:
    """Load trajectory from JSONL file."""
    events = []
    with path.open() as f:
        for line in f:
            data = json.loads(line)
            event = TrajectoryEvent(
                event_type=EventType(data["event_type"]),
                timestamp=data["timestamp"],
                step=data["step"],
                data=data.get("data", {}),
            )
            events.append(event)
    return events
