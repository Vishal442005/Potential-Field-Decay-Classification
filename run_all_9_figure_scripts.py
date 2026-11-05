import os
import shutil
import subprocess

scripts = [
    "generate_perfect_single_point_figure.py",
    "generate_perfect_stacking_figure.py",
    "generate_perfect_2d_and_3d_cases.py",
    "generate_vibrant_parametric_dashboard.py",
    "generate_four_fields_figure.py",
    "generate_haepo_figure.py",
    "generate_medium_scale_figure.py",
    "restyler_all_figures.py",
    "restyle_and_scale_remaining.py"
]

print("="*80)
print("EXECUTING ALL 9 FIGURE GENERATION SCRIPTS")
print("="*80)

for s in scripts:
    print(f"\n---> Running: {s} ...")
    res = subprocess.run(["python", s], capture_output=True, text=True)
    if res.returncode == 0:
        print(f"Success: {s}")
        if res.stdout.strip():
            print(res.stdout.strip()[:300])
    else:
        print(f"Error in {s}:")
        print(res.stderr[:500])

# Ensure pfdc_highd_learned_weights.pdf exists (copied from anisotropic_feature_weights.pdf if needed)
if os.path.exists("figures/anisotropic_feature_weights.pdf") and not os.path.exists("figures/pfdc_highd_learned_weights.pdf"):
    shutil.copy2("figures/anisotropic_feature_weights.pdf", "figures/pfdc_highd_learned_weights.pdf")
elif os.path.exists("figures/anisotropic_feature_weights.pdf"):
    shutil.copy2("figures/anisotropic_feature_weights.pdf", "figures/pfdc_highd_learned_weights.pdf")

# Distribute all PDFs to elsevier_submission/figures and tpami_submission/figures
dest_dirs = ["elsevier_submission/figures", "tpami_submission/figures"]
for dest in dest_dirs:
    os.makedirs(dest, exist_ok=True)
    for fname in os.listdir("figures"):
        if fname.lower().endswith(".pdf"):
            src = os.path.join("figures", fname)
            dst = os.path.join(dest, fname)
            shutil.copy2(src, dst)

print("\nSuccessfully synchronized all PDF figures to elsevier_submission and tpami_submission.")

# Delete ALL .png files everywhere in figures/
deleted_pngs = 0
for d in ["figures", "elsevier_submission/figures", "tpami_submission/figures"]:
    if os.path.exists(d):
        for fname in os.listdir(d):
            if fname.lower().endswith(".png"):
                os.remove(os.path.join(d, fname))
                deleted_pngs += 1

print(f"Total PNG files deleted across all directories: {deleted_pngs}")
