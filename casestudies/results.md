# Reanalysis of published sim-to-real validations

proxyrank 0.1.0, 20000 draws, linked posterior, seed 0. Proxy (simulator) noise is ignored,
which makes every interval below narrower than the truth.

## SIMPLER, Google Robot (6 policies)

| setting | metric | observed | 95% interval | perfect-proxy ceiling | P(perfect ≤ obs) | P(random ≥ obs) |
|---|---|---|---|---|---|---|
| pick_coke_can / visual_matching | mmrv | 0.031 | [0.000, 0.052] | 0.008 [0.000, 0.038] | 0.06 | 0.010 |
| pick_coke_can / visual_matching | spearman | 0.771 | [0.771, 1.000] | 0.943 [0.771, 1.000] | 0.03 | 0.051 |
| pick_coke_can / visual_matching | pearson | 0.976 | [0.960, 0.996] | 0.994 [0.980, 0.999] | 0.01 | 0.008 |
| pick_coke_can / variant_aggregation | mmrv | 0.084 | [0.000, 0.126] | 0.010 [0.000, 0.044] | 0.00 | 0.032 |
| pick_coke_can / variant_aggregation | spearman | 0.714 | [0.714, 1.000] | 0.934 [0.771, 1.000] | 0.01 | 0.068 |
| pick_coke_can / variant_aggregation | pearson | 0.960 | [0.931, 0.996] | 0.994 [0.980, 0.999] | 0.00 | 0.017 |
| move_near / visual_matching | mmrv | 0.111 | [0.056, 0.164] | 0.014 [0.000, 0.064] | 0.00 | 0.031 |
| move_near / visual_matching | spearman | 0.943 | [0.771, 0.943] | 0.946 [0.771, 1.000] | 0.55 | 0.008 |
| move_near / visual_matching | pearson | 0.856 | [0.746, 0.943] | 0.978 [0.935, 0.997] | 0.00 | 0.003 |
| move_near / variant_aggregation | mmrv | 0.111 | [0.053, 0.163] | 0.014 [0.000, 0.064] | 0.00 | 0.031 |
| move_near / variant_aggregation | spearman | 0.943 | [0.771, 0.943] | 0.946 [0.771, 1.000] | 0.55 | 0.008 |
| move_near / variant_aggregation | pearson | 0.886 | [0.786, 0.961] | 0.978 [0.935, 0.997] | 0.00 | 0.004 |
| drawer / visual_matching | mmrv | 0.056 | [0.000, 0.120] | 0.066 [0.000, 0.426] | 0.36 | 0.007 |
| drawer / visual_matching | spearman | 0.943 | [0.771, 1.000] | 0.851 [0.086, 1.000] | 0.71 | 0.008 |
| drawer / visual_matching | pearson | 0.915 | [0.844, 0.999] | 0.877 [0.223, 0.994] | 0.38 | 0.004 |
| drawer / variant_aggregation | mmrv | 0.321 | [0.114, 0.358] | 0.064 [0.000, 0.367] | 0.04 | 0.161 |
| drawer / variant_aggregation | spearman | 0.543 | [0.200, 0.657] | 0.871 [0.143, 1.000] | 0.07 | 0.149 |
| drawer / variant_aggregation | pearson | 0.736 | [0.421, 0.883] | 0.880 [0.297, 0.996] | 0.11 | 0.072 |
| **mean of 3 tasks** / visual_matching | mmrv | 0.066 | [0.024, 0.086] | 0.029 [0.000, 0.148] | 0.09 | 0.000 |
| **mean of 3 tasks** / visual_matching | spearman | 0.886 | [0.829, 0.981] | 0.914 [0.662, 0.995] | 0.23 | 0.000 |
| **mean of 3 tasks** / variant_aggregation | mmrv | 0.172 | [0.083, 0.182] | 0.029 [0.000, 0.130] | 0.00 | 0.001 |
| **mean of 3 tasks** / variant_aggregation | spearman | 0.733 | [0.619, 0.829] | 0.918 [0.695, 0.995] | 0.04 | 0.001 |

Visual Matching vs Variant Aggregation on the same real data (paper: Visual Matching is better):

- mmrv: A - B = -0.106  95% interval [-0.137, -0.026]  P(A better) = 0.996
- spearman: A - B = +0.152  95% interval [+0.076, +0.229]  P(A better) = 0.999
- pearson: A - B = +0.055  95% interval [+0.001, +0.121]  P(A better) = 0.977

## SIMPLER, WidowX + Bridge (3 policies)

| setting | metric | observed | 95% interval | perfect-proxy ceiling | P(perfect ≤ obs) | P(random ≥ obs) |
|---|---|---|---|---|---|---|
| spoon | mmrv | 0.000 | [0.000, 0.093] | 0.011 [0.000, 0.111] | 1.00 | 0.167 |
| spoon | spearman | 1.000 | [0.500, 1.000] | 0.899 [0.500, 1.000] | 1.00 | 0.167 |
| carrot | mmrv | 0.111 | [0.000, 0.200] | 0.011 [0.000, 0.097] | 0.02 | 0.500 |
| carrot | spearman | 0.500 | [-0.500, 1.000] | 0.828 [0.000, 1.000] | 0.21 | 0.500 |
| block | mmrv | 0.000 | [0.000, 0.010] | 0.003 [0.000, 0.042] | 1.00 | 0.333 |
| block | spearman | 1.000 | [0.866, 0.866] | 0.800 [0.000, 1.000] | 0.90 | 0.333 |
| eggplant | mmrv | 0.000 | [0.000, 0.000] | 0.003 [0.000, 0.044] | 1.00 | 0.167 |
| eggplant | spearman | 1.000 | [1.000, 1.000] | 0.969 [0.500, 1.000] | 1.00 | 0.167 |
| **mean of 4 tasks** | mmrv | 0.028 | [0.000, 0.056] | 0.007 [0.000, 0.038] | 0.08 | 0.008 |
| **mean of 4 tasks** | spearman | 0.875 | [0.592, 0.967] | 0.879 [0.533, 1.000] | 0.43 | 0.011 |

## Practical Recipe (arXiv:2606.10366), 5 policies, rankings only

Only rankings are published, so intervals and ceilings cannot be computed; the exact
random-ordering null still can. Spearman over 5 policies takes only 21 distinct values.

| simulator | dims | mean ρ (recomputed) | mean ρ (paper) | P(random ≥ obs), exact |
|---|---|---|---|---|
| VLA-Arena | 4 | 0.575 | 0.575 | 0.0105 |
| SIMPLER | 3 | 0.400 | 0.400 | 0.0960 |
| REALM | 4 | 0.700 | 0.700 | 0.0017 |

Single dimension, N=5: P(random ρ ≥ 0.7) = 0.117, P(random ρ ≥ 0.9) = 0.042.

