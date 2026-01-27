# Self-Correcting Computer-Use Agent

A vision-language agent that executes desktop tasks and learns to recover from failures through multi-turn reinforcement learning. The agent operates on real desktop environments via OSWorld, combining GUI actions with MCP tool invocations, and uses SCoRe-style online RL to improve self-correction behavior.

## Key Capabilities

- Execute multi-step desktop workflows through screenshot observation and GUI actions
- Invoke MCP tools when programmatic access outperforms GUI interaction
- Detect failures (stalled progress, tool misuse, wrong window focus) and attempt recovery
- Train via supervised fine-tuning on expert trajectories or reinforcement learning with recovery rewards

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         AgentLoop                               │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ Observe  │───▶│  Decide  │───▶│   Act    │───▶│   Log    │  │
│  │(screenshot)   │ (policy) │    │(GUI/MCP) │    │(trajectory)  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│        │              │               │               │         │
│        ▼              ▼               ▼               ▼         │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ Failure  │    │ Reflect  │    │  Safety  │    │  Replay  │  │
│  │ Detector │    │  Policy  │    │  Filter  │    │  (MP4)   │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Clone and install
git clone https://github.com/waycodes/self-correcting-computer-use-agent.git
cd self-correcting-computer-use-agent
uv pip install -e ".[dev]"

# Verify installation
sca doctor

# Run smoke tests (no VM required)
pytest -q
```

For the complete setup and evaluation workflow, see the [End-to-End Walkthrough](docs/walkthrough.md).

## Project Structure

```
src/sca/
├── agent/           # AgentLoop state machine, policies (reactive, reflective)
├── actions/         # GUI action schema, reflection schema, safety filters
├── envs/osworld/    # OSWorld adapter, task runners, evaluation hooks
├── mcp/             # MCP client, JSON-RPC transport, tool registry, safety gates
├── failures/        # Failure taxonomy, detectors, recovery metrics
├── logging/         # Trajectory logs (JSONL), screenshot storage, MP4 replay
├── metrics/         # Task metrics, bootstrap CIs, smoke test suite
├── training/        # Dataset builder, SFT trainer, SCoRe RL trainer
├── reports/         # Evaluation runner, leaderboard generator
└── demos/           # Live demo runner, failure injection, MCP showcase
```

## Benchmarks

| Benchmark | Description | Metrics |
|-----------|-------------|---------|
| OSWorld | 369 real desktop tasks across 9 applications | Success rate, steps, wall time |
| OSWorld-MCP | OSWorld tasks with MCP tool availability | Tool invocation rate, tool success rate |

## Training Pipelines

### Supervised Fine-Tuning (SFT)
Train on expert trajectories using LoRA adapters:
```bash
python -m sca.training.sft --data data/sft/ --output checkpoints/sft/
```

### SCoRe Reinforcement Learning
Multi-turn RL with recovery rewards:
```bash
python -m sca.training.rl_trainer --data data/rl/ --output checkpoints/rl/
```

The reward function includes:
- Task success/failure (+10/-1)
- Per-step cost (-0.01)
- Tool success bonus (+0.5)
- Recovery bonus for correcting failures (+5)

## Documentation

- [End-to-End Walkthrough](docs/walkthrough.md) - Complete guide from setup to results
- [OSWorld Local Setup](docs/setup/osworld-local.md) - VMware/VirtualBox configuration
- [OSWorld Docker Setup](docs/setup/osworld-docker.md) - Container-based environment
- [Reproducibility](docs/reproducibility.md) - Seed management and result reproduction

## Development

```bash
# Run linter
ruff check .

# Run type checker
pyright src

# Run tests
pytest -q

# Run all checks
ruff check . && pyright src && pytest -q
```

## References

- [OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments](https://arxiv.org/abs/2404.07972)
- [Training Language Models to Self-Correct via Reinforcement Learning](https://arxiv.org/abs/2409.12917)
- [OSWorld-MCP: Tool Invocation Benchmark](https://arxiv.org/abs/2510.24563)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/2025-11-25)

## License

MIT
