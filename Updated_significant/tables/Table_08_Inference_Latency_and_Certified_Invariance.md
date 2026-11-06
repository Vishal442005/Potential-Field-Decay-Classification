# Table 08 Inference Latency and Certified Invariance

| Model Architecture | Banknote (D=4) | Cancer (D=30) | Ionosphere (D=34) | Sonar (D=60) | Certified Invariance Guarantee |
| --- | --- | --- | --- | --- | --- |
| Dual-Charge PFDC (Ours) | 72.65 ms | 23.54 ms | 11.43 ms | 7.59 ms | 100% Certified Safe (Theorem 2) |
| Kernel SVM (RBF) | 8.97 ms | 19.41 ms | 12.61 ms | 18.97 ms | 0% (Adversarially Vulnerable) |
| XGBoost | 1.76 ms | 2.53 ms | 1.71 ms | 2.10 ms | 0% (Adversarially Vulnerable) |
| LightGBM | 3.46 ms | 4.06 ms | 3.23 ms | 2.84 ms | 0% (Adversarially Vulnerable) |
| Deep MLP | 1.60 ms | 2.81 ms | 1.72 ms | 2.06 ms | 0% (Adversarially Vulnerable) |
| Random Forest | 11.06 ms | 16.38 ms | 8.44 ms | 10.99 ms | 0% (Adversarially Vulnerable) |
