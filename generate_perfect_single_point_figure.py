"""
generate_perfect_single_point_figure.py
Visualizes the Fundamental Potential Field and Vector Force Dynamics of an Isolated Point Anchor:
(a) 2D Concentric Equipotential Shells & Vector Force Field with Distance-Dependent Arrow Lengths
    (Longer arrows at center showing high field strength, smoothly shrinking to smaller arrows far away)
    Plus explicit dimension callouts for Core Radius R_core and Decay Radius R_decay.
(b) 3D Continuous Potential Energy Mesa (Certainty Core Plateau + Exponential Decay Skirt + Ground Plane)
(c) 1D Radial Influence Profile I(d) and Field Strength / Force Magnitude ||F(d)||
Strict Physical Conventions:
- Positive Anchor (+1.0): Red potential hill/contours, outward repulsive force vectors
- Publication-grade typography: 1.3x font scaling, zero overlap, 300 DPI.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import Circle, FancyArrowPatch

OUTPUT_DIR = "figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Publication typography (1.3x scaled)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 16
plt.rcParams['axes.titlesize'] = 19
plt.rcParams['axes.labelsize'] = 17
plt.rcParams['xtick.labelsize'] = 15
plt.rcParams['ytick.labelsize'] = 15
plt.rcParams['legend.fontsize'] = 13.5
plt.rcParams['figure.titlesize'] = 23

# Physical parameters of single anchor
R_core = 0.60
R_decay = 1.40
R_horizon = R_core + R_decay # 2.00
lam = 2.2
alpha = 2.0

fig = plt.figure(figsize=(26, 8.5))

# -------------------------------------------------------------------------
# Panel (a): 2D Concentric Equipotential Field & Vector Force Arrows
# -------------------------------------------------------------------------
ax1 = fig.add_subplot(1, 3, 1)

grid_lim = 2.45
res = 160
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
cf = ax1.contourf(X, Y, I_2d, levels=30, cmap='Reds', alpha=0.62)
cbar = plt.colorbar(cf, ax=ax1, pad=0.03, shrink=0.88)
cbar.set_label('Potential Influence $I(d)$', fontweight='bold', fontsize=15)

# Boundary rings
circle_core = Circle((0, 0), R_core, color='#b30000', fill=False, linewidth=2.8, linestyle='-',
                     label=f'Core Boundary ($R^{{\\mathrm{{core}}}}={R_core:.2f}$)')
circle_decay = Circle((0, 0), R_horizon, color='#d35400', fill=False, linewidth=2.4, linestyle='--',
                      label=f'Decay Horizon ($R^{{\\mathrm{{core}}}}+R^{{\\mathrm{{decay}}}}={R_horizon:.2f}$)')
ax1.add_patch(circle_core)
ax1.add_patch(circle_decay)

# Center anchor point
ax1.scatter(0, 0, color='#b30000', s=240, edgecolors='black', linewidth=2.2, zorder=7,
            label='Support Anchor $\\mathbf{x}_i$ ($+q_i$)')

# Vector force arrows radiating outward:
# USER REQUIREMENT: "longer arrows at center showing high strength and smaller at far"
# Radii from inner core outwards:
radii_quiver = [0.22, 0.45, 0.75, 1.05, 1.35, 1.65, 1.90]
n_angles_list = [8, 12, 16, 16, 20, 20, 24]

for idx_r, r in enumerate(radii_quiver):
    n_angles = n_angles_list[idx_r]
    angles = np.linspace(0, 2*np.pi, n_angles, endpoint=False)
    # Stagger angles across successive rings for visual aesthetics
    angles += (np.pi / n_angles) * (idx_r % 2)
    qx = r * np.cos(angles)
    qy = r * np.sin(angles)
    
    # Monotonically decaying arrow length: longest at center, smoothly shrinking to small at far
    # r=0.22 -> mag ~ 0.38; r=0.60 -> mag ~ 0.28; r=1.90 -> mag ~ 0.07
    norm_dist = r / R_horizon
    mag = 0.42 * (1.0 - 0.85 * (norm_dist ** 1.1))
    
    u_vec = mag * np.cos(angles)
    v_vec = mag * np.sin(angles)
    ax1.quiver(qx, qy, u_vec, v_vec, angles='xy', scale_units='xy', scale=1.0,
               color='#1f2d3d', width=0.0068, headwidth=4.6, headlength=5.6, zorder=5)

# Dimension markers for R_core and R_decay along the negative horizontal axis
ax1.annotate('', xy=(-R_core, 0), xytext=(0, 0),
             arrowprops=dict(arrowstyle='<->', color='#8b0000', lw=2.4))
ax1.text(-R_core/2, 0.12, '$R^{\\mathrm{core}}$', ha='center', va='bottom',
         fontweight='bold', fontsize=14.5, color='#8b0000',
         bbox=dict(boxstyle='square,pad=0.15', facecolor='white', edgecolor='none', alpha=0.85))

ax1.annotate('', xy=(-R_horizon, 0), xytext=(-R_core, 0),
             arrowprops=dict(arrowstyle='<->', color='#d35400', lw=2.4))
ax1.text(-(R_core + R_horizon)/2, 0.12, '$R^{\\mathrm{decay}}$', ha='center', va='bottom',
         fontweight='bold', fontsize=14.5, color='#d35400',
         bbox=dict(boxstyle='square,pad=0.15', facecolor='white', edgecolor='none', alpha=0.85))

# Explanatory callouts on panel (a)
ax1.annotate('Longer Arrows Near Center\n(High Field Strength)', xy=(0.35, 0.35), xytext=(0.85, 1.45),
             arrowprops=dict(facecolor='#1f2d3d', shrink=0.08, width=1.6, headwidth=6.5),
             fontweight='bold', fontsize=12.5,
             bbox=dict(boxstyle='round,pad=0.35', facecolor='#fff5eb', edgecolor='#d35400', lw=1.5))

ax1.annotate('Smaller Arrows at Distance\n(Decaying Field Strength)', xy=(1.45, -0.95), xytext=(0.40, -2.15),
             arrowprops=dict(facecolor='#1f2d3d', shrink=0.08, width=1.6, headwidth=6.5),
             fontweight='bold', fontsize=12.5,
             bbox=dict(boxstyle='round,pad=0.35', facecolor='#f8f9fa', edgecolor='#7f8c8d', lw=1.5))

ax1.set_xlim(-grid_lim, grid_lim)
ax1.set_ylim(-grid_lim, grid_lim)
ax1.set_title('(a) 2D Equipotential Shells & Vector Field', fontweight='bold', pad=14)
ax1.set_xlabel('Spatial Coordinate $x_1$', fontweight='bold')
ax1.set_ylabel('Spatial Coordinate $x_2$', fontweight='bold')
ax1.legend(loc='lower left', framealpha=0.94, edgecolor='#cccccc', fontsize=11.5)
ax1.grid(True, linestyle='--', alpha=0.35)

# -------------------------------------------------------------------------
# Panel (b): 3D Single-Point Potential Energy Mesa
# -------------------------------------------------------------------------
ax2 = fig.add_subplot(1, 3, 2, projection='3d')

res_3d = 80
x3 = np.linspace(-grid_lim, grid_lim, res_3d)
y3 = np.linspace(-grid_lim, grid_lim, res_3d)
X3, Y3 = np.meshgrid(x3, y3)
D3 = np.sqrt(X3**2 + Y3**2)

I_3d = np.zeros_like(D3)
I_3d[D3 <= R_core] = 1.0
mask_3d = (D3 > R_core) & (D3 <= R_horizon)
u_3d = (D3[mask_3d] - R_core) / R_decay
I_3d[mask_3d] = np.exp(-lam * (u_3d ** alpha))

surf = ax2.plot_surface(X3, Y3, I_3d, cmap='Reds', edgecolor='none', alpha=0.90, zorder=2)

# Wireframe flat base
z_zero = np.zeros_like(X3)
ax2.plot_wireframe(X3, Y3, z_zero, color='gray', linestyle=':', linewidth=0.6, alpha=0.30, zorder=1)

# Concentric circle projections on ground plane
theta_ring = np.linspace(0, 2*np.pi, 120)
x_rc = R_core * np.cos(theta_ring)
y_rc = R_core * np.sin(theta_ring)
ax2.plot(x_rc, y_rc, np.zeros_like(x_rc), color='#b30000', linewidth=2.6, linestyle='-', zorder=3)

x_rh = R_horizon * np.cos(theta_ring)
y_rh = R_horizon * np.sin(theta_ring)
ax2.plot(x_rh, y_rh, np.zeros_like(x_rh), color='#d35400', linewidth=2.2, linestyle='--', zorder=3)

# 3D Vector arrows descending down the potential slope
quiver_radii_3d = [0.85, 1.30, 1.70]
quiver_angles_3d = [np.pi/4, 3*np.pi/4, 5*np.pi/4, 7*np.pi/4]
for r3 in quiver_radii_3d:
    u_val = (r3 - R_core) / R_decay
    z_val = np.exp(-lam * (u_val ** alpha))
    dz_dr = -(lam * alpha / R_decay) * (u_val ** (alpha - 1)) * z_val
    mag3 = 0.35 * (1.0 - 0.75 * (r3 / R_horizon))
    for ang3 in quiver_angles_3d:
        qx3 = r3 * np.cos(ang3)
        qy3 = r3 * np.sin(ang3)
        ax2.quiver(qx3, qy3, z_val, mag3*np.cos(ang3), mag3*np.sin(ang3), mag3*dz_dr*0.6,
                   color='#1f2d3d', arrow_length_ratio=0.35, linewidth=1.8, zorder=5)

# Text labels on 3D plot
ax2.text(0, 0, 1.08, 'Certainty Core Plateau\n($I \\equiv 1.0, R^{\\mathrm{core}}$)',
         ha='center', va='bottom', fontweight='bold', fontsize=12, color='#660000', zorder=7)
ax2.text(1.2, 1.2, 0.40, 'Decay Skirt\n($R^{\\mathrm{decay}}$)',
         ha='center', va='center', fontweight='bold', fontsize=12, color='#9c4100', zorder=7)
ax2.text(1.6, -1.6, 0.03, 'Ground Vacuum ($I = 0$)',
         ha='center', va='center', fontweight='bold', fontsize=11.5, color='#555555', zorder=7)

ax2.set_zlim(0.0, 1.28)
ax2.set_title('(b) 3D Potential Energy Mesa Landscape', fontweight='bold', pad=14)
ax2.set_xlabel('$x_1$', fontweight='bold', labelpad=8)
ax2.set_ylabel('$x_2$', fontweight='bold', labelpad=8)
ax2.set_zlabel('Potential $I(d)$', fontweight='bold', labelpad=8)
ax2.view_init(elev=30, azim=132)

# -------------------------------------------------------------------------
# Panel (c): 1D Radial Influence Profile I(d) vs. Field Strength ||F(d)||
# -------------------------------------------------------------------------
ax3 = fig.add_subplot(1, 3, 3)

d_fine = np.linspace(0, 2.4, 500)
I_1d = np.zeros_like(d_fine)
Field_Strength = np.zeros_like(d_fine)

for idx, dist in enumerate(d_fine):
    if dist <= R_core:
        I_1d[idx] = 1.0
        # High field strength inside core
        Field_Strength[idx] = 1.0
    elif dist <= R_horizon:
        u = (dist - R_core) / R_decay
        val = np.exp(-lam * (u ** alpha))
        I_1d[idx] = val
        # Decaying field strength across decay shell
        Field_Strength[idx] = 1.0 - 0.85 * ((dist / R_horizon) ** 1.1)
    else:
        I_1d[idx] = 0.0
        Field_Strength[idx] = 0.0

# Plot Potential Profile on left y-axis
color_p = '#b30000'
ax3.plot(d_fine, I_1d, color=color_p, linewidth=3.4, label='Scalar Potential $I(d)$ (Plateau + Exponential Decay)')
ax3.set_xlabel('Euclidean Distance from Anchor $d = \\|\\mathbf{x} - \\mathbf{x}_i\\|_2$', fontweight='bold')
ax3.set_ylabel('Potential Field Influence $I(d)$', color=color_p, fontweight='bold')
ax3.tick_params(axis='y', labelcolor=color_p)

# Zone fills
ax3.axvspan(0, R_core, color='#b30000', alpha=0.15, label=f'Certainty Core ($R^{{\\mathrm{{core}}}}={R_core:.2f}$)')
ax3.axvspan(R_core, R_horizon, color='#f39c12', alpha=0.16, label=f'Decay Shell ($R^{{\\mathrm{{decay}}}}={R_decay:.2f}$)')
ax3.axvspan(R_horizon, 2.4, color='#bdc3c7', alpha=0.14, label='Zero-Support Vacuum ($I \\equiv 0$)')

# Second y-axis for Field Strength (Arrow length)
ax3_twin = ax3.twinx()
color_f = '#1f2d3d'
ax3_twin.plot(d_fine, Field_Strength, color=color_f, linewidth=2.8, linestyle='-.',
              label='Field Strength / Vector Magnitude $\\|\\mathbf{F}(d)\\|_2$')
ax3_twin.set_ylabel('Force Vector Magnitude $\\|\\mathbf{F}(d)\\|_2$', color=color_f, fontweight='bold')
ax3_twin.tick_params(axis='y', labelcolor=color_f)

# Dimension line at top of Panel (c)
y_top_dim = 1.07
ax3.annotate('', xy=(R_core, y_top_dim), xytext=(0, y_top_dim),
             arrowprops=dict(arrowstyle='<->', color='#8b0000', lw=2.4))
ax3.text(R_core/2, y_top_dim + 0.02, '$R^{\\mathrm{core}}$', ha='center', va='bottom',
         fontweight='bold', fontsize=14, color='#8b0000')

ax3.annotate('', xy=(R_horizon, y_top_dim), xytext=(R_core, y_top_dim),
             arrowprops=dict(arrowstyle='<->', color='#d35400', lw=2.4))
ax3.text((R_core + R_horizon)/2, y_top_dim + 0.02, '$R^{\\mathrm{decay}}$', ha='center', va='bottom',
         fontweight='bold', fontsize=14, color='#d35400')

ax3.set_xlim(0, 2.4)
ax3.set_ylim(-0.05, 1.18)
ax3_twin.set_ylim(-0.05, 1.18)
ax3.set_title('(c) 1D Radial Influence $I(d)$ vs. Field Strength $\\|\\mathbf{F}(d)\\|_2$', fontweight='bold', pad=14)
ax3.grid(True, linestyle='--', alpha=0.35)

# Legends combined cleanly
lines_1, labels_1 = ax3.get_legend_handles_labels()
lines_2, labels_2 = ax3_twin.get_legend_handles_labels()
ax3.legend(lines_1 + lines_2, labels_1 + labels_2, loc='center right', framealpha=0.92, fontsize=11.2)

plt.suptitle('Electrostatic Potential Field, Core & Decay Radii, and Force Vector Dynamics of an Isolated Support Anchor',
             fontsize=22, fontweight='bold', y=0.99)
plt.subplots_adjust(left=0.05, right=0.94, bottom=0.10, top=0.90, wspace=0.26)

out_fig = os.path.join(OUTPUT_DIR, "single_point_potential_2d_3d.png")
plt.savefig(out_fig, dpi=300, bbox_inches='tight')
plt.close()
print(f"Successfully generated flagship single point potential figure: {out_fig}")
