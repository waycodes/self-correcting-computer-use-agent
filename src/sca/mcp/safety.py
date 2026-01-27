"""MCP safety gates: consent hooks, allowlist, and log redaction."""

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SafetyConfig:
    """Configuration for MCP safety gates."""

    # Tool allowlist (empty = allow all)
    allowed_tools: set[str] = field(default_factory=set)

    # Patterns to redact from logs
    redact_patterns: list[str] = field(
        default_factory=lambda: [
            r"password[\"']?\s*[:=]\s*[\"']?[^\"'\s]+",
            r"api[_-]?key[\"']?\s*[:=]\s*[\"']?[^\"'\s]+",
            r"secret[\"']?\s*[:=]\s*[\"']?[^\"'\s]+",
            r"token[\"']?\s*[:=]\s*[\"']?[^\"'\s]+",
        ]
    )

    # Require consent for tool calls
    require_consent: bool = False


ConsentCallback = Callable[[str, dict[str, Any]], bool]


class SafetyGate:
    """Safety gate for MCP tool calls."""

    def __init__(
        self,
        config: SafetyConfig | None = None,
        consent_callback: ConsentCallback | None = None,
    ) -> None:
        """Initialize safety gate."""
        self.config = config or SafetyConfig()
        self.consent_callback = consent_callback
        self._compiled_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.config.redact_patterns
        ]

    def check_tool_allowed(self, tool_name: str) -> tuple[bool, str]:
        """Check if a tool is allowed."""
        if not self.config.allowed_tools:
            return True, ""  # Empty allowlist = allow all

        if tool_name in self.config.allowed_tools:
            return True, ""

        return False, f"Tool '{tool_name}' not in allowlist"

    def request_consent(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> tuple[bool, str]:
        """Request consent for a tool call."""
        if not self.config.require_consent:
            return True, ""

        if self.consent_callback is None:
            return False, "Consent required but no callback configured"

        if self.consent_callback(tool_name, arguments):
            return True, ""

        return False, "User denied consent"

    def redact_for_logging(self, data: Any) -> Any:
        """Redact sensitive data for logging."""
        if isinstance(data, str):
            return self._redact_string(data)
        elif isinstance(data, dict):
            return {k: self.redact_for_logging(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.redact_for_logging(item) for item in data]
        return data

    def _redact_string(self, text: str) -> str:
        """Redact sensitive patterns from a string."""
        result = text
        for pattern in self._compiled_patterns:
            result = pattern.sub("[REDACTED]", result)
        return result

    def validate_call(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> tuple[bool, str]:
        """Validate a tool call through all safety gates."""
        # Check allowlist
        allowed, reason = self.check_tool_allowed(tool_name)
        if not allowed:
            return False, reason

        # Request consent
        consented, reason = self.request_consent(tool_name, arguments)
        if not consented:
            return False, reason

        return True, ""
