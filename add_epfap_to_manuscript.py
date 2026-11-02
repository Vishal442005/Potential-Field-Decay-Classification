with open('PFDC_Manuscript.tex', 'r', encoding='utf-8') as f:
    content = f.read()

target = r"achieving guaranteed convergence in \textbf{40.96 ms vs. 206.64 ms (5.0$\times$ faster)} with a 21.4\% reduction in modification distance without encountering local minima."

addition = r"""

\subsection{Robust Electro-Potential Field-Aligned Projection (EP-FAP)}
To inspect high-dimensional ($D \gg 2$) continuous recourse streamlines and potential landscapes visually, conventional machine learning literature predominantly employs Principal Component Analysis (PCA) or unsupervised t-SNE projections. However, standard PCA exhibits severe pathological failure modes in physical field classification:
\begin{enumerate}
    \item \textbf{Field-Blind Variance Maximization}: PCA maximizes unconditional sample variance $\max_{\mathbf{v}} \mathbf{v}^T \boldsymbol{\Sigma} \mathbf{v}$, prioritizing noise features with large variances over the discriminative potential separatrix $\Phi(\mathbf{x}) = 0$.
    \item \textbf{Outlier Brittleness}: Due to quadratic leverage in sample covariance estimation, extreme outliers tilt the principal axes away from the true decision manifold.
    \item \textbf{Distortion of Conservative Flows}: Unsupervised linear projections destroy the directional integrity of the conservative force field $\mathbf{F}(\mathbf{x}) = -\nabla \Phi(\mathbf{x})$, distorting streamline trajectories.
\end{enumerate}

To overcome these fundamental limitations, we completely eliminate PCA and propose the \textbf{Electro-Potential Field-Aligned Projection (EP-FAP)}, an intrinsic, robust 2D physical coordinate frame $(\mathbf{u}_1, \mathbf{u}_2)$ derived directly from the underlying electro-potential geometry:
\begin{itemize}
    \item \textbf{Primary Dipole Recourse Axis ($\mathbf{u}_1$)}: Aligned with the anisotropically weighted difference between robust class spatial medians $\boldsymbol{\mu}_+^{\mathrm{med}}$ and $\boldsymbol{\mu}_-^{\mathrm{med}}$:
    \begin{equation}
        \mathbf{v}_1 = \mathbf{W} (\boldsymbol{\mu}_+^{\mathrm{med}} - \boldsymbol{\mu}_-^{\mathrm{med}}), \quad \mathbf{u}_1 = \frac{\mathbf{v}_1}{\|\mathbf{v}_1\|_2}
    \end{equation}
    The coordinate $\xi_{\mathrm{dipole}} = \mathbf{u}_1^T (\mathbf{x} - \boldsymbol{\mu}_0)$ directly indexes physical displacement along the electrostatic class separation dipole.
    \item \textbf{Transverse Robust Equipotential Axis ($\mathbf{u}_2$)}: Constructed strictly orthogonal to $\mathbf{u}_1$ ($\mathbf{u}_2 \perp \mathbf{u}_1$) via Huber-weighted robust scatter on the projected null space $\mathbf{P}_{\perp} = \mathbf{I} - \mathbf{u}_1 \mathbf{u}_1^T$:
    \begin{equation}
        \mathbf{S}_{\perp} = \mathbf{P}_{\perp} \left( \sum_{i=1}^N \psi_{\mathrm{Huber}}(\|\mathbf{z}_i\|_2) \frac{\mathbf{z}_i \mathbf{z}_i^T}{\|\mathbf{z}_i\|_2^2} \right) \mathbf{P}_{\perp}
    \end{equation}
    where $\mathbf{z}_i = \mathbf{W}^{1/2}(\mathbf{x}_i - \boldsymbol{\mu}_0)$ and $\psi_{\mathrm{Huber}}(r) = \min(1, k/r)$ attenuates heavy-tailed outliers. The second axis $\mathbf{u}_2$ is the leading eigenvector of $\mathbf{S}_{\perp}$.
\end{itemize}
Under EP-FAP, the 2D coordinate transformation $\boldsymbol{\xi} = [\mathbf{u}_1, \mathbf{u}_2]^T (\mathbf{x} - \boldsymbol{\mu}_0)$ forms an exact physical coordinate system where the zero-potential separatrix and conservative force streamlines are preserved without PCA artifacts."""

if target in content:
    content = content.replace(target, target + addition)
    with open('PFDC_Manuscript.tex', 'w', encoding='utf-8') as f:
        f.write(content)
    print('SUCCESS: Updated PFDC_Manuscript.tex with EP-FAP!')
else:
    print('ERROR: Target not found')
