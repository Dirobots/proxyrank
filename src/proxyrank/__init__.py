"""Uncertainty for sim-to-real (proxy-to-real) agreement metrics in robot policy evaluation."""

from .core import Comparison, ValidationResult, compare, posterior_rates, validate
from .pairwise import PairwiseRanking, rank_pairwise, validate_pairwise
from .plan import Plan, plan
from .metrics import HIGHER_IS_BETTER, METRICS, kendall, mmrv, pairwise_accuracy, pearson, spearman

__all__ = [
    "validate", "compare", "plan", "Plan", "rank_pairwise", "validate_pairwise", "PairwiseRanking", "posterior_rates", "ValidationResult", "Comparison",
    "METRICS", "HIGHER_IS_BETTER", "mmrv", "spearman", "pearson", "kendall", "pairwise_accuracy",
]
__version__ = "0.1.0"
