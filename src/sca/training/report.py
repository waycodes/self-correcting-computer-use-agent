"""Baseline report template for leaderboard automation."""

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sca.metrics.schema import AggregateMetrics


@dataclass
class ReportEntry:
    """A single entry in the leaderboard."""

    model_name: str
    metrics: AggregateMetrics
    timestamp: str
    config: dict[str, Any]


REPORT_TEMPLATE = """# Evaluation Report

Generated: {timestamp}

## Summary

| Model | Success Rate | Avg Steps | Tool Invocation | Recovery Rate |
|-------|-------------|-----------|-----------------|---------------|
{rows}

## Configuration

```json
{config}
```

## Notes

{notes}
"""


def generate_report(
    entries: list[ReportEntry],
    notes: str = "",
) -> str:
    """Generate markdown report from entries."""
    import json

    rows = []
    for entry in entries:
        m = entry.metrics
        sr = f"{m.success_rate:.2%}"
        steps = f"{m.avg_steps:.1f}"
        tool = f"{m.tool_invocation_rate:.2f}"
        row = f"| {entry.model_name} | {sr} | {steps} | {tool} | N/A |"
        rows.append(row)

    config = entries[0].config if entries else {}

    return REPORT_TEMPLATE.format(
        timestamp=datetime.now(timezone.utc).isoformat(),
        rows="\n".join(rows),
        config=json.dumps(config, indent=2),
        notes=notes or "No additional notes.",
    )


def save_report(report: str, output_path: Path) -> None:
    """Save report to file."""
    output_path.write_text(report)
