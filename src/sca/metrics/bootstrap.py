"""Bootstrap confidence intervals for metrics."""

import random
from dataclasses import dataclass


@dataclass
class ConfidenceInterval:
    """Confidence interval for a metric."""

    mean: float
    lower: float
    upper: float
    confidence: float = 0.95


def bootstrap_ci(
    values: list[float],
    n_bootstrap: int = 1000,
    confidence: float = 0.95,
    seed: int | None = None,
) -> ConfidenceInterval:
    """Compute bootstrap confidence interval for mean.

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

    if seed is not None:
        random.seed(seed)

    n = len(values)
    means: list[float] = []

    for _ in range(n_bootstrap):
        sample = [random.choice(values) for _ in range(n)]
        means.append(sum(sample) / n)

    means.sort()
    alpha = 1 - confidence
    lower_idx = int(n_bootstrap * alpha / 2)
    upper_idx = int(n_bootstrap * (1 - alpha / 2))

    return ConfidenceInterval(
        mean=sum(values) / n,
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
