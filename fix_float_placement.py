import os
import re

def fix_weights_figure_placement(filepath, is_tpami=False):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    # Pattern to find the figure inside the enumerate
    # Remove the figure from its current position inside the enumerate item
    if is_tpami:
        fig_block = r"""\begin{figure*}[!t]
\centering
\includegraphics[width=0.95\textwidth]{figures/pfdc_highd_learned_weights.png}
\caption{Learned anisotropic metric tensor feature weights $w_j$ in $D=1,000$ dimensions under $\ell_1$ sparsity regularization. The optimizer drives 990 uninformative noise features toward zero ($w_j \to 0$) while boosting informative signal features ($w_j > 1.2$), collapsing the effective intrinsic dimensionality from $D=1,000$ to $d_{\mathrm{eff}} \approx 14.2$.}
\label{fig:weights}
\end{figure*}"""
    else:
        fig_block = r"""\begin{figure}[!htbp]
\centering
\includegraphics[width=0.92\textwidth]{figures/pfdc_highd_learned_weights.png}
\caption{Learned anisotropic metric tensor feature weights $w_j$ in $D=1,000$ dimensions under $\ell_1$ sparsity regularization. The optimizer drives 990 uninformative noise features toward zero ($w_j \to 0$) while boosting informative signal features ($w_j > 1.2$), collapsing the effective intrinsic dimensionality from $D=1,000$ to $d_{\mathrm{eff}} \approx 14.2$.}
\label{fig:weights}
\end{figure}"""

    # Remove any existing fig:weights from inside text
    text = re.sub(r'\\begin\{figure\*?\}\[[^\]]*\].*?\\label\{fig:weights\}.*?\\end\{figure\*?\}', '', text, flags=re.DOTALL)

    # Now place fig_block cleanly right after \end{enumerate} in the highd section
    # Find the enumerate in highd section
    highd_marker = r"\subsection{1,000-Dimensional Scaling & Theoretical Resolution of Measure Concentration}"
    # In tex it is 1,000-Dimensional Scaling \& Theoretical Resolution of Measure Concentration
    if r"\subsection{1,000-Dimensional Scaling \& Theoretical Resolution of Measure Concentration}" in text:
        target_enum_end = r"""    \item \textbf{Additive Potential Decoupling via Subspace Stacking}: As formulated in Section~\ref{sec:subspace_stacking}, PFDC further circumvents high-dimensional volume dilution through Orthogonal Subspace Stacking. By decomposing the joint feature space into 1D and 2D orthogonal potential slices $P_j(x_j)$ and $V_k(x_{\mathrm{pivot}}, x_k)$ and superposing their scalar outputs additively ($P_{\mathrm{composite}} = \sum w_j P_j + b$), the individual potential evaluations operate strictly in low-dimensional domains ($D \in \{1, 2\}$) where measure concentration is mathematically impossible.
\end{enumerate}"""
        
        replacement = target_enum_end + "\n\n" + fig_block

        if target_enum_end in text:
            text = text.replace(target_enum_end, replacement)
        else:
            print(f"Warning: target_enum_end not matched exactly in {filepath}")
    else:
        print(f"Warning: highd_marker not found in {filepath}")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"Fixed float placement in {filepath}")

if __name__ == "__main__":
    fix_weights_figure_placement("PFDC_Manuscript.tex", is_tpami=False)
    fix_weights_figure_placement("elsevier_submission/PFDC_PatternRecognition.tex", is_tpami=False)
    fix_weights_figure_placement("tpami_submission/PFDC_TPAMI.tex", is_tpami=True)
