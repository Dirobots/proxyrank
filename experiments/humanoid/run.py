"""Runs every policy in the real world and in each simulator, saves per-trial outcomes.

    uv run python experiments/humanoid/run.py /path/to/mujoco_menagerie [trials_per_direction]

Writes experiments/results/g1_outcomes.npz: outcomes[world, policy, direction, trial].
"""

from __future__ import annotations

import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from g1_push import DIRECTIONS, POLICIES, REAL, SIMS, Runner  # noqa: E402

OUT = Path(__file__).parents[1] / "results" / "g1_outcomes.npz"
WORLDS = [REAL, *SIMS]
_runner = None


def _init(menagerie):
    global _runner
    _runner = Runner(Path(menagerie))


def _job(args):
    w, p, direction, trials = args
    # seeds are disjoint across worlds, policies and directions
    base = ((w * 100 + p) * DIRECTIONS + direction) * 10_000
    return [_runner.trial(WORLDS[w], POLICIES[p], direction, base + s) for s in range(trials)]


def main(menagerie, trials):
    jobs = [(w, p, d, trials) for w in range(len(WORLDS)) for p in range(len(POLICIES)) for d in range(DIRECTIONS)]
    t0 = time.time()
    with Pool(initializer=_init, initargs=(menagerie,)) as pool:
        flat = pool.map(_job, jobs, chunksize=1)
    out = np.array(flat, dtype=bool).reshape(len(WORLDS), len(POLICIES), DIRECTIONS, trials)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, outcomes=out, worlds=[w.name for w in WORLDS], policies=[p.name for p in POLICIES])
    print(f"{out.size} trials in {time.time() - t0:.0f} s -> {OUT}")
    for w, name in enumerate(out.mean((2, 3))):
        print(f"{WORLDS[w].name:<14}", " ".join(f"{x:.2f}" for x in name))


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 100)
