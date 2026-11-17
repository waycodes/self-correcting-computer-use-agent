"""Regression tests for OSWorld batch aggregation validity.

These guard four defects found in the 2026-09-30 aggregation-validity audit, where
the reported success rate was not the quantity anybody thought it was. Each test is
written to fail BEHAVIORALLY against the pre-fix source rather than to fail at
import, so `getattr` shims are used for any attribute the fix introduces. A test
that errors at collection proves only that a name is missing. A test that fails on
an assertion proves the number is wrong, which is the claim being guarded.

Defect map, all observed at commit 841e328:

1. `TaskRunner.run` returned no `success` key while `BatchResult.add_result` read
   `result.get("success", False)`, pinning the reported rate at 0.0 for every
   possible input. A saturated metric is insensitive to everything upstream, which
   is why defect 2 was invisible until this one was repaired.
2. `to_summary` divided by `completed`, which only increments on the success path
   of the `try` in `BatchRunner.run`. Tasks lost to a crash, and tasks never
   reached because the batch aborted, were both excluded from the denominator
   instead of counting as failures.
3. `bootstrap_ci` returns a zero-width interval whenever the sample is all zeros
   or all ones, so the rendered leaderboard claimed total certainty exactly when
   it had the least evidence.
4. `bootstrap_ci` drew from the global `random` module, so an unseeded call both
   perturbed the caller's stream and produced a different interval on each render.

Tests 1 and 2 are ordered deliberately: 2 cannot be observed while 1 is live, and
repairing 1 alone introduces an upward bias rather than fixing the number.
"""

import random
from pathlib import Path
from typing import Any

import pytest

from sca.envs.osworld.batch import BatchResult, BatchRunner
from sca.metrics.bootstrap import bootstrap_ci
from sca.types import Action, ActionType, Observation, StepResult


class _StubEnv:
    """Minimal env adapter. Optionally raises on a chosen step to force a crash."""

    def __init__(self, succeed: bool = True, crash_on_step: int | None = None) -> None:
        self.succeed = succeed
        self.crash_on_step = crash_on_step
        self.steps = 0
        self.closed = False

    def reset(self) -> Observation:
        return Observation(screenshot=b"stub")

    def step(self, action: Action) -> StepResult:
        self.steps += 1
        if self.crash_on_step is not None and self.steps >= self.crash_on_step:
            raise RuntimeError("stub environment crash")
        return StepResult(
            observation=Observation(screenshot=b"stub"),
            reward=1.0 if self.succeed else 0.0,
            done=True,
        )

    def close(self) -> None:
        self.closed = True


def _policy(obs: Observation) -> Action:
    return Action(type=ActionType.CLICK, params={"x": 0, "y": 0})


def _result(task_id: str, **over: Any) -> dict[str, Any]:
    """A task result in the shape `TaskRunner.run` returns."""
    base: dict[str, Any] = {
        "task_id": task_id,
        "steps": 1,
        "total_reward": 1.0,
        "done": True,
        "success": True,
    }
    base.update(over)
    return base


# Defect 1: the missing success key saturated the metric at 0.0


def test_task_runner_emits_success_key(tmp_path: Path) -> None:
    """A task result must carry an explicit success verdict.

    Without this key `add_result` falls through to its `False` default, so the
    reported rate is 0.0 for every input and no upstream change can move it.
    """
    runner = BatchRunner(tmp_path / "out")
    results = runner.run(["task-a"], _policy, lambda: _StubEnv(succeed=True))

    assert results.task_results, "batch produced no task results"
    record = results.task_results[0]
    assert "success" in record, (
        "TaskRunner.run must emit an explicit 'success' key. Without it "
        "BatchResult.add_result defaults to False and pins success_rate at 0.0."
    )
    assert isinstance(record["success"], bool)


def test_successful_task_is_counted_as_success(tmp_path: Path) -> None:
    """A task the environment terminated with positive reward must not read as 0.0.

    This is the end-to-end form of defect 1: before the fix this asserted 0.0 on a
    batch where every task succeeded.
    """
    runner = BatchRunner(tmp_path / "out")
    results = runner.run(
        ["task-a", "task-b"], _policy, lambda: _StubEnv(succeed=True)
    )
    summary = results.to_summary()

    assert summary["success"] == 2, f"expected 2 successes, got {summary['success']}"
    assert summary["success_rate"] == pytest.approx(1.0), (
        "two successful tasks must report rate 1.0, not "
        f"{summary['success_rate']}"
    )


def test_unsuccessful_task_is_not_counted_as_success(tmp_path: Path) -> None:
    """The repaired success key must still be able to report failure.

    Control for the test above. A fix that hardcodes success to True would pass
    the previous assertion, so the negative direction has to be pinned too.
    """
    runner = BatchRunner(tmp_path / "out")
    results = runner.run(["task-a"], _policy, lambda: _StubEnv(succeed=False))
    summary = results.to_summary()

    assert summary["success"] == 0
    assert summary["success_rate"] == pytest.approx(0.0)


# Defect 2: the denominator excluded crashed and never-reached tasks


def test_success_rate_denominator_is_total_tasks() -> None:
    """The denominator must be every task asked for, not every task survived.

    Two of four tasks are recorded. The honest rate is 1 of 4, because a task lost
    to a crash is a task the agent did not complete. Dividing by `completed` gives
    1 of 2, which overstates the agent by 25 points here and grows with harness
    flakiness.
    """
    results = BatchResult()
    results.total_tasks = 4
    results.add_result(_result("task-a", success=True))
    results.add_result(_result("task-b", success=False))

    summary = results.to_summary()
    assert summary["completed"] == 2
    assert summary["total_tasks"] == 4
    assert summary["success_rate"] == pytest.approx(0.25), (
        "success_rate must divide by total_tasks (1/4 = 0.25), not by completed "
        f"(1/2 = 0.5). Got {summary['success_rate']}."
    )


def test_crashed_batch_does_not_inflate_rate(tmp_path: Path) -> None:
    """A mid-batch crash must not leave a flattering recoverable summary.

    `BatchRunner.run` has no `except`, so the exception propagates and the batch
    aborts. The caller can still read `runner.results`, and before the fix that
    summary divided the single completed task by 1 instead of by the 4 requested.
    """
    runner = BatchRunner(tmp_path / "out")
    built: list[_StubEnv] = []

    def factory() -> _StubEnv:
        env = _StubEnv(succeed=True, crash_on_step=1 if len(built) == 1 else None)
        built.append(env)
        return env

    with pytest.raises(RuntimeError):
        runner.run(["t1", "t2", "t3", "t4"], _policy, factory)

    summary = runner.results.to_summary()
    assert summary["total_tasks"] == 4
    assert summary["completed"] == 1
    assert all(env.closed for env in built), "the finally block must close envs"
    assert summary["success_rate"] == pytest.approx(0.25), (
        "one success out of four requested tasks is 0.25. Reporting 1.0 by "
        f"dividing by completed hides the crash. Got {summary['success_rate']}."
    )


def test_empty_batch_reports_zero_not_error() -> None:
    """Guard the degenerate denominator the original guarded, after the swap."""
    summary = BatchResult().to_summary()
    assert summary["success_rate"] == 0
    assert summary["avg_steps"] == 0


# Defect 3: zero-width intervals at the boundaries


@pytest.mark.parametrize("n", [1, 5, 8, 58])
def test_confidence_interval_is_not_zero_width_at_zero(n: int) -> None:
    """All-failure samples must not claim perfect certainty.

    Resampling a constant vector can only ever produce that constant, so the
    percentile bootstrap collapses to a point exactly at the boundaries. This is
    the case that matters, because an agent scoring 0 of n is the state the
    leaderboard is most likely to render during bring-up.
    """
    ci = bootstrap_ci([0.0] * n)
    assert ci.upper > ci.lower, (
        f"0 of {n} produced the zero-width interval "
        f"[{ci.lower}, {ci.upper}], which asserts certainty from no evidence."
    )
    assert ci.lower == pytest.approx(0.0, abs=1e-9)


@pytest.mark.parametrize("n", [1, 5, 8, 58])
def test_confidence_interval_is_not_zero_width_at_one(n: int) -> None:
    """All-success samples must not claim perfect certainty either."""
    ci = bootstrap_ci([1.0] * n)
    assert ci.upper > ci.lower, (
        f"{n} of {n} produced the zero-width interval "
        f"[{ci.lower}, {ci.upper}]."
    )
    assert ci.upper == pytest.approx(1.0, abs=1e-9)


def test_boundary_interval_narrows_as_n_grows() -> None:
    """More evidence must buy a tighter bound at the boundary.

    Non-degeneracy alone is satisfiable by returning a fixed pad, so pin the
    direction: 0 of 58 must be strictly more informative than 0 of 5.
    """
    small = bootstrap_ci([0.0] * 5)
    large = bootstrap_ci([0.0] * 58)
    assert (large.upper - large.lower) < (small.upper - small.lower), (
        f"width at n=58 ({large.upper - large.lower:.4f}) must be below width at "
        f"n=5 ({small.upper - small.lower:.4f})"
    )


def test_interval_brackets_the_mean_in_the_interior() -> None:
    """The ordinary case must keep working: the interval contains its own mean."""
    values = [1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0]
    ci = bootstrap_ci(values, seed=11)
    assert ci.mean == pytest.approx(sum(values) / len(values))
    assert ci.lower <= ci.mean <= ci.upper


# Defect 4: global RNG use made renders non-reproducible


def test_unseeded_interval_is_reproducible() -> None:
    """Two renders of one report must agree.

    `leaderboard.py` calls `bootstrap_ci(successes)` with no seed. Drawing from
    the global module made the interval depend on whatever consumed `random`
    earlier in the process, so the same report rendered twice disagreed. The
    effect grows with sample size, so n=58 is the honest test. On n=5 the pre-fix
    code can pass by luck, which is why a small sample is the wrong probe.
    """
    rng = random.Random(7)
    values = [1.0 if rng.random() < 0.48 else 0.0 for _ in range(58)]

    seen = {
        (round(bootstrap_ci(values).lower, 10), round(bootstrap_ci(values).upper, 10))
        for _ in range(8)
    }
    assert len(seen) == 1, (
        f"an unseeded render produced {len(seen)} different intervals across 8 "
        "repeats, so a published leaderboard is not reproducible"
    )


def test_bootstrap_does_not_disturb_global_rng() -> None:
    """Computing an interval must not move the caller's random stream.

    A metrics helper that reseeds or consumes the global module silently changes
    unrelated sampling downstream of it, which is the worst class of this bug
    because nothing near the call site looks wrong.
    """
    random.seed(4242)
    expected = [random.random() for _ in range(3)]

    random.seed(4242)
    bootstrap_ci([1.0, 0.0] * 20)
    after_unseeded = [random.random() for _ in range(3)]
    assert after_unseeded == pytest.approx(expected), (
        "an unseeded bootstrap_ci consumed the caller's global random stream"
    )

    random.seed(4242)
    bootstrap_ci([1.0, 0.0] * 20, seed=5)
    after_seeded = [random.random() for _ in range(3)]
    assert after_seeded == pytest.approx(expected), (
        "a seeded bootstrap_ci reseeded the global random module"
    )


def test_explicit_seed_is_deterministic() -> None:
    """An explicit seed must still pin the result exactly."""
    values = [1.0, 0.0, 1.0, 1.0, 0.0] * 6
    first = bootstrap_ci(values, seed=99)
    second = bootstrap_ci(values, seed=99)
    assert (first.lower, first.upper) == (second.lower, second.upper)

    other = bootstrap_ci(values, seed=100)
    assert isinstance(other.lower, float)
