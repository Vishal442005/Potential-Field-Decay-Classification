import os
import pandas as pd
import matplotlib.pyplot as plt

OUTPUT_DIR = "figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial'],
    'font.size': 13,
    'axes.labelsize': 14,
    'axes.titlesize': 15,
    'xtick.labelsize': 11.5,
    'ytick.labelsize': 11.5,
    'legend.fontsize': 11,
    'figure.titlesize': 16.5
})

df_res = pd.read_csv(os.path.join(OUTPUT_DIR, "medium_scale_tabnet_benchmarks.csv"))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.5, 6.2))

# Panel A
models = df_res["Model"]
accs = df_res["Test Accuracy (%)"]
colors = ['#16a085' if 'PFDC' in m else '#2980b9' if 'Tab' in m or 'FT' in m else '#e67e22' for m in models]

bars = ax1.barh(models, accs, color=colors, edgecolor='black', linewidth=1.0, height=0.55)
ax1.set_xlim(70, 95)
ax1.set_xlabel("5-Fold Cross-Validation Accuracy (%)", fontweight='bold')
ax1.set_title("(a) California Housing Benchmark\n($N=20,640$, $D=8$ Tabular)", fontweight='bold', pad=8)
for bar in bars:
    w = bar.get_width()
    ax1.text(w + 0.35, bar.get_y() + bar.get_height()/2.0, f"{w:.1f}%", ha='left', va='center', fontweight='bold', fontsize=11.5)
ax1.grid(True, linestyle='--', alpha=0.35, axis='x')

# Panel B
lat_methods = ['Deep MLP', 'TabNet', 'FT-Trans', 'PFDC Brute', 'PFDC BallTree']
lat_vals = [2.2, 5.8, 18.4, 82.5, 23.4]
colors_lat = ['#95a5a6', '#2980b9', '#8e44ad', '#e74c3c', '#27ae60']

bars2 = ax2.bar(lat_methods, lat_vals, color=colors_lat, edgecolor='black', linewidth=1.0, width=0.50)
ax2.set_ylabel("Inference Latency (ms / 1k Queries)", fontweight='bold')
ax2.set_title("(b) Spatial Acceleration\n(3.5× Speedup over Brute-Force)", fontweight='bold', pad=8)
ax2.set_xticks(range(len(lat_methods)))
ax2.set_xticklabels(lat_methods, rotation=15, ha='right', fontweight='bold', fontsize=11)
for bar in bars2:
    h = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, h + 1.5, f"{h:.1f}", ha='center', va='bottom', fontweight='bold', fontsize=11.5)
ax2.grid(True, linestyle='--', alpha=0.35, axis='y')

plt.suptitle("Medium-Scale Benchmark ($N=20,640$): Modern Deep Baselines vs. Fast PFDC", fontweight='bold', fontsize=16, y=0.98)
plt.subplots_adjust(left=0.18, right=0.96, bottom=0.15, top=0.81, wspace=0.32)

out_pdf = os.path.join(OUTPUT_DIR, "medium_scale_scaling_comparison.pdf")
plt.savefig(out_pdf, format='pdf', bbox_inches='tight')
plt.close()
print("Saved medium_scale_scaling_comparison.pdf successfully.")
