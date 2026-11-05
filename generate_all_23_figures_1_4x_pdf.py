import sys
import os
import shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches as patches
from scipy.stats import norm
from sklearn.datasets import make_classification, load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_curve, auc

# Ensure directories exist
OUTPUT_DIRS = [
    "figures",
    os.path.join("elsevier_submission", "figures"),
    os.path.join("tpami_submission", "figures")
]
for d in OUTPUT_DIRS:
    os.makedirs(d, exist_ok=True)

# 1.4x Scaled Global Typography Settings
# Base standard publication fonts multiplied by 1.4x
GLOBAL_RC = {
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial'],
    'font.size': 25,
    'axes.labelsize': 26,
    'axes.titlesize': 29,
    'xtick.labelsize': 22,
    'ytick.labelsize': 22,
    'legend.fontsize': 21,
    'figure.titlesize': 34
}
plt.rcParams.update(GLOBAL_RC)

def save_and_distribute(fig, base_name):
    pdf_name = f"{base_name}.pdf"
    root_path = os.path.join("figures", pdf_name)
    fig.savefig(root_path, format='pdf', bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {root_path}")
    
    # Copy to submission folders
    for d in OUTPUT_DIRS[1:]:
        dest = os.path.join(d, pdf_name)
        shutil.copy2(root_path, dest)
        
    # Delete any lingering png with same base_name
    for d in OUTPUT_DIRS:
        png_path = os.path.join(d, f"{base_name}.png")
        if os.path.exists(png_path):
            os.remove(png_path)
            print(f"Deleted PNG: {png_path}")

print("="*80)
print("REGENERATING ALL MANUSCRIPT FIGURES WITH 1.4x TYPOGRAPHY DIRECTLY TO PDF")
print("="*80)
