import numpy as np
import pytest

from proxyrank import plan, validate
from proxyrank.conditions import effective_counts, grouped_counts


def test_plan_more_trials_order_more_pairs():
    p = plan([20, 40, 60, 80], 100, budgets=(10, 100, 1000), draws=500)
    pairs = [r["pairs_ordered"] for r in p.rows]
    assert pairs[0] < pairs[1] < pairs[2]
    assert p.rows[-1]["power_null"] > 0.9


def test_plan_flags_a_reversed_proxy():
    k = [10, 30, 50, 70, 90]
    p = plan(k, 100, budgets=(50,), proxy=[0.9, 0.7, 0.5, 0.3, 0.1], draws=500)
    assert p.rows[0]["detect_imperfect"] > 0.99
    assert p.trials_for("power_null", 0.5) == 50
    assert p.trials_for("power_null", 1.01) is None
    assert "trials/cell" in str(p)


def test_identical_conditions_give_no_design_effect():
    k = np.array([[5, 5, 5], [2, 2, 2], [8, 8, 8]])
    _, _, deff = effective_counts(*grouped_counts(k, 10))
    assert deff[0] == pytest.approx(1.0)


def test_heterogeneous_conditions_widen_the_interval():
    # each policy succeeds always in some conditions and never in others
    k = np.array([[10, 0, 10, 0], [10, 10, 0, 0], [0, 10, 10, 10], [10, 10, 10, 0], [0, 0, 0, 10]])
    proxy = k.mean(1) / 10
    pooled = validate(proxy, k.sum(1), 40, metric="pearson")
    grouped = validate(proxy, k, 10, metric="pearson", by_condition=True)
    width = lambda r: r.interval[1] - r.interval[0]
    assert width(grouped) > 2 * width(pooled)


def test_grouped_counts_validate_shape():
    with pytest.raises(ValueError):
        grouped_counts([1, 2, 3], 10)
