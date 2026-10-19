"""What small real evaluations say about simulator quality, against a large-sample truth.

    uv run python experiments/humanoid/analyze.py [reps] > experiments/results/g1_study.md

Truth: each simulator's agreement with the real rates measured from all 800 real
trials per policy (100 per push direction). Each replicate draws b trials per
direction and policy without replacement from that pool, as a small real
evaluation would, and asks three questions:

1. Does the naive observed metric pick the truly best simulator?
2. For every pair of simulators, naive claims (sign of the observed difference)
   versus proxyrank claims (``compare`` probability >= 0.95): how often is a
   claim wrong?
3. Do the 95% intervals of ``validate`` contain each simulator's true score?
   Independent-rate posterior with pooled trials, versus the linked posterior
   with pooled trials and with the push directions as conditions.
4. How often does the ceiling test (P(perfect proxy scores this badly) < 0.05)
   flag each simulator?
"""

from __future__ import annotations

import itertools
import os
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

import proxyrank as pr

DATA = Path(__file__).parents[1] / "results" / "g1_outcomes.npz"
BUDGETS = (1, 2, 5, 10, 25)          # trials per direction; x 8 directions per policy
METRICS = ("mmrv", "spearman", "pearson")
DRAWS = 1000
COVERAGE = (("pool_indep", False, "independent"), ("pool", False, "linked"), ("cond", True, "linked"))


def load():
    z = np.load(DATA)
    out = z["outcomes"]
    return out[0], out[1:].mean((2, 3)), list(z["worlds"][1:]), list(z["policies"])


def better(metric, a, b):
    return a > b if pr.HIGHER_IS_BETTER[metric] else a < b


def replicate(args):
    b, seed = args
    real, sims, _, _ = load()
    rng = np.random.default_rng(seed)
    p_true = real.mean((1, 2))
    pick = rng.permuted(np.tile(np.arange(real.shape[-1]), (*real.shape[:2], 1)), axis=-1)[..., :b]
    k = np.take_along_axis(real, pick, -1).sum(-1)              # (P, G)
    n_pol = b * real.shape[1]
    rec = {}
    for m in METRICS:
        truth = np.array([pr.METRICS[m](s, p_true) for s in sims])
        obs = np.array([pr.METRICS[m](s, k.sum(1) / n_pol) for s in sims])
        best = np.argmax(truth) if pr.HIGHER_IS_BETTER[m] else np.argmin(truth)
        rec[(m, "naive_best")] = float((np.argmax(obs) if pr.HIGHER_IS_BETTER[m] else np.argmin(obs)) == best)
        for tag, grouped, model in COVERAGE:
            kk, nn = (k, b) if grouped else (k.sum(1), n_pol)
            for i, s in enumerate(sims):
                v = pr.validate(s, kk, nn, metric=m, draws=DRAWS, seed=seed, by_condition=grouped, model=model)
                lo, hi = v.interval
                rec[(m, f"cover_{tag}", i)] = float(lo - 1e-9 <= truth[i] <= hi + 1e-9)
                rec[(m, f"flag_{tag}", i)] = float(v.p_vs_ceiling < 0.05)
        for grouped in (False, True):
            tag = "cond" if grouped else "pool"
            kk, nn = (k, b) if grouped else (k.sum(1), n_pol)
            claims = wrong = 0
            for i, j in itertools.combinations(range(len(sims)), 2):
                if truth[i] == truth[j]:
                    continue
                c = pr.compare(sims[i], sims[j], kk, nn, metric=m, draws=DRAWS, seed=seed, by_condition=grouped)
                if c.prob_a_better >= 0.95 or c.prob_a_better <= 0.05:
                    claims += 1
                    wrong += (c.prob_a_better >= 0.95) != better(m, truth[i], truth[j])
            rec[(m, f"claims_{tag}")] = claims
            rec[(m, f"wrong_{tag}")] = wrong
        pairs = [(i, j) for i, j in itertools.combinations(range(len(sims)), 2) if truth[i] != truth[j]]
        rec[(m, "pairs")] = len(pairs)
        rec[(m, "wrong_naive")] = sum(better(m, obs[i], obs[j]) != better(m, truth[i], truth[j])
                                      for i, j in pairs if obs[i] != obs[j])
        rec[(m, "claims_naive")] = sum(obs[i] != obs[j] for i, j in pairs)
    return b, rec


def main(reps=300):
    real, sims, names, policies = load()
    p_true = real.mean((1, 2))
    print("# G1 push recovery: simulator validation from small real evaluations\n")
    print(f"{len(policies)} balance controllers, {real.shape[1]} push directions, {real.shape[-1]} real trials per "
          f"direction and policy as the truth pool, {reps} replicates per budget, {DRAWS} posterior draws.\n")
    print("Real success rates:", " ".join(f"{x:.2f}" for x in p_true), "\n")
    print("| simulator | " + " | ".join(f"true {m}" for m in METRICS) + " |\n" + "|---" * (len(METRICS) + 1) + "|")
    for name, s in zip(names, sims):
        print(f"| {name} | " + " | ".join(f"{float(pr.METRICS[m](s, p_true)):+.3f}" for m in METRICS) + " |")
    with Pool(int(os.environ.get("WORKERS", 0)) or None) as pool:   # WORKERS caps memory on small machines
        results = pool.map(replicate, [(b, 1000 * b + r) for b in BUDGETS for r in range(reps)], chunksize=4)
    print()
    for m in METRICS:
        print(f"## {m}\n")
        print("| real trials / policy | naive picks best sim | wrong naive claims | proxyrank claims (pooled) "
              "| wrong (pooled) | proxyrank claims (by direction) | wrong (by direction) |")
        print("|---|---|---|---|---|---|---|")
        for b in BUDGETS:
            rs = [r for bb, r in results if bb == b]
            tot = lambda key: sum(r[(m, key)] for r in rs)
            rate = lambda w, c: f"{tot(w) / max(tot(c), 1):.1%}"
            print(f"| {b * real.shape[1]} | {np.mean([r[(m, 'naive_best')] for r in rs]):.2f} "
                  f"| {rate('wrong_naive', 'claims_naive')} "
                  f"| {tot('claims_pool') / tot('pairs'):.1%} | {rate('wrong_pool', 'claims_pool')} "
                  f"| {tot('claims_cond') / tot('pairs'):.1%} | {rate('wrong_cond', 'claims_cond')} |")
        print("\nInterval coverage per simulator: independent pooled / linked pooled / linked by direction. "
              "Ceiling-test flag rate (linked, pooled / by direction) in brackets.\n")
        print("| real trials / policy | " + " | ".join(names) + " |\n" + "|---" * (len(names) + 1) + "|")
        for b in BUDGETS:
            rs = [r for bb, r in results if bb == b]
            mean = lambda key, i: np.mean([r[(m, key, i)] for r in rs])
            cells = [" / ".join(f"{mean('cover_' + t, i):.2f}" for t, _, _ in COVERAGE)
                     + f" [{mean('flag_pool', i):.2f} / {mean('flag_cond', i):.2f}]" for i in range(len(names))]
            print(f"| {b * real.shape[1]} | " + " | ".join(cells) + " |")
        print()

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 300)
