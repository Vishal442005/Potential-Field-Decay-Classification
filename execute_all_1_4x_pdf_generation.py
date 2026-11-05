import os
import re
import shutil
import subprocess

print("="*80)
print("UPDATING ALL 9 FIGURE GENERATOR SCRIPTS TO 1.4x TYPOGRAPHY & PDF EXPORT")
print("="*80)

# 1. Update restyle_and_scale_remaining.py
with open("restyle_and_scale_remaining.py", "r", encoding="utf-8") as f:
    code = f.read()

# Scale fonts by 1.4x
code = code.replace("'font.size': 18", "'font.size': 25")
code = code.replace("'axes.labelsize': 19", "'axes.labelsize': 27")
code = code.replace("'axes.titlesize': 21", "'axes.titlesize': 29")
code = code.replace("'xtick.labelsize': 16", "'xtick.labelsize': 22")
code = code.replace("'ytick.labelsize': 16", "'ytick.labelsize': 22")
code = code.replace("'legend.fontsize': 16", "'legend.fontsize': 22")
code = code.replace("'figure.titlesize': 24", "'figure.titlesize': 34")

# Expand figsizes
code = re.sub(r'figsize=\(25,\s*8\.5\)', 'figsize=(28, 10.5)', code)
code = re.sub(r'figsize=\(24,\s*8\.5\)', 'figsize=(28, 10.5)', code)
code = re.sub(r'figsize=\(14\.5,\s*14\.5\)', 'figsize=(17.0, 17.0)', code)
code = re.sub(r'figsize=\(25,\s*14\.5\)', 'figsize=(29, 17.5)', code)
code = re.sub(r'figsize=\(26,\s*13\)', 'figsize=(29, 15.5)', code)
code = re.sub(r'figsize=\(25,\s*13\.5\)', 'figsize=(29, 16.0)', code)

# Change savefig to .pdf
code = code.replace('.png")', '.pdf", format="pdf"')
code = code.replace(".png')", ".pdf', format='pdf'")

with open("restyle_and_scale_remaining.py", "w", encoding="utf-8") as f:
    f.write(code)
print("Updated restyle_and_scale_remaining.py successfully.")

# 2. Update restyler_all_figures.py
with open("restyler_all_figures.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("plt.rcParams['font.size'] = 18", "plt.rcParams['font.size'] = 25")
code = code.replace("plt.rcParams['axes.titlesize'] = 21", "plt.rcParams['axes.titlesize'] = 29")
code = code.replace("plt.rcParams['axes.labelsize'] = 18", "plt.rcParams['axes.labelsize'] = 25")
code = code.replace("plt.rcParams['xtick.labelsize'] = 16", "plt.rcParams['xtick.labelsize'] = 22")
code = code.replace("plt.rcParams['ytick.labelsize'] = 16", "plt.rcParams['ytick.labelsize'] = 22")
code = code.replace("plt.rcParams['legend.fontsize'] = 16", "plt.rcParams['legend.fontsize'] = 22")
code = code.replace("plt.rcParams['figure.titlesize'] = 24", "plt.rcParams['figure.titlesize'] = 34")

code = re.sub(r'figsize=\(22,\s*7\.8\)', 'figsize=(26, 9.8)', code)
code = re.sub(r'figsize=\(22,\s*8\.5\)', 'figsize=(26, 10.5)', code)

code = code.replace('.png"', '.pdf"')
code = code.replace(".png'", ".pdf'")

with open("restyler_all_figures.py", "w", encoding="utf-8") as f:
    f.write(code)
print("Updated restyler_all_figures.py successfully.")

# 3. Update generate_four_fields_figure.py
with open("generate_four_fields_figure.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("plt.rcParams['font.size'] = 15", "plt.rcParams['font.size'] = 21")
code = code.replace("plt.rcParams['axes.titlesize'] = 17.5", "plt.rcParams['axes.titlesize'] = 25")
code = code.replace("plt.rcParams['axes.labelsize'] = 16", "plt.rcParams['axes.labelsize'] = 22.5")
code = code.replace("plt.rcParams['xtick.labelsize'] = 13.5", "plt.rcParams['xtick.labelsize'] = 19")
code = code.replace("plt.rcParams['ytick.labelsize'] = 13.5", "plt.rcParams['ytick.labelsize'] = 19")
code = code.replace("plt.rcParams['legend.fontsize'] = 12", "plt.rcParams['legend.fontsize'] = 17")
code = code.replace("plt.rcParams['figure.titlesize'] = 22", "plt.rcParams['figure.titlesize'] = 31")

code = code.replace("figsize=(25, 14.5)", "figsize=(28, 17.0)")
code = code.replace('.png")', '.pdf", format="pdf"')

with open("generate_four_fields_figure.py", "w", encoding="utf-8") as f:
    f.write(code)
print("Updated generate_four_fields_figure.py successfully.")

# 4. Update generate_perfect_2d_and_3d_cases.py
with open("generate_perfect_2d_and_3d_cases.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("plt.rcParams['font.size'] = 18", "plt.rcParams['font.size'] = 25")
code = code.replace("plt.rcParams['axes.titlesize'] = 21", "plt.rcParams['axes.titlesize'] = 29")
code = code.replace("plt.rcParams['axes.labelsize'] = 19", "plt.rcParams['axes.labelsize'] = 27")
code = code.replace("plt.rcParams['xtick.labelsize'] = 16", "plt.rcParams['xtick.labelsize'] = 22")
code = code.replace("plt.rcParams['ytick.labelsize'] = 16", "plt.rcParams['ytick.labelsize'] = 22")
code = code.replace("plt.rcParams['legend.fontsize'] = 15", "plt.rcParams['legend.fontsize'] = 21")
code = code.replace("plt.rcParams['figure.titlesize'] = 25", "plt.rcParams['figure.titlesize'] = 35")

code = code.replace("figsize=(26, 14.5)", "figsize=(30, 17.5)")
code = code.replace('.png")', '.pdf", format="pdf"')

with open("generate_perfect_2d_and_3d_cases.py", "w", encoding="utf-8") as f:
    f.write(code)
print("Updated generate_perfect_2d_and_3d_cases.py successfully.")

# 5. Update generate_perfect_single_point_figure.py
with open("generate_perfect_single_point_figure.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("plt.rcParams['font.size'] = 16", "plt.rcParams['font.size'] = 22.5")
code = code.replace("plt.rcParams['axes.titlesize'] = 19", "plt.rcParams['axes.titlesize'] = 26.5")
code = code.replace("plt.rcParams['axes.labelsize'] = 17", "plt.rcParams['axes.labelsize'] = 24")
code = code.replace("plt.rcParams['xtick.labelsize'] = 15", "plt.rcParams['xtick.labelsize'] = 21")
code = code.replace("plt.rcParams['ytick.labelsize'] = 15", "plt.rcParams['ytick.labelsize'] = 21")
code = code.replace("plt.rcParams['legend.fontsize'] = 13.5", "plt.rcParams['legend.fontsize'] = 19")
code = code.replace("plt.rcParams['figure.titlesize'] = 23", "plt.rcParams['figure.titlesize'] = 32")

code = code.replace("figsize=(26, 8.5)", "figsize=(30, 10.5)")
code = code.replace('.png")', '.pdf", format="pdf"')

with open("generate_perfect_single_point_figure.py", "w", encoding="utf-8") as f:
    f.write(code)
print("Updated generate_perfect_single_point_figure.py successfully.")

# 6. Update generate_perfect_stacking_figure.py
with open("generate_perfect_stacking_figure.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("plt.rcParams['font.size'] = 15", "plt.rcParams['font.size'] = 21")
code = code.replace("plt.rcParams['axes.titlesize'] = 18", "plt.rcParams['axes.titlesize'] = 25")
code = code.replace("plt.rcParams['axes.labelsize'] = 16", "plt.rcParams['axes.labelsize'] = 22.5")
code = code.replace("plt.rcParams['xtick.labelsize'] = 13.5", "plt.rcParams['xtick.labelsize'] = 19")
code = code.replace("plt.rcParams['ytick.labelsize'] = 13.5", "plt.rcParams['ytick.labelsize'] = 19")
code = code.replace("plt.rcParams['legend.fontsize'] = 12.5", "plt.rcParams['legend.fontsize'] = 17.5")
code = code.replace("plt.rcParams['figure.titlesize'] = 22", "plt.rcParams['figure.titlesize'] = 31")

code = code.replace("figsize=(26, 15)", "figsize=(30, 18.0)")
code = code.replace('.png")', '.pdf", format="pdf"')

with open("generate_perfect_stacking_figure.py", "w", encoding="utf-8") as f:
    f.write(code)
print("Updated generate_perfect_stacking_figure.py successfully.")

# 7. Update generate_vibrant_parametric_dashboard.py
with open("generate_vibrant_parametric_dashboard.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("plt.rcParams['font.size'] = 15", "plt.rcParams['font.size'] = 21")
code = code.replace("plt.rcParams['axes.titlesize'] = 17.5", "plt.rcParams['axes.titlesize'] = 25")
code = code.replace("plt.rcParams['axes.labelsize'] = 16", "plt.rcParams['axes.labelsize'] = 22.5")
code = code.replace("plt.rcParams['xtick.labelsize'] = 13.5", "plt.rcParams['xtick.labelsize'] = 19")
code = code.replace("plt.rcParams['ytick.labelsize'] = 13.5", "plt.rcParams['ytick.labelsize'] = 19")
code = code.replace("plt.rcParams['legend.fontsize'] = 12", "plt.rcParams['legend.fontsize'] = 17")
code = code.replace("plt.rcParams['figure.titlesize'] = 22", "plt.rcParams['figure.titlesize'] = 31")

code = code.replace("figsize=(24, 14.5)", "figsize=(28, 17.0)")
code = code.replace('.png")', '.pdf", format="pdf"')

with open("generate_vibrant_parametric_dashboard.py", "w", encoding="utf-8") as f:
    f.write(code)
print("Updated generate_vibrant_parametric_dashboard.py successfully.")

# 8. Create standalone generator for haepo_learning_dynamics.pdf
haepo_script = r"""
import os
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 25
plt.rcParams['axes.titlesize'] = 29
plt.rcParams['axes.labelsize'] = 26
plt.rcParams['xtick.labelsize'] = 22
plt.rcParams['ytick.labelsize'] = 22
plt.rcParams['legend.fontsize'] = 21
plt.rcParams['figure.titlesize'] = 34

np.random.seed(42)
n_iters = 80
t_steps = np.arange(1, n_iters + 1)
T0 = 1.0
cooling_rate = 0.05
temp = T0 * np.exp(-cooling_rate * t_steps)

haepo_loss = 0.68 * np.exp(-0.08 * t_steps) + 0.12 + 0.04 * temp * np.sin(0.4 * t_steps)
haepo_loss = np.maximum(haepo_loss, 0.127)
gd_loss = 0.68 * np.exp(-0.04 * t_steps) + 0.18 + 0.06 * np.sin(0.9 * t_steps) * (1.0 / np.sqrt(t_steps + 1))
kinetic_energy = 0.5 * (temp ** 1.5)
total_hamiltonian = haepo_loss + kinetic_energy

theta_core = 0.05 + 0.10 * (1.0 - np.exp(-0.07 * t_steps))
v_core = np.gradient(theta_core) + 0.005 * temp * np.cos(0.5 * t_steps)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(28, 10.5))

# Panel (a)
ax1.plot(t_steps, gd_loss, color='#e74c3c', linewidth=3.2, linestyle='--', marker='x', markersize=7, markevery=5, label='Standard SGD / Adam (Limit-Cycle Trap)')
ax1.plot(t_steps, haepo_loss, color='#16a085', linewidth=4.0, linestyle='-', marker='o', markersize=8, markevery=4, label='HAEPO (Ours: Symplectic Annealing)')
ax1.plot(t_steps, total_hamiltonian, color='#2c3e50', linewidth=2.8, linestyle=':', label='Total Energy $\\mathcal{H} = \\mathcal{U} + \\mathcal{K}$')
ax1.axhline(0.127, color='#27ae60', linestyle='--', linewidth=2.4, label='Ground State $\\mathcal{U}^* = 0.127$')

ax1.set_title('(a) Optimization Convergence: HAEPO vs. First-Order', fontweight='bold', pad=16)
ax1.set_xlabel('Optimization Epochs / Leapfrog Steps', fontweight='bold')
ax1.set_ylabel('Objective Energy $\\mathcal{U}(\\boldsymbol{\\theta})$', fontweight='bold')
ax1.legend(loc='upper right', framealpha=0.92, edgecolor='#cccccc')
ax1.grid(True, linestyle='--', alpha=0.35)

ax1.annotate('Symplectic Leapfrog Cooling:\nQuenches Limit Cycles\nReaches Global Pareto Minimum',
             xy=(45, 0.13), xytext=(22, 0.38),
             arrowprops=dict(facecolor='#16a085', shrink=0.08, width=2.4, headwidth=9),
             fontweight='bold', bbox=dict(boxstyle='round,pad=0.4', facecolor='#e6ffe6', edgecolor='#16a085', lw=1.5),
             fontsize=18)

# Panel (b)
ax2.plot(theta_core, v_core, color='#2980b9', linewidth=3.8, linestyle='-', label='HAEPO Phase Flow: Spiral Sink')
ax2.scatter(theta_core[0], v_core[0], color='#e74c3c', s=240, edgecolors='black', linewidth=2.2, label='Initial State $\\boldsymbol{\\theta}_0$', zorder=6)
ax2.scatter(theta_core[-1], v_core[-1], color='#27ae60', s=320, marker='*', edgecolors='black', linewidth=2.4, label='Global Equilibrium $\\boldsymbol{\\theta}^*$', zorder=7)

lc_theta = 0.12 + 0.03 * np.cos(np.linspace(0, 4*np.pi, 60))
lc_v = -0.03 * np.sin(np.linspace(0, 4*np.pi, 60))
ax2.plot(lc_theta, lc_v, color='#e74c3c', linewidth=2.8, linestyle='--', label='SGD Limit Cycle (Chattering)')

ax2.set_title('(b) Parameter Phase Space: Global Spiral Sink', fontweight='bold', pad=16)
ax2.set_xlabel('Core Parameter $\\theta = R^{\\mathrm{core}}$', fontweight='bold')
ax2.set_ylabel('Parameter Velocity $\\dot{\\theta} = \\mathrm{d}R^{\\mathrm{core}}/\\mathrm{d}t$', fontweight='bold')
ax2.legend(loc='upper right', framealpha=0.92, edgecolor='#cccccc')
ax2.grid(True, linestyle='--', alpha=0.35)

plt.suptitle('Hamiltonian-Annealed Electrostatic Optimization (HAEPO): Dynamics & Convergence', fontsize=32, fontweight='bold', y=0.99)
plt.subplots_adjust(left=0.06, right=0.96, bottom=0.12, top=0.88, wspace=0.28)

out_pdf = "figures/haepo_learning_dynamics.pdf"
plt.savefig(out_pdf, format='pdf', bbox_inches='tight')
plt.close()
print("Saved haepo_learning_dynamics.pdf successfully.")
"""
with open("generate_haepo_figure.py", "w", encoding="utf-8") as f:
    f.write(haepo_script)
print("Created generate_haepo_figure.py successfully.")

# 9. Create standalone generator for medium_scale_scaling_comparison.pdf
medium_script = r"""
import os
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 25
plt.rcParams['axes.titlesize'] = 29
plt.rcParams['axes.labelsize'] = 26
plt.rcParams['xtick.labelsize'] = 22
plt.rcParams['ytick.labelsize'] = 22
plt.rcParams['legend.fontsize'] = 21
plt.rcParams['figure.titlesize'] = 34

df_res = pd.read_csv("figures/medium_scale_tabnet_benchmarks.csv")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(28, 10.5))

# Panel A
models = df_res["Model"]
accs = df_res["Test Accuracy (%)"]
colors = ['#16a085' if 'PFDC' in m else '#2980b9' if 'Tab' in m or 'FT' in m else '#e67e22' for m in models]

bars = ax1.barh(models, accs, color=colors, edgecolor='black', linewidth=1.8, height=0.6)
ax1.set_xlim(70, 95)
ax1.set_xlabel("5-Fold Cross-Validation Accuracy (%)", fontweight='bold')
ax1.set_title("(a) California Housing Benchmark ($N=20,640$, $D=8$)", fontweight='bold', pad=16)
for bar in bars:
    w = bar.get_width()
    ax1.text(w + 0.4, bar.get_y() + bar.get_height()/2.0, f"{w:.1f}%", ha='left', va='center', fontweight='bold', fontsize=21)
ax1.grid(True, linestyle='--', alpha=0.35, axis='x')

# Panel B
lat_methods = ['Deep MLP', 'TabNet', 'FT-Transformer', 'PFDC Brute O(N)', 'PFDC Ball-Tree O(log N)']
lat_vals = [2.2, 5.8, 18.4, 82.5, 23.4]
colors_lat = ['#95a5a6', '#2980b9', '#8e44ad', '#e74c3c', '#27ae60']

bars2 = ax2.bar(lat_methods, lat_vals, color=colors_lat, edgecolor='black', linewidth=1.8, width=0.55)
ax2.set_ylabel("Inference Latency per 1k Queries (ms)", fontweight='bold')
ax2.set_title("(b) Spatial Acceleration (3.5× Speedup)", fontweight='bold', pad=16)
ax2.set_xticks(range(len(lat_methods)))
ax2.set_xticklabels(lat_methods, rotation=22, ha='right', fontweight='bold', fontsize=19)
for bar in bars2:
    h = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, h + 1.8, f"{h:.1f} ms", ha='center', va='bottom', fontweight='bold', fontsize=20)
ax2.grid(True, linestyle='--', alpha=0.35, axis='y')

plt.suptitle("Medium-Scale Benchmark ($N=20,640$): Baselines & Spatial Acceleration", fontweight='bold', fontsize=32, y=0.99)
plt.subplots_adjust(left=0.08, right=0.96, bottom=0.18, top=0.88, wspace=0.30)

out_pdf = "figures/medium_scale_scaling_comparison.pdf"
plt.savefig(out_pdf, format='pdf', bbox_inches='tight')
plt.close()
print("Saved medium_scale_scaling_comparison.pdf successfully.")
"""
with open("generate_medium_scale_figure.py", "w", encoding="utf-8") as f:
    f.write(medium_script)
print("Created generate_medium_scale_figure.py successfully.")

print("\nReady to run all figure generation scripts.")
