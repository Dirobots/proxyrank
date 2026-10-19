"""Rankings from pairwise real-world comparisons, with uncertainty.

Arena-style evaluations (RoboArena) run two policies on the same task and record
which did better. ``rank_pairwise`` fits a Bradley-Terry model,
``P(i beats j) = s_i / (s_i + s_j)``, with the MM algorithm (Hunter 2004).
A tie counts as half a win for each side.

Two ways to get uncertainty:

* ``method="laplace"`` (default): a N(0, prior_sd^2) prior on log-strengths and
  draws from the Gaussian approximation at the posterior mode. The prior keeps
  unbeaten or barely played policies finite and uncertain.
* ``method="bootstrap"``: a Bayesian bootstrap over sessions (Dirichlet(1, ..., 1)
  weights on whole sessions, then a refit), for sessions holding several
  dependent comparisons. Each policy also plays one tied pseudo-game against a
  reference of strength 1. It cannot imagine outcomes that never happened, so
  with policies seen in only a few comparisons it is overconfident: on RoboArena
  subsets of 50 sessions, 13% of its 95% claims were wrong, against 6% for
  the Laplace draws (casestudies/results/roboarena.md).

``validate_pairwise`` scores a proxy against those draws, which gives the same
interval as ``validate`` when the real side is a pairwise ranking instead of
success counts.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .core import _score
from .metrics import resolve

__all__ = ["PairwiseRanking", "rank_pairwise", "validate_pairwise"]


@dataclass(frozen=True)
class PairwiseRanking:
    policies: list[str]
    strength: np.ndarray        # log-strength fitted on the unweighted data, centred
    draws: np.ndarray           # bootstrap log-strengths, (draws, P)
    level: float

    def rank_interval(self, policy: str) -> tuple[int, int]:
        """Equal-tailed interval of the policy's rank (1 = best) over the draws."""
        i = self.policies.index(policy)
        ranks = 1 + (self.draws > self.draws[:, [i]]).sum(1)
        lo, hi = np.quantile(ranks, ((1 - self.level) / 2, (1 + self.level) / 2))
        return int(lo), int(hi)

    def prob_above(self) -> np.ndarray:
        """P[i, j] = fraction of draws in which policy i is ranked above policy j."""
        return (self.draws[:, :, None] > self.draws[:, None, :]).mean(0)

    def __str__(self) -> str:
        order = np.argsort(-self.strength)
        p = self.prob_above()
        lines = [f"{'rank':>4}  {'policy':<36} {'log-strength':>12}  {'rank ' + str(round(self.level * 100)) + '%':>9}  P(above next)"]
        for r, i in enumerate(order):
            lo, hi = self.rank_interval(self.policies[i])
            nxt = f"{p[i, order[r + 1]]:.2f}" if r + 1 < len(order) else ""
            lines.append(f"{r + 1:>4}  {self.policies[i][:36]:<36} {self.strength[i]:>+12.2f}  {f'[{lo}, {hi}]':>9}  {nxt}")
        return "\n".join(lines)


def _fit(wins, games, iters):
    # wins (D, P), games (D, P, P) symmetric; returns log-strengths (D, P), mean zero
    s = np.ones(wins.shape)
    for _ in range(iters):
        denom = (games / (s[:, :, None] + s[:, None, :])).sum(-1) + 1 / (s + 1)  # + pseudo-game vs reference
        s = (wins + 0.5) / denom
        s /= np.exp(np.log(s).mean(-1, keepdims=True))
    return np.log(s) - np.log(s).mean(-1, keepdims=True)


def _laplace(ia, ib, y, p, prior_sd, draws, rng, iters=50):
    # Newton on the penalized log-likelihood, then Gaussian draws at the mode
    theta = np.zeros(p)
    x = np.zeros((len(y), p))
    x[np.arange(len(y)), ia] = 1
    x[np.arange(len(y)), ib] -= 1
    for _ in range(iters):
        q = 1 / (1 + np.exp(-(x @ theta)))
        grad = x.T @ (y - q) - theta / prior_sd**2
        hess = (x.T * (q * (1 - q))) @ x + np.eye(p) / prior_sd**2
        step = np.linalg.solve(hess, grad)
        theta += step
        if np.abs(step).max() < 1e-10:
            break
    q = 1 / (1 + np.exp(-(x @ theta)))
    cov = np.linalg.inv((x.T * (q * (1 - q))) @ x + np.eye(p) / prior_sd**2)
    sample = rng.multivariate_normal(theta, cov, size=draws, method="cholesky")
    centre = lambda v: v - v.mean(-1, keepdims=True)
    return centre(theta), centre(sample)


def rank_pairwise(a, b, outcome, *, sessions=None, method="laplace", prior_sd=1.0, draws=1000,
                  level=0.95, iters=300, seed=0) -> PairwiseRanking:
    """Bradley-Terry ranking from comparisons ``a`` vs ``b``.

    Args:
        a, b: policy names of each comparison.
        outcome: 1 if ``a`` did better, 0 if ``b`` did, 0.5 for a tie.
        sessions: optional session id per comparison; the bootstrap resamples
            sessions, so comparisons from one session stay together.
        method: "laplace" or "bootstrap" (see the module docstring).
        prior_sd: standard deviation of the log-strength prior ("laplace" only).
    """
    a, b = np.asarray(a, dtype=object), np.asarray(b, dtype=object)
    y = np.asarray(outcome, dtype=float)
    if not (a.shape == b.shape == y.shape) or np.any((y < 0) | (y > 1)):
        raise ValueError("a, b and outcome must have one entry per comparison, outcome in [0, 1]")
    policies = sorted(set(a) | set(b))
    ia = np.array([policies.index(x) for x in a])
    ib = np.array([policies.index(x) for x in b])
    if method not in ("laplace", "bootstrap"):
        raise ValueError("method must be 'laplace' or 'bootstrap'")
    if method == "laplace":
        theta, sample = _laplace(ia, ib, y, len(policies), prior_sd, draws, np.random.default_rng(seed))
        return PairwiseRanking(policies=policies, strength=theta, draws=sample, level=level)
    sess = np.arange(len(y)) if sessions is None else np.unique(np.asarray(sessions), return_inverse=True)[1]
    rng = np.random.default_rng(seed)
    p = len(policies)
    w = np.vstack([np.ones(sess.max() + 1), rng.dirichlet(np.ones(sess.max() + 1), size=draws) * (sess.max() + 1)])
    wc = w[:, sess]                                   # (D + 1, C) weight of every comparison
    wins = np.zeros((len(w), p))
    np.add.at(wins.T, ia, (wc * y).T)
    np.add.at(wins.T, ib, (wc * (1 - y)).T)
    games = np.zeros((len(w), p, p))
    np.add.at(games.transpose(1, 2, 0), (ia, ib), wc.T)
    games = games + games.transpose(0, 2, 1)
    logs = _fit(wins, games, iters)
    return PairwiseRanking(policies=policies, strength=logs[0], draws=logs[1:], level=level)


def validate_pairwise(proxy: dict, ranking: PairwiseRanking, *, metric="spearman", level=0.95):
    """Agreement of proxy scores ``{policy: score}`` with the pairwise ranking.

    Returns (observed, (lo, hi)): the metric against the fitted strengths and its
    interval over the bootstrap draws. MMRV is not defined here because strengths
    are not success rates.
    """
    name, fn, _ = resolve(metric)
    if name == "mmrv":
        raise ValueError("mmrv needs success rates; use spearman, kendall or pairwise_accuracy")
    names = [x for x in ranking.policies if x in proxy]
    if len(names) < 3:
        raise ValueError("need proxy scores for at least 3 ranked policies")
    idx = [ranking.policies.index(x) for x in names]
    s = np.array([proxy[x] for x in names], dtype=float)
    obs = float(_score(fn, s[None], ranking.strength[idx][None]))
    vals = _score(fn, np.broadcast_to(s, (len(ranking.draws), 1, len(s))), ranking.draws[:, None, idx])
    return obs, tuple(float(v) for v in np.nanquantile(vals, ((1 - level) / 2, (1 + level) / 2)))
