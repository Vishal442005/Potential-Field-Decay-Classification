import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.neighbors import BallTree
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_classification
from sklearn.svm import SVC
from sklearn.metrics.pairwise import euclidean_distances

OUTPUT_DIR = "figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'

class SpatialPFDC:
    """
    PFDC Spatial Inference Engine using Ball-Tree Indexing.
    
    Exploits the hard cutoff boundary of PFDC:
    Because I(d) == 0.0 for all d > R_core + R_decay, points outside
    this sphere exert strictly zero influence.
    
    Reduces query complexity from O(N) to O(K + log N).
    """
    def __init__(self, r_core=0.25, r_decay=0.85, decay_rate=5.0, alpha=1.0):
        self.r_core = r_core
        self.r_decay = r_decay
        self.decay_rate = decay_rate
        self.alpha = alpha
        self.active_radius = r_core + r_decay

    def fit(self, X, y):
        self.scaler = StandardScaler()
        self.X_train = self.scaler.fit_transform(X)
        self.y_train = np.asarray(y)
        self.classes_ = np.unique(self.y_train)
        
        pos_mask = (self.y_train == self.classes_[1])
        n_samples = len(y)
        n_pos = np.sum(pos_mask)
        n_neg = n_samples - n_pos
        q_pos = (n_samples / (2.0 * n_pos)) if n_pos > 0 else 1.0
        q_neg = -(n_samples / (2.0 * n_neg)) if n_neg > 0 else -1.0
        self.charges = np.where(pos_mask, q_pos, q_neg)
        
        # Build spatial BallTree index
        self.ball_tree = BallTree(self.X_train, leaf_size=30)
        return self

    def _influence(self, dists):
        inf = np.zeros_like(dists, dtype=float)
        mask_core = (dists <= self.r_core)
        inf[mask_core] = 1.0
        mask_decay = (dists > self.r_core) & (dists <= self.active_radius)
        if np.any(mask_decay):
            u = (dists[mask_decay] - self.r_core) / self.r_decay
            inf[mask_decay] = np.exp(-self.decay_rate * (u ** self.alpha))
        return inf

    def predict_potential_brute(self, X):
        """Standard O(N) brute-force pairwise distance inference."""
        X_scaled = self.scaler.transform(X)
        dists = euclidean_distances(X_scaled, self.X_train)
        inf = self._influence(dists)
        return np.sum(inf * self.charges[np.newaxis, :], axis=1)

    def predict_potential_fast(self, X):
        """Accelerated O(log N) BallTree query inference."""
        X_scaled = self.scaler.transform(X)
        indices, dists = self.ball_tree.query_radius(
            X_scaled, r=self.active_radius, return_distance=True
        )
        
        n_queries = X.shape[0]
        potentials = np.zeros(n_queries, dtype=float)
        
        for m in range(n_queries):
            idx = indices[m]
            if len(idx) == 0:
                continue
            sub_dists = dists[m]
            sub_inf = self._influence(sub_dists)
            potentials[m] = np.sum(sub_inf * self.charges[idx])
            
        return potentials

    def predict(self, X):
        pot = self.predict_potential_fast(X)
        return np.where(pot >= 0, self.classes_[1], self.classes_[0])


def benchmark_spatial_acceleration():
    print("="*80)
    print("OPTION 3: SPATIAL BALL-TREE INFERENCE ACCELERATION (O(N) VS O(log N))")
    print("="*80)

    sample_sizes = [500, 1000, 2500, 5000, 10000, 20000]
    n_test = 200
    n_features = 10

    records = []

    for N in sample_sizes:
        print(f"\nEvaluating Inference Scalability at N = {N} training samples...")
        X, y = make_classification(n_samples=N + n_test, n_features=n_features, n_informative=8, random_state=42)
        X_train, X_test = X[:N], X[N:]
        y_train, y_test = y[:N], y[N:]

        model = SpatialPFDC(r_core=0.25, r_decay=0.85)
        model.fit(X_train, y_train)

        # Warmup
        _ = model.predict_potential_brute(X_test[:5])
        _ = model.predict_potential_fast(X_test[:5])

        # 1. Brute Force O(N) inference
        t0 = time.perf_counter()
        pot_brute = model.predict_potential_brute(X_test)
        time_brute = (time.perf_counter() - t0) * 1000.0 # ms

        # 2. Fast BallTree O(log N) inference
        t0 = time.perf_counter()
        pot_fast = model.predict_potential_fast(X_test)
        time_fast = (time.perf_counter() - t0) * 1000.0 # ms

        # 3. Competitor: SVM (Linear/RBF kernel)
        svm = SVC(kernel='rbf', random_state=42)
        svm.fit(model.scaler.transform(X_train), y_train)
        t0 = time.perf_counter()
        _ = svm.predict(model.scaler.transform(X_test))
        time_svm = (time.perf_counter() - t0) * 1000.0

        # Verify mathematical equivalence (zero numerical error)
        max_error = np.max(np.abs(pot_brute - pot_fast))
        speedup = time_brute / max(1e-6, time_fast)

        records.append({
            "Train Samples (N)": N,
            "Brute Force O(N) (ms)": round(time_brute, 2),
            "BallTree O(log N) (ms)": round(time_fast, 2),
            "SVM Inference (ms)": round(time_svm, 2),
            "Speedup Factor": f"{speedup:.2f}x",
            "Max Numerical Discrepancy": f"{max_error:.2e}"
        })
        print(f"N={N:5d} | Brute: {time_brute:7.2f} ms | BallTree: {time_fast:7.2f} ms | Speedup: {speedup:5.2f}x | Max Err: {max_error:.1e}")

    df_accel = pd.DataFrame(records)
    print("\n" + "="*80)
    print("INFERENCE ACCELERATION BENCHMARK RESULTS")
    print("="*80)
    print(df_accel.to_string(index=False))
    df_accel.to_csv("figures/fast_indexing_benchmarks.csv", index=False)

    # Visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.5))

    ns = [r["Train Samples (N)"] for r in records]
    t_brute = [r["Brute Force O(N) (ms)"] for r in records]
    t_fast = [r["BallTree O(log N) (ms)"] for r in records]
    t_svm = [r["SVM Inference (ms)"] for r in records]
    speedups = [float(r["Speedup Factor"].replace('x', '')) for r in records]

    # Plot 1: Inference Time vs N
    ax1.plot(ns, t_brute, 'o--', color='#e74c3c', linewidth=2.2, label='Brute-Force PFDC (O(N) Complexity)')
    ax1.plot(ns, t_svm, '^-.', color='#3498db', linewidth=2.0, label='SVM (RBF Kernel)')
    ax1.plot(ns, t_fast, 's-', color='#2ecc71', linewidth=2.4, label='Fast BallTree PFDC (O(log N) Indexing)')
    ax1.set_title("Inference Latency vs. Dataset Scale (200 Queries)", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Number of Training Samples (N)", fontsize=11)
    ax1.set_ylabel("Inference Time for 200 Queries (ms)", fontsize=11)
    ax1.legend(frameon=True, fontsize=10)

    # Plot 2: Speedup Factor
    ax2.plot(ns, speedups, 'd-', color='#8e44ad', linewidth=2.4)
    ax2.set_title("Acceleration Ratio: BallTree vs. Brute-Force", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Number of Training Samples (N)", fontsize=11)
    ax2.set_ylabel("Speedup Multiplier (x Faster)", fontsize=11)
    for x_val, y_val in zip(ns, speedups):
        ax2.annotate(f"{y_val:.1f}x", (x_val, y_val + (0.05 * max(speedups))), ha='center', fontweight='bold', fontsize=9.5)

    plt.suptitle("Algorithmic Scaling: Accelerating PFDC via Hard-Cutoff Spatial Tree Indexing", fontsize=14, fontweight='bold')
    plt.tight_layout()
    p_path = os.path.join(OUTPUT_DIR, "fast_indexing_speedup.png")
    plt.savefig(p_path, dpi=300)
    plt.close()
    print(f"Saved Spatial Acceleration Figure: {p_path}")

if __name__ == "__main__":
    benchmark_spatial_acceleration()
