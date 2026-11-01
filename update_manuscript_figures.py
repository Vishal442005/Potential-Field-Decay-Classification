"""
update_manuscript_figures.py
Integrates the 6 newly generated publication figures into PFDC_Manuscript.tex.
"""

with open('PFDC_Manuscript.tex', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Figure: Radial Chattering Cases
fig_radial = r"""
\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{figures/radial_chattering_cases.png}
\caption{Radial parameter optimization dynamics and asymptotic stability across learning rate schedules. (a) Iteration trajectory $R^{\mathrm{core}}(t)$ showing persistent limit-cycle chattering in Case 1 (119 boundary flips) vs. damped Case 2 (50 flips) vs. exponential quenching in Case 3 (settling in 8 flips). (b) Phase portrait in $(R^{\mathrm{core}}, \dot{R}^{\mathrm{core}})$ parameter space illustrating closed limit cycle attractor (Case 1) vs. Lyapunov inward convergence (Case 3). (c) Cumulative boundary sign flips over optimization epochs. (d) Test loss convergence $\mathcal{L}_{\mathrm{test}}(t)$.}
\label{fig:radial_chattering}
\end{figure*}
"""

# 2. Figure: Ambient Bias Resolution
fig_ambient = r"""
\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{figures/ambient_bias_resolution.png}
\caption{The Ambient DC Ground Bias Trap and Dual Support-Charge Calibration. (a) Latent potential distribution under naive superposition exhibiting $+4.12$ DC ground bias and massive false positive trapping at the zero threshold. (b) Calibrated potential distribution with learned bias $b^*$ and support weights $a_i$ restoring Bayes-optimal separation (accuracy leaps from 70.09\% to 94.29\%). (c) Diagnostic ROC curves and operating point shift. (d) Learned support charge spectrum $|a_i|$ demonstrating emergent sparsity and interior pruning.}
\label{fig:ambient_bias}
\end{figure*}
"""

# 3. Figure: Multi-Class Field Competition
fig_multiclass = r"""
\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{figures/multiclass_field_competition.png}
\caption{Multi-class potential field vector superposition and Boltzmann landscape dynamics. (a) 3-Class potential energy landscape and curved equipotential ridges with central triple-point saddle. (b) Dynamic vector force streamlines showing stable attractor sinks and continuous physics-based recourse trajectory. (c) Softmax-calibrated posterior probability confidence map $P(y=0 \mid \mathbf{x})$.}
\label{fig:multiclass_fields}
\end{figure*}
"""

# 4. Figure: Ball-Tree Geometric Partitioning
fig_balltree = r"""
\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{figures/balltree_geometric_partitioning.png}
\caption{Sub-linear spatial Ball-Tree indexing and compact support horizon pruning. (a) 2D geometric bounding spheres and active search horizon $R^{\mathrm{core}} + R^{\mathrm{decay}}$, showing exterior clusters pruned in $O(1)$ with zero approximation error ($V \equiv 0$). (b) Hierarchical $O(\log N)$ tree pruning traversal bypassing 75\% of nodes. (c) Empirical query latency scaling vs. dataset size $N$ achieving 97.6$\times$ speedup at $N=20,000$ with exact machine precision ($< 10^{-14}$ error).}
\label{fig:balltree_geom}
\end{figure*}
"""

# 5. Figure: Riemannian Manifold Geometries
fig_riemann = r"""
\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{figures/riemannian_manifold_geometries.png}
\caption{Non-Euclidean Riemannian manifold generalizations of potential field classifiers. (a) Hyperspherical manifold $\mathbb{S}^2$ with surface charges and tangent plane projection $(\mathbf{I} - \mathbf{x}\mathbf{x}^T)\mathbf{F}$. (b) Hyperbolic Poincar\'e disk $\mathbb{H}^2$ preserving hierarchical tree structures. (c) Non-Euclidean metric distance divergence preventing boundary collapse and preserving infinite margin capacity.}
\label{fig:riemannian_manifolds}
\end{figure*}
"""

# 6. Figure: Multi-Dataset Overall Radar Profile
fig_radar = r"""
\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{figures/multidataset_overall_radar_profile.png}
\caption{Holistic benchmark radar profile and multi-objective Pareto frontier across 6 real-world datasets. (a) 6-Axis radar chart comparing PFDC vs. SVM, Deep MLP, and Random Forest across accuracy, certified radius, latency, recourse speed, and epistemic calibration. (b) Pareto frontier of clean accuracy vs. adversarial robustness under PGD ($\epsilon=0.35$). (c) Recourse computation latency vs. path length: PFDC continuous streamlines achieve 100$\times$--300$\times$ speedup over iterative optimization.}
\label{fig:overall_radar}
\end{figure*}
"""

# Perform insertions
# 1. After fig:pfdc_2d
target1 = r"\label{fig:pfdc_2d}" + "\n" + r"\end{figure}"
assert target1 in text, "Target 1 not found"
text = text.replace(target1, target1 + "\n" + fig_radial)

# 2. In Dual Support Charges section
target2 = r"\item \textbf{Sonar ($D=60$)}: Rose from \textbf{76.48\% to 81.28\%}, closing the high-dimensional gap." + "\n" + r"\end{itemize}"
assert target2 in text, "Target 2 not found"
text = text.replace(target2, target2 + "\n\nAs visualized in Figure~\\ref{fig:ambient_bias}, learning the ambient bias $b^*$ neutralizes the background potential shift, re-centering the decision boundary at Bayes-optimal separation while pruning interior non-support points." + "\n" + fig_ambient)

# 3. After fig:multiclass
target3 = r"\label{fig:multiclass}" + "\n" + r"\end{figure}"
assert target3 in text, "Target 3 not found"
text = text.replace(target3, target3 + "\n\nFigure~\\ref{fig:multiclass_fields} demonstrates the 3-class potential energy landscape, directional force streamlines, and calibrated Boltzmann posterior probabilities." + "\n" + fig_multiclass)

# 4. After fig:indexing
target4 = r"\label{fig:indexing}" + "\n" + r"\end{figure}"
assert target4 in text, "Target 4 not found"
text = text.replace(target4, target4 + "\n\nFigure~\\ref{fig:balltree_geom} illustrates the spatial bounding ball geometry, search horizon pruning, and hierarchical DAG traversal." + "\n" + fig_balltree)

# 5. In Riemannian Manifold Generalization section
target5 = r"\end{enumerate}" + "\n\n" + r"\section{Conclusion}"
assert target5 in text, "Target 5 not found"
text = text.replace(target5, r"\end{enumerate}" + "\n\n" + r"Figure~\ref{fig:riemannian_manifolds} illustrates the spherical tangent space projection and hyperbolic Poincar\'e disk metric expansion." + "\n" + fig_riemann + "\n\n" + r"Figure~\ref{fig:overall_radar} synthesizes the comprehensive multi-dataset radar profile and Pareto optimality across predictive accuracy, certified robustness, and recourse efficiency." + "\n" + fig_radar + "\n\n" + r"\section{Conclusion}")

with open('PFDC_Manuscript.tex', 'w', encoding='utf-8') as f:
    f.write(text)

print("Successfully updated PFDC_Manuscript.tex with all 6 publication figures!")
