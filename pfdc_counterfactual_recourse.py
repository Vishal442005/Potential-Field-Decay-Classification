import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_breast_cancer
from sklearn.preprocessing import StandardScaler
from robust_field_projection import ElectroPotentialFieldProjection
from anisotropic_pfdc import AnisotropicPFDC

OUTPUT_DIR = "figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'

def generate_counterfactual_recourse():
    print("="*80)
    print("OPTION B: EXPLAINABLE AI (XAI) & PHYSICAL COUNTERFACTUAL RECOURSE VIA PFDC")
    print("="*80)

    # 1. Load real clinical dataset: Breast Cancer Wisconsin
    # Class 0: Malignant (Unfavorable), Class 1: Benign (Favorable)
    cancer = load_breast_cancer()
    X, y = cancer.data, cancer.target
    feature_names = cancer.feature_names
    target_names = cancer.target_names # ['malignant', 'benign']
    
    print(f"Loaded Clinical Dataset: {X.shape[0]} patients, {X.shape[1]} clinical biomarkers.")
    print(f"Target distribution: {np.sum(y == 0)} Malignant (Class 0), {np.sum(y == 1)} Benign (Class 1)")

    # Fit Anisotropic PFDC
    pfdc = AnisotropicPFDC(max_epochs=70, lr_radii=0.06, lr_w=0.04)
    pfdc.fit(X, y, learn_weights=True)

    # 2. Pick a high-risk Malignant patient (x_orig) with high negative potential
    scaler = pfdc.scaler_
    X_scaled = scaler.transform(X)
    potentials = pfdc.predict_potential(X)
    
    malignant_indices = np.where((y == 0) & (potentials < -2.0))[0]
    patient_idx = malignant_indices[0]
    x_orig_scaled = X_scaled[patient_idx].copy()
    x_orig_raw = X[patient_idx].copy()
    p_orig = potentials[patient_idx]
    
    print(f"\nSelected High-Risk Malignant Patient (Patient #{patient_idx}):")
    print(f"Initial Predicted Potential P(x0) = {p_orig:.4f} (Strongly Malignant)")

    # 3. Compute Counterfactual Recourse Path by Integrating Along Force Field
    # Path: x_{t+1} = x_t + eta * F(x_t) / ||F(x_t)||
    step_size = 0.08
    max_steps = 60
    
    trajectory = [x_orig_scaled.copy()]
    pot_trajectory = [p_orig]
    
    curr_x = x_orig_scaled.copy()
    w = pfdc.w_final_
    w_sqrt = np.sqrt(np.maximum(w, 1e-8))
    
    for step in range(max_steps):
        # Compute distance to all training points
        diffs = pfdc.X_train_ - curr_x[np.newaxis, :] # (N, D)
        weighted_diffs = diffs * w_sqrt[np.newaxis, :]
        dists = np.linalg.norm(weighted_diffs, axis=1)
        
        # Unit direction vectors from curr_x to training points
        unit_vecs = diffs / (dists[:, np.newaxis] + 1e-9)
        
        # Influence
        inf, _ = pfdc._compute_influence(dists, pfdc.r_core_final_, pfdc.r_decay_final_)
        
        # Force vector F = sum_i q_i * I(d) * unit_vec
        weighted_pull = unit_vecs * (inf * pfdc.charges_)[:, np.newaxis]
        force_vec = np.sum(weighted_pull, axis=0) # (D,)
        
        norm_f = np.linalg.norm(force_vec)
        if norm_f < 1e-8:
            break
            
        unit_force = force_vec / norm_f
        # Move along force vector toward higher certainty
        curr_x = curr_x + step_size * unit_force
        
        # Evaluate new potential
        curr_x_raw = scaler.inverse_transform(curr_x[np.newaxis, :])
        new_pot = float(pfdc.predict_potential(curr_x_raw)[0])
        
        trajectory.append(curr_x.copy())
        pot_trajectory.append(new_pot)
        
        # Stop once securely inside Benign Certainty Core (P >= +1.5)
        if new_pot >= 1.5:
            print(f"Reached Target Benign Certainty Zone at Step {step+1}! Potential P = {new_pot:.4f}")
            break

    traj_array = np.array(trajectory)
    x_recourse_raw = scaler.inverse_transform(traj_array[-1][np.newaxis, :])[0]
    p_final = pot_trajectory[-1]

    print("\n--- Physical Counterfactual Recourse Summary ---")
    print(f"Initial State: P = {p_orig:.3f} (Class: Malignant)")
    print(f"Final Recourse State: P = {p_final:.3f} (Class: Benign Safety Core)")
    print(f"Total Trajectory Steps: {len(trajectory) - 1}")
    print(f"L2 Perturbation Distance: {np.linalg.norm(traj_array[-1] - traj_array[0]):.4f} (Normalized feature units)")

    # Top biomarker changes along recourse path
    feature_shifts = x_recourse_raw - x_orig_raw
    shift_percent = (feature_shifts / (x_orig_raw + 1e-8)) * 100.0
    
    top_indices = np.argsort(np.abs(feature_shifts / (scaler.scale_ + 1e-8)))[::-1][:6]
    df_shifts = pd.DataFrame({
        "Biomarker Feature": [feature_names[i] for i in top_indices],
        "Patient Original": [f"{x_orig_raw[i]:.3f}" for i in top_indices],
        "Recommended Recourse": [f"{x_recourse_raw[i]:.3f}" for i in top_indices],
        "Absolute Change": [f"{feature_shifts[i]:+.3f}" for i in top_indices],
        "Relative Shift (%)": [f"{shift_percent[i]:+.1f}%" for i in top_indices]
    })
    print("\nKey Clinical Biomarker Counterfactual Recommendations:")
    print(df_shifts.to_string(index=False))
    df_shifts.to_csv("figures/counterfactual_clinical_recommendations.csv", index=False)

    # -------------------------------------------------------------
    # Visualization: Robust Electro-Potential Field-Aligned Projection (EP-FAP)
    # Replaces PCA with an intrinsic physical coordinate system aligned to the dipole field
    # -------------------------------------------------------------
    epfap = ElectroPotentialFieldProjection(huber_quantile=0.85, random_state=42)
    # Fit projection using learned anisotropic weights
    learned_w = getattr(pfdc, 'w_final_', None)
    if learned_w is not None:
        learned_w = learned_w.copy()
    X_epfap = epfap.fit_transform(X_scaled, y, feature_weights=learned_w)
    traj_epfap = epfap.transform(traj_array)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(17, 7))
    
    # Left: EP-FAP Projection with Decision Field & Patient Trajectory Streamline
    x_min, x_max = X_epfap[:, 0].min() - 0.8, X_epfap[:, 0].max() + 0.8
    y_min, y_max = X_epfap[:, 1].min() - 0.8, X_epfap[:, 1].max() + 0.8
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 60), np.linspace(y_min, y_max, 60))
    grid_epfap = np.c_[xx.ravel(), yy.ravel()]
    grid_orig = epfap.inverse_transform(grid_epfap)
    grid_raw = scaler.inverse_transform(grid_orig)
    grid_pot = pfdc.predict_potential(grid_raw).reshape(xx.shape)
    
    from matplotlib.colors import TwoSlopeNorm
    v_abs = max(abs(grid_pot.min()), abs(grid_pot.max()))
    norm_pot = TwoSlopeNorm(vmin=-v_abs, vcenter=0.0, vmax=v_abs)
    cf = ax1.contourf(xx, yy, grid_pot, levels=25, cmap='coolwarm', norm=norm_pot, alpha=0.38)
    ax1.contour(xx, yy, grid_pot, levels=[0.0], colors='black', linewidths=2.0)
    
    # Scatter all patients: Strictly Negative (Class 0) = Blue, Positive (Class 1) = Red
    ax1.scatter(X_epfap[y == 0, 0], X_epfap[y == 0, 1], color='#1f77b4', s=30, alpha=0.6, label='Malignant Patients (Class 0: Blue)')
    ax1.scatter(X_epfap[y == 1, 0], X_epfap[y == 1, 1], color='#d62728', s=30, alpha=0.6, label='Benign Patients (Class 1: Red)')
    
    # Plot Trajectory
    ax1.plot(traj_epfap[:, 0], traj_epfap[:, 1], color='#00cc99', linewidth=3.0, linestyle='-', marker='o', markersize=4, label='Physical Recourse Streamline')
    ax1.scatter(traj_epfap[0, 0], traj_epfap[0, 1], color='#1f77b4', s=160, edgecolor='black', linewidth=2, zorder=5, label=r'Patient $x_0$ (Malignant: Blue)')
    ax1.scatter(traj_epfap[-1, 0], traj_epfap[-1, 1], color='#d62728', s=160, edgecolor='black', linewidth=2, zorder=5, label=r'Target $x^*$ (Benign Core: Red)')
    
    ax1.set_title("PFDC Counterfactual Recourse Path in EP-FAP Coordinates", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Dipole Recourse Coordinate $\\xi_{\\mathrm{dipole}}$ (Field Axis $\\mathbf{u}_1$)", fontweight='bold')
    ax1.set_ylabel("Transverse Coordinate $\\xi_{\\perp}$ (Huber Scatter Axis $\\mathbf{u}_2$)", fontweight='bold')
    ax1.legend(loc='lower left', frameon=True, fontsize=9)
    fig.colorbar(cf, ax=ax1, label='Net Potential P(x)')

    # Right: Biomarker Shift Bar Chart
    norm_shifts = feature_shifts[top_indices] / (scaler.scale_[top_indices] + 1e-8)
    b_names = [feature_names[i] for i in top_indices]
    colors = ['#e74c3c' if s < 0 else '#2ecc71' for s in norm_shifts]
    
    bars = ax2.barh(b_names[::-1], norm_shifts[::-1], color=colors[::-1], edgecolor='black')
    ax2.axvline(0, color='black', linewidth=1.2)
    ax2.set_title("Actionable Clinical Adjustments to Reach Benign Safety", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Normalized Feature Adjustment (Standard Deviations)")
    for bar in bars:
        w = bar.get_width()
        x_pos = w + (0.05 if w >= 0 else -0.25)
        ax2.annotate(f"{w:+.2f} σ", (x_pos, bar.get_y() + bar.get_height()/2.), va='center', fontweight='bold', fontsize=9.5)
        
    plt.suptitle("Explainable AI (XAI): Continuous Counterfactual Recourse via Physical Force Fields", fontsize=15, fontweight='bold')
    plt.tight_layout()
    p_path = os.path.join(OUTPUT_DIR, "counterfactual_recourse_trajectory.png")
    plt.savefig(p_path, dpi=300)
    plt.close()
    print(f"Saved Counterfactual Recourse Figure: {p_path}")

if __name__ == "__main__":
    generate_counterfactual_recourse()
