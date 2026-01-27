"""JSON-RPC transport abstraction for MCP."""

import json
import subprocess
from abc import ABC, abstractmethod
from typing import Any

from sca.mcp.messages import JSONRPCRequest, JSONRPCResponse, parse_response


class Transport(ABC):
    """Abstract base for MCP transports."""

    @abstractmethod
    def send(self, message: dict[str, Any]) -> None:
        """Send a message."""

    @abstractmethod
    def receive(self) -> dict[str, Any]:
        """Receive a message."""

    @abstractmethod
    def close(self) -> None:
        """Close the transport."""


class StdioTransport(Transport):
    """Transport using stdio (stdin/stdout) to communicate with MCP server."""

    def __init__(self, command: list[str]) -> None:
        """Initialize stdio transport.

        Args:
            command: Command to start the MCP server process
        """
        self.command = command
        self.process: subprocess.Popen[bytes] | None = None

    def start(self) -> None:
        """Start the MCP server process."""
        self.process = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def send(self, message: dict[str, Any]) -> None:
        """Send a message to the server."""
        if self.process is None or self.process.stdin is None:
            raise RuntimeError("Transport not started")

        data = json.dumps(message) + "\n"
        self.process.stdin.write(data.encode())
        self.process.stdin.flush()

    def receive(self) -> dict[str, Any]:
        """Receive a message from the server."""
        if self.process is None or self.process.stdout is None:
            raise RuntimeError("Transport not started")

        line = self.process.stdout.readline()
        if not line:
            raise EOFError("Server closed connection")

        return json.loads(line.decode())

    def close(self) -> None:
        """Close the transport and terminate the server."""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None


class MCPClient:
    """MCP client for communicating with MCP servers."""

    def __init__(self, transport: Transport) -> None:
        """Initialize MCP client."""
        self.transport = transport
        self._request_id = 0

    def _next_id(self) -> int:
        """Get next request ID."""
        self._request_id += 1
        return self._request_id

    def request(
        self, method: str, params: dict[str, Any] | None = None
    ) -> JSONRPCResponse:
        """Send a request and wait for response."""
        req = JSONRPCRequest(
            method=method,
            id=self._next_id(),
            params=params or {},
        )
        self.transport.send(req.to_dict())
        response_data = self.transport.receive()
        return parse_response(response_data)

    def notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        """Send a notification (no response expected)."""
        from sca.mcp.messages import JSONRPCNotification

        notif = JSONRPCNotification(method=method, params=params or {})
        self.transport.send(notif.to_dict())

    def close(self) -> None:
        """Close the client and transport."""
        self.transport.close()
