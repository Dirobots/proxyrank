# Method

Notation: N policies, T tasks, real counts `k[t, i]` of `n[t, i]` trials, proxy scores `s[t, i]`, an agreement metric `m(s, r)` computed per task and averaged over tasks.

## Interval

The interval is the equal-tailed range of `m(s, p)` over posterior draws `p` of the true real rates. It describes agreement with the *true* real rates, not with the observed ones. Two posteriors are available:

- **linked** (default). Per task, `logit p_i = a + b z_i + e_i` with `e_i ~ N(0, tau^2)` and `z` the standardized proxy score. The data decide how far the proxy predicts reality: an unrelated proxy gets `b ≈ 0` or a large `tau`, and its draws fall back to near-independent rates. Priors: `a ~ N(0, 10^2)`, `b ~ N(0, 2^2)`, `tau ~ half-normal(1)`. Each binomial likelihood is approximated by a normal on the logit scale at `logit((k + 0.5) / (n + 1))`. `(a, b)` are integrated in closed form and `tau` on a 400-point grid.
- **independent**. `p[t, i] ~ Beta(k + 0.5, n - k + 0.5)`. This prior treats the true ordering as unrelated to the proxy, so for a good proxy the draws scramble the order and the interval sits *below* the true score. In the G1 study it covered a near-perfect simulator's true Spearman in 0% of evaluations with 8–16 real trials per policy, against 100% for the linked posterior (`experiments/results/g1_study.md`).

For an unrelated proxy the linked interval is wider than the independent one (Spearman width 1.9 vs 0.8 at 8 trials per policy), which is the honest answer at that budget.

## Perfect-proxy ceiling

For every posterior draw `p`, a new real evaluation with the same budget is simulated, `r' = Binomial(n, p) / n`, and the metric is computed for `m(p, r')`. This is the score a proxy that knows the true rates would get against a real evaluation of this size. `p_vs_ceiling` is the fraction of these scores that are no better than the observed score. When it is large, the real data cannot separate the proxy from a perfect one.

## Random-ordering null

The proxy scores are permuted within each task and the metric is recomputed against the observed real rates. For one task with N! ≤ 40320 all permutations are enumerated and the p-value is exact; otherwise each draw shuffles every task independently and the p-value is `(hits + 1) / (draws + 1)`. With N policies, no single task can reach a p-value below 1/N!: 1/6 for N = 3, 1/120 for N = 5.

## Comparing two proxies

`compare` scores both proxies on the same independent-posterior draws of the real rates and reports the distribution of the difference. The real-side noise the two proxies share cancels in the difference.

## Conditions

Real trials are rarely exchangeable: each policy is run on a few scenes, objects or push directions. Passing counts with a trailing condition axis and `by_condition=True` estimates the intra-condition correlation `rho` per task (one-way ANOVA, averaged over policies, clipped to [0, 1]) and divides successes and trials by the Kish design effect `1 + (m - 1) rho`, `m` the mean trials per condition. The target becomes the rate over the population of conditions.

## Trial planner

`plan` draws true rates from a pilot posterior and simulates the validation at each per-cell budget. It reports the perfect-proxy score, how often that score beats the random null at `alpha`, the fraction of policy pairs the real evaluation orders correctly and, given a proxy, how often the real data would flag it as worse than perfect.

## Pairwise evaluations

`rank_pairwise` fits a Bradley–Terry model to A/B/tie outcomes (ties count half). The default posterior puts `N(0, 1)` on log-strengths and samples the Laplace approximation at the mode. A Bayesian bootstrap over sessions is available (`method="bootstrap"`) but overstates certainty when policies have few comparisons. `validate_pairwise` scores a proxy against the strength draws.

## Calibration

| experiment | file | result |
|---|---|---|
| condition effects, 6 policies, 5 conditions × 10 trials | `experiments/results/coverage.md` | linked posterior: pooled 0.88–1.00, by condition 0.93–1.00; the independent posterior (`coverage_independent.md`) gave Pearson 0.84–0.89 |
| G1 push recovery, 5 simulators, 8–80 real trials per policy | `experiments/results/g1_study.md` | `compare` claims at P ≥ 0.95 are wrong ≤ 6.8% of the time at 8 trials and ≤ 0.5% from 40; linked intervals cover ≥ 0.92 |
| RoboArena subsets of 50–2000 sessions | `casestudies/results/roboarena.md` | Laplace 95% claims wrong 5.9% at 50 sessions, 0% at 2000; bootstrap 13.2% at 50 |

## Limits

- Proxy noise is ignored unless `proxy_successes` and `proxy_trials` are passed.
- The linked posterior assumes the real rates are roughly logit-linear in the proxy score; a non-monotone relation is absorbed by a larger `tau`, which widens the interval.
- The logit-normal likelihood approximation is crude for cells with 0 or n successes out of very few trials.
- The ceiling test had no power against the G1 *misidentified* simulator (Spearman 0.87) at any budget tried.
- Rates transcribed from papers are converted back to counts; partial-credit rates are rounded, and two corpus studies do not state trial counts (`casestudies/corpus.py` marks the assumed ones).
