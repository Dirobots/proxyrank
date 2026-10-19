"""How many real trials a sim-to-real validation needs.

From pilot real counts (or guessed rates), ``plan`` simulates the validation at
several per-cell trial budgets and reports, for each budget:

* the score a perfect proxy would get (median and interval);
* how often that perfect proxy beats a random ordering at level ``alpha``;
* the fraction of policy pairs the real evaluation itself orders correctly;
* when ``proxy`` is given, how often the real data would show that proxy to be
  worse than a perfect one.

The truth is drawn from the pilot posterior, so the plan carries the pilot's
uncertainty. The last column reuses one ceiling distribution per budget instead
of re-fitting a posterior per simulated study, which slightly overstates it.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass

import numpy as np

from .core import JEFFREYS, _score
from .metrics import pairwise_accuracy, resolve

__all__ = ["plan", "Plan"]


@dataclass(frozen=True)
class Plan:
    metric: str
    alpha: float
    level: float
    rows: list[dict]

    def trials_for(self, column: str, target: float) -> int | None:
        """Smallest planned budget whose ``column`` reaches ``target``, or None."""
        for row in self.rows:
            if row[column] is not None and row[column] >= target:
                return row["trials"]
        return None

    def __str__(self) -> str:
        has_proxy = self.rows[0]["detect_imperfect"] is not None
        head = f"{'trials/cell':>11}  {'perfect-proxy ' + self.metric:>22}  {'P(beats random)':>15}  {'pairs ordered':>13}"
        if has_proxy:
            head += f"  {'P(flags proxy)':>14}"
        lines = [head]
        for r in self.rows:
            lo, hi = r["ceiling_interval"]
            line = (f"{r['trials']:>11}  {r['ceiling_median']:+.3f} [{lo:+.2f}, {hi:+.2f}]"
                    f"  {r['power_null']:>15.2f}  {r['pairs_ordered']:>13.2f}")
            if has_proxy:
                line += f"  {r['detect_imperfect']:>14.2f}"
            lines.append(line)
        return "\n".join(lines)


def _null_quantile(fn, truth, rep, higher, alpha, perms_cap, rng):
    # critical value of the random-ordering null for every simulated study
    d, t, n = truth.shape
    if t == 1 and math.factorial(n) <= perms_cap:
        perms = np.array(list(itertools.permutations(range(n))))
        null = _score(fn, truth[:, 0][:, perms][:, :, None, :], rep[:, None])
    else:
        idx = np.argsort(rng.random((d, 1000, t, n)), axis=-1)
        null = _score(fn, np.take_along_axis(np.broadcast_to(truth[:, None], idx.shape), idx, -1), rep[:, None])
    q = 1 - alpha if higher else alpha
    return np.quantile(null, q, axis=1, method="higher" if higher else "lower")


def plan(
    real_successes,
    real_trials,
    budgets=(10, 20, 50, 100, 200),
    *,
    proxy=None,
    metric="spearman",
    alpha=0.05,
    level=0.95,
    draws=2000,
    prior=JEFFREYS,
    seed=0,
    higher_is_better=None,
) -> Plan:
    """Simulate a validation of the same policies at each per-cell trial budget.

    Args:
        real_successes, real_trials: pilot counts, shape (N,) or (T, N). For guessed
            rates with no pilot, pass ``round(rate * 1000)`` of 1000.
        budgets: real trials per (task, policy) cell to simulate.
        proxy: optional proxy scores of the same shape; adds ``detect_imperfect``.
    """
    name, fn, higher = resolve(metric, higher_is_better)
    rng = np.random.default_rng(seed)
    k = np.atleast_2d(np.asarray(real_successes, dtype=float))
    n = np.broadcast_to(np.atleast_2d(np.asarray(real_trials, dtype=float)), k.shape)
    truth = rng.beta(k + prior[0], n - k + prior[1], size=(draws, *k.shape))
    q = ((1 - level) / 2, (1 + level) / 2)
    rows = []
    for b in budgets:
        rep = rng.binomial(int(b), truth) / b
        ceiling = _score(fn, truth, rep)
        crit = _null_quantile(fn, truth, rep, higher, alpha, 720, rng)
        beats = ceiling > crit if higher else ceiling < crit
        pairs = _score(pairwise_accuracy, truth, rep)
        detect = None
        if proxy is not None:
            p = np.broadcast_to(np.atleast_2d(np.asarray(proxy, dtype=float)), truth.shape)
            obs = _score(fn, p, rep)
            # flagged when the proxy scores in the worst alpha tail of the perfect proxy
            cut = np.quantile(ceiling, alpha if higher else 1 - alpha)
            detect = float(np.mean(obs < cut if higher else obs > cut))
        rows.append({
            "trials": int(b),
            "ceiling_median": float(np.nanmedian(ceiling)),
            "ceiling_interval": tuple(float(x) for x in np.nanquantile(ceiling, q)),
            "power_null": float(np.mean(beats)),
            "pairs_ordered": float(np.nanmean(pairs)),
            "detect_imperfect": detect,
        })
    return Plan(metric=name, alpha=alpha, level=level, rows=rows)
