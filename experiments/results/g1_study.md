# G1 push recovery: simulator validation from small real evaluations

12 balance controllers, 8 push directions, 100 real trials per direction and policy as the truth pool, 200 replicates per budget, 1000 posterior draws.

Real success rates: 0.79 0.65 0.79 0.71 0.66 0.53 0.63 0.45 0.36 0.40 0.32 0.20 

| simulator | true mmrv | true spearman | true pearson |
|---|---|---|---|
| nominal | +0.014 | +0.986 | +0.963 |
| randomized | +0.001 | +0.993 | +0.992 |
| sysid | +0.007 | +0.986 | +0.993 |
| sysid+delay | +0.001 | +0.993 | +0.996 |
| misidentified | +0.093 | +0.874 | +0.881 |

## mmrv

| real trials / policy | naive picks best sim | wrong naive claims | proxyrank claims (pooled) | wrong (pooled) | proxyrank claims (by direction) | wrong (by direction) |
|---|---|---|---|---|---|---|
| 8 | 0.30 | 22.1% | 13.1% | 6.8% | 13.1% | 6.8% |
| 16 | 0.50 | 14.0% | 19.9% | 2.5% | 10.4% | 2.1% |
| 40 | 0.65 | 12.2% | 36.8% | 0.3% | 6.8% | 0.0% |
| 80 | 0.73 | 9.8% | 50.9% | 0.4% | 3.9% | 0.0% |

Interval coverage per simulator: independent pooled / linked pooled / linked by direction. Ceiling-test flag rate (linked, by direction) in brackets.

| real trials / policy | nominal | randomized | sysid | sysid+delay | misidentified |
|---|---|---|---|---|---|
| 8 | 0.00 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.14 / 1.00 / 1.00 [0.00] |
| 16 | 0.00 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.56 / 0.99 / 1.00 [0.00] |
| 40 | 0.11 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.01 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.90 / 0.92 / 1.00 [0.00] |
| 80 | 0.65 / 1.00 / 1.00 [0.00] | 0.01 / 1.00 / 1.00 [0.00] | 0.40 / 1.00 / 1.00 [0.00] | 0.01 / 1.00 / 1.00 [0.00] | 0.97 / 0.93 / 1.00 [0.00] |

## spearman

| real trials / policy | naive picks best sim | wrong naive claims | proxyrank claims (pooled) | wrong (pooled) | proxyrank claims (by direction) | wrong (by direction) |
|---|---|---|---|---|---|---|
| 8 | 0.36 | 20.4% | 12.3% | 6.1% | 12.3% | 6.1% |
| 16 | 0.51 | 13.5% | 16.7% | 2.2% | 9.8% | 1.3% |
| 40 | 0.68 | 8.5% | 33.4% | 0.0% | 5.8% | 0.0% |
| 80 | 0.73 | 7.1% | 52.5% | 0.5% | 3.0% | 0.0% |

Interval coverage per simulator: independent pooled / linked pooled / linked by direction. Ceiling-test flag rate (linked, by direction) in brackets.

| real trials / policy | nominal | randomized | sysid | sysid+delay | misidentified |
|---|---|---|---|---|---|
| 8 | 0.00 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.30 / 1.00 / 1.00 [0.00] |
| 16 | 0.00 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.58 / 1.00 / 1.00 [0.00] |
| 40 | 0.07 / 1.00 / 1.00 [0.00] | 0.01 / 1.00 / 1.00 [0.00] | 0.07 / 1.00 / 1.00 [0.00] | 0.01 / 1.00 / 1.00 [0.00] | 0.81 / 1.00 / 1.00 [0.00] |
| 80 | 0.50 / 1.00 / 1.00 [0.00] | 0.32 / 1.00 / 1.00 [0.00] | 0.65 / 1.00 / 1.00 [0.00] | 0.32 / 1.00 / 1.00 [0.00] | 0.85 / 1.00 / 1.00 [0.00] |

## pearson

| real trials / policy | naive picks best sim | wrong naive claims | proxyrank claims (pooled) | wrong (pooled) | proxyrank claims (by direction) | wrong (by direction) |
|---|---|---|---|---|---|---|
| 8 | 0.33 | 26.2% | 12.8% | 1.2% | 12.8% | 1.2% |
| 16 | 0.43 | 18.9% | 22.7% | 2.0% | 12.3% | 0.8% |
| 40 | 0.45 | 14.6% | 40.1% | 0.1% | 11.7% | 0.0% |
| 80 | 0.49 | 13.8% | 52.0% | 0.6% | 10.0% | 0.0% |

Interval coverage per simulator: independent pooled / linked pooled / linked by direction. Ceiling-test flag rate (linked, by direction) in brackets.

| real trials / policy | nominal | randomized | sysid | sysid+delay | misidentified |
|---|---|---|---|---|---|
| 8 | 0.00 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.12 / 1.00 / 1.00 [0.00] |
| 16 | 0.00 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.41 / 0.98 / 1.00 [0.00] |
| 40 | 0.17 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.82 / 0.94 / 1.00 [0.00] |
| 80 | 0.62 / 0.96 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.00 / 1.00 / 1.00 [0.00] | 0.94 / 0.94 / 1.00 [0.00] |

