"""
update_stacking_caption_and_docx.py
Updates the caption in PFDC_Manuscript.tex and create_pattern_recognition_docx.py
to describe all 6 panels of Figure 3 accurately.
"""

# Update LaTeX
with open("PFDC_Manuscript.tex", "r", encoding="utf-8") as f:
    tex = f.read()

old_tex_cap = r"""\includegraphics[width=\textwidth]{figures/real_dataset_stacking_architecture.png}
\caption{Multi-dimensional subspace stacking on real clinical data. (a) Individual 2D independent variable potential curves $P_j(x_j)$ with learned variable weights $w_j^*$. (b) Composite 2D overlapped stacking field showing superimposed decision boundary (Test Acc: 91.81\%). (c) Common-pivot 3D subspace 1: $(x_{\mathrm{radius}}, x_{\mathrm{texture}}, P_1)$. (d) Common-pivot 3D subspace 2: $(x_{\mathrm{radius}}, x_{\mathrm{perimeter}}, P_2)$ (Combined 3D Stack Acc: 87.13\%).}
\label{fig:stacking_architecture}"""

new_tex_cap = r"""\includegraphics[width=\textwidth]{figures/real_dataset_stacking_architecture.png}
\caption{Multi-dimensional orthogonal subspace stacking on real clinical data (Breast Cancer Wisconsin, $N=569$). (a) Individual 2D independent variable potential curves $P_j(x_j)$ with learned variable weights $w_j^*$. (b) Composite 2D overlapped stacking field showing both positive (Red) and negative (Blue) potentials, zero separatrix ($P=0$), and explicit positive/negative core ($P = \pm 1.5$) and decay ($P = \pm 0.5$) boundaries (Test Acc: 91.81\%, F1: 0.9364). (c) 3D potential surface of the 2D overlapped stack. (d) Common-pivot 3D subspace 1: $(x_1, x_2, V_1)$. (e) Common-pivot 3D subspace 2: $(x_1, x_3, V_2)$. (f) The Unified Combined 3D Stacked Potential Manifold $\Phi_{\mathrm{net}}(\mathbf{x}) = \sum_{k} w_k V_k + b$ (Combined 3D Stack Acc: 87.13\%).}
\label{fig:stacking_architecture}"""

if old_tex_cap in tex:
    tex = tex.replace(old_tex_cap, new_tex_cap, 1)
    with open("PFDC_Manuscript.tex", "w", encoding="utf-8") as f:
        f.write(tex)
    print("Updated caption in PFDC_Manuscript.tex!")
else:
    print("Old caption not found in PFDC_Manuscript.tex!")

# Update DOCX script
with open("create_pattern_recognition_docx.py", "r", encoding="utf-8") as f:
    docx_code = f.read()

old_docx_cap = 'r_cap = p_cap.add_run("Figure 3: Multi-Dimensional Orthogonal Subspace Stacking on Real Clinical Data (Breast Cancer Wisconsin, N=569). (a) Individual 2D independent variable potential curves P_j(x_j) with learned weights. (b) Composite 2D overlapped stacking field (91.81% accuracy). (c-d) Common-pivot 3D subspace manifolds (87.13% combined accuracy).")'

new_docx_cap = 'r_cap = p_cap.add_run("Figure 3: Multi-Dimensional Orthogonal Subspace Stacking on Real Clinical Data (Breast Cancer Wisconsin, N=569). (a) Individual 2D independent variable potential curves P_j(x_j) with learned weights. (b) Composite 2D overlapped stacking field showing both positive (Red) and negative (Blue) potentials, zero separatrix, and core/decay boundaries (91.81% accuracy, F1: 0.9364). (c) 3D continuous potential energy surface of the 2D overlapped stack. (d) Common-pivot 3D subspace 1 (x1, x2, V1). (e) Common-pivot 3D subspace 2 (x1, x3, V2). (f) The Unified Combined 3D Stacked Potential Manifold Phi_net(x) = sum w_k V_k + b (Combined 3D Stack Acc: 87.13%).")'

if old_docx_cap in docx_code:
    docx_code = docx_code.replace(old_docx_cap, new_docx_cap, 1)
    with open("create_pattern_recognition_docx.py", "w", encoding="utf-8") as f:
        f.write(docx_code)
    print("Updated caption in create_pattern_recognition_docx.py!")
else:
    print("Old docx caption not found!")
