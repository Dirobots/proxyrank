"""Reanalysis of five more published real-vs-proxy tables.

    uv run python casestudies/corpus.py > casestudies/results/corpus.md

Each CSV in casestudies/data has a header naming the source table, the trial
counts and the paper's own metrics. Two levels per study:

* cells: every (task, policy) cell is one item, as the papers' pooled Pearson
  and R^2 are computed;
* policies: tasks summed per policy, the ranking the papers claim to recover.

Where a paper does not state real trial counts, ASSUMED gives the count used;
partial-credit rates are rounded to whole successes.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import proxyrank as pr

DATA = Path(__file__).parent / "data"
DRAWS = 20_000
STUDIES = [   # file, label, trials assumed when the paper does not state them
    ("worldgym.csv", "WorldGym, arXiv:2506.00613, Table 5 (video world model)", None),
    ("ctrlworld.csv", "Ctrl-World, arXiv:2510.10125, Table 3 (video world model)", 20),
    ("gsworld.csv", "GSWorld, arXiv:2510.20813, Table I (Gaussian-splat twin)", None),
    ("robolab.csv", "RoboLab, arXiv:2604.09860v1, Table VII (Isaac simulator)", 10),
    ("geniesim3.csv", "Genie Sim 3.0, arXiv:2601.02078, Table I (simulator, humanoid)", None),
]


def load(name, assumed):
    with open(DATA / name) as f:
        rows = list(csv.DictReader(line for line in f if not line.startswith("#")))
    tasks = sorted({r["task"] for r in rows})
    policies = sorted({r["policy"] for r in rows})
    cell = {(r["task"], r["policy"]): r for r in rows}
    out = []
    for r in rows:
        t = r["real_trials"].split()[0]
        n = int(t) if t.isdigit() else assumed
        out.append((r["task"], r["policy"], int(np.floor(float(r["real_rate"]) * n + 0.5)), n,
                    float(r["proxy_score"])))
    return out, tasks, policies, cell


def row(label, metric, res):
    lo, hi = res.interval
    clo, chi = res.ceiling_interval
    return (f"| {label} | {metric} | {res.observed:+.3f} | [{lo:+.3f}, {hi:+.3f}] | {res.ceiling_mean:+.3f} "
            f"[{clo:+.2f}, {chi:+.2f}] | {res.p_vs_ceiling:.2f} | {res.null_p:.3f} |")


def main():
    print("# Five more published sim-to-real validations\n")
    print(f"proxyrank {pr.__version__}, {DRAWS} draws, linked posterior, seed 0. Proxy noise ignored.\n")
    print("| study | level | metric | observed | 95% interval | perfect-proxy ceiling | P(perfect ≤ obs) "
          "| P(random ≥ obs) |\n|---|---|---|---|---|---|---|---|")
    for name, label, assumed in STUDIES:
        items, tasks, policies, _ = load(name, assumed)
        k = np.array([x[2] for x in items])
        n = np.array([x[3] for x in items])
        s = np.array([x[4] for x in items])
        tag = label.split(",")[0] + (f" (n={assumed} assumed)" if assumed else f" (n={n[0]})")
        for m in ("pearson", "spearman"):
            print(row(f"{tag} | {len(items)} cells", m, pr.validate(s, k, n, metric=m, draws=DRAWS)))
        pk = np.array([sum(x[2] for x in items if x[1] == p) for p in policies])
        pn = np.array([sum(x[3] for x in items if x[1] == p) for p in policies])
        ps = np.array([np.mean([x[4] for x in items if x[1] == p]) for p in policies])
        # the policy-level proxy is the mean over the tasks the policy was scored on
        for m in ("mmrv", "spearman"):
            print(row(f"{tag} | {len(policies)} policies", m, pr.validate(ps, pk, pn, metric=m, draws=DRAWS)))
    print("\nWith 2-4 policies the exact random-ordering null has 2-24 outcomes, so the smallest possible")
    print("P(random ≥ obs) is 1/2, 1/6 or 1/24: no policy-level claim in these studies can reach p < 0.04.")


if __name__ == "__main__":
    main()
