# End-to-End Walkthrough

This guide walks through the complete workflow: environment setup, baseline evaluation, model training, and result reproduction. Each step includes the reasoning behind the approach.

## Prerequisites

- Python 3.10+
- 16GB RAM minimum (32GB recommended for training)
- Docker (for containerized OSWorld) or VMware/VirtualBox (for local VM)
- GPU with 24GB VRAM for training (optional for evaluation-only)

## Step 1: Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/waycodes/self-correcting-computer-use-agent.git
cd self-correcting-computer-use-agent
```

We use `uv` for fast, reproducible dependency resolution:

```bash
# Install uv if not present
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

**Why uv?** It resolves dependencies deterministically and caches aggressively, making environment setup 10-100x faster than pip.

Verify the installation:

```bash
sca --help
sca doctor
```

The `doctor` command checks for required dependencies (Python version, optional GPU libraries, OSWorld availability) and reports any issues.

## Step 2: Environment Setup

The agent requires a desktop environment to interact with. Choose one option:

### Option A: Docker (Recommended for Quick Start)

Docker provides an isolated, reproducible environment without VM configuration:

```bash
./scripts/osworld_smoke_docker.sh
```

This script:
1. Pulls the OSWorld Docker image with pre-configured Ubuntu desktop
2. Starts the container with VNC access
3. Runs a smoke test to verify connectivity

**Why Docker?** Eliminates host OS differences, provides consistent screenshots, and allows parallel evaluation across multiple containers.

### Option B: Local VM (Required for Full Benchmark)

For the complete OSWorld benchmark with all 369 tasks, use a local VM:

```bash
# See detailed instructions
cat docs/setup/osworld-local.md
```

The local VM setup requires:
1. VMware Workstation/Fusion or VirtualBox
2. Ubuntu 22.04 ISO
3. Specific display resolution (1920x1080) for consistent screenshots

**Why local VM?** Some OSWorld tasks require specific application states that Docker cannot persist. The full benchmark assumes a VM with pre-installed applications.

## Step 3: Run Smoke Tests

Before running the full benchmark, verify the setup with smoke tests:

```bash
# Unit tests (no environment required)
pytest -q

# Smoke evaluation (requires Docker or VM)
sca eval --benchmark osworld --tasks smoke --output reports/smoke.json
```

The smoke suite contains 5 representative tasks that exercise:
- Basic GUI interactions (click, type, scroll)
- Multi-step workflows
- Error recovery scenarios

**Why smoke tests?** They catch configuration issues in minutes rather than hours, and provide a quick feedback loop during development.

## Step 4: Baseline Evaluation

Run the baseline (untrained) agent on the benchmark:

```bash
sca eval \
  --benchmark osworld \
  --max-steps 30 \
  --output reports/baseline.json
```

Parameters explained:
- `--benchmark osworld`: Use the OSWorld task suite
- `--max-steps 30`: Limit each task to 30 actions (prevents infinite loops)
- `--output`: Save results for later comparison

The evaluation produces:
- `reports/baseline.json`: Structured metrics (success rate, steps, timing)
- `trajectories/baseline/`: Per-task logs with screenshots and actions

**Expected baseline performance:** 5-15% success rate. The untrained agent lacks task-specific knowledge and recovery strategies.

### OSWorld-MCP Evaluation

To evaluate with MCP tool access:

```bash
sca eval \
  --benchmark osworld-mcp \
  --max-steps 30 \
  --output reports/baseline_mcp.json
```

This enables the agent to invoke command-line tools (grep, find, jq) alongside GUI actions. Tasks where tools provide advantage (file search, batch operations) should show improved success rates.

## Step 5: Collect Training Data

Training requires trajectories from successful task completions. Options:

### Option A: Use Pre-collected Trajectories

Download expert trajectories:

```bash
# Download from release artifacts
wget https://github.com/waycodes/self-correcting-computer-use-agent/releases/download/v1.0/trajectories.tar.gz
tar -xzf trajectories.tar.gz -C data/
```

### Option B: Collect Your Own

Run the agent with human oversight to collect successful trajectories:

```bash
sca collect \
  --benchmark osworld \
  --output trajectories/expert/ \
  --interactive
```

The `--interactive` flag pauses after each action for human verification, allowing correction of mistakes before they propagate.

## Step 6: Supervised Fine-Tuning (SFT)

Convert trajectories to training format:

```bash
python -m sca.training.dataset \
  --input trajectories/expert/ \
  --output data/sft/ \
  --format chat
```

This creates conversation-format examples where:
- Input: screenshot + task description + action history
- Output: next action (GUI command or tool invocation)

Train the model:

```bash
python -m sca.training.sft \
  --model Qwen/Qwen2-VL-2B-Instruct \
  --data data/sft/ \
  --output checkpoints/sft/ \
  --lora-rank 16 \
  --epochs 3 \
  --batch-size 4
```

Parameters explained:
- `--model`: Base vision-language model (Qwen2-VL supports interleaved image-text)
- `--lora-rank 16`: Low-rank adaptation reduces memory from 48GB to 24GB
- `--epochs 3`: Sufficient for convergence on ~1000 trajectories

**Why SFT first?** It provides a strong initialization for RL by teaching the model the action space and basic task patterns. RL from scratch is sample-inefficient.

Training time: ~2 hours on A100 for 1000 trajectories.

## Step 7: SCoRe Reinforcement Learning (Optional)

SCoRe (Self-Correction via Reinforcement Learning) improves recovery behavior through multi-turn RL.

Generate RL training data with failure injection:

```bash
python -m sca.training.score_data \
  --input trajectories/expert/ \
  --output data/rl/ \
  --inject-failures
```

This creates paired examples:
1. Original successful trajectory
2. Same trajectory with injected failure + recovery attempt

Train with RL:

```bash
python -m sca.training.rl_trainer \
  --model checkpoints/sft/final/ \
  --data data/rl/ \
  --output checkpoints/rl/ \
  --kl-coef 0.1 \
  --recovery-bonus 5.0
```

The reward function:
- `+10` for task success
- `-1` for task failure
- `-0.01` per step (encourages efficiency)
- `+0.5` for successful tool invocation
- `+5` for recovering from detected failure (the key SCoRe signal)

**Why SCoRe?** Standard RL optimizes for task success but doesn't explicitly reward recovery. SCoRe adds a bonus when the agent detects a failure and successfully corrects it, teaching robust self-correction.

## Step 8: Evaluate Trained Models

Compare baseline, SFT, and RL models:

```bash
# Evaluate SFT
sca eval \
  --benchmark osworld \
  --checkpoint checkpoints/sft/final/ \
  --output reports/sft.json

# Evaluate RL
sca eval \
  --benchmark osworld \
  --checkpoint checkpoints/rl/final/ \
  --output reports/rl.json
```

## Step 9: Generate Reports

Create a comparison leaderboard:

```bash
python -c "
from sca.reports import LeaderboardGenerator
from sca.metrics.schema import EvalReport

gen = LeaderboardGenerator()
gen.add_report(EvalReport.load('reports/baseline.json'), 'Baseline', 'osworld')
gen.add_report(EvalReport.load('reports/sft.json'), 'SFT', 'osworld')
gen.add_report(EvalReport.load('reports/rl.json'), 'SCoRe-RL', 'osworld')
gen.save('reports/LEADERBOARD.md')
print(gen.generate_markdown())
"
```

Generate failure analysis:

```bash
python -c "
from sca.reports import FailureReportGenerator
from sca.failures.taxonomy import FailureCategory
import json

gen = FailureReportGenerator()
# Load failures from evaluation
with open('reports/rl.json') as f:
    data = json.load(f)
for task in data['tasks']:
    if not task['success']:
        for error in task.get('errors', []):
            gen.add_failure(task['task_id'], FailureCategory.GUI_GROUNDING, error)
gen.save('reports/FAILURE_REPORT.md')
"
```

## Step 10: Reproduce Results

All evaluations are reproducible via seed and configuration:

```bash
# View config from a report
cat reports/rl.json | jq '.config'

# Re-run with identical settings
sca eval \
  --seed 42 \
  --benchmark osworld \
  --checkpoint checkpoints/rl/final/ \
  --output reports/rl_reproduced.json

# Verify identical results
diff <(jq '.aggregate' reports/rl.json) <(jq '.aggregate' reports/rl_reproduced.json)
```

**Why reproducibility matters:** Scientific claims require independent verification. Seeded evaluation ensures identical task ordering, action sampling, and environment initialization.

## Quick Reference

| Task | Command |
|------|---------|
| Verify setup | `sca doctor` |
| Run unit tests | `pytest -q` |
| Smoke evaluation | `sca eval --tasks smoke` |
| Full baseline | `sca eval --benchmark osworld` |
| Build SFT dataset | `python -m sca.training.dataset` |
| Train SFT | `python -m sca.training.sft` |
| Train RL | `python -m sca.training.rl_trainer` |
| Generate leaderboard | See Step 9 |

## Troubleshooting

### Docker container won't start
```bash
# Check Docker is running
docker ps

# Pull image manually
docker pull osworld/desktop:latest
```

### Out of GPU memory during training
```bash
# Reduce batch size
python -m sca.training.sft --batch-size 1

# Use gradient checkpointing
python -m sca.training.sft --gradient-checkpointing
```

### Evaluation hangs on a task
```bash
# Add timeout
sca eval --timeout 300  # 5 minutes per task

# Check VM/Docker connectivity
sca doctor --check-env
```

### Inconsistent results between runs
```bash
# Ensure seed is set
sca eval --seed 42

# Check for non-deterministic operations
cat reports/run.json | jq '.config.seed'
```

## Next Steps

- Explore the [MCP showcase](../src/sca/demos/mcp_showcase.py) for tasks where tools outperform GUI
- Run [failure injection demos](../src/sca/demos/failure_injection.py) to test recovery behavior
- Extend the [failure taxonomy](../src/sca/failures/taxonomy.py) with new failure categories
- Add custom tasks to the [smoke suite](../src/sca/metrics/smoke_suite.py)
