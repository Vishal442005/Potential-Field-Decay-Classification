import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_breast_cancer, fetch_openml
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, log_loss
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import lightgbm as lgb

from anisotropic_pfdc import AnisotropicPFDC
from rl_classifier import ReinforcementLearningClassifier
from unsupervised_classifier import SelfSupervisedContrastiveClassifier

OUTPUT_DIR = "figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'

def load_datasets():
    datasets = {}
    
    # 1. Breast Cancer Wisconsin (D=30)
    bc = load_breast_cancer()
    datasets["Breast Cancer (D=30)"] = {
        "X": bc.data,
        "y": bc.target,
        "feature_names": bc.feature_names
    }
    
    # 2. Ionosphere (D=34)
    iono = fetch_openml('ionosphere', version=1, as_frame=False, parser='auto')
    le_iono = LabelEncoder()
    y_iono = le_iono.fit_transform(iono.target)
    datasets["Ionosphere (D=34)"] = {
        "X": iono.data.astype(float),
        "y": y_iono,
        "feature_names": [f"Freq_{i+1}" for i in range(iono.data.shape[1])]
    }
    
    # 3. Sonar (D=60)
    sonar = fetch_openml('sonar', version=1, as_frame=False, parser='auto')
    le_sonar = LabelEncoder()
    y_sonar = le_sonar.fit_transform(sonar.target)
    datasets["Sonar (D=60)"] = {
        "X": sonar.data.astype(float),
        "y": y_sonar,
        "feature_names": [f"Band_{i+1}" for i in range(sonar.data.shape[1])]
    }
    
    return datasets

def run_benchmark():
    datasets = load_datasets()
    
    models = {
        "A-PFDC (Ours: Anisotropic)": lambda: AnisotropicPFDC(max_epochs=45, lr_radii=0.06, lr_w=0.04, gamma=0.85),
        "PFDC (Isotropic)": lambda: AnisotropicPFDC(max_epochs=45, lr_radii=0.06, lr_w=0.00, gamma=0.85),
        "XGBoost": lambda: xgb.XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.08, random_state=42, eval_metric='logloss'),
        "LightGBM": lambda: lgb.LGBMClassifier(n_estimators=100, max_depth=4, learning_rate=0.08, random_state=42, verbose=-1),
        "Random Forest": lambda: RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42),
        "SVM (RBF Kernel)": lambda: SVC(kernel='rbf', C=1.5, probability=True, random_state=42),
        "Deep MLP": lambda: MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=200, random_state=42),
        "Self-Supervised (SimCLR-SSL)": lambda: SelfSupervisedContrastiveClassifier(epochs=30, lr=0.01, random_state=42),
        "RL Bandit (Actor-Critic)": lambda: ReinforcementLearningClassifier(epochs=35, lr=0.01, random_state=42)
    }

    records = []
    learned_weights_dict = {}

    print("="*90)
    print("EXECUTING ALL LEARNING MODELS ACROSS 3 HIGH-DIMENSIONAL DATASETS (D > 2)")
    print("="*90)

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    for d_name, d_data in datasets.items():
        X, y = d_data["X"], d_data["y"]
        n_samples, n_features = X.shape
        print(f"\nEvaluating Dataset: {d_name} (N = {n_samples}, D = {n_features} independent variables)...")

        # Track weights for A-PFDC on full dataset
        a_pfdc_full = AnisotropicPFDC(max_epochs=50, lr_radii=0.06, lr_w=0.04, gamma=0.85)
        a_pfdc_full.fit(X, y, learn_weights=True)
        learned_weights_dict[d_name] = a_pfdc_full.w_final_

        for m_name, m_constructor in models.items():
            fold_accs, fold_f1s, fold_aucs, fold_losses = [], [], [], []
            t_trains, t_inferences = [], []

            for fold_idx, (train_idx, test_idx) in enumerate(skf.split(X, y)):
                X_tr, y_tr = X[train_idx], y[train_idx]
                X_te, y_te = X[test_idx], y[test_idx]

                scaler = StandardScaler()
                X_tr_sc = scaler.fit_transform(X_tr)
                X_te_sc = scaler.transform(X_te)

                model = m_constructor()
                
                # Training latency
                t0 = time.perf_counter()
                if "PFDC" in m_name:
                    model.fit(X_tr, y_tr, learn_weights=("Anisotropic" in m_name))
                elif "SVM" in m_name or "Deep MLP" in m_name:
                    model.fit(X_tr_sc, y_tr)
                else:
                    model.fit(X_tr, y_tr)
                t_train = (time.perf_counter() - t0) * 1000.0

                # Inference latency
                t0 = time.perf_counter()
                if "PFDC" in m_name:
                    preds = model.predict(X_te)
                    probs = model.predict_proba(X_te)[:, 1] if hasattr(model, 'predict_proba') else None
                elif "SVM" in m_name or "Deep MLP" in m_name:
                    preds = model.predict(X_te_sc)
                    probs = model.predict_proba(X_te_sc)[:, 1]
                else:
                    preds = model.predict(X_te)
                    probs = model.predict_proba(X_te)[:, 1] if hasattr(model, 'predict_proba') else None
                t_infer = (time.perf_counter() - t0) * 1000.0

                acc = accuracy_score(y_te, preds)
                f1 = f1_score(y_te, preds, zero_division=0)
                auc = roc_auc_score(y_te, probs) if probs is not None and len(np.unique(y_te)) > 1 else np.nan
                loss = log_loss(y_te, probs) if probs is not None else np.nan

                fold_accs.append(acc)
                fold_f1s.append(f1)
                fold_aucs.append(auc)
                fold_losses.append(loss)
                t_trains.append(t_train)
                t_inferences.append(t_infer)

            mean_acc = np.mean(fold_accs) * 100.0
            std_acc = np.std(fold_accs) * 100.0
            mean_f1 = np.mean(fold_f1s) * 100.0
            mean_auc = np.nanmean(fold_aucs)
            mean_loss = np.nanmean(fold_losses)
            mean_t_tr = np.mean(t_trains)
            mean_t_inf = np.mean(t_inferences)

            records.append({
                "Dataset": d_name,
                "Model": m_name,
                "Accuracy (%)": f"{mean_acc:.2f} ± {std_acc:.2f}",
                "Mean Accuracy": mean_acc,
                "F1 Score (%)": f"{mean_f1:.2f}",
                "ROC-AUC": f"{mean_auc:.4f}" if not np.isnan(mean_auc) else "N/A",
                "Log Loss": f"{mean_loss:.4f}" if not np.isnan(mean_loss) else "N/A",
                "Train Time (ms)": f"{mean_t_tr:.1f}",
                "Infer Time (ms)": f"{mean_t_inf:.2f}"
            })
            print(f"  {m_name:30s} | Acc: {mean_acc:6.2f}% (±{std_acc:4.2f}%) | F1: {mean_f1:6.2f}% | AUC: {mean_auc:.4f} | Train: {mean_t_tr:6.1f}ms")

    df_results = pd.DataFrame(records)
    csv_path = os.path.join(OUTPUT_DIR, "multidataset_all_models_results.csv")
    df_results.to_csv(csv_path, index=False)
    print(f"\nSaved full benchmark results to: {csv_path}")

    # 1. Grouped Bar Chart of Accuracies across Datasets
    plt.figure(figsize=(14, 7))
    sns.barplot(
        data=df_results,
        x="Dataset",
        y="Mean Accuracy",
        hue="Model",
        palette="tab10"
    )
    plt.title("Comparative Performance of All Learning Paradigms Across High-Dimensional Datasets (D > 2)", fontsize=13, fontweight='bold', pad=12)
    plt.ylabel("5-Fold Cross-Validation Accuracy (%)", fontsize=11)
    plt.xlabel("Benchmark Dataset", fontsize=11)
    plt.ylim(55, 102)
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0., frameon=True)
    plt.tight_layout()
    bar_path = os.path.join(OUTPUT_DIR, "multidataset_all_models_accuracy.png")
    plt.savefig(bar_path, dpi=300)
    plt.close()
    print(f"Saved Grouped Bar Chart: {bar_path}")

    # 2. Anisotropic Feature Weights Visualization (D > 2 in action)
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
    for ax, (d_name, weights) in zip(axes, learned_weights_dict.items()):
        feat_idx = np.arange(len(weights)) + 1
        colors = plt.cm.viridis(weights / np.max(weights))
        ax.bar(feat_idx, weights, color=colors, width=0.8, edgecolor='black', linewidth=0.5)
        ax.axhline(1.0, color='red', linestyle='--', linewidth=1.2, label='Baseline Isotropic Weight (w=1.0)')
        ax.set_title(f"Learned Metric Tensor w_j\n{d_name}", fontsize=11, fontweight='bold')
        ax.set_xlabel("Independent Variable Index j (1 to D)", fontsize=10)
        ax.set_ylabel("Anisotropic Weight w_j", fontsize=10)
        ax.legend(loc='upper right', frameon=True, fontsize=8.5)
    
    plt.suptitle("Automated Dimensionality Modulation in D > 2: PFDC Metric Tensor Learning", fontsize=14, fontweight='bold')
    plt.tight_layout()
    w_path = os.path.join(OUTPUT_DIR, "pfdc_highd_learned_weights.png")
    plt.savefig(w_path, dpi=300)
    plt.close()
    print(f"Saved Feature Weight Figure: {w_path}")

    # 3. Pivot Summary Table
    pivot_df = df_results.pivot(index="Model", columns="Dataset", values="Mean Accuracy")
    pivot_df["Mean Across Datasets"] = pivot_df.mean(axis=1)
    pivot_df = pivot_df.sort_values(by="Mean Across Datasets", ascending=False)
    pivot_csv = os.path.join(OUTPUT_DIR, "multidataset_all_models_pivot.csv")
    pivot_df.to_csv(pivot_csv)
    print("\n" + "="*90)
    print("OVERALL LEADERBOARD (MEAN ACCURACY ACROSS ALL 3 HIGH-DIMENSIONAL DATASETS)")
    print("="*90)
    print(pivot_df.round(2).to_string())

if __name__ == "__main__":
    run_benchmark()
