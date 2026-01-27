"""Run manifest for reproducibility tracking."""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sca import __version__
from sca.utils.repro import SeedState, get_git_sha


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RunManifest:
    """Manifest capturing all info needed to reproduce a run."""

    run_id: str
    timestamp: str = field(default_factory=_now_iso)
    version: str = field(default_factory=lambda: __version__)
    git_sha: str | None = field(default_factory=get_git_sha)
    seed_state: SeedState | None = None
    config: dict[str, Any] = field(default_factory=dict)

    def save(self, path: Path) -> None:
        """Save manifest to JSON file."""
        data = asdict(self)
        path.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path: Path) -> "RunManifest":
        """Load manifest from JSON file."""
        data = json.loads(path.read_text())
        if data.get("seed_state"):
            data["seed_state"] = SeedState(**data["seed_state"])
        return cls(**data)
