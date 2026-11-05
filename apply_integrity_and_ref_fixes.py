import re
import os

def update_tex_file(filepath, is_tpami=False):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    # 1. Update Banknote numbers in Abstract
    # Replace "100.00% on Banknote (tied #1 with Kernel SVM and Deep MLP)"
    # with "97.23 \pm 1.05% on Banknote (Macro F1: 0.9698)"
    text = re.sub(
        r'\\textbf\{100\.00\\% on Banknote\}\s*\([^\)]*Kernel SVM and Deep MLP\)',
        r'\\textbf{97.23 $\\pm$ 1.05\\% on Banknote} (Macro F1: 0.9698)',
        text
    )
    text = re.sub(
        r'100\.00% on Banknote\s*\([^\)]*Kernel SVM and Deep MLP\)',
        r'97.23 $\\pm$ 1.05% on Banknote (Macro F1: 0.9698)',
        text
    )

    # 2. Update Banknote in Section 6.5 (Four Fields bullet list)
    old_banknote_bullet = (
        r"\\item \\textbf\{Financial Security \(Banknote, \$D=4\$\)\}: "
        r"Dual-Charge PFDC achieves \\textbf\{100\.00 \\pm 0\.00\\% accuracy\} \(Macro F1: 1\.0000\), "
        r"tying for \\#1 rank with Kernel SVM \(100\.00\\%\) and Deep MLP \(100\.00\\%\), "
        r"while outperforming modern tree ensembles \(XGBoost 99\.49 \\pm 0\.55\\%, LightGBM 99\.49 \\pm 0\.55\\%, Random Forest 98\.98 \\pm 0\.54\\%\)\."
    )
    new_banknote_bullet = (
        r"\\item \\textbf{Financial Security (Banknote, $D=4$)}: "
        r"On continuous wavelet features, standard infinite-margin Kernel SVM and overparameterized Deep MLP achieve 100.00\% empirical test separation. "
        r"In contrast, Dual-Charge PFDC optimizes localized radial potential shells with finite compact support, achieving \\textbf{97.23 $\\pm$ 1.05\\% accuracy} (Macro F1: 0.9698), "
        r"outperforming standard linear margins while trailing global kernel models on this cleanly separable 4D benchmark. "
        r"Crucially, whereas Kernel SVM and Deep MLP exhibit zero certified adversarial invariance, PFDC provides non-vacuous certainty cores ($r_{\\mathrm{core}} > 0$) where predictions are provably immune to gradient manipulation."
    )
    text = re.sub(old_banknote_bullet, new_banknote_bullet, text)

    # 3. Update Table tab:four_fields_acc row for PFDC
    text = text.replace(
        r"\textbf{Dual-Charge PFDC (Ours)} & \textbf{100.00 $\pm$ 0.00\%} & \textbf{1.0000}",
        r"\textbf{Dual-Charge PFDC (Ours)} & \textbf{97.23 $\pm$ 1.05\%} & \textbf{0.9698}"
    )

    # 4. Insert Table tab:1000d and Figure fig:weights in Section highd_scaling
    # Check if tab:1000d is already defined
    if r"\label{tab:1000d}" not in text:
        if is_tpami:
            table_1000d_latex = r"""
\begin{table}[!htbp]
\centering
\caption{1,000-Dimensional Stress Benchmark ($N=2,500, D=1,000$, 10 Signal Features, 990 Noise Features).}
\label{tab:1000d}
\resizebox{\columnwidth}{!}{
\begin{tabular}{lcccc}
\toprule
\textbf{Model Architecture} & \textbf{Paradigm} & \textbf{Test Acc (\%)} & \textbf{Macro F1} & \textbf{BCE Loss} \\
\midrule
Kernel SVM (RBF) & Global Kernel & 85.47\% & 0.8575 & 0.3172 \\
Deep MLP (PyTorch) & Deep Network & 81.73\% & 0.8181 & 0.5974 \\
\textbf{Anisotropic PFDC (Ours)} & \textbf{Weighted Potential} & \textbf{75.87\%} & \textbf{0.7735} & \textbf{0.5263} \\
Isotropic PFDC (Ours) & Unweighted Potential & 74.80\% & 0.7629 & 0.5485 \\
LightGBM (v4.7.0) & Tree Boosting & 72.80\% & 0.7323 & 0.5315 \\
XGBoost (v3.2.0) & Tree Boosting & 72.00\% & 0.7207 & 0.5373 \\
Random Forest (100 Trees) & Tree Ensemble & 70.27\% & 0.7108 & 0.6460 \\
Logistic Regression ($\ell_2$) & Linear Margin & 64.53\% & 0.6509 & 2.8932 \\
\bottomrule
\end{tabular}
}
\end{table}
"""
            fig_weights_latex = r"""
\begin{figure*}[!t]
\centering
\includegraphics[width=0.95\textwidth]{figures/pfdc_highd_learned_weights.png}
\caption{Learned anisotropic metric tensor feature weights $w_j$ in $D=1,000$ dimensions under $\ell_1$ sparsity regularization. The optimizer drives 990 uninformative noise features toward zero ($w_j \to 0$) while boosting informative signal features ($w_j > 1.2$), collapsing the effective intrinsic dimensionality from $D=1,000$ to $d_{\mathrm{eff}} \approx 14.2$.}
\label{fig:weights}
\end{figure*}
"""
        else:
            table_1000d_latex = r"""
\begin{table}[!htbp]
\centering
\small
\caption{1,000-Dimensional Stress Benchmark ($N=2,500, D=1,000$, 10 Informative Signal Features, 990 Noise Features).}
\label{tab:1000d}
\resizebox{\textwidth}{!}{
\begin{tabular}{lccccc}
\toprule
\textbf{Model Architecture} & \textbf{Paradigm} & \textbf{Test Accuracy (\%)} & \textbf{Macro F1} & \textbf{BCE Loss} & \textbf{Fit Time (s)} \\
\midrule
Kernel SVM (RBF) & Global Kernel & 85.47\% & 0.8575 & 0.3172 & 4.34 s \\
Deep MLP (PyTorch) & Deep Network & 81.73\% & 0.8181 & 0.5974 & 2.10 s \\
\textbf{Anisotropic PFDC (Ours)} & \textbf{Weighted Potential} & \textbf{75.87\%} & \textbf{0.7735} & \textbf{0.5263} & 52.51 s \\
Isotropic PFDC (Ours) & Unweighted Potential & 74.80\% & 0.7629 & 0.5485 & 24.30 s \\
LightGBM (v4.7.0) & Tree Boosting & 72.80\% & 0.7323 & 0.5315 & 2.33 s \\
XGBoost (v3.2.0) & Tree Boosting & 72.00\% & 0.7207 & 0.5373 & 3.97 s \\
Random Forest (100 Trees) & Tree Ensemble & 70.27\% & 0.7108 & 0.6460 & 1.97 s \\
Logistic Regression ($\ell_2$) & Linear Margin & 64.53\% & 0.6509 & 2.8932 & 0.57 s \\
\bottomrule
\end{tabular}
}
\end{table}
"""
            fig_weights_latex = r"""
\begin{figure}[!htbp]
\centering
\includegraphics[width=0.92\textwidth]{figures/pfdc_highd_learned_weights.png}
\caption{Learned anisotropic metric tensor feature weights $w_j$ in $D=1,000$ dimensions under $\ell_1$ sparsity regularization. The optimizer drives 990 uninformative noise features toward zero ($w_j \to 0$) while boosting informative signal features ($w_j > 1.2$), collapsing the effective intrinsic dimensionality from $D=1,000$ to $d_{\mathrm{eff}} \approx 14.2$.}
\label{fig:weights}
\end{figure}
"""
        target_str = "ranking #1 ahead of all competing models." if "ranking #1 ahead of all competing models." in text else "ranking \\#1 ahead of all competing models."
        if target_str in text:
            text = text.replace(target_str, target_str + "\n" + table_1000d_latex)

        target_str_fig = "This collapses the effective intrinsic dimension:"
        if target_str_fig in text:
            text = text.replace(target_str_fig, target_str_fig + "\n" + fig_weights_latex)

    # 5. Fix sec:adversarial_bench label
    if r"\label{sec:adversarial_bench}" not in text:
        text = text.replace(
            r"\subsection{Certified Adversarial Robustness vs. Deep MLP Collapse}",
            r"\subsection{Certified Adversarial Robustness vs. Deep MLP Collapse}" + "\n" + r"\label{sec:adversarial_bench}"
        )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"Updated {filepath} successfully.")

def update_cover_letters():
    for cl in ["tpami_submission/cover_letter_tpami.tex", "elsevier_submission/cover_letter_pattern_recognition.tex"]:
        if os.path.exists(cl):
            with open(cl, 'r', encoding='utf-8') as f:
                c = f.read()
            c = c.replace("100.00% on Banknote", "97.23% on Banknote")
            with open(cl, 'w', encoding='utf-8') as f:
                f.write(c)
            print(f"Updated cover letter: {cl}")

if __name__ == "__main__":
    update_tex_file("PFDC_Manuscript.tex", is_tpami=False)
    update_tex_file("elsevier_submission/PFDC_PatternRecognition.tex", is_tpami=False)
    update_tex_file("tpami_submission/PFDC_TPAMI.tex", is_tpami=True)
    update_cover_letters()
