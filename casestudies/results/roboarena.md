# RoboArena: preference ranking with uncertainty

3666 A/B comparisons in 3666 sessions among the 9 policies with at least 100 comparisons; 2000 posterior draws. Episodes counts every scored episode of the policy, including sessions with more than two policies.

| rank | policy | log-strength | 95% rank interval | P(above next) | success rate | episodes |
|---|---|---|---|---|---|---|
| 1 | `dreaming_zebra` | +1.02 | [1, 1] | 1.00 | 0.242 | 190 |
| 2 | `pi05_droid` | +0.52 | [2, 3] | 0.90 | 0.160 | 711 |
| 3 | `pi0_fast_droid` | +0.40 | [2, 4] | 0.93 | 0.155 | 1338 |
| 4 | `paligemma_vq_droid` | +0.26 | [3, 7] | 0.71 | 0.119 | 1360 |
| 5 | `paligemma_fast_specialist_droid` | +0.21 | [4, 7] | 0.52 | 0.131 | 1496 |
| 6 | `paligemma_diffusion_droid` | +0.21 | [4, 7] | 0.73 | 0.111 | 1344 |
| 7 | `paligemma_fast_droid` | +0.15 | [4, 7] | 1.00 | 0.127 | 1498 |
| 8 | `pi0_droid` | -0.10 | [8, 8] | 1.00 | 0.076 | 1542 |
| 9 | `paligemma_binning_droid` | -2.67 | [9, 9] |  | 0.009 | 1068 |

## Success rate vs preference

| metric | observed | 95% interval over preference draws |
|---|---|---|
| spearman | +0.917 | [+0.817, +0.983] |
| kendall | +0.833 | [+0.667, +0.944] |
| pairwise_accuracy | +0.917 | [+0.833, +0.972] |

The interval covers preference uncertainty only; success rates come from 190+ episodes per policy and are held fixed.

## How many sessions

Adjacent pairs of the full-data ranking (8) separated at P >= 0.95 when only S sessions are run, 50 random subsets each.

| sessions | adjacent pairs separated, laplace | wrong claims, laplace | adjacent pairs separated, bootstrap | wrong claims, bootstrap |
|---|---|---|---|---|
| 50 | 5% | 15/256 (5.9%) | 21% | 89/676 (13.2%) |
| 100 | 14% | 18/512 (3.5%) | 24% | 46/749 (6.1%) |
| 200 | 18% | 10/590 (1.7%) | 23% | 21/753 (2.8%) |
| 500 | 22% | 7/849 (0.8%) | 27% | 9/970 (0.9%) |
| 1000 | 30% | 1/1088 (0.1%) | 36% | 1/1169 (0.1%) |
| 2000 | 39% | 0/1302 (0.0%) | 45% | 0/1360 (0.0%) |
