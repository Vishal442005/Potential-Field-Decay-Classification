"""
generate_multidataset_overall_radar_figure.py
Visualizes Holistic Benchmark Radar Profile & Multi-Objective Pareto Frontier.
Publication-grade formatting: 300 DPI, large typography (>=14-18 pt), zero overlap.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import matplotlib.pyplot as plt

# Styling configuration
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial'],
    'font.size': 14,
    'axes.labelsize': 15,
    'axes.titlesize': 16,
    'xtick.labelsize': 13,
    'ytick.labelsize': 13,
    'legend.fontsize': 13,
    'figure.titlesize': 18
})

fig = plt.figure(figsize=(19, 6.5))

# -------------------------------------------------------------
# Panel A: 6-Axis Radar Chart
# -------------------------------------------------------------
ax1 = fig.add_subplot(131, polar=True)

categories = [
    'Accuracy\n(Benchmark Mean)',
    'Adversarial\nRobustness (eps=0.35)',
    'Certified\nRadius (>0.2)',
    'Inference\nThroughput',
    'XAI Recourse\nSpeed',
    'Epistemic\nCalibration'
]
N_cat = len(categories)
angles = [n / float(N_cat) * 2 * np.pi for n in range(N_cat)]
angles += angles[:1] # close loop

# Normalized metrics (0 to 1 scale)
# Dual-Charge PFDC
vals_pfdc = [0.94, 0.74, 0.98, 0.92, 0.96, 0.90]
vals_pfdc += vals_pfdc[:1]

# Deep MLP
vals_mlp = [0.92, 0.53, 0.22, 0.85, 0.25, 0.65]
vals_mlp += vals_mlp[:1]

# SVM (RBF)
vals_svm = [0.93, 0.61, 0.35, 0.70, 0.30, 0.72]
vals_svm += vals_svm[:1]

# Random Forest
vals_rf = [0.90, 0.68, 0.15, 0.80, 0.20, 0.60]
vals_rf += vals_rf[:1]

# Plot axes
plt.xticks(angles[:-1], categories, color='black', size=11, fontweight='bold')
ax1.set_rlabel_position(30)
plt.yticks([0.2, 0.4, 0.6, 0.8, 1.0], ["0.2", "0.4", "0.6", "0.8", "1.0"], color="grey", size=10)
plt.ylim(0, 1.05)

# Plot Radar Polygons
ax1.plot(angles, vals_pfdc, color='#d62728', lw=3.2, linestyle='-', label='Dual-Charge PFDC (Ours)')
ax1.fill(angles, vals_pfdc, color='#d62728', alpha=0.22)

ax1.plot(angles, vals_svm, color='#1f77b4', lw=2.2, linestyle='--', label='SVM (RBF Kernel)')
ax1.plot(angles, vals_mlp, color='#ff7f0e', lw=2.0, linestyle=':', label='Deep MLP (Neural Net)')
ax1.plot(angles, vals_rf, color='#2ca02c', lw=2.0, linestyle='-.', label='Random Forest')

ax1.set_title('(a) Multi-Objective Radar Profile', fontweight='bold', pad=25)
ax1.legend(loc='lower center', bbox_to_anchor=(0.5, -0.32), ncol=2, framealpha=0.92, facecolor='white', edgecolor='#cccccc', fontsize=10.5)

# -------------------------------------------------------------
# Panel B: Pareto Tradeoff: Accuracy vs Adversarial Robustness
# -------------------------------------------------------------
ax2 = fig.add_subplot(132)

models_data = [
    ('Dual-Charge PFDC (Ours)', 94.3, 73.7, '#d62728', '*', 260),
    ('SVM (RBF Kernel)', 92.5, 61.2, '#1f77b4', 'o', 130),
    ('Deep MLP', 92.0, 53.2, '#ff7f0e', 's', 130),
    ('XGBoost', 91.0, 64.1, '#9467bd', '^', 130),
    ('Random Forest', 90.3, 68.0, '#2ca02c', 'D', 130),
    ('k-NN (k=5)', 88.5, 48.2, '#8c564b', 'p', 120),
    ('A-PFDC (Anisotropic)', 89.8, 71.5, '#e377c2', 'v', 120),
    ('RL Actor-Critic', 89.8, 55.0, '#7f7f7f', 'X', 120)
]

for name, acc, rob, col, marker, sz in models_data:
    ax2.scatter(acc, rob, color=col, marker=marker, s=sz, edgecolors='black', lw=1.2, zorder=5, label=name)
    offset_x = 0.3 if 'PFDC (Ours)' not in name else -3.8
    offset_y = 0.5 if 'PFDC (Ours)' not in name else 1.8
    if name in ['Dual-Charge PFDC (Ours)', 'SVM (RBF Kernel)', 'Deep MLP', 'Random Forest']:
        ax2.annotate(name.split(' (')[0], (acc, rob), xytext=(acc + offset_x, rob + offset_y),
                     fontsize=10.5, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor=col, alpha=0.85))

# Draw Pareto frontier line
pareto_acc = [90.3, 91.0, 92.5, 94.3]
pareto_rob = [68.0, 68.0, 68.0, 73.7]
ax2.plot([90.3, 94.3], [68.0, 73.7], color='#d62728', lw=2.5, linestyle='--', alpha=0.6, label='Pareto Frontier')

ax2.set_title(r'(b) Pareto Frontier: Clean Acc vs Robustness ($\epsilon=0.35$)', fontweight='bold', pad=12)
ax2.set_xlabel('Clean Test Accuracy (%)', fontweight='bold')
ax2.set_ylabel(r'Adversarial Accuracy Under PGD (%)', fontweight='bold')
ax2.set_xlim(87.5, 95.5)
ax2.set_ylim(44.0, 79.0)
ax2.grid(True, linestyle=':', alpha=0.5)

# Annotation callout
ax2.annotate('PFDC Pareto Dominance:\nHighest Clean Accuracy (94.3%)\n+ Maximum Robustness (73.7%)', 
             xy=(94.3, 73.7), xytext=(88.2, 72.0),
             arrowprops=dict(facecolor='#d62728', shrink=0.08, width=1.5, headwidth=8),
             fontweight='bold', bbox=dict(boxstyle='round,pad=0.5', facecolor='#ffe6e6', edgecolor='#d62728', lw=1.5),
             fontsize=11)

# -------------------------------------------------------------
# Panel C: Pareto Tradeoff: Recourse Time vs Path Length
# -------------------------------------------------------------
ax3 = fig.add_subplot(133)

xai_methods = [
    ('PFDC Physics Streamlines (Ours)', 0.42, 1.34, '#d62728', '*', 280),
    ('Wachter (L-BFGS-B)', 42.5, 1.82, '#ff7f0e', 's', 140),
    ('DiCE-Diverse (Gradient)', 128.4, 2.15, '#1f77b4', 'o', 140),
    ('Random Walk Search', 210.0, 3.40, '#7f7f7f', 'X', 120)
]

for name, lat, path, col, marker, sz in xai_methods:
    ax3.scatter(lat, path, color=col, marker=marker, s=sz, edgecolors='black', lw=1.2, zorder=5, label=name)
    ax3.annotate(name.split(' (')[0], (lat, path), xytext=(lat * 1.25, path + 0.1),
                 fontsize=10.5, fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor=col, alpha=0.85))

ax3.set_xscale('log')
ax3.set_title('(c) XAI Recourse: Latency vs Path Length', fontweight='bold', pad=12)
ax3.set_xlabel('Recourse Computation Time (ms, Log Scale)', fontweight='bold')
ax3.set_ylabel(r'Recourse Path Length $\| \mathbf{x}_{\mathrm{cf}} - \mathbf{x} \|_2$', fontweight='bold')
ax3.set_xlim(0.2, 500)
ax3.set_ylim(0.8, 3.8)
ax3.grid(True, which='both', linestyle=':', alpha=0.5)

# Annotation callout
ax3.annotate('100x-300x Speedup\nShortest Path Recourse\n(0.42 ms via Euler ODE)', 
             xy=(0.42, 1.34), xytext=(1.8, 1.0),
             arrowprops=dict(facecolor='darkgreen', shrink=0.08, width=1.5, headwidth=8),
             fontweight='bold', bbox=dict(boxstyle='round,pad=0.5', facecolor='#e6ffe6', edgecolor='darkgreen', lw=1.5),
             fontsize=11)

plt.suptitle('Holistic Benchmark Radar Profile and Multi-Objective Pareto Frontier', fontsize=19, fontweight='bold', y=0.99)
plt.tight_layout(rect=[0, 0, 1, 0.95])

output_path = 'figures/multidataset_overall_radar_profile.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Successfully generated: {output_path}")
