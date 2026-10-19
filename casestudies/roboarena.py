"""RoboArena: pairwise ranking with uncertainty, and how it relates to success rate.

    uv run python casestudies/roboarena.py > casestudies/results/roboarena.md

Data: casestudies/data/roboarena_*.csv, written by roboarena_extract.py from the
public RoboArena dump. Policies with at least MIN_GAMES comparisons are kept.

1. Bradley-Terry ranking of the evaluators' A/B/tie preferences, with rank
   intervals from the Laplace posterior (``rank_pairwise``'s default).
2. Agreement of the binary task-success ranking (what simulators and most
   benchmarks score) with the preference ranking, with an interval.
3. Session subsampling: with S sessions, how many adjacent policy pairs of the
   full-data ranking are separated at 95%, and how often such a claim is wrong,
   for the Laplace posterior and for the session bootstrap.
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

import proxyrank as pr

DATA = Path(__file__).parent / "data"
MIN_GAMES = 100
SUBSAMPLES = (50, 100, 200, 500, 1000, 2000)
REPS = 50


def load():
    pairs = list(csv.DictReader(open(DATA / "roboarena_pairs.csv")))
    games = defaultdict(int)
    for r in pairs:
        games[r["policy_a"]] += 1
        games[r["policy_b"]] += 1
    keep = {p for p, g in games.items() if g >= MIN_GAMES}
    pairs = [r for r in pairs if r["policy_a"] in keep and r["policy_b"] in keep]
    succ = defaultdict(list)
    for r in csv.DictReader(open(DATA / "roboarena_episodes.csv")):
        if r["policy"] in keep:
            succ[r["policy"]].append(int(r["success"]))
    return pairs, succ


def fit(pairs, draws, seed, method="laplace"):
    y = [{"A": 1.0, "B": 0.0, "TIE": 0.5}[r["preference"]] for r in pairs]
    return pr.rank_pairwise([r["policy_a"] for r in pairs], [r["policy_b"] for r in pairs], y,
                            sessions=[r["session"] for r in pairs], method=method, draws=draws, seed=seed)


def main():
    pairs, succ = load()
    full = fit(pairs, 2000, 0)
    order = list(np.argsort(-full.strength))
    names = [full.policies[i] for i in order]
    rate = {p: float(np.mean(v)) for p, v in succ.items()}
    print("# RoboArena: preference ranking with uncertainty\n")
    print(f"{len(pairs)} A/B comparisons in {len({r['session'] for r in pairs})} sessions among the "
          f"{len(names)} policies with at least {MIN_GAMES} comparisons; 2000 posterior draws. Episodes "
          "counts every scored episode of the policy, including sessions with more than two policies.\n")
    p = full.prob_above()
    print("| rank | policy | log-strength | 95% rank interval | P(above next) | success rate | episodes |")
    print("|---|---|---|---|---|---|---|")
    for r, i in enumerate(order):
        lo, hi = full.rank_interval(full.policies[i])
        nxt = f"{p[i, order[r + 1]]:.2f}" if r + 1 < len(order) else ""
        name = full.policies[i]
        print(f"| {r + 1} | `{name}` | {full.strength[i]:+.2f} | [{lo}, {hi}] | {nxt} "
              f"| {rate[name]:.3f} | {len(succ[name])} |")
    print("\n## Success rate vs preference\n")
    print("| metric | observed | 95% interval over preference draws |\n|---|---|---|")
    for m in ("spearman", "kendall", "pairwise_accuracy"):
        obs, (lo, hi) = pr.validate_pairwise(rate, full, metric=m)
        print(f"| {m} | {obs:+.3f} | [{lo:+.3f}, {hi:+.3f}] |")
    print("\nThe interval covers preference uncertainty only; success rates come from "
          f"{min(len(v) for v in succ.values())}+ episodes per policy and are held fixed.\n")

    print("## How many sessions\n")
    print(f"Adjacent pairs of the full-data ranking ({len(order) - 1}) separated at P >= 0.95 "
          f"when only S sessions are run, {REPS} random subsets each.\n")
    print("| sessions | adjacent pairs separated, laplace | wrong claims, laplace "
          "| adjacent pairs separated, bootstrap | wrong claims, bootstrap |\n|---|---|---|---|---|")
    sessions = sorted({r["session"] for r in pairs})
    by_session = defaultdict(list)
    for r in pairs:
        by_session[r["session"]].append(r)
    truth = {(a, b): full.strength[full.policies.index(a)] > full.strength[full.policies.index(b)]
             for a in names for b in names if a != b}
    for s in SUBSAMPLES:
        if s > len(sessions):
            break
        cells = []
        for method in ("laplace", "bootstrap"):
            sep, claims, wrong = [], 0, 0
            sub_rng = np.random.default_rng(s)    # same subsets for both methods
            for rep in range(REPS):
                pick = sub_rng.choice(len(sessions), s, replace=False)
                sub = [r for j in pick for r in by_session[sessions[j]]]
                rk = fit(sub, 400, rep, method)
                pa = rk.prob_above()
                ix = {n: rk.policies.index(n) if n in rk.policies else None for n in names}
                sep.append(np.mean([ix[a] is not None and ix[b] is not None and pa[ix[a], ix[b]] >= 0.95
                                    for a, b in zip(names, names[1:])]))
                for (a, b), t in truth.items():
                    if ix[a] is not None and ix[b] is not None and pa[ix[a], ix[b]] >= 0.95:
                        claims += 1
                        wrong += not t
            cells += [f"{np.mean(sep):.0%}", f"{wrong}/{claims} ({wrong / max(claims, 1):.1%})"]
        print(f"| {s} | " + " | ".join(cells) + " |")

if __name__ == "__main__":
    sys.exit(main())
