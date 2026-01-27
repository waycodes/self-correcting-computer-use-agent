# Self-Correcting Computer-Use Agent

A multimodal agent that performs real desktop workflows and learns to recover from failures using multi-turn RL and structured self-correction, evaluated on OSWorld and OSWorld-MCP.

## Executive Summary

Build an agent that operates a real desktop environment and learns robust recovery behaviors via multi-turn RL, evaluated on OSWorld and OSWorld-MCP. This directly targets "real-world actions" and "self-course-correct" with modern benchmarks and tool standards.

## Goals

- Integrate OSWorld environment execution and evaluation
- Add MCP tool invocation and measure tool-use rate and success on OSWorld-MCP
- Train self-correction using SCoRe-style multi-turn online RL (or a faithful approximation)
- Publish a failure taxonomy and recovery metrics (not just success rate)

## Non-Goals

- Building a full OS-level automation product
- Relying on closed models; use open multimodal models (or provide adapters)

---

## Design and Architecture

**Key idea:** Agent loop with observation (screenshot + accessibility tree + tool state), policy outputs (GUI action or MCP tool call), and trained reflection action for diagnosis and plan revision.

### Core Modules

- `sca/envs/osworld/` - OSWorld & OSWorld-MCP adapters, task runners, evaluation harness
- `sca/mcp/` - MCP JSON-RPC client, transports, schema registry, tool result normalization, safety gates
- `sca/agent/` - Core loop, planner, action/tool heads, reflection controller, safety filters
- `sca/actions/` - Typed action schema (GUI + tool + reflection), validators, constrained decoding helpers
- `sca/logging/` - Trajectory event log, artifact writer (screenshots/video), replay
- `sca/metrics/` - Success + efficiency + tool metrics + recovery metrics, bootstrap CIs
- `sca/training/` - SFT pipeline, SCoRe-like multi-turn RL pipeline, configs
- `demos/` - Live runs, failure injection, MCP showcase, recorder integration
- `reports/` - Generated markdown/JSON and minimal leaderboard renderer

### Key Design Decisions

- **Policy architecture**: VisionBackbone (open VLM) + ActionHead (GUI) + ToolHead (MCP) + ReflectionHead (structured reflection tokens)
- **Reward design**: Primary task success (execution-based), shaping for fewer steps/unsafe actions/correct tool usage, self-correction reward as delta in success probability conditioned on error states
- **Standard vs SOTA**: Standard = offline imitation on successful trajectories; SOTA = multi-turn online RL for self-correction (SCoRe), optionally with GRPO-style optimization

### Engineering Constraints

- OSWorld supports Ubuntu/Windows/macOS with Docker VM hosting
- MCP spec requires explicit consent, data privacy, and tool safety gates
- Must report both tool invocation rate and tool success rate (not just task success)

---

## Implementation Plan

### Phase 0: Eval-first (1 week)

- Get OSWorld running; log full trajectories; implement replay
- Baseline: scripted or simple reactive policy; establish metrics

### Phase 1: MCP tooling (1 week)

- Implement MCP client and minimal tool set
- Run OSWorld-MCP tasks and measure tool invocation rate

### Phase 2: Failure taxonomy (4-6 days)

- Label failures automatically: navigation error, wrong app focus, tool misuse, stalled loops
- Add detectors and counter metrics

### Phase 3: Self-correction training (2-3 weeks)

- Implement SCoRe-style loop: generate attempt → detect failure → generate correction attempt → RL update on multi-turn trajectory

### Phase 4: Report + demo (1 week)

- Publish OSWorld and OSWorld-MCP improvements with confidence intervals
- Add video demos and "run your own task" interactive script

---

## Expected Timeline

**5-9 weeks** total (OSWorld engineering + reliable training loop takes real time; demos are critical).

---

## Success Criteria / Demo

- "Before and after" video where baseline fails and trained agent recovers mid-task
- Benchmark table: success rate, tool invocation rate, recovery rate, average steps on OSWorld-MCP
- Resume bullet: "Trained a self-correcting computer-use agent with multi-turn RL (SCoRe-style) on OSWorld and OSWorld-MCP; improved recovery rate and tool invocation reliability using MCP-based structured tools."

---

## References

1. [OSWorld](https://arxiv.org/abs/2404.07972) - Real computer benchmark with 369 desktop/web workflows
2. [SCoRe](https://arxiv.org/abs/2409.12917) - Multi-turn online RL for self-correction
3. [OSWorld-MCP](https://arxiv.org/abs/2510.24563) - Tool invocation benchmark with 158 validated tools
4. [MCP Spec](https://modelcontextprotocol.io/specification/2025-11-25) - JSON-RPC 2.0 standard for agent tool access
