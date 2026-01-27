"""Reproducibility utilities for seed control and determinism."""

import os
import random
from dataclasses import dataclass


@dataclass
class SeedState:
    """Captured seed state for reproducibility."""

    global_seed: int
    python_hash_seed: str | None


def set_seed(seed: int) -> SeedState:
    """Set global random seed for reproducibility."""
    random.seed(seed)
    hash_seed = os.environ.get("PYTHONHASHSEED")
    return SeedState(global_seed=seed, python_hash_seed=hash_seed)


def get_git_sha() -> str | None:
    """Get current git commit SHA, or None if not in a git repo."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
