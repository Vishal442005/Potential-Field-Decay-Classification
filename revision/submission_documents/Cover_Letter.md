Prof. Ahmed Begga, Ph.D
Managing Editor, Pattern Recognition
Elsevier Editorial Office

November 9, 2026

SUBJECT: Resubmission of Revised Manuscript Ms. Ref. No.: PR-D-26-16242
Title: "Potential Field Decay Classification (PFDC): Provably Robust Classification via Electrostatic Potential Fields"

Dear Dr. Begga and Editorial Board,

Thank you for the opportunity to revise and resubmit our manuscript, Ms. Ref. No.: PR-D-26-16242, entitled "Potential Field Decay Classification (PFDC): Provably Robust Classification via Electrostatic Potential Fields" for publication as a Regular Paper in Pattern Recognition.

We are deeply grateful to you and the reviewers for the constructive, insightful, and rigorous feedback. We have addressed every comment raised in the editorial evaluation and peer review with absolute diligence. Below, we summarize the major structural, methodological, and formatting revisions implemented:

1. Compliance with Journal Formatting Guidelines:
- Document Class & Spacing: The manuscript is prepared using the official Elsevier template \documentclass[times, review, 10pt]{elsarticle} in single-column, double-spaced format with 10 pt font for the main text.
- Page Count: The revised manuscript is exactly 30 pages, strictly meeting the journal requirement ("longer than 20 pages and does not exceed 35 pages").
- Highlights: Provided as a separate file with 5 concise bullet points, each strictly under the 85-character limit (including spaces).
- Tables & Figures: All 13 tables adhere to standard portrait orientation in booktabs style, with 8-10 pt font, zero vertical rules, and zero cell shading. All 25 flagship figures are placed directly adjacent to their first text citations.
- Editable Equations: All equations are formatted in editable 10 pt text.
- References: Exactly 44 peer-reviewed references are numbered in the order of appearance using the elsarticle-num style, strictly within the 35-55 reference requirement. Recent high-impact contributions from Pattern Recognition and IEEE TPAMI (2020-2024) have been integrated.
- Mandatory Declarations: Included Declarations of Generative AI, Competing Interests, and Data & Code Availability.

2. Comprehensive Resolution of Theoretical and Empirical Questions:
- Certified Adversarial Robustness vs. Gradient Quenching: We rigorously resolved the distinction between gradient masking (Athalye et al., ICML 2018) and certified robustness. Theorem 2 Part 1 provides the universal mathematical certificate r_cert(x) = |P(x)| / L_P derived from global Lipschitz continuity, which holds unconditionally against any zero-order, decision-based, or transfer attack. Theorem 2 Part 2 explains the physical mechanism of core gradient quenching (nabla_x L = 0) against first-order attacks. Table 11 has been updated with genuine certified robust accuracy bounds.
- Clamped Lipschitz Bound: Lemma 1 now rigorously clamps the critical inflection point to the compact decay shell domain: u* = min(1, ((alpha - 1)/(lambda * alpha))^(1/alpha)).
- Data Consistency: All empirical results across all tables, text, and figures are 100% consistent with authentic benchmark CSV logs (Ball-Tree speedup 2.81x at N=10,000; XAI recourse latency 40.96 ms vs. Wachter 206.64 ms; 5-fold CV accuracies; and Ionosphere ambient DC bias Delta V_ambient = -1.84 normalized / +4.12 raw).
- Algorithmic Rigor: Added formal Algorithm 1 Box detailing the Bi-Level Alternating Electrostatic Optimization scheme (inner convex charge optimization + outer Hamiltonian parameter learning).
- Unique Figures & Data Availability: All figures are unique, publication-grade vector graphics. The non-existent placeholder DOI was removed and replaced with the active, public GitHub repository: https://github.com/Vishal442005/Potential-Field-Decay-Classification.

We enclose our detailed, point-by-point Response to Reviewers along with all required submission declarations. We believe this thoroughly revised manuscript fully satisfies the archival standards of Pattern Recognition and provides substantial theoretical and empirical value to the pattern recognition community.

Thank you for your time, consideration, and continued editorial guidance.

Sincerely,

Vishal Chandel (Corresponding Author)
Department of Electronics and Communication Engineering,
Jawaharlal Nehru Government Engineering College Sundernagar, India
Email: chandelvishal445@gmail.com

Riya Kumari (Co-Author)
Department of Electronics and Communication Engineering,
Jawaharlal Nehru Government Engineering College Sundernagar, India

Adarsh Chandel (Co-Author)
Chitkara School of Pharmacy, Chitkara University Punjab, India
Email: aadichandel76@gmail.com
