"""Single task runner for OSWorld."""

import json
from pathlib import Path
from typing import Any

from sca.logging.run_manifest import RunManifest
from sca.types import EventType, Observation, TrajectoryEvent
from sca.utils.repro import set_seed


class TaskRunner:
    """Runs a single OSWorld task and saves artifacts."""

    def __init__(
        self,
        output_dir: Path,
        task_id: str,
        seed: int = 42,
    ) -> None:
        """Initialize runner."""
        self.output_dir = output_dir
        self.task_id = task_id
        self.seed = seed
        self.events: list[TrajectoryEvent] = []
        self.step_count = 0

    def run(
        self,
        policy_fn: Any,  # Callable[[Observation], Action]
        env: Any,  # EnvAdapter
        max_steps: int = 100,
    ) -> dict[str, Any]:
        """Run task with given policy and environment."""
        # Setup
        self.output_dir.mkdir(parents=True, exist_ok=True)
        seed_state = set_seed(self.seed)

        # Create manifest
        manifest = RunManifest(
            run_id=self.task_id,
            seed_state=seed_state,
            config={"max_steps": max_steps, "task_id": self.task_id},
        )

        # Reset environment
        obs = env.reset()
        self._log_event(EventType.RESET, {"task_id": self.task_id})
        self._save_screenshot(obs, 0)

        # Run loop
        done = False
        total_reward = 0.0

        while not done and self.step_count < max_steps:
            # Get action from policy
            action = policy_fn(obs)
            self._log_event(
                EventType.ACTION,
                {"type": action.type.value, "params": action.params},
            )

            # Execute action
            result = env.step(action)
            self.step_count += 1

            # Log observation
            self._log_event(EventType.OBSERVATION, {"step": self.step_count})
            self._save_screenshot(result.observation, self.step_count)

            # Update state
            obs = result.observation
            total_reward += result.reward
            done = result.done

            if result.reward != 0:
                self._log_event(EventType.REWARD, {"reward": result.reward})

        # Log completion
        self._log_event(
            EventType.DONE,
            {"total_reward": total_reward, "steps": self.step_count},
        )

        # Save artifacts
        manifest.save(self.output_dir / "manifest.json")
        self._save_trajectory()

        return {
            "task_id": self.task_id,
            "steps": self.step_count,
            "total_reward": total_reward,
            "done": done,
        }

    def _log_event(self, event_type: EventType, data: dict[str, Any]) -> None:
        """Log a trajectory event."""
        event = TrajectoryEvent(
            event_type=event_type,
            step=self.step_count,
            data=data,
        )
        self.events.append(event)

    def _save_screenshot(self, obs: Observation, step: int) -> None:
        """Save screenshot to disk."""
        screenshot_path = self.output_dir / f"screenshot_{step:04d}.png"
        screenshot_path.write_bytes(obs.screenshot)

    def _save_trajectory(self) -> None:
        """Save trajectory log to JSONL."""
        traj_path = self.output_dir / "trajectory.jsonl"
        with traj_path.open("w") as f:
            for event in self.events:
                f.write(json.dumps(event.to_dict()) + "\n")
