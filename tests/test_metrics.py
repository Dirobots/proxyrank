import csv
from pathlib import Path

import numpy as np
import pytest
from scipy import stats

from proxyrank import kendall, mmrv, pairwise_accuracy, pearson, spearman

DATA = Path(__file__).parents[1] / "casestudies" / "data"


def load(name):
    with open(DATA / name) as f:
        rows = list(csv.DictReader(line for line in f if not line.startswith("#")))
    out = {}
    for r in rows:
        out.setdefault(r["task"], []).append(r)
    return out


def test_identical_rankings_are_perfect():
    x = [0.1, 0.5, 0.3, 0.9]
    assert mmrv(x, x) == 0
    assert spearman(x, x) == pytest.approx(1)
    assert kendall(x, x) == pytest.approx(1)
    assert pairwise_accuracy(x, x) == 1


def test_reversed_ranking():
    real = np.array([0.1, 0.4, 0.7])
    assert spearman(real[::-1], real) == pytest.approx(-1)
    # every policy's worst violation is its gap to the farthest policy
    assert mmrv(real[::-1], real) == pytest.approx(np.mean([0.6, 0.3, 0.6]))


def test_against_scipy():
    rng = np.random.default_rng(1)
    for _ in range(50):
        a, b = rng.random(7), rng.random(7)
        assert spearman(a, b) == pytest.approx(stats.spearmanr(a, b).statistic)
        assert pearson(a, b) == pytest.approx(stats.pearsonr(a, b).statistic)
        assert kendall(a, b) == pytest.approx(stats.kendalltau(a, b).statistic)


def test_batched_matches_loop():
    rng = np.random.default_rng(2)
    a, b = rng.random((100, 5)), rng.random((100, 5))
    np.testing.assert_allclose(mmrv(a, b), [mmrv(x, y) for x, y in zip(a, b)])
    np.testing.assert_allclose(spearman(a, b), [spearman(x, y) for x, y in zip(a, b)])


# Values printed in SIMPLER Table IV / V (Visual Matching). Reproducing them checks
# the MMRV definition and the transcription of the tables in casestudies/data.
@pytest.mark.parametrize(
    "task,col,mmrv_ref,r_ref",
    [
        ("pick_coke_can", "visual_matching", 0.031, 0.976),
        ("move_near", "visual_matching", 0.111, 0.855),
        ("drawer", "visual_matching", 0.055, 0.915),
        ("pick_coke_can", "variant_aggregation", 0.084, 0.960),
        ("move_near", "variant_aggregation", 0.111, 0.887),
        ("drawer", "variant_aggregation", 0.321, 0.737),
    ],
)
def test_reproduces_simpler_google(task, col, mmrv_ref, r_ref):
    rows = load("simpler_google_robot.csv")[task]
    real = [float(r["real_rate"]) for r in rows]
    sim = [float(r[col]) for r in rows]
    assert mmrv(sim, real) == pytest.approx(mmrv_ref, abs=1.5e-3)
    assert pearson(sim, real) == pytest.approx(r_ref, abs=1.5e-3)


# Pearson for carrot and eggplant does not reproduce from the published Table V rates
# (0.571 vs 0.575, 0.970 vs 0.990; the grasp column gives 0.995 / 0.972, so it is not a
# column swap). MMRV reproduces for all four, so the paper's Pearson likely used unrounded
# rates. The recomputed values are pinned instead.
@pytest.mark.parametrize(
    "task,mmrv_ref,r_ref,r_paper",
    [("spoon", 0, 0.827, 0.827), ("carrot", 0.111, 0.571, 0.575), ("block", 0, 1.0, 1.0), ("eggplant", 0, 0.970, 0.990)],
)
def test_reproduces_simpler_bridge(task, mmrv_ref, r_ref, r_paper):
    rows = load("simpler_bridge.csv")[task]
    real = [float(r["real_rate"]) for r in rows]
    sim = [float(r["visual_matching"]) for r in rows]
    assert mmrv(sim, real) == pytest.approx(mmrv_ref, abs=1.5e-3)
    assert pearson(sim, real) == pytest.approx(r_ref, abs=1.5e-3)
    assert abs(r_ref - r_paper) <= 0.021
