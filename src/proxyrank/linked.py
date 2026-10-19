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
rates. Priors: a ~ N(0, 10^2), b ~ N(0, slope_sd^2), and tau half-normal(tau_scale)
with an extra point mass p_exact at tau = 0.

Proposals for (a, b, tau) come from a normal likelihood on the logit scale,
under which (a, b) integrate in closed form and tau lives on a grid; the
binomial likelihood is linearized at the empirical logit, then again at the
first pass's posterior mean. The proposals are importance-resampled to the exact
binomial likelihood, with every logit integrated out on a per-cell grid, and
each logit is then drawn from its exact conditional on that grid. Without the
correction, cells with 0 or n successes are pulled toward 1/2, the spread of
the rates is underestimated, and MMRV intervals covered 0.80 instead of 0.95
with 12 policies and 8 trials each.
"""

from __future__ import annotations

import numpy as np

__all__ = ["linked_rates"]


U = np.linspace(-6, 6, 81)                                          # per-cell grid, in conditional sds
CHUNK = 2048                                                        # draws per grid evaluation, bounds memory


def _hyper(y, v, z, draws, rng, tau_scale, slope_sd, p_exact):
    # draws of (mean logits mu, tau^2) given normal pseudo-observations y with variances v,
    # with the log density of the pseudo-observations given each draw
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
    # half-normal prior on the grid plus a point mass p_exact at tau ~ 0: a proxy that
    # predicts the logits exactly is a real possibility, and without the point mass
    # every draw has tau > 0 and the interval falls below a perfect proxy's Pearson
    prior = np.exp(-taus**2 / (2 * tau_scale**2))
    prior *= (1 - p_exact) / prior.sum()
    prior[0] += p_exact
    logpost = loglik + np.log(prior)
    prob = np.exp(logpost - logpost.max())
    g = rng.choice(len(taus), size=draws, p=prob / prob.sum())
    chol = np.linalg.cholesky(np.linalg.inv(a))                     # (G, 2, 2)
    b = beta[g] + np.einsum("dij,dj->di", chol[g], rng.standard_normal((draws, 2)))
    mu = b @ x.T                                                    # (D, N)
    t2 = taus[g, None] ** 2
    approx = -0.5 * (np.log(t2 + v) + (y - mu) ** 2 / (t2 + v)).sum(-1)
    return mu, t2, approx


def _cells(k, n, y, v, mu, t2):
    # grid over each cell's logit, centered on its normal-approximation conditional
    prec = 1 / v + 1 / t2
    m = (y / v + mu / t2) / prec
    sd = 1 / np.sqrt(prec)
    theta = m[..., None] + sd[..., None] * U                        # (D, N, U)
    logf = (k[:, None] * theta - n[:, None] * np.logaddexp(0, theta)
            - (theta - mu[..., None]) ** 2 / (2 * t2[..., None]) - 0.5 * np.log(t2[..., None]))
    return theta, logf, np.log(sd)


def _task(k, n, s, draws, rng, tau_scale, slope_sd, p_exact):
    sd = s.std()
    z = (s - s.mean()) / sd if sd > 0 else np.zeros_like(s)
    ph = (k + 0.5) / (n + 1)
    y, v = np.log(ph / (1 - ph)), 1 / ((n + 1) * ph * (1 - ph))
    # relinearize the binomial likelihood once at a pilot posterior mean
    mu, t2, _ = _hyper(y, v, z, min(draws, CHUNK), rng, tau_scale, slope_sd, p_exact)
    theta, logf, _ = _cells(k, n, y, v, mu, t2)
    f = np.exp(logf - logf.max(-1, keepdims=True))
    t0 = ((f * theta).sum(-1) / f.sum(-1)).mean(0)
    q = 1 / (1 + np.exp(-t0))
    v = 1 / (n * q * (1 - q))
    y = t0 + (k - n * q) * v
    mu, t2, approx = _hyper(y, v, z, draws, rng, tau_scale, slope_sd, p_exact)
    # exact likelihood of (a, b, tau): each logit integrated out on its grid; the
    # importance weights then live on 3 dimensions instead of N + 3
    cell = np.empty_like(mu)
    for i in range(0, draws, CHUNK):
        _, logf, logsd = _cells(k, n, y, v, mu[i:i + CHUNK], t2[i:i + CHUNK])
        top = logf.max(-1)
        cell[i:i + CHUNK] = np.log(np.exp(logf - top[..., None]).sum(-1)) + top + logsd
    logw = cell.sum(-1) - approx
    w = np.exp(logw - logw.max())
    w /= w.sum()
    keep = rng.choice(draws, size=draws, p=w)
    # each logit from its exact conditional, by inverse CDF on the grid plus jitter within a step
    th = np.empty_like(mu)
    for i in range(0, draws, CHUNK):
        kk = keep[i:i + CHUNK]
        theta, logf, logsd = _cells(k, n, y, v, mu[kk], t2[kk])
        cdf = np.cumsum(np.exp(logf - logf.max(-1, keepdims=True)), -1)
        j = np.minimum((cdf < rng.random((*cdf.shape[:-1], 1)) * cdf[..., -1:]).sum(-1), len(U) - 1)
        jitter = (rng.random(j.shape) - 0.5) * (U[1] - U[0]) * np.exp(logsd)
        th[i:i + CHUNK] = np.take_along_axis(theta, j[..., None], -1)[..., 0] + jitter
    return 1 / (1 + np.exp(-th)), 1 / np.sum(w**2)


def linked_rates(k, n, proxy, draws, rng, *, tau_scale=1.0, slope_sd=2.0, p_exact=0.2, return_ess=False):
    """Posterior draws of real rates, shape (draws, T, N), from (T, N) counts and proxy.

    With ``return_ess``, also returns the importance-sampling effective sample
    size of each task.
    """
    k, n, s = np.broadcast_arrays(*(np.atleast_2d(np.asarray(x, dtype=float)) for x in (k, n, proxy)))
    out = [_task(k[t], n[t], s[t], draws, rng, tau_scale, slope_sd, p_exact) for t in range(len(k))]
    p = np.stack([o[0] for o in out], 1)
    return (p, np.array([o[1] for o in out])) if return_ess else p
