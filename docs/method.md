# Method

Notation: N policies, T tasks, real counts `k[t, i]` of `n[t, i]` trials, proxy scores `s[t, i]`, an agreement metric `m(s, r)` computed per task and averaged over tasks.

## Interval

Each true real rate gets an independent posterior, `p[t, i] ~ Beta(k + a, n - k + b)`, with the Jeffreys prior `(a, b) = (0.5, 0.5)` by default. The metric is computed for every draw, `m(s, p)`, and the reported interval is the equal-tailed quantile range of those values. It describes the agreement with the *true* real rates, not with the observed ones.

## Perfect-proxy ceiling

For every posterior draw `p`, a new real evaluation with the same budget is simulated, `r' = Binomial(n, p) / n`, and the metric is computed for `m(p, r')`. This is the score a proxy that knows the true rates would get against a real evaluation of this size. `p_vs_ceiling` is the fraction of these scores that are no better than the observed score. When it is large, the real data cannot separate the proxy from a perfect one. More real trials, not a better simulator, is then the only way to improve the reported score.

## Random-ordering null

The proxy scores are permuted within each task and the metric is recomputed against the observed real rates. For one task with N! ≤ 40320, all permutations are enumerated and the p-value is exact. Otherwise each draw shuffles every task independently. With N policies, no single task can reach a p-value below 1/N!: the floor is 1/6 for N = 3 and 1/120 for N = 5.

## Comparing two proxies

`compare` scores both proxies on the same posterior draws of the real rates and reports the distribution of the difference. The real-side noise the two proxies share cancels in the difference, which makes this test sharper than comparing two separate intervals.

## Limits

- Proxy noise is ignored unless `proxy_successes` and `proxy_trials` are passed.
- Trials are treated as independent Bernoulli outcomes. Evaluations that vary scene, initial state or operator across trials are overdispersed, which makes the intervals too narrow.
- Rates transcribed from papers are converted back to counts. `casestudies/reanalyze.py` asserts that `k / n` rounds to every published rate.
