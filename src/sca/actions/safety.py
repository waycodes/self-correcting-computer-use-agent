"""Action safety filter to deny unsafe operations."""

from dataclasses import dataclass

from sca.actions.gui import GUIAction, HotkeyAction, TypeAction


@dataclass
class SafetyResult:
    """Result of safety check."""

    allowed: bool
    reason: str = ""


# Dangerous hotkey combinations
BLOCKED_HOTKEYS: set[tuple[str, ...]] = {
    ("alt", "f4"),  # Close window
    ("ctrl", "alt", "delete"),  # System interrupt
    ("super", "l"),  # Lock screen
    ("ctrl", "shift", "escape"),  # Task manager
}

# Dangerous text patterns (commands that could be typed into terminal)
BLOCKED_TEXT_PATTERNS: list[str] = [
    "rm -rf",
    "sudo rm",
    "mkfs",
    "dd if=",
    ":(){:|:&};:",  # Fork bomb
    "chmod 777 /",
    "shutdown",
    "reboot",
    "halt",
]


class ActionSafetyFilter:
    """Filter to block unsafe actions."""

    def __init__(
        self,
        block_hotkeys: bool = True,
        block_dangerous_text: bool = True,
        custom_blocked_patterns: list[str] | None = None,
    ) -> None:
        """Initialize safety filter."""
        self.block_hotkeys = block_hotkeys
        self.block_dangerous_text = block_dangerous_text
        self.blocked_patterns = list(BLOCKED_TEXT_PATTERNS)
        if custom_blocked_patterns:
            self.blocked_patterns.extend(custom_blocked_patterns)

    def check(self, action: GUIAction) -> SafetyResult:
        """Check if action is safe to execute."""
        if isinstance(action, HotkeyAction):
            return self._check_hotkey(action)
        elif isinstance(action, TypeAction):
            return self._check_type(action)
        return SafetyResult(allowed=True)

    def _check_hotkey(self, action: HotkeyAction) -> SafetyResult:
        """Check if hotkey is safe."""
        if not self.block_hotkeys:
            return SafetyResult(allowed=True)

        keys = tuple(k.lower() for k in action.keys)
        if keys in BLOCKED_HOTKEYS:
            return SafetyResult(
                allowed=False, reason=f"Blocked hotkey: {'+'.join(keys)}"
            )
        return SafetyResult(allowed=True)

    def _check_type(self, action: TypeAction) -> SafetyResult:
        """Check if typed text is safe."""
        if not self.block_dangerous_text:
            return SafetyResult(allowed=True)

        text_lower = action.text.lower()
        for pattern in self.blocked_patterns:
            if pattern.lower() in text_lower:
                return SafetyResult(
                    allowed=False, reason=f"Blocked text pattern: {pattern}"
                )
        return SafetyResult(allowed=True)

    def filter_action(self, action: GUIAction) -> GUIAction | None:
        """Filter action, returning None if blocked."""
        result = self.check(action)
        return action if result.allowed else None
