import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, log_loss
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier

import xgboost as xgb
import lightgbm as lgb

OUTPUT_DIR = "figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

class HighDimensionalPFDC:
    """
    High-Dimensional Potential Field Decay Classifier (PFDC).
    Incorporates high-dimensional distance scaling (concentration of measure compensation).
    Supports all dynamic learning-rate cases and extended parameters (alpha, gamma).
    """
    def __init__(
        self,
        decay_rate=5.0,
        alpha=1.0,
        gamma=1.0,
        rbf_beta=None,
        lr_case="exponential_accelerating", # "fixed", "halved", "exponential_accelerating"
        lr_core_init=0.05,
        lr_decay_init=0.03,
        accel_beta=0.15,
        max_epochs=80,
        balance_charges=True,
        random_state=42
    ):
        self.decay_rate = decay_rate
        self.alpha = alpha
        self.gamma = gamma
        self.rbf_beta = rbf_beta
        self.lr_case = lr_case
        self.lr_core_init = lr_core_init
        self.lr_decay_init = lr_decay_init
        self.accel_beta = accel_beta
        self.max_epochs = max_epochs
        self.balance_charges = balance_charges
        self.random_state = random_state

    def _sigmoid(self, z):
        return 1.0 / (1.0 + np.exp(-np.clip(z, -20.0, 20.0)))

    def _compute_influence(self, dists, r_core_mag, r_decay):
        influence = np.zeros_like(dists, dtype=float)
        mask_core = (dists <= r_core_mag)
        influence[mask_core] = 1.0
        
        outer_limit = r_core_mag + r_decay
        mask_decay = (dists > r_core_mag) & (dists <= outer_limit)
        
        if np.any(mask_decay):
            u = (dists[mask_decay] - r_core_mag) / np.maximum(r_decay, 1e-6)
            influence[mask_decay] = np.exp(-self.decay_rate * (u ** self.alpha))
            
        return influence, mask_decay

    def fit(self, X, y, eval_set=None):
        self.scaler_ = StandardScaler()
        self.X_train_ = self.scaler_.fit_transform(X)
        self.y_train_ = np.asarray(y)
        self.classes_ = np.unique(self.y_train_)
        self.pos_class_ = self.classes_[1]
        
        n_samples = len(self.y_train_)
        pos_mask = (self.y_train_ == self.pos_class_)
        neg_mask = ~pos_mask
        
        if self.balance_charges:
            n_pos = np.sum(pos_mask)
            n_neg = np.sum(neg_mask)
            q_pos = (n_samples / (2.0 * n_pos)) if n_pos > 0 else 1.0
            q_neg = -(n_samples / (2.0 * n_neg)) if n_neg > 0 else -1.0
            self.charges_ = np.where(pos_mask, q_pos, q_neg)
        else:
            self.charges_ = np.where(pos_mask, 1.0, -1.0)

        # Compute pairwise distance matrix among training points using memory-efficient BLAS GEMM (24MB instead of 24GB)
        train_dists = euclidean_distances(self.X_train_, self.X_train_)
        
        # High-D Distance Statistics
        non_diag = train_dists[train_dists > 0]
        mean_d = float(np.mean(non_diag))
        std_d = float(np.std(non_diag))
        
        # Initialize Radii anchored to empirical distance concentration
        # Core covers the tighter intra-class neighborhood: mean_d - 1.2 * std_d
        # Decay covers the boundary transition shell: 3.0 * std_d
        r_core = max(0.5, mean_d - 1.2 * std_d)
        r_decay = max(1.0, 3.0 * std_d)
        
        if self.rbf_beta is None:
            self.rbf_beta = 1.0 / (2.0 * (mean_d ** 2))

        # Eval set distances
        if eval_set is not None:
            X_val, y_val = eval_set
            X_val_scaled = self.scaler_.transform(X_val)
            val_dists = euclidean_distances(X_val_scaled, self.X_train_)
            y_val_bin = (y_val == self.pos_class_).astype(float)
        else:
            val_dists, y_val_bin = None, None

        y_train_bin = (self.y_train_ == self.pos_class_).astype(float)

        lr_core = float(self.lr_core_init)
        lr_decay = float(self.lr_decay_init)
        
        self.history_ = {
            "epoch": [], "loss": [], "val_loss": [], "train_acc": [], "val_acc": [],
            "r_core": [], "r_decay": [], "lr_core": [], "lr_decay": [],
            "sign_changes_core": [], "sign_changes_decay": []
        }
        
        sign_changes_core = 0
        sign_changes_decay = 0
        prev_grad_core_sign = 0
        prev_grad_decay_sign = 0

        for epoch in range(1, self.max_epochs + 1):
            r_core_mag = np.maximum(np.abs(r_core), 0.1)
            core_sign = np.sign(r_core) if r_core != 0 else 1.0
            
            inf, mask_decay = self._compute_influence(train_dists, r_core_mag, r_decay)
            p_pfdc = np.sum(inf * self.charges_[np.newaxis, :], axis=1)
            
            if self.gamma < 1.0:
                p_rbf = np.sum(np.exp(-self.rbf_beta * (train_dists ** 2)) * self.charges_[np.newaxis, :], axis=1)
                pot = self.gamma * p_pfdc + (1.0 - self.gamma) * p_rbf
            else:
                pot = p_pfdc
                
            probs = self._sigmoid(pot)
            preds = (pot >= 0).astype(int)
            train_acc = np.mean(preds == y_train_bin)
            
            eps = 1e-12
            loss = -np.mean(y_train_bin * np.log(probs + eps) + (1.0 - y_train_bin) * np.log(1.0 - probs + eps))
            
            if val_dists is not None:
                val_inf, _ = self._compute_influence(val_dists, r_core_mag, r_decay)
                val_pfdc = np.sum(val_inf * self.charges_[np.newaxis, :], axis=1)
                if self.gamma < 1.0:
                    val_rbf = np.sum(np.exp(-self.rbf_beta * (val_dists ** 2)) * self.charges_[np.newaxis, :], axis=1)
                    val_pot = self.gamma * val_pfdc + (1.0 - self.gamma) * val_rbf
                else:
                    val_pot = val_pfdc
                val_probs = self._sigmoid(val_pot)
                val_preds = (val_pot >= 0).astype(int)
                val_acc = np.mean(val_preds == y_val_bin)
                val_loss = -np.mean(y_val_bin * np.log(val_probs + eps) + (1.0 - y_val_bin) * np.log(1.0 - val_probs + eps))
            else:
                val_loss, val_acc = None, None

            # Gradients
            delta = probs - y_train_bin
            dI_dcore = np.zeros_like(train_dists)
            dI_ddecay = np.zeros_like(train_dists)
            
            if np.any(mask_decay):
                u_decay = (train_dists[mask_decay] - r_core_mag) / np.maximum(r_decay, 1e-6)
                u_clamped = np.maximum(u_decay, 1e-6)
                decay_exp = np.exp(-self.decay_rate * (u_clamped ** self.alpha))
                factor = (self.decay_rate * self.alpha / np.maximum(r_decay, 1e-6)) * decay_exp
                dI_dcore[mask_decay] = factor * (u_clamped ** (self.alpha - 1.0))
                dI_ddecay[mask_decay] = factor * (u_clamped ** self.alpha)

            dP_dcore = np.sum(dI_dcore * self.charges_[np.newaxis, :], axis=1)
            dP_ddecay = np.sum(dI_ddecay * self.charges_[np.newaxis, :], axis=1)
            
            if self.gamma < 1.0:
                dP_dcore *= self.gamma
                dP_ddecay *= self.gamma

            grad_core = core_sign * np.clip(np.mean(delta * dP_dcore), -5.0, 5.0)
            grad_decay = np.clip(np.mean(delta * dP_ddecay), -5.0, 5.0)

            # Boundary crossing / sign detection
            curr_grad_core_sign = np.sign(grad_core)
            curr_grad_decay_sign = np.sign(grad_decay)
            
            sign_shifted_core = (epoch > 1 and prev_grad_core_sign != 0 and curr_grad_core_sign != prev_grad_core_sign)
            sign_shifted_decay = (epoch > 1 and prev_grad_decay_sign != 0 and curr_grad_decay_sign != prev_grad_decay_sign)
            
            if sign_shifted_core: sign_changes_core += 1
            if sign_shifted_decay: sign_changes_decay += 1

            # Dynamic learning rate regimes
            if self.lr_case == "fixed":
                lr_core = self.lr_core_init
                lr_decay = self.lr_decay_init
            elif self.lr_case == "halved":
                if sign_shifted_core: lr_core *= 0.5
                if sign_shifted_decay: lr_decay *= 0.5
            elif self.lr_case == "exponential_accelerating":
                lr_core = self.lr_core_init * np.exp(-self.accel_beta * (sign_changes_core ** 2))
                lr_decay = self.lr_decay_init * np.exp(-self.accel_beta * (sign_changes_decay ** 2))

            # Record
            self.history_["epoch"].append(epoch)
            self.history_["loss"].append(loss)
            self.history_["val_loss"].append(val_loss)
            self.history_["train_acc"].append(train_acc)
            self.history_["val_acc"].append(val_acc)
            self.history_["r_core"].append(r_core)
            self.history_["r_decay"].append(r_decay)
            self.history_["lr_core"].append(lr_core)
            self.history_["lr_decay"].append(lr_decay)
            self.history_["sign_changes_core"].append(sign_changes_core)
            self.history_["sign_changes_decay"].append(sign_changes_decay)

            # Update radii
            r_core = np.clip(r_core - lr_core * grad_core, 0.1, mean_d + 10.0)
            r_decay = np.clip(r_decay - lr_decay * grad_decay, 0.1, 30.0)

            prev_grad_core_sign = curr_grad_core_sign
            prev_grad_decay_sign = curr_grad_decay_sign

        self.r_core_final_ = r_core
        self.r_decay_final_ = r_decay
        return self

    def predict_potential(self, X):
        X_scaled = self.scaler_.transform(X)
        dists = euclidean_distances(X_scaled, self.X_train_)
        inf, _ = self._compute_influence(dists, self.r_core_final_, self.r_decay_final_)
        p_pfdc = np.sum(inf * self.charges_[np.newaxis, :], axis=1)
        if self.gamma < 1.0:
            p_rbf = np.sum(np.exp(-self.rbf_beta * (dists ** 2)) * self.charges_[np.newaxis, :], axis=1)
            pot = self.gamma * p_pfdc + (1.0 - self.gamma) * p_rbf
        else:
            pot = p_pfdc
        return pot

    def predict_proba(self, X):
        pot = self.predict_potential(X)
        p1 = self._sigmoid(pot)
        return np.column_stack([1.0 - p1, p1])

    def predict(self, X):
        pot = self.predict_potential(X)
        return np.where(pot >= 0, self.classes_[1], self.classes_[0])


def run_1000d_experiment():
    print("="*80)
    print("HIGH-DIMENSIONAL BENCHMARK & ABLATION STUDY: 1,000 INDEPENDENT VARIABLES")
    print("="*80)

    # 1. Load Data
    train_data = np.load("data/dataset_1000d_train.npz")
    test_data = np.load("data/dataset_1000d_test.npz")
    X_train, y_train = train_data['X'], train_data['y']
    X_test, y_test = test_data['X'], test_data['y']
    print(f"Loaded: Train = {X_train.shape}, Test = {X_test.shape} (1000 Features)")

    # 2. Part A: PFDC Ablation Study (Configurations B0, B1, B2, E1, E2, E3)
    ablation_configs = [
        ("B0 (Case 1: Fixed LR)", {"lr_case": "fixed", "alpha": 1.0, "gamma": 1.0}),
        ("B1 (Case 2: Halved LR)", {"lr_case": "halved", "alpha": 1.0, "gamma": 1.0}),
        ("B2 (Case 3: Exp-Accel LR)", {"lr_case": "exponential_accelerating", "alpha": 1.0, "gamma": 1.0}),
        ("E1 (+ Decay Shape alpha=1.5)", {"lr_case": "exponential_accelerating", "alpha": 1.5, "gamma": 1.0}),
        ("E2 (+ Kernel Mixing gamma=0.85)", {"lr_case": "exponential_accelerating", "alpha": 1.0, "gamma": 0.85}),
        ("E3 (Full Extended: Case3+alpha+gamma)", {"lr_case": "exponential_accelerating", "alpha": 1.5, "gamma": 0.85})
    ]

    ablation_results = []
    pfdc_models = {}

    print("\n--- Training PFDC Ablation Configurations on 1,000 Dimensions ---")
    for name, params in ablation_configs:
        t0 = time.time()
        clf = HighDimensionalPFDC(max_epochs=80, lr_core_init=0.08, lr_decay_init=0.05, **params)
        clf.fit(X_train, y_train, eval_set=(X_test, y_test))
        fit_time = time.time() - t0
        
        t0 = time.time()
        y_pred = clf.predict(X_test)
        infer_time = (time.time() - t0) * 1000.0
        
        y_prob = clf.predict_proba(X_test)[:, 1]
        acc = accuracy_score(y_test, y_pred) * 100.0
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)
        bce = log_loss(y_test, y_prob)
        
        total_shifts = clf.history_["sign_changes_core"][-1] + clf.history_["sign_changes_decay"][-1]
        
        ablation_results.append({
            "Configuration": name,
            "Accuracy (%)": acc,
            "F1-Score": f1,
            "ROC-AUC": auc,
            "BCE Loss": bce,
            "Total Sign Shifts": total_shifts,
            "Final Core Radius": f"{clf.r_core_final_:.2f}",
            "Final Decay Radius": f"{clf.r_decay_final_:.2f}",
            "Fit Time (s)": fit_time,
            "Inference Time (ms)": infer_time
        })
        pfdc_models[name] = clf
        print(f"--> {name}: Test Acc = {acc:.2f}%, F1 = {f1:.4f}, Loss = {bce:.4f}, Shifts = {total_shifts}, Time = {fit_time:.2f}s")

    df_ablation = pd.DataFrame(ablation_results)
    df_ablation.to_csv("figures/highd_ablation_results.csv", index=False)

    # 3. Part B: Full Benchmark against Supervised Competitors on 1,000 Dimensions
    print("\n--- Benchmarking PFDC against Modern Supervised Competitors on 1,000 Dimensions ---")
    benchmark_models = {
        "PFDC E3 (Proposed Full Extended)": pfdc_models["E3 (Full Extended: Case3+alpha+gamma)"],
        "PFDC B2 (Proposed Case 3)": pfdc_models["B2 (Case 3: Exp-Accel LR)"],
        "XGBoost (v3.2.0)": xgb.XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.08, random_state=42),
        "LightGBM (v4.7.0)": lgb.LGBMClassifier(n_estimators=100, max_depth=4, learning_rate=0.08, random_state=42, verbose=-1),
        "Deep MLP (PyTorch/Sklearn)": MLPClassifier(hidden_layer_sizes=(128, 64), activation='relu', max_iter=150, random_state=42),
        "Random Forest (100 Trees)": RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42),
        "SVM (RBF Kernel)": SVC(kernel='rbf', probability=True, random_state=42),
        "Logistic Regression (L2)": LogisticRegression(max_iter=300, random_state=42)
    }

    bench_results = []
    for name, model in benchmark_models.items():
        if "PFDC" in name:
            # Already evaluated
            clf = model
            y_pred = clf.predict(X_test)
            y_prob = clf.predict_proba(X_test)[:, 1]
            fit_t = df_ablation.loc[df_ablation["Configuration"].str.contains("E3" if "E3" in name else "B2"), "Fit Time (s)"].values[0]
            infer_t = df_ablation.loc[df_ablation["Configuration"].str.contains("E3" if "E3" in name else "B2"), "Inference Time (ms)"].values[0]
        else:
            t0 = time.time()
            model.fit(X_train, y_train)
            fit_t = time.time() - t0
            
            t0 = time.time()
            y_pred = model.predict(X_test)
            infer_t = (time.time() - t0) * 1000.0
            y_prob = model.predict_proba(X_test)[:, 1]
            
        acc = accuracy_score(y_test, y_pred) * 100.0
        f1 = f1_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        auc = roc_auc_score(y_test, y_prob)
        bce = log_loss(y_test, y_prob)
        
        bench_results.append({
            "Model": name,
            "Accuracy (%)": acc,
            "F1-Score": f1,
            "Precision": prec,
            "Recall": rec,
            "ROC-AUC": auc,
            "Test BCE Loss": bce,
            "Fit Time (s)": fit_t,
            "Inference Time (ms)": infer_t
        })
        print(f"--> {name}: Test Acc = {acc:.2f}%, F1 = {f1:.4f}, ROC-AUC = {auc:.4f}, Fit Time = {fit_t:.2f}s")

    df_bench = pd.DataFrame(bench_results).sort_values(by="Accuracy (%)", ascending=False).reset_index(drop=True)
    df_bench.to_csv("figures/highd_benchmark_results.csv", index=False)
    print("\n" + "="*80)
    print("FINAL 1,000-DIMENSIONAL BENCHMARK RESULTS")
    print("="*80)
    print(df_bench.to_string(index=False))

    # 4. Generate Visualizations
    # Plot 1: PFDC Cases Convergence on 1000D
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.5))
    cases_to_plot = ["B0 (Case 1: Fixed LR)", "B1 (Case 2: Halved LR)", "B2 (Case 3: Exp-Accel LR)"]
    c_map = {"B0 (Case 1: Fixed LR)": "#e74c3c", "B1 (Case 2: Halved LR)": "#3498db", "B2 (Case 3: Exp-Accel LR)": "#2ecc71"}
    
    for c_name in cases_to_plot:
        h = pfdc_models[c_name].history_
        ax1.plot(h["epoch"], h["val_loss"], label=c_name, color=c_map[c_name], linewidth=2.2)
        ax2.plot(h["epoch"], np.array(h["val_acc"]) * 100.0, label=c_name, color=c_map[c_name], linewidth=2.2)
        
    ax1.set_title("Test Loss vs. Epoch (1,000 Independent Variables)", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Binary Cross-Entropy Loss")
    ax1.legend()
    
    ax2.set_title("Test Accuracy vs. Epoch (1,000 Independent Variables)", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Test Accuracy (%)")
    ax2.legend()
    plt.suptitle("PFDC Dynamic Learning-Rate Cases on 1,000-Dimensional Data", fontsize=14, fontweight='bold')
    plt.tight_layout()
    p1 = os.path.join(OUTPUT_DIR, "highd_cases_convergence.png")
    plt.savefig(p1, dpi=300)
    plt.close()
    print(f"Saved Plot 1: {p1}")

    # Plot 2: Ablation Bar Chart
    fig, ax = plt.subplots(figsize=(12, 5.5))
    sns.barplot(data=df_ablation, x="Accuracy (%)", y="Configuration", hue="Configuration", palette="viridis", legend=False, ax=ax)
    ax.set_title("PFDC Component Ablation on 1,000 Features (Accuracy %)", fontsize=13, fontweight='bold')
    ax.set_xlim(80, 100)
    for p in ax.patches:
        w = p.get_width()
        ax.annotate(f"{w:.2f}%", (w - 1.8, p.get_y() + p.get_height()/2.), ha='center', va='center', color='white', fontweight='bold')
    plt.tight_layout()
    p2 = os.path.join(OUTPUT_DIR, "highd_ablation_comparison.png")
    plt.savefig(p2, dpi=300)
    plt.close()
    print(f"Saved Plot 2: {p2}")

    # Plot 3: Paradigm Comparison Bar Chart on 1,000 Features
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    bar_colors = ["#2ecc71" if "PFDC" in m else "#3498db" for m in df_bench["Model"]]
    sns.barplot(data=df_bench, x="Accuracy (%)", y="Model", hue="Model", palette=bar_colors, legend=False, ax=ax1)
    ax1.set_title("Test Accuracy Comparison (1,000 Features)", fontsize=13, fontweight='bold')
    ax1.set_xlim(80, 100)
    for p in ax1.patches:
        w = p.get_width()
        ax1.annotate(f"{w:.2f}%", (w - 1.8, p.get_y() + p.get_height()/2.), ha='center', va='center', color='white', fontweight='bold')
        
    sns.barplot(data=df_bench, x="Fit Time (s)", y="Model", hue="Model", palette=bar_colors, legend=False, ax=ax2)
    ax2.set_title("Training Time (Seconds)", fontsize=13, fontweight='bold')
    ax2.set_xscale('log')
    for p in ax2.patches:
        w = p.get_width()
        ax2.annotate(f"{w:.2f}s", (w * 1.15, p.get_y() + p.get_height()/2.), ha='left', va='center', fontsize=9)
    plt.suptitle("1,000 Independent Variables Benchmark: Accuracy & Training Efficiency", fontsize=14, fontweight='bold')
    plt.tight_layout()
    p3 = os.path.join(OUTPUT_DIR, "highd_paradigm_benchmark_metrics.png")
    plt.savefig(p3, dpi=300)
    plt.close()
    print(f"Saved Plot 3: {p3}")

    # Plot 4: 2D PCA Projection of 1,000-D Potential Field
    print("Generating PCA 2D Potential Landscape for the 1,000D model...")
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_test)
    
    fig, ax = plt.subplots(figsize=(9, 7))
    potentials = pfdc_models["E3 (Full Extended: Case3+alpha+gamma)"].predict_potential(X_test)
    scatter = ax.scatter(X_pca[:, 0], X_pca[:, 1], c=potentials, cmap='coolwarm', edgecolors='k', s=45, alpha=0.85)
    ax.axhline(0, color='gray', linestyle=':', alpha=0.5)
    ax.axvline(0, color='gray', linestyle=':', alpha=0.5)
    cbar = fig.colorbar(scatter, ax=ax, label="Net Scalar Potential P(x)")
    ax.set_title("1,000D PFDC Model: 2D PCA Manifold Projection & Scalar Potential", fontsize=12, fontweight='bold')
    ax.set_xlabel(f"Principal Component 1 ({pca.explained_variance_ratio_[0]*100:.1f}% Variance)")
    ax.set_ylabel(f"Principal Component 2 ({pca.explained_variance_ratio_[1]*100:.1f}% Variance)")
    plt.tight_layout()
    p4 = os.path.join(OUTPUT_DIR, "highd_pca_projection_field.png")
    plt.savefig(p4, dpi=300)
    plt.close()
    print(f"Saved Plot 4: {p4}")

    print("\nHigh-Dimensional Benchmark Completed Successfully!")

if __name__ == "__main__":
    run_1000d_experiment()
