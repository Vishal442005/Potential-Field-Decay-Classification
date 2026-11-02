"""
insert_fig3_docx.py
Inserts Figure 3 into create_pattern_recognition_docx.py.
"""

with open("create_pattern_recognition_docx.py", "r", encoding="utf-8") as f:
    text = f.read()

target = """        if row_idx >= 5:
            for p in row_cells[col_idx].paragraphs:
                for run in p.runs:
                    run.font.bold = True
doc.add_paragraph()"""

replacement = """        if row_idx >= 5:
            for p in row_cells[col_idx].paragraphs:
                for run in p.runs:
                    run.font.bold = True
doc.add_paragraph()

if os.path.exists("figures/real_dataset_stacking_architecture.png"):
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture("figures/real_dataset_stacking_architecture.png", width=Inches(6.5))
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap = p_cap.add_run(
        "Figure 3: Multi-Dimensional Orthogonal Subspace Stacking on Real Clinical Data (Breast Cancer Wisconsin, N=569). "
        "(a) Individual 2D independent variable potential curves P_j(x_j) with learned weights. "
        "(b) Composite 2D overlapped stacking field showing balanced positive (Red) and negative (Blue) potentials, zero separatrix (P=0), and explicit core and decay boundaries (91.81% accuracy, F1: 0.9364). "
        "(c) 3D continuous potential energy landscape of the 2D overlapped stack. "
        "(d) Common-pivot 3D subspace 1 (x1, x2, V1). "
        "(e) Common-pivot 3D subspace 2 (x1, x3, V2). "
        "(f) The Unified Combined 3D Stacked Potential Manifold Phi_net(x) = sum w_k V_k + b (Combined 3D Stack Acc: 87.13%)."
    )
    r_cap.font.italic = True
    r_cap.font.size = Pt(9.5)"""

if target in text:
    text = text.replace(target, replacement, 1)
    with open("create_pattern_recognition_docx.py", "w", encoding="utf-8") as f:
        f.write(text)
    print("Successfully inserted Figure 3 into create_pattern_recognition_docx.py!")
else:
    print("Target not found in create_pattern_recognition_docx.py!")
