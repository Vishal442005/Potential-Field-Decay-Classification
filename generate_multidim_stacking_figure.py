import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import Ellipse

OUTPUT_DIR = "figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 18
plt.rcParams['axes.titlesize'] = 21
plt.rcParams['axes.labelsize'] = 18
plt.rcParams['xtick.labelsize'] = 16
plt.rcParams['ytick.labelsize'] = 16
plt.rcParams['legend.fontsize'] = 16
plt.rcParams['figure.titlesize'] = 26

fig = plt.figure(figsize=(26, 12.5))

# -------------------------------------------------------------------------
# Panel (a): 2D Orthogonal Subspace Slices Decomposition
# -------------------------------------------------------------------------
ax1 = fig.add_subplot(2, 2, 1)

# Generate grid for 2D slice
x1 = np.linspace(-2.5, 2.5, 100)
x2 = np.linspace(-2.5, 2.5, 100)
X1, X2 = np.meshgrid(x1, x2)

# Informative 2D slice with anisotropic weights w1=2.0, w2=0.8
d_slice = np.sqrt(2.0 * X1**2 + 0.8 * X2**2)
pot_slice = np.exp(-1.5 * np.maximum(0.0, d_slice - 0.5)**1.5)
pot_slice[d_slice <= 0.5] = 1.0

cf1 = ax1.contourf(X1, X2, pot_slice, levels=25, cmap='viridis', alpha=0.45)
cs1_core = ax1.contour(X1, X2, d_slice, levels=[0.5], colors=['#16a085'], linewidths=3.0)
cs1_decay = ax1.contour(X1, X2, d_slice, levels=[1.8], colors=['#d35400'], linewidths=2.2, linestyles='--')

# Anchor point at center
ax1.scatter(0, 0, color='#2c3e50', s=207, edgecolors='black', linewidth=1.8, label='Training Anchor $\\mathbf{x}_i$', zorder=5)

# Annotations
ax1.text(0, 0.15, 'Deterministic\nCore ($R^{\\mathrm{core}}$)', ha='center', va='center', fontweight='bold', color='#0e6655', fontsize=16)
ax1.annotate('Decay Shell Boundary\n($R^{\\mathrm{core}} + R^{\\mathrm{decay}}$)', xy=(1.1, 1.1), xytext=(1.4, 2.0),
             arrowprops=dict(facecolor='#d35400', shrink=0.08, width=2, headwidth=7),
             fontweight='bold', color='#d35400', fontsize=14)

ax1.set_xlim(-2.5, 2.5)
ax1.set_ylim(-2.5, 2.5)
ax1.set_title('(a) Pairwise 2D Orthogonal Subspace Slice $(x_1, x_2)$', fontweight='bold', pad=16)
ax1.set_xlabel('Informative Variable $x_1$ ($w_1 = 2.0$)', fontweight='bold')
ax1.set_ylabel('Informative Variable $x_2$ ($w_2 = 0.8$)', fontweight='bold')
ax1.legend(loc='lower left', framealpha=0.95, edgecolor='#cccccc')
ax1.grid(True, linestyle='--', alpha=0.35)

# -------------------------------------------------------------------------
# Panel (b): 3D Volumetric Stacking of 2D Slices
# -------------------------------------------------------------------------
ax2 = fig.add_subplot(2, 2, 2, projection='3d')

# Create stacked ellipses across z-axis (e.g. x3 dimension)
z_slices = np.linspace(-1.5, 1.5, 7)
theta = np.linspace(0, 2*np.pi, 100)

for z_val in z_slices:
    # Ellipse radius shrinks as z increases away from anchor center
    scale_factor = np.sqrt(max(0.01, 1.0 - (z_val / 1.8)**2))
    r_core_x = 0.7 * scale_factor
    r_core_y = 1.1 * scale_factor
    r_decay_x = 1.5 * scale_factor
    r_decay_y = 2.1 * scale_factor
    
    # Core contour
    x_core = r_core_x * np.cos(theta)
    y_core = r_core_y * np.sin(theta)
    z_core = np.full_like(theta, z_val)
    ax2.plot(x_core, y_core, z_core, color='#16a085', linewidth=2.5, alpha=0.85, zorder=4)
    
    # Decay contour
    x_decay = r_decay_x * np.cos(theta)
    y_decay = r_decay_y * np.sin(theta)
    z_decay = np.full_like(theta, z_val)
    ax2.plot(x_decay, y_decay, z_decay, color='#e67e22', linewidth=1.5, linestyle='--', alpha=0.6, zorder=3)

# Anchor point at center
ax2.scatter(0, 0, 0, color='#e74c3c', s=230, edgecolors='black', linewidth=2.0, label='Central Anchor $\\mathbf{x}_i$', zorder=6)

# Draw central trajectory axis
ax2.plot([0, 0], [0, 0], [-1.8, 1.8], color='#2c3e50', linewidth=2.5, linestyle=':', label='Stacking Axis ($x_3$ Dimension)', zorder=2)

ax2.set_xlim(-2.2, 2.2)
ax2.set_ylim(-2.2, 2.2)
ax2.set_zlim(-1.8, 1.8)
ax2.set_title('(b) Volumetric Stacking: 2D Slices $\\to$ 3D Hyper-Ellipsoid', fontweight='bold', pad=16)
ax2.set_xlabel('Dimension $x_1$', fontweight='bold', labelpad=8)
ax2.set_ylabel('Dimension $x_2$', fontweight='bold', labelpad=8)
ax2.set_zlabel('Stacking Dimension $x_3$', fontweight='bold', labelpad=8)
ax2.view_init(elev=26, azim=135)

# -------------------------------------------------------------------------
# Panel (c): Anisotropic Metric Tensor Stretching Mechanism
# -------------------------------------------------------------------------
ax3 = fig.add_subplot(2, 2, 3)

# 1. Isotropic circular core (w1 = 1, w2 = 1)
circle_core = Ellipse((0, 0), width=1.6, height=1.6, color='#2980b9', fill=False, linewidth=2.8, linestyle='--', label='Isotropic Core: $w_1 = w_2 = 1.0$ (Drowning in Noise)')
circle_decay = Ellipse((0, 0), width=3.2, height=3.2, color='#2980b9', fill=False, linewidth=1.5, linestyle=':')
ax3.add_patch(circle_core)
ax3.add_patch(circle_decay)

# 2. Anisotropic feature selection ellipse (w_informative = 2.5, w_noise = 0.15)
# Major axis along noise dimension (stretched to infinity = ignored)
aniso_core = Ellipse((0, 0), width=1.0, height=3.8, color='#16a085', fill=True, alpha=0.25, label='Anisotropic Core: $w_1=2.5, w_2=0.15$ (Noise Flattened)')
aniso_core_edge = Ellipse((0, 0), width=1.0, height=3.8, color='#16a085', fill=False, linewidth=3.2)
ax3.add_patch(aniso_core)
ax3.add_patch(aniso_core_edge)

# Scatter anchor and noise-perturbed test points
ax3.scatter(0, 0, color='#2c3e50', s=184, edgecolors='black', linewidth=1.8, zorder=5)
# Perturbation along noise axis (x2)
ax3.scatter([0, 0], [1.4, -1.4], color='#8e44ad', s=138, marker='D', edgecolors='black', linewidth=1.5, label='Noise Perturbations along $x_2$ (Preserved in Core)', zorder=6)

ax3.annotate(r'Noise Axis $x_2$ Stretched:' + '\n' + r'$w_2 \to 0 \Rightarrow R_2 = R^{\mathrm{core}} / \sqrt{w_2} \to \infty$' + '\n(Noise Invariant)',
             xy=(0, 1.4), xytext=(0.6, 2.0),
             arrowprops=dict(facecolor='#8e44ad', shrink=0.08, width=2, headwidth=7),
             fontweight='bold', color='#6c3483', fontsize=14)

ax3.annotate(r'Informative Axis $x_1$ Compressed:' + '\n' + r'$w_1 > 1.2 \Rightarrow$ Sharp Boundary',
             xy=(0.5, 0), xytext=(1.2, -0.8),
             arrowprops=dict(facecolor='#16a085', shrink=0.08, width=2, headwidth=7),
             fontweight='bold', color='#0e6655', fontsize=14)

ax3.set_xlim(-2.5, 2.5)
ax3.set_ylim(-2.5, 2.5)
ax3.set_title('(c) Metric Tensor Geometry: Stretching Noise vs. Sharpening Signal', fontweight='bold', pad=16)
ax3.set_xlabel('Informative Dimension $x_1$ ($w_1 = 2.5$)', fontweight='bold')
ax3.set_ylabel('Noise Dimension $x_2$ ($w_2 = 0.15$)', fontweight='bold')
ax3.legend(loc='lower right', framealpha=0.95, edgecolor='#cccccc')
ax3.grid(True, linestyle='--', alpha=0.35)

# -------------------------------------------------------------------------
# Panel (d): Superposition of 2D Subspace Vector Forces
# -------------------------------------------------------------------------
ax4 = fig.add_subplot(2, 2, 4)

# Multi-dimensional gradient superposition: F(x) = sum_k F_k
# Show vector force arrows driving query point from multiple stacked subspaces
q_point = np.array([1.5, 1.2])

# Subspace 1 force (along x1)
F_sub1 = np.array([-1.2, 0.0])
# Subspace 2 force (along x2)
F_sub2 = np.array([0.0, -0.9])
# Net combined force
F_total = F_sub1 + F_sub2

# Plot query point
ax4.scatter(q_point[0], q_point[1], color='#e74c3c', s=207, edgecolors='black', linewidth=2.0, label='Query Sample $\\mathbf{x} \\in \\mathbb{R}^D$', zorder=5)

# Subspace vectors
ax4.quiver(q_point[0], q_point[1], F_sub1[0], F_sub1[1], angles='xy', scale_units='xy', scale=1,
           color='#2980b9', width=0.012, label='Subspace Force $\\mathbf{F}_{12} = -\\nabla_{(x_1, x_2)} P$', zorder=4)
ax4.quiver(q_point[0], q_point[1], F_sub2[0], F_sub2[1], angles='xy', scale_units='xy', scale=1,
           color='#e67e22', width=0.012, label='Subspace Force $\\mathbf{F}_{34} = -\\nabla_{(x_3, x_4)} P$', zorder=4)

# Total resultant force
ax4.quiver(q_point[0], q_point[1], F_total[0], F_total[1], angles='xy', scale_units='xy', scale=1,
           color='#27ae60', width=0.016, label='Net Conservative Force $\\mathbf{F}(\\mathbf{x}) = \\bigoplus_k \\mathbf{F}_k$', zorder=5)

# Safety core basin
core_target = Ellipse((0, 0), width=1.4, height=1.4, color='#16a085', fill=True, alpha=0.25)
core_target_edge = Ellipse((0, 0), width=1.4, height=1.4, color='#16a085', fill=False, linewidth=2.5, linestyle='--')
ax4.add_patch(core_target)
ax4.add_patch(core_target_edge)
ax4.scatter(0, 0, color='#16a085', s=184, marker='*', edgecolors='black', linewidth=1.5, label='Target Certainty Core $\\mathbf{x}^*$', zorder=5)

# Mathematical formula box
formula_text = (
    r"Additive Multi-Dimensional Stacking:" + "\n" +
    r"$d_{\mathbf{w}}^2(\mathbf{x}, \mathbf{x}_i) = \sum_{k=1}^{D/2} d_{\mathbf{w}, k}^2(x_{2k-1}, x_{2k})$" + "\n" +
    r"$\mathbf{F}(\mathbf{x}) = -\sum_{k=1}^D w_k (x_k - x_{ik}) \cdot \Theta(d_{\mathbf{w}})$" + "\n" +
    r"$\mathbf{F}_{\mathrm{net}} = \mathbf{F}_1 \oplus \mathbf{F}_2 \oplus \dots \oplus \mathbf{F}_D$"
)
ax4.text(0.04, 0.96, formula_text, transform=ax4.transAxes, fontsize=16, verticalalignment='top',
         bbox=dict(boxstyle='round,pad=0.5', facecolor='#f8f9fa', edgecolor='#bdc3c7', linewidth=1.5), fontweight='bold')

ax4.set_xlim(-1.5, 2.5)
ax4.set_ylim(-1.5, 2.5)
ax4.set_title('(d) Vector Force Superposition Across Stacked Subspaces', fontweight='bold', pad=16)
ax4.set_xlabel('Superposed Coordinate Axis 1', fontweight='bold')
ax4.set_ylabel('Superposed Coordinate Axis 2', fontweight='bold')
ax4.legend(loc='lower left', framealpha=0.95, edgecolor='#cccccc')
ax4.grid(True, linestyle='--', alpha=0.35)

plt.suptitle('Multi-Dimensional PFDC ($D > 2$): 2D Subspace Stacking, Hyper-Ellipsoidal Geometry, and Force Superposition', fontweight='bold', fontsize=25, y=0.99)
plt.tight_layout()
fig_path = os.path.join(OUTPUT_DIR, "multidimensional_2d_stacking_architecture.png")
plt.savefig(fig_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Successfully generated multi-dimensional 2D stacking figure: {fig_path}")
