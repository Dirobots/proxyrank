# proxyrank

Uncertainty for sim-to-real agreement metrics in robot policy evaluation.

Simulators, world models and other proxy evaluators are validated by scoring a few policies in both the proxy and the real world, then reporting MMRV, Spearman or Pearson. The real side of that table is a handful of binomial counts, often 20–75 trials per cell, so the agreement score is itself an estimate. proxyrank reports, for any such score:

| quantity | question it answers |
|---|---|
| **interval** | Which values of the metric are plausible for the *true* real success rates? |
| **perfect-proxy ceiling** | What would a proxy that ranks by the true real rates score, given the same real-trial budget? |
| `p_vs_ceiling` | How often does that perfect proxy score as badly as the observed one? A large value means the data cannot tell the proxy apart from a perfect one. |
| `null_p` | How often does a proxy that orders the policies at random score at least this well? The test is exact for one task with N ≤ 8 policies. |
| `compare` | For two proxies scored on the same real data, which one agrees better? Both are scored on shared posterior draws. |

## Install

```bash
pip install git+https://github.com/<user>/proxyrank   # numpy + scipy only
```

## Example

```python
import proxyrank as pr

sim  = [0.857, 0.710, 0.567, 0.787, 0.170, 0.027]   # simulator success rates
real = [0.853, 0.920, 0.760, 0.907, 0.293, 0.133]   # real success rates ...
n = 75                                               # ... over 75 trials each
k = [round(r * n) for r in real]

print(pr.validate(sim, k, [n] * 6, metric="spearman"))
```

```
spearman over 6 policies x 1 task(s)
  observed            +0.771
  95% interval        [+0.600, +0.943]
  perfect-proxy ceil  +0.948  [+0.771, +1.000]
  P(perfect proxy scores this badly or worse) = 0.029
  P(random ordering scores this well or better) = 0.051 (exact)
```

These are SIMPLER's Google Robot *pick coke can* numbers (Visual Matching). Inputs can carry a leading task axis, `(T, N)`. Each task is scored separately and the scores are averaged per draw, as in SIMPLER. Metrics: `mmrv`, `spearman`, `pearson`, `kendall`, `pairwise_accuracy`, or any callable that works on the last axis. Pass `proxy_successes` and `proxy_trials` when the proxy side is also small.

## Reanalysis of published validations

`casestudies/reanalyze.py` reruns three published sim-to-real tables. The full output is in [`casestudies/results.md`](casestudies/results.md).

- **The SIMPLER Google Robot comparison holds up.** Visual Matching agrees with real more than Variant Aggregation does on the same real data. Mean MMRV over 3 tasks: −0.106, 95% interval [−0.137, −0.026]. Spearman: +0.152, interval [+0.076, +0.229].
- **Some per-task scores sit at the ceiling.** With 54–60 real trials, a perfect simulator would score Spearman as low as Visual Matching's 0.943 on *move near* and *drawer* 56–59% of the time. Those tasks cannot rank SIMPLER against a perfect simulator. On *pick coke can*, Visual Matching's 0.771 is distinguishable from perfect (p = 0.03).
- **No single SIMPLER Bridge task can reject a random ordering.** With 3 policies, the best possible exact p-value is 1/6. The mean over 4 tasks can (p = 0.011).
- **One simulator in a 2026 comparison is indistinguishable from random.** In arXiv:2606.10366 (5 policies, rankings only), SIMPLER's mean ρ = 0.40 across 3 dimensions has an exact random-ordering p of 0.096. VLA-Arena's is 0.011 and REALM's is 0.002. A single-dimension ρ = 0.7 with 5 policies occurs 11.7% of the time under random ordering.

Every transcribed number is checked against the paper's own reported metric before it is used. Two cells do not reproduce: SIMPLER Table V Bridge Pearson for *carrot* (0.571 recomputed vs 0.575 published) and *eggplant* (0.970 vs 0.990). MMRV reproduces for all eight Google and Bridge cells. See `tests/test_metrics.py`.

## Method

See [`docs/method.md`](docs/method.md). Real success rates get independent Beta posteriors (Jeffreys prior by default). Each metric is computed on every posterior draw. The ceiling simulates a fresh real evaluation with the same trial counts, drawn from those posteriors, and scores the true rates against it. Proxy noise is ignored unless proxy counts are passed, so the default intervals are lower bounds on the true uncertainty.

## Related work

- [SIMPLER](https://arxiv.org/abs/2405.05941) defines MMRV.
- STEP, robostats and N-SCORE cover sequential tests and confidence bounds on the success rate of *one* policy, or on the difference between two.
- SureSim combines sim and real evaluations to estimate real performance (prediction-powered inference).
- [RoboArena](https://arxiv.org/abs/2506.18123) ranks policies from pairwise real-world comparisons and scores rankings against an oracle ranking.
- proxyrank asks a different question: how much the *agreement* between a proxy and the real world can be trusted, and whether it is better than chance.

## Citation

```bibtex
@software{proxyrank,
  title  = {proxyrank: uncertainty for sim-to-real agreement metrics},
  year   = {2026},
  url    = {https://github.com/<user>/proxyrank}
}
```

Apache-2.0.
