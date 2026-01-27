"""MCP metrics: invocation rate, tool success rate, latency, error codes."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCallMetric:
    """Metrics for a single tool call."""

    tool_name: str
    success: bool
    latency_ms: float
    error_code: int | None = None
    error_message: str | None = None


@dataclass
class MCPMetrics:
    """Aggregated MCP metrics for a run."""

    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_latency_ms: float = 0.0
    calls_by_tool: dict[str, int] = field(default_factory=dict)
    errors_by_code: dict[int, int] = field(default_factory=dict)
    call_history: list[ToolCallMetric] = field(default_factory=list)

    def record_call(self, metric: ToolCallMetric) -> None:
        """Record a tool call."""
        self.total_calls += 1
        self.total_latency_ms += metric.latency_ms
        self.call_history.append(metric)

        # Track by tool name
        self.calls_by_tool[metric.tool_name] = (
            self.calls_by_tool.get(metric.tool_name, 0) + 1
        )

        if metric.success:
            self.successful_calls += 1
        else:
            self.failed_calls += 1
            if metric.error_code is not None:
                self.errors_by_code[metric.error_code] = (
                    self.errors_by_code.get(metric.error_code, 0) + 1
                )

    @property
    def success_rate(self) -> float:
        """Tool call success rate."""
        if self.total_calls == 0:
            return 0.0
        return self.successful_calls / self.total_calls

    @property
    def avg_latency_ms(self) -> float:
        """Average latency per call."""
        if self.total_calls == 0:
            return 0.0
        return self.total_latency_ms / self.total_calls

    def invocation_rate(self, total_steps: int) -> float:
        """Tool invocation rate (calls per step)."""
        if total_steps == 0:
            return 0.0
        return self.total_calls / total_steps

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "success_rate": self.success_rate,
            "avg_latency_ms": self.avg_latency_ms,
            "calls_by_tool": self.calls_by_tool,
            "errors_by_code": self.errors_by_code,
        }


class MCPMetricsCollector:
    """Collector for MCP metrics during a run."""

    def __init__(self) -> None:
        """Initialize collector."""
        self.metrics = MCPMetrics()

    def record_success(
        self, tool_name: str, latency_ms: float
    ) -> None:
        """Record a successful tool call."""
        self.metrics.record_call(
            ToolCallMetric(tool_name=tool_name, success=True, latency_ms=latency_ms)
        )

    def record_failure(
        self,
        tool_name: str,
        latency_ms: float,
        error_code: int | None = None,
        error_message: str | None = None,
    ) -> None:
        """Record a failed tool call."""
        self.metrics.record_call(
            ToolCallMetric(
                tool_name=tool_name,
                success=False,
                latency_ms=latency_ms,
                error_code=error_code,
                error_message=error_message,
            )
        )

    def get_metrics(self) -> MCPMetrics:
        """Get collected metrics."""
        return self.metrics

    def reset(self) -> None:
        """Reset metrics."""
        self.metrics = MCPMetrics()
