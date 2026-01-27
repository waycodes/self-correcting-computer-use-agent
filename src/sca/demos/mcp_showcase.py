"""MCP showcase demos where tools beat GUI-only."""

from dataclasses import dataclass
from typing import Any


@dataclass
class ShowcaseTask:
    """A task that showcases MCP tool advantage."""

    task_id: str
    description: str
    gui_steps: int  # Steps needed with GUI-only
    mcp_steps: int  # Steps needed with MCP tools
    tools_used: list[str]


# Tasks where MCP tools provide significant advantage
SHOWCASE_TASKS: list[ShowcaseTask] = [
    ShowcaseTask(
        task_id="file_search",
        description="Find file containing specific text",
        gui_steps=15,
        mcp_steps=3,
        tools_used=["grep", "find"],
    ),
    ShowcaseTask(
        task_id="batch_rename",
        description="Rename multiple files with pattern",
        gui_steps=20,
        mcp_steps=2,
        tools_used=["rename", "mv"],
    ),
    ShowcaseTask(
        task_id="data_extract",
        description="Extract data from structured file",
        gui_steps=12,
        mcp_steps=4,
        tools_used=["jq", "read_file"],
    ),
]


class MCPShowcase:
    """Run MCP showcase demonstrations."""

    def __init__(self) -> None:
        """Initialize showcase."""
        self.tasks = SHOWCASE_TASKS
        self.results: list[dict[str, Any]] = []

    def get_tasks(self) -> list[ShowcaseTask]:
        """Get available showcase tasks."""
        return self.tasks

    def run_comparison(self, task_id: str) -> dict[str, Any]:
        """Run GUI vs MCP comparison for a task (stub)."""
        task = next((t for t in self.tasks if t.task_id == task_id), None)
        if not task:
            return {"error": f"Task {task_id} not found"}

        # Stub: return expected comparison
        return {
            "task_id": task.task_id,
            "description": task.description,
            "gui_only": {"steps": task.gui_steps, "success": True},
            "with_mcp": {"steps": task.mcp_steps, "success": True},
            "speedup": f"{task.gui_steps / task.mcp_steps:.1f}x",
            "tools_used": task.tools_used,
        }

    def run_all(self) -> list[dict[str, Any]]:
        """Run all showcase comparisons."""
        self.results = [self.run_comparison(t.task_id) for t in self.tasks]
        return self.results

    def generate_summary(self) -> str:
        """Generate markdown summary of showcase results."""
        lines = [
            "# MCP Tool Showcase",
            "",
            "Tasks where MCP tools significantly outperform GUI-only:",
            "",
            "| Task | GUI Steps | MCP Steps | Speedup | Tools |",
            "|------|-----------|-----------|---------|-------|",
        ]

        for task in self.tasks:
            speedup = f"{task.gui_steps / task.mcp_steps:.1f}x"
            tools = ", ".join(task.tools_used)
            lines.append(
                f"| {task.description} | {task.gui_steps} | "
                f"{task.mcp_steps} | {speedup} | {tools} |"
            )

        return "\n".join(lines)
