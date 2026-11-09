# Table 12 Spatial BallTree Indexing Scalability

| Reference N | Brute Force O(N) | BallTree O(log N) | RBF-SVM | Speedup | Max Numerical Discrepancy |
| --- | --- | --- | --- | --- | --- |
| 500 | 3.27 ms | 4.61 ms | 8.59 ms | 0.71× | 9.60 × 10^-15 |
| 2,500 | 12.35 ms | 11.79 ms | 25.74 ms | 1.05× | 7.27 × 10^-15 |
| 5,000 | 26.04 ms | 17.70 ms | 33.71 ms | 1.47× | 5.27 × 10^-15 |
| 10,000 | 71.11 ms | 25.27 ms | 95.68 ms | 2.81× | 7.99 × 10^-15 |
| 20,000 | 141.83 ms | 58.97 ms | 107.62 ms | 2.40× | 2.33 × 10^-14 |
