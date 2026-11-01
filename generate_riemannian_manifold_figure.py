"""
generate_riemannian_manifold_figure.py
Visualizes Non-Euclidean Riemannian Manifold Extensions of PFDC (Spherical & Hyperbolic Poincaré).
Publication-grade formatting: 300 DPI, large typography (>=14-18 pt), zero overlap.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

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

fig = plt.figure(figsize=(22.5, 7.5))

# -------------------------------------------------------------
# Panel A: Hypersphere S^2 Geodesic Field & Tangent Projection
# -------------------------------------------------------------
ax1 = fig.add_subplot(131, projection='3d')

# Draw wireframe sphere
u = np.linspace(0, 2 * np.pi, 30)
v = np.linspace(0, np.pi, 20)
xs = np.outer(np.cos(u), np.sin(v))
ys = np.outer(np.sin(u), np.sin(v))
zs = np.outer(np.ones(np.size(u)), np.cos(v))

ax1.plot_wireframe(xs, ys, zs, color='#b0c4de', alpha=0.35, lw=0.6)

# Sample charges on sphere surface
np.random.seed(42)
# Positive charges (Northern hemisphere)
phi_p = np.random.uniform(0.3, 0.9, 5)
theta_p = np.random.uniform(0, 2*np.pi, 5)
xp = np.sin(phi_p) * np.cos(theta_p)
yp = np.sin(phi_p) * np.sin(theta_p)
zp = np.cos(phi_p)

# Negative charges (Southern hemisphere)
phi_n = np.random.uniform(2.1, 2.7, 5)
theta_n = np.random.uniform(0, 2*np.pi, 5)
xn = np.sin(phi_n) * np.cos(theta_n)
yn = np.sin(phi_n) * np.sin(theta_n)
zn = np.cos(phi_n)

ax1.scatter(xp, yp, zp, color='#1f77b4', s=104, label=r'Positive Charges ($+q_i$)', depthshade=False)
ax1.scatter(xn, yn, zn, color='#d62728', s=104, label=r'Negative Charges ($-q_i$)', depthshade=False)

# Test query point at equator
xq, yq, zq = 1.0, 0.0, 0.0
ax1.scatter([xq], [yq], [zq], color='black', s=150, marker='*', depthshade=False, label=r'Query $\mathbf{x} \in \mathbb{S}^2$')

# Tangent Plane at (1, 0, 0) -> spanned by dy, dz
tp_y, tp_z = np.meshgrid(np.linspace(-0.5, 0.5, 5), np.linspace(-0.5, 0.5, 5))
tp_x = np.ones_like(tp_y) * 1.0
ax1.plot_surface(tp_x, tp_y, tp_z, color='#2ca02c', alpha=0.25)

# Unprojected 3D Force Vector
F_raw = np.array([-0.4, 0.35, 0.45])
# Projected Tangent Force Vector: (I - x x^T) F
P_tangent = np.eye(3) - np.outer([xq, yq, zq], [xq, yq, zq])
F_proj = P_tangent @ F_raw

ax1.quiver(xq, yq, zq, F_raw[0], F_raw[1], F_raw[2], color='red', lw=2.5, arrow_length_ratio=0.2, label=r'Raw Force $\mathbf{F}_{\mathbb{R}}$')
ax1.quiver(xq, yq, zq, F_proj[0], F_proj[1], F_proj[2], color='darkgreen', lw=3.2, arrow_length_ratio=0.2, label=r'Tangent Force $\mathbf{F}_{\mathbb{S}}$')

ax1.set_title('(a) Spherical Manifold $\\mathbb{S}^2$ Tangent Projection', fontweight='bold', pad=16)
ax1.legend(loc='lower left', framealpha=0.9, facecolor='white', edgecolor='#cccccc', fontsize=12.5)
ax1.view_init(elev=20, azim=40)
ax1.axis('off')

# -------------------------------------------------------------
# Panel B: Hyperbolic Poincaré Disk H^2 Potential Field
# -------------------------------------------------------------
ax2 = fig.add_subplot(132)
ax2.set_xlim(-1.18, 1.18)
ax2.set_ylim(-1.18, 1.18)
ax2.set_aspect('equal')

# Boundary circle ||x|| = 1
circle_boundary = plt.Circle((0, 0), 1.0, color='#1f77b4', fill=False, lw=3.0, label=r'Hyperbolic Boundary $\|\mathbf{x}\| = 1$')
circle_interior = plt.Circle((0, 0), 1.0, color='#f0f4ff', alpha=0.5)
ax2.add_patch(circle_interior)
ax2.add_patch(circle_boundary)

# Draw Hyperbolic Geodesics (Arcs orthogonal to unit circle)
thetas = np.linspace(0, 2*np.pi, 8, endpoint=False)
for th in thetas:
    r_arc = 0.65
    center_x = (1.0 + r_arc**2)**0.5 * np.cos(th)
    center_y = (1.0 + r_arc**2)**0.5 * np.sin(th)
    arc = plt.Circle((center_x, center_y), r_arc, color='#888888', fill=False, linestyle='--', lw=1.2, alpha=0.6)
    ax2.add_patch(arc)

# Tree charges embedded in Poincaré disk
# Root charge at origin
ax2.scatter([0], [0], color='#1f77b4', s=161, zorder=6, label=r'Root Charge (Level 0)')
# Level 1 charges
r1 = 0.45
for th in np.linspace(0, 2*np.pi, 4, endpoint=False):
    ax2.scatter([r1*np.cos(th)], [r1*np.sin(th)], color='#2ca02c', s=115, zorder=6)
    ax2.plot([0, r1*np.cos(th)], [0, r1*np.sin(th)], color='#2ca02c', lw=1.8, alpha=0.7)
    
    # Level 2 charges
    for delta in [-0.25, 0.25]:
        th2 = th + delta
        r2 = 0.78
        ax2.scatter([r2*np.cos(th2)], [r2*np.sin(th2)], color='#d62728', s=81, zorder=6)
        ax2.plot([r1*np.cos(th), r2*np.cos(th2)], [r1*np.sin(th), r2*np.sin(th2)], color='#d62728', lw=1.4, alpha=0.7)

ax2.scatter([], [], color='#2ca02c', s=115, label=r'Branch Charges (Level 1)')
ax2.scatter([], [], color='#d62728', s=81, label=r'Leaf Charges (Level 2)')

ax2.set_title(r'(b) Hyperbolic Poincaré Disk $\mathbb{H}^2$ Embedding', fontweight='bold', pad=16)
ax2.legend(loc='lower left', framealpha=0.92, facecolor='white', edgecolor='#cccccc', fontsize=13)
ax2.grid(True, linestyle=':', alpha=0.4)

# -------------------------------------------------------------
# Panel C: Geodesic vs Euclidean Distance Metric Divergence
# -------------------------------------------------------------
ax3 = fig.add_subplot(133)
r_vals = np.linspace(0.0, 0.98, 200)

d_euclidean = r_vals
d_hyperbolic = 2.0 * np.arctanh(r_vals) # Geodesic distance from origin to (r, 0)
conformal_factor = 2.0 / (1.0 - r_vals**2)

ax3.plot(r_vals, d_hyperbolic, color='#d62728', lw=3.2, label=r'Hyperbolic Distance $d_{\mathbb{H}}(0, r)$')
ax3.plot(r_vals, conformal_factor, color='#ff7f0e', lw=2.5, linestyle='--', label=r'Conformal Scale $\lambda(r) = \frac{2}{1-r^2}$')
ax3.plot(r_vals, d_euclidean, color='#1f77b4', lw=2.5, linestyle=':', label=r'Euclidean Distance $d_{\mathbb{R}}(0, r)$')

ax3.axvline(1.0, color='black', linestyle='--', lw=2.0, alpha=0.7, label=r'Disk Boundary ($r = 1$)')
ax3.set_xlim(-0.02, 1.05)
ax3.set_ylim(0, 10)

ax3.set_title('(c) Non-Euclidean Metric Distortion vs Radius', fontweight='bold', pad=16)
ax3.set_xlabel('Radial Position from Center $r = \\|\\mathbf{x}\\|$', fontweight='bold')
ax3.set_ylabel('Metric Distance / Scale Value', fontweight='bold')
ax3.legend(loc='upper left', framealpha=0.92, facecolor='white', edgecolor='#cccccc', fontsize=14.5)
ax3.grid(True, linestyle=':', alpha=0.5)

# Annotation callout
ax3.annotate(r'Exponential Volume Expansion:' + '\n' + r'$d_{\mathbb{H}} \to \infty$ as $r \to 1$' + '\nNatural Margin Protection', 
             xy=(0.93, 7.5), xytext=(0.35, 6.0),
             arrowprops=dict(facecolor='#d62728', shrink=0.08, width=1.5, headwidth=8),
             fontweight='bold', bbox=dict(boxstyle='round,pad=0.5', facecolor='#ffe6e6', edgecolor='#d62728', lw=1.5),
             fontsize=14.5)

plt.suptitle('Non-Euclidean Riemannian Manifold Generalizations of Potential Field Classifiers', fontsize=25, fontweight='bold', y=0.99)
plt.tight_layout(rect=[0, 0, 1, 0.95])

output_path = 'figures/riemannian_manifold_geometries.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Successfully generated: {output_path}")
