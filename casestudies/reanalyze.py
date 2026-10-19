"""Reanalysis of published sim-to-real validation tables with proxyrank.

    uv run python casestudies/reanalyze.py > casestudies/results.md

Sources (numbers transcribed in casestudies/data, see headers there):
  SIMPLER   Li et al. 2024, arXiv:2405.05941, Tables IV-V
  Recipe    "A Practical Recipe Towards Improving Sim-and-Real Correlation for VLA
            Evaluation", arXiv:2606.10366, Tables 1-2 (rankings only)
"""

from __future__ import annotations

import csv
import itertools
from pathlib import Path

import numpy as np

import proxyrank as pr

DATA = Path(__file__).parent / "data"
DRAWS = 20_000


def load(name):
    with open(DATA / name) as f:
        rows = list(csv.DictReader(line for line in f if not line.startswith("#")))
    tasks = {}
    for r in rows:
        tasks.setdefault(r["task"], []).append(r)
    return tasks


def counts(rows):
    n = np.array([int(r["real_trials"]) for r in rows])
    rate = np.array([float(r["real_rate"]) for r in rows])
    k = np.round(rate * n)
    # the transcribed rate must be k/n rounded to 3 decimals, else n is wrong
    assert np.allclose(np.round(k / n, 3), rate, atol=1.1e-3), (rows[0]["task"], k / n, rate)
    return k, n


def fmt(res):
    lo, hi = res.interval
    clo, chi = res.ceiling_interval
    return (
        f"{res.observed:.3f} | [{lo:.3f}, {hi:.3f}] | {res.ceiling_mean:.3f} [{clo:.3f}, {chi:.3f}] | "
        f"{res.p_vs_ceiling:.2f} | {res.null_p:.3f}"
    )


HEADER = "| setting | metric | observed | 95% interval | perfect-proxy ceiling | P(perfect ≤ obs) | P(random ≥ obs) |\n|---|---|---|---|---|---|---|"


def simpler_google():
    tasks = load("simpler_google_robot.csv")
    print("## SIMPLER, Google Robot (6 policies)\n")
    print(HEADER)
    stacked = {}
    for task, rows in tasks.items():
        k, n = counts(rows)
        for col in ("visual_matching", "variant_aggregation"):
            sim = np.array([float(r[col]) for r in rows])
            stacked.setdefault(col, []).append((sim, k, n))
            for metric in ("mmrv", "spearman", "pearson"):
                res = pr.validate(sim, k, n, metric=metric, draws=DRAWS)
                print(f"| {task} / {col} | {metric} | {fmt(res)} |")
    for col, parts in stacked.items():
        sim, k, n = (np.stack(x) for x in zip(*parts))
        for metric in ("mmrv", "spearman"):
            res = pr.validate(sim, k, n, metric=metric, draws=DRAWS)
            print(f"| **mean of 3 tasks** / {col} | {metric} | {fmt(res)} |")

    print("\nVisual Matching vs Variant Aggregation on the same real data (paper: Visual Matching is better):\n")
    vm, k, n = (np.stack(x) for x in zip(*stacked["visual_matching"]))
    va = np.stack([s for s, _, _ in stacked["variant_aggregation"]])
    for metric in ("mmrv", "spearman", "pearson"):
        print(f"- {pr.compare(vm, va, k, n, metric=metric, draws=DRAWS)}")
    print()


def simpler_bridge():
    tasks = load("simpler_bridge.csv")
    print("## SIMPLER, WidowX + Bridge (3 policies)\n")
    print(HEADER)
    parts = []
    for task, rows in tasks.items():
        k, n = counts(rows)
        sim = np.array([float(r["visual_matching"]) for r in rows])
        parts.append((sim, k, n))
        for metric in ("mmrv", "spearman"):
            res = pr.validate(sim, k, n, metric=metric, draws=DRAWS)
            print(f"| {task} | {metric} | {fmt(res)} |")
    sim, k, n = (np.stack(x) for x in zip(*parts))
    for metric in ("mmrv", "spearman"):
        res = pr.validate(sim, k, n, metric=metric, draws=DRAWS)
        print(f"| **mean of 4 tasks** | {metric} | {fmt(res)} |")
    print()


# Table 1 of arXiv:2606.10366, policies A-E, best to worst.
RECIPE = {
    "VLA-Arena": {"Vision": "CBAED", "Layout": "CEADB", "Language": "CABED", "Behavior": "CABED"},
    "SIMPLER": {"Vision": "EDCAB", "Layout": "ECDAB", "Language": "CEDAB"},
    "REALM": {"Vision": "CEBAD", "Layout": "CEABD", "Language": "CEBAD", "Behavior": "CEBAD"},
}
RECIPE_REAL = {"Vision": "ECADB", "Layout": "CAEBD", "Language": "CABED", "Behavior": "CEADB"}
# Table 2 of the same paper, Spearman per dimension, to check the transcription
RECIPE_RHO = {
    "VLA-Arena": {"Vision": 0.0, "Layout": 0.8, "Language": 1.0, "Behavior": 0.5},
    "SIMPLER": {"Vision": 0.7, "Layout": 0.3, "Language": 0.2},
    "REALM": {"Vision": 0.6, "Layout": 0.9, "Language": 0.6, "Behavior": 0.7},
}


def scores(order):
    # best policy gets the highest score
    return np.array([len(order) - order.index(p) for p in "ABCDE"], dtype=float)


def _sum_tail(samples, threshold):
    # P(sum of independent uniform draws, one from each sample, >= threshold)
    vals, cnt = np.array([0.0]), np.array([1.0])
    for x in samples:
        v, c = np.unique(np.round(x, 9), return_counts=True)
        vals = np.add.outer(vals, v).ravel()
        cnt = np.outer(cnt, c / c.sum()).ravel()
        vals, inv = np.unique(np.round(vals, 9), return_inverse=True)
        cnt = np.bincount(inv, weights=cnt)
    return float(cnt[vals >= threshold - 1e-9].sum())


def recipe():
    print("## Practical Recipe (arXiv:2606.10366), 5 policies, rankings only\n")
    print("Only rankings are published, so intervals and ceilings cannot be computed; the exact")
    print("random-ordering null still can. Spearman over 5 policies takes only 21 distinct values.\n")
    print("| simulator | dims | mean ρ (recomputed) | mean ρ (paper) | P(random ≥ obs), exact |\n|---|---|---|---|---|")
    perms = np.array(list(itertools.permutations(range(5))))
    for sim, dims in RECIPE.items():
        rhos, nulls = [], []
        for dim, order in dims.items():
            real = scores(RECIPE_REAL[dim])
            proxy = scores(order)
            rho = float(pr.spearman(proxy, real))
            assert abs(rho - RECIPE_RHO[sim][dim]) < 1e-9, (sim, dim, rho)
            rhos.append(rho)
            nulls.append(pr.spearman(proxy[perms], real))
        # exact null of the mean: each dimension shuffled independently. The full
        # grid is 120^dims values (6.6 GB for 4 dims), so convolve value counts instead.
        obs = float(np.mean(rhos))
        p = _sum_tail(nulls, obs * len(nulls))
        print(f"| {sim} | {len(dims)} | {obs:.3f} | {np.mean(list(RECIPE_RHO[sim].values())):.3f} | {p:.4f} |")
    single = pr.spearman(scores("ABCDE")[perms], scores("ABCDE"))
    print(f"\nSingle dimension, N=5: P(random ρ ≥ 0.7) = {np.mean(single >= 0.7 - 1e-12):.3f}, "
          f"P(random ρ ≥ 0.9) = {np.mean(single >= 0.9 - 1e-12):.3f}.\n")


if __name__ == "__main__":
    print("# Reanalysis of published sim-to-real validations\n")
    print(f"proxyrank {pr.__version__}, {DRAWS} draws, Jeffreys prior, seed 0. Proxy (simulator) noise is ignored,")
    print("which makes every interval below narrower than the truth.\n")
    simpler_google()
    simpler_bridge()
    recipe()
