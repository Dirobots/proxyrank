"""Uncertainty for proxy-vs-real agreement metrics.

The real side of a sim-to-real study is a handful of binomial counts, so any
agreement score computed from it is itself an estimate. This module answers
three questions about such a score:

* ``interval``: what values of the score are plausible for the *true* real rates?
* ``ceiling``: what would a proxy that ranks by the true real rates score, given
  the same real-trial budget? An observed score near the ceiling cannot be told
  apart from a perfect proxy with this data.
* ``null_p``: how often does a proxy that orders policies at random score at
  least this well?

Inputs are arrays with policies on the last axis and an optional leading task
axis; scores of multiple tasks are averaged per draw, as in SIMPLER.
"""

from __future__ import annotations

import itertools
import math
import warnings
from dataclasses import dataclass, field

import numpy as np

from .conditions import effective_counts, grouped_counts
from .linked import linked_rates
from .metrics import resolve

__all__ = ["ValidationResult", "Comparison", "validate", "compare", "posterior_rates"]

JEFFREYS = (0.5, 0.5)


def _counts(successes, trials):
    k = np.atleast_2d(np.asarray(successes, dtype=float))
    n = np.atleast_2d(np.asarray(trials, dtype=float))
    k, n = np.broadcast_arrays(k, n)
    if np.any(n <= 0) or np.any(k < 0) or np.any(k > n):
        raise ValueError("need 0 <= successes <= trials and trials > 0")
    if np.any(k != np.round(k)):
        raise ValueError("successes must be integers; convert rates with round(rate * trials)")
    return k, n


def posterior_rates(successes, trials, draws, rng, prior=JEFFREYS):
    """Draws of the true success rates under independent Beta posteriors, shape (draws, T, N)."""
    k, n = _counts(successes, trials)
    a, b = prior
    return rng.beta(k + a, n - k + b, size=(draws, *k.shape))


def _score(fn, proxy, real):
    # per-task score, then mean over tasks; nanmean so a constant task does not poison the average
    s = fn(proxy, real)
    with np.errstate(all="ignore"), warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return np.nanmean(s, axis=-1) if s.ndim and s.shape[-1] > 0 else s


def _null_draws(fn, proxy_hat, real_hat, draws, rng):
    t, n = real_hat.shape
    if t == 1 and math.factorial(n) <= 40320:
        perms = np.array(list(itertools.permutations(range(n))))
        return _score(fn, proxy_hat[0][perms][:, None, :], real_hat[None]), True
    idx = np.argsort(rng.random((draws, t, n)), axis=-1)
    shuffled = np.take_along_axis(np.broadcast_to(proxy_hat, (draws, t, n)), idx, axis=-1)
    return _score(fn, shuffled, real_hat[None]), False


def _tail(sample, observed, higher, exact=False):
    # P(sample at least as good as observed); small tolerance for float ties.
    # A Monte Carlo estimate counts the observed value as one more draw, so it is
    # never exactly 0 (Phipson & Smyth 2010); an enumerated null needs no correction.
    eps = 1e-12
    hits = np.sum(sample >= observed - eps) if higher else np.sum(sample <= observed + eps)
    return float(hits / sample.size if exact else (hits + 1) / (sample.size + 1))


@dataclass(frozen=True)
class ValidationResult:
    metric: str
    higher_is_better: bool
    level: float
    observed: float
    interval: tuple[float, float]
    ceiling_mean: float
    ceiling_interval: tuple[float, float]
    p_vs_ceiling: float
    null_p: float
    null_exact: bool
    n_policies: int
    n_tasks: int
    draws: dict = field(repr=False, compare=False, default_factory=dict)

    @property
    def distinguishable_from_perfect(self) -> bool:
        """True when a perfect proxy would rarely score as badly as the observed proxy."""
        return self.p_vs_ceiling < 1 - self.level

    @property
    def better_than_random(self) -> bool:
        return self.null_p < 1 - self.level

    def __str__(self) -> str:
        pct = f"{100 * self.level:.0f}%"
        lo, hi = self.interval
        clo, chi = self.ceiling_interval
        exact = "exact" if self.null_exact else "Monte Carlo"
        return "\n".join(
            [
                f"{self.metric} over {self.n_policies} policies x {self.n_tasks} task(s)",
                f"  observed            {self.observed:+.3f}",
                f"  {pct} interval        [{lo:+.3f}, {hi:+.3f}]",
                f"  perfect-proxy ceil  {self.ceiling_mean:+.3f}  [{clo:+.3f}, {chi:+.3f}]",
                f"  P(perfect proxy scores this badly or worse) = {self.p_vs_ceiling:.3f}",
                f"  P(random ordering scores this well or better) = {self.null_p:.3f} ({exact})",
            ]
        )


def validate(
    proxy,
    real_successes,
    real_trials,
    *,
    proxy_successes=None,
    proxy_trials=None,
    metric="spearman",
    level=0.95,
    draws=20_000,
    prior=JEFFREYS,
    seed=0,
    higher_is_better=None,
    by_condition=False,
    model="linked",
) -> ValidationResult:
    """Score a proxy evaluator against real evaluation, with uncertainty.

    Args:
        proxy: proxy success rates (or any score where higher means better),
            shape (N,) or (T, N). Ignored for draws when proxy counts are given.
        real_successes, real_trials: real-world counts, same shape as ``proxy``.
        proxy_successes, proxy_trials: optional proxy counts; when given, proxy
            rates are also drawn from their posterior. Leave unset when the
            proxy runs thousands of episodes and its noise is negligible.
        metric: one of ``proxyrank.METRICS`` or a callable ``f(proxy, real)``
            that works on the last axis.
        level: credibility level of the reported intervals.
        draws: posterior / Monte Carlo draws.
        prior: Beta prior on every success rate (default Jeffreys).
        seed: RNG seed; results are deterministic given it.
        higher_is_better: direction of a callable metric (default True);
            must match the built-in direction when ``metric`` is a name.
        by_condition: real counts carry a trailing condition axis, shape
            (N, G) or (T, N, G), with the same G conditions for every policy of
            a task. The target becomes the rate over the population of
            conditions, through a design effect; see ``proxyrank.conditions``.
        model: posterior of the real rates. "linked" (default) lets the real
            data decide how far the proxy predicts them; "independent" gives
            each rate its own ``prior``, which biases the interval low for
            good proxies. See ``proxyrank.linked``.
    """
    name, fn, higher = resolve(metric, higher_is_better)
    if model not in ("linked", "independent"):
        raise ValueError("model must be 'linked' or 'independent'")
    rng = np.random.default_rng(seed)
    deff = None
    if by_condition:
        k, n, deff = effective_counts(*grouped_counts(real_successes, real_trials))
    else:
        k, n = _counts(real_successes, real_trials)
    proxy_hat = np.atleast_2d(np.asarray(proxy, dtype=float))
    if proxy_hat.shape != k.shape:
        raise ValueError(f"proxy shape {proxy_hat.shape} != real shape {k.shape}")
    real_hat = k / n
    q = ((1 - level) / 2, (1 + level) / 2)

    observed = float(_score(fn, proxy_hat, real_hat))

    if model == "linked":
        p_real = linked_rates(k, n, proxy_hat, draws, rng)
    else:
        p_real = rng.beta(k + prior[0], n - k + prior[1], size=(draws, *k.shape))
    if proxy_successes is not None:
        p_proxy = posterior_rates(proxy_successes, proxy_trials, draws, rng, prior)
    else:
        p_proxy = np.broadcast_to(proxy_hat, p_real.shape)
    true_score = _score(fn, p_proxy, p_real)

    # Perfect proxy: its scores are the true real rates; the real side is re-sampled
    # with the same trial budget. Uses posterior draws so the truth is not taken as known.
    # effective counts can be fractional; the replicate uses the nearest whole budget
    n_rep = np.maximum(np.round(n), 1)
    real_rep = rng.binomial(n_rep.astype(int), p_real) / n_rep
    ceiling = _score(fn, p_real, real_rep)

    null, exact = _null_draws(fn, proxy_hat, real_hat, draws, rng)

    return ValidationResult(
        metric=name,
        higher_is_better=higher,
        level=level,
        observed=observed,
        interval=tuple(float(x) for x in np.nanquantile(true_score, q)),
        ceiling_mean=float(np.nanmean(ceiling)),
        ceiling_interval=tuple(float(x) for x in np.nanquantile(ceiling, q)),
        # how often a perfect proxy scores no better than the observed proxy
        p_vs_ceiling=_tail(ceiling, observed, not higher),
        null_p=_tail(null, observed, higher, exact),
        null_exact=exact,
        n_policies=k.shape[-1],
        n_tasks=k.shape[0],
        draws={"true": true_score, "ceiling": ceiling, "null": null},
    )


@dataclass(frozen=True)
class Comparison:
    metric: str
    level: float
    observed_diff: float
    interval: tuple[float, float]
    prob_a_better: float

    def __str__(self) -> str:
        lo, hi = self.interval
        return (
            f"{self.metric}: A - B = {self.observed_diff:+.3f}  "
            f"{100 * self.level:.0f}% interval [{lo:+.3f}, {hi:+.3f}]  P(A better) = {self.prob_a_better:.3f}"
        )


def compare(
    proxy_a,
    proxy_b,
    real_successes,
    real_trials,
    *,
    metric="spearman",
    level=0.95,
    draws=20_000,
    prior=JEFFREYS,
    seed=0,
    higher_is_better=None,
    by_condition=False,
) -> Comparison:
    """Compare two proxies scored against the *same* real evaluation.

    Both proxies are scored on shared posterior draws of the real rates, so the
    real-side noise they have in common cancels in the difference.
    """
    name, fn, higher = resolve(metric, higher_is_better)
    rng = np.random.default_rng(seed)
    if by_condition:
        k, n, _ = effective_counts(*grouped_counts(real_successes, real_trials))
    else:
        k, n = _counts(real_successes, real_trials)
    a = np.atleast_2d(np.asarray(proxy_a, dtype=float))
    b = np.atleast_2d(np.asarray(proxy_b, dtype=float))
    if a.shape != k.shape or b.shape != k.shape:
        raise ValueError("proxy_a, proxy_b and real counts must share a shape")
    p = rng.beta(k + prior[0], n - k + prior[1], size=(draws, *k.shape))
    diff = _score(fn, np.broadcast_to(a, p.shape), p) - _score(fn, np.broadcast_to(b, p.shape), p)
    observed = float(_score(fn, a, k / n) - _score(fn, b, k / n))
    q = ((1 - level) / 2, (1 + level) / 2)
    better = np.mean(diff > 0) if higher else np.mean(diff < 0)
    return Comparison(
        metric=name,
        level=level,
        observed_diff=observed,
        interval=tuple(float(x) for x in np.nanquantile(diff, q)),
        prob_a_better=float(better),
    )
