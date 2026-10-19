"""Coverage of validate intervals across proxy quality, trial budget and metric.

    uv run python experiments/calibration.py [reps] > experiments/results/calibration.md

Each replicate draws N true logits from N(0, SPREAD^2) and a proxy correlated
with them at RHO on the logit scale (RHO = 0: unrelated, 1: perfect), then n
real trials per policy, and checks whether the 95% interval contains the
agreement between the proxy and the true rates.
"""

from __future__ import annotations

import os
import sys
from multiprocessing import Pool

import numpy as np

import proxyrank as pr

NS = (6, 12)
SPREADS = (0.5, 1.0, 2.0)
RHOS = (0.0, 0.5, 0.9, 1.0)
BUDGETS = (8, 20, 80)
METRICS = ("spearman", "pearson", "mmrv")
MODELS = ("independent", "linked")
DRAWS = 1000


def replicate(args):
    n_pol, spread, rho, n, seed = args
    rng = np.random.default_rng(seed)
    theta = rng.normal(0, spread, n_pol)
    z = (theta - theta.mean()) / theta.std()
    proxy = rho * z + np.sqrt(1 - rho**2) * rng.normal(0, 1, n_pol)
    p = 1 / (1 + np.exp(-theta))
    k = rng.binomial(n, p)
    out = {}
    for m in METRICS:
        truth = float(pr.METRICS[m](proxy, p))
        for model in MODELS:
            lo, hi = pr.validate(proxy, k, n, metric=m, draws=DRAWS, seed=seed, model=model).interval
            out[(m, model)] = (lo - 1e-9 <= truth <= hi + 1e-9, hi - lo)
    return args[:4], out


def main(reps=200):
    grid = [(a, s, r, n) for a in NS for s in SPREADS for r in RHOS for n in BUDGETS]
    jobs = [(*g, 100_000 * i + j) for i, g in enumerate(grid) for j in range(reps)]
    with Pool(int(os.environ.get("WORKERS", 0)) or None) as pool:   # WORKERS caps memory on small machines
        res = pool.map(replicate, jobs, chunksize=8)
    print(f"# Interval calibration\n\n{reps} replicates per cell, {DRAWS} draws, nominal 95%. "
          "Each cell: coverage independent / linked, linked mean width in brackets.\n")
    for m in METRICS:
        print(f"## {m}\n\n| N | logit spread | proxy rho | " + " | ".join(f"n={n}" for n in BUDGETS) + " |")
        print("|---" * (3 + len(BUDGETS)) + "|")
        for a in NS:
            for s in SPREADS:
                for r in RHOS:
                    cells = []
                    for n in BUDGETS:
                        rs = [o for g, o in res if g == (a, s, r, n)]
                        cov = [np.mean([o[(m, md)][0] for o in rs]) for md in MODELS]
                        w = np.mean([o[(m, "linked")][1] for o in rs])
                        cells.append(f"{cov[0]:.2f} / {cov[1]:.2f} [{w:.2f}]")
                    print(f"| {a} | {s} | {r} | " + " | ".join(cells) + " |")
        print()


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 200)
