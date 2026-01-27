# Agent Instructions

Before starting any work, run `bd onboard` to understand the current project state and available issues.

## Project Overview

Self-Correcting Computer-Use Agent - A multimodal agent that performs real desktop workflows and learns to recover from failures using multi-turn RL (SCoRe-style), evaluated on OSWorld and OSWorld-MCP.

**Key References: (YOU MUST READ THESE BEFORE STARTING WORK)**
- `docs/CONTEXT.md` - Full project overview, architecture, and implementation plan

## Issue Tracking

Use `bd` (beads) for task management:

```bash
bd ready              # List tasks with no open blockers
bd create "Title" -p 0  # Create a P0 task
bd show <id>          # View task details
bd close <id>         # Close completed task
```

**Periodically run `bd doctor`** to identify critical issues, blockers, and health problems. Fix any issues it reports before continuing work.

**DO NOT use `bd edit`** - it opens an interactive editor. Use `bd update` with flags:
```bash
bd update <id> --description "new description"
bd update <id> --status in_progress
```

## Development Guidelines

### Code Standards

- **Language/version**: Python 3.10+
- **Package manager**: uv
- **Linting**: ruff
- **Type checking**: pyright
- **Testing**: pytest

### File Organization

```
sca/
├── envs/osworld/    # OSWorld adapters, task runners, evaluation
├── mcp/             # MCP client, transports, schema registry, safety
├── agent/           # Core loop, planner, action heads, reflection
├── actions/         # Typed action schema, validators
├── logging/         # Trajectory logs, artifact writer, replay
├── metrics/         # Success/efficiency/tool/recovery metrics
├── training/        # SFT and SCoRe RL pipelines
demos/               # Live runs, failure injection, MCP showcase
reports/             # Generated benchmarks and leaderboard
tests/
```

### Testing Requirements

**Every non-trivial code change MUST have tests.** Tests must pass before committing.

If you cannot fix failing tests after reasonable effort:
1. Create an issue with `bd create "Fix failing tests for <feature>" -p 0`
2. Include in the description: what was attempted, error messages, and relevant context
3. Do NOT commit code with failing tests

### Before Committing

1. Run linter: `ruff check .`
2. Run tests: `pytest tests/` - **ALL tests must pass**
3. Run type checker: `pyright`
4. Update docs if behavior changed

## Landing the Plane (Session Completion)

**When ending a work session**, complete ALL steps:

1. **File issues for remaining work** - Create beads issues for follow-up
2. **Run quality gates** (if code changed):
   ```bash
   ruff check .
   pytest tests/ -x
   pyright
   ```
3. **Update issue status** - Close finished work
4. **PUSH TO REMOTE** - MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Verify** - All changes committed AND pushed
6. **Hand off** - Provide context for next session

**CRITICAL:** Work is NOT complete until `git push` succeeds. NEVER stop before pushing.

**WORK IS NOT DONE UNTIL ALL TASKS ARE CLOSED.** Workers must continue until every open issue (all priorities) is completed. Do not stop with open tasks remaining.

## Key Architecture Decisions

From `docs/CONTEXT.md`:

- **Policy architecture**: VisionBackbone (open VLM) + ActionHead (GUI) + ToolHead (MCP) + ReflectionHead
- **Reward design**: Task success primary, shaping for efficiency, self-correction reward as delta in success probability
- **MCP safety**: Explicit consent, data privacy, and tool safety gates required per spec

## Common Tasks

### Adding a New MCP Tool

1. Define tool schema in `sca/mcp/`
2. Implement handler with safety gates
3. Add tests for tool invocation and error cases
4. Register in schema registry

### Adding a New Failure Detector

1. Implement detector in `sca/metrics/`
2. Add to failure taxonomy
3. Add tests with example failure cases
4. Update counter metrics

## Questions?

- Check existing issues: `bd list`
- Read the docs: `docs/CONTEXT.md`
- Create an issue: `bd create "Question: ..." -t task -p 2`
