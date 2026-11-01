"""
restyle_2d_cases.py
Re-styles 2D decision boundary cases with 1.3x font scaling, wider layout, and anti-overlap spacing.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from pfdc_engine import DynamicPFDC

OUTPUT_DIR = "figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1.3x scaled typography
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 18
plt.rcParams['axes.titlesize'] = 21
plt.rcParams['axes.labelsize'] = 19
plt.rcParams['xtick.labelsize'] = 16
plt.rcParams['ytick.labelsize'] = 16
plt.rcParams['legend.fontsize'] = 16
plt.rcParams['figure.titlesize'] = 24

# Generate standardized 2D non-linear multi-cluster data
X, y = make_classification(
    n_samples=1200, n_features=2, n_informative=2, n_redundant=0,
    n_clusters_per_class=2, flip_y=0.03, class_sep=1.15, random_state=42
)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

cases = [
    ("fixed", "Case 1: Fixed Rate (119 Limit Cycles)"),
    ("halved", "Case 2: Sign Halving (50 Sign Shifts)"),
    ("exponential_accelerating", "Case 3: Accelerating Exp (Ours: Settled in 8 Shifts)")
]

fig, axes = plt.subplots(1, 3, figsize=(26, 8.2))

x_min, x_max = X[:, 0].min() - 0.6, X[:, 0].max() + 0.6
y_min, y_max = X[:, 1].min() - 0.6, X[:, 1].max() + 0.6
xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100), np.linspace(y_min, y_max, 100))
grid_points = np.c_[xx.ravel(), yy.ravel()]

# Quiver grid
xx_q, yy_q = np.meshgrid(np.linspace(x_min, x_max, 20), np.linspace(y_min, y_max, 20))
grid_q = np.c_[xx_q.ravel(), yy_q.ravel()]

for idx, (case_mode, label) in enumerate(cases):
    ax = axes[idx]
    clf = DynamicPFDC(
        r_core_init=0.08, r_decay_init=0.40, decay_rate=2.0, alpha=2.0,
        lr_case=case_mode, max_epochs=120, random_state=42
    )
    clf.fit(X_train, y_train)
    pot_grid = clf.predict_potential(grid_points).reshape(xx.shape)
    
    # Potential contour
    cf = ax.contourf(xx, yy, pot_grid, levels=26, cmap="coolwarm", alpha=0.42)
    ax.contour(xx, yy, pot_grid, levels=[0], colors="black", linewidths=3.0)
    
    # Directional force vectors (quiver)
    forces = clf.compute_force_vectors(grid_q)
    fx = forces[:, 0].reshape(xx_q.shape)
    fy = forces[:, 1].reshape(yy_q.shape)
    norm = np.sqrt(fx**2 + fy**2) + 1e-6
    ax.quiver(xx_q, yy_q, fx/norm, fy/norm, color='#2c3e50', alpha=0.6, scale=28, width=0.0035)
    
    # Test scatter points
    ax.scatter(X_test[y_test == 0, 0], X_test[y_test == 0, 1], color='#e74c3c', s=70, edgecolors='black', linewidth=1.0, alpha=0.85, label='Class 0' if idx==0 else "")
    ax.scatter(X_test[y_test == 1, 0], X_test[y_test == 1, 1], color='#2980b9', s=70, edgecolors='black', linewidth=1.0, alpha=0.85, label='Class 1' if idx==0 else "")
    
    acc_val = clf.score(X_test, y_test) * 100.0
    ax.set_title(f"{label}\nTest Accuracy: {acc_val:.2f}%", fontsize=18, fontweight='bold', pad=14)
    ax.set_xlabel("Feature Coordinate $x_1$", fontweight='bold')
    if idx == 0:
        ax.set_ylabel("Feature Coordinate $x_2$", fontweight='bold')
        ax.legend(loc='lower left', framealpha=0.95, edgecolor='#cccccc', fontsize=16)
    ax.grid(True, linestyle='--', alpha=0.35)

cbar = fig.colorbar(cf, ax=axes.ravel().tolist(), pad=0.02, shrink=0.85)
cbar.set_label("Net Potential Field $P(\mathbf{x})$", fontweight='bold', fontsize=18)
cbar.ax.tick_params(labelsize=15)

plt.suptitle("PFDC 2D Potential Landscapes & Directional Force Fields Across Dynamic Learning-Rate Schedules", fontsize=23, fontweight='bold', y=0.99)
plt.tight_layout(rect=[0, 0, 0.95, 0.96])
plot2_path = os.path.join(OUTPUT_DIR, "pfdc_decision_boundaries_cases.png")
plt.savefig(plot2_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Successfully re-styled 2D cases figure: {plot2_path}")
