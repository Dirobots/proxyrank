# Five more published sim-to-real validations

proxyrank 0.1.0, 20000 draws, linked posterior, seed 0. Proxy noise ignored.

| study | level | metric | observed | 95% interval | perfect-proxy ceiling | P(perfect ≤ obs) | P(random ≥ obs) |
|---|---|---|---|---|---|---|---|
| WorldGym (n=10) | 51 cells | pearson | +0.791 | [+0.782, +0.915] | +0.930 [+0.89, +0.96] | 0.00 | 0.000 |
| WorldGym (n=10) | 51 cells | spearman | +0.743 | [+0.728, +0.890] | +0.903 [+0.84, +0.95] | 0.00 | 0.000 |
| WorldGym (n=10) | 3 policies | mmrv | +0.000 | [+0.000, +0.029] | +0.003 [+0.00, +0.03] | 1.00 | 0.167 |
| WorldGym (n=10) | 3 policies | spearman | +1.000 | [+0.500, +1.000] | +0.924 [+0.50, +1.00] | 1.00 | 0.167 |
| Ctrl-World (n=20 assumed) | 21 cells | pearson | +0.832 | [+0.790, +0.980] | +0.932 [+0.87, +0.97] | 0.01 | 0.000 |
| Ctrl-World (n=20 assumed) | 21 cells | spearman | +0.846 | [+0.779, +0.973] | +0.914 [+0.83, +0.97] | 0.05 | 0.000 |
| Ctrl-World (n=20 assumed) | 3 policies | mmrv | +0.000 | [+0.000, +0.000] | +0.000 [+0.00, +0.00] | 1.00 | 0.167 |
| Ctrl-World (n=20 assumed) | 3 policies | spearman | +1.000 | [+1.000, +1.000] | +0.990 [+1.00, +1.00] | 1.00 | 0.167 |
| GSWorld (n=10) | 8 cells | pearson | +0.874 | [-1.000, +1.000] | +0.468 [-0.41, +0.92] | 0.93 | 0.007 |
| GSWorld (n=10) | 8 cells | spearman | +0.772 | [-1.000, +1.000] | +0.447 [-0.41, +0.93] | 0.81 | 0.021 |
| GSWorld (n=10) | 2 policies | mmrv | +0.000 | [+0.000, +0.168] | +0.017 [+0.00, +0.15] | 1.00 | 0.500 |
| GSWorld (n=10) | 2 policies | spearman | +1.000 | [-1.000, +1.000] | +0.564 [-1.00, +1.00] | 0.94 | 0.500 |
| RoboLab (n=10 assumed) | 17 cells | pearson | +0.490 | [+0.403, +0.637] | +0.964 [+0.92, +0.99] | 0.00 | 0.024 |
| RoboLab (n=10 assumed) | 17 cells | spearman | +0.472 | [+0.369, +0.684] | +0.940 [+0.87, +0.98] | 0.00 | 0.029 |
| RoboLab (n=10 assumed) | 4 policies | mmrv | +0.140 | [+0.032, +0.218] | +0.002 [+0.00, +0.03] | 0.00 | 0.125 |
| RoboLab (n=10 assumed) | 4 policies | spearman | +0.800 | [+0.800, +0.800] | +0.982 [+0.80, +1.00] | 0.08 | 0.167 |
| Genie Sim 3.0 (n=50) | 16 cells | pearson | +0.970 | [+0.970, +0.997] | +0.945 [+0.89, +0.98] | 0.88 | 0.000 |
| Genie Sim 3.0 (n=50) | 16 cells | spearman | +0.960 | [+0.951, +0.998] | +0.924 [+0.83, +0.98] | 0.84 | 0.000 |
| Genie Sim 3.0 (n=50) | 4 policies | mmrv | +0.000 | [+0.000, +0.014] | +0.004 [+0.00, +0.03] | 1.00 | 0.042 |
| Genie Sim 3.0 (n=50) | 4 policies | spearman | +1.000 | [+0.800, +1.000] | +0.952 [+0.80, +1.00] | 1.00 | 0.042 |

With 2-4 policies the exact random-ordering null has 2-24 outcomes, so the smallest possible
P(random ≥ obs) is 1/2, 1/6 or 1/24: no policy-level claim in these studies can reach p < 0.04.
