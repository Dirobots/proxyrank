# Reanalysis of published sim-to-real validations

proxyrank 0.1.0, 20000 draws, Jeffreys prior, seed 0. Proxy (simulator) noise is ignored,
which makes every interval below narrower than the truth.

## SIMPLER, Google Robot (6 policies)

| setting | metric | observed | 95% interval | perfect-proxy ceiling | P(perfect ≤ obs) | P(random ≥ obs) |
|---|---|---|---|---|---|---|
| pick_coke_can / visual_matching | mmrv | 0.031 | [0.002, 0.085] | 0.008 [0.000, 0.040] | 0.06 | 0.010 |
| pick_coke_can / visual_matching | spearman | 0.771 | [0.600, 0.943] | 0.948 [0.771, 1.000] | 0.03 | 0.051 |
| pick_coke_can / visual_matching | pearson | 0.976 | [0.939, 0.989] | 0.994 [0.981, 0.999] | 0.01 | 0.008 |
| pick_coke_can / variant_aggregation | mmrv | 0.084 | [0.034, 0.153] | 0.008 [0.000, 0.040] | 0.00 | 0.032 |
| pick_coke_can / variant_aggregation | spearman | 0.714 | [0.543, 0.886] | 0.948 [0.771, 1.000] | 0.01 | 0.068 |
| pick_coke_can / variant_aggregation | pearson | 0.960 | [0.915, 0.983] | 0.994 [0.981, 0.999] | 0.00 | 0.017 |
| move_near / visual_matching | mmrv | 0.111 | [0.072, 0.177] | 0.015 [0.000, 0.069] | 0.00 | 0.031 |
| move_near / visual_matching | spearman | 0.943 | [0.771, 0.943] | 0.941 [0.771, 1.000] | 0.59 | 0.008 |
| move_near / visual_matching | pearson | 0.856 | [0.716, 0.922] | 0.978 [0.937, 0.997] | 0.00 | 0.003 |
| move_near / variant_aggregation | mmrv | 0.111 | [0.072, 0.177] | 0.015 [0.000, 0.069] | 0.00 | 0.031 |
| move_near / variant_aggregation | spearman | 0.943 | [0.771, 0.943] | 0.941 [0.771, 1.000] | 0.59 | 0.008 |
| move_near / variant_aggregation | pearson | 0.886 | [0.756, 0.942] | 0.978 [0.937, 0.997] | 0.00 | 0.004 |
| drawer / visual_matching | mmrv | 0.056 | [0.002, 0.206] | 0.039 [0.000, 0.284] | 0.22 | 0.007 |
| drawer / visual_matching | spearman | 0.943 | [0.543, 0.943] | 0.914 [0.429, 1.000] | 0.56 | 0.008 |
| drawer / visual_matching | pearson | 0.915 | [0.679, 0.975] | 0.929 [0.499, 0.998] | 0.22 | 0.004 |
| drawer / variant_aggregation | mmrv | 0.321 | [0.162, 0.403] | 0.039 [0.000, 0.284] | 0.02 | 0.161 |
| drawer / variant_aggregation | spearman | 0.543 | [0.200, 0.657] | 0.914 [0.429, 1.000] | 0.03 | 0.149 |
| drawer / variant_aggregation | pearson | 0.736 | [0.428, 0.848] | 0.929 [0.499, 0.998] | 0.05 | 0.072 |
| **mean of 3 tasks** / visual_matching | mmrv | 0.066 | [0.045, 0.124] | 0.020 [0.000, 0.099] | 0.05 | 0.000 |
| **mean of 3 tasks** / visual_matching | spearman | 0.886 | [0.733, 0.943] | 0.935 [0.771, 1.000] | 0.15 | 0.000 |
| **mean of 3 tasks** / variant_aggregation | mmrv | 0.172 | [0.117, 0.213] | 0.020 [0.000, 0.099] | 0.00 | 0.001 |
| **mean of 3 tasks** / variant_aggregation | spearman | 0.733 | [0.581, 0.790] | 0.935 [0.771, 1.000] | 0.02 | 0.001 |

Visual Matching vs Variant Aggregation on the same real data (paper: Visual Matching is better):

- mmrv: A - B = -0.106  95% interval [-0.137, -0.026]  P(A better) = 0.996
- spearman: A - B = +0.152  95% interval [+0.076, +0.229]  P(A better) = 0.999
- pearson: A - B = +0.055  95% interval [+0.001, +0.121]  P(A better) = 0.977

## SIMPLER, WidowX + Bridge (3 policies)

| setting | metric | observed | 95% interval | perfect-proxy ceiling | P(perfect ≤ obs) | P(random ≥ obs) |
|---|---|---|---|---|---|---|
| spoon | mmrv | 0.000 | [0.000, 0.123] | 0.013 [0.000, 0.139] | 1.00 | 0.167 |
| spoon | spearman | 1.000 | [0.500, 1.000] | 0.894 [0.500, 1.000] | 1.00 | 0.167 |
| carrot | mmrv | 0.111 | [0.000, 0.248] | 0.008 [0.000, 0.083] | 0.01 | 0.500 |
| carrot | spearman | 0.500 | [-0.500, 1.000] | 0.874 [0.500, 1.000] | 0.16 | 0.500 |
| block | mmrv | 0.000 | [0.000, 0.047] | 0.005 [0.000, 0.056] | 1.00 | 0.333 |
| block | spearman | 1.000 | [0.000, 0.866] | 0.815 [0.000, 1.000] | 0.95 | 0.333 |
| eggplant | mmrv | 0.000 | [0.000, 0.024] | 0.005 [0.000, 0.067] | 1.00 | 0.167 |
| eggplant | spearman | 1.000 | [0.500, 1.000] | 0.947 [0.500, 1.000] | 1.00 | 0.167 |
| **mean of 4 tasks** | mmrv | 0.028 | [0.001, 0.076] | 0.008 [0.000, 0.042] | 0.10 | 0.007 |
| **mean of 4 tasks** | spearman | 0.875 | [0.467, 0.967] | 0.883 [0.592, 1.000] | 0.47 | 0.011 |

## Practical Recipe (arXiv:2606.10366), 5 policies, rankings only

Only rankings are published, so intervals and ceilings cannot be computed; the exact
random-ordering null still can. Spearman over 5 policies takes only 21 distinct values.

| simulator | dims | mean ρ (recomputed) | mean ρ (paper) | P(random ≥ obs), exact |
|---|---|---|---|---|
| VLA-Arena | 4 | 0.575 | 0.575 | 0.0105 |
| SIMPLER | 3 | 0.400 | 0.400 | 0.0960 |
| REALM | 4 | 0.700 | 0.700 | 0.0017 |

Single dimension, N=5: P(random ρ ≥ 0.7) = 0.117, P(random ρ ≥ 0.9) = 0.042.

