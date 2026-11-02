"""
run_real_stacking_benchmark.py
Empirical Demonstration of Multi-Dimensional Orthogonal Subspace Stacking on Real Data:
1. 2D Subspace Overlapping: n 2D plots (each feature x_j vs y), weighted superposition.
2. 3D Common-Pivot Stacking: fixing x_pivot common to all plots, generating (n-1) 3D surfaces.
3. Generates publication-grade figure: figures/real_dataset_stacking_architecture.png
4. Generates benchmark CSV: figures/stacking_empirical_results.csv
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import TwoSlopeNorm
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score

OUTPUT_DIR = "figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Publication typography
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 16
plt.rcParams['axes.titlesize'] = 19
plt.rcParams['axes.labelsize'] = 17
plt.rcParams['xtick.labelsize'] = 14
plt.rcParams['ytick.labelsize'] = 14
plt.rcParams['legend.fontsize'] = 14
plt.rcParams['figure.titlesize'] = 24

# Load real clinical dataset: Breast Cancer Wisconsin
data = load_breast_cancer()
X_full, y = data.data, data.target
# Map to {-1, +1} for physical potential charges
y_sign = np.where(y == 1, +1.0, -1.0) # Class 1: Benign (+), Class 0: Malignant (-)

# Select top 4 informative clinical features for clear visual stacking demonstration
# Feature 0: mean radius, Feature 1: mean texture, Feature 2: mean perimeter, Feature 3: mean area
feature_names = [data.feature_names[0], data.feature_names[1], data.feature_names[2], data.feature_names[3]]
feature_labels = ['Radius ($x_1$)', 'Texture ($x_2$)', 'Perimeter ($x_3$)', 'Area ($x_4$)']
X = X_full[:, [0, 1, 2, 3]]

X_train, X_test, y_train, y_test, y_sign_train, y_sign_test = train_test_split(
    X, y, y_sign, test_size=0.3, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc = scaler.transform(X_test)

N_train, D = X_train_sc.shape

# -------------------------------------------------------------------------
# Step 1: Compute 1D/2D Subspace Potential Functions P_j(x_j)
# -------------------------------------------------------------------------
# Kernel bandwidth for 1D:
r_core_1d = 0.25
r_decay_1d = 1.2

def compute_1d_potential(x_eval_1d, x_train_1d, y_train_sign):
    # Pairwise distance in 1D
    dists = np.abs(x_eval_1d[:, None] - x_train_1d[None, :])
    I = np.zeros_like(dists)
    mask_core = dists <= r_core_1d
    mask_decay = (dists > r_core_1d) & (dists <= (r_core_1d + r_decay_1d))
    I[mask_core] = 1.0
    u = (dists[mask_decay] - r_core_1d) / r_decay_1d
    I[mask_decay] = np.exp(-2.0 * (u ** 2))
    return np.dot(I, y_train_sign) / np.sqrt(N_train)

# Evaluate 2D potentials for each feature on train and test
P_train_2d = np.zeros((N_train, D))
P_test_2d = np.zeros((len(X_test_sc), D))

for j in range(D):
    P_train_2d[:, j] = compute_1d_potential(X_train_sc[:, j], X_train_sc[:, j], y_sign_train)
    P_test_2d[:, j] = compute_1d_potential(X_test_sc[:, j], X_train_sc[:, j], y_sign_train)

# Learn optimal Variable Weights w_j via convex regularized logistic regression
clf_stacking_2d = LogisticRegression(fit_intercept=True, C=2.0)
clf_stacking_2d.fit(P_train_2d, y_train)

var_weights_2d = clf_stacking_2d.coef_[0]
bias_2d = clf_stacking_2d.intercept_[0]
# Normalize variable weights to sum to 1.0 for physical clarity
sum_w = np.sum(np.abs(var_weights_2d)) + 1e-6
var_weights_norm = np.abs(var_weights_2d) / sum_w

# Evaluate 2D stacked prediction
y_pred_2d_stack = clf_stacking_2d.predict(P_test_2d)
acc_2d_stack = accuracy_score(y_test, y_pred_2d_stack) * 100.0
f1_2d_stack = f1_score(y_test, y_pred_2d_stack)

# Individual feature accuracies
acc_individual = []
for j in range(D):
    pred_j = np.where(P_test_2d[:, j] >= 0, 1, 0)
    acc_individual.append(accuracy_score(y_test, pred_j) * 100.0)

# -------------------------------------------------------------------------
# Step 2: 3D Common-Pivot Stacking (Taking x_pivot = x_1 common to all plots)
# -------------------------------------------------------------------------
# Pairwise 3D subspaces: (x_1, x_2), (x_1, x_3), (x_1, x_4) -> (D-1) 3D surfaces
pivot_idx = 0 # Feature 0: Radius is common pivot
other_indices = [1, 2, 3] # Texture, Perimeter, Area

def compute_2d_bivariate_potential(X_eval_pair, X_train_pair, y_train_sign):
    dists = np.sqrt(np.sum((X_eval_pair[:, None, :] - X_train_pair[None, :, :]) ** 2, axis=2))
    I = np.zeros_like(dists)
    r_core = 0.35
    r_decay = 1.6
    I[dists <= r_core] = 1.0
    mask_decay = (dists > r_core) & (dists <= (r_core + r_decay))
    u = (dists[mask_decay] - r_core) / r_decay
    I[mask_decay] = np.exp(-2.0 * (u ** 2))
    return np.dot(I, y_train_sign) / np.sqrt(N_train)

P_train_3d = np.zeros((N_train, len(other_indices)))
P_test_3d = np.zeros((len(X_test_sc), len(other_indices)))

for k, other_idx in enumerate(other_indices):
    train_pair = X_train_sc[:, [pivot_idx, other_idx]]
    test_pair = X_test_sc[:, [pivot_idx, other_idx]]
    P_train_3d[:, k] = compute_2d_bivariate_potential(train_pair, train_pair, y_sign_train)
    P_test_3d[:, k] = compute_2d_bivariate_potential(test_pair, train_pair, y_sign_train)

clf_stacking_3d = LogisticRegression(fit_intercept=True, C=2.0)
clf_stacking_3d.fit(P_train_3d, y_train)

var_weights_3d = clf_stacking_3d.coef_[0]
bias_3d = clf_stacking_3d.intercept_[0]
y_pred_3d_stack = clf_stacking_3d.predict(P_test_3d)
acc_3d_stack = accuracy_score(y_test, y_pred_3d_stack) * 100.0
f1_3d_stack = f1_score(y_test, y_pred_3d_stack)

# Save Benchmark Results
results_df = pd.DataFrame({
    'Architecture': [
        f'Individual 2D: {feature_labels[0]}',
        f'Individual 2D: {feature_labels[1]}',
        f'Individual 2D: {feature_labels[2]}',
        f'Individual 2D: {feature_labels[3]}',
        'Composite 2D Overlapped Stacking (All 4 Features)',
        'Common-Pivot 3D Manifold Stacking (Pivot: Radius x1)'
    ],
    'Learned Variable Weight (w_j)': [
        f'{var_weights_norm[0]:.3f}',
        f'{var_weights_norm[1]:.3f}',
        f'{var_weights_norm[2]:.3f}',
        f'{var_weights_norm[3]:.3f}',
        'Learned Vector w in R^4',
        f'w_pivot + {len(other_indices)} Subspace Weights'
    ],
    'Test Accuracy (%)': [
        f'{acc_individual[0]:.2f}%',
        f'{acc_individual[1]:.2f}%',
        f'{acc_individual[2]:.2f}%',
        f'{acc_individual[3]:.2f}%',
        f'{acc_2d_stack:.2f}%',
        f'{acc_3d_stack:.2f}%'
    ],
    'Test F1-Score': [
        f'{f1_score(y_test, np.where(P_test_2d[:, 0] >= 0, 1, 0)):.4f}',
        f'{f1_score(y_test, np.where(P_test_2d[:, 1] >= 0, 1, 0)):.4f}',
        f'{f1_score(y_test, np.where(P_test_2d[:, 2] >= 0, 1, 0)):.4f}',
        f'{f1_score(y_test, np.where(P_test_2d[:, 3] >= 0, 1, 0)):.4f}',
        f'{f1_2d_stack:.4f}',
        f'{f1_3d_stack:.4f}'
    ]
})
results_df.to_csv(os.path.join(OUTPUT_DIR, "stacking_empirical_results.csv"), index=False)
print("Empirical Stacking Benchmark Table:")
print(results_df.to_string(index=False))

# -------------------------------------------------------------------------
# Step 3: Multi-Panel Visualization of 2D & 3D Stacking Architecture
# -------------------------------------------------------------------------
fig = plt.figure(figsize=(26, 13.5))

# Subplot 1: 2D Subspace Potential Curves for each Independent Variable
ax1 = fig.add_subplot(2, 2, 1)
x_eval_grid = np.linspace(-3.0, 3.0, 200)

colors_feat = ['#e74c3c', '#3498db', '#2ecc71', '#9b59b6']
for j in range(D):
    p_curve = compute_1d_potential(x_eval_grid, X_train_sc[:, j], y_sign_train)
    ax1.plot(x_eval_grid, p_curve, color=colors_feat[j], linewidth=2.8,
             label=f'{feature_labels[j]} ($w_{j+1}^*={var_weights_norm[j]:.2f}$, Acc={acc_individual[j]:.1f}%)')

ax1.axhline(0.0, color='black', linestyle='--', linewidth=2.0, label='Zero-Threshold Separatrix ($P_j=0$)')
ax1.set_title('(a) Individual 2D Independent Variable Potential Curves $P_j(x_j)$', fontweight='bold', pad=14)
ax1.set_xlabel('Normalized Feature Value (Standard Deviations)', fontweight='bold')
ax1.set_ylabel('Subspace Potential $P_j(x_j)$', fontweight='bold')
ax1.legend(loc='upper right', framealpha=0.92, edgecolor='#cccccc', fontsize=12)
ax1.grid(True, linestyle='--', alpha=0.35)

# Subplot 2: Composite 2D Overlapped Stacking Field
ax2 = fig.add_subplot(2, 2, 2)
# Show superposition of radius (x1) vs texture (x2) with all 4 weights active
x1_grid = np.linspace(-2.5, 2.5, 80)
x2_grid = np.linspace(-2.5, 2.5, 80)
X1_g, X2_g = np.meshgrid(x1_grid, x2_grid)

# Stacked potential across the 2 primary visual axes
p1_g = compute_1d_potential(X1_g.ravel(), X_train_sc[:, 0], y_sign_train).reshape(X1_g.shape)
p2_g = compute_1d_potential(X2_g.ravel(), X_train_sc[:, 1], y_sign_train).reshape(X2_g.shape)
p_stacked_vis = var_weights_norm[0] * p1_g + var_weights_norm[1] * p2_g + bias_2d

norm_stack = TwoSlopeNorm(vmin=min(-0.1, p_stacked_vis.min()), vcenter=0.0, vmax=max(0.1, p_stacked_vis.max()))
cf2 = ax2.contourf(X1_g, X2_g, p_stacked_vis, levels=25, cmap='coolwarm', norm=norm_stack, alpha=0.45)
cbar2 = plt.colorbar(cf2, ax=ax2, pad=0.03)
cbar2.set_label('Stacked Potential $P_{\\mathrm{stacked}}(\\mathbf{x})$', fontweight='bold', fontsize=14)

# Contours
ax2.contour(X1_g, X2_g, p_stacked_vis, levels=[0.0], colors='black', linewidths=3.0)
ax2.scatter(X_test_sc[y_test == 0, 0], X_test_sc[y_test == 0, 1], color='#1f77b4', s=60, edgecolors='black', label='Malignant (Class 0: Blue)')
ax2.scatter(X_test_sc[y_test == 1, 0], X_test_sc[y_test == 1, 1], color='#d62728', s=60, edgecolors='black', label='Benign (Class 1: Red)')

ax2.set_title(f'(b) Composite 2D Overlapped Stacking Field (Test Acc: {acc_2d_stack:.2f}%)', fontweight='bold', pad=14)
ax2.set_xlabel('Normalized Radius $x_1$ ($w_1^* = ' + f'{var_weights_norm[0]:.2f}$)', fontweight='bold')
ax2.set_ylabel('Normalized Texture $x_2$ ($w_2^* = ' + f'{var_weights_norm[1]:.2f}$)', fontweight='bold')
ax2.legend(loc='lower left', framealpha=0.92, edgecolor='#cccccc', fontsize=12)
ax2.grid(True, linestyle='--', alpha=0.35)

# Subplot 3: 3D Common-Pivot Subspace 1: (x_pivot, x_2, P)
ax3 = fig.add_subplot(2, 2, 3, projection='3d')
x_p_grid = np.linspace(-2.2, 2.2, 50)
x_k_grid = np.linspace(-2.2, 2.2, 50)
XP, XK = np.meshgrid(x_p_grid, x_k_grid)
pts_pair = np.c_[XP.ravel(), XK.ravel()]

p_3d_sub1 = compute_2d_bivariate_potential(pts_pair, X_train_sc[:, [0, 1]], y_sign_train).reshape(XP.shape)
norm_3d_1 = TwoSlopeNorm(vmin=min(-0.1, p_3d_sub1.min()), vcenter=0.0, vmax=max(0.1, p_3d_sub1.max()))
ax3.plot_surface(XP, XK, p_3d_sub1, cmap='coolwarm', norm=norm_3d_1, edgecolor='none', alpha=0.85)
ax3.plot_wireframe(XP, XK, np.zeros_like(XP), color='gray', linestyle=':', linewidth=0.8, alpha=0.35)

ax3.set_title(r'(c) Common-Pivot 3D Subspace 1: $(x_{\mathrm{radius}}, x_{\mathrm{texture}}, P_1)$', fontweight='bold', pad=14)
ax3.set_xlabel('$x_1$ (Radius)', fontweight='bold', labelpad=8)
ax3.set_ylabel('$x_2$ (Texture)', fontweight='bold', labelpad=8)
ax3.set_zlabel('Potential $P_1$', fontweight='bold', labelpad=8)
ax3.view_init(elev=30, azim=130)

# Subplot 4: 3D Common-Pivot Subspace 2: (x_pivot, x_3, P)
ax4 = fig.add_subplot(2, 2, 4, projection='3d')
p_3d_sub2 = compute_2d_bivariate_potential(pts_pair, X_train_sc[:, [0, 2]], y_sign_train).reshape(XP.shape)
norm_3d_2 = TwoSlopeNorm(vmin=min(-0.1, p_3d_sub2.min()), vcenter=0.0, vmax=max(0.1, p_3d_sub2.max()))
ax4.plot_surface(XP, XK, p_3d_sub2, cmap='coolwarm', norm=norm_3d_2, edgecolor='none', alpha=0.85)
ax4.plot_wireframe(XP, XK, np.zeros_like(XP), color='gray', linestyle=':', linewidth=0.8, alpha=0.35)

ax4.set_title(r'(d) Common-Pivot 3D Subspace 2: $(x_{\mathrm{radius}}, x_{\mathrm{perimeter}}, P_2)$' + f'\n(Combined 3D Stack Acc: {acc_3d_stack:.2f}%)', fontweight='bold', pad=14)
ax4.set_xlabel('$x_1$ (Radius)', fontweight='bold', labelpad=8)
ax4.set_ylabel('$x_3$ (Perimeter)', fontweight='bold', labelpad=8)
ax4.set_zlabel('Potential $P_2$', fontweight='bold', labelpad=8)
ax4.view_init(elev=30, azim=130)

plt.suptitle('Multi-Dimensional Subspace Stacking on Real Clinical Data: 2D Overlapping & Common-Pivot 3D Superposition', fontsize=23, fontweight='bold', y=0.99)
plt.subplots_adjust(left=0.05, right=0.95, bottom=0.06, top=0.92, wspace=0.22, hspace=0.26)

out_fig = os.path.join(OUTPUT_DIR, "real_dataset_stacking_architecture.png")
plt.savefig(out_fig, dpi=300, bbox_inches='tight')
plt.close()
print(f"Successfully generated real dataset stacking figure: {out_fig}")
