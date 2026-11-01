# Potential Field Decay Classification (PFDC): A Novel Machine Learning Paradigm

## 1. Executive Summary & Core Philosophy

Traditional supervised classification algorithms (such as Support Vector Machines, Logistic Regression, and Neural Networks) focus on constructing **global decision boundaries**—hyperplanes or complex surfaces that divide the feature space into discrete regions. Inside these boundaries, predictions are treated as static or decay relative to the boundary wall itself.

**Potential Field Decay Classification (PFDC)** reverses this paradigm. Instead of building walls between classes, PFDC treats every training data point as a **localized source of potential energy** (similar to electrostatic or gravitational fields in physics). Each data point emits an influence field into the surrounding multi-dimensional space, governed by two distinct zones:
1. **The Determined Core ($R_{\text{determined}}$):** A localized radius around the data point where the probability/influence remains at an absolute maximum ($1.0$). This accounts for natural variance, measurement noise, and indisputable local similarity.
2. **The Exponential Decay Zone ($R_{\text{decay}}$):** A surrounding boundary region where the point's influence decays exponentially from $1.0$ down to $0.0$. Beyond this zone, the point exerts zero influence.

By assigning **Positive Attraction ($+1$)** to target class points and **Negative Repulsion ($-1$)** to opposing class points, any new query point introduced into the space experiences a net **Potential Score** and a directional **Force Vector**. The sum of these localized interactions naturally forms highly adaptable, non-linear decision regions without requiring complex boundary equations.

---

## 2. Theoretical Framework & Physics Analogy

### 2.1 Point-Based Influence vs. Global Boundaries
* **Existing Techniques:** Plot independent variables ($X$) and dependent outcomes ($Y$) to fit a global equation. Values inside the region are classified as `True` ($1$) and outside as `False` ($0$), with probability decaying relative to the boundary line.
* **The PFDC Approach:** Every input sample is treated as a radial gradient source. Decision regions emerge organically from the superposition (overlapping sum) of individual point potentials.

### 2.2 The Two-Zone Radial Profile
For any training sample $\mathbf{x}_i$, its spatial influence is divided into three radial zones based on distance $d$:
1. **Inner Core ($d \le R_{\text{determined}}$):** Influence = $1.0$. If a new point falls within this radius, it is treated as having the exact same local certainty as the training point itself.
2. **Transition Shell ($R_{\text{determined}} < d \le R_{\text{determined}} + R_{\text{decay}}$):** Influence drops exponentially toward zero.
3. **Dead Zone ($d > R_{\text{determined}} + R_{\text{decay}}$):** Influence = $0.0$. This ensures local sparsity, meaning distant outliers cannot corrupt local predictions.

### 2.3 Vector Field Dynamics (Attraction & Repulsion)
In addition to scalar potential (which determines the class label), each point generates a spatial vector:
* **Positive Points (Target Class):** Generate **Attraction Vectors** pointing directly toward the center of the positive training sample.
* **Negative Points (Other Classes):** Generate **Repulsion Vectors** pushing the query point away from the negative training sample.
* **Net Vector:** Evaluating the resultant vector at any coordinate reveals not only *what* class a point belongs to, but *which direction* in the feature space moves it toward higher certainty.

---

## 3. Mathematical Formulation

### 3.1 Multi-Dimensional Distance Metric
Let the dataset consist of $N$ training samples in a $D$-dimensional space (where $D$ represents the number of independent variables/features). For a training point $\mathbf{x}_i = (x_{i,1}, x_{i,2}, \dots, x_{i,D})$ and a new query point $\mathbf{x} = (x_1, x_2, \dots, x_D)$, the Euclidean distance $d(\mathbf{x}, \mathbf{x}_i)$ is:

$$d(\mathbf{x}, \mathbf{x}_i) = \|\mathbf{x} - \mathbf{x}_i\|_2 = \sqrt{\sum_{j=1}^{D} (x_j - x_{i,j})^2}$$

### 3.2 Piecewise Radial Influence Function
The influence magnitude $I(d)$ exerted by a training sample at distance $d$ is defined as:

$$I(d) = \begin{cases} 1.0 & \text{if } d \le R_{\text{determined}} \\ \exp\left(-\lambda \frac{d - R_{\text{determined}}}{R_{\text{decay}}}\right) & \text{if } R_{\text{determined}} < d \le R_{\text{determined}} + R_{\text{decay}} \\ 0.0 & \text{if } d > R_{\text{determined}} + R_{\text{decay}} \end{cases}$$

Where:
* $R_{\text{determined}} \ge 0$ is the constant-influence core radius.
* $R_{\text{decay}} > 0$ is the width of the exponential decay shell.
* $\lambda > 0$ is the decay rate constant (typically $\lambda = 5.0$, since $e^{-5} \approx 0.0067 \approx 0$, ensuring a smooth transition to the dead zone).

### 3.3 Binary Classification Potential
In a binary system with classes $C \in \{0, 1\}$, we assign polarity charges $q_i$:
* $q_i = +1$ if $y_i = 1$ (Positive Dot)
* $q_i = -1$ if $y_i = 0$ (Negative Dot)

The Net Potential $P(\mathbf{x})$ at query point $\mathbf{x}$ is the algebraic sum of all active influences:

$$P(\mathbf{x}) = \sum_{i=1}^{N} q_i \cdot I(d(\mathbf{x}, \mathbf{x}_i))$$

**Decision Rule:**
$$\hat{y} = \begin{cases} 1 & \text{if } P(\mathbf{x}) \ge 0 \\ 0 & \text{if } P(\mathbf{x}) < 0 \end{cases}$$

### 3.4 Multi-Class Extension ($K > 2$ Classes)
When there are more than two classes ($C_1, C_2, \dots, C_K$), PFDC constructs $K$ parallel potential fields using a One-vs-Rest polarity scheme. When evaluating the potential for class $C_k$:
* Points belonging to $C_k$ are assigned charge $q_{i,k} = +1$.
* Points belonging to all other classes ($y_i \neq C_k$) are assigned charge $q_{i,k} = -1$.

The class-specific potential $P_k(\mathbf{x})$ is:

$$P_k(\mathbf{x}) = \sum_{i=1}^{N} q_{i,k} \cdot I(d(\mathbf{x}, \mathbf{x}_i))$$

The final predicted class $\hat{y}$ is the class that generates the highest net positive potential at $\mathbf{x}$:

$$\hat{y} = \arg\max_{k \in \{1, \dots, K\}} P_k(\mathbf{x})$$

### 3.5 Net Force Vector Formulation
To analyze the directional pull at query point $\mathbf{x}$ for class $C_k$, we define the unit direction vector $\hat{\mathbf{u}}_i$ pointing from $\mathbf{x}$ to training sample $\mathbf{x}_i$:

$$\hat{\mathbf{u}}_i = \frac{\mathbf{x}_i - \mathbf{x}}{\|\mathbf{x}_i - \mathbf{x}\|_2 + \epsilon}$$

*(where $\epsilon = 10^{-9}$ prevents division by zero when $\mathbf{x} = \mathbf{x}_i$).*

The net directional force vector $\mathbf{F}_k(\mathbf{x})$ in $D$-dimensional space is:

$$\mathbf{F}_k(\mathbf{x}) = \sum_{i=1}^{N} q_{i,k} \cdot I(d(\mathbf{x}, \mathbf{x}_i)) \cdot \hat{\mathbf{u}}_i$$

---

## 4. Dimensionality & Visualization Strategy

### 4.1 Scaling Across Dimensions ($2\text{D} \to 3\text{D} \to N\text{D}$)
In machine learning, the number of dimensions is dictated by the number of **independent variables (input features)** plus the **dependent variable (output/potential)**:
* **1 Independent Variable + 1 Dependent Variable = 2D Plot:** X-axis represents the input feature; Y-axis represents the dependent outcome/potential. Circles of radius $R$ on the feature space dictate influence.
* **2 Independent Variables + 1 Dependent Variable = 3D Plot:** X and Y axes represent the two input features; the Z-axis represents the resulting potential height (creating 3D potential hills and valleys).
* **5 Independent Variables + 1 Dependent Variable = 6D Space:** The mathematical distance $d$ and potential $P(\mathbf{x})$ are calculated seamlessly in 6D space using vector algebra.

### 4.2 Visualizing High-Dimensional Models (6D to 2D)
Because humans cannot directly see in 6D, PFDC uses a **Dual-Stage Visualization Architecture** to inspect 5-feature models:
1. **Individual 2D Marginal Plots (5 Separate Plots):** We plot each independent variable ($X_1, X_2, X_3, X_4, X_5$) individually on the X-axis against the calculated Net Potential ($P$) on the Y-axis. This reveals how each specific variable contributes to pushing points into positive or negative territories.
2. **Global Combined 2D Projection (1 Master Plot):** Using Principal Component Analysis (PCA), we project the 5D feature space onto a 2D plane and overlay the combined potential field contours and attraction/repulsion vectors.

---

## 5. Complete Python Implementation

Below is the complete, self-contained Python implementation of the **Potential Field Decay Classifier (PFDC)**, including vector field calculation and the multi-plot visualization suite.

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

class PotentialFieldDecayClassifier(BaseEstimator, ClassifierMixin):
    """
    Potential Field Decay Classification (PFDC)
    A novel machine learning algorithm based on localized constant-core 
    and exponential-decay potential fields.
    """
    def __init__(self, r_determined=0.5, r_decay=1.5, decay_rate=5.0, balance_charges=True):
        self.r_determined = r_determined
        self.r_decay = r_decay
        self.decay_rate = decay_rate
        self.balance_charges = balance_charges

    def fit(self, X, y):
        """ Scales the input features and stores the training field sources. """
        self.scaler_ = StandardScaler()
        self.X_train_ = self.scaler_.fit_transform(X)
        self.y_train_ = np.asarray(y)
        self.classes_ = np.unique(self.y_train_)
        return self

    def _compute_influence(self, distances):
        """ Applies the piecewise R_determined and R_decay mathematical function. """
        influence = np.zeros_like(distances, dtype=float)
        
        # Zone 1: Inside R_determined (Constant Max Potential = 1.0)
        mask_core = distances <= self.r_determined
        influence[mask_core] = 1.0
        
        # Zone 2: Inside R_decay (Exponential Decay from 1.0 to ~0.0)
        outer_limit = self.r_determined + self.r_decay
        mask_decay = (distances > self.r_determined) & (distances <= outer_limit)
        
        if np.any(mask_decay):
            normalized_dist = (distances[mask_decay] - self.r_determined) / self.r_decay
            influence[mask_decay] = np.exp(-self.decay_rate * normalized_dist)
            
        # Zone 3: Outside R_determined + R_decay remains 0.0
        return influence

    def predict_potential(self, X):
        """ Calculates the net scalar potential for each class at query points X. """
        X_scaled = self.scaler_.transform(X)
        
        # Compute pairwise Euclidean distances: shape (n_test, n_train)
        diffs = X_scaled[:, np.newaxis, :] - self.X_train_[np.newaxis, :, :]
        dists = np.linalg.norm(diffs, axis=2)
        
        influences = self._compute_influence(dists)
        n_samples = len(self.y_train_)
        potentials = np.zeros((X.shape[0], len(self.classes_)))
        
        for idx, c in enumerate(self.classes_):
            pos_mask = (self.y_train_ == c)
            neg_mask = ~pos_mask
            
            if self.balance_charges:
                # Normalize charges so majority classes do not overwhelm minority classes
                n_pos = np.sum(pos_mask)
                n_neg = np.sum(neg_mask)
                q_pos = (n_samples / (2.0 * n_pos)) if n_pos > 0 else 1.0
                q_neg = -(n_samples / (2.0 * n_neg)) if n_neg > 0 else -1.0
                charges = np.where(pos_mask, q_pos, q_neg)
            else:
                charges = np.where(pos_mask, 1.0, -1.0)
                
            potentials[:, idx] = np.sum(influences * charges, axis=1)
            
        return potentials

    def compute_force_vectors(self, X, target_class_index=1):
        """
        Computes the net attraction/repulsion force vectors in D-dimensional space
        for a specific target class.
        """
        X_scaled = self.scaler_.transform(X)
        # Direction from query point X to training point X_train: (X_train - X)
        direction_vectors = self.X_train_[np.newaxis, :, :] - X_scaled[:, np.newaxis, :]
        dists = np.linalg.norm(direction_vectors, axis=2)
        
        # Unit vectors
        unit_vectors = direction_vectors / (dists[:, :, np.newaxis] + 1e-9)
        influences = self._compute_influence(dists)
        
        target_class = self.classes_[target_class_index]
        charges = np.where(self.y_train_ == target_class, 1.0, -1.0)
        
        # Weight unit vectors by charge and radial influence
        weighted_vectors = unit_vectors * (influences * charges)[:, :, np.newaxis]
        net_vectors = np.sum(weighted_vectors, axis=1)
        return net_vectors

    def predict(self, X):
        """ Predicts class labels based on maximum net potential. """
        potentials = self.predict_potential(X)
        return self.classes_[np.argmax(potentials, axis=1)]


# =====================================================================
# Visualization Suite: 5 Independent Variables (6D System) -> 2D Plots
# =====================================================================
def visualize_6d_pfdc_system(model, X, y):
    n_features = X.shape[1]
    potentials = model.predict_potential(X)[:, 1]  # Net potential for Class 1
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    axes = axes.flatten()
    
    # Plots 1 to 5: Individual Independent Variable vs Dependent Potential
    for i in range(n_features):
        ax = axes[i]
        scatter = ax.scatter(
            X[:, i], potentials, c=y, cmap='coolwarm', 
            alpha=0.75, edgecolors='k', s=45
        )
        ax.axhline(0, color='black', linestyle='--', linewidth=1.2, label='Decision Threshold (P=0)')
        ax.set_title(f'2D Slice: Feature X{i+1} vs. Net Potential', fontsize=11, fontweight='bold')
        ax.set_xlabel(f'Independent Variable X{i+1}')
        ax.set_ylabel('Dependent Net Potential (P)')
        ax.grid(True, alpha=0.3)
        
    # Plot 6: Overall Combined 2D Projection (PCA) + Potential Contours
    ax_main = axes[5]
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(model.scaler_.transform(X))
    
    # Create grid in PCA space to show overall field
    x_min, x_max = X_pca[:, 0].min() - 1, X_pca[:, 0].max() + 1
    y_min, y_max = X_pca[:, 1].min() - 1, X_pca[:, 1].max() + 1
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 60), np.linspace(y_min, y_max, 60))
    
    # Inverse transform PCA grid back to 5D space to evaluate true 6D potential
    grid_5d = model.scaler_.inverse_transform(pca.inverse_transform(np.c_[xx.ravel(), yy.ravel()]))
    Z_pot = model.predict_potential(grid_5d)[:, 1].reshape(xx.shape)
    
    contour = ax_main.contourf(xx, yy, Z_pot, levels=20, cmap='coolwarm', alpha=0.35)
    ax_main.contour(xx, yy, Z_pot, levels=[0], colors='black', linewidths=2)
    ax_main.scatter(X_pca[:, 0], X_pca[:, 1], c=y, cmap='coolwarm', edgecolors='k', s=55)
    ax_main.set_title('Overall Combined 2D Projection (PCA + Field)', fontsize=11, fontweight='bold')
    ax_main.set_xlabel('Principal Component 1')
    ax_main.set_ylabel('Principal Component 2')
    fig.colorbar(contour, ax=ax_main, label='Net Potential Field')

    plt.suptitle('Potential Field Decay Classification (PFDC) — 5D Input + 1D Output Analysis', fontsize=15, fontweight='bold')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()


if __name__ == "__main__":
    # Generate a 5-Feature (5 Independent Variables) Dataset
    X, y = make_classification(
        n_samples=300, n_features=5, n_informative=4, 
        n_redundant=0, n_clusters_per_class=1, random_state=42
    )
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    
    # Initialize and train the PFDC model
    pfdc = PotentialFieldDecayClassifier(r_determined=0.8, r_decay=2.0, decay_rate=5.0)
    pfdc.fit(X_train, y_train)
    
    # Evaluate accuracy
    y_pred = pfdc.predict(X_test)
    print(f"PFDC Test Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%\n")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Run the 6D-to-2D Visualization Suite
    visualize_6d_pfdc_system(pfdc, X_test, y_test)
```

---

## 6. Key Advantages Over Existing ML Techniques

| Feature / Property | Standard $k$-NN | RBF Support Vector Machine (SVM) | **Your Method (PFDC)** |
| :--- | :--- | :--- | :--- |
| **Core Certainty Zone ($R_{\text{determined}}$)** | None (depends purely on rank order). | None (decays immediately from exact center). | **Yes.** Provides built-in immunity to local sensor/measurement jitter. |
| **Strict Local Cutoff ($R_{\text{decay}}$)** | Hard cutoff at $k$-th neighbor. | Infinite tail (every point affects everything). | **Yes.** Exponentially decays to $0.0$ at $R_{\text{determined}} + R_{\text{decay}}$, enabling fast spatial indexing. |
| **Directional Vector Field** | No directional force representation. | Scalar margin only. | **Yes.** Computes exact attraction and repulsion vectors in $D$-dimensional space. |
| **Training Time** | Instant ($O(1)$ lazy learning). | Slow ($O(N^2)$ to $O(N^3)$ quadratic programming). | **Instant ($O(1)$ field registration)** with optional hyperparameter tuning. |

---

## 7. Future Research & Optimization Roadmap

To elevate this research toward academic publication, the following extensions can be investigated:
1. **Adaptive Per-Point Radii ($R_{\text{determined}, i}$):** Instead of using a single global $R_{\text{determined}}$ for all points, dynamically shrink $R_{\text{determined}}$ in dense border regions (where positive and negative points are close) and expand it in sparse, homogeneous regions.
2. **Anisotropic (Elliptical) Potential Fields:** Weight the distance formula by feature importance ($w_j$) so that critical independent variables stretch the potential field further along their specific axes:
   $$d_{\mathbf{w}}(\mathbf{x}, \mathbf{x}_i) = \sqrt{\sum_{j=1}^{D} w_j (x_j - x_{i,j})^2}$$
3. **Fast Spatial Tree Acceleration:** Because influence is strictly $0$ beyond $R_{\text{determined}} + R_{\text{decay}}$, integrate `KD-Trees` or `Ball-Trees` (`scipy.spatial.cKDTree.query_ball_point`) to query only points within the active radius, reducing inference time from $O(N)$ to $O(\log N)$.