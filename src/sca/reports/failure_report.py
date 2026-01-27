"""Failure taxonomy report generator."""

from dataclasses import dataclass, field
from pathlib import Path

from sca.failures.taxonomy import FailureCategory


@dataclass
class FailureExemplar:
    """Example of a failure."""

    task_id: str
    category: FailureCategory
    description: str
    replay_link: str | None = None


@dataclass
class CategoryStats:
    """Statistics for a failure category."""

    category: FailureCategory
    count: int
    rate: float
    exemplars: list[FailureExemplar] = field(default_factory=list)


class FailureReportGenerator:
    """Generate failure taxonomy report."""

    def __init__(self, output_dir: Path = Path("reports")) -> None:
        """Initialize generator."""
        self.output_dir = output_dir
        self.stats: dict[FailureCategory, CategoryStats] = {}
        self.total_failures = 0

    def add_failure(
        self,
        task_id: str,
        category: FailureCategory,
        description: str,
        replay_link: str | None = None,
    ) -> None:
        """Record a failure."""
        self.total_failures += 1

        if category not in self.stats:
            self.stats[category] = CategoryStats(category=category, count=0, rate=0.0)

        self.stats[category].count += 1

        # Keep top 3 exemplars per category
        if len(self.stats[category].exemplars) < 3:
            self.stats[category].exemplars.append(
                FailureExemplar(
                    task_id=task_id,
                    category=category,
                    description=description,
                    replay_link=replay_link,
                )
            )

    def finalize(self) -> None:
        """Compute rates after all failures added."""
        for stats in self.stats.values():
            stats.rate = stats.count / self.total_failures if self.total_failures else 0

    def generate_markdown(self) -> str:
        """Generate failure report markdown."""
        self.finalize()

        lines = [
            "# Failure Taxonomy Report",
            "",
            f"Total failures analyzed: {self.total_failures}",
            "",
            "## Category Breakdown",
            "",
            "| Category | Count | Rate |",
            "|----------|-------|------|",
        ]

        for stats in sorted(self.stats.values(), key=lambda x: -x.count):
            cat = stats.category.value
            lines.append(f"| {cat} | {stats.count} | {stats.rate:.1%} |")

        lines.extend(["", "## Top Exemplars", ""])

        for stats in sorted(self.stats.values(), key=lambda x: -x.count):
            if stats.exemplars:
                lines.append(f"### {stats.category.value}")
                lines.append("")
                for ex in stats.exemplars:
                    link = f" ([replay]({ex.replay_link}))" if ex.replay_link else ""
                    lines.append(f"- **{ex.task_id}**: {ex.description}{link}")
                lines.append("")

        return "\n".join(lines)

    def save(self, filename: str = "FAILURE_REPORT.md") -> Path:
        """Save report to file."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / filename
        path.write_text(self.generate_markdown())
        return path
