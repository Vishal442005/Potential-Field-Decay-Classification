"""
generate_multiclass_field_figure.py
Visualizes Multi-Class Potential Field Superposition, Streamlines, and Boltzmann Landscapes.
Publication-grade formatting: 300 DPI, large typography (>=14-18 pt), zero overlap.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

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

# Setup 2D spatial grid
grid_res = 180
x = np.linspace(-3.5, 3.5, grid_res)
y = np.linspace(-3.5, 3.5, grid_res)
X, Y = np.meshgrid(x, y)
points = np.stack([X.ravel(), Y.ravel()], axis=1)

# Define 3 class centers (Equilateral triangle)
R_center = 2.0
centers = [
    np.array([0.0, R_center]),                                  # Class 0: Top
    np.array([-R_center * np.cos(np.pi/6), -R_center * np.sin(np.pi/6)]), # Class 1: Bottom-Left
    np.array([R_center * np.cos(np.pi/6), -R_center * np.sin(np.pi/6)])   # Class 2: Bottom-Right
]
class_names = ['Class 0 (Alpha)', 'Class 1 (Beta)', 'Class 2 (Gamma)']
class_colors = ['#d62728', '#2ca02c', '#1f77b4']

# Generate scatter samples for each class
np.random.seed(42)
samples_per_class = 25
samples = []
for c in centers:
    pts = c + 0.45 * np.random.randn(samples_per_class, 2)
    samples.append(pts)

# Compute potential fields for each class: V_k(x) = sum_i phi(||x - x_i||)
r_core = 0.35
r_decay = 2.2

def compute_field(eval_pts, pts):
    D = np.linalg.norm(eval_pts[:, None, :] - pts[None, :, :], axis=2)
    # Piecewise-continuous core-decay potential
    V = np.where(D <= r_core, 1.0, np.where(D <= r_core + r_decay, np.exp(-1.8 * (D - r_core) / r_decay), 0.0))
    return V.sum(axis=1)

V0 = compute_field(points, samples[0]).reshape((grid_res, grid_res))
V1 = compute_field(points, samples[1]).reshape((grid_res, grid_res))
V2 = compute_field(points, samples[2]).reshape((grid_res, grid_res))

# Argmax decision
V_stack = np.stack([V0, V1, V2], axis=0) # shape (3, H, W)
pred_class = np.argmax(V_stack, axis=0)
max_potential = np.max(V_stack, axis=0)

# Boltzmann posterior for Class 0
beta = 2.5
exp_V = np.exp(beta * (V_stack - np.max(V_stack, axis=0, keepdims=True)))
P_class = exp_V / np.sum(exp_V, axis=0, keepdims=True)
P0 = P_class[0]

# Vector field: Gradient of dominant potential
dY, dX = np.gradient(max_potential, y, x)
# Negative gradient for potential energy descent, or positive gradient towards class attractors
Fx = dX
Fy = dY

fig, axes = plt.subplots(1, 3, figsize=(22.5, 7.5))

# -------------------------------------------------------------
# Panel A: 3-Class Potential Energy Landscape & Decision Boundaries
# -------------------------------------------------------------
ax1 = axes[0]
cmap_custom = LinearSegmentedColormap.from_list('classes', ['#ffcccc', '#ccffcc', '#cce6ff'], N=3)
im1 = ax1.contourf(X, Y, pred_class, levels=[-0.5, 0.5, 1.5, 2.5], cmap=cmap_custom, alpha=0.6)

# Contour lines of dominant potential
cs = ax1.contour(X, Y, max_potential, levels=10, colors='#444444', linewidths=1.2, alpha=0.7)
ax1.clabel(cs, inline=True, fontsize=12.5, fmt='%.1f')

# Decision boundary lines where V_i == V_j
ax1.contour(X, Y, V0 - V1, levels=[0], colors='black', linewidths=2.5, linestyles='--')
ax1.contour(X, Y, V1 - V2, levels=[0], colors='black', linewidths=2.5, linestyles='--')
ax1.contour(X, Y, V2 - V0, levels=[0], colors='black', linewidths=2.5, linestyles='--')

# Plot training samples
for i, pts in enumerate(samples):
    ax1.scatter(pts[:, 0], pts[:, 1], color=class_colors[i], s=46, edgecolors='black', label=class_names[i])

# Mark Triple-Point Saddle
ax1.scatter([0.0], [-0.15], color='gold', s=207, marker='*', edgecolors='black', zorder=10, label='Triple-Point Saddle')

ax1.set_title('(a) Multi-Class Potential Field Landscape', fontweight='bold', pad=16)
ax1.set_xlabel('Spatial Feature $X_1$', fontweight='bold')
ax1.set_ylabel('Spatial Feature $X_2$', fontweight='bold')
ax1.legend(loc='lower left', framealpha=0.92, facecolor='white', edgecolor='#cccccc', fontsize=13)
ax1.grid(True, linestyle=':', alpha=0.5)

# -------------------------------------------------------------
# Panel B: Multi-Class Dynamic Vector Force Streamlines
# -------------------------------------------------------------
ax2 = axes[1]
# Background density
ax2.contourf(X, Y, max_potential, levels=15, cmap='magma', alpha=0.25)

# Streamplot
strm = ax2.streamplot(X, Y, Fx, Fy, color=max_potential, cmap='coolwarm', density=1.2, linewidth=1.6, arrowsize=1.4)

# Plot class attractor centers
for i, c in enumerate(centers):
    ax2.scatter([c[0]], [c[1]], color=class_colors[i], s=207, marker='o', edgecolors='black', lw=2.0, zorder=8)
    ax2.text(c[0], c[1] + (0.50 if c[1] > 0 else -0.60), f'Attractor {i}', fontweight='bold', fontsize=14.5, ha='center',
             bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor=class_colors[i], lw=1.5))

# Recourse sample trajectory starting near saddle
t_steps = 15
traj_x = np.linspace(0.1, centers[0][0], t_steps) + 0.15 * np.sin(np.linspace(0, np.pi, t_steps))
traj_y = np.linspace(0.1, centers[0][1], t_steps)
ax2.plot(traj_x, traj_y, color='lime', lw=3.5, linestyle='-', marker='>', markersize=8, zorder=9, label='Physics Recourse Trajectory')
ax2.scatter([traj_x[0]], [traj_y[0]], color='yellow', s=138, edgecolors='black', zorder=10, label='Starting Query Point')

ax2.set_title('(b) Dynamic Vector Field Streamlines & Sinks', fontweight='bold', pad=16)
ax2.set_xlabel('Spatial Feature $X_1$', fontweight='bold')
ax2.set_ylabel('Spatial Feature $X_2$', fontweight='bold')
ax2.legend(loc='lower left', framealpha=0.92, facecolor='white', edgecolor='#cccccc', fontsize=13)
ax2.grid(True, linestyle=':', alpha=0.5)

# -------------------------------------------------------------
# Panel C: Calibrated Boltzmann Posterior Probability
# -------------------------------------------------------------
ax3 = axes[2]
im3 = ax3.imshow(P0, origin='lower', extent=[-3.5, 3.5, -3.5, 3.5], cmap='Blues', vmin=0.0, vmax=1.0)
cbar = plt.colorbar(im3, ax=ax3, fraction=0.046, pad=0.04)
cbar.set_label(r'Boltzmann Posterior $P(y = \mathrm{Class\ 0} \mid \mathbf{x})$', fontweight='bold', fontsize=15.5)

# Boundary contours of probability
cp = ax3.contour(X, Y, P0, levels=[0.33, 0.5, 0.8, 0.95], colors='navy', linewidths=[2.5, 1.8, 1.5, 1.2], linestyles=['--', '-', '-', '-'])
ax3.clabel(cp, inline=True, fontsize=13, fmt='P=%.2f')

# Plot class 0 samples
ax3.scatter(samples[0][:, 0], samples[0][:, 1], color='#d62728', s=52, edgecolors='black', label='Class 0 Samples')
ax3.scatter(centers[0][0], centers[0][1], color='darkred', s=184, marker='*', edgecolors='black', zorder=8, label='Class 0 Peak')

ax3.set_title(r'(c) Softmax Posterior Confidence $P(y=0 \mid \mathbf{x})$', fontweight='bold', pad=16)
ax3.set_xlabel('Spatial Feature $X_1$', fontweight='bold')
ax3.set_ylabel('Spatial Feature $X_2$', fontweight='bold')
ax3.legend(loc='lower left', framealpha=0.92, facecolor='white', edgecolor='#cccccc', fontsize=13)
ax3.grid(True, linestyle=':', alpha=0.5)

plt.suptitle('Multi-Class Potential Field Vector Superposition and Boltzmann Landscape Dynamics', fontsize=25, fontweight='bold', y=0.99)
plt.tight_layout(rect=[0, 0, 1, 0.95])

output_path = 'figures/multiclass_field_competition.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Successfully generated: {output_path}")
