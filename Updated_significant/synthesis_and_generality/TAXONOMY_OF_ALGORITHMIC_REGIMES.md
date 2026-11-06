# Taxonomy of Algorithmic Regimes: Operational Boundaries, Generality Synthesis, and Failure Modes

**Publication Synthesis for Elsevier *Pattern Recognition***  
**Authors:** Vishal Chandel and Adarsh Chandel  
**Permanent Software DOI:** [10.5281/zenodo.23936990](https://doi.org/10.5281/zenodo.23936990)

---

## Executive Abstract of Generality
A rigorous, archival pattern recognition framework cannot merely assert universal superiority across arbitrary benchmarks. Scientific value requires establishing a formal **operational boundary map**: defining precisely where the mathematical and physical inductive biases of Potential Field Decay Classification (PFDC) confer decisive advantages, where performance is competitive or neutral, and where structural pathologies cause the algorithm to degrade or fail.

```
+---------------------------------------------------------------------------------------------------+
|                                 PFDC OPERATIONAL REGIME MAP                                       |
+---------------------------------------------------------------------------------------------------+
|  REGIME I: PERFORMANCE DOMINANCE        |  REGIME II: COMPETITIVE / EQUIVALENT                    |
|  - Low/Medium Intrinsic Dim (D_eff <= 30) |  - Standard Clean Tabular Data (D <= 50, N <= 10^5)    |
|  - Safety-Critical Certified Invariance |  - Balanced Multi-Class Settings                        |
|  - Fast Continuous Counterfactual Recourse |  - Mixed Categorical/Continuous (with Subspace Stacking)|
|  - Spatially Clustered Datasets (BallTree)|                                                       |
|------------------------------------------+--------------------------------------------------------|
|  REGIME III: DEGRADATION & STRESS        |  REGIME IV: STRUCTURAL BREAKDOWN / FAILURE             |
|  - Low Sample-to-Dim Ratio (N/D < 5)     |  - Dense Unstructured High-D Manifolds (D > 10^4, raw) |
|  - Moderate Label Flip Noise (10% - 25%) |  - Extreme Label Corruption (> 30% inverted charges)   |
|  - Moderate Class Imbalance (> 1:10)     |  - Complete Distributional Overlap (Bayes Error > 35%) |
|                                          |  - Ultra-Scale Unclustered Big Data (N > 10^7 unpruned)|
+---------------------------------------------------------------------------------------------------+
```

---

## 1. Regime I: Performance Dominance (Where PFDC Outperforms SOTA)

PFDC achieves clear empirical and theoretical dominance under four specific operational conditions:

### 1.1 Safety-Critical Environments Under Adversarial Threat
* **Operational Criterion:** The system must guarantee mathematical invariance against $\ell_2$ bounded perturbations $\|\boldsymbol{\delta}\|_2 \le \varepsilon$ without relying on empirical adversarial training.
* **Why PFDC Dominates:** Traditional models (Deep MLPs, ResNets) possess non-zero loss gradients $\nabla_{\mathbf{x}} \mathcal{L} \ne \mathbf{0}$ throughout the input space. As demonstrated in Table 11 and Figure 16, iterative PGD/FGSM attacks collapse Deep MLP accuracy from $97.08\%$ to $13.45\%$ at $\varepsilon = 0.35$. In sharp contrast, PFDC establishes **Certainty Basins** where the influence function is saturated ($I(d) \equiv 1.0$), forcing $\nabla_{\mathbf{x}} \mathcal{L} \equiv \mathbf{0}$. With gradient torque identically zero, gradient-based adversaries cannot compute an ascent direction, guaranteeing **100.0% certified adversarial invariance** within $R^{\mathrm{core}}$.

### 1.2 Explainable AI Requiring Instantaneous, Guaranteed Recourse
* **Operational Criterion:** The decision subject requires an actionable, minimum-effort feature modification vector $\mathbf{x} \to \mathbf{x}^*$ transitioning into the favorable class.
* **Why PFDC Dominates:** Classical recourse frameworks (e.g., Wachter et al., DiCE) formulate recourse as a non-convex optimization problem solved via iterative gradient descent. These methods frequently get trapped in local saddle points, oscillate across boundaries, and require expensive inference loops ($62.1\text{ ms}$). PFDC provides a continuous, conservative directional force vector field $\mathbf{F}(\mathbf{x}) = -\nabla P(\mathbf{x})$. Because $\nabla \times \mathbf{F} \equiv \mathbf{0}$, streamlines integrate natively via ODE solvers, converging **5.0× faster ($12.4\text{ ms}$)** with **100% convergence guarantee**.

### 1.3 High-Dimensional Sparse Feature Spaces with Low Intrinsic Dimensionality
* **Operational Criterion:** Ambient dimensionality is large ($D \ge 500$), but discriminative signal is concentrated in a smaller subspace ($d_{\mathrm{eff}} \le 30$).
* **Why PFDC Dominates:** As shown in Table 6 ($N=2,500, D=1,000$), standard tree ensembles suffer severe feature fragmentation across noise splits (Random Forest $70.27\%$, XGBoost $72.00\%$, LightGBM $72.80\%$). Isotropic kernels fail due to measure concentration. PFDC's learned metric tensor $\mathbf{W} = \mathrm{diag}(\mathbf{w})$ with $\ell_1$ sparsity penalty actively drives uninformative dimensions to zero ($w_j \to 0$), collapsing intrinsic dimensionality to $d_{\mathrm{eff}} \approx 20.0$ and achieving **75.87% accuracy** (ranking #1 among non-kernel methods).

### 1.4 Large Reference Datasets with Spatial Clustering Structure
* **Operational Criterion:** Inference latency must scale sub-linearly with training set size $N$.
* **Why PFDC Dominates:** Gaussian RBF networks maintain infinite spatial tails ($K(d) > 0, \forall d$), forcing exhaustive $\mathcal{O}(N)$ distance computations. PFDC's compact support horizon ($I(d) \equiv 0$ for $d > R^{\mathrm{horizon}}$) enables exact hierarchical spatial Ball-Tree indexing, accelerating query evaluation from $48.0\text{ ms}$ to $17.1\text{ ms}$ (**2.81× speedup at $N=10,000$**) with zero approximation error ($< 10^{-14}$ error).

---

## 2. Regime II: Competitive / Equivalent Performance

Under standard benchmark conditions, PFDC performs comparably to optimized baseline ensembles:
* **Clean Tabular Benchmarks ($D \le 50, N \in [10^3, 10^5]$):** On Breast Cancer ($96.84\%$) and Ionosphere ($94.29\%$), PFDC matches LightGBM ($96.84\%$) and Kernel SVM ($94.30\%$). On Banknote Authentication ($D=4$), PFDC achieves $97.23 \pm 1.05\%$.
* **Medium-Scale Tabular Datasets:** On California Housing ($N=20,640, D=8$), PFDC achieves $83.72\%$, closely trailing specialized deep tabular architectures (TabNet $84.59\%$, FT-Transformer $86.87\%$) while offering closed-form certified radius guarantees that deep networks lack.

---

## 3. Regime III: Degradation & Stress Sensitivity

When operational conditions diverge from ideal physical assumptions, PFDC exhibits measurable sensitivity:

### 3.1 Low Sample-to-Dimensionality Ratio ($N/D < 5$)
* **Manifestation:** On Sonar ($N=208, D=60, N/D = 3.47$), isotropic PFDC achieves $76.00\%$. While Dual-Charge calibration recovers performance to **81.28 ± 4.12%**, it trails Kernel SVM ($84.13\%$) and LightGBM ($86.59\%$).
* **Mechanism:** In undersampled high-dimensional regimes, Euclidean distances concentrate, making it difficult to estimate accurate anchor decay radii without overfitting. Tree ensembles with random feature subsampling are more resilient to small $N/D$ ratios.

### 3.2 Label Corruption & Anchor Polarity Inversion (10% to 25% Noise)
* **Manifestation:** If labels contain random noise, mislabeled training points act as inverted electrostatic charges placed inside the core of the opposing class.
* **Mechanism:** An inverted point creates a local potential vortex / false attractor basin. While HAEPO regularizer $C$ prunes isolated outliers, sustained label noise degrades core radius estimation.

---

## 4. Regime IV: Structural Breakdown / Failure Modes (Where PFDC Should NOT Be Used)

To ensure scientific honesty and guide practical engineering, we document four structural failure regimes:

| Failure Regime | Mathematical Root Cause | Recommended Alternative |
| :--- | :--- | :--- |
| **1. Dense Unstructured High-D ($D > 10^4$, raw images/audio)** | Hyperspherical measure concentration ($\lim_{D \to \infty} \sigma(d)/\mu(d) = 0$). Distance metric becomes diffuse across uncompressed pixels. | Deep Convolutional Networks (CNNs), Vision Transformers (ViT) |
| **2. Severe Label Noise (> 30% label corruption)** | Inverted polarity anchors saturate local basins, distorting zero-potential decision separatrix. | Robust Loss Ensembles, Noise-Tolerant Generalized Cross-Entropy |
| **3. Massive Scale Unclustered Data ($N > 10^7$)** | Storing and querying non-sparse anchor arrays requires significant memory compared to constant-size weights in parametric DNNs. | Parametric Neural Networks, Quantized Linear Models |
| **4. Extreme Distributional Overlap (Bayes Error > 35%)** | When classes share identical spatial density, non-overlapping certainty core assumption ($R^{\mathrm{core}} > 0$) collapses to $R^{\mathrm{core}} \to 0$. | Probabilistic Logistic Regression, Mixture of Density Experts |

---

## 5. Synthesis & Empirical Generalization Matrix

The table below synthesizes performance across varied operational axes:

| Operational Condition | PFDC Rank | Primary Competitor | Critical Advantage / Limiting Factor |
| :--- | :---: | :--- | :--- |
| **Low-Dim Separable ($D \le 10$)** | **#1** | Kernel SVM | Certainty cores eliminate false overconfidence in voids. |
| **High-D with Sparse Signal ($D=1000$)** | **#2 (Non-kernel #1)** | Kernel SVM (RBF) | Metric tensor prunes 990 noise coordinates; defeats tree boosting. |
| **Adversarial $\ell_2$ Attack ($\varepsilon \ge 0.15$)** | **#1 (Dominant)** | All models collapse | Flat Certainty Basins provide 100% certified mathematical immunity. |
| **Recourse Query Latency** | **#1 (5.0× faster)** | Wachter Non-convex | Curl-free force field streamlines guarantee monotonic descent. |
| **Sub-Linear Query Scaling ($N > 10^4$)** | **#1 (2.81× speedup)** | Scikit-Learn RBF | Compact support horizon enables exact Ball-Tree pruning. |
| **Undersampled Feature Space ($N/D < 5$)** | **#4** | LightGBM, SVM | Radial distance concentration degrades core estimation. |
