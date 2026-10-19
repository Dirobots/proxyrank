# Method

Notation: N policies, T tasks, real counts `k[t, i]` of `n[t, i]` trials, proxy scores `s[t, i]`, an agreement metric `m(s, r)` computed per task and averaged over tasks.

## Interval

The interval is the equal-tailed range of `m(s, p)` over posterior draws `p` of the true real rates. It describes agreement with the *true* real rates, not with the observed ones. Two posteriors are available:

- **linked** (default). Per task, `logit p_i = a + b z_i + e_i` with `e_i ~ N(0, tau^2)` and `z` the standardized proxy score. The data decide how far the proxy predicts reality: an unrelated proxy gets `b ≈ 0` or a large `tau`, and its draws fall back to near-independent rates. Priors: `a ~ N(0, 10^2)`, `b ~ N(0, 2^2)`, and `tau` half-normal(1) with an extra point mass 0.2 at `tau = 0`. Proposals for `(a, b, tau)` come from a normal likelihood on the logit scale, linearized at the empirical logit and again at the first pass's posterior mean; under it `(a, b)` integrate in closed form and `tau` lives on a 400-point grid. The proposals are importance-resampled to the exact binomial likelihood, with each logit integrated out on an 81-point grid, and each logit is drawn from its exact conditional. Without the correction, cells at 0/n or n/n are pulled toward 1/2 and MMRV intervals with 12 policies and 8 trials covered 0.80.
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
| condition effects, 6 policies, 5 conditions × 10 trials | `experiments/results/coverage.md` | linked posterior: pooled 0.83–0.99, by condition 0.90–1.00; the independent posterior (`coverage_independent.md`) gave Pearson 0.84–0.89 |
| proxy quality 0–1, logit spread 0.5–2, 6 or 12 policies, 8–80 trials | `experiments/results/calibration.md` | linked: ≥ 0.89 in all 216 cells except Pearson with an exact proxy (9 cells, 0.57–0.88); Spearman ≥ 0.92 everywhere; independent: down to 0.00 for good proxies |
| G1 push recovery, 5 simulators, 8–200 real trials per policy | `experiments/results/g1_study.md` | `compare` claims at P ≥ 0.95 are wrong ≤ 6.8% of the time at 8 trials and ≤ 0.5% from 40; linked intervals cover ≥ 0.92 |
| RoboArena subsets of 50–2000 sessions | `casestudies/results/roboarena.md` | Laplace 95% claims wrong 5.9% at 50 sessions, 0% at 2000; bootstrap 13.2% at 50 |

## Limits

- Proxy noise is ignored unless `proxy_successes` and `proxy_trials` are passed.
- The linked posterior assumes the real rates are roughly logit-linear in the proxy score; a non-monotone relation is absorbed by a larger `tau`, which widens the interval.
- The logit-normal likelihood approximation is crude for cells with 0 or n successes out of very few trials.
- When the proxy is an exact logistic transform of the true rates, the true Pearson sits at the edge of the posterior and the interval covers it in 0.57–0.96 of cases (`calibration.md`, rho = 1). With neither the point mass at `tau = 0` nor the exact-likelihood correction it was 0.06–0.89.
- The ceiling test needs large budgets: pooled, it flags the G1 *misidentified* simulator (Spearman 0.87) in 68% of evaluations at 80 real trials per policy and in all of them at 200. With push directions as conditions, the design effect shrinks the effective budget and it flags none.
- Rates transcribed from papers are converted back to counts; partial-credit rates are rounded, and two corpus studies do not state trial counts (`casestudies/corpus.py` marks the assumed ones).
