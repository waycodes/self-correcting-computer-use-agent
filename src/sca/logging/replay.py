"""Replay trajectory to annotated MP4."""

from pathlib import Path
from typing import Any

from sca.logging.trajectory import load_trajectory


class TrajectoryReplay:
    """Replay a trajectory and render to MP4."""

    def __init__(self, trajectory_dir: Path) -> None:
        """Initialize replay from trajectory directory."""
        self.trajectory_dir = trajectory_dir
        self.events = load_trajectory(trajectory_dir / "trajectory.jsonl")
        self.screenshots_dir = trajectory_dir / "screenshots"

    def render_mp4(
        self,
        output_path: Path,
        fps: int = 2,
        annotate: bool = True,
    ) -> Path:
        """Render trajectory to MP4 video.

        Args:
            output_path: Path for output MP4 file
            fps: Frames per second
            annotate: Whether to add action annotations

        Returns:
            Path to rendered video
        """
        # Check for ffmpeg availability
        import shutil

        if not shutil.which("ffmpeg"):
            raise RuntimeError("ffmpeg not found. Install ffmpeg to render videos.")

        # Get screenshot files
        screenshots = sorted(self.screenshots_dir.glob("screenshot_*.png"))
        if not screenshots:
            raise ValueError("No screenshots found in trajectory")

        # Create annotated frames if requested
        if annotate:
            frames_dir = self.trajectory_dir / "annotated_frames"
            frames_dir.mkdir(exist_ok=True)
            self._create_annotated_frames(screenshots, frames_dir)
            input_pattern = str(frames_dir / "frame_%04d.png")
        else:
            input_pattern = str(self.screenshots_dir / "screenshot_%04d.png")

        # Run ffmpeg
        import subprocess

        cmd = [
            "ffmpeg",
            "-y",  # Overwrite output
            "-framerate",
            str(fps),
            "-i",
            input_pattern,
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(output_path),
        ]

        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def _create_annotated_frames(
        self, screenshots: list[Path], output_dir: Path
    ) -> None:
        """Create annotated frames with action overlays.

        Note: This is a stub. Full implementation would use PIL/OpenCV
        to draw action annotations on screenshots.
        """
        # For now, just copy screenshots as frames
        for i, screenshot in enumerate(screenshots):
            output_path = output_dir / f"frame_{i:04d}.png"
            output_path.write_bytes(screenshot.read_bytes())

    def get_action_at_step(self, step: int) -> dict[str, Any] | None:
        """Get action data for a specific step."""
        for event in self.events:
            if event.step == step and event.event_type.value == "action":
                return event.data
        return None


def replay_to_mp4(
    trajectory_dir: Path,
    output_path: Path | None = None,
    fps: int = 2,
) -> Path:
    """Convenience function to replay trajectory to MP4."""
    if output_path is None:
        output_path = trajectory_dir / "replay.mp4"

    replay = TrajectoryReplay(trajectory_dir)
    return replay.render_mp4(output_path, fps=fps)
