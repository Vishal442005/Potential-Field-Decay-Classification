import re

TABLE_4_REPLACEMENT = r"""\begin{table}[!htbp]
\centering
\small
\caption{Systematic Hyperparameter Sweep Results on Clinical Benchmark Data.}
\label{tab:param_sweeps}
\resizebox{\textwidth}{!}{
\begin{tabular}{lcccc}
\toprule
\textbf{Parameter Swept} & \textbf{Tested Value} & \textbf{Test Accuracy (\%)} & \textbf{F1-Score} & \textbf{Physical Effect / Guarantee} \\
\midrule
Core Ratio ($R^{\mathrm{core}} / R^{\mathrm{decay}}$) & 0.05 & 97.66\% & 0.9811 & Compact core ($r_{\mathrm{cert}} = 0.051$) \\
Core Ratio ($R^{\mathrm{core}} / R^{\mathrm{decay}}$) & \textbf{0.15} & \textbf{97.08\%} & \textbf{0.9763} & \textbf{Optimal certified safety ($r_{\mathrm{cert}} = 0.154$)} \\
Core Ratio ($R^{\mathrm{core}} / R^{\mathrm{decay}}$) & 0.30 & 96.49\% & 0.9717 & Moderate core expansion ($r_{\mathrm{cert}} = 0.307$) \\
Core Ratio ($R^{\mathrm{core}} / R^{\mathrm{decay}}$) & 0.50 & 96.49\% & 0.9717 & Saturated core domain \\
\midrule
Decay Rate ($\lambda$) & 1.0 & 97.66\% & 0.9811 & Diffuse boundary gradient \\
Decay Rate ($\lambda$) & \textbf{2.5} & \textbf{97.08\%} & \textbf{0.9763} & \textbf{Optimal conservative force gradient ($L_I \le 0.96$)} \\
Decay Rate ($\lambda$) & 5.0 & 97.66\% & 0.9811 & Steep step-like falloff \\
\midrule
Support Regularizer ($C$) & 0.10 & 94.74\% & 0.9585 & High sparsity, smooth boundary \\
Support Regularizer ($C$) & \textbf{2.00} & \textbf{97.08\%} & \textbf{0.9763} & \textbf{Optimal margin and charge allocation (63.8\% pruned)} \\
Support Regularizer ($C$) & 10.00 & 96.49\% & 0.9717 & Dense boundary charge retention \\
\midrule
Kernel Blend ($\gamma$) & 0.10 & 97.08\% & 0.9763 & Predominantly RBF tail \\
Kernel Blend ($\gamma$) & \textbf{0.50} & \textbf{97.08\%} & \textbf{0.9763} & \textbf{Equipartition of compact core and tail (2.45$\times$ speedup)} \\
Kernel Blend ($\gamma$) & 1.00 & 95.91\% & 0.9665 & Pure compact support kernel (3.86$\times$ speedup) \\
\bottomrule
\end{tabular}
}
\end{table}"""

TABLE_7_REPLACEMENT = r"""\begin{table}[!htbp]
\centering
\small
\caption{Multi-Field Stratified 5-Fold Cross-Validation Performance (Mean $\pm$ Std \%) Across 4 Diverse Real-World Domains.}
\label{tab:four_fields_acc}
\resizebox{\textwidth}{!}{
\begin{tabular}{lcccccccc}
\toprule
\textbf{Model Architecture} & \multicolumn{2}{c}{\textbf{Financial Security (Banknote, $D=4$)}} & \multicolumn{2}{c}{\textbf{Biomedical Oncology (Cancer, $D=30$)}} & \multicolumn{2}{c}{\textbf{Aerospace Radar (Ionosphere, $D=34$)}} & \multicolumn{2}{c}{\textbf{Marine Geophysics (Sonar, $D=60$)}} \\
\cmidrule(lr){2-3} \cmidrule(lr){4-5} \cmidrule(lr){6-7} \cmidrule(lr){8-9}
& \textbf{Accuracy (\%)} & \textbf{Macro F1} & \textbf{Accuracy (\%)} & \textbf{Macro F1} & \textbf{Accuracy (\%)} & \textbf{Macro F1} & \textbf{Accuracy (\%)} & \textbf{Macro F1} \\
\midrule
\textbf{Dual-Charge PFDC (Ours)} & \textbf{97.23 $\pm$ 1.05\%} & \textbf{0.9698} & \textbf{96.84 $\pm$ 2.12\%} & \textbf{0.9663} & \textbf{94.29 $\pm$ 2.72\%} & \textbf{0.9377} & \textbf{81.28 $\pm$ 4.12\%} & \textbf{0.8016} \\
Kernel SVM (RBF) & 100.00 $\pm$ 0.00\% & 1.0000 & 98.07 $\pm$ 1.79\% & 0.9792 & 94.30 $\pm$ 2.03\% & 0.9369 & 84.13 $\pm$ 4.23\% & 0.8279 \\
XGBoost & 99.49 $\pm$ 0.55\% & 0.9948 & 95.78 $\pm$ 1.02\% & 0.9547 & 92.59 $\pm$ 3.06\% & 0.9176 & 84.66 $\pm$ 6.78\% & 0.8371 \\
LightGBM & 99.49 $\pm$ 0.55\% & 0.9948 & 96.84 $\pm$ 1.43\% & 0.9658 & 94.01 $\pm$ 2.29\% & 0.9334 & 86.59 $\pm$ 6.78\% & 0.8607 \\
Deep MLP & 100.00 $\pm$ 0.00\% & 1.0000 & 97.54 $\pm$ 1.02\% & 0.9734 & 93.44 $\pm$ 2.15\% & 0.9264 & 85.57 $\pm$ 1.52\% & 0.8430 \\
Random Forest & 98.98 $\pm$ 0.54\% & 0.9897 & 95.08 $\pm$ 1.62\% & 0.9472 & 93.44 $\pm$ 1.95\% & 0.9278 & 82.24 $\pm$ 5.51\% & 0.8005 \\
\bottomrule
\end{tabular}
}
\end{table}"""

tex_files = [
    'elsevier_submission/PFDC_PatternRecognition.tex',
    'tpami_submission/PFDC_TPAMI.tex',
    'PFDC_Manuscript.tex'
]

pat4 = r'\\begin\{table\*?\}(?:(?!\\begin\{table\*?\}).)*?\\label\{tab:param_sweeps\}.*?\\end\{table\*?\}'
pat7 = r'\\begin\{table\*?\}(?:(?!\\begin\{table\*?\}).)*?\\label\{tab:four_fields_acc\}.*?\\end\{table\*?\}'

for tf in tex_files:
    with open(tf, 'r', encoding='utf-8') as f:
        c = f.read()

    # Safe replace table 4
    c = re.sub(pat4, lambda m: TABLE_4_REPLACEMENT, c, flags=re.DOTALL)
    # Safe replace table 7
    c = re.sub(pat7, lambda m: TABLE_7_REPLACEMENT, c, flags=re.DOTALL)

    # Harmonize Banknote in text prose if 100.00% appears for PFDC Banknote
    c = c.replace(r"100.00\% on Banknote (tied #1 with Kernel SVM and Deep MLP)", r"97.23 \pm 1.05\% on Banknote (Macro F1: 0.9698)")
    c = c.replace(r"100.00\% on Banknote", r"97.23 \pm 1.05\% on Banknote")
    c = c.replace(r"100.00 \pm 0.00\%", r"97.23 \pm 1.05\%")

    # Limit cycle chatter
    c = c.replace(r'quenching 93.3\% of limit-cycle chatter', r'quenching 89.7\% of limit-cycle chatter (reducing sign shifts from 78 to 8)')
    c = c.replace(r'quenches $93.3\%$ of boundary limit-cycle chattering', r'quenches $89.7\%$ of boundary limit-cycle chattering (reducing sign shifts from 78 to 8)')
    c = c.replace('93.3\\%', '89.7\\%')

    # Boundary flips
    c = c.replace(r'Case 1 (119 boundary flips) vs. damped Case 2 (50 flips)', r'Case 1 (78 boundary flips) vs. damped Case 2 (34 flips)')
    c = c.replace(r'Case 1 (119 shifts)', r'Case 1 (78 shifts)')
    c = c.replace(r'Case 2 (50 shifts)', r'Case 2 (34 shifts)')

    # DC ground shift
    c = c.replace(r'+4.12 DC ground bias and massive false positive trapping', r'-1.84 DC ground shift and false positive trapping')
    c = c.replace(r'+4.12 DC ground bias', r'-1.84 DC ground shift')

    # Sonar Dual-Charge text
    old_sonar_text = r"Dual-Charge PFDC achieving \textbf{76.91 $\pm$ 6.50\% accuracy}"
    new_sonar_text = r"Dual-Charge PFDC achieving \textbf{81.28 $\pm$ 4.12\% accuracy} (up from 76.00\% for isotropic PFDC, Macro F1: 0.8016)"
    c = c.replace(old_sonar_text, new_sonar_text)

    with open(tf, 'w', encoding='utf-8') as f:
        f.write(c)

    tabs = re.findall(r'\\label\{(tab:[^}]+)\}', c)
    figs = re.findall(r'\\label\{(fig:[^}]+)\}', c)
    print(f"Updated {tf}: {len(tabs)} tables, {len(figs)} figures, {len(c.splitlines())} lines")

print("Safe harmonization complete!")
