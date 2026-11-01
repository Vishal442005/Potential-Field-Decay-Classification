import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.datasets import make_moons, make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, log_loss
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier

# Import custom modules
from pfdc_engine import DynamicPFDC
from rl_classifier import ReinforcementLearningClassifier
from unsupervised_classifier import UnsupervisedGMMClassifier, SelfSupervisedContrastiveClassifier

# Optional imports with graceful fallbacks
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

try:
    import lightgbm as lgb
    LGB_AVAILABLE = True
except ImportError:
    LGB_AVAILABLE = False

# Ensure output directory for figures exists
OUTPUT_DIR = "figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set high-quality plotting aesthetics
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

def generate_2d_benchmark_dataset(n_samples=1200, random_state=42):
    """
    Generates a 2-independent variables dataset with non-linear separable structures,
    measurement noise, and realistic intra-cluster dispersion.
    """
    print(f"Generating 2D benchmark dataset (2 Independent Variables, {n_samples} samples)...")
    # Intertwined multi-cluster with non-linear boundary
    X_moons, y_moons = make_moons(n_samples=n_samples, noise=0.22, random_state=random_state)
    
    # Stratified 70/30 split
    X_train, X_test, y_train, y_test = train_test_split(
        X_moons, y_moons, test_size=0.30, stratify=y_moons, random_state=random_state
    )
    print(f"Dataset split: Train = {X_train.shape[0]} samples, Test = {X_test.shape[0]} samples.")
    return X_train, X_test, y_train, y_test

def evaluate_model(name, model, X_train, y_train, X_test, y_test):
    """
    Fits and evaluates a model, measuring accuracy, precision, recall, f1, auc, and timing.
    """
    t0 = time.time()
    model.fit(X_train, y_train)
    fit_time = time.time() - t0
    
    t0 = time.time()
    y_pred = model.predict(X_test)
    inference_time = (time.time() - t0) * 1000.0 # in ms
    
    # Probabilities for AUC
    try:
        y_prob = model.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, y_prob)
        bce = log_loss(y_test, y_prob)
    except Exception:
        y_prob = y_pred
        auc = roc_auc_score(y_test, y_pred)
        bce = np.nan

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    return {
        "Model": name,
        "Accuracy (%)": acc * 100.0,
        "F1-Score": f1,
        "Precision": prec,
        "Recall": rec,
        "ROC-AUC": auc,
        "Test BCE Loss": bce,
        "Fit Time (s)": fit_time,
        "Inference Time (ms)": inference_time
    }

def run_pfdc_three_cases_comparison(X_train, y_train, X_test, y_test):
    """
    Runs the comprehensive comparison across the 3 PFDC dynamic learning-rate cases:
    - Case 1: Fixed
    - Case 2: Halved on sign shift
    - Case 3: Exponentially accelerating decrease on sign shift
    """
    print("\n" + "="*70)
    print("STEP 1: Training PFDC Across the 3 Dynamic Learning-Rate Cases")
    print("="*70)
    
    cases = [
        ("Case 1 (Fixed)", "fixed"),
        ("Case 2 (Halved)", "halved"),
        ("Case 3 (Exp-Accelerating)", "exponential_accelerating")
    ]
    
    models = {}
    metrics_summary = []
    
    for label, case_code in cases:
        print(f"--> Training PFDC under {label}...")
        clf = DynamicPFDC(
            r_core_init=0.55,
            r_decay_init=1.1,
            decay_rate=5.0,
            alpha=1.0,
            gamma=1.0,
            lr_core_init=0.08,
            lr_decay_init=0.06,
            lr_case=case_code,
            accel_beta=0.18,
            max_epochs=120,
            random_state=42
        )
        
        clf.fit(X_train, y_train, eval_set=(X_test, y_test))
        models[label] = clf
        
        hist = clf.history_
        best_val_loss = min(hist["val_loss"])
        best_val_epoch = hist["val_loss"].index(best_val_loss) + 1
        final_test_acc = hist["val_acc"][-1] * 100.0
        final_train_acc = hist["train_acc"][-1] * 100.0
        sign_shifts_total = hist["sign_changes_core"][-1] + hist["sign_changes_decay"][-1]
        
        # Calculate learning speed: epochs to achieve 95% of peak accuracy
        peak_acc = max(hist["val_acc"])
        threshold_acc = 0.95 * peak_acc
        epochs_to_threshold = next((i + 1 for i, a in enumerate(hist["val_acc"]) if a >= threshold_acc), hist["epoch"][-1])
        
        metrics_summary.append({
            "PFDC Case": label,
            "LR Strategy": case_code,
            "Final Test Acc (%)": final_test_acc,
            "Final Train Acc (%)": final_train_acc,
            "Best Test Loss": best_val_loss,
            "Epochs to Converge (95% Peak)": epochs_to_threshold,
            "Total Sign Shifts": sign_shifts_total,
            "Final Core Radius": f"{clf.r_core_final_:.4f}",
            "Final Decay Radius": f"{clf.r_decay_final_:.4f}",
            "Final Core LR": f"{clf.lr_core_final_:.6f}",
            "Final Decay LR": f"{clf.lr_decay_final_:.6f}"
        })
        
    df_pfdc_summary = pd.DataFrame(metrics_summary)
    print("\nPFDC 3-Case Convergence & Learning Speed Results:")
    print(df_pfdc_summary.to_string(index=False))
    df_pfdc_summary.to_csv("figures/pfdc_cases_metrics.csv", index=False)
    
    # -------------------------------------------------------------
    # PLOT 1: PFDC Cases Learning Speed, Loss, Acc, Radii, & LR Curves
    # -------------------------------------------------------------
    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    colors = {"Case 1 (Fixed)": "#e74c3c", "Case 2 (Halved)": "#3498db", "Case 3 (Exp-Accelerating)": "#2ecc71"}
    styles = {"Case 1 (Fixed)": "--", "Case 2 (Halved)": "-.", "Case 3 (Exp-Accelerating)": "-"}
    
    for label, clf in models.items():
        hist = clf.history_
        ep = hist["epoch"]
        c = colors[label]
        ls = styles[label]
        
        # 1. Test Loss
        axes[0, 0].plot(ep, hist["val_loss"], label=label, color=c, linestyle=ls, linewidth=2.2)
        # 2. Test Accuracy
        axes[0, 1].plot(ep, np.array(hist["val_acc"]) * 100.0, label=label, color=c, linestyle=ls, linewidth=2.2)
        # 3. Learning Rate Core
        axes[0, 2].plot(ep, hist["lr_core"], label=label, color=c, linestyle=ls, linewidth=2.2)
        # 4. Learning Rate Decay
        axes[1, 0].plot(ep, hist["lr_decay"], label=label, color=c, linestyle=ls, linewidth=2.2)
        # 5. Core Radius Trajectory
        axes[1, 1].plot(ep, hist["r_core"], label=label, color=c, linestyle=ls, linewidth=2.2)
        # 6. Decay Radius Trajectory
        axes[1, 2].plot(ep, hist["r_decay"], label=label, color=c, linestyle=ls, linewidth=2.2)

    # Subplot styling
    axes[0, 0].set_title("Test Loss vs. Epoch", fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel("Epoch")
    axes[0, 0].set_ylabel("Binary Cross-Entropy Loss")
    axes[0, 0].legend(frameon=True)
    
    axes[0, 1].set_title("Test Accuracy vs. Epoch", fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel("Epoch")
    axes[0, 1].set_ylabel("Test Accuracy (%)")
    axes[0, 1].legend(frameon=True)
    
    axes[0, 2].set_title(r"Core Learning Rate $\eta^{\mathrm{core}}_t$ vs. Epoch", fontsize=12, fontweight='bold')
    axes[0, 2].set_xlabel("Epoch")
    axes[0, 2].set_ylabel(r"$\eta^{\mathrm{core}}_t$ (Step Size)")
    axes[0, 2].set_yscale('log')
    axes[0, 2].legend(frameon=True)
    
    axes[1, 0].set_title(r"Decay Learning Rate $\eta^{\mathrm{decay}}_t$ vs. Epoch", fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel("Epoch")
    axes[1, 0].set_ylabel(r"$\eta^{\mathrm{decay}}_t$ (Step Size)")
    axes[1, 0].set_yscale('log')
    axes[1, 0].legend(frameon=True)
    
    axes[1, 1].set_title(r"Core Radius $R^{\mathrm{core}}_t$ Trajectory", fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel("Epoch")
    axes[1, 1].set_ylabel(r"$R^{\mathrm{core}}$ (Signed)")
    axes[1, 1].axhline(0, color='black', linestyle=':', alpha=0.6, label='Boundary (0)')
    axes[1, 1].legend(frameon=True)
    
    axes[1, 2].set_title(r"Decay Radius $R^{\mathrm{decay}}_t$ Trajectory", fontsize=12, fontweight='bold')
    axes[1, 2].set_xlabel("Epoch")
    axes[1, 2].set_ylabel(r"$R^{\mathrm{decay}}$ (Width)")
    axes[1, 2].legend(frameon=True)
    
    plt.suptitle("PFDC Dynamic Learning-Rate Cases: Convergence, Speed & Trajectory Comparison", fontsize=15, fontweight='bold', y=0.98)
    plt.tight_layout()
    plot1_path = os.path.join(OUTPUT_DIR, "pfdc_cases_learning_speed_comparison.png")
    plt.savefig(plot1_path, dpi=300)
    plt.close()
    print(f"Saved Plot 1: {plot1_path}")

    # -------------------------------------------------------------
    # PLOT 2: 2D Decision Surfaces & Vector Fields for the 3 Cases
    # -------------------------------------------------------------
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
    x_min, x_max = X_test[:, 0].min() - 0.5, X_test[:, 0].max() + 0.5
    y_min, y_max = X_test[:, 1].min() - 0.5, X_test[:, 1].max() + 0.5
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100), np.linspace(y_min, y_max, 100))
    grid_points = np.c_[xx.ravel(), yy.ravel()]
    
    # Subsampled grid for vector field quiver
    xx_q, yy_q = np.meshgrid(np.linspace(x_min, x_max, 22), np.linspace(y_min, y_max, 22))
    grid_q = np.c_[xx_q.ravel(), yy_q.ravel()]

    for idx, (label, clf) in enumerate(models.items()):
        ax = axes[idx]
        pot_grid = clf.predict_potential(grid_points).reshape(xx.shape)
        
        # Potential contour
        cf = ax.contourf(xx, yy, pot_grid, levels=25, cmap="coolwarm", alpha=0.45)
        ax.contour(xx, yy, pot_grid, levels=[0], colors="black", linewidths=2.0)
        
        # Directional force vectors (quiver)
        forces = clf.compute_force_vectors(grid_q)
        fx = forces[:, 0].reshape(xx_q.shape)
        fy = forces[:, 1].reshape(yy_q.shape)
        # Normalize for visualization
        norm = np.sqrt(fx**2 + fy**2) + 1e-6
        ax.quiver(xx_q, yy_q, fx/norm, fy/norm, color='#2c3e50', alpha=0.55, scale=30, width=0.003)
        
        # Test scatter points
        scatter = ax.scatter(X_test[:, 0], X_test[:, 1], c=y_test, cmap="coolwarm", edgecolors="k", s=40, alpha=0.85)
        acc_val = clf.score(X_test, y_test) * 100.0
        ax.set_title(f"{label}\nTest Accuracy: {acc_val:.2f}%", fontsize=12, fontweight='bold')
        ax.set_xlabel("Feature $X_1$")
        ax.set_ylabel("Feature $X_2$")
        
    fig.colorbar(cf, ax=axes.ravel().tolist(), label="Net Potential Field $P(x)$", shrink=0.8)
    plt.suptitle("PFDC 2D Potential Landscapes & Directional Force Fields Across the 3 Cases", fontsize=14, fontweight='bold')
    plot2_path = os.path.join(OUTPUT_DIR, "pfdc_decision_boundaries_cases.png")
    plt.savefig(plot2_path, dpi=300)
    plt.close()
    print(f"Saved Plot 2: {plot2_path}")

    return models

def run_paradigms_benchmark(X_train, y_train, X_test, y_test, best_pfdc_model):
    """
    Benchmarks PFDC against recent and state-of-the-art models from:
    1. Supervised Learning: XGBoost / HistGradientBoosting, Deep Neural Network (MLP), RBF SVM, Random Forest
    2. Unsupervised / Self-Supervised Learning: GMM, Contrastive Representation Probe
    3. Reinforcement Learning: Actor-Critic Policy Gradient Bandit
    """
    print("\n" + "="*70)
    print("STEP 2: Benchmarking PFDC vs. Supervised vs. Unsupervised vs. RL Paradigms")
    print("="*70)
    
    benchmark_models = {}
    
    # Proposed Model
    benchmark_models["PFDC (Proposed)"] = best_pfdc_model
    
    # 1. Supervised Models
    if XGB_AVAILABLE:
        benchmark_models["XGBoost (Supervised SOTA)"] = xgb.XGBClassifier(
            n_estimators=100, max_depth=4, learning_rate=0.08, eval_metric='logloss', random_state=42
        )
    elif LGB_AVAILABLE:
        benchmark_models["LightGBM (Supervised SOTA)"] = lgb.LGBMClassifier(
            n_estimators=100, max_depth=4, learning_rate=0.08, random_state=42
        )
    else:
        benchmark_models["HistGradientBoosting (Supervised SOTA)"] = HistGradientBoostingClassifier(
            max_iter=100, max_depth=4, learning_rate=0.08, random_state=42
        )
        
    benchmark_models["Deep MLP (Supervised)"] = MLPClassifier(
        hidden_layer_sizes=(128, 64), activation='relu', max_iter=250, alpha=1e-4, random_state=42
    )
    benchmark_models["SVM (RBF Kernel)"] = SVC(kernel='rbf', C=1.5, probability=True, random_state=42)
    benchmark_models["Random Forest"] = RandomForestClassifier(n_estimators=120, max_depth=5, random_state=42)
    
    # 2. Unsupervised / Self-Supervised Models
    benchmark_models["Contrastive SSL (Self-Supervised)"] = SelfSupervisedContrastiveClassifier(
        embed_dim=16, epochs=60, lr=0.01, random_state=42
    )
    benchmark_models["GMM (Unsupervised Clustering)"] = UnsupervisedGMMClassifier(
        n_components=6, random_state=42
    )
    
    # 3. Reinforcement Learning Model
    benchmark_models["Actor-Critic RL (Reinforced)"] = ReinforcementLearningClassifier(
        hidden_dim=64, lr=0.015, epochs=80, random_state=42
    )

    results = []
    trained_models = {}
    
    for name, model in benchmark_models.items():
        print(f"Evaluating {name}...")
        res = evaluate_model(name, model, X_train, y_train, X_test, y_test)
        results.append(res)
        trained_models[name] = model

    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values(by="Accuracy (%)", ascending=False).reset_index(drop=True)
    
    print("\n" + "="*80)
    print("FINAL BENCHMARK COMPARISON TABLE ACROSS ALL PARADIGMS")
    print("="*80)
    print(df_results.to_string(index=False))
    df_results.to_csv("figures/paradigm_benchmark_results.csv", index=False)

    # -------------------------------------------------------------
    # PLOT 3: Decision Boundary Comparison Across Paradigms
    # -------------------------------------------------------------
    selected_for_plot = [
        "PFDC (Proposed)",
        list(benchmark_models.keys())[1], # XGBoost / HistGradientBoosting
        "Deep MLP (Supervised)",
        "SVM (RBF Kernel)",
        "Contrastive SSL (Self-Supervised)",
        "Actor-Critic RL (Reinforced)"
    ]
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    axes = axes.flatten()
    
    x_min, x_max = X_test[:, 0].min() - 0.5, X_test[:, 0].max() + 0.5
    y_min, y_max = X_test[:, 1].min() - 0.5, X_test[:, 1].max() + 0.5
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 120), np.linspace(y_min, y_max, 120))
    grid = np.c_[xx.ravel(), yy.ravel()]

    for idx, model_name in enumerate(selected_for_plot):
        ax = axes[idx]
        mod = trained_models[model_name]
        
        try:
            # Try probability contour
            probs = mod.predict_proba(grid)[:, 1].reshape(xx.shape)
            cf = ax.contourf(xx, yy, probs, levels=25, cmap="coolwarm", alpha=0.45)
            ax.contour(xx, yy, probs, levels=[0.5], colors="black", linewidths=2.0)
        except Exception:
            # Fallback to discrete prediction
            preds = mod.predict(grid).reshape(xx.shape)
            cf = ax.contourf(xx, yy, preds, levels=[-0.5, 0.5, 1.5], cmap="coolwarm", alpha=0.45)
            ax.contour(xx, yy, preds, levels=[0.5], colors="black", linewidths=2.0)

        # Scatter test data points
        ax.scatter(X_test[:, 0], X_test[:, 1], c=y_test, cmap="coolwarm", edgecolors="k", s=35, alpha=0.85)
        
        acc = df_results.loc[df_results["Model"] == model_name, "Accuracy (%)"].values[0]
        f1 = df_results.loc[df_results["Model"] == model_name, "F1-Score"].values[0]
        ax.set_title(f"{model_name}\nAcc: {acc:.2f}% | F1: {f1:.4f}", fontsize=11, fontweight='bold')
        ax.set_xlabel("Independent Variable $X_1$")
        ax.set_ylabel("Independent Variable $X_2$")

    fig.colorbar(cf, ax=axes.ravel().tolist(), label="Class 1 Probability / Output", shrink=0.8)
    plt.suptitle("2D Decision Boundary Comparison: PFDC vs. Modern Supervised vs. Unsupervised vs. RL", fontsize=15, fontweight='bold')
    plot3_path = os.path.join(OUTPUT_DIR, "paradigm_comparison_decision_boundaries.png")
    plt.savefig(plot3_path, dpi=300)
    plt.close()
    print(f"Saved Plot 3: {plot3_path}")

    # -------------------------------------------------------------
    # PLOT 4: Performance Bar Chart Across Paradigms
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Accuracy and F1
    bar_colors = ["#2ecc71" if "PFDC" in m else "#3498db" if "Supervised" in m or "SVM" in m or "Forest" in m or "XGB" in m or "MLP" in m else "#9b59b6" if "SSL" in m or "GMM" in m else "#e67e22" for m in df_results["Model"]]
    
    sns.barplot(data=df_results, x="Accuracy (%)", y="Model", palette=bar_colors, ax=ax1)
    ax1.set_title("Test Accuracy Comparison Across Paradigms", fontsize=13, fontweight='bold')
    ax1.set_xlim(50, 100)
    for p in ax1.patches:
        width = p.get_width()
        ax1.annotate(f"{width:.1f}%", (width - 4.5, p.get_y() + p.get_height() / 2.),
                     ha='center', va='center', color='white', fontweight='bold', fontsize=10)
                     
    # Fit Time
    sns.barplot(data=df_results, x="Fit Time (s)", y="Model", palette=bar_colors, ax=ax2)
    ax2.set_title("Training Time (Seconds)", fontsize=13, fontweight='bold')
    ax2.set_xscale('log')
    for p in ax2.patches:
        width = p.get_width()
        ax2.annotate(f"{width:.3f}s", (width * 1.15, p.get_y() + p.get_height() / 2.),
                     ha='left', va='center', color='black', fontsize=9)
                     
    plt.suptitle("Empirical Benchmark: Accuracy & Computational Efficiency by Paradigm", fontsize=15, fontweight='bold')
    plt.tight_layout()
    plot4_path = os.path.join(OUTPUT_DIR, "paradigm_benchmark_metrics.png")
    plt.savefig(plot4_path, dpi=300)
    plt.close()
    print(f"Saved Plot 4: {plot4_path}")

    return df_results

if __name__ == "__main__":
    X_train, X_test, y_train, y_test = generate_2d_benchmark_dataset()
    pfdc_models = run_pfdc_three_cases_comparison(X_train, y_train, X_test, y_test)
    
    # Pick the best PFDC model (e.g. Case 3 or Case 2)
    best_pfdc = pfdc_models["Case 3 (Exp-Accelerating)"]
    df_final = run_paradigms_benchmark(X_train, y_train, X_test, y_test, best_pfdc)
    print("\nBenchmark completed successfully! All figures saved in figures/.")
