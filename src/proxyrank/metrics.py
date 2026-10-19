"""Agreement metrics between a proxy evaluator (simulator, world model) and real evaluation.

Every function takes ``proxy`` and ``real`` arrays whose last axis indexes policies,
so the same code scores one table or a stack of posterior draws of shape (draws, N).
"""

from __future__ import annotations

import numpy as np
from scipy.stats import rankdata

__all__ = ["mmrv", "spearman", "pearson", "kendall", "pairwise_accuracy", "METRICS", "HIGHER_IS_BETTER"]


def _as_arrays(proxy, real):
    proxy = np.asarray(proxy, dtype=float)
    real = np.asarray(real, dtype=float)
    if proxy.shape[-1] != real.shape[-1]:
        raise ValueError(f"policy axis mismatch: {proxy.shape[-1]} vs {real.shape[-1]}")
    if proxy.shape[-1] < 2:
        raise ValueError("need at least 2 policies")
    return np.broadcast_arrays(proxy, real)


def _pairwise(x):
    # x[..., i, j] = x_i - x_j
    return x[..., :, None] - x[..., None, :]


def mmrv(proxy, real):
    """Mean Maximum Rank Violation (Li et al., SIMPLER, 2024). Lower is better.

    A pair (i, j) is violated when the proxy orders it differently from the real
    evaluation; the violation costs |R_i - R_j|. Each policy keeps its worst
    violation and MMRV averages those. Uses strict ``<`` exactly as in the paper.
    """
    proxy, real = _as_arrays(proxy, real)
    violated = (proxy[..., :, None] < proxy[..., None, :]) != (real[..., :, None] < real[..., None, :])
    cost = np.abs(_pairwise(real)) * violated
    return cost.max(axis=-1).mean(axis=-1)


def pearson(proxy, real):
    """Pearson correlation of success rates. NaN when either side is constant."""
    proxy, real = _as_arrays(proxy, real)
    p = proxy - proxy.mean(axis=-1, keepdims=True)
    r = real - real.mean(axis=-1, keepdims=True)
    denom = np.sqrt((p * p).sum(-1) * (r * r).sum(-1))
    with np.errstate(invalid="ignore", divide="ignore"):
        return (p * r).sum(-1) / denom


def spearman(proxy, real):
    """Spearman rank correlation, average ranks for ties."""
    proxy, real = _as_arrays(proxy, real)
    return pearson(rankdata(proxy, axis=-1), rankdata(real, axis=-1))


def kendall(proxy, real):
    """Kendall tau-a: (concordant - discordant) / all pairs."""
    proxy, real = _as_arrays(proxy, real)
    n = proxy.shape[-1]
    s = np.sign(_pairwise(proxy)) * np.sign(_pairwise(real))
    return s.sum(axis=(-1, -2)) / (n * (n - 1))


def pairwise_accuracy(proxy, real):
    """Fraction of policy pairs, strictly ordered in the real data, that the proxy orders the same way."""
    proxy, real = _as_arrays(proxy, real)
    dr, dp = np.sign(_pairwise(real)), np.sign(_pairwise(proxy))
    ordered = dr != 0
    with np.errstate(invalid="ignore", divide="ignore"):
        return ((dr == dp) & ordered).sum(axis=(-1, -2)) / ordered.sum(axis=(-1, -2))


METRICS = {
    "mmrv": mmrv,
    "spearman": spearman,
    "pearson": pearson,
    "kendall": kendall,
    "pairwise_accuracy": pairwise_accuracy,
}
HIGHER_IS_BETTER = {"mmrv": False, "spearman": True, "pearson": True, "kendall": True, "pairwise_accuracy": True}


def resolve(metric):
    """Return (name, fn, higher_is_better) for a metric name or callable."""
    if callable(metric):
        return getattr(metric, "__name__", "custom"), metric, True
    try:
        return metric, METRICS[metric], HIGHER_IS_BETTER[metric]
    except KeyError:
        raise ValueError(f"unknown metric {metric!r}; choose from {sorted(METRICS)}") from None
