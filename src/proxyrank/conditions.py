"""Effective trial counts for real evaluations whose trials are grouped by condition.

Real evaluations vary the scene, object, initial pose or perturbation across
trials. Trials under one condition are then correlated, and pooling them as
independent Bernoulli outcomes makes every interval too narrow. When counts are
given per condition, shape (T, N, G) with G conditions shared by all N policies
of a task, proxyrank estimates the intra-condition correlation rho of each task
with the one-way ANOVA estimator, averaged over its policies and clipped to
[0, 1], and divides successes and trials by the design effect
``1 + (m - 1) * rho`` (Kish 1965), m being the mean trials per condition.
With rho = 0 this is the pooled binomial model.
"""

from __future__ import annotations

import numpy as np


def grouped_counts(successes, trials):
    """Validate per-condition counts; returns float arrays of shape (T, N, G)."""
    k = np.asarray(successes, dtype=float)
    n = np.broadcast_to(np.asarray(trials, dtype=float), k.shape)
    if k.ndim == 2:
        k, n = k[None], n[None]
    if k.ndim != 3 or k.shape[-1] < 2:
        raise ValueError("per-condition counts need shape (N, G) or (T, N, G) with G >= 2")
    if np.any(n <= 0) or np.any(k < 0) or np.any(k > n) or np.any(k != np.round(k)):
        raise ValueError("need integer 0 <= successes <= trials and trials > 0 in every condition")
    return k, n.copy()


def icc(k, n):
    """ANOVA intra-condition correlation per task, shape (T,)."""
    g = k.shape[-1]
    p_cell = k / n
    p_pol = k.sum(-1, keepdims=True) / n.sum(-1, keepdims=True)
    m0 = (n.sum(-1) - (n**2).sum(-1) / n.sum(-1)) / (g - 1)
    msb = (n * (p_cell - p_pol) ** 2).sum(-1) / (g - 1)
    with np.errstate(invalid="ignore", divide="ignore"):
        msw = (k * (1 - p_cell)).sum(-1) / (n.sum(-1) - g)
        rho = (msb - msw) / (msb + (m0 - 1) * msw)
    # policies at 0% or 100% everywhere carry no information about rho
    ok = np.isfinite(rho)
    mean = np.where(ok, rho, 0).sum(-1) / np.maximum(ok.sum(-1), 1)
    return np.clip(mean, 0, 1)


def effective_counts(k, n):
    """Pooled counts divided by each task's design effect, plus the design effects."""
    rho = icc(k, n)
    m = n.mean(axis=(-2, -1))
    deff = 1 + (m - 1) * rho
    return k.sum(-1) / deff[:, None], n.sum(-1) / deff[:, None], deff
