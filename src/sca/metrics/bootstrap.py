"""Bootstrap confidence intervals for metrics."""

import random
from dataclasses import dataclass

# Two-sided normal quantiles for the confidence levels the reports use. Kept as a
# table so this module needs no scipy dependency.
NORMAL_QUANTILES: dict[float, float] = {
    0.80: 1.281551566,
    0.90: 1.644853627,
    0.95: 1.959963985,
    0.98: 2.326347874,
    0.99: 2.575829304,
}

# Default stream for an unseeded call. A fixed value makes a rendered report
# reproducible, which is what a published leaderboard needs. Callers that want a
# different stream pass ``seed`` explicitly.
_STABLE_SEED = 20260930


@dataclass
class ConfidenceInterval:
    """Confidence interval for a metric."""

    mean: float
    lower: float
    upper: float
    confidence: float = 0.95


def _wilson_bounds(successes: float, n: int, z: float) -> tuple[float, float]:
    """Wilson score interval for a proportion, clamped to [0, 1].

    Used at the boundaries where the percentile bootstrap is degenerate.
    Resampling an all-zero or all-one vector can only reproduce that constant,
    so the bootstrap returns a zero-width interval exactly when the sample is
    least informative. Wilson stays finite there and narrows with n, which is
    the behaviour a reader expects from a confidence interval.
    """
    if n <= 0:
        return 0.0, 1.0

    p = successes / n
    denom = 1.0 + (z * z) / n
    center = (p + (z * z) / (2 * n)) / denom
    margin = (
        z / denom * ((p * (1 - p) / n) + (z * z) / (4 * n * n)) ** 0.5
    )
    return max(0.0, center - margin), min(1.0, center + margin)


def bootstrap_ci(
    values: list[float],
    n_bootstrap: int = 1000,
    confidence: float = 0.95,
    seed: int | None = None,
) -> ConfidenceInterval:
    """Compute bootstrap confidence interval for mean.

    Draws from a local ``random.Random`` instance rather than the global module,
    so computing an interval neither consumes nor reseeds the caller's random
    stream, and an unseeded call is reproducible across renders.

    When every value is identical the percentile bootstrap is degenerate and
    would report a zero-width interval. For a 0/1 sample the Wilson score
    interval is substituted in that case, so an all-failure or all-success
    result reports real uncertainty that narrows as the sample grows.

    Args:
        values: Sample values
        n_bootstrap: Number of bootstrap samples
        confidence: Confidence level (default 0.95)
        seed: Random seed for reproducibility

    Returns:
        ConfidenceInterval with mean and bounds
    """
    if not values:
        return ConfidenceInterval(mean=0.0, lower=0.0, upper=0.0, confidence=confidence)

    n = len(values)
    mean = sum(values) / n
    alpha = 1 - confidence
    z = NORMAL_QUANTILES.get(round(confidence, 4), 1.959963985)

    # Degenerate sample: the bootstrap cannot express any spread. Fall back to
    # Wilson when the data are binary, which is the leaderboard's only use.
    if all(value == values[0] for value in values) and set(values) <= {0.0, 1.0}:
        lower, upper = _wilson_bounds(sum(values), n, z)
        return ConfidenceInterval(
            mean=mean, lower=lower, upper=upper, confidence=confidence
        )

    rng = random.Random(seed if seed is not None else _STABLE_SEED)
    means: list[float] = []

    for _ in range(n_bootstrap):
        sample = [rng.choice(values) for _ in range(n)]
        means.append(sum(sample) / n)

    means.sort()
    lower_idx = int(n_bootstrap * alpha / 2)
    upper_idx = min(int(n_bootstrap * (1 - alpha / 2)), n_bootstrap - 1)

    return ConfidenceInterval(
        mean=mean,
        lower=means[lower_idx],
        upper=means[upper_idx],
        confidence=confidence,
    )


def success_rate_ci(
    successes: list[bool],
    n_bootstrap: int = 1000,
    confidence: float = 0.95,
    seed: int | None = None,
) -> ConfidenceInterval:
    """Compute bootstrap CI for success rate."""
    values = [1.0 if s else 0.0 for s in successes]
    return bootstrap_ci(values, n_bootstrap, confidence, seed)
