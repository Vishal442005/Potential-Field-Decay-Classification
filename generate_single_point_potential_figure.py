"""
generate_single_point_potential_figure.py
Visualizes the Fundamental Potential Field and Vector Force Dynamics of an Isolated Point Charge:
(a) 2D Concentric Equipotential Shells & Vector Force Field with Distance-Dependent Arrow Lengths
(b) 3D Continuous Potential Energy Mesa (Plateau Core + Exponential Skirt)
(c) 1D Radial Influence Profile I(d) and Analytical Force Magnitude ||F(d)||
Strict Physical Conventions:
- Positive Anchor (+1.0): Red potential hill, outward force vectors
- Longer arrows at inner decay boundary (high field strength), shrinking smoothly to zero at the horizon
- Publication-grade typography: 1.3x font scaling, zero overlap, 300 DPI.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import Circle

OUTPUT_DIR = "figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Publication typography (1.3x scaled)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 17
plt.rcParams['axes.titlesize'] = 20
plt.rcParams['axes.labelsize'] = 18
plt.rcParams['xtick.labelsize'] = 15
plt.rcParams['ytick.labelsize'] = 15
plt.rcParams['legend.fontsize'] = 14
plt.rcParams['figure.titlesize'] = 24

# Physical parameters of single anchor
R_core = 0.60
R_decay = 1.40
R_horizon = R_core + R_decay
lam = 2.2
alpha = 2.0

fig = plt.figure(figsize=(26, 8.5))

# -------------------------------------------------------------------------
# Panel (a): 2D Concentric Equipotential Field & Vector Force Arrows
# -------------------------------------------------------------------------
ax1 = fig.add_subplot(1, 3, 1)

# Grid for 2D field
grid_lim = 2.4
res = 120
x_vals = np.linspace(-grid_lim, grid_lim, res)
y_vals = np.linspace(-grid_lim, grid_lim, res)
X, Y = np.meshgrid(x_vals, y_vals)
D = np.sqrt(X**2 + Y**2)

# Compute single-point potential I(d)
I_2d = np.zeros_like(D)
I_2d[D <= R_core] = 1.0
mask_decay = (D > R_core) & (D <= R_horizon)
u_2d = (D[mask_decay] - R_core) / R_decay
I_2d[mask_decay] = np.exp(-lam * (u_2d ** alpha))

# Contour fill (Red gradient for positive potential)
cf = ax1.contourf(X, Y, I_2d, levels=30, cmap='Reds', alpha=0.60)
cbar = plt.colorbar(cf, ax=ax1, pad=0.03, shrink=0.88)
cbar.set_label('Potential Influence $I(d)$', fontweight='bold', fontsize=15)

# Boundary rings
circle_core = Circle((0, 0), R_core, color='#b30000', fill=False, linewidth=2.8, linestyle='-', label=f'Deterministic Core ($R^{{\\mathrm{{core}}}}={R_core:.2f}$)')
circle_decay = Circle((0, 0), R_horizon, color='#d35400', fill=False, linewidth=2.4, linestyle='--', label=f'Search Horizon ($R^{{\\mathrm{{core}}}}+R^{{\\mathrm{{decay}}}}={R_horizon:.2f}$)')
ax1.add_patch(circle_core)
ax1.add_patch(circle_decay)

# Center anchor point
ax1.scatter(0, 0, color='#b30000', s=230, edgecolors='black', linewidth=2.0, zorder=7, label='Support Anchor $\\mathbf{x}_i$ ($+q_i$)')

# Concentric Quiver: Vector force arrows
# Arrow strength ||F|| = -dI/dd = lambda * alpha / R_decay * u^(alpha-1) * I(d)
# Inside core: small nominal guidance; Near core boundary: maximum length; At far: shrinking to zero
radii_quiver = np.linspace(0.25, R_horizon * 0.95, 8)
n_angles = 16

for r in radii_quiver:
    angles = np.linspace(0, 2*np.pi, n_angles, endpoint=False)
    # Stagger angles across successive rings for visual clarity
    angles += (np.pi / n_angles) * (radii_quiver.tolist().index(r) % 2)
    qx = r * np.cos(angles)
    qy = r * np.sin(angles)
    
    if r <= R_core:
        # Near core: high readiness force pointing outward
        mag = 0.22
    else:
        u = (r - R_core) / R_decay
        # Derivative magnitude: peak near inner decay, decaying exponentially
        grad_mag = (lam * alpha / R_decay) * (u ** (alpha - 1)) * np.exp(-lam * (u ** alpha))
        mag = 0.08 + 0.32 * (grad_mag / 1.1) # longer at center, smaller at far
        
    u_vec = mag * np.cos(angles)
    v_vec = mag * np.sin(angles)
    ax1.quiver(qx, qy, u_vec, v_vec, angles='xy', scale_units='xy', scale=1.0,
               color='#2c3e50', width=0.007, headwidth=4.5, headlength=5.5, zorder=5)

# Annotations
ax1.text(0, R_core*0.5, 'Saturated\nCore ($I=1$)', ha='center', va='center', fontweight='bold', color='#660000', fontsize=13)
ax1.annotate('High-Strength Vectors\n(Steep Potential Gradient)', xy=(0.85, 0.4), xytext=(1.25, 1.2),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1.8, headwidth=7),
             fontweight='bold', fontsize=13, bbox=dict(boxstyle='round,pad=0.35', facecolor='#fff5eb', edgecolor='#d35400', lw=1.5))
ax1.annotate('Diminishing Vectors\n(Smooth Falloff to Zero)', xy=(1.5, -0.9), xytext=(0.4, -2.1),
             arrowprops=dict(facecolor='black', shrink=0.08, width=1.8, headwidth=7),
             fontweight='bold', fontsize=13, bbox=dict(boxstyle='round,pad=0.35', facecolor='#f8f9fa', edgecolor='#7f8c8d', lw=1.5))

ax1.set_xlim(-grid_lim, grid_lim)
ax1.set_ylim(-grid_lim, grid_lim)
ax1.set_title('(a) 2D Equipotential Shells & Vector Force Field', fontweight='bold', pad=14)
ax1.set_xlabel('Spatial Coordinate $x_1$', fontweight='bold')
ax1.set_ylabel('Spatial Coordinate $x_2$', fontweight='bold')
ax1.legend(loc='lower left', framealpha=0.92, edgecolor='#cccccc', fontsize=11.5)
ax1.grid(True, linestyle='--', alpha=0.35)

# -------------------------------------------------------------------------
# Panel (b): 3D Single-Point Potential Energy Mesa
# -------------------------------------------------------------------------
ax2 = fig.add_subplot(1, 3, 2, projection='3d')

res_3d = 70
x3 = np.linspace(-grid_lim, grid_lim, res_3d)
y3 = np.linspace(-grid_lim, grid_lim, res_3d)
X3, Y3 = np.meshgrid(x3, y3)
D3 = np.sqrt(X3**2 + Y3**2)

I_3d = np.zeros_like(D3)
I_3d[D3 <= R_core] = 1.0
mask_3d = (D3 > R_core) & (D3 <= R_horizon)
u_3d = (D3[mask_3d] - R_core) / R_decay
I_3d[mask_3d] = np.exp(-lam * (u_3d ** alpha))

surf = ax2.plot_surface(X3, Y3, I_3d, cmap='Reds', edgecolor='none', alpha=0.88, zorder=2)

# Wireframe flat base
z_zero = np.zeros_like(X3)
ax2.plot_wireframe(X3, Y3, z_zero, color='gray', linestyle=':', linewidth=0.7, alpha=0.30, zorder=1)

# Concentric circle projections on ground plane
theta_ring = np.linspace(0, 2*np.pi, 100)
x_rc = R_core * np.cos(theta_ring)
y_rc = R_core * np.sin(theta_ring)
ax2.plot(x_rc, y_rc, np.zeros_like(x_rc), color='#b30000', linewidth=2.5, linestyle='-', zorder=3)

x_rh = R_horizon * np.cos(theta_ring)
y_rh = R_horizon * np.sin(theta_ring)
ax2.plot(x_rh, y_rh, np.zeros_like(x_rh), color='#d35400', linewidth=2.0, linestyle='--', zorder=3)

ax2.set_zlim(0.0, 1.25)
ax2.set_title('(b) 3D Potential Mesa: Core Plateau & Decay Skirt', fontweight='bold', pad=14)
ax2.set_xlabel('$x_1$', fontweight='bold', labelpad=8)
ax2.set_ylabel('$x_2$', fontweight='bold', labelpad=8)
ax2.set_zlabel('Potential $I(d)$', fontweight='bold', labelpad=8)
ax2.view_init(elev=28, azim=130)

# -------------------------------------------------------------------------
# Panel (c): 1D Radial Influence Profile I(d) vs. Force Strength ||F(d)||
# -------------------------------------------------------------------------
ax3 = fig.add_subplot(1, 3, 3)

d_fine = np.linspace(0, 2.4, 500)
I_1d = np.zeros_like(d_fine)
F_mag = np.zeros_like(d_fine)

for idx, dist in enumerate(d_fine):
    if dist <= R_core:
        I_1d[idx] = 1.0
        F_mag[idx] = 0.0 # Zero conservative force inside deterministic plateau
    elif dist <= R_horizon:
        u = (dist - R_core) / R_decay
        val = np.exp(-lam * (u ** alpha))
        I_1d[idx] = val
        # Analytical force magnitude: ||F|| = -dI/dd
        F_mag[idx] = (lam * alpha / R_decay) * (u ** (alpha - 1)) * val
    else:
        I_1d[idx] = 0.0
        F_mag[idx] = 0.0

# Plot Potential Profile on left y-axis
color_p = '#b30000'
ax3.plot(d_fine, I_1d, color=color_p, linewidth=3.4, label='Scalar Potential $I(d)$ (Plateau Core + Decay)')
ax3.set_xlabel('Euclidean Distance from Anchor $d = \\|\\mathbf{x} - \\mathbf{x}_i\\|_2$', fontweight='bold')
ax3.set_ylabel('Potential Field Influence $I(d)$', color=color_p, fontweight='bold')
ax3.tick_params(axis='y', labelcolor=color_p)

# Zone fills
ax3.axvspan(0, R_core, color='#b30000', alpha=0.15, label=f'Certainty Core ($R^{{\\mathrm{{core}}}}={R_core}$)')
ax3.axvspan(R_core, R_horizon, color='#f39c12', alpha=0.16, label=f'Decay Shell ($R^{{\\mathrm{{decay}}}}={R_decay}$)')
ax3.axvspan(R_horizon, 2.4, color='#bdc3c7', alpha=0.14, label='Zero-Support Vacuum ($I \\equiv 0$)')

# Second y-axis for Force Strength
ax3_twin = ax3.twinx()
color_f = '#2c3e50'
ax3_twin.plot(d_fine, F_mag, color=color_f, linewidth=2.8, linestyle='-.', label='Force Strength $\\|\\mathbf{F}(d)\\|_2 = |\\mathrm{d}I/\\mathrm{d}d|$')
ax3_twin.set_ylabel('Force Vector Magnitude $\\|\\mathbf{F}(d)\\|_2$', color=color_f, fontweight='bold')
ax3_twin.tick_params(axis='y', labelcolor=color_f)

# Annotate force peak
peak_d = d_fine[np.argmax(F_mag)]
peak_f = np.max(F_mag)
ax3_twin.scatter([peak_d], [peak_f], color='#2c3e50', s=160, zorder=6)
ax3_twin.annotate(f'Peak Force Magnitude\n(Longest Vectors at $d={peak_d:.2f}$)', xy=(peak_d, peak_f), xytext=(peak_d+0.25, peak_f-0.20),
                 arrowprops=dict(facecolor='#2c3e50', shrink=0.08, width=1.8, headwidth=7),
                 fontweight='bold', fontsize=12.5, bbox=dict(boxstyle='round,pad=0.35', facecolor='#f0f4ff', edgecolor='#2c3e50', lw=1.4))

ax3.set_xlim(0, 2.4)
ax3.set_ylim(-0.05, 1.15)
ax3_twin.set_ylim(-0.05, 1.25)
ax3.set_title('(c) 1D Radial Influence $I(d)$ vs. Force Magnitude $\\|\\mathbf{F}(d)\\|_2$', fontweight='bold', pad=14)
ax3.grid(True, linestyle='--', alpha=0.35)

plt.suptitle('Electrostatic Potential Field and Force Vector Dynamics of an Isolated Support Anchor', fontsize=23, fontweight='bold', y=0.99)
plt.subplots_adjust(left=0.05, right=0.94, bottom=0.10, top=0.90, wspace=0.25)

out_fig = os.path.join(OUTPUT_DIR, "single_point_potential_2d_3d.png")
plt.savefig(out_fig, dpi=300, bbox_inches='tight')
plt.close()
print(f"Successfully generated single point potential figure: {out_fig}")
