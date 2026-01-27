# Contributing

Thank you for your interest in contributing!

## Development Setup

```bash
git clone <repo-url>
cd self-correcting-computer-use-agent
uv venv && uv pip install -e ".[dev]"
pre-commit install
```

## Workflow

1. Create a branch for your changes
2. Make changes with tests
3. Run quality checks: `ruff check . && pyright src && pytest`
4. Submit a pull request

## Code Standards

- Python 3.10+
- Type hints required
- Docstrings for public APIs
- Tests for new functionality

## Pull Request Process

1. Ensure all checks pass
2. Update documentation if needed
3. Request review from maintainers
