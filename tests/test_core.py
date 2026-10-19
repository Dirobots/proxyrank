import math

import numpy as np
import pytest

from proxyrank import compare, validate


def test_null_is_exact_for_small_n():
    # a perfectly ordered proxy over 3 policies: 1 of 3! orderings is as good
    res = validate([0.1, 0.5, 0.9], [10, 50, 90], [100, 100, 100], draws=2000)
    assert res.null_exact
    assert res.null_p == pytest.approx(1 / math.factorial(3))


def test_null_for_five_policies_spearman_one():
    res = validate([1, 2, 3, 4, 5], [10, 20, 30, 40, 50], [60] * 5, draws=2000)
    assert res.observed == pytest.approx(1)
    assert res.null_p == pytest.approx(1 / 120)


def test_ceiling_approaches_one_with_many_trials():
    rates = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
    n = np.full(5, 100_000)
    res = validate(rates, np.round(rates * n), n, draws=4000)
    assert res.ceiling_mean > 0.999
    assert res.interval[0] > 0.99


def test_ceiling_is_low_for_close_policies_and_few_trials():
    rates = np.array([0.70, 0.72, 0.74, 0.76, 0.78])
    n = np.full(5, 20)
    res = validate(rates, np.round(rates * n), n, draws=4000)
    # 20 trials cannot resolve 2-point gaps: even a perfect proxy averages well below 1
    assert res.ceiling_mean < 0.75
    # a perfect ranking cannot be told apart from a perfect proxy
    assert not res.distinguishable_from_perfect


def test_mmrv_direction():
    res = validate([0.9, 0.1, 0.5], [10, 90, 50], [100] * 3, metric="mmrv", draws=2000)
    assert not res.higher_is_better
    assert res.observed > 0.3
    assert res.distinguishable_from_perfect


def test_multi_task_average():
    proxy = [[0.1, 0.9], [0.9, 0.1]]
    res = validate(proxy, [[10, 90], [10, 90]], [[100, 100], [100, 100]], metric="spearman", draws=2000)
    assert res.n_tasks == 2
    assert res.observed == pytest.approx(0)


def test_deterministic_given_seed():
    a = validate([0.2, 0.4, 0.6, 0.8], [5, 9, 11, 16], [20] * 4, seed=3, draws=3000)
    b = validate([0.2, 0.4, 0.6, 0.8], [5, 9, 11, 16], [20] * 4, seed=3, draws=3000)
    assert a.interval == b.interval and a.ceiling_mean == b.ceiling_mean


def test_rejects_rates_as_counts():
    with pytest.raises(ValueError):
        validate([0.1, 0.2], [0.5, 0.6], [10, 10])


def test_compare_same_proxy_is_a_coin_flip_free_tie():
    c = compare([0.1, 0.5, 0.9], [0.1, 0.5, 0.9], [10, 50, 90], [100] * 3, draws=2000)
    assert c.observed_diff == 0
    assert c.prob_a_better == 0


def test_compare_detects_clearly_better_proxy():
    real_k, n = [10, 30, 50, 70, 90], [100] * 5
    c = compare([0.1, 0.3, 0.5, 0.7, 0.9], [0.9, 0.7, 0.5, 0.3, 0.1], real_k, n, draws=2000)
    assert c.prob_a_better > 0.99


def test_null_p_is_calibrated_under_random_proxy():
    # proxy unrelated to real: null_p should be roughly uniform, so P(null_p < 0.1) ~ 0.1
    rng = np.random.default_rng(0)
    ps = []
    for i in range(300):
        real_rates = rng.random(6)
        k = rng.binomial(1000, real_rates)
        ps.append(validate(rng.random(6), k, [1000] * 6, draws=200, seed=i).null_p)
    assert 0.05 < np.mean(np.array(ps) <= 0.1) < 0.16


def test_monte_carlo_p_values_are_never_zero():
    # 2 tasks force the Monte Carlo null; a perfect proxy on far-apart rates beats every shuffle
    real = np.array([[10, 30, 50, 70, 90, 99]] * 2)
    res = validate(real / 100, real, np.full_like(real, 100), metric="spearman", draws=2000)
    assert not res.null_exact
    assert res.null_p == pytest.approx(1 / 2001)
    assert res.p_vs_ceiling > 0


def test_callable_metric_direction():
    def l1(proxy, real):
        return np.abs(proxy - real).mean(axis=-1)

    real = np.array([10, 30, 50, 70, 90])
    close = validate(real / 100, real, [100] * 5, metric=l1, higher_is_better=False)
    assert close.null_p < 0.05
    with pytest.raises(ValueError):
        validate(real / 100, real, [100] * 5, metric="mmrv", higher_is_better=True)
