# Table 15: Operational Boundary Map and Generality Synthesis Across Algorithmic Regimes

| Regime Category | Operational Condition | PFDC Behavior / Guarantee | Primary Competitor | Physical / Mathematical Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **Regime I: Dominance** | Adversarial $\ell_2$ Attack ($\varepsilon \ge 0.15$) | **100.0% Certified Invariance** | All DNNs Collapse ($13.45\%$) | Saturated Core $I \equiv 1.0 \implies \nabla \mathcal{L} \equiv \mathbf{0}$ (Zero Torque) |
| | Continuous XAI Recourse | **5.0$\times$ Faster, 100% Convergence** | Wachter Non-Convex ($3.3\%$) | Curl-Free Conservative Force Field ($\nabla \times \mathbf{F} \equiv \mathbf{0}$) |
| | High-D Sparse Signals ($D=1000$) | **75.87% Acc (#1 Non-Kernel)** | Trees Degrade ($70.27\%$) | $\ell_1$ Metric Tensor Pruning ($d_{\mathrm{eff}} \approx 20.0 \ll 1000$) |
| | Clustered Workloads ($N \ge 10^4$) | **Sub-linear $\mathcal{O}(\log N)$ Scaling** | RBF-SVM Quadratic | Compact Horizon $R^{\mathrm{horizon}}$ Prunes Exterior Spheres in $\mathcal{O}(1)$ |
| **Regime II: Competitive** | Standard Clean Tabular ($D \le 50$) | $94.29\%\text{--}97.23\%$ Accuracy | LightGBM, Kernel SVM | Dual Support Charges Match Bayes-Optimal Separability |
| | Balanced Multi-Class Settings | $94.88\%\text{--}96.63\%$ Accuracy | OvR RBF-SVM, Deep MLP | Boltzmann Softmax Maps Potential Ridges to Simplex |
| | Medium Tabular ($N=20,640$) | $83.72\%$ Acc, $3.26\times$ BallTree | TabNet ($84.59\%$), FT-Trans | Competitive with Deep Tabular + Certified Radius |
| **Regime III: Stress** | Undersampled Space ($N/D < 5$) | Accuracy Drops to $81.28\%$ | LightGBM ($86.59\%$) | Distance Concentration Degrades Anchor Core Estimation |
| | Moderate Noise ($10\%\text{--}25\%$) | Moderate Margin Distortion | Robust Ensemble | Inverted Polarity Anchors Induce Local Potential Vortices |
| | Class Imbalance ($> 1:10$) | Requires Bias $b^*$ Re-centering | Cost-Sensitive Boosting | Unmitigated Superposition Floats DC Ambient Ground Offset |
| **Regime IV: Breakdown** | Dense Unstructured High-D ($D > 10^4$) | Complete Metric Collapse | Convolutional Networks / ViT | $\lim_{D \to \infty} \sigma(d)/\mu(d) \to 0$ Across Raw Pixels |
| | Severe Label Noise ($> 30\%$) | Boundary Inversion Breakdown | Noise-Tolerant Loss Models | Opposing Cores Cancel Decision Margin ($R^{\mathrm{core}} \to 0$) |
| | Massive Unclustered Big Data ($N > 10^7$) | Storage / Kernel Memory Limit | Parametric DNNs | Non-Sparse Anchor Arrays Exceed Cache Hierarchy |
| | Distributional Overlap (Bayes Error $> 35\%$) | Core Assumption Collapses | Logistic Density Mixture | Identical Class Density Prevents Separation ($R^{\mathrm{core}} \to 0$) |
