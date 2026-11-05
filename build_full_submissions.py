import os
import re

# 1. Read base manuscript
with open("PFDC_Manuscript.tex", "r", encoding="utf-8") as f:
    orig_text = f.read()

# Extract from Section 2 onwards
sec2_idx = orig_text.find(r"\section{Mathematical Formulation}")
body = orig_text[sec2_idx:]

# Remove bibliography from body
bib_idx = body.find(r"\bibliographystyle")
if bib_idx != -1:
    body_core = body[:bib_idx].strip()
else:
    body_core = body.strip()

# Clean up end of document if present
body_core = re.sub(r'\\end\{document\}', '', body_core).strip()

# Apply requested section title changes
body_core = body_core.replace(
    r"\section{Frank Limitations \& Creative Critical Discussion}",
    r"\section{Limitations and Discussion}"
)
body_core = body_core.replace(
    r"\section{Future Directions \& Theoretical Outlook}",
    r"\section{Future Directions}"
)

# Also ensure FloatBarriers are placed before sections
sections_to_barrier = [
    r"\section{Mathematical Formulation}",
    r"\section{Statistical Learning Theory \& Certified Robustness}",
    r"\section{Closed-Form Gradients \& Optimization Schedules}",
    r"\section{Parametric Specification and Hamiltonian-Annealed Electrostatic Optimization (HAEPO)}",
    r"\section{Experimental Evaluation}",
    r"\section{Theoretical Riemannian Manifold Projections}",
    r"\section{Limitations and Discussion}",
    r"\section{Future Directions}",
    r"\section{Conclusion}"
]

for sec in sections_to_barrier:
    body_core = body_core.replace(sec, r"\FloatBarrier" + "\n\n" + sec)

# Also add FloatBarrier at key subsections in Section 6 to prevent queuing
subsecs_to_barrier = [
    r"\subsection{Multi-Field Empirical Benchmark Across Diverse Real-World Domains}",
    r"\subsection{Certified Adversarial Robustness vs. Deep MLP Collapse}",
    r"\subsection{Medium-Scale Tabular Benchmark \& Modern Baselines (TabNet, FT-Transformer)}",
    r"\subsection{Head-to-Head Explainable AI (XAI) Recourse Benchmark}"
]

for sub in subsecs_to_barrier:
    body_core = body_core.replace(sub, r"\FloatBarrier" + "\n\n" + sub)

# Import Expanded Introduction from generate_submission_files
from generate_submission_files import EXPANDED_INTRO

# =========================================================================
# BUILD ELSEVIER PATTERN RECOGNITION LATEX
# =========================================================================
elsevier_body = body_core
# In elsarticle (single column review format), convert figure* and table* to figure and table with [!htbp]
elsevier_body = elsevier_body.replace(r"\begin{figure*}[t]", r"\begin{figure}[!htbp]")
elsevier_body = elsevier_body.replace(r"\begin{figure*}[!t]", r"\begin{figure}[!htbp]")
elsevier_body = elsevier_body.replace(r"\end{figure*}", r"\end{figure}")
elsevier_body = elsevier_body.replace(r"\begin{figure}[t]", r"\begin{figure}[!htbp]")
elsevier_body = elsevier_body.replace(r"\begin{figure}[h]", r"\begin{figure}[!htbp]")

elsevier_body = elsevier_body.replace(r"\begin{table*}[t]", r"\begin{table}[!htbp]")
elsevier_body = elsevier_body.replace(r"\begin{table*}[!t]", r"\begin{table}[!htbp]")
elsevier_body = elsevier_body.replace(r"\end{table*}", r"\end{table}")
elsevier_body = elsevier_body.replace(r"\begin{table}[t]", r"\begin{table}[!htbp]")
elsevier_body = elsevier_body.replace(r"\begin{table}[h]", r"\begin{table}[!htbp]")

# Adjust figures widths for elsarticle review layout
elsevier_body = elsevier_body.replace(r"\includegraphics[width=\textwidth]", r"\includegraphics[width=0.92\textwidth]")

elsevier_tex = r"""\documentclass[preprint,review,12pt]{elsarticle}

\usepackage{amsmath,amssymb,amsfonts,amsthm}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{algorithm}
\usepackage{algorithmic}
\usepackage{color}
\usepackage{subcaption}
\usepackage{microtype}
\usepackage{hyperref}
\usepackage{cite}
\usepackage{lineno}
\usepackage{placeins}

\journal{Pattern Recognition}

\newtheorem{theorem}{Theorem}
\newtheorem{lemma}{Lemma}
\newtheorem{definition}{Definition}
\newtheorem{corollary}{Corollary}

\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    citecolor=blue,
    urlcolor=blue
}

% Generous float placement parameters to keep floats inline with text
\renewcommand{\topfraction}{0.95}
\renewcommand{\bottomfraction}{0.90}
\renewcommand{\textfraction}{0.05}
\renewcommand{\floatpagefraction}{0.70}
\setcounter{topnumber}{4}
\setcounter{bottomnumber}{3}
\setcounter{totalnumber}{6}

\begin{document}

\begin{frontmatter}

\title{\textbf{Potential Field Decay Classification (PFDC): A Physics-Grounded Machine Learning Paradigm with Certified Certainty Cores, PAC Generalization Bounds, and Continuous Counterfactual Recourse}}

\author{Research Team\corref{cor1}}
\ead{research@gradientlab.org}
\cortext[cor1]{Corresponding author.}
\affiliation{organization={Department of Computer Science and Machine Learning, Gradient Research Laboratory},
            city={Cambridge},
            country={USA}}

\begin{abstract}
Traditional supervised classification algorithms focus on constructing global decision boundaries---hyperplanes or orthogonal partitions that divide feature space into discrete regions. Inside these boundaries, predictions are static, models lack native mechanisms to quantify directional certainty, and representations are vulnerable to adversarial perturbations. In this paper, we reverse this paradigm and propose \textbf{Potential Field Decay Classification (PFDC)}, an interpretable machine learning framework inspired by physical electrostatics. In PFDC, every training point acts as a localized radial energy source defined by a dual-zone profile: an inner deterministic core zone ($R^{\mathrm{core}}$) of absolute local certainty ($1.0$), transitioning into an exponential decay shell ($R^{\mathrm{decay}}$) that gracefully tapers to zero. Opposing classes radiate inverted polarity charges, yielding an organic superposition of scalar potentials and continuous directional force fields ($\mathbf{F}(\mathbf{x}) = -\nabla P(\mathbf{x})$).

We establish the foundational statistical learning theory of PFDC, proving a formal \textbf{PAC Generalization Bound} via Rademacher complexity $\mathcal{O}(M^{-1/2})$, and prove a \textbf{Certified Adversarial Invariance Theorem} guaranteeing that points within $R^{\mathrm{core}}$ maintain 100\% mathematical immunity against $\ell_2$ perturbations. To eliminate boundary-crossing limit cycles during optimization, we introduce an \textbf{Accelerating Exponential Learning-Rate Schedule (Case 3)}, quenching 93.3\% of limit-cycle chatter. Addressing high-dimensional hyperspherical measure concentration, we formulate \textbf{Dual Support Charge Learning} and \textbf{Anisotropic Metric Tensors} ($d_{\mathbf{w}}$) for automated feature selection.

Empirical evaluation demonstrates that PFDC achieves \textbf{97.22\% accuracy in 2D} (\#1 rank, defeating XGBoost, Deep MLP, and Kernel SVM), and outperforms LightGBM (72.80\%) and XGBoost (72.00\%) in \textbf{1,000 dimensions with 75.87\% accuracy}. On real-world benchmarks, Dual-Charge PFDC achieves \textbf{96.84\% on Breast Cancer} (outperforming XGBoost 95.78\%) and \textbf{94.29\% on Ionosphere} (outperforming Deep MLP 92.01\%). In adversarial benchmarks, PFDC cores preserve \textbf{100.0\% certified invariance} under attacks where Deep MLP accuracy collapses to 13.45\%. In spatial tree indexing, PFDC achieves \textbf{$\mathcal{O}(\log N)$ query scaling} (2.81$\times$ faster than brute force and 3.8$\times$ faster than SVM at $N=10,000$). Finally, head-to-head Explainable AI benchmarks prove that PFDC's curl-free force streamlines generate clinical counterfactual recourse paths \textbf{5.0$\times$ faster than Wachter's non-convex optimization} with guaranteed convergence.
\end{abstract}

\begin{keyword}
Potential Field Decay Classification \sep Certified Adversarial Robustness \sep Certainty Basins \sep Explainable AI \sep Counterfactual Recourse \sep Hamiltonian Annealing \sep Spatial Ball-Tree
\end{keyword}

\end{frontmatter}

\linenumbers

""" + EXPANDED_INTRO + "\n\n" + elsevier_body + r"""

\bibliographystyle{elsarticle-num}
\bibliography{references}

\end{document}
"""

with open(os.path.join("elsevier_submission", "PFDC_PatternRecognition.tex"), "w", encoding="utf-8") as f:
    f.write(elsevier_tex)
print("Successfully wrote elsevier_submission/PFDC_PatternRecognition.tex")

# =========================================================================
# BUILD IEEE TPAMI LATEX
# =========================================================================
tpami_body = body_core
# In IEEEtran (two-column), keep figure* and table* for wide floats spanning both columns
# Single-column figures should be [width=\columnwidth] or [width=0.98\columnwidth]
tpami_body = tpami_body.replace(r"\includegraphics[width=0.88\linewidth]", r"\includegraphics[width=\columnwidth]")
tpami_body = tpami_body.replace(r"\includegraphics[width=0.92\linewidth]", r"\includegraphics[width=\columnwidth]")

tpami_tex = r"""\documentclass[10pt,journal,compsoc]{IEEEtran}

\usepackage{amsmath,amssymb,amsfonts,amsthm}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{algorithm}
\usepackage{algorithmic}
\usepackage{subcaption}
\usepackage{microtype}
\usepackage{hyperref}
\usepackage{cite}
\usepackage{placeins}
\usepackage{textcomp}
\usepackage{xcolor}

\newtheorem{theorem}{Theorem}
\newtheorem{lemma}{Lemma}
\newtheorem{definition}{Definition}
\newtheorem{corollary}{Corollary}

\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    citecolor=blue,
    urlcolor=blue
}

% Generous float placement parameters
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

We establish the foundational statistical learning theory of PFDC, proving a formal \textbf{PAC Generalization Bound} via Rademacher complexity $\mathcal{O}(M^{-1/2})$, and prove a \textbf{Certified Adversarial Invariance Theorem} guaranteeing that points within $R^{\mathrm{core}}$ maintain 100\% mathematical immunity against $\ell_2$ perturbations. To eliminate boundary-crossing limit cycles during optimization, we introduce an \textbf{Accelerating Exponential Learning-Rate Schedule (Case 3)}, quenching 93.3\% of limit-cycle chatter. Addressing high-dimensional hyperspherical measure concentration, we formulate \textbf{Dual Support Charge Learning} and \textbf{Anisotropic Metric Tensors} ($d_{\mathbf{w}}$) for automated feature selection.

Empirical evaluation demonstrates that PFDC achieves \textbf{97.22\% accuracy in 2D} (\#1 rank, defeating XGBoost, Deep MLP, and Kernel SVM), and outperforms LightGBM (72.80\%) and XGBoost (72.00\%) in \textbf{1,000 dimensions with 75.87\% accuracy}. On real-world benchmarks, Dual-Charge PFDC achieves \textbf{96.84\% on Breast Cancer} (outperforming XGBoost 95.78\%) and \textbf{94.29\% on Ionosphere} (outperforming Deep MLP 92.01\%). In adversarial benchmarks, PFDC cores preserve \textbf{100.0\% certified invariance} under attacks where Deep MLP accuracy collapses to 13.45\%. In spatial tree indexing, PFDC achieves \textbf{$\mathcal{O}(\log N)$ query scaling} (2.81$\times$ faster than brute force and 3.8$\times$ faster than SVM at $N=10,000$). Finally, head-to-head Explainable AI benchmarks prove that PFDC's curl-free force streamlines generate clinical counterfactual recourse paths \textbf{5.0$\times$ faster than Wachter's non-convex optimization} with guaranteed convergence.
\end{abstract}

\begin{IEEEkeywords}
Potential field classification, certified adversarial robustness, certainty basins, explainable AI, counterfactual recourse, Hamiltonian annealing, spatial Ball-Tree indexing.
\end{IEEEkeywords}}

\maketitle

\IEEEdisplaynontitleabstractindextext
\IEEEpeerreviewmaketitle

""" + EXPANDED_INTRO + "\n\n" + tpami_body + r"""

\bibliographystyle{IEEEtran}
\bibliography{references}

\end{document}
"""

with open(os.path.join("tpami_submission", "PFDC_TPAMI.tex"), "w", encoding="utf-8") as f:
    f.write(tpami_tex)
print("Successfully wrote tpami_submission/PFDC_TPAMI.tex")
