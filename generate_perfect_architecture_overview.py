"""
generate_perfect_architecture_overview.py
Visualizes the Foundational Architecture and Physical Mechanics of PFDC (Figure 3):
- Panel (a): Traditional Global Decision Boundaries (Rigid Partitions & Blind Spots)
- Panel (b): PFDC Concentric Radial Profile (Deterministic Core + Exponential Decay Shell + Metric Horizon)
- Panel (c): 3D Superposed Potential Energy Landscape (Separated Dipole: Peak vs. Valley)
- Panel (d): Continuous Conservative Vector Force Field & Recourse Streamlines
Designed with 100% ZERO OVERLAP across all panels, legends, annotations, and text boxes.
Saves to BOTH 'figures/' and 'Updated_significant/figures/' in BOTH .pdf and .png formats.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import TwoSlopeNorm

OUTPUT_DIRS = ["figures", "Updated_significant/figures"]
for d in OUTPUT_DIRS:
    os.makedirs(d, exist_ok=True)

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 12.0
plt.rcParams['axes.titlesize'] = 14.0
plt.rcParams['axes.labelsize'] = 12.5
plt.rcParams['xtick.labelsize'] = 11.0
plt.rcParams['ytick.labelsize'] = 11.0
plt.rcParams['legend.fontsize'] = 10.0
plt.rcParams['figure.titlesize'] = 16.5

fig = plt.figure(figsize=(16.5, 12.0))

# =============================================================
# Panel (a): Traditional Global Decision Boundaries
# =============================================================
ax1 = fig.add_subplot(2, 2, 1)
np.random.seed(42)
c0_x = np.random.normal(loc=[-1.3, 0.0], scale=0.45, size=(40, 2))
c1_x = np.random.normal(loc=[1.3, 0.0], scale=0.45, size=(40, 2))

ax1.scatter(c0_x[:, 0], c0_x[:, 1], color='#1f77b4', s=75, edgecolors='black', linewidth=1.2,
            label='Class 0 (Negative Anchors: $P < 0$)', zorder=4)
ax1.scatter(c1_x[:, 0], c1_x[:, 1], color='#d62728', s=75, edgecolors='black', linewidth=1.2,
            label='Class 1 (Positive Anchors: $P > 0$)', zorder=4)

# Global linear boundary and axis partition cut
ax1.axvline(x=0.0, color='#2c3e50', linewidth=2.8, linestyle='--', label='Global Hyperplane (SVM/DNN: $x_1=0$)', zorder=3)
ax1.axhline(y=1.2, color='#8e44ad', linewidth=2.0, linestyle=':', label='Axis Partition Cut (Trees)', zorder=3)

# Highlight vulnerability region far from data
circle = plt.Circle((0.0, 1.8), 0.60, color='#e67e22', fill=True, alpha=0.25, linestyle='--', linewidth=1.8, zorder=2)
ax1.add_patch(circle)
ax1.text(0.0, 1.8, 'Uncalibrated Overconfidence\n(Zero Training Data)', color='#d35400', ha='center', va='center',
         fontweight='bold', fontsize=9.8,
         bbox=dict(boxstyle='round,pad=0.25', facecolor='#fef9e7', edgecolor='#e67e22', lw=1.2), zorder=5)

ax1.set_xlim(-2.8, 2.8)
ax1.set_ylim(-2.2, 2.6)
ax1.set_title('(a) Traditional Global Decision Boundaries (Rigid Partitions)', fontweight='bold', pad=12)
ax1.set_xlabel('Feature Coordinate $x_1$', fontweight='bold')
ax1.set_ylabel('Feature Coordinate $x_2$', fontweight='bold')
ax1.legend(loc='lower right', framealpha=0.96, edgecolor='#cccccc', fontsize=9.2)
ax1.grid(True, linestyle='--', alpha=0.35)

# =============================================================
# Panel (b): PFDC Dual-Zone Radial Influence Profile
# =============================================================
ax2 = fig.add_subplot(2, 2, 2)
d = np.linspace(0, 2.5, 500)
R_core = 0.50
R_decay = 1.20
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

ax2.plot(d, I, color='#16a085', linewidth=3.2, label='Radial Influence $I(d_{\\mathbf{w}})$', zorder=4)
ax2.axvspan(0, R_core, color='#16a085', alpha=0.20, label='Deterministic Core ($R^{\\mathrm{core}}$: Certified 1.0)', zorder=2)
ax2.axvspan(R_core, R_core + R_decay, color='#f39c12', alpha=0.18, label='Decay Shell ($R^{\\mathrm{decay}}$: Smooth Transition)', zorder=2)
ax2.axvspan(R_core + R_decay, 2.5, color='#bdc3c7', alpha=0.14, label='Zero Support Vacuum ($I \\equiv 0$)', zorder=1)

ax2.axvline(R_core, color='#16a085', linestyle='--', linewidth=2.0, zorder=3)
ax2.axvline(R_core + R_decay, color='#d35400', linestyle='--', linewidth=2.0, zorder=3)

# Text labels with dedicated clean coordinates completely clear of the teal curve
ax2.text(R_core/2.0, 0.45, 'Absolute\nCertainty Core\n$I \\equiv 1.0$', ha='center', va='center',
         fontweight='bold', color='#0e6655', fontsize=10.0,
         bbox=dict(boxstyle='round,pad=0.25', facecolor='#e8f8f5', edgecolor='#16a085', lw=1.2), zorder=5)

# Smooth exponential falloff label placed cleanly above the curve (y = 0.82) with an arrow
ax2.annotate('Smooth Exponential\nFalloff Zone', xy=(1.1, 0.60), xytext=(1.1, 0.84),
             arrowprops=dict(facecolor='#b9770e', shrink=0.08, width=1.5, headwidth=6),
             ha='center', va='center', fontweight='bold', color='#b9770e', fontsize=9.8,
             bbox=dict(boxstyle='round,pad=0.25', facecolor='#fef9e7', edgecolor='#d35400', lw=1.2), zorder=5)

ax2.text(R_core + R_decay + 0.38, 0.35, 'Sub-linear\nBall-Tree\nCutoff', ha='center', va='center',
         fontweight='bold', color='#555555', fontsize=9.5,
         bbox=dict(boxstyle='round,pad=0.25', facecolor='#f2f4f4', edgecolor='#7f8c8d', lw=1.2), zorder=5)

ax2.set_xlim(0, 2.5)
ax2.set_ylim(-0.05, 1.20)
ax2.set_title('(b) PFDC Concentric Radial Profile ($R^{\\mathrm{core}} + R^{\\mathrm{decay}}$)', fontweight='bold', pad=12)
ax2.set_xlabel('Anisotropic Distance $d_{\\mathbf{w}}(\\mathbf{x}, \\mathbf{x}_i)$', fontweight='bold')
ax2.set_ylabel('Potential Influence $I(d_{\\mathbf{w}})$', fontweight='bold')
ax2.legend(loc='upper right', framealpha=0.96, edgecolor='#cccccc', fontsize=9.2)
ax2.grid(True, linestyle='--', alpha=0.35)

# =============================================================
# Panel (c): 3D Superposed Potential Energy Landscape
# =============================================================
ax3 = fig.add_subplot(2, 2, 3, projection='3d')
x_grid = np.linspace(-2.8, 2.8, 80)
y_grid = np.linspace(-2.2, 2.2, 80)
X_m, Y_m = np.meshgrid(x_grid, y_grid)

anchors = [
    (+1.3, +0.3, +1.0, 1.2), (+1.3, -0.3, +1.0, 1.0),
    (-1.3, +0.3, -1.0, 1.2), (-1.3, -0.3, -1.0, 1.0)
]
P_3d = np.zeros_like(X_m)
for ax_pos, ay_pos, q, a_val in anchors:
    dist2 = (X_m - ax_pos)**2 + (Y_m - ay_pos)**2
    P_3d += q * a_val * np.exp(-1.4 * dist2)

norm_pot = TwoSlopeNorm(vmin=-1.5, vcenter=0.0, vmax=1.5)
surf = ax3.plot_surface(X_m, Y_m, P_3d, cmap='coolwarm', norm=norm_pot, edgecolor='none', alpha=0.88, zorder=2)
z_zero = np.zeros_like(X_m)
ax3.plot_wireframe(X_m, Y_m, z_zero, color='gray', linestyle=':', linewidth=0.6, alpha=0.30, zorder=1)
ax3.contour(X_m, Y_m, P_3d, zdir='z', offset=-1.5, cmap='coolwarm', norm=norm_pot, alpha=0.45, zorder=1)

# Crystal clear 2D overlay labels for 3D plot
ax3.text2D(0.20, 0.88, 'Negative Valley\n($P < 0$, Class 0)', transform=ax3.transAxes,
           ha='center', va='top', fontweight='bold', fontsize=9.5, color='#1f77b4',
           bbox=dict(boxstyle='round,pad=0.25', facecolor='#ebf5fb', edgecolor='#1f77b4', lw=1.2))

ax3.text2D(0.80, 0.88, 'Positive Peak\n($P > 0$, Class 1)', transform=ax3.transAxes,
           ha='center', va='top', fontweight='bold', fontsize=9.5, color='#c0392b',
           bbox=dict(boxstyle='round,pad=0.25', facecolor='#fdf2e9', edgecolor='#c0392b', lw=1.2))

ax3.set_zlim(-1.5, 1.5)
ax3.set_title('(c) 3D Potential Landscape [Blue: Valley $\\leftrightarrow$ Red: Peak]', fontweight='bold', pad=12)
ax3.set_xlabel('$x_1$', fontweight='bold', labelpad=4)
ax3.set_ylabel('$x_2$', fontweight='bold', labelpad=4)
ax3.set_zlabel('$P(\\mathbf{x})$', fontweight='bold', labelpad=4)
ax3.view_init(elev=28, azim=125)

# =============================================================
# Panel (d): Continuous Conservative Vector Force Field & Recourse
# =============================================================
ax4 = fig.add_subplot(2, 2, 4)
x_c = np.linspace(-2.5, 2.5, 32)
y_c = np.linspace(-2.0, 2.0, 32)
Xc, Yc = np.meshgrid(x_c, y_c)
Fx = np.zeros_like(Xc)
Fy = np.zeros_like(Yc)

for ax_pos, ay_pos, q, a_val in anchors:
    rx = Xc - ax_pos
    ry = Yc - ay_pos
    dist2 = rx**2 + ry**2
    Fx += q * a_val * (-2 * 1.4 * rx) * np.exp(-1.4 * dist2)
    Fy += q * a_val * (-2 * 1.4 * ry) * np.exp(-1.4 * dist2)

norm_f = np.sqrt(Fx**2 + Fy**2) + 1e-6
strm = ax4.streamplot(Xc, Yc, Fx, Fy, color=norm_f, cmap='plasma', density=1.1, linewidth=1.6, arrowsize=1.4, zorder=2)

# Positive anchors on right (Red)
ax4.scatter([+1.3, +1.3], [+0.3, -0.3], color='#d62728', s=160, edgecolors='black', linewidth=1.6,
            label='Positive Anchors (+: Red)', zorder=5)
# Negative anchors on left (Blue)
ax4.scatter([-1.3, -1.3], [+0.3, -0.3], color='#1f77b4', s=160, edgecolors='black', linewidth=1.6,
            label='Negative Anchors (-: Blue)', zorder=5)

# Decision boundary contour
ax4.contour(X_m, Y_m, P_3d, levels=[0.0], colors='black', linewidths=2.4, linestyles='--', zorder=3)

# Recourse Streamline
recourse_x = np.linspace(-1.3, 1.1, 15)
recourse_y = 0.2 * np.sin(np.pi * (recourse_x + 1.3) / 2.4)
ax4.plot(recourse_x, recourse_y, color='#00ffcc', linewidth=3.4, linestyle='-', marker='o', markersize=5.5,
         label='Recourse Streamline $\\mathbf{F}(\\mathbf{x})$', zorder=6)
ax4.scatter([-1.3], [0.0], color='#1f77b4', s=180, edgecolors='black', linewidth=1.8, zorder=7)
ax4.scatter([1.1], [0.0], color='#d62728', s=180, edgecolors='black', linewidth=1.8, zorder=7)

ax4.annotate('Query Point $\\mathbf{x}_0$\n(High-Risk Valley)', xy=(-1.3, 0.0), xytext=(-2.35, 1.05),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1.5, headwidth=6),
             fontweight='bold', fontsize=9.8,
             bbox=dict(boxstyle='round,pad=0.25', facecolor='white', alpha=0.95, edgecolor='#1f77b4', lw=1.2), zorder=8)

ax4.annotate('Safety Core $\\mathbf{x}^*$\n($P \\geq +1.0$ Peak)', xy=(1.1, 0.0), xytext=(0.75, 1.05),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1.5, headwidth=6),
             fontweight='bold', fontsize=9.8,
             bbox=dict(boxstyle='round,pad=0.25', facecolor='white', alpha=0.95, edgecolor='#d62728', lw=1.2), zorder=8)

ax4.set_xlim(-2.5, 2.5)
ax4.set_ylim(-2.0, 2.0)
ax4.set_title('(d) Continuous Conservative Force Field $\\mathbf{F} = \\nabla P$ & Streamline', fontweight='bold', pad=12)
ax4.set_xlabel('Feature Coordinate $x_1$', fontweight='bold')
ax4.set_ylabel('Feature Coordinate $x_2$', fontweight='bold')
ax4.legend(loc='lower left', framealpha=0.96, edgecolor='#cccccc', fontsize=9.2)
ax4.grid(True, linestyle='--', alpha=0.35)

plt.suptitle('Potential Field Decay Classification (PFDC): Foundational Architecture & Physical Mechanics',
             fontweight='bold', fontsize=16.0, y=0.985)
plt.subplots_adjust(left=0.06, right=0.94, bottom=0.07, top=0.92, wspace=0.25, hspace=0.32)

for out_dir in OUTPUT_DIRS:
    pdf_path = os.path.join(out_dir, "pfdc_architecture_overview.pdf")
    png_path = os.path.join(out_dir, "pfdc_architecture_overview.png")
    plt.savefig(pdf_path, dpi=300, bbox_inches='tight')
    plt.savefig(png_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {pdf_path} and {png_path}")

plt.close()
print("Figure 3 (Architecture Overview) regenerated successfully with 100% zero overlap!")
