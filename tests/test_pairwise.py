import numpy as np
import pytest

from proxyrank import rank_pairwise, validate_pairwise


def _arena(true, n, rng):
    names = list(true)
    a, b, y = [], [], []
    for _ in range(n):
        i, j = rng.choice(len(names), 2, replace=False)
        p = 1 / (1 + np.exp(true[names[j]] - true[names[i]]))
        a.append(names[i]); b.append(names[j]); y.append(float(rng.random() < p))
    return a, b, y


def test_recovers_order_and_scale():
    true = {"p0": -1.0, "p1": -0.3, "p2": 0.3, "p3": 1.0}
    r = rank_pairwise(*_arena(true, 4000, np.random.default_rng(0)), draws=200)
    fitted = dict(zip(r.policies, r.strength))
    assert sorted(fitted, key=fitted.get) == ["p0", "p1", "p2", "p3"]
    assert fitted["p3"] - fitted["p0"] == pytest.approx(2.0, abs=0.3)
    assert r.rank_interval("p3") == (1, 1)


def test_few_comparisons_give_wide_ranks():
    true = {"p0": 0.0, "p1": 0.1, "p2": 0.2}
    r = rank_pairwise(*_arena(true, 30, np.random.default_rng(1)), draws=300)
    lo, hi = r.rank_interval("p1")
    assert hi - lo >= 1
    assert 0.1 < r.prob_above()[2, 0] < 0.99


def test_unbeaten_policy_stays_finite():
    r = rank_pairwise(["a", "a", "b"], ["b", "c", "c"], [1, 1, 1], draws=50)
    assert np.all(np.isfinite(r.draws))


def test_validate_pairwise_perfect_proxy():
    true = {f"p{i}": i * 0.5 for i in range(6)}
    r = rank_pairwise(*_arena(true, 3000, np.random.default_rng(2)), draws=200)
    obs, (lo, hi) = validate_pairwise(true, r, metric="spearman")
    assert obs == pytest.approx(1.0)
    assert lo > 0.7
    with pytest.raises(ValueError):
        validate_pairwise(true, r, metric="mmrv")


def test_laplace_claims_are_calibrated_with_few_games():
    # 95% "i above j" claims from 40 comparisons among 8 policies should rarely be wrong
    rng = np.random.default_rng(3)
    claims = wrong = 0
    for _ in range(40):
        true = dict(zip([f"p{i}" for i in range(8)], rng.normal(0, 1, 8)))
        r = rank_pairwise(*_arena(true, 40, rng), draws=400, seed=int(rng.integers(1 << 30)))
        t = np.array([true[x] for x in r.policies])
        hit = r.prob_above() >= 0.95
        claims += hit.sum()
        wrong += (hit & (t[:, None] < t[None, :])).sum()
    assert claims > 0 and wrong / claims < 0.05


def test_bootstrap_method_and_bad_method():
    a, b, y = _arena({"p0": 0.0, "p1": 1.0, "p2": 2.0}, 300, np.random.default_rng(4))
    r = rank_pairwise(a, b, y, method="bootstrap", draws=100)
    assert r.rank_interval("p2")[0] == 1
    with pytest.raises(ValueError):
        rank_pairwise(a, b, y, method="mcmc")
