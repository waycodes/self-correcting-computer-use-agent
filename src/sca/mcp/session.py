"""MCP capability negotiation and server feature discovery."""

from dataclasses import dataclass, field
from typing import Any

from sca.mcp.messages import MCPMethod
from sca.mcp.transport import MCPClient


@dataclass
class ServerCapabilities:
    """Capabilities reported by an MCP server."""

    tools: bool = False
    resources: bool = False
    prompts: bool = False
    logging: bool = False
    experimental: dict[str, Any] = field(default_factory=dict)


@dataclass
class ClientCapabilities:
    """Capabilities supported by this client."""

    roots: bool = False
    sampling: bool = False
    experimental: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        caps: dict[str, Any] = {}
        if self.roots:
            caps["roots"] = {"listChanged": True}
        if self.sampling:
            caps["sampling"] = {}
        if self.experimental:
            caps["experimental"] = self.experimental
        return caps


@dataclass
class ServerInfo:
    """Information about an MCP server."""

    name: str
    version: str
    capabilities: ServerCapabilities


class MCPSession:
    """MCP session with capability negotiation."""

    def __init__(self, client: MCPClient) -> None:
        """Initialize MCP session."""
        self.client = client
        self.server_info: ServerInfo | None = None
        self.initialized = False

    def initialize(
        self,
        client_info: dict[str, str] | None = None,
        capabilities: ClientCapabilities | None = None,
    ) -> ServerInfo:
        """Initialize the MCP session with capability negotiation."""
        if capabilities is None:
            capabilities = ClientCapabilities()

        params = {
            "protocolVersion": "2024-11-05",
            "capabilities": capabilities.to_dict(),
            "clientInfo": client_info or {"name": "sca", "version": "0.1.0"},
        }

        response = self.client.request(MCPMethod.INITIALIZE.value, params)

        if response.is_error:
            raise RuntimeError(f"Initialize failed: {response.error}")

        result = response.result
        server_caps = ServerCapabilities(
            tools="tools" in result.get("capabilities", {}),
            resources="resources" in result.get("capabilities", {}),
            prompts="prompts" in result.get("capabilities", {}),
            logging="logging" in result.get("capabilities", {}),
        )

        self.server_info = ServerInfo(
            name=result.get("serverInfo", {}).get("name", "unknown"),
            version=result.get("serverInfo", {}).get("version", "unknown"),
            capabilities=server_caps,
        )

        # Send initialized notification
        self.client.notify(MCPMethod.INITIALIZED.value)
        self.initialized = True

        return self.server_info

    def list_tools(self) -> list[dict[str, Any]]:
        """List available tools from the server."""
        if not self.initialized:
            raise RuntimeError("Session not initialized")

        response = self.client.request(MCPMethod.TOOLS_LIST.value)
        if response.is_error:
            raise RuntimeError(f"tools/list failed: {response.error}")

        return response.result.get("tools", [])

    def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Call a tool on the server."""
        if not self.initialized:
            raise RuntimeError("Session not initialized")

        params = {"name": name, "arguments": arguments}
        response = self.client.request(MCPMethod.TOOLS_CALL.value, params)

        if response.is_error:
            raise RuntimeError(f"tools/call failed: {response.error}")

        return response.result

    def shutdown(self) -> None:
        """Shutdown the session."""
        if self.initialized:
            self.client.request(MCPMethod.SHUTDOWN.value)
            self.initialized = False
