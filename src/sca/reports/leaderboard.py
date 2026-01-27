"""Leaderboard markdown generator."""

from dataclasses import dataclass
from pathlib import Path

from sca.metrics.bootstrap import bootstrap_ci
from sca.metrics.schema import EvalReport


@dataclass
class LeaderboardEntry:
    """Single leaderboard entry."""

    model: str
    benchmark: str
    success_rate: float
    success_ci_low: float
    success_ci_high: float
    avg_steps: float
    recovery_rate: float | None = None
    tool_invocation_rate: float | None = None


class LeaderboardGenerator:
    """Generate leaderboard markdown from evaluation reports."""

    def __init__(self, output_dir: Path = Path("reports")) -> None:
        """Initialize generator."""
        self.output_dir = output_dir
        self.entries: list[LeaderboardEntry] = []

    def add_report(
        self,
        report: EvalReport,
        model_name: str,
        benchmark: str = "osworld",
        recovery_rate: float | None = None,
        tool_rate: float | None = None,
    ) -> None:
        """Add evaluation report to leaderboard."""
        successes = [1.0 if t.success else 0.0 for t in report.tasks]
        ci = bootstrap_ci(successes) if successes else None
        ci_low = ci.lower if ci else 0.0
        ci_high = ci.upper if ci else 0.0

        entry = LeaderboardEntry(
            model=model_name,
            benchmark=benchmark,
            success_rate=report.aggregate.success_rate,
            success_ci_low=ci_low,
            success_ci_high=ci_high,
            avg_steps=report.aggregate.avg_steps,
            recovery_rate=recovery_rate,
            tool_invocation_rate=tool_rate,
        )
        self.entries.append(entry)

    def generate_markdown(self) -> str:
        """Generate leaderboard markdown."""
        lines = [
            "# Evaluation Leaderboard",
            "",
            "## Results",
            "",
            "| Model | Benchmark | Success Rate | 95% CI | Avg Steps |"
            " Recovery | Tool Rate |",
            "|-------|-----------|--------------|--------|-----------|"
            "----------|-----------|",
        ]

        for e in sorted(self.entries, key=lambda x: -x.success_rate):
            recovery = f"{e.recovery_rate:.1%}" if e.recovery_rate else "N/A"
            tool = f"{e.tool_invocation_rate:.1%}" if e.tool_invocation_rate else "N/A"
            lines.append(
                f"| {e.model} | {e.benchmark} | {e.success_rate:.1%} | "
                f"[{e.success_ci_low:.1%}, {e.success_ci_high:.1%}] | "
                f"{e.avg_steps:.1f} | {recovery} | {tool} |"
            )

        lines.extend(["", "---", f"*Generated with {len(self.entries)} entries*"])
        return "\n".join(lines)

    def save(self, filename: str = "LEADERBOARD.md") -> Path:
        """Save leaderboard to file."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / filename
        path.write_text(self.generate_markdown())
        return path
