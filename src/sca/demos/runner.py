"""Live demo runner with on-screen overlays."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class DemoConfig:
    """Configuration for demo run."""

    task_id: str
    show_overlay: bool = True
    record: bool = False
    output_dir: Path = Path("demos/output")
    overlay_position: str = "top-right"  # top-left, top-right, etc.


class DemoRunner:
    """Run live demos with visual overlays."""

    def __init__(self, config: DemoConfig) -> None:
        """Initialize demo runner."""
        self.config = config
        self.step_count = 0
        self.status = "idle"

    def start(self) -> None:
        """Start demo run."""
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        self.status = "running"
        self.step_count = 0

    def step(self, action: dict[str, Any], result: dict[str, Any]) -> None:
        """Process one demo step."""
        self.step_count += 1
        # In real implementation: update overlay, capture frame if recording

    def show_overlay(self, text: str) -> None:
        """Display overlay text (stub)."""
        if self.config.show_overlay:
            # In real implementation: render overlay on screen
            pass

    def finish(self, success: bool) -> dict[str, Any]:
        """Finish demo and return summary."""
        self.status = "finished"
        return {
            "task_id": self.config.task_id,
            "success": success,
            "steps": self.step_count,
            "recorded": self.config.record,
        }

    def run_task(self, task_id: str | None = None) -> dict[str, Any]:
        """Run a complete demo task (stub)."""
        self.start()
        self.show_overlay(f"Running: {task_id or self.config.task_id}")

        # Stub: simulate a few steps
        for i in range(3):
            self.step({"type": "click", "step": i}, {"success": True})
            self.show_overlay(f"Step {i + 1}")

        return self.finish(success=True)
