"""Tool schema registry with typed argument validation."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolParameter:
    """A parameter in a tool's input schema."""

    name: str
    type: str  # "string", "number", "boolean", "object", "array"
    description: str = ""
    required: bool = False
    default: Any = None


@dataclass
class ToolSchema:
    """Schema for an MCP tool."""

    name: str
    description: str
    parameters: list[ToolParameter] = field(default_factory=list)
    returns: str = "object"

    def validate_arguments(self, arguments: dict[str, Any]) -> tuple[bool, str]:
        """Validate arguments against schema."""
        # Check required parameters
        for param in self.parameters:
            if param.required and param.name not in arguments:
                return False, f"Missing required parameter: {param.name}"

        # Check types (basic validation)
        for param in self.parameters:
            if param.name in arguments:
                value = arguments[param.name]
                if not self._check_type(value, param.type):
                    msg = f"Invalid type for {param.name}: expected {param.type}"
                    return False, msg

        return True, ""

    def _check_type(self, value: Any, expected: str) -> bool:
        """Check if value matches expected type."""
        type_map = {
            "string": str,
            "number": (int, float),
            "boolean": bool,
            "object": dict,
            "array": list,
        }
        expected_type = type_map.get(expected)
        if expected_type is None:
            return True  # Unknown type, allow
        return isinstance(value, expected_type)


class ToolRegistry:
    """Registry of available MCP tools."""

    def __init__(self) -> None:
        """Initialize tool registry."""
        self._tools: dict[str, ToolSchema] = {}

    def register(self, schema: ToolSchema) -> None:
        """Register a tool schema."""
        self._tools[schema.name] = schema

    def get(self, name: str) -> ToolSchema | None:
        """Get a tool schema by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        """List all registered tool names."""
        return list(self._tools.keys())

    def validate_call(
        self, name: str, arguments: dict[str, Any]
    ) -> tuple[bool, str]:
        """Validate a tool call."""
        schema = self.get(name)
        if schema is None:
            return False, f"Unknown tool: {name}"
        return schema.validate_arguments(arguments)

    def load_from_mcp(self, tools: list[dict[str, Any]]) -> None:
        """Load tool schemas from MCP tools/list response."""
        for tool in tools:
            params = []
            input_schema = tool.get("inputSchema", {})
            properties = input_schema.get("properties", {})
            required = input_schema.get("required", [])

            for name, prop in properties.items():
                params.append(
                    ToolParameter(
                        name=name,
                        type=prop.get("type", "string"),
                        description=prop.get("description", ""),
                        required=name in required,
                    )
                )

            schema = ToolSchema(
                name=tool["name"],
                description=tool.get("description", ""),
                parameters=params,
            )
            self.register(schema)
