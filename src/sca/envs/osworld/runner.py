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
        evaluator: Any = None,  # OSWorldEvaluator | None
    ) -> dict[str, Any]:
        """Run task with given policy and environment.

        The returned dict always carries an explicit ``success`` verdict plus a
        ``success_source`` tag naming where that verdict came from. Aggregators
        read ``success``, so omitting it silently scored every task as a failure.

        ``done`` is environment termination, not task success, so it is not a
        substitute for a verdict. When an ``evaluator`` is supplied its
        ``EvalVerdict`` is authoritative. Otherwise the fallback is the weakest
        defensible rule (terminated under the step limit with positive reward)
        and is labelled ``heuristic`` so a consumer can tell the two apart
        rather than inferring an eval ran when none did.
        """
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

        success, success_source = self._resolve_success(
            evaluator=evaluator,
            env=env,
            done=done,
            total_reward=total_reward,
            max_steps=max_steps,
        )

        return {
            "task_id": self.task_id,
            "steps": self.step_count,
            "total_reward": total_reward,
            "done": done,
            "success": success,
            "success_source": success_source,
        }

    def _resolve_success(
        self,
        evaluator: Any,
        env: Any,
        done: bool,
        total_reward: float,
        max_steps: int,
    ) -> tuple[bool, str]:
        """Resolve the task success verdict and name its provenance.

        Returns a ``(success, success_source)`` pair. ``success_source`` is
        ``"evaluator"`` when an OSWorld evaluator decided, ``"heuristic"`` when
        the reward fallback decided, and ``"evaluator_error"`` when an evaluator
        was supplied but raised. An evaluator crash fails closed rather than
        falling back, because silently downgrading to the heuristic would report
        a weaker verdict under a stronger label.
        """
        if evaluator is not None:
            from sca.envs.osworld.eval import EvalVerdict

            try:
                trajectory = [event.to_dict() for event in self.events]
                result = evaluator.evaluate(env, trajectory)
            except Exception:
                return False, "evaluator_error"
            return result.verdict is EvalVerdict.SUCCESS, "evaluator"

        truncated = self.step_count >= max_steps and not done
        return (done and not truncated and total_reward > 0.0), "heuristic"

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
