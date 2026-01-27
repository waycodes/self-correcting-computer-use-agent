"""Invalid output repair fallback for action parsing."""

from typing import Any

from sca.actions.constrained import validate_action_json
from sca.types import Action, ActionType


class OutputRepair:
    """Repair invalid action outputs from models."""

    def __init__(self, max_retries: int = 3) -> None:
        """Initialize output repair."""
        self.max_retries = max_retries

    def repair(self, raw_output: str | dict[str, Any]) -> Action | None:
        """Attempt to repair invalid output into a valid action.

        Args:
            raw_output: Raw model output (string or dict)

        Returns:
            Valid Action or None if repair failed
        """
        # If string, try to parse as JSON
        if isinstance(raw_output, str):
            data = self._parse_json(raw_output)
            if data is None:
                return self._fallback_action()
        else:
            data = raw_output

        # Validate and repair
        valid, error = validate_action_json(data)
        if valid:
            return self._dict_to_action(data)

        # Try common repairs
        repaired = self._try_repairs(data, error)
        if repaired:
            return repaired

        return self._fallback_action()

    def _parse_json(self, text: str) -> dict[str, Any] | None:
        """Try to parse JSON from text."""
        import json
        import re

        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from markdown code block
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find any JSON object
        match = re.search(r"\{[^{}]*\}", text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        return None

    def _try_repairs(
        self, data: dict[str, Any], error: str
    ) -> Action | None:
        """Try common repairs for invalid data."""
        # Missing type field
        if "type" not in data:
            # Try to infer type from other fields
            if "x" in data and "y" in data:
                data["type"] = "click"
            elif "text" in data:
                data["type"] = "type"
            elif "keys" in data:
                data["type"] = "hotkey"

        # Validate again
        valid, _ = validate_action_json(data)
        if valid:
            return self._dict_to_action(data)

        return None

    def _dict_to_action(self, data: dict[str, Any]) -> Action:
        """Convert validated dict to Action."""
        action_type = ActionType(data["type"])
        params = {k: v for k, v in data.items() if k != "type"}
        return Action(type=action_type, params=params)

    def _fallback_action(self) -> Action:
        """Return a safe fallback action."""
        # Default to a no-op click at origin
        return Action.click(0, 0)
