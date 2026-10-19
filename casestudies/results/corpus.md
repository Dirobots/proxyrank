# Five more published sim-to-real validations

proxyrank 0.1.0, 20000 draws, linked posterior, seed 0. Proxy noise ignored.

| study | level | metric | observed | 95% interval | perfect-proxy ceiling | P(perfect ≤ obs) | P(random ≥ obs) |
|---|---|---|---|---|---|---|---|
| WorldGym (n=10) | 51 cells | pearson | +0.791 | [+0.807, +0.997] | +0.852 [+0.74, +0.92] | 0.10 | 0.000 |
| WorldGym (n=10) | 51 cells | spearman | +0.743 | [+0.756, +0.996] | +0.825 [+0.70, +0.91] | 0.07 | 0.000 |
| WorldGym (n=10) | 3 policies | mmrv | +0.000 | [+0.000, +0.034] | +0.004 [+0.00, +0.04] | 1.00 | 0.167 |
| WorldGym (n=10) | 3 policies | spearman | +1.000 | [+0.500, +1.000] | +0.903 [+0.50, +1.00] | 1.00 | 0.167 |
| Ctrl-World (n=20 assumed) | 21 cells | pearson | +0.832 | [+0.795, +0.998] | +0.909 [+0.81, +0.96] | 0.04 | 0.000 |
| Ctrl-World (n=20 assumed) | 21 cells | spearman | +0.846 | [+0.789, +0.991] | +0.894 [+0.79, +0.96] | 0.14 | 0.000 |
| Ctrl-World (n=20 assumed) | 3 policies | mmrv | +0.000 | [+0.000, +0.000] | +0.001 [+0.00, +0.00] | 1.00 | 0.167 |
| Ctrl-World (n=20 assumed) | 3 policies | spearman | +1.000 | [+1.000, +1.000] | +0.983 [+0.50, +1.00] | 1.00 | 0.167 |
| GSWorld (n=10) | 8 cells | pearson | +0.874 | [-0.851, +1.000] | +0.478 [-0.34, +0.92] | 0.94 | 0.007 |
| GSWorld (n=10) | 8 cells | spearman | +0.772 | [-0.833, +1.000] | +0.450 [-0.36, +0.92] | 0.82 | 0.021 |
| GSWorld (n=10) | 2 policies | mmrv | +0.000 | [+0.000, +0.162] | +0.017 [+0.00, +0.15] | 1.00 | 0.500 |
| GSWorld (n=10) | 2 policies | spearman | +1.000 | [-1.000, +1.000] | +0.555 [-1.00, +1.00] | 0.94 | 0.500 |
| RoboLab (n=10 assumed) | 17 cells | pearson | +0.490 | [+0.319, +0.841] | +0.906 [+0.76, +0.97] | 0.00 | 0.024 |
| RoboLab (n=10 assumed) | 17 cells | spearman | +0.472 | [+0.295, +0.838] | +0.888 [+0.73, +0.97] | 0.00 | 0.029 |
| RoboLab (n=10 assumed) | 4 policies | mmrv | +0.140 | [+0.021, +0.220] | +0.006 [+0.00, +0.07] | 0.00 | 0.125 |
| RoboLab (n=10 assumed) | 4 policies | spearman | +0.800 | [+0.400, +0.800] | +0.959 [+0.80, +1.00] | 0.17 | 0.167 |
| Genie Sim 3.0 (n=50) | 16 cells | pearson | +0.970 | [+0.956, +0.997] | +0.941 [+0.88, +0.98] | 0.90 | 0.000 |
| Genie Sim 3.0 (n=50) | 16 cells | spearman | +0.960 | [+0.931, +0.998] | +0.922 [+0.82, +0.98] | 0.85 | 0.000 |
| Genie Sim 3.0 (n=50) | 4 policies | mmrv | +0.000 | [+0.000, +0.021] | +0.004 [+0.00, +0.04] | 1.00 | 0.042 |
| Genie Sim 3.0 (n=50) | 4 policies | spearman | +1.000 | [+0.800, +1.000] | +0.950 [+0.80, +1.00] | 1.00 | 0.042 |

With 2-4 policies the exact random-ordering null has 2-24 outcomes, so the smallest possible
P(random ≥ obs) is 1/2, 1/6 or 1/24: no policy-level claim in these studies can reach p < 0.04.
