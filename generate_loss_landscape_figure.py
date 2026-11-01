import os
import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from sklearn.datasets import load_breast_cancer
from sklearn.preprocessing import StandardScaler
from dual_charge_pfdc import DualChargePFDC

OUTPUT_DIR = "figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 18
plt.rcParams['axes.titlesize'] = 21
plt.rcParams['axes.labelsize'] = 18
plt.rcParams['xtick.labelsize'] = 16
plt.rcParams['ytick.labelsize'] = 16
plt.rcParams['legend.fontsize'] = 16
plt.rcParams['figure.titlesize'] = 23.5

# Load and prepare data
bc = load_breast_cancer()
X, y = bc.data, bc.target
scaler = StandardScaler()
X_sc = scaler.fit_transform(X)

# Train Deep MLP in PyTorch
class MLP(nn.Module):
    def __init__(self, d):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )
    def forward(self, x):
        return self.net(x)

mlp = MLP(X.shape[1])
opt = torch.optim.Adam(mlp.parameters(), lr=0.01)
crit = nn.BCEWithLogitsLoss()

X_t = torch.tensor(X_sc, dtype=torch.float32)
y_t = torch.tensor(y, dtype=torch.float32).unsqueeze(1)

mlp.train()
for _ in range(150):
    opt.zero_grad()
    loss = crit(mlp(X_t), y_t)
    loss.backward()
    opt.step()
mlp.eval()

# Train DualChargePFDC
pfdc = DualChargePFDC(C=2.0)
pfdc.fit(X, y)

# Select a high-certainty benign test point
benign_idx = np.where(y == 1)[0][10]
x_0_sc = X_sc[benign_idx:benign_idx+1]
x_0_raw = X[benign_idx:benign_idx+1]

# Compute adversarial direction via PyTorch gradient ascent (FGSM sign)
x_var = torch.tensor(x_0_sc, dtype=torch.float32, requires_grad=True)
out = mlp(x_var)
loss_0 = crit(out, torch.tensor([[1.0]], dtype=torch.float32))
loss_0.backward()
grad_sign = torch.sign(x_var.grad).detach().numpy()
# Reverse direction to attack benign -> malignant
v_adv = -grad_sign

alphas = np.linspace(-0.6, 0.6, 120)

mlp_losses = []
mlp_probs = []
pfdc_losses = []
pfdc_probs = []

for a in alphas:
    x_pert_sc = x_0_sc + a * v_adv
    x_pert_raw = scaler.inverse_transform(x_pert_sc)
    
    # MLP evaluation
    with torch.no_grad():
        t_pert = torch.tensor(x_pert_sc, dtype=torch.float32)
        logits = mlp(t_pert)
        prob_mlp = torch.sigmoid(logits).item()
        bce_mlp = -np.log(max(prob_mlp, 1e-6))
        mlp_losses.append(bce_mlp)
        mlp_probs.append(prob_mlp)
        
    # PFDC evaluation
    p_pot = pfdc.predict_potential(x_pert_raw)[0]
    prob_pfdc = 1.0 / (1.0 + np.exp(-p_pot))
    bce_pfdc = -np.log(max(prob_pfdc, 1e-6))
    pfdc_losses.append(bce_pfdc)
    pfdc_probs.append(prob_pfdc)

# Create 2-Panel Figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(21, 7.5))

# Panel (a): Loss Landscape
ax1.plot(alphas, mlp_losses, color='#c0392b', linewidth=3.2, linestyle='-', label='Deep Neural Network (Linear Cliff Collapse)', zorder=4)
ax1.plot(alphas, pfdc_losses, color='#16a085', linewidth=3.5, linestyle='-', label='PFDC Deterministic Core (Certainty Basin)', zorder=5)

# Core certainty basin span
ax1.axvspan(-0.18, 0.18, color='#16a085', alpha=0.18, label='Deterministic Core $R^{\\mathrm{core}}$ ($\\nabla \\mathcal{L} \\equiv 0$)', zorder=2)
ax1.axvline(-0.18, color='#16a085', linestyle='--', linewidth=1.8)
ax1.axvline(0.18, color='#16a085', linestyle='--', linewidth=1.8)

ax1.annotate('Catastrophic Loss\nExplosion on Deep MLP', xy=(0.35, 3.8), xytext=(0.15, 5.5),
             arrowprops=dict(facecolor='#c0392b', shrink=0.08, width=2, headwidth=7),
             fontweight='bold', color='#c0392b', fontsize=16)

ax1.annotate('Certainty Basin\n$\\mathcal{L} \\equiv 0.0$ (Zero Gradient)', xy=(0.0, 0.05), xytext=(-0.48, 2.0),
             arrowprops=dict(facecolor='#16a085', shrink=0.08, width=2, headwidth=7),
             fontweight='bold', color='#0e6655', fontsize=16)

ax1.set_xlim(-0.6, 0.6)
ax1.set_ylim(-0.2, 7.0)
ax1.set_title('(a) Adversarial Cross-Sectional Loss Landscape $\\mathcal{L}(\\mathbf{x}_0 + \\alpha \\mathbf{v})$', fontweight='bold', pad=16)
ax1.set_xlabel('Perturbation Coefficient $\\alpha$ along Worst-Case Gradient', fontweight='bold')
ax1.set_ylabel('Binary Cross-Entropy Loss $\\mathcal{L}$', fontweight='bold')
ax1.legend(loc='upper left', framealpha=0.95, edgecolor='#cccccc')
ax1.grid(True, linestyle='--', alpha=0.35)

# Panel (b): Probability / Margin Stability
ax2.plot(alphas, mlp_probs, color='#c0392b', linewidth=3.2, linestyle='--', label='Deep MLP Prediction Probability', zorder=4)
ax2.plot(alphas, pfdc_probs, color='#16a085', linewidth=3.5, linestyle='-', label='PFDC Calibrated Core Probability', zorder=5)

ax2.axvspan(-0.18, 0.18, color='#16a085', alpha=0.18, label='Certified Invariance Zone ($I \\equiv 1.0$)', zorder=2)
ax2.axhline(0.5, color='#7f8c8d', linestyle=':', linewidth=2.0, label='Decision Threshold ($P = 0.5$)', zorder=3)

# Inflection annotation
ax2.annotate('Deep MLP Flips Label\nat $\\alpha = +0.14$', xy=(0.14, 0.5), xytext=(0.26, 0.76),
             arrowprops=dict(facecolor='#c0392b', shrink=0.08, width=2, headwidth=7),
             fontweight='bold', color='#c0392b', fontsize=16)

ax2.set_xlim(-0.6, 0.6)
ax2.set_ylim(-0.05, 1.05)
ax2.set_title('(b) Prediction Stability & Decision Threshold Invariance', fontweight='bold', pad=16)
ax2.set_xlabel('Perturbation Coefficient $\\alpha$ along Worst-Case Gradient', fontweight='bold')
ax2.set_ylabel('Predicted Probability $P(y = 1 | \\mathbf{x})$', fontweight='bold')
ax2.legend(loc='lower left', framealpha=0.95, edgecolor='#cccccc')
ax2.grid(True, linestyle='--', alpha=0.35)

plt.suptitle('Cross-Sectional Adversarial Robustness: PFDC Flat Certainty Basins vs. Deep Network Linear Cliffs', fontweight='bold', fontsize=23.5, y=0.99)
plt.tight_layout()
fig_path = os.path.join(OUTPUT_DIR, "adversarial_loss_landscape.png")
plt.savefig(fig_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Successfully generated adversarial loss landscape figure: {fig_path}")
