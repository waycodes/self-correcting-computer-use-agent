"""OSWorld-MCP task mode selection and tool registry wiring."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from sca.mcp.registry import ToolRegistry
from sca.mcp.session import MCPSession


class TaskMode(Enum):
    """Task execution modes."""

    GUI_ONLY = "gui_only"  # Standard OSWorld (GUI actions only)
    MCP_ONLY = "mcp_only"  # MCP tools only
    HYBRID = "hybrid"  # Both GUI and MCP tools


@dataclass
class MCPTaskConfig:
    """Configuration for MCP-enabled tasks."""

    mode: TaskMode = TaskMode.HYBRID
    mcp_server_command: list[str] | None = None
    tool_allowlist: set[str] = field(default_factory=set)
    require_consent: bool = False


class OSWorldMCPRunner:
    """Runner that supports both GUI and MCP tool actions."""

    def __init__(
        self,
        config: MCPTaskConfig,
        session: MCPSession | None = None,
    ) -> None:
        """Initialize runner."""
        self.config = config
        self.session = session
        self.registry = ToolRegistry()
        self._initialized = False

    def initialize(self) -> None:
        """Initialize MCP session and load tools."""
        if self.config.mode == TaskMode.GUI_ONLY:
            self._initialized = True
            return

        if self.session is None:
            raise RuntimeError("MCP session required for MCP/hybrid mode")

        # Initialize session and load tools
        self.session.initialize()
        tools = self.session.list_tools()
        self.registry.load_from_mcp(tools)
        self._initialized = True

    def can_use_gui(self) -> bool:
        """Check if GUI actions are allowed."""
        return self.config.mode in (TaskMode.GUI_ONLY, TaskMode.HYBRID)

    def can_use_tools(self) -> bool:
        """Check if MCP tools are allowed."""
        return self.config.mode in (TaskMode.MCP_ONLY, TaskMode.HYBRID)

    def get_available_tools(self) -> list[str]:
        """Get list of available tool names."""
        if not self.can_use_tools():
            return []
        return self.registry.list_tools()

    def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Call an MCP tool."""
        if not self.can_use_tools():
            raise RuntimeError("Tool calls not allowed in GUI-only mode")

        if not self._initialized:
            raise RuntimeError("Runner not initialized")

        # Validate against registry
        valid, error = self.registry.validate_call(name, arguments)
        if not valid:
            raise ValueError(error)

        # Call via session
        if self.session is None:
            raise RuntimeError("No MCP session")

        return self.session.call_tool(name, arguments)

    def shutdown(self) -> None:
        """Shutdown MCP session."""
        if self.session and self._initialized:
            self.session.shutdown()
            self._initialized = False
