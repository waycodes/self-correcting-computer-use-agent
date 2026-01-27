"""Allow running as python -m sca.cli."""

from sca.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
