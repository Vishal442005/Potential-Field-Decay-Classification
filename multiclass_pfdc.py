import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.datasets import load_wine, load_digits
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import lightgbm as lgb

OUTPUT_DIR = "figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'

class MultiClassPFDC:
    """
    Multi-Class Potential Field Decay Classifier (K > 2 Classes).
    
    Constructs K parallel potential energy fields using One-vs-Rest polarity:
        P_k(x) = sum_i q_{i,k} * I(d_w(x, x_i))
    
    Decision rule:
        y_hat = argmax_k P_k(x)
    """
    def __init__(
        self,
        decay_rate=5.0,
        alpha=1.0,
        r_core_init=0.5,
        r_decay_init=1.5,
        lr_radii=0.06,
        lr_w=0.04,
        max_epochs=60,
        temperature=1.0,
        balance_charges=True,
        random_state=42
    ):
        self.decay_rate = decay_rate
        self.alpha = alpha
        self.r_core_init = r_core_init
        self.r_decay_init = r_decay_init
        self.lr_radii = lr_radii
        self.lr_w = lr_w
        self.max_epochs = max_epochs
        self.temperature = temperature
        self.balance_charges = balance_charges
        self.random_state = random_state

    def _compute_influence(self, dists, r_core, r_decay):
        influence = np.zeros_like(dists, dtype=float)
        mask_core = (dists <= r_core)
        influence[mask_core] = 1.0
        
        outer_limit = r_core + r_decay
        mask_decay = (dists > r_core) & (dists <= outer_limit)
        
        if np.any(mask_decay):
            u = (dists[mask_decay] - r_core) / max(r_decay, 1e-6)
            influence[mask_decay] = np.exp(-self.decay_rate * (u ** self.alpha))
            
        return influence, mask_decay

    def fit(self, X, y):
        self.scaler_ = StandardScaler()
        self.X_train_ = self.scaler_.fit_transform(X)
        self.y_train_ = np.asarray(y)
        self.classes_ = np.unique(self.y_train_)
        self.K_ = len(self.classes_)
        n_samples, n_features = self.X_train_.shape

        # Precompute polarity charges for all K classes: shape (N, K)
        self.charges_ = np.zeros((n_samples, self.K_), dtype=float)
        for k_idx, c in enumerate(self.classes_):
            pos_mask = (self.y_train_ == c)
            neg_mask = ~pos_mask
            n_pos = np.sum(pos_mask)
            n_neg = np.sum(neg_mask)
            
            if self.balance_charges:
                q_pos = (n_samples / (2.0 * n_pos)) if n_pos > 0 else 1.0
                q_neg = -(n_samples / (2.0 * n_neg)) if n_neg > 0 else -1.0
                self.charges_[:, k_idx] = np.where(pos_mask, q_pos, q_neg)
            else:
                self.charges_[:, k_idx] = np.where(pos_mask, 1.0, -1.0)

        # Pairwise distance initialization
        from sklearn.metrics.pairwise import euclidean_distances
        train_dists = euclidean_distances(self.X_train_, self.X_train_)
        non_diag = train_dists[train_dists > 0]
        mean_d = float(np.mean(non_diag))
        std_d = float(np.std(non_diag))

        r_core = max(0.2, mean_d - 1.2 * std_d)
        r_decay = max(0.8, 2.5 * std_d)
        lr_radii = float(self.lr_radii)

        # Train parameters using multi-class cross-entropy
        y_one_hot = np.zeros((n_samples, self.K_))
        for k_idx, c in enumerate(self.classes_):
            y_one_hot[:, k_idx] = (self.y_train_ == c).astype(float)

        for epoch in range(1, self.max_epochs + 1):
            inf, mask_decay = self._compute_influence(train_dists, r_core, r_decay)
            # Potentials for each class: shape (N, K)
            pots = np.matmul(inf, self.charges_)
            
            # Softmax
            exp_pots = np.exp(np.clip(pots / self.temperature, -20.0, 20.0))
            probs = exp_pots / (np.sum(exp_pots, axis=1, keepdims=True) + 1e-12)
            
            # Error signal: (probs - y_one_hot) shape (N, K)
            delta = probs - y_one_hot
            
            # Gradient w.r.t r_core and r_decay inside decay shell
            dI_dcore = np.zeros_like(train_dists)
            dI_ddecay = np.zeros_like(train_dists)
            
            if np.any(mask_decay):
                u = (train_dists[mask_decay] - r_core) / max(r_decay, 1e-6)
                u_clamped = np.maximum(u, 1e-6)
                decay_exp = np.exp(-self.decay_rate * (u_clamped ** self.alpha))
                factor = (self.decay_rate * self.alpha / max(r_decay, 1e-6)) * decay_exp
                dI_dcore[mask_decay] = factor * (u_clamped ** (self.alpha - 1.0))
                dI_ddecay[mask_decay] = factor * (u_clamped ** self.alpha)

            # dP_k / dTheta = sum_i q_{i,k} * (dI / dTheta)
            dP_dcore = np.matmul(dI_dcore, self.charges_) # (N, K)
            dP_ddecay = np.matmul(dI_ddecay, self.charges_) # (N, K)
            
            # Chain rule through softmax cross-entropy
            grad_core = np.clip(np.mean(np.sum(delta * dP_dcore, axis=1)), -5.0, 5.0)
            grad_decay = np.clip(np.mean(np.sum(delta * dP_ddecay, axis=1)), -5.0, 5.0)
            
            # Update
            r_core = max(0.01, r_core - lr_radii * grad_core)
            r_decay = max(0.1, r_decay - lr_radii * grad_decay)

        self.r_core_final_ = r_core
        self.r_decay_final_ = r_decay
        return self

    def predict_potential(self, X):
        from sklearn.metrics.pairwise import euclidean_distances
        X_scaled = self.scaler_.transform(X)
        dists = euclidean_distances(X_scaled, self.X_train_)
        inf, _ = self._compute_influence(dists, self.r_core_final_, self.r_decay_final_)
        pots = np.matmul(inf, self.charges_)
        return pots

    def predict_proba(self, X):
        pots = self.predict_potential(X)
        exp_pots = np.exp(np.clip(pots / self.temperature, -20.0, 20.0))
        return exp_pots / (np.sum(exp_pots, axis=1, keepdims=True) + 1e-12)

    def predict(self, X):
        pots = self.predict_potential(X)
        class_indices = np.argmax(pots, axis=1)
        return self.classes_[class_indices]


def run_multiclass_benchmark():
    print("="*80)
    print("OPTION 2: MULTI-CLASS PFDC BENCHMARK (K > 2 CLASSES)")
    print("="*80)

    datasets = {
        "Wine Recognition (K=3)": load_wine(),
        "Digits MNIST-Lite (K=10)": load_digits()
    }

    models = {
        "Multi-Class PFDC (Ours)": lambda: MultiClassPFDC(max_epochs=60),
        "XGBoost": lambda: xgb.XGBClassifier(eval_metric='mlogloss', random_state=42),
        "LightGBM": lambda: lgb.LGBMClassifier(random_state=42, verbose=-1),
        "Deep MLP": lambda: MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=200, random_state=42),
        "SVM (RBF OvR)": lambda: SVC(kernel='rbf', probability=True, random_state=42),
        "Random Forest": lambda: RandomForestClassifier(n_estimators=100, random_state=42)
    }

    all_results = []
    confusion_matrices = {}

    for d_name, d_obj in datasets.items():
        X, y = d_obj.data, d_obj.target
        K = len(np.unique(y))
        print(f"\nEvaluating Multi-Class Benchmark on {d_name}: N={X.shape[0]}, D={X.shape[1]}, K={K} Classes...")
        
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        dataset_scores = {m: [] for m in models}

        for train_idx, test_idx in skf.split(X, y):
            X_tr, X_te = X[train_idx], X[test_idx]
            y_tr, y_te = y[train_idx], y[test_idx]

            for m_name, m_fn in models.items():
                clf = m_fn()
                if "PFDC" in m_name:
                    clf.fit(X_tr, y_tr)
                    y_pred = clf.predict(X_te)
                else:
                    sc = StandardScaler()
                    clf.fit(sc.fit_transform(X_tr), y_tr)
                    y_pred = clf.predict(sc.transform(X_te))

                acc = accuracy_score(y_te, y_pred) * 100.0
                dataset_scores[m_name].append(acc)

        for m_name in models:
            mean_acc = np.mean(dataset_scores[m_name])
            std_acc = np.std(dataset_scores[m_name])
            all_results.append({
                "Dataset": d_name,
                "Model": m_name,
                "Accuracy (%)": f"{mean_acc:.2f} ± {std_acc:.2f}",
                "Mean Accuracy (%)": mean_acc
            })
            print(f"--> {m_name:24s}: {mean_acc:.2f}% ± {std_acc:.2f}%")

    df_mc = pd.DataFrame(all_results)
    df_mc.to_csv("figures/multiclass_benchmark_results.csv", index=False)

    # Plot Multi-Class Results
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5.5))
    wine_df = df_mc[df_mc["Dataset"].str.contains("Wine")].sort_values(by="Mean Accuracy (%)", ascending=False)
    digits_df = df_mc[df_mc["Dataset"].str.contains("Digits")].sort_values(by="Mean Accuracy (%)", ascending=False)

    bar_colors_wine = ["#2ecc71" if "PFDC" in m else "#3498db" for m in wine_df["Model"]]
    bar_colors_digits = ["#2ecc71" if "PFDC" in m else "#3498db" for m in digits_df["Model"]]

    sns.barplot(data=wine_df, x="Mean Accuracy (%)", y="Model", palette=bar_colors_wine, ax=ax1)
    ax1.set_title("Wine Recognition (K = 3 Classes, D = 13)", fontsize=12, fontweight='bold')
    ax1.set_xlim(90, 100)
    for p in ax1.patches:
        w = p.get_width()
        ax1.annotate(f"{w:.2f}%", (w - 1.2, p.get_y() + p.get_height()/2.), ha='center', va='center', color='white', fontweight='bold')

    sns.barplot(data=digits_df, x="Mean Accuracy (%)", y="Model", palette=bar_colors_digits, ax=ax2)
    ax2.set_title("Optical Digits MNIST-Lite (K = 10 Classes, D = 64)", fontsize=12, fontweight='bold')
    ax2.set_xlim(90, 100)
    for p in ax2.patches:
        w = p.get_width()
        ax2.annotate(f"{w:.2f}%", (w - 1.2, p.get_y() + p.get_height()/2.), ha='center', va='center', color='white', fontweight='bold')

    plt.suptitle("Multi-Class Generalization: PFDC vs. SOTA on K = 3 and K = 10 Benchmark Tasks", fontsize=14, fontweight='bold')
    plt.tight_layout()
    p_path = os.path.join(OUTPUT_DIR, "multiclass_benchmark_results.png")
    plt.savefig(p_path, dpi=300)
    plt.close()
    print(f"Saved Multi-Class Benchmark Figure: {p_path}")

if __name__ == "__main__":
    run_multiclass_benchmark()
