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
from pfdc_engine import DynamicPFDC
from dual_charge_pfdc import DualChargePFDC

OUTPUT_DIRS = [
    "figures",
    os.path.join("elsevier_submission", "figures"),
    os.path.join("tpami_submission", "figures")
]
for d in OUTPUT_DIRS:
    os.makedirs(d, exist_ok=True)

# 1.4x Typography Settings
GLOBAL_RC = {
    'font.family': 'DejaVu Sans',
    'font.size': 24,
    'axes.labelsize': 26,
    'axes.titlesize': 28,
    'xtick.labelsize': 21,
    'ytick.labelsize': 21,
    'legend.fontsize': 20,
    'figure.titlesize': 33
}
plt.rcParams.update(GLOBAL_RC)

def save_and_distribute(fig, base_name):
    pdf_name = f"{base_name}.pdf"
    root_path = os.path.join("figures", pdf_name)
    fig.savefig(root_path, format='pdf', bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {root_path}")
    
    for d in OUTPUT_DIRS[1:]:
        dest = os.path.join(d, pdf_name)
        shutil.copy2(root_path, dest)
        
    for d in OUTPUT_DIRS:
        png_path = os.path.join(d, f"{base_name}.png")
        if os.path.exists(png_path):
            os.remove(png_path)
            print(f"Deleted PNG: {png_path}")

print("="*80)
print("GENERATING 23 MANUSCRIPT FIGURES WITH 1.4x SCALED FONTS & ANTI-OVERLAP CANVAS DIRECTLY TO PDF")
print("="*80)
