"""
update_restyle_remaining_full.py
Updates restyle_and_scale_remaining.py with:
- Compact canvas dimensions (13.0 to 15.5 inches width)
- Two-line subplot titles
- Generous wspace (0.30-0.34) and hspace (0.36-0.40)
- Suptitle y=0.985
"""

import re

with open("restyle_and_scale_remaining.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update GLOBAL_RC
old_rc = """GLOBAL_RC = {
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial'],
    'font.size': 25,
    'axes.labelsize': 27,
    'axes.titlesize': 29,
    'xtick.labelsize': 22,
    'ytick.labelsize': 22,
    'legend.fontsize': 22,
    'figure.titlesize': 34
}"""

new_rc = """GLOBAL_RC = {
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial'],
    'font.size': 12.5,
    'axes.labelsize': 13.5,
    'axes.titlesize': 14.5,
    'xtick.labelsize': 11.5,
    'ytick.labelsize': 11.5,
    'legend.fontsize': 10.5,
    'figure.titlesize': 16.0
}"""
code = code.replace(old_rc, new_rc)

# 2. Update figsizes
code = re.sub(r"figsize=\(20,\s*15\.5\)", "figsize=(13.5, 8.8)", code)
code = re.sub(r"figsize=\(24,\s*8\.0\)", "figsize=(15.5, 4.8)", code)
code = re.sub(r"figsize=\(24,\s*12\.0\)", "figsize=(13.5, 8.8)", code)
code = re.sub(r"figsize=\(22,\s*8\.0\)", "figsize=(13.0, 4.8)", code)
code = re.sub(r"figsize=\(22,\s*9\.0\)", "figsize=(13.0, 4.8)", code)
code = re.sub(r"figsize=\(22,\s*16\.0\)", "figsize=(13.5, 8.8)", code)

# 3. Update titles
title_replacements = [
    # 1. Ambient Bias
    ("'(a) Naive Superposition: The Ambient DC Ground Bias Trap'", "'(a) Naive Superposition:\\nAmbient Ground Bias Trap'"),
    ("'(b) Dual-Charge Calibration: Learned Ground Bias $b^*$ & Weights $a_i$'", "'(b) Dual-Charge Calibration:\\nLearned Bias $b^*$ & Weights $a_i$'"),
    ("'(c) Diagnostic ROC Separation & Operating Point Shift'", "'(c) Diagnostic ROC Separation\\n& Operating Point Shift'"),
    ("r'(d) Learned Support Charge Spectrum $|a_i|$: Emergent Sparsity'", "r'(d) Support Charge Spectrum:\\nEmergent Sparsity $|a_i|$'"),
    
    # 2. Radial Chattering
    ("r'(a) Core Radius Trajectories $R^{\\mathrm{core}}(t)'", "r'(a) Core Radius Trajectories\\n$R^{\\mathrm{core}}(t)$ Across Laws'"),
    ("r'(b) Phase Portrait: Trajectory in $(R^{\\mathrm{core}}, \\dot{R}^{\\mathrm{core}})$ Space'", "r'(b) Phase Portrait: $(R^{\\mathrm{core}}, \\dot{R}^{\\mathrm{core}})$\\nState Space Trajectory'"),
    ("'(c) Cumulative Boundary Sign Flips vs Epoch'", "'(c) Cumulative Boundary Flips\\nvs. Optimization Epoch'"),
    ("r'(d) Test Loss Convergence: $\\mathcal{L}_{\\mathrm{test}}(t)$ Under Gradient Flow'", "r'(d) Test Loss Convergence $\\mathcal{L}(t)$\\nUnder Gradient Flow'"),

    # 3. Balltree
    ("'(a) Compact Support Horizon & Bounding Balls'", "'(a) Support Horizon &\\nBounding Spheres'"),
    ("'(b) Hierarchical $O(\\log N)$ Tree Pruning'", "'(b) Hierarchical $O(\\log N)$\\nTree Pruning Traversal'"),
    ("'(c) Empirical Query Latency vs Scale $N$'", "'(c) Empirical Query Latency\\nvs. Dataset Size $N$'"),

    # 4. Radar
    ("'(a) Multi-Objective Radar Profile'", "'(a) 6-Axis Holistic Benchmark\\nRadar Performance Profile'"),
    ("r'(b) Clean Acc vs Robustness ($\\epsilon=0.35$)'", "r'(b) Clean Acc vs Robustness\\nPareto Frontier ($\\epsilon=0.35$)'"),
    ("'(c) XAI Recourse: Latency vs Path Length'", "'(c) Recourse Efficiency:\\nLatency vs. Geodesic Path'"),

    # 5. Multiclass
    ("'(a) Multi-Class Potential Field Landscape'", "'(a) Multi-Class Potential\\nDominant Field $\\max_k V_k$'"),
    ("'(b) Dynamic Vector Field Streamlines'", "'(b) Dynamic Force Vector\\nStreamlines & Attractors'"),
    ("r'(c) Softmax Posterior Confidence $P(y = 0 \\mid \\mathbf{x})$'", "r'(c) Softmax Posterior\\nConfidence $P(y = 0 \\mid \\mathbf{x})$'"),

    # 6. Riemannian
    ("'(a) Hyperspherical Manifold $\\mathbb{S}^2$'", "'(a) Hyperspherical Space $\\mathbb{S}^2$\\nTangent Plane Projection'"),
    ("r'(b) Hyperbolic Disk $\\mathbb{H}^2$ (Poincaré Model)'", "r'(b) Hyperbolic Poincaré $\\mathbb{H}^2$\\nHierarchical Tree Sinks'"),
    ("'(c) Geodesic Separation Divergence'", "'(c) Distance Metric Divergence\\nPreserving Margin Capacity'"),

    # 7. Architecture Overview
    ("'(a) Traditional Boundary-Partitioning (Global Risk)'", "'(a) Traditional Boundaries:\\nUncalibrated Far-Field Risk'"),
    ("r'(b) Dual-Zone Influence Profile $I(d)'", "r'(b) Dual-Zone Profile:\\nDeterministic Core & Decay'"),
    ("'(c) Multi-Charge Energy Landscape $P(\\mathbf{x})'", "'(c) 3D Potential Energy:\\nCharge Superposition'"),
    ("r'(d) Conservative Recourse Vector Field $\\mathbf{F}(\\mathbf{x})'", "r'(d) Conservative Force Field:\\nRecourse Streamline Flow'"),

    # 8. Loss Landscape
    ("r'(a) Cross-Sectional Loss Landscape $\\mathcal{L}(\\mathbf{x}_0 + \\alpha \\mathbf{v})'", "r'(a) Loss Landscape $\\mathcal{L}(\\mathbf{x}_0 + \\alpha \\mathbf{v})$\\nAlong Worst-Case Gradient'"),
    ("r'Perturbation Step $\\alpha$ along Worst-Case Gradient Direction $\\mathbf{v}'", "r'Perturbation Step $\\alpha$'"),
    ("r'(b) Prediction Stability Across Adversarial Perturbation $\\alpha$'", "r'(b) Prediction Stability Across\\nPerturbation Magnitude $\\alpha$'"),

    # 9. Certified Radius
    ("r'(a) Certified Accuracy vs. Perturbation Radius $r$ ($\\ell_2$ Space)'", "r'(a) Certified Accuracy vs. Radius\\nProvable Bound ($r \\leq R^{\\mathrm{core}}$)'"),
    ("r'$\\ell_2$ Perturbation Radius $r$ (Normalized Feature Units)'", "r'Perturbation Radius $r$ ($\\ell_2$ Units)'"),
    ("r'(b) Empirical Distribution of Certified Safety Margins'", "r'(b) Empirical CDF of Certified\\nSafety Margins $r_{\\mathrm{cert}}(\\mathbf{x})$'"),

    # 10. XAI Streamlines
    ("'(a) Continuous Energy Landscape'", "'(a) Continuous Energy Landscape\\nStreamline Ascent Across $P=0$'"),
    ("'(b) Dynamic Vector Field Phase Portrait'", "'(b) Force Field Phase Portrait\\n& Recourse Streamlines'"),

    # 11. Stacking
    ("'(a) 2D Subspace Potential Slices'", "'(a) 2D Subspace Potential\\nElliptical Contour Slices'"),
    ("'(b) Volumetric Stacking Along Dimensions'", "'(b) Volumetric Stacking Along\\nHigher Dimensions $(D > 2)$'"),
    ("'(c) Learned Metric Tensor Stretching'", "'(c) Metric Tensor Stretching:\\nPruning Noise Dimensions'"),
    ("r'(d) Conservative Superposition of Forces $\\mathbf{F}(\\mathbf{x})'", "r'(d) Superposition of Forces\\nConservative Vector Sum'")
]

for old_t, new_t in title_replacements:
    code = code.replace(old_t, new_t)

# 4. Replace suptitle and tight_layout patterns with subplots_adjust
# Replace tight_layout(rect=[0, 0, 1, 0.9X]) or tight_layout()
code = re.sub(r"plt\.suptitle\(([^,]+),\s*fontsize=[0-9\.]+,\s*fontweight='bold',\s*y=[0-9\.]+\)\nplt\.tight_layout\([^\)]*\)",
              r"plt.suptitle(\1, fontsize=16, fontweight='bold', y=0.985)\nplt.subplots_adjust(left=0.08, right=0.96, bottom=0.10, top=0.89, wspace=0.30, hspace=0.38)", code)

code = re.sub(r"plt\.suptitle\(([^,]+),\s*fontsize=[0-9\.]+,\s*fontweight='bold',\s*y=[0-9\.]+\)\nplt\.tight_layout\(\)",
              r"plt.suptitle(\1, fontsize=16, fontweight='bold', y=0.985)\nplt.subplots_adjust(left=0.08, right=0.96, bottom=0.13, top=0.87, wspace=0.30)", code)

with open("restyle_and_scale_remaining.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Successfully updated restyle_and_scale_remaining.py with clean layouts!")
