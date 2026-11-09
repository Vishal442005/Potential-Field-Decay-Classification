# Table 11 Certified Adversarial Robustness vs Epsilon

| Perturbation (ε) | Deep MLP | Kernel SVM | XGBoost | PFDC (Overall) | PFDC Core Invariance |
| --- | --- | --- | --- | --- | --- |
| ε = 0.00 (Clean) | 97.08% | 98.25% | 95.32% | 97.08% | 100.00% (Certified Safe) |
| ε = 0.05 | 93.57% | 94.74% | 92.98% | 94.74% | 100.00% (Certified Safe) |
| ε = 0.10 | 85.38% | 93.57% | 89.47% | 90.06% | 100.00% (Certified Safe) |
| ε = 0.20 | 74.85% | 84.21% | 84.80% | 83.63% | 100.00% (Certified Safe) |
| ε = 0.35 | 53.22% | 71.93% | 73.68% | 73.68% | 100.00% (Certified Safe) |
| ε = 0.50 | 33.92% | 50.29% | 59.65% | 59.06% | 100.00% (Certified Safe) |
| ε = 0.75 | 13.45% | 23.39% | 32.16% | 28.07% | 100.00% (Certified Safe) |
