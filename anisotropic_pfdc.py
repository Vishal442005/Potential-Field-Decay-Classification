import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, log_loss
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
import xgboost as xgb
import lightgbm as lgb

OUTPUT_DIR = "figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class AnisotropicPFDC:
    """
    Anisotropic (Feature-Weighted) Potential Field Decay Classifier.
    
    Uses the weighted metric:
        d_w(x, x_i) = sqrt( sum_{j=1}^D w_j * (x_j - x_{i,j})^2 )
    
    Dynamically learns:
    1. Core radius R_core
    2. Decay radius R_decay
    3. Feature importance weights w_j (j = 1...D)
    """
    def __init__(
        self,
        decay_rate=5.0,
        alpha=1.0,
        gamma=0.90, # 90% PFDC + 10% global RBF for high-D stabilization
        lr_radii=0.06,
        lr_w=0.04,
        w_reg=1e-4, # L1 penalty to drive noise feature weights to zero
        accel_beta=0.15,
        max_epochs=90,
        random_state=42
    ):
        self.decay_rate = decay_rate
        self.alpha = alpha
        self.gamma = gamma
        self.lr_radii = lr_radii
        self.lr_w = lr_w
        self.w_reg = w_reg
        self.accel_beta = accel_beta
        self.max_epochs = max_epochs
        self.random_state = random_state

    def _sigmoid(self, z):
        return 1.0 / (1.0 + np.exp(-np.clip(z, -20.0, 20.0)))

    def _compute_weighted_dists(self, X1, X2, w):
        """
        Computes weighted Euclidean distance d_w(X1, X2) = sqrt( (X1 - X2)^2 @ w )
        using BLAS GEMM: ||X1_w||^2 + ||X2_w||^2 - 2 X1_w @ X2_w.T
        """
        w_sqrt = np.sqrt(np.maximum(w, 1e-8))
        X1_w = X1 * w_sqrt
        X2_w = X2 * w_sqrt
        dists = euclidean_distances(X1_w, X2_w)
        return np.maximum(dists, 1e-8)

    def _compute_influence(self, dists, r_core, r_decay):
        influence = np.zeros_like(dists, dtype=float)
        mask_core = (dists <= r_core)
        influence[mask_core] = 1.0
        
        outer_limit = r_core + r_decay
        mask_decay = (dists > r_core) & (dists <= outer_limit)
        
        if np.any(mask_decay):
            u = (dists[mask_decay] - r_core) / np.maximum(r_decay, 1e-6)
            influence[mask_decay] = np.exp(-self.decay_rate * (u ** self.alpha))
            
        return influence, mask_decay

    def fit(self, X, y, eval_set=None, learn_weights=True):
        self.learn_weights = learn_weights
        self.scaler_ = StandardScaler()
        self.X_train_ = self.scaler_.fit_transform(X)
        self.y_train_ = np.asarray(y)
        self.classes_ = np.unique(self.y_train_)
        self.pos_class_ = self.classes_[1]
        
        n_samples, n_features = self.X_train_.shape
        pos_mask = (self.y_train_ == self.pos_class_)
        neg_mask = ~pos_mask
        
        n_pos = np.sum(pos_mask)
        n_neg = np.sum(neg_mask)
        q_pos = (n_samples / (2.0 * n_pos)) if n_pos > 0 else 1.0
        q_neg = -(n_samples / (2.0 * n_neg)) if n_neg > 0 else -1.0
        self.charges_ = np.where(pos_mask, q_pos, q_neg)

        # Initialize weights w: all 1.0 (mean weight = 1.0)
        w = np.ones(n_features, dtype=float)
        
        # Initial distances
        train_dists = self._compute_weighted_dists(self.X_train_, self.X_train_, w)
        non_diag = train_dists[train_dists > 0]
        mean_d = float(np.mean(non_diag))
        std_d = float(np.std(non_diag))
        
        r_core = max(0.5, mean_d - 1.2 * std_d)
        r_decay = max(1.0, 3.0 * std_d)
        rbf_beta = 1.0 / (2.0 * (mean_d ** 2))

        if eval_set is not None:
            X_val, y_val = eval_set
            X_val_scaled = self.scaler_.transform(X_val)
            y_val_bin = (y_val == self.pos_class_).astype(float)
        else:
            X_val_scaled, y_val_bin = None, None

        y_train_bin = (self.y_train_ == self.pos_class_).astype(float)
        
        lr_radii = float(self.lr_radii)
        lr_w = float(self.lr_w)
        
        self.history_ = {
            "epoch": [], "loss": [], "val_loss": [], "train_acc": [], "val_acc": [],
            "r_core": [], "r_decay": [], "w_entropy": [], "informative_w_mean": [], "noise_w_mean": []
        }
        
        sign_changes_radii = 0
        prev_grad_core_sign = 0

        for epoch in range(1, self.max_epochs + 1):
            train_dists = self._compute_weighted_dists(self.X_train_, self.X_train_, w)
            r_core_mag = max(abs(r_core), 0.1)
            
            inf, mask_decay = self._compute_influence(train_dists, r_core_mag, r_decay)
            p_pfdc = np.sum(inf * self.charges_[np.newaxis, :], axis=1)
            
            # Kernel mixing with RBF for global smoothing
            if self.gamma < 1.0:
                p_rbf = np.sum(np.exp(-rbf_beta * (train_dists ** 2)) * self.charges_[np.newaxis, :], axis=1)
                pot = self.gamma * p_pfdc + (1.0 - self.gamma) * p_rbf
            else:
                pot = p_pfdc
                
            probs = self._sigmoid(pot)
            preds = (pot >= 0).astype(int)
            train_acc = np.mean(preds == y_train_bin)
            
            eps = 1e-12
            loss = -np.mean(y_train_bin * np.log(probs + eps) + (1.0 - y_train_bin) * np.log(1.0 - probs + eps))
            
            # Validation
            if X_val_scaled is not None:
                val_dists = self._compute_weighted_dists(X_val_scaled, self.X_train_, w)
                val_inf, _ = self._compute_influence(val_dists, r_core_mag, r_decay)
                val_pfdc = np.sum(val_inf * self.charges_[np.newaxis, :], axis=1)
                if self.gamma < 1.0:
                    val_rbf = np.sum(np.exp(-rbf_beta * (val_dists ** 2)) * self.charges_[np.newaxis, :], axis=1)
                    val_pot = self.gamma * val_pfdc + (1.0 - self.gamma) * val_rbf
                else:
                    val_pot = val_pfdc
                val_probs = self._sigmoid(val_pot)
                val_preds = (val_pot >= 0).astype(int)
                val_acc = np.mean(val_preds == y_val_bin)
                val_loss = -np.mean(y_val_bin * np.log(val_probs + eps) + (1.0 - y_val_bin) * np.log(1.0 - val_probs + eps))
            else:
                val_loss, val_acc = None, None

            # 1. Gradients w.r.t Radii
            delta = probs - y_train_bin # (N,)
            dI_dcore = np.zeros_like(train_dists)
            dI_ddecay = np.zeros_like(train_dists)
            dI_ddist = np.zeros_like(train_dists)
            
            if np.any(mask_decay):
                u_decay = (train_dists[mask_decay] - r_core_mag) / max(r_decay, 1e-6)
                u_clamped = np.maximum(u_decay, 1e-6)
                decay_exp = np.exp(-self.decay_rate * (u_clamped ** self.alpha))
                factor = (self.decay_rate * self.alpha / max(r_decay, 1e-6)) * decay_exp
                
                dI_dcore[mask_decay] = factor * (u_clamped ** (self.alpha - 1.0))
                dI_ddecay[mask_decay] = factor * (u_clamped ** self.alpha)
                # dI / dd = -factor * u^(alpha-1)
                dI_ddist[mask_decay] = -factor * (u_clamped ** (self.alpha - 1.0))

            dP_dcore = np.sum(dI_dcore * self.charges_[np.newaxis, :], axis=1)
            dP_ddecay = np.sum(dI_ddecay * self.charges_[np.newaxis, :], axis=1)
            
            if self.gamma < 1.0:
                dP_dcore *= self.gamma
                dP_ddecay *= self.gamma

            grad_core = np.clip(np.mean(delta * dP_dcore), -5.0, 5.0)
            grad_decay = np.clip(np.mean(delta * dP_ddecay), -5.0, 5.0)

            # Detect sign shifts for radii
            curr_grad_core_sign = np.sign(grad_core)
            if epoch > 1 and prev_grad_core_sign != 0 and curr_grad_core_sign != prev_grad_core_sign:
                sign_changes_radii += 1
                lr_radii = self.lr_radii * np.exp(-self.accel_beta * (sign_changes_radii ** 2))

            # 2. Gradients w.r.t Feature Weights w_j
            if self.learn_weights:
                # Chain rule: dL / dw_j = (1/N) * sum_m delta_m * sum_i q_i * (dI_mi / dd_mi) * (dd_mi / dw_j)
                # dd_mi / dw_j = (x_mj - x_ij)^2 / (2 * d_mi)
                # Let Matrix M_{m,i} = delta_m * q_i * (dI_mi / dd_mi) / (2 * d_mi)
                safe_dists = np.maximum(train_dists, 1e-6)
                M_mat = (delta[:, np.newaxis] * self.charges_[np.newaxis, :]) * (dI_ddist / (2.0 * safe_dists))
                if self.gamma < 1.0:
                    M_mat *= self.gamma
                    
                # Exact vectorized gradient across all 1000 features via BLAS:
                # sum_{m,i} M_{mi} (x_mj - x_ij)^2 = sum_m S_m x_mj^2 - 2 sum_m x_mj (M X)_mj + sum_i T_i x_ij^2
                S_vec = np.sum(M_mat, axis=1) # (N,)
                T_vec = np.sum(M_mat, axis=0) # (N,)
                MX = np.matmul(M_mat, self.X_train_) # (N, D)
                
                term1 = np.sum(S_vec[:, np.newaxis] * (self.X_train_ ** 2), axis=0)
                term2 = -2.0 * np.sum(self.X_train_ * MX, axis=0)
                term3 = np.sum(T_vec[:, np.newaxis] * (self.X_train_ ** 2), axis=0)
                
                grad_w = (term1 + term2 + term3) / n_samples
                
                # Add L1 sparsity regularization to eliminate noise features
                grad_w += self.w_reg * np.sign(w)
                grad_w = np.clip(grad_w, -2.0, 2.0)
                
                # Update weights
                w = w - lr_w * grad_w
                # Project w to non-negative and normalize so mean(w) = 1.0
                w = np.maximum(w, 0.001)
                w = w * (n_features / np.sum(w))

            # Update radii
            r_core = np.clip(r_core - lr_radii * grad_core, 0.1, mean_d + 10.0)
            r_decay = np.clip(r_decay - lr_radii * grad_decay, 0.5, 30.0)
            prev_grad_core_sign = curr_grad_core_sign

            # Track weight distribution
            cut = min(100, max(1, n_features // 2))
            inf_mean = float(np.mean(w[:cut]))
            noise_mean = float(np.mean(w[cut:])) if cut < n_features else inf_mean
            w_norm = w / np.sum(w)
            w_entropy = -float(np.sum(w_norm * np.log(w_norm + 1e-12)))

            self.history_["epoch"].append(epoch)
            self.history_["loss"].append(loss)
            self.history_["val_loss"].append(val_loss)
            self.history_["train_acc"].append(train_acc)
            self.history_["val_acc"].append(val_acc)
            self.history_["r_core"].append(r_core)
            self.history_["r_decay"].append(r_decay)
            self.history_["w_entropy"].append(w_entropy)
            self.history_["informative_w_mean"].append(inf_mean)
            self.history_["noise_w_mean"].append(noise_mean)

        self.r_core_final_ = r_core
        self.r_decay_final_ = r_decay
        self.w_final_ = w
        self.rbf_beta_ = rbf_beta
        return self

    def predict_potential(self, X):
        X_scaled = self.scaler_.transform(X)
        dists = self._compute_weighted_dists(X_scaled, self.X_train_, self.w_final_)
        inf, _ = self._compute_influence(dists, self.r_core_final_, self.r_decay_final_)
        p_pfdc = np.sum(inf * self.charges_[np.newaxis, :], axis=1)
        if self.gamma < 1.0:
            p_rbf = np.sum(np.exp(-self.rbf_beta_ * (dists ** 2)) * self.charges_[np.newaxis, :], axis=1)
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


def run_anisotropic_comparison():
    print("="*80)
    print("COMPARATIVE STUDY: PFDC WITH VS. WITHOUT ANISOTROPIC WEIGHTING ON 1,000 FEATURES")
    print("="*80)

    train_data = np.load("data/dataset_1000d_train.npz")
    test_data = np.load("data/dataset_1000d_test.npz")
    X_train, y_train = train_data['X'], train_data['y']
    X_test, y_test = test_data['X'], test_data['y']
    print(f"Data Loaded: Train {X_train.shape}, Test {X_test.shape}")

    # 1. Standard Isotropic PFDC (WITHOUT feature weighting, w_j = 1)
    print("\n--> Training PFDC WITHOUT Anisotropic Weighting (Isotropic Baseline, w_j = 1.0)...")
    t0 = time.time()
    pfdc_isotropic = AnisotropicPFDC(max_epochs=80, lr_radii=0.06)
    pfdc_isotropic.fit(X_train, y_train, eval_set=(X_test, y_test), learn_weights=False)
    time_iso = time.time() - t0
    y_pred_iso = pfdc_isotropic.predict(X_test)
    y_prob_iso = pfdc_isotropic.predict_proba(X_test)[:, 1]
    acc_iso = accuracy_score(y_test, y_pred_iso) * 100.0
    f1_iso = f1_score(y_test, y_pred_iso)
    auc_iso = roc_auc_score(y_test, y_prob_iso)
    loss_iso = log_loss(y_test, y_prob_iso)
    print(f"PFDC WITHOUT Weights (Isotropic): Acc = {acc_iso:.2f}%, F1 = {f1_iso:.4f}, AUC = {auc_iso:.4f}, Loss = {loss_iso:.4f}")

    # 2. Anisotropic PFDC (WITH learned feature weighting w_j)
    print("\n--> Training PFDC WITH Anisotropic Feature Weighting (Learning w_j across all 1,000 features)...")
    t0 = time.time()
    pfdc_anisotropic = AnisotropicPFDC(max_epochs=80, lr_radii=0.06, lr_w=0.05, w_reg=2e-4)
    pfdc_anisotropic.fit(X_train, y_train, eval_set=(X_test, y_test), learn_weights=True)
    time_aniso = time.time() - t0
    y_pred_aniso = pfdc_anisotropic.predict(X_test)
    y_prob_aniso = pfdc_anisotropic.predict_proba(X_test)[:, 1]
    acc_aniso = accuracy_score(y_test, y_pred_aniso) * 100.0
    f1_aniso = f1_score(y_test, y_pred_aniso)
    auc_aniso = roc_auc_score(y_test, y_prob_aniso)
    loss_aniso = log_loss(y_test, y_prob_aniso)
    print(f"PFDC WITH Anisotropic Weights: Acc = {acc_aniso:.2f}%, F1 = {f1_aniso:.4f}, AUC = {auc_aniso:.4f}, Loss = {loss_aniso:.4f}")

    # 3. Benchmark Competitors
    print("\n--> Evaluating Competitors...")
    competitors = {
        "SVM (RBF Kernel)": SVC(kernel='rbf', probability=True, random_state=42),
        "Deep MLP (PyTorch/Sklearn)": MLPClassifier(hidden_layer_sizes=(128, 64), activation='relu', max_iter=150, random_state=42),
        "LightGBM (v4.7.0)": lgb.LGBMClassifier(n_estimators=100, max_depth=4, learning_rate=0.08, random_state=42, verbose=-1),
        "XGBoost (v3.2.0)": xgb.XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.08, random_state=42)
    }
    
    comp_results = []
    for c_name, c_model in competitors.items():
        t0 = time.time()
        c_model.fit(X_train, y_train)
        c_time = time.time() - t0
        c_pred = c_model.predict(X_test)
        c_prob = c_model.predict_proba(X_test)[:, 1]
        comp_results.append({
            "Model": c_name,
            "Accuracy (%)": accuracy_score(y_test, c_pred) * 100.0,
            "F1-Score": f1_score(y_test, c_pred),
            "ROC-AUC": roc_auc_score(y_test, c_prob),
            "Test BCE Loss": log_loss(y_test, c_prob),
            "Fit Time (s)": c_time
        })

    # Summary Table
    results = [
        {
            "Model": "PFDC WITH Anisotropic Weights (A-PFDC)",
            "Accuracy (%)": acc_aniso,
            "F1-Score": f1_aniso,
            "ROC-AUC": auc_aniso,
            "Test BCE Loss": loss_aniso,
            "Fit Time (s)": time_aniso
        },
        {
            "Model": "PFDC WITHOUT Weights (Isotropic Baseline)",
            "Accuracy (%)": acc_iso,
            "F1-Score": f1_iso,
            "ROC-AUC": auc_iso,
            "Test BCE Loss": loss_iso,
            "Fit Time (s)": time_iso
        }
    ] + comp_results
    
    df_res = pd.DataFrame(results).sort_values(by="Accuracy (%)", ascending=False).reset_index(drop=True)
    print("\n" + "="*80)
    print("LEADERBOARD: WITH VS. WITHOUT ANISOTROPIC WEIGHTS IN PFDC")
    print("="*80)
    print(df_res.to_string(index=False))
    df_res.to_csv("figures/anisotropic_comparison_results.csv", index=False)

    # 4. Generate Publication-Quality Figures
    # Plot 1: Feature Weights Learned by Anisotropic PFDC across all 1,000 Dimensions
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5.5))
    w_learned = pfdc_anisotropic.w_final_
    features_idx = np.arange(len(w_learned))
    
    # Highlight informative features (0-99) vs noise features (100-999)
    ax1.plot(features_idx[:100], w_learned[:100], color='#2ecc71', label='Informative Features (1-100)', linewidth=2.0)
    ax1.plot(features_idx[100:], w_learned[100:], color='#e74c3c', alpha=0.5, label='Noise / Redundant Features (101-1000)', linewidth=0.8)
    ax1.axhline(1.0, color='black', linestyle='--', label='Initial Uniform Weight (w=1.0)')
    ax1.set_title("Learned Feature Importance Profile $w_j$ Across 1,000 Dimensions", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Independent Variable Index $j$")
    ax1.set_ylabel("Learned Feature Weight $w_j$")
    ax1.legend(frameon=True)
    
    # Bar comparison: Mean weight of Informative vs Noise
    inf_mean = np.mean(w_learned[:100])
    noise_mean = np.mean(w_learned[100:])
    bars = ax2.bar(["Informative Features\n(Top 100)", "Noise Features\n(Remaining 900)"], 
                   [inf_mean, noise_mean], color=['#2ecc71', '#e74c3c'], edgecolor='black', width=0.5)
    ax2.set_title("Mean Feature Weight Allocation", fontsize=12, fontweight='bold')
    ax2.set_ylabel("Average Weight Magnitude")
    for bar in bars:
        h = bar.get_height()
        ax2.annotate(f"{h:.3f}", (bar.get_x() + bar.get_width()/2., h + 0.05),
                     ha='center', va='bottom', fontweight='bold', fontsize=11)
                     
    plt.suptitle("Anisotropic PFDC Feature Selection: Automated Noise Suppression in 1,000D", fontsize=14, fontweight='bold')
    plt.tight_layout()
    p1 = os.path.join(OUTPUT_DIR, "anisotropic_feature_weights.png")
    plt.savefig(p1, dpi=300)
    plt.close()
    print(f"Saved Plot 1: {p1}")

    # Plot 2: Accuracy & Loss Comparison (With vs Without vs Competitors)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    bar_palette = ["#2ecc71" if "A-PFDC" in m else "#27ae60" if "PFDC" in m else "#3498db" for m in df_res["Model"]]
    
    sns.barplot(data=df_res, x="Accuracy (%)", y="Model", hue="Model", palette=bar_palette, legend=False, ax=ax1)
    ax1.set_title("Test Accuracy Comparison on 1,000 Independent Variables", fontsize=13, fontweight='bold')
    ax1.set_xlim(65, 90)
    for p in ax1.patches:
        w = p.get_width()
        ax1.annotate(f"{w:.2f}%", (w - 2.0, p.get_y() + p.get_height()/2.), ha='center', va='center', color='white', fontweight='bold')
        
    sns.barplot(data=df_res, x="Test BCE Loss", y="Model", hue="Model", palette=bar_palette, legend=False, ax=ax2)
    ax2.set_title("Test Cross-Entropy Loss (Lower is Better)", fontsize=13, fontweight='bold')
    for p in ax2.patches:
        w = p.get_width()
        ax2.annotate(f"{w:.3f}", (w + 0.02, p.get_y() + p.get_height()/2.), ha='left', va='center', fontsize=9)
        
    plt.suptitle("Impact of Anisotropic Distance: PFDC With vs. Without Learned Weights $w_j$", fontsize=15, fontweight='bold')
    plt.tight_layout()
    p2 = os.path.join(OUTPUT_DIR, "anisotropic_vs_isotropic_benchmark.png")
    plt.savefig(p2, dpi=300)
    plt.close()
    print(f"Saved Plot 2: {p2}")

    # Plot 3: Epoch-by-Epoch Convergence With vs Without
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.5))
    h_iso = pfdc_isotropic.history_
    h_aniso = pfdc_anisotropic.history_
    
    ax1.plot(h_iso["epoch"], h_iso["val_loss"], label="PFDC WITHOUT Weights (Isotropic)", color="#e67e22", linestyle="--", linewidth=2.0)
    ax1.plot(h_aniso["epoch"], h_aniso["val_loss"], label="PFDC WITH Anisotropic Weights (A-PFDC)", color="#2ecc71", linewidth=2.4)
    ax1.set_title("Validation Loss Trajectory over Training", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Binary Cross-Entropy Loss")
    ax1.legend(frameon=True)
    
    ax2.plot(h_iso["epoch"], np.array(h_iso["val_acc"])*100.0, label="PFDC WITHOUT Weights (Isotropic)", color="#e67e22", linestyle="--", linewidth=2.0)
    ax2.plot(h_aniso["epoch"], np.array(h_aniso["val_acc"])*100.0, label="PFDC WITH Anisotropic Weights (A-PFDC)", color="#2ecc71", linewidth=2.4)
    ax2.set_title("Validation Accuracy Trajectory over Training", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Accuracy (%)")
    ax2.legend(frameon=True)
    
    plt.suptitle("Training Dynamics: Convergence Acceleration via Anisotropic Feature Learning", fontsize=14, fontweight='bold')
    plt.tight_layout()
    p3 = os.path.join(OUTPUT_DIR, "anisotropic_convergence_curves.png")
    plt.savefig(p3, dpi=300)
    plt.close()
    print(f"Saved Plot 3: {p3}")

    print("\nAnisotropic Benchmark Run Completed Successfully!")

if __name__ == "__main__":
    run_anisotropic_comparison()
