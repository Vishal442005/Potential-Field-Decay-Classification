with open('PFDC_Manuscript.tex', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Figure 1 (fig:pfdc_2d)
old_fig1 = r"""\begin{figure}[t]
\centering
\includegraphics[width=0.95\linewidth]{figures/pfdc_decision_boundaries_cases.png}
\caption{2D Potential landscapes and directional force fields across dynamic learning-rate schedules.}
\label{fig:pfdc_2d}
\end{figure}"""

new_fig1 = r"""\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{figures/pfdc_decision_boundaries_cases.png}
\caption{PFDC 2D decision partitions and 3D potential energy landscapes across radial learning rate update schedules. (a) Case 1 (Fixed rate: persistent limit-cycle chattering), (b) Case 2 (Sign halving: damped oscillations), (c) Case 3 (Accelerating exponential: settled in 8 sign shifts with 97.22\% accuracy). (d--f) Corresponding 3D continuous scalar potential energy landscapes $P(x_1, x_2)$, illustrating deep negative potential basins (blue) and positive certainty cores (red) intersecting the transparent zero-potential decision plane $z=0$.}
\label{fig:pfdc_2d}
\end{figure*}"""

# 2. Update Figure 11 (fig:multiclass_fields)
old_fig11 = r"""\caption{Multi-class potential field vector superposition and Boltzmann landscape dynamics. (a) 3-Class potential energy landscape and curved equipotential ridges with central triple-point saddle. (b) Dynamic vector force streamlines showing stable attractor sinks and continuous physics-based recourse trajectory. (c) Softmax-calibrated posterior probability confidence map $P(y=0 \mid \mathbf{x})$.}"""

new_fig11 = r"""\caption{Multi-class potential field vector superposition and Boltzmann landscape dynamics. (a) 3D multi-class dominant potential energy landscape $\max_k V_k(\mathbf{x})$ and central triple-point saddle. (b) 2D equipotential ridges and decision partitions between competing class basins. (c) Dynamic vector force streamlines showing stable attractor sinks and continuous physics-based recourse trajectory. (d) Softmax-calibrated posterior probability confidence map $P(y=0 \mid \mathbf{x})$.}"""

# 3. Update Figure 16 (fig:streamlines_portrait)
old_fig16 = r"""\caption{Continuous Neural ODE recourse phase portrait and trajectory dynamics. (a) 2D Phase portrait of conservative recourse vector field $\mathbf{F}(\mathbf{x}) = -\nabla P(\mathbf{x})$ with streamlines colored by velocity magnitude $\|\mathbf{F}\|_2$. (b) Dynamic trajectory comparison: smooth monotonic PFDC physical streamline (RK4) vs. Wachter et al. (2017) non-convex L-BFGS oscillations and excessive Euclidean displacement.}"""

new_fig16 = r"""\caption{Explainable AI (XAI) continuous counterfactual recourse in Electro-Potential Field-Aligned coordinates (EP-FAP). (a) 3D continuous potential energy landscape $P(\xi_1, \xi_2)$ showing smooth streamline ascent from the negative potential basin (blue) into the positive safety core (red) crossing the $z=0$ equipotential plane. (b) 2D Phase portrait of conservative recourse vector field $\mathbf{F}(\mathbf{x}) = -\nabla P(\mathbf{x})$ with streamlines colored by velocity magnitude $\|\mathbf{F}\|_2$. (c) Dynamic trajectory comparison: smooth monotonic PFDC physical streamline (RK4) vs. Wachter et al. (2017) non-convex L-BFGS oscillations and excessive Euclidean displacement.}"""

# Normalizing newlines
text = text.replace(old_fig1, new_fig1)
text = text.replace(old_fig11, new_fig11)
text = text.replace(old_fig16, new_fig16)

with open('PFDC_Manuscript.tex', 'w', encoding='utf-8') as f:
    f.write(text)

print("SUCCESS: Updated captions in PFDC_Manuscript.tex!")
