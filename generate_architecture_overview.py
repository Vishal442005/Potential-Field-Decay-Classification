import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

OUTPUT_DIR = "figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set global publication styling
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 18
plt.rcParams['axes.titlesize'] = 21
plt.rcParams['axes.labelsize'] = 18
plt.rcParams['xtick.labelsize'] = 16
plt.rcParams['ytick.labelsize'] = 16
plt.rcParams['legend.fontsize'] = 16
plt.rcParams['figure.titlesize'] = 26

fig = plt.figure(figsize=(24, 11))

# -------------------------------------------------------------
# Panel (a): Traditional Global Decision Boundaries
# -------------------------------------------------------------
ax1 = fig.add_subplot(2, 2, 1)
np.random.seed(42)
c0_x = np.random.normal(loc=[-1.2, -0.8], scale=0.45, size=(40, 2))
c1_x = np.random.normal(loc=[1.2, 0.8], scale=0.45, size=(40, 2))

# Plot samples
ax1.scatter(c0_x[:, 0], c0_x[:, 1], color='#e74c3c', s=80, edgecolors='black', linewidth=1.2, label='Class 0 (Negative)', zorder=4)
ax1.scatter(c1_x[:, 0], c1_x[:, 1], color='#2980b9', s=80, edgecolors='black', linewidth=1.2, label='Class 1 (Positive)', zorder=4)

# Global linear boundary and tree orthogonal cuts
x_line = np.linspace(-3, 3, 100)
ax1.plot(x_line, -0.8 * x_line, color='#2c3e50', linewidth=3.0, linestyle='--', label='Global Hyperplane (SVM/DNN)', zorder=3)
ax1.axvline(x=0.0, color='#8e44ad', linewidth=2.0, linestyle=':', label='Axis Partition (XGBoost/Trees)', zorder=3)

# Highlight vulnerability region
circle = plt.Circle((-2.2, 1.8), 0.7, color='#e67e22', fill=True, alpha=0.25, linestyle='--', linewidth=2, zorder=2)
ax1.add_patch(circle)
ax1.text(-2.2, 1.8, 'Uncalibrated\nOverconfidence\n(No Local Core)', color='#d35400', ha='center', va='center', fontweight='bold', fontsize=14)

ax1.set_xlim(-3.0, 3.0)
ax1.set_ylim(-2.5, 2.5)
ax1.set_title('(a) Traditional Global Decision Boundaries (Rigid Partitions)', fontweight='bold', pad=16)
ax1.set_xlabel('Feature Coordinate $x_1$', fontweight='bold')
ax1.set_ylabel('Feature Coordinate $x_2$', fontweight='bold')
ax1.legend(loc='lower right', framealpha=0.95, edgecolor='#cccccc')
ax1.grid(True, linestyle='--', alpha=0.35)

# -------------------------------------------------------------
# Panel (b): PFDC Dual-Zone Radial Influence Profile
# -------------------------------------------------------------
ax2 = fig.add_subplot(2, 2, 2)
d = np.linspace(0, 2.5, 500)
R_core = 0.5
R_decay = 1.2
lam = 2.0
alpha = 2.0

I = np.zeros_like(d)
for idx, dist in enumerate(d):
    if dist <= R_core:
        I[idx] = 1.0
    elif dist <= R_core + R_decay:
        u = (dist - R_core) / R_decay
        I[idx] = np.exp(-lam * (u ** alpha))
    else:
        I[idx] = 0.0

ax2.plot(d, I, color='#16a085', linewidth=3.5, label='Radial Influence $I(d)$', zorder=4)
ax2.axvspan(0, R_core, color='#16a085', alpha=0.22, label='Deterministic Core ($R^{\\mathrm{core}}$: Certified 1.0 Certainty)', zorder=2)
ax2.axvspan(R_core, R_core + R_decay, color='#f39c12', alpha=0.20, label='Decay Shell ($R^{\\mathrm{decay}}$: Smooth Transition)', zorder=2)
ax2.axvspan(R_core + R_decay, 2.5, color='#bdc3c7', alpha=0.15, label='Zero Support Zone ($I(d) \\equiv 0$)', zorder=1)

ax2.axvline(R_core, color='#16a085', linestyle='--', linewidth=2.0)
ax2.axvline(R_core + R_decay, color='#d35400', linestyle='--', linewidth=2.0)

ax2.text(R_core/2.0, 0.5, 'Absolute\nCertainty Core\n$I = 1.0$', ha='center', va='center', fontweight='bold', color='#0e6655', fontsize=16)
ax2.text(R_core + R_decay/2.0, 0.45, 'Smooth Exponential\nFalloff Zone', ha='center', va='center', fontweight='bold', color='#b9770e', fontsize=16)
ax2.text(R_core + R_decay + 0.35, 0.3, 'Sub-linear\nBall-Tree\nCutoff', ha='center', va='center', fontweight='bold', color='#7f8c8d', fontsize=14)

ax2.set_xlim(0, 2.5)
ax2.set_ylim(-0.05, 1.15)
ax2.set_title('(b) PFDC Concentric Radial Profile ($R^{\\mathrm{core}} + R^{\\mathrm{decay}}$)', fontweight='bold', pad=16)
ax2.set_xlabel('Anisotropic Distance $d_{\\mathbf{w}}(\\mathbf{x}, \\mathbf{x}_i)$', fontweight='bold')
ax2.set_ylabel('Potential Influence $I(d_{\\mathbf{w}})$', fontweight='bold')
ax2.legend(loc='upper right', framealpha=0.95, edgecolor='#cccccc')
ax2.grid(True, linestyle='--', alpha=0.35)

# -------------------------------------------------------------
# Panel (c): 3D Superposed Potential Energy Landscape
# -------------------------------------------------------------
ax3 = fig.add_subplot(2, 2, 3, projection='3d')
x_grid = np.linspace(-2.5, 2.5, 70)
y_grid = np.linspace(-2.5, 2.5, 70)
X_m, Y_m = np.meshgrid(x_grid, y_grid)

# Superposition of positive and negative anchors
P_3d = np.zeros_like(X_m)
anchors = [
    (1.1, 0.7, +1.0, 1.2), (0.7, 1.2, +1.0, 1.0),
    (-1.1, -0.7, -1.0, 1.2), (-0.7, -1.2, -1.0, 1.0)
]
for ax_pos, ay_pos, q, a_val in anchors:
    dist = np.sqrt((X_m - ax_pos)**2 + (Y_m - ay_pos)**2)
    P_3d += q * a_val * np.exp(-1.8 * (dist**2))

surf = ax3.plot_surface(X_m, Y_m, P_3d, cmap='coolwarm', edgecolor='none', alpha=0.88, zorder=2)
ax3.contour(X_m, Y_m, P_3d, zdir='z', offset=-1.5, cmap='coolwarm', alpha=0.5, zorder=1)
ax3.set_zlim(-1.5, 1.5)
ax3.set_title('(c) 3D Superposed Scalar Potential Landscape $P(\\mathbf{x})$', fontweight='bold', pad=16)
ax3.set_xlabel('$x_1$', fontweight='bold', labelpad=8)
ax3.set_ylabel('$x_2$', fontweight='bold', labelpad=8)
ax3.set_zlabel('$P(\\mathbf{x})$', fontweight='bold', labelpad=8)
ax3.view_init(elev=32, azim=225)

# -------------------------------------------------------------
# Panel (d): Continuous Conservative Vector Force Field & Recourse
# -------------------------------------------------------------
ax4 = fig.add_subplot(2, 2, 4)
# Calculate analytical gradient for vector field
x_c = np.linspace(-2.2, 2.2, 30)
y_c = np.linspace(-2.2, 2.2, 30)
Xc, Yc = np.meshgrid(x_c, y_c)
Fx = np.zeros_like(Xc)
Fy = np.zeros_like(Yc)

for ax_pos, ay_pos, q, a_val in anchors:
    rx = Xc - ax_pos
    ry = Yc - ay_pos
    dist2 = rx**2 + ry**2
    # Force F = -grad P
    Fx += - q * a_val * (-2 * 1.8 * rx) * np.exp(-1.8 * dist2)
    Fy += - q * a_val * (-2 * 1.8 * ry) * np.exp(-1.8 * dist2)

norm = np.sqrt(Fx**2 + Fy**2) + 1e-6
Fx_norm = Fx / norm
Fy_norm = Fy / norm

strm = ax4.streamplot(Xc, Yc, Fx, Fy, color=norm, cmap='plasma', density=1.1, linewidth=1.8, arrowsize=1.5, zorder=2)
# Positive anchors
ax4.scatter([1.1, 0.7], [0.7, 1.2], color='#2980b9', s=184, edgecolors='black', linewidth=1.5, label='Positive Charges (+)', zorder=5)
# Negative anchors
ax4.scatter([-1.1, -0.7], [-0.7, -1.2], color='#e74c3c', s=184, edgecolors='black', linewidth=1.5, label='Negative Charges (-)', zorder=5)

# Example Recourse Streamline from malignant point
recourse_x = np.array([-1.5, -1.1, -0.6, -0.1, 0.4, 0.9])
recourse_y = np.array([-0.2, 0.1, 0.4, 0.6, 0.8, 0.9])
ax4.plot(recourse_x, recourse_y, color='#27ae60', linewidth=4.0, linestyle='-', marker='o', markersize=7, label='Physical Recourse Streamline $\\mathbf{F}(\\mathbf{x})$', zorder=6)
ax4.annotate('Query Point $\\mathbf{x}_0$\n(High Risk)', xy=(-1.5, -0.2), xytext=(-2.1, 0.8),
             arrowprops=dict(facecolor='black', shrink=0.08, width=2, headwidth=8),
             fontweight='bold', fontsize=14, bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.9))
ax4.annotate('Safety Core\n$P(\\mathbf{x}) \\geq +1.0$', xy=(0.9, 0.9), xytext=(1.0, 1.8),
             arrowprops=dict(facecolor='black', shrink=0.08, width=2, headwidth=8),
             fontweight='bold', fontsize=14, bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.9))

ax4.set_xlim(-2.2, 2.2)
ax4.set_ylim(-2.2, 2.2)
ax4.set_title('(d) Continuous Force Field $\\mathbf{F}(\\mathbf{x}) = -\\nabla P$ & Recourse Streamline', fontweight='bold', pad=16)
ax4.set_xlabel('Feature Coordinate $x_1$', fontweight='bold')
ax4.set_ylabel('Feature Coordinate $x_2$', fontweight='bold')
ax4.legend(loc='lower left', framealpha=0.95, edgecolor='#cccccc')
ax4.grid(True, linestyle='--', alpha=0.35)

plt.suptitle('Potential Field Decay Classification (PFDC): Foundational Architecture & Physical Mechanics', fontweight='bold', fontsize=26, y=0.99)
plt.tight_layout()
fig_path = os.path.join(OUTPUT_DIR, "pfdc_architecture_overview.png")
plt.savefig(fig_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Successfully generated flagship architectural figure: {fig_path}")
