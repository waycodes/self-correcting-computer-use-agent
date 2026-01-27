# End-to-End Walkthrough

Complete guide: setup → baseline eval → train → eval → reproduce report.

## 1. Setup

```bash
# Clone and install
git clone <repo-url>
cd self-correcting-computer-use-agent
uv pip install -e ".[dev]"

# Verify installation
sca --help
sca doctor
```

## 2. Environment Setup

### Option A: Docker (Recommended)
```bash
./scripts/osworld_smoke_docker.sh
```

### Option B: Local VM
See `docs/setup/osworld-local.md` for VMware/VirtualBox setup.

## 3. Baseline Evaluation

```bash
# Run smoke test suite
sca eval --benchmark osworld --tasks smoke

# Full evaluation (requires OSWorld environment)
sca eval --benchmark osworld --output reports/baseline.json
```

## 4. Training

### SFT Baseline
```bash
# Build dataset from trajectories
python -m sca.training.dataset --input trajectories/ --output data/sft/

# Run SFT training
python -m sca.training.sft --data data/sft/ --output checkpoints/sft/
```

### SCoRe RL (Optional)
```bash
# Generate RL training data
python -m sca.training.score_data --input trajectories/ --output data/rl/

# Run RL training
python -m sca.training.rl_trainer --data data/rl/ --output checkpoints/rl/
```

## 5. Evaluate Trained Model

```bash
# Evaluate SFT checkpoint
sca eval --benchmark osworld --checkpoint checkpoints/sft/ --output reports/sft.json

# Evaluate RL checkpoint
sca eval --benchmark osworld --checkpoint checkpoints/rl/ --output reports/rl.json
```

## 6. Generate Reports

```bash
# Generate leaderboard
python -c "
from sca.reports import LeaderboardGenerator
from sca.metrics.schema import EvalReport

gen = LeaderboardGenerator()
gen.add_report(EvalReport.load('reports/baseline.json'), 'Baseline')
gen.add_report(EvalReport.load('reports/sft.json'), 'SFT')
gen.add_report(EvalReport.load('reports/rl.json'), 'SCoRe-RL')
gen.save('reports/LEADERBOARD.md')
"
```

## 7. Reproduce Results

All runs are reproducible via seed and config:

```bash
# Check reproducibility info
cat reports/baseline.json | jq '.config'

# Re-run with same seed
sca eval --seed 42 --config reports/baseline_config.json
```

## Quick Commands Reference

| Task | Command |
|------|---------|
| Check setup | `sca doctor` |
| Run smoke tests | `sca eval --tasks smoke` |
| Full eval | `sca eval --benchmark osworld` |
| Train SFT | `python -m sca.training.sft` |
| Train RL | `python -m sca.training.rl_trainer` |
| Generate report | `python -m sca.reports.leaderboard` |
