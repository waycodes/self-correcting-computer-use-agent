"""Constrained output utilities for action JSON generation."""

import json
from typing import Any

# JSON schema for GUI actions
GUI_ACTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "oneOf": [
        {
            "properties": {
                "type": {"const": "click"},
                "x": {"type": "integer", "minimum": 0},
                "y": {"type": "integer", "minimum": 0},
                "button": {"enum": ["left", "right", "middle"]},
                "clicks": {"type": "integer", "minimum": 1, "maximum": 3},
            },
            "required": ["type", "x", "y"],
        },
        {
            "properties": {
                "type": {"const": "type"},
                "text": {"type": "string"},
                "interval": {"type": "number", "minimum": 0},
            },
            "required": ["type", "text"],
        },
        {
            "properties": {
                "type": {"const": "scroll"},
                "x": {"type": "integer", "minimum": 0},
                "y": {"type": "integer", "minimum": 0},
                "direction": {"enum": ["up", "down", "left", "right"]},
                "amount": {"type": "integer", "minimum": 1},
            },
            "required": ["type", "x", "y"],
        },
        {
            "properties": {
                "type": {"const": "hotkey"},
                "keys": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["type", "keys"],
        },
        {
            "properties": {
                "type": {"const": "drag"},
                "start_x": {"type": "integer", "minimum": 0},
                "start_y": {"type": "integer", "minimum": 0},
                "end_x": {"type": "integer", "minimum": 0},
                "end_y": {"type": "integer", "minimum": 0},
                "button": {"enum": ["left", "right", "middle"]},
            },
            "required": ["type", "start_x", "start_y", "end_x", "end_y"],
        },
        {
            "properties": {"type": {"const": "done"}},
            "required": ["type"],
        },
    ],
}


def get_action_schema() -> dict[str, Any]:
    """Get JSON schema for action validation."""
    return GUI_ACTION_SCHEMA.copy()


def get_action_schema_str() -> str:
    """Get JSON schema as formatted string for prompts."""
    return json.dumps(GUI_ACTION_SCHEMA, indent=2)


def validate_action_json(data: dict[str, Any]) -> tuple[bool, str]:
    """Validate action JSON against schema (basic validation)."""
    action_type = data.get("type")
    if not action_type:
        return False, "Missing 'type' field"

    valid_types = {"click", "type", "scroll", "hotkey", "drag", "done"}
    if action_type not in valid_types:
        return False, f"Invalid type: {action_type}"

    if action_type == "click":
        if "x" not in data or "y" not in data:
            return False, "Click requires 'x' and 'y'"
    elif action_type == "type":
        if "text" not in data:
            return False, "Type requires 'text'"
    elif action_type == "scroll":
        if "x" not in data or "y" not in data:
            return False, "Scroll requires 'x' and 'y'"
    elif action_type == "hotkey":
        if "keys" not in data:
            return False, "Hotkey requires 'keys'"
    elif action_type == "drag":
        required = ["start_x", "start_y", "end_x", "end_y"]
        for field in required:
            if field not in data:
                return False, f"Drag requires '{field}'"

    return True, ""
