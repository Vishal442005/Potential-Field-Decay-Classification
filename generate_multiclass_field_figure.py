"""
generate_multiclass_field_figure.py
Visualizes Multi-Class Potential Field Superposition, Streamlines, and Boltzmann Landscapes.
Upgraded to 4 Panels (2x2) including a 3D Multi-Class Potential Surface.
Publication-grade formatting: 300 DPI, large typography (>=14-18 pt), zero overlap.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LinearSegmentedColormap

OUTPUT_DIR = "figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

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
    'figure.titlesize': 24
})

# Setup 2D spatial grid
grid_res = 160
x = np.linspace(-3.5, 3.5, grid_res)
y = np.linspace(-3.5, 3.5, grid_res)
X, Y = np.meshgrid(x, y)
points = np.stack([X.ravel(), Y.ravel()], axis=1)

# Define 3 class centers (Equilateral triangle)
R_center = 2.0
centers = [
    np.array([0.0, R_center]),                                            # Class 0: Top
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
Fx = dX
Fy = dY

fig = plt.figure(figsize=(22.5, 17.5))

# -------------------------------------------------------------
# Panel (a): 3D Multi-Class Potential Energy Landscape
# -------------------------------------------------------------
ax1 = fig.add_subplot(2, 2, 1, projection='3d')
x_3d = np.linspace(-3.5, 3.5, 60)
y_3d = np.linspace(-3.5, 3.5, 60)
X3, Y3 = np.meshgrid(x_3d, y_3d)
pts_3d = np.stack([X3.ravel(), Y3.ravel()], axis=1)

v0_3d = compute_field(pts_3d, samples[0]).reshape((60, 60))
v1_3d = compute_field(pts_3d, samples[1]).reshape((60, 60))
v2_3d = compute_field(pts_3d, samples[2]).reshape((60, 60))
max_pot_3d = np.maximum(np.maximum(v0_3d, v1_3d), v2_3d)

surf1 = ax1.plot_surface(X3, Y3, max_pot_3d, cmap='viridis', edgecolor='none', alpha=0.88, zorder=2)
ax1.contour(X3, Y3, max_pot_3d, zdir='z', offset=0.0, cmap='viridis', alpha=0.5, zorder=1)

# Mark the 3 class attractor centers on the 3D surface
for i, c in enumerate(centers):
    c_pt = c.reshape(1, 2)
    c_val = np.max([compute_field(c_pt, samples[k])[0] for k in range(3)])
    ax1.scatter([c[0]], [c[1]], [c_val + 0.5], color=class_colors[i], s=180, edgecolors='black', linewidth=1.8, zorder=8)

# Mark saddle
saddle_xy = np.array([[0.0, -0.15]])
saddle_val = np.max([compute_field(saddle_xy, samples[k])[0] for k in range(3)])
ax1.scatter([0.0], [-0.15], [saddle_val + 0.4], color='gold', s=230, marker='*', edgecolors='black', zorder=9, label='Triple-Point Saddle')

ax1.set_zlim(0.0, np.max(max_pot_3d) * 1.15)
ax1.set_title('(a) 3D Multi-Class Potential Surface $\\max_k V_k(\\mathbf{x})$', fontweight='bold', pad=16)
ax1.set_xlabel('$X_1$', fontweight='bold', labelpad=9)
ax1.set_ylabel('$X_2$', fontweight='bold', labelpad=9)
ax1.set_zlabel('Potential $V(\\mathbf{x})$', fontweight='bold', labelpad=9)
ax1.legend(loc='upper right', framealpha=0.92, edgecolor='#cccccc', fontsize=14)
ax1.view_init(elev=32, azim=225)

# -------------------------------------------------------------
# Panel (b): 2D Multi-Class Landscape & Decision Boundaries
# -------------------------------------------------------------
ax2 = fig.add_subplot(2, 2, 2)
cmap_custom = LinearSegmentedColormap.from_list('classes', ['#ffcccc', '#ccffcc', '#cce6ff'], N=3)
im2 = ax2.contourf(X, Y, pred_class, levels=[-0.5, 0.5, 1.5, 2.5], cmap=cmap_custom, alpha=0.6)

# Contour lines of dominant potential
cs = ax2.contour(X, Y, max_potential, levels=10, colors='#444444', linewidths=1.2, alpha=0.7)
ax2.clabel(cs, inline=True, fontsize=12.5, fmt='%.1f')

# Decision boundary lines where V_i == V_j
ax2.contour(X, Y, V0 - V1, levels=[0], colors='black', linewidths=2.5, linestyles='--')
ax2.contour(X, Y, V1 - V2, levels=[0], colors='black', linewidths=2.5, linestyles='--')
ax2.contour(X, Y, V2 - V0, levels=[0], colors='black', linewidths=2.5, linestyles='--')

# Plot training samples
for i, pts in enumerate(samples):
    ax2.scatter(pts[:, 0], pts[:, 1], color=class_colors[i], s=46, edgecolors='black', label=class_names[i])

# Mark Triple-Point Saddle
ax2.scatter([0.0], [-0.15], color='gold', s=207, marker='*', edgecolors='black', zorder=10, label='Triple-Point Saddle')

ax2.set_title('(b) 2D Equipotential Ridges & Boundaries', fontweight='bold', pad=16)
ax2.set_xlabel('Spatial Feature $X_1$', fontweight='bold')
ax2.set_ylabel('Spatial Feature $X_2$', fontweight='bold')
ax2.legend(loc='lower left', framealpha=0.92, facecolor='white', edgecolor='#cccccc', fontsize=13)
ax2.grid(True, linestyle=':', alpha=0.5)

# -------------------------------------------------------------
# Panel (c): Dynamic Vector Force Streamlines & Sinks
# -------------------------------------------------------------
ax3 = fig.add_subplot(2, 2, 3)
ax3.contourf(X, Y, max_potential, levels=15, cmap='magma', alpha=0.25)
strm = ax3.streamplot(X, Y, Fx, Fy, color=max_potential, cmap='coolwarm', density=1.2, linewidth=1.6, arrowsize=1.4)

for i, c in enumerate(centers):
    ax3.scatter([c[0]], [c[1]], color=class_colors[i], s=207, marker='o', edgecolors='black', lw=2.0, zorder=8)
    ax3.text(c[0], c[1] + (0.45 if c[1] > 0 else -0.55), f'Attractor {i}', fontweight='bold', fontsize=14.5, ha='center',
             bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor=class_colors[i], lw=1.5))

# Recourse trajectory starting near saddle
t_steps = 15
traj_x = np.linspace(0.1, centers[0][0], t_steps) + 0.15 * np.sin(np.linspace(0, np.pi, t_steps))
traj_y = np.linspace(0.1, centers[0][1], t_steps)
ax3.plot(traj_x, traj_y, color='lime', lw=3.5, linestyle='-', marker='>', markersize=8, zorder=9, label='Physics Recourse Trajectory')
ax3.scatter([traj_x[0]], [traj_y[0]], color='yellow', s=138, edgecolors='black', zorder=10, label='Starting Query Point')

ax3.set_title('(c) Dynamic Vector Field Streamlines & Sinks', fontweight='bold', pad=16)
ax3.set_xlabel('Spatial Feature $X_1$', fontweight='bold')
ax3.set_ylabel('Spatial Feature $X_2$', fontweight='bold')
ax3.legend(loc='lower left', framealpha=0.92, facecolor='white', edgecolor='#cccccc', fontsize=13)
ax3.grid(True, linestyle=':', alpha=0.5)

# -------------------------------------------------------------
# Panel (d): Calibrated Boltzmann Posterior Probability Map
# -------------------------------------------------------------
ax4 = fig.add_subplot(2, 2, 4)
im4 = ax4.imshow(P0, origin='lower', extent=[-3.5, 3.5, -3.5, 3.5], cmap='Blues', vmin=0.0, vmax=1.0)
cbar = plt.colorbar(im4, ax=ax4, fraction=0.046, pad=0.04)
cbar.set_label(r'Boltzmann Posterior $P(y = \mathrm{Class\ 0} \mid \mathbf{x})$', fontweight='bold', fontsize=15.5)

cs4 = ax4.contour(X, Y, P0, levels=[0.5, 0.8, 0.95], colors=['red', 'darkblue', 'green'], linewidths=[2.2, 2.0, 2.0], linestyles=['--', '-', '-'])
ax4.clabel(cs4, inline=True, fontsize=13, fmt='P=%.2f')

for i, pts in enumerate(samples):
    ax4.scatter(pts[:, 0], pts[:, 1], color=class_colors[i], s=35, alpha=0.7, edgecolors='black')

ax4.set_title('(d) Calibrated Boltzmann Confidence: $P(\\mathrm{Class\ 0})$', fontweight='bold', pad=16)
ax4.set_xlabel('Spatial Feature $X_1$', fontweight='bold')
ax4.set_ylabel('Spatial Feature $X_2$', fontweight='bold')
ax4.grid(True, linestyle=':', alpha=0.5)

plt.suptitle('Multi-Class Potential Superposition: 3D Surface, Streamlines, and Boltzmann Calibration', fontsize=24, fontweight='bold', y=0.99)
plt.subplots_adjust(left=0.05, right=0.95, bottom=0.06, top=0.94, wspace=0.22, hspace=0.26)

output_path = 'figures/multiclass_field_competition.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Successfully generated: {output_path}")
