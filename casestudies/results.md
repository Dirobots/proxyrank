# Reanalysis of published sim-to-real validations

proxyrank 0.1.0, 20000 draws, linked posterior, seed 0. Proxy (simulator) noise is ignored,
which makes every interval below narrower than the truth.

## SIMPLER, Google Robot (6 policies)

| setting | metric | observed | 95% interval | perfect-proxy ceiling | P(perfect ≤ obs) | P(random ≥ obs) |
|---|---|---|---|---|---|---|
| pick_coke_can / visual_matching | mmrv | 0.031 | [0.000, 0.056] | 0.010 [0.000, 0.042] | 0.08 | 0.010 |
| pick_coke_can / visual_matching | spearman | 0.771 | [0.771, 1.000] | 0.936 [0.771, 1.000] | 0.04 | 0.051 |
| pick_coke_can / visual_matching | pearson | 0.976 | [0.957, 0.997] | 0.993 [0.979, 0.999] | 0.01 | 0.008 |
| pick_coke_can / variant_aggregation | mmrv | 0.084 | [0.002, 0.126] | 0.011 [0.000, 0.047] | 0.00 | 0.032 |
| pick_coke_can / variant_aggregation | spearman | 0.714 | [0.714, 0.943] | 0.933 [0.771, 1.000] | 0.01 | 0.068 |
| pick_coke_can / variant_aggregation | pearson | 0.960 | [0.931, 0.995] | 0.993 [0.978, 0.999] | 0.00 | 0.017 |
| move_near / visual_matching | mmrv | 0.111 | [0.000, 0.150] | 0.016 [0.000, 0.069] | 0.00 | 0.031 |
| move_near / visual_matching | spearman | 0.943 | [0.771, 1.000] | 0.939 [0.771, 1.000] | 0.59 | 0.008 |
| move_near / visual_matching | pearson | 0.856 | [0.759, 0.998] | 0.968 [0.890, 0.997] | 0.01 | 0.003 |
| move_near / variant_aggregation | mmrv | 0.111 | [0.000, 0.147] | 0.016 [0.000, 0.069] | 0.00 | 0.031 |
| move_near / variant_aggregation | spearman | 0.943 | [0.771, 1.000] | 0.940 [0.771, 1.000] | 0.59 | 0.008 |
| move_near / variant_aggregation | pearson | 0.886 | [0.802, 0.999] | 0.967 [0.888, 0.997] | 0.02 | 0.004 |
| drawer / visual_matching | mmrv | 0.056 | [0.000, 0.142] | 0.072 [0.000, 0.426] | 0.39 | 0.007 |
| drawer / visual_matching | spearman | 0.943 | [0.714, 1.000] | 0.841 [0.086, 1.000] | 0.74 | 0.008 |
| drawer / visual_matching | pearson | 0.915 | [0.792, 0.999] | 0.863 [0.201, 0.992] | 0.43 | 0.004 |
| drawer / variant_aggregation | mmrv | 0.321 | [0.100, 0.334] | 0.076 [0.000, 0.380] | 0.04 | 0.161 |
| drawer / variant_aggregation | spearman | 0.543 | [0.143, 0.714] | 0.847 [0.143, 1.000] | 0.09 | 0.149 |
| drawer / variant_aggregation | pearson | 0.736 | [0.336, 0.891] | 0.856 [0.261, 0.994] | 0.15 | 0.072 |
| **mean of 3 tasks** / visual_matching | mmrv | 0.066 | [0.007, 0.086] | 0.032 [0.000, 0.150] | 0.11 | 0.000 |
| **mean of 3 tasks** / visual_matching | spearman | 0.886 | [0.810, 0.981] | 0.906 [0.657, 0.995] | 0.28 | 0.000 |
| **mean of 3 tasks** / variant_aggregation | mmrv | 0.172 | [0.061, 0.167] | 0.034 [0.000, 0.134] | 0.00 | 0.002 |
| **mean of 3 tasks** / variant_aggregation | spearman | 0.733 | [0.600, 0.829] | 0.907 [0.695, 0.995] | 0.04 | 0.001 |

Visual Matching vs Variant Aggregation on the same real data (paper: Visual Matching is better):

- mmrv: A - B = -0.106  95% interval [-0.137, -0.026]  P(A better) = 0.996
- spearman: A - B = +0.152  95% interval [+0.076, +0.229]  P(A better) = 0.999
- pearson: A - B = +0.055  95% interval [+0.001, +0.121]  P(A better) = 0.977

## SIMPLER, WidowX + Bridge (3 policies)

| setting | metric | observed | 95% interval | perfect-proxy ceiling | P(perfect ≤ obs) | P(random ≥ obs) |
|---|---|---|---|---|---|---|
| spoon | mmrv | 0.000 | [0.000, 0.121] | 0.019 [0.000, 0.139] | 1.00 | 0.167 |
| spoon | spearman | 1.000 | [-0.500, 1.000] | 0.810 [-0.500, 1.000] | 1.00 | 0.167 |
| carrot | mmrv | 0.111 | [0.000, 0.253] | 0.018 [0.000, 0.111] | 0.05 | 0.500 |
| carrot | spearman | 0.500 | [-1.000, 1.000] | 0.762 [-0.500, 1.000] | 0.29 | 0.500 |
| block | mmrv | 0.000 | [0.000, 0.089] | 0.012 [0.000, 0.083] | 1.00 | 0.333 |
| block | spearman | 1.000 | [-0.022, 0.866] | 0.713 [-0.866, 1.000] | 0.97 | 0.333 |
| eggplant | mmrv | 0.000 | [0.000, 0.018] | 0.006 [0.000, 0.067] | 1.00 | 0.167 |
| eggplant | spearman | 1.000 | [0.500, 1.000] | 0.938 [0.500, 1.000] | 1.00 | 0.167 |
| **mean of 4 tasks** | mmrv | 0.028 | [0.000, 0.082] | 0.014 [0.000, 0.056] | 0.20 | 0.010 |
| **mean of 4 tasks** | spearman | 0.875 | [0.283, 0.967] | 0.804 [0.375, 1.000] | 0.66 | 0.012 |

## Practical Recipe (arXiv:2606.10366), 5 policies, rankings only

Only rankings are published, so intervals and ceilings cannot be computed; the exact
random-ordering null still can. Spearman over 5 policies takes only 21 distinct values.

| simulator | dims | mean ρ (recomputed) | mean ρ (paper) | P(random ≥ obs), exact |
|---|---|---|---|---|
| VLA-Arena | 4 | 0.575 | 0.575 | 0.0105 |
| SIMPLER | 3 | 0.400 | 0.400 | 0.0960 |
| REALM | 4 | 0.700 | 0.700 | 0.0017 |

Single dimension, N=5: P(random ρ ≥ 0.7) = 0.117, P(random ρ ≥ 0.9) = 0.042.

