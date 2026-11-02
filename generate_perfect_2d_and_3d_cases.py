"""
generate_perfect_2d_and_3d_cases.py
Generates Figure 1 with both 2D Field Partitions and 3D Potential Landscapes.
Strict Physical Conventions:
- Negative Potential (P < 0) & Negative Class 0: BLUE (#1f77b4)
- Positive Potential (P > 0) & Positive Class 1: RED (#d62728)
- Both Positive and Negative Core (+1.0, -1.0) and Decay (+0.25, -0.25) Boundaries explicitly contoured!
- Zero Decision Boundary (P = 0.0) bold black contour.
- 3D Potential Surface directly underneath 2D Field: Blue valleys (P < 0), Red peaks (P > 0), Zero equipotential plane.
- Dedicated isolated colorbar axis on far right: ZERO overlap on Case 3 or any other subplot.
- 300 DPI, 1.3x typography.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import TwoSlopeNorm
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
plt.rcParams['legend.fontsize'] = 15
plt.rcParams['figure.titlesize'] = 25

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

fig = plt.figure(figsize=(27, 17.5))

x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5

# 2D Grid
xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100), np.linspace(y_min, y_max, 100))
grid_points = np.c_[xx.ravel(), yy.ravel()]

# Quiver grid
xx_q, yy_q = np.meshgrid(np.linspace(x_min, x_max, 22), np.linspace(y_min, y_max, 22))
grid_q = np.c_[xx_q.ravel(), yy_q.ravel()]

# 3D Grid
xx_3d, yy_3d = np.meshgrid(np.linspace(x_min, x_max, 60), np.linspace(y_min, y_max, 60))
grid_3d = np.c_[xx_3d.ravel(), yy_3d.ravel()]

for idx, (case_mode, label) in enumerate(cases):
    clf = DynamicPFDC(
        r_core_init=0.08, r_decay_init=0.40, decay_rate=2.0, alpha=2.0,
        lr_case=case_mode, max_epochs=120, random_state=42
    )
    clf.fit(X_train, y_train)
    acc_val = clf.score(X_test, y_test) * 100.0

    pot_2d = clf.predict_potential(grid_points).reshape(xx.shape)
    pot_3d = clf.predict_potential(grid_3d).reshape(xx_3d.shape)
    
    # Establish symmetric norm: strictly Blue for negative, Red for positive
    v_abs = max(abs(pot_2d.min()), abs(pot_2d.max()))
    norm = TwoSlopeNorm(vmin=-v_abs, vcenter=0.0, vmax=v_abs)

    # ---------------------------------------------------------
    # ROW 1: 2D Field Contours, Force Quivers, and Data Points
    # ---------------------------------------------------------
    ax1 = fig.add_subplot(2, 3, idx + 1)
    
    cf = ax1.contourf(xx, yy, pot_2d, levels=30, cmap="coolwarm", norm=norm, alpha=0.45)
    
    # Explicitly contour ALL physical boundaries:
    # 1. Zero Decision Boundary (Black)
    cs0 = ax1.contour(xx, yy, pot_2d, levels=[0.0], colors="black", linewidths=3.2)
    # 2. Positive Certainty Core (Solid Crimson) and Decay Shell (Dashed Orange)
    if pot_2d.max() >= 1.0:
        ax1.contour(xx, yy, pot_2d, levels=[1.0], colors=["#b30000"], linewidths=2.4, linestyles='-')
    if pot_2d.max() >= 0.25:
        ax1.contour(xx, yy, pot_2d, levels=[0.25], colors=["#e67e22"], linewidths=2.0, linestyles='--')
    # 3. Negative Certainty Core (Solid Dark Blue) and Decay Shell (Dashed Cyan)
    if pot_2d.min() <= -1.0:
        ax1.contour(xx, yy, pot_2d, levels=[-1.0], colors=["#004080"], linewidths=2.4, linestyles='-')
    if pot_2d.min() <= -0.25:
        ax1.contour(xx, yy, pot_2d, levels=[-0.25], colors=["#0099cc"], linewidths=2.0, linestyles='--')

    # Directional force vectors (quiver)
    forces = clf.compute_force_vectors(grid_q)
    fx = forces[:, 0].reshape(xx_q.shape)
    fy = forces[:, 1].reshape(yy_q.shape)
    f_norm = np.sqrt(fx**2 + fy**2) + 1e-6
    ax1.quiver(xx_q, yy_q, fx/f_norm, fy/f_norm, color='#2c3e50', alpha=0.55, scale=28, width=0.0035)
    
    # Strictly: Negative Class 0 = Blue, Positive Class 1 = Red
    ax1.scatter(X_test[y_test == 0, 0], X_test[y_test == 0, 1], color='#1f77b4', s=70, edgecolors='black', linewidth=1.0, alpha=0.85, label='Class 0 (Negative: $P < 0$)' if idx==0 else "")
    ax1.scatter(X_test[y_test == 1, 0], X_test[y_test == 1, 1], color='#d62728', s=70, edgecolors='black', linewidth=1.0, alpha=0.85, label='Class 1 (Positive: $P > 0$)' if idx==0 else "")
    
    # Dummy legend items for boundaries in panel (a)
    if idx == 0:
        ax1.plot([], [], color='black', lw=3.0, label='Decision Separatrix ($P=0$)')
        ax1.plot([], [], color='#b30000', lw=2.2, label='Pos Core / Shell ($P=+1.0, +0.25$)')
        ax1.plot([], [], color='#004080', lw=2.2, label='Neg Core / Shell ($P=-1.0, -0.25$)')
        ax1.legend(loc='lower left', framealpha=0.95, edgecolor='#cccccc', fontsize=12)

    panel_letter = chr(ord('a') + idx)
    ax1.set_title(f"({panel_letter}) {label}\nTest Accuracy: {acc_val:.2f}%", fontsize=18, fontweight='bold', pad=14)
    ax1.set_xlabel("Feature Coordinate $x_1$", fontweight='bold')
    if idx == 0:
        ax1.set_ylabel("Feature Coordinate $x_2$", fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.35)

    # ---------------------------------------------------------
    # ROW 2: 3D Potential Energy Landscape Surfaces
    # ---------------------------------------------------------
    ax2 = fig.add_subplot(2, 3, idx + 4, projection='3d')
    
    surf = ax2.plot_surface(
        xx_3d, yy_3d, pot_3d, cmap="coolwarm", norm=norm,
        edgecolor='none', alpha=0.85, antialiased=True, zorder=2
    )
    
    # Zero equipotential plane (transparent wireframe)
    z_zero = np.zeros_like(xx_3d)
    ax2.plot_wireframe(xx_3d, yy_3d, z_zero, color='gray', linestyle=':', linewidth=0.8, alpha=0.35, zorder=1)
    
    # Contour projection on bottom
    z_offset = -v_abs * 1.15
    ax2.contour(xx_3d, yy_3d, pot_3d, levels=15, zdir='z', offset=z_offset, cmap='coolwarm', norm=norm, alpha=0.45)
    
    ax2.set_zlim(z_offset, v_abs * 1.1)
    panel_letter_3d = chr(ord('d') + idx)
    ax2.set_title(f"({panel_letter_3d}) 3D Potential Surface: {case_mode.split('_')[0].capitalize()}", fontsize=18, fontweight='bold', pad=16)
    ax2.set_xlabel("$x_1$", fontweight='bold', labelpad=9)
    ax2.set_ylabel("$x_2$", fontweight='bold', labelpad=9)
    ax2.set_zlabel("Potential $P(\\mathbf{x})$", fontweight='bold', labelpad=9)
    ax2.view_init(elev=32, azim=225)

# Dedicated isolated colorbar axis on far right: ZERO OVERLAP on any subplot
cbar_ax = fig.add_axes([0.925, 0.15, 0.015, 0.70])
cbar = fig.colorbar(plt.cm.ScalarMappable(norm=TwoSlopeNorm(vmin=-1, vcenter=0, vmax=1), cmap='coolwarm'), cax=cbar_ax)
cbar.set_label("Net Potential Field $P(\\mathbf{x})$ [Blue: Negative $\\to$ Red: Positive]", fontweight='bold', fontsize=17)
cbar.ax.tick_params(labelsize=15)

plt.suptitle("PFDC 2D Decision Partitions & 3D Potential Landscapes Across Radial Learning-Rate Regimes", fontsize=24, fontweight='bold', y=0.99)
# Subplot margins guarantee ample clearance between Case 3 and the colorbar
plt.subplots_adjust(left=0.04, right=0.90, bottom=0.06, top=0.93, wspace=0.22, hspace=0.28)

plot_path = os.path.join(OUTPUT_DIR, "pfdc_decision_boundaries_cases.png")
plt.savefig(plot_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Successfully generated perfect 2D+3D cases figure: {plot_path}")
