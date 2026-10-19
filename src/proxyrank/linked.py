"""Posterior of real success rates that lets the proxy inform the real rates.

``validate``'s default posterior gives every real rate its own Beta prior. That
prior treats the policies' true ordering as unrelated to the proxy, so when the
proxy is good, posterior draws scramble the order and the interval on the
agreement score sits below its true value: on the G1 study it covered a
near-perfect simulator's true Spearman in under 10% of small real evaluations.

``linked_rates`` uses a hierarchical model per task instead::

    logit p_i = a + b * z_i + e_i,    e_i ~ N(0, tau^2)

where z is the standardized proxy score. How strongly the proxy predicts reality
(b and tau) is learned from the real counts, so a proxy unrelated to the real
rates gets b near 0 or a large tau and the draws fall back to near-independent
rates. Priors: a ~ N(0, 10^2), b ~ N(0, slope_sd^2), tau ~ half-normal(tau_scale).

The binomial likelihood of each rate is approximated on the logit scale by a
normal at logit((k + 0.5) / (n + 1)). (a, b) are integrated in closed form and
tau on a grid, so the posterior is sampled exactly under that approximation.
"""

from __future__ import annotations

import numpy as np

__all__ = ["linked_rates"]


def _task(k, n, s, draws, rng, tau_scale, slope_sd):
    ph = (k + 0.5) / (n + 1)
    y = np.log(ph / (1 - ph))
    v = 1 / ((n + 1) * ph * (1 - ph))
    sd = s.std()
    z = (s - s.mean()) / sd if sd > 0 else np.zeros_like(s)
    x = np.column_stack([np.ones_like(z), z])                       # (N, 2)
    p0 = np.diag([1 / 10.0**2, 1 / slope_sd**2])
    taus = np.linspace(1e-3, 4 * tau_scale, 400)
    w = 1 / (taus[:, None] ** 2 + v)                                # (G, N)
    a = np.einsum("gn,ni,nj->gij", w, x, x) + p0
    rhs = np.einsum("gn,ni,n->gi", w, x, y)
    beta = np.linalg.solve(a, rhs[..., None])[..., 0]
    logdet = np.linalg.slogdet(a)[1]
    # log marginal likelihood of y given tau, with beta integrated out
    loglik = 0.5 * (np.log(w).sum(-1) - logdet - (w * y**2).sum(-1) + (rhs * beta).sum(-1))
    logpost = loglik - taus**2 / (2 * tau_scale**2)
    prob = np.exp(logpost - logpost.max())
    g = rng.choice(len(taus), size=draws, p=prob / prob.sum())
    chol = np.linalg.cholesky(np.linalg.inv(a))                     # (G, 2, 2)
    b = beta[g] + np.einsum("dij,dj->di", chol[g], rng.standard_normal((draws, 2)))
    mu = b @ x.T                                                    # (D, N)
    t2 = taus[g, None] ** 2
    prec = 1 / v + 1 / t2
    mean = (y / v + mu / t2) / prec
    theta = mean + rng.standard_normal(mu.shape) / np.sqrt(prec)
    return 1 / (1 + np.exp(-theta))


def linked_rates(k, n, proxy, draws, rng, *, tau_scale=1.0, slope_sd=2.0):
    """Posterior draws of real rates, shape (draws, T, N), from (T, N) counts and proxy."""
    k, n, s = (np.atleast_2d(np.asarray(x, dtype=float)) for x in (k, n, proxy))
    return np.stack([_task(k[t], n[t], s[t], draws, rng, tau_scale, slope_sd) for t in range(len(k))], 1)
