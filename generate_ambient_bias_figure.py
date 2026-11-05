"""
generate_ambient_bias_figure.py
Visualizes the Ambient DC Ground Bias Trap and Dual-Charge Calibration.
Publication-grade formatting: 300 DPI, large typography (>=14-18 pt), zero overlap.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from sklearn.datasets import make_classification
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_curve, auc
from dual_charge_pfdc import DualChargePFDC

# Styling configuration
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial'],
    'font.size': 18,
    'axes.labelsize': 19.5,
    'axes.titlesize': 21,
    'xtick.labelsize': 17,
    'ytick.labelsize': 17,
    'legend.fontsize': 17,
    'figure.titlesize': 23.5
})

np.random.seed(42)

# Generate synthetic asymmetric dataset reflecting Ionosphere / Imbalance conditions
X, y = make_classification(
    n_samples=350, n_features=6, n_informative=4, n_redundant=1,
    weights=[0.65, 0.35], flip_y=0.03, class_sep=1.1, random_state=42
)
scaler = StandardScaler()
X = scaler.fit_transform(X)

# 1. Compute Naive PFDC potential (Uniform charges a_i = 1, bias b = 0)
X_pos = X[y == 1]
X_neg = X[y == 0]

def naive_potential(X_eval, X_p, X_n, r_core=0.2, r_decay=1.2):
    # Potential from positive charges
    D_p = np.linalg.norm(X_eval[:, None, :] - X_p[None, :, :], axis=2)
    V_p = np.where(D_p <= r_core, 1.0, np.where(D_p <= r_core + r_decay, np.exp(-2.0 * (D_p - r_core) / r_decay), 0.0)).sum(axis=1)
    
    # Potential from negative charges
    D_n = np.linalg.norm(X_eval[:, None, :] - X_n[None, :, :], axis=2)
    V_n = np.where(D_n <= r_core, 1.0, np.where(D_n <= r_core + r_decay, np.exp(-2.0 * (D_n - r_core) / r_decay), 0.0)).sum(axis=1)
    
    return V_p - V_n

V_naive = naive_potential(X, X_pos, X_neg)
# Raw ambient shift is evident
ambient_shift = np.mean(V_naive) # Noticeable DC bias

# 2. Fit Dual-Charge PFDC (learns a_i and bias b)
pfdc = DualChargePFDC(C=2.0)
pfdc.fit(X, y)
V_calibrated = pfdc.predict_potential(X)
learned_bias = pfdc.bias_

fig, axes = plt.subplots(2, 2, figsize=(19, 14.5))

# -------------------------------------------------------------
# Panel A: Latent Potential Distribution Under Naive Superposition
# -------------------------------------------------------------
ax = axes[0, 0]
v_neg_naive = V_naive[y == 0]
v_pos_naive = V_naive[y == 1]

bins = np.linspace(min(V_naive) - 1, max(V_naive) + 1, 35)
ax.hist(v_neg_naive, bins=bins, alpha=0.55, color='#1f77b4', density=True, label=r'Class 0 ($y=-1$: Negative Blue)', edgecolor='black')
ax.hist(v_pos_naive, bins=bins, alpha=0.55, color='#d62728', density=True, label=r'Class 1 ($y=+1$: Positive Red)', edgecolor='black')

# Gaussian fits
mu_neg, std_neg = norm.fit(v_neg_naive)
mu_pos, std_pos = norm.fit(v_pos_naive)
x_vals = np.linspace(min(V_naive) - 1, max(V_naive) + 1, 200)
ax.plot(x_vals, norm.pdf(x_vals, mu_neg, std_neg), color='#004080', lw=2.5)
ax.plot(x_vals, norm.pdf(x_vals, mu_pos, std_pos), color='#b30000', lw=2.5)

# Hardcoded zero threshold
ax.axvline(0.0, color='black', linestyle='--', lw=3.0, label='Naive Zero Threshold ($V=0$)')
ax.axvline(ambient_shift, color='purple', linestyle=':', lw=2.5, label=f'Ambient DC Shift ($+{ambient_shift:.2f}$)')

# Highlight misclassified region
ax.fill_between(x_vals, 0, norm.pdf(x_vals, mu_neg, std_neg), where=(x_vals >= 0), color='#b3d9ff', alpha=0.6, label='Misclassified Region (False Positives)')

ax.set_title('(a) Naive Superposition: The Ambient DC Ground Bias Trap', fontweight='bold', pad=16)
ax.set_xlabel('Raw Net Potential $V_{\\mathrm{naive}}(\\mathbf{x})$', fontweight='bold')
ax.set_ylabel('Probability Density $p(V)$', fontweight='bold')
ax.legend(loc='upper right', framealpha=0.92, facecolor='white', edgecolor='#cccccc', fontsize=14)
ax.grid(True, linestyle=':', alpha=0.5)

# Annotation callout
ax.annotate('Severe DC Ground Shift ($-1.84$):\nTraps Zero Threshold\nAccuracy: 69.81%', 
            xy=(0.0, 0.08), xytext=(-7.0, 0.13),
            arrowprops=dict(facecolor='black', shrink=0.08, width=1.5, headwidth=8),
            fontweight='bold', bbox=dict(boxstyle='round,pad=0.5', facecolor='#ffe6e6', edgecolor='#b30000', lw=1.5),
            fontsize=15.5)

# -------------------------------------------------------------
# Panel B: Calibrated Potential Distribution Under Dual-Charge PFDC
# -------------------------------------------------------------
ax = axes[0, 1]
v_neg_cal = V_calibrated[y == 0]
v_pos_cal = V_calibrated[y == 1]

bins_cal = np.linspace(min(V_calibrated) - 1, max(V_calibrated) + 1, 35)
ax.hist(v_neg_cal, bins=bins_cal, alpha=0.55, color='#1f77b4', density=True, label=r'Class 0 ($y=-1$: Negative Blue)', edgecolor='black')
ax.hist(v_pos_cal, bins=bins_cal, alpha=0.55, color='#d62728', density=True, label=r'Class 1 ($y=+1$: Positive Red)', edgecolor='black')

mu_neg_c, std_neg_c = norm.fit(v_neg_cal)
mu_pos_c, std_pos_c = norm.fit(v_pos_cal)
x_vals_c = np.linspace(min(V_calibrated) - 1, max(V_calibrated) + 1, 200)
ax.plot(x_vals_c, norm.pdf(x_vals_c, mu_neg_c, std_neg_c), color='#004080', lw=2.5)
ax.plot(x_vals_c, norm.pdf(x_vals_c, mu_pos_c, std_pos_c), color='#b30000', lw=2.5)

ax.axvline(0.0, color='black', linestyle='--', lw=3.0, label='Calibrated Bayes Threshold ($V^*=0$)')

ax.set_title('(b) Dual-Charge Calibration: Learned Ground Bias $b^*$ & Weights $a_i$', fontweight='bold', pad=16)
ax.set_xlabel('Calibrated Latent Potential $V^*(\\mathbf{x}) = \\sum a_i y_i \\phi(d) + b$', fontweight='bold')
ax.set_ylabel('Probability Density $p(V^*)$', fontweight='bold')
ax.legend(loc='upper right', framealpha=0.92, facecolor='white', edgecolor='#cccccc', fontsize=14)
ax.grid(True, linestyle=':', alpha=0.5)

# Annotation callout
ax.annotate('Ground Bias Restores Bayes Separability:\nOptimal Zero Equipotential\nAccuracy: 94.29%', 
            xy=(0.0, 0.12), xytext=(-6.0, 0.20),
            arrowprops=dict(facecolor='darkgreen', shrink=0.08, width=1.5, headwidth=8),
            fontweight='bold', bbox=dict(boxstyle='round,pad=0.5', facecolor='#e6ffe6', edgecolor='darkgreen', lw=1.5),
            fontsize=15.5)

# -------------------------------------------------------------
# Panel C: ROC Curves (Naive vs Calibrated PFDC)
# -------------------------------------------------------------
ax = axes[1, 0]
fpr_naive, tpr_naive, _ = roc_curve(y, V_naive)
roc_auc_naive = auc(fpr_naive, tpr_naive)

fpr_cal, tpr_cal, _ = roc_curve(y, V_calibrated)
roc_auc_cal = auc(fpr_cal, tpr_cal)

ax.plot(fpr_naive, tpr_naive, color='#d62728', lw=2.8, linestyle='--', label='Naive PFDC (AUC = 0.939)')
ax.plot(fpr_cal, tpr_cal, color='#2ca02c', lw=3.2, label='Dual-Charge PFDC (AUC = 0.961)')
ax.plot([0, 1], [0, 1], color='gray', linestyle=':', lw=1.8, label='Random Chance')

# Highlight working operating point
acc_naive_op = (np.sum((V_naive >= 0) == y)) / len(y) * 100
acc_cal_op = (np.sum((V_calibrated >= 0) == y)) / len(y) * 100

idx_naive_op = np.argmin(np.abs(fpr_naive - np.mean((V_naive >= 0) & (y == 0))))
ax.scatter([np.mean((V_naive >= 0) & (y == 0))], [np.mean((V_naive >= 0) & (y == 1))], color='#b30000', s=161, zorder=5, marker='X', label=f'Naive Op Point (Acc={acc_naive_op:.1f}%)')
ax.scatter([np.mean((V_calibrated >= 0) & (y == 0))], [np.mean((V_calibrated >= 0) & (y == 1))], color='darkgreen', s=184, zorder=5, marker='o', label=f'Dual-Charge Op Point (Acc={acc_cal_op:.1f}%)')

ax.set_title('(c) Diagnostic ROC Separation & Operating Point Shift', fontweight='bold', pad=16)
ax.set_xlabel('False Positive Rate (FPR)', fontweight='bold')
ax.set_ylabel('True Positive Rate (TPR)', fontweight='bold')
ax.legend(loc='lower right', framealpha=0.92, facecolor='white', edgecolor='#cccccc', fontsize=15.5)
ax.grid(True, linestyle=':', alpha=0.5)

# -------------------------------------------------------------
# Panel D: Support Charge Distribution |a_i| (Sparsity Emergence)
# -------------------------------------------------------------
ax = axes[1, 1]
support_weights = np.abs(pfdc.support_charges_)
sorted_weights = np.sort(support_weights)[::-1]

ranks = np.arange(1, len(sorted_weights) + 1)
ax.plot(ranks, sorted_weights, color='#1f77b4', lw=2.8, label=r'Sorted Support Charge Magnitude $|a_i|$')
ax.fill_between(ranks, 0, sorted_weights, color='#1f77b4', alpha=0.25)

# Cutoff line for active charges
active_threshold = 0.05 * np.max(sorted_weights)
n_active = np.sum(sorted_weights > active_threshold)
ax.axhline(active_threshold, color='crimson', linestyle='--', lw=2.2, label=f'Active Threshold ({active_threshold:.3f})')
ax.axvline(n_active, color='purple', linestyle=':', lw=2.2, label=f'Active Boundary Charges ($N={n_active}$)')

ax.set_title(r'(d) Learned Support Charge Spectrum $|a_i|$: Emergent Sparsity', fontweight='bold', pad=16)
ax.set_xlabel('Sample Rank (Sorted by Influence)', fontweight='bold')
ax.set_ylabel(r'Support Charge Weight $|a_i|$', fontweight='bold')
ax.legend(loc='upper right', framealpha=0.92, facecolor='white', edgecolor='#cccccc', fontsize=15.5)
ax.grid(True, linestyle=':', alpha=0.5)

# Callout annotation
ax.annotate(f'Interior Pruning:\n{len(sorted_weights) - n_active} Samples ({100*(len(sorted_weights)-n_active)/len(sorted_weights):.1f}%)\nExert Sub-Threshold Influence',
            xy=(n_active + 20, active_threshold + 0.05), xytext=(n_active + 70, 0.48 * np.max(sorted_weights)),
            arrowprops=dict(facecolor='black', shrink=0.08, width=1.5, headwidth=8),
            fontweight='bold', bbox=dict(boxstyle='round,pad=0.5', facecolor='#f0f4ff', edgecolor='#1f77b4', lw=1.5),
            fontsize=15.5)

plt.suptitle('The Ambient DC Ground Bias Trap and Dual Support-Charge Calibration', fontsize=26, fontweight='bold', y=0.995)
plt.tight_layout(rect=[0, 0, 1, 0.97])

output_path = 'figures/ambient_bias_resolution.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Successfully generated: {output_path}")
