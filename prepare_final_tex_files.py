import os
import re

# 1. Read base PFDC_Manuscript.tex
with open("PFDC_Manuscript.tex", "r", encoding="utf-8") as f:
    base_tex = f.read()

# Verify that PFDC_Manuscript.tex has tab:1000d and fig:weights
assert r"\label{tab:1000d}" in base_tex, "tab:1000d missing from PFDC_Manuscript.tex"
assert r"\label{fig:weights}" in base_tex, "fig:weights missing from PFDC_Manuscript.tex"
assert r"\label{sec:adversarial_bench}" in base_tex, "sec:adversarial_bench missing"
assert "97.23" in base_tex, "Banknote 97.23% missing from PFDC_Manuscript.tex"

print("PFDC_Manuscript.tex verified! Size:", len(base_tex))

# 2. Prepare elsevier_submission/PFDC_PatternRecognition.tex
els_tex = base_tex.replace(
    r"\textit{Research Manuscript --- Gradient Research Laboratory}",
    r"\textit{Preprint submitted to Elsevier Pattern Recognition}"
)
with open("elsevier_submission/PFDC_PatternRecognition.tex", "w", encoding="utf-8") as f:
    f.write(els_tex)
print("elsevier_submission/PFDC_PatternRecognition.tex written successfully.")

# 3. Prepare tpami_submission/PFDC_TPAMI.tex
# Extract body from base_tex starting from Section 2
sec2_idx = base_tex.find(r"\section{Mathematical Formulation}")
body = base_tex[sec2_idx:]
bib_idx = body.find(r"\bibliographystyle")
if bib_idx != -1:
    body_core = body[:bib_idx].strip()
else:
    body_core = body.strip()
body_core = re.sub(r'\\end\{document\}', '', body_core).strip()

# Adjust floats for IEEEtran 2-column format:
# In IEEEtran, convert wide 2-column floats to figure* and table*
# fig:weights should be figure*
body_tpami = body_core.replace(
    r"\begin{figure}[!htbp]" + "\n" + r"\centering" + "\n" + r"\includegraphics[width=0.92\textwidth]{figures/pfdc_highd_learned_weights.png}",
    r"\begin{figure*}[!t]" + "\n" + r"\centering" + "\n" + r"\includegraphics[width=0.95\textwidth]{figures/pfdc_highd_learned_weights.png}"
).replace(
    r"\label{fig:weights}" + "\n" + r"\end{figure}",
    r"\label{fig:weights}" + "\n" + r"\end{figure*}"
)

# tab:1000d should use \columnwidth
body_tpami = body_tpami.replace(
    r"\caption{1,000-Dimensional Stress Benchmark ($N=2,500, D=1,000$, 10 Informative Signal Features, 990 Noise Features).}" + "\n" + r"\label{tab:1000d}" + "\n" + r"\resizebox{\textwidth}{!}{",
    r"\caption{1,000-Dimensional Stress Benchmark ($N=2,500, D=1,000$, 10 Informative Signal Features, 990 Noise Features).}" + "\n" + r"\label{tab:1000d}" + "\n" + r"\resizebox{\columnwidth}{!}{"
)

# Other wide figures in IEEEtran to figure*
wide_figs = [
    "figures/pfdc_architecture_overview.png",
    "figures/multidimensional_2d_stacking_architecture.png",
    "figures/real_dataset_stacking_architecture.png",
    "figures/haepo_learning_dynamics.png",
    "figures/pfdc_decision_boundaries_cases.png",
    "figures/radial_chattering_cases.png",
    "figures/four_fields_multi_domain_benchmark.png",
    "figures/multiclass_field_competition.png",
    "figures/adversarial_loss_landscape.png",
    "figures/fast_indexing_speedup.png",
    "figures/medium_scale_scaling_comparison.png",
    "figures/balltree_geometric_partitioning.png",
    "figures/xai_streamlines_phase_portrait.png",
    "figures/riemannian_manifold_geometries.png"
]

for wf in wide_figs:
    body_tpami = body_tpami.replace(
        r"\begin{figure}[!htbp]" + "\n" + r"\centering" + "\n" + f"\\includegraphics[width=0.92\\textwidth]{{{wf}}}",
        r"\begin{figure*}[!t]" + "\n" + r"\centering" + "\n" + f"\\includegraphics[width=0.95\\textwidth]{{{wf}}}"
    )

body_tpami = re.sub(
    r'(\\includegraphics\[width=0\.95\\textwidth\]\{[^\}]+\}\s*\\caption\{[^\}]+\}\s*\\label\{[^\}]+\}\s*)\\end\{figure\}',
    r'\1\\end{figure*}',
    body_tpami
)

# Wide tables to table*
wide_tables = [
    r"\label{tab:paradigm_differentiation}",
    r"\label{tab:four_fields_acc}",
    r"\label{tab:four_fields_lat}",
    r"\label{tab:multidataset_6}",
    r"\label{tab:adversarial}",
    r"\label{tab:spatial_accel}",
    r"\label{tab:california_housing}",
    r"\label{tab:xai}"
]

for wt in wide_tables:
    body_tpami = body_tpami.replace(
        r"\begin{table}[!htbp]" + "\n" + r"\centering" + "\n" + r"\small" + "\n" + wt,
        r"\begin{table*}[!t]" + "\n" + r"\centering" + "\n" + r"\small" + "\n" + wt
    )
    body_tpami = body_tpami.replace(
        r"\begin{table}[!htbp]" + "\n" + r"\centering" + "\n" + wt,
        r"\begin{table*}[!t]" + "\n" + r"\centering" + "\n" + wt
    )

from generate_submission_files import EXPANDED_INTRO

# Adjust EXPANDED_INTRO for TPAMI: Table 1 to table*
intro_tpami = EXPANDED_INTRO.replace(
    r"\begin{table}[!htbp]" + "\n" + r"\centering" + "\n" + r"\small" + "\n" + r"\caption{Architectural & Theoretical Differentiation: PFDC vs. Prior Decision Paradigms.}" + "\n" + r"\label{tab:paradigm_differentiation}",
    r"\begin{table*}[!t]" + "\n" + r"\centering" + "\n" + r"\small" + "\n" + r"\caption{Architectural & Theoretical Differentiation: PFDC vs. Prior Decision Paradigms.}" + "\n" + r"\label{tab:paradigm_differentiation}"
).replace(
    r"\bottomrule" + "\n" + r"\end{tabular}" + "\n" + r"}" + "\n" + r"\end{table}",
    r"\bottomrule" + "\n" + r"\end{tabular}" + "\n" + r"}" + "\n" + r"\end{table*}"
)

tpami_full_tex = r"""\documentclass[10pt,journal,compsoc]{IEEEtran}

\usepackage{amsmath,amssymb,amsfonts,amsthm}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{algorithm}
\usepackage{algorithmic}
\usepackage{subcaption}
\usepackage{microtype}
\usepackage{hyperref}
\usepackage{cite}
\usepackage{textcomp}
\usepackage{xcolor}

\newtheorem{theorem}{Theorem}
\newtheorem{lemma}{Lemma}
\newtheorem{definition}{Definition}
\newtheorem{corollary}{Corollary}

\makeatletter
\newcommand{\FloatBarrier}{\clearpage}
\makeatother

\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    citecolor=blue,
    urlcolor=blue
}

\renewcommand{\topfraction}{0.95}
\renewcommand{\dbltopfraction}{0.95}
\renewcommand{\bottomfraction}{0.90}
\renewcommand{\textfraction}{0.05}
\renewcommand{\floatpagefraction}{0.70}
\renewcommand{\dblfloatpagefraction}{0.70}
\setcounter{topnumber}{4}
\setcounter{bottomnumber}{3}
\setcounter{totalnumber}{6}
\setcounter{dbltopnumber}{4}

\begin{document}

\title{Potential Field Decay Classification (PFDC): A Physics-Grounded Machine Learning Paradigm with Certified Certainty Cores, PAC Generalization Bounds, and Continuous Counterfactual Recourse}

\author{Research~Team,
        Department of Computer Science and Machine Learning,
        Gradient Research Laboratory%
\IEEEcompsocitemizethanks{\IEEEcompsocthanksitem Research Team is with the Gradient Research Laboratory, Cambridge, MA, USA. E-mail: research@gradientlab.org.}%
}

\markboth{IEEE Transactions on Pattern Analysis and Machine Intelligence}%
{Research Team: Potential Field Decay Classification (PFDC)}

\IEEEtitleabstractindextext{%
\begin{abstract}
Traditional supervised classification algorithms focus on constructing global decision boundaries---hyperplanes or orthogonal partitions that divide feature space into discrete regions. Inside these boundaries, predictions are static, models lack native mechanisms to quantify directional certainty, and representations are vulnerable to adversarial perturbations. In this paper, we reverse this paradigm and propose \textbf{Potential Field Decay Classification (PFDC)}, an interpretable machine learning framework inspired by physical electrostatics. In PFDC, every training point acts as a localized radial energy source defined by a dual-zone profile: an inner deterministic core zone ($R^{\mathrm{core}}$) of absolute local certainty ($1.0$), transitioning into an exponential decay shell ($R^{\mathrm{decay}}$) that gracefully tapers to zero. Opposing classes radiate inverted polarity charges, yielding an organic superposition of scalar potentials and continuous directional force fields ($\mathbf{F}(\mathbf{x}) = -\nabla P(\mathbf{x})$).

We establish the foundational statistical learning theory of PFDC, proving a formal \textbf{PAC Generalization Bound} via Rademacher complexity $\mathcal{O}(M^{-1/2})$, and prove a \textbf{Certified Adversarial Invariance Theorem} guaranteeing that points within $R^{\mathrm{core}}$ maintain 100\% mathematical immunity against $\ell_2$ perturbations by creating Certainty Basins ($\nabla_{\mathbf{x}} \mathcal{L} \equiv \mathbf{0}$) that starve gradient-directed adversaries of torque. To eliminate boundary-crossing limit cycles during optimization, we introduce an \textbf{Accelerating Exponential Learning-Rate Schedule (Case 3)}, quenching 93.3\% of limit-cycle chatter. To overcome hyperspherical measure concentration in high dimensions, we formulate \textbf{Dual Support Charge Learning}, \textbf{Anisotropic Metric Tensors} ($d_{\mathbf{w}}$), and \textbf{Multi-Dimensional Orthogonal Subspace Stacking}.

Empirical evaluation demonstrates that PFDC achieves \textbf{97.22\% accuracy in 2D} (\#1 rank, defeating XGBoost, Deep MLP, and Kernel SVM), and outperforms LightGBM (72.80\%) and XGBoost (72.00\%) in \textbf{1,000 dimensions with 75.87\% accuracy} by collapsing intrinsic dimensionality to $d_{\mathrm{eff}} \approx 14.2$. Across real-world benchmarks, Dual-Charge PFDC achieves competitive clean accuracy: \textbf{97.23 $\pm$ 1.05\% on Banknote} (Macro F1: 0.9698), \textbf{96.84 $\pm$ 2.12\% on Breast Cancer} (matching LightGBM 96.84\%, beating XGBoost 95.78\%, while trailing Kernel SVM 98.07\% and Deep MLP 97.54\%), and \textbf{94.29 $\pm$ 2.72\% on Ionosphere} (statistically matching Kernel SVM 94.30\%, beating Deep MLP 93.44\% and XGBoost 92.59\%). On medium-scale tabular data (California Housing, $N=20,640$), PFDC achieves \textbf{83.72\% accuracy}, remaining competitive with modern deep tabular architectures (TabNet 84.59\%, FT-Transformer 86.87\%). Crucially, under adversarial attacks where Deep MLP accuracy collapses from 97.08\% to 13.45\%, PFDC certainty cores preserve \textbf{100.0\% certified invariance}. In spatial indexing, PFDC achieves \textbf{$\mathcal{O}(\log N)$ query scaling} (2.81$\times$ faster than brute force and 3.8$\times$ faster than SVM at $N=10,000$). Finally, head-to-head Explainable AI benchmarks prove that PFDC's curl-free force streamlines generate clinical counterfactual recourse paths \textbf{5.0$\times$ faster than Wachter's non-convex optimization} with guaranteed convergence.
\end{abstract}

\begin{IEEEkeywords}
Potential field classification, certified adversarial robustness, certainty basins, explainable AI, counterfactual recourse, Hamiltonian annealing, spatial Ball-Tree indexing.
\end{IEEEkeywords}}

\maketitle

\IEEEdisplaynontitleabstractindextext
\IEEEpeerreviewmaketitle

""" + intro_tpami + "\n\n" + body_tpami + r"""

\bibliographystyle{IEEEtran}
\bibliography{references}

\end{document}
"""

with open("tpami_submission/PFDC_TPAMI.tex", "w", encoding="utf-8") as f:
    f.write(tpami_full_tex)
print("tpami_submission/PFDC_TPAMI.tex written successfully. Size:", len(tpami_full_tex))
