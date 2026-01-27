"""Screenshot storage with deduplication."""

import hashlib
from pathlib import Path


class ScreenshotStore:
    """Store screenshots with hash-based deduplication."""

    def __init__(self, output_dir: Path) -> None:
        """Initialize screenshot store."""
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.hash_to_path: dict[str, Path] = {}
        self.step_to_hash: dict[int, str] = {}

    def save(self, screenshot: bytes, step: int) -> tuple[Path, bool]:
        """Save screenshot with deduplication.

        Args:
            screenshot: PNG image data
            step: Step number

        Returns:
            Tuple of (path, is_new) where is_new indicates if this was a new image
        """
        # Compute hash
        img_hash = hashlib.sha256(screenshot).hexdigest()[:16]
        self.step_to_hash[step] = img_hash

        # Check for duplicate
        if img_hash in self.hash_to_path:
            return self.hash_to_path[img_hash], False

        # Save new screenshot
        filename = f"screenshot_{step:04d}.png"
        path = self.output_dir / filename
        path.write_bytes(screenshot)
        self.hash_to_path[img_hash] = path

        return path, True

    def get_path_for_step(self, step: int) -> Path | None:
        """Get screenshot path for a step."""
        img_hash = self.step_to_hash.get(step)
        if img_hash is None:
            return None
        return self.hash_to_path.get(img_hash)

    def get_stats(self) -> dict[str, int]:
        """Get storage statistics."""
        return {
            "total_steps": len(self.step_to_hash),
            "unique_images": len(self.hash_to_path),
            "duplicates_avoided": len(self.step_to_hash) - len(self.hash_to_path),
        }
