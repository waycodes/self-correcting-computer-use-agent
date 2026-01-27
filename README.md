# Self-Correcting Computer-Use Agent

A multimodal agent that performs real desktop workflows and learns to recover from failures using multi-turn RL (SCoRe-style), evaluated on OSWorld and OSWorld-MCP.

## Installation

```bash
# Install with uv (recommended)
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

## Usage

```bash
# Show help
sca --help

# Or run as module
python -m sca.cli --help
```

## Development

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run linter
ruff check .

# Run type checker
pyright

# Run tests
pytest
```

## Project Structure

```
sca/
├── envs/osworld/    # OSWorld adapters, task runners, evaluation
├── mcp/             # MCP client, transports, schema registry, safety
├── agent/           # Core loop, planner, action heads, reflection
├── actions/         # Typed action schema, validators
├── logging/         # Trajectory logs, artifact writer, replay
├── metrics/         # Success/efficiency/tool/recovery metrics
├── training/        # SFT and SCoRe RL pipelines
```

## References

- [OSWorld](https://arxiv.org/abs/2404.07972) - Real computer benchmark
- [SCoRe](https://arxiv.org/abs/2409.12917) - Multi-turn online RL for self-correction
- [OSWorld-MCP](https://arxiv.org/abs/2510.24563) - Tool invocation benchmark
- [MCP Spec](https://modelcontextprotocol.io/specification/2025-11-25) - JSON-RPC 2.0 standard
