"""Coverage of proxyrank intervals when trials are grouped by condition.

    uv run python experiments/coverage.py [reps]

Generative model, logit scale: policy i under condition c succeeds with
probability sigmoid(theta_i + u_c + v_ic), with u_c ~ N(0, s) shared by all
policies and v_ic ~ N(0, s / 2) a policy-by-condition interaction. The target is
the agreement between a fixed proxy and the *population* rates (the average over
conditions). Each replicate draws G new conditions and m trials per condition,
then checks whether the 95% interval contains the true score.
"""

from __future__ import annotations

import sys

import numpy as np

import proxyrank as pr

N, G, M = 6, 5, 10
THETA = np.array([-0.9, -0.5, -0.2, 0.2, 0.5, 0.9])
SPREADS = [0.0, 0.5, 1.0, 1.5, 2.0]
METRICS = ["pearson", "spearman", "mmrv"]


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def population_rates(s, rng, n_cond=200_000):
    u = rng.normal(0, s, n_cond)[:, None]
    v = rng.normal(0, s / 2, (n_cond, N))
    return sigmoid(THETA + u + v).mean(0)


def one_rep(proxy, s, rng):
    u = rng.normal(0, s, G)[None, :]
    v = rng.normal(0, s / 2, (N, G))
    k = rng.binomial(M, sigmoid(THETA[:, None] + u + v))
    return k


def main(reps=300):
    rng = np.random.default_rng(1)
    print(f"N={N} policies, G={G} conditions x m={M} trials, {reps} replicates, nominal 95%\n")
    print("| condition spread s | metric | coverage, pooled binomial | coverage, by condition |")
    print("|---|---|---|---|")
    for s in SPREADS:
        p_pop = population_rates(s, rng)
        # proxy: the population rates seen through a fixed, imperfect simulator
        proxy = sigmoid(np.log(p_pop / (1 - p_pop)) + np.array([0.4, -0.3, 0.5, -0.4, 0.2, -0.2]))
        truth = {m: float(pr.METRICS[m](proxy, p_pop)) for m in METRICS}
        hits = {m: [0, 0] for m in METRICS}
        for r in range(reps):
            k = one_rep(proxy, s, rng)
            for m in METRICS:
                for j, grouped in enumerate((False, True)):
                    kk, nn = (k, np.full_like(k, M)) if grouped else (k.sum(1), np.full(N, G * M))
                    res = pr.validate(proxy, kk, nn, metric=m, draws=2000, seed=r, by_condition=grouped)
                    lo, hi = res.interval
                    hits[m][j] += lo - 1e-9 <= truth[m] <= hi + 1e-9
        for m in METRICS:
            print(f"| {s} | {m} | {hits[m][0] / reps:.2f} | {hits[m][1] / reps:.2f} |")
        sys.stdout.flush()


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 300)
