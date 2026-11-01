"""
create_cover_letter_docx.py
Generates a formal, professional Cover Letter for submission to
Pattern Recognition (Elsevier) in DOCX format.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

doc = Document()

# Margins
for section in doc.sections:
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

normal_style = doc.styles['Normal']
normal_style.font.name = 'Times New Roman'
normal_style.font.size = Pt(11)
normal_style.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
normal_style.paragraph_format.line_spacing = 1.15
normal_style.paragraph_format.space_after = Pt(4)

# Letterhead / Header
p_hdr = doc.add_paragraph()
p_hdr.paragraph_format.space_after = Pt(2)
r_inst = p_hdr.add_run("ADVANCED GRADIENT RESEARCH LABORATORY")
r_inst.font.bold = True
r_inst.font.size = Pt(13)
r_inst.font.color.rgb = RGBColor(0x00, 0x20, 0x60)

p_dept = doc.add_paragraph()
p_dept.paragraph_format.space_after = Pt(16)
r_dept = p_dept.add_run("Department of Computer Science & Artificial Intelligence\nE-mail: vishal.research@gradient.org")
r_dept.font.size = Pt(9.5)
r_dept.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

# Date
p_date = doc.add_paragraph()
p_date.paragraph_format.space_after = Pt(12)
r_date = p_date.add_run("November 1, 2026")
r_date.font.size = Pt(11)

# Recipient
p_rec = doc.add_paragraph()
p_rec.paragraph_format.space_after = Pt(14)
r_rec = p_rec.add_run(
    "Prof. Dr. Edwin Hancock / Prof. Dr. Xiaoou Tang\n"
    "Editors-in-Chief, Pattern Recognition\n"
    "Elsevier B.V., Radarweg 29, 1043 NX Amsterdam, The Netherlands"
)
r_rec.font.size = Pt(11)

# Subject
p_subj = doc.add_paragraph()
p_subj.paragraph_format.space_after = Pt(14)
r_subj_pre = p_subj.add_run("SUBJECT: ")
r_subj_pre.font.bold = True
r_subj_pre.font.color.rgb = RGBColor(0x00, 0x20, 0x60)
r_subj_t = p_subj.add_run("Submission of Original Research Manuscript: \"Potential Field Decay Classification: A Physics-Grounded Machine Learning Paradigm with Certified Certainty Cores, PAC Generalization Bounds, and Continuous Counterfactual Recourse\"")
r_subj_t.font.bold = True

# Salutation
p_sal = doc.add_paragraph()
p_sal.paragraph_format.space_after = Pt(8)
p_sal.add_run("Dear Editors-in-Chief and Editorial Board Members,")

# Body Paragraph 1: Intent & Alignment
p_body1 = doc.add_paragraph()
p_body1.add_run(
    "On behalf of all co-authors, I am delighted to submit our original research manuscript entitled "
    "\"Potential Field Decay Classification: A Physics-Grounded Machine Learning Paradigm with Certified Certainty Cores, "
    "PAC Generalization Bounds, and Continuous Counterfactual Recourse\" for consideration as a Full Research Article in "
    "Elsevier's Pattern Recognition."
)

# Body Paragraph 2: Why Pattern Recognition
p_body2 = doc.add_paragraph()
p_body2.add_run(
    "Pattern Recognition has long served as the premier international venue for seminal breakthroughs in classification methodology, "
    "mathematical pattern modeling, and geometric learning theory. Our work directly engages with the foundational questions of the field: "
    "we challenge the sixty-year-old doctrine of fitting rigid global decision boundaries and instead formulate an electrostatic potential "
    "field paradigm that intrinsically couples predictive classification, certified adversarial robustness, and actionable explainability."
)

# Body Paragraph 3: Core Breakthroughs
p_body3 = doc.add_paragraph()
p_body3.paragraph_format.space_after = Pt(4)
r_core_h = p_body3.add_run("Key Contributions & Highlights of the Manuscript:")
r_core_h.font.bold = True

bullet1 = doc.add_paragraph(style='List Bullet')
r = bullet1.add_run("Physics-Grounded Potential Formulation: ")
r.font.bold = True
bullet1.add_run(
    "We model training instances as localized physical sources radiating concentric dual-zone fields (deterministic certainty core R^core "
    "and exponential decay shell R^decay), eliminating the uncalibrated extrapolation of global hyperplanes."
)

bullet2 = doc.add_paragraph(style='List Bullet')
r = bullet2.add_run("Formal Statistical & Adversarial Guarantees: ")
r.font.bold = True
bullet2.add_run(
    "We prove uniform Lipschitz continuity, establish formal PAC generalization error bounds O(M^{-1/2}) via Rademacher complexity, and prove "
    "a closed-form ℓ₂ certified adversarial invariance theorem guaranteeing 100% immunity within deterministic certainty cores under attacks "
    "where Deep MLPs collapse from 97.08% to 13.45%."
)

bullet3 = doc.add_paragraph(style='List Bullet')
r = bullet3.add_run("Continuous Physical Recourse (Explainable AI): ")
r.font.bold = True
bullet3.add_run(
    "Because the potential field generates a conservative, irrotational force field (∇ × F = 0), counterfactual recourse integrates along "
    "autonomous Neural ODE streamlines, executing 5.0× faster than Wachter's non-convex optimization (40.96 ms vs. 206.64 ms) with 100% convergence."
)

bullet4 = doc.add_paragraph(style='List Bullet')
r = bullet4.add_run("Sub-Linear Spatial Indexing & Real Medium-Scale Workloads: ")
r.font.bold = True
bullet4.add_run(
    "Compact support enables hierarchical spatial Ball-Tree indexing, achieving 3.26× to 97.6× query acceleration with exact machine precision "
    "(< 10⁻¹⁴). On a medium-scale real workload (California Housing, N=20,640), PFDC achieves 83.72% accuracy, remaining competitive with "
    "modern deep tabular architectures (TabNet 84.59%, FT-Transformer 86.87%)."
)

bullet5 = doc.add_paragraph(style='List Bullet')
r = bullet5.add_run("Frank & Creative Critical Discussion: ")
r.font.bold = True
bullet5.add_run(
    "We provide an unvarnished, creative critical discussion explaining that as a nascent paradigm, PFDC's accuracy trade-off is the natural "
    "and deliberate price paid for certifiable robustness and transparent physical recourse."
)

# Declarations
p_dec = doc.add_paragraph()
p_dec.paragraph_format.space_before = Pt(6)
p_dec.add_run(
    "We confirm that this manuscript is original, has not been published previously, and is not currently under consideration for publication "
    "elsewhere. All authors have critically reviewed and approved the manuscript for submission. There are no competing financial or commercial "
    "conflicts of interest associated with this work."
)

# Suggested Reviewers
p_rev_h = doc.add_paragraph()
p_rev_h.paragraph_format.space_before = Pt(6)
p_rev_h.paragraph_format.space_after = Pt(2)
r_rev_h = p_rev_h.add_run("Suggested Expert Reviewers:")
r_rev_h.font.bold = True

revs = [
    "1. Prof. Dr. J. Zico Kolter (Carnegie Mellon University) — Expert in certified adversarial robustness and convex optimization.",
    "2. Prof. Dr. Ricky T.Q. Chen / David Duvenaud (University of Toronto) — Experts in Neural Ordinary Differential Equations and continuous dynamical learning.",
    "3. Dr. Sercan Ö. Arik (Google Cloud AI Research) — Expert in tabular deep learning, attention architectures, and interpretability (creator of TabNet)."
]
for rv in revs:
    p_rv = doc.add_paragraph(style='List Bullet')
    p_rv.add_run(rv)

# Sign-off
p_close = doc.add_paragraph()
p_close.paragraph_format.space_before = Pt(10)
p_close.add_run("Thank you very much for your time, consideration, and editorial stewardship.\n\nSincerely,")

p_sig = doc.add_paragraph()
p_sig.paragraph_format.space_before = Pt(12)
r_sig = p_sig.add_run("Vishal, Lead Researcher\nOn behalf of all co-authors\nAdvanced Gradient Research Laboratory\nE-mail: vishal.research@gradient.org")
r_sig.font.bold = True

output_cover = "Cover_Letter_Pattern_Recognition.docx"
doc.save(output_cover)
print(f"Successfully generated Elsevier Pattern Recognition Cover Letter: {output_cover}")
