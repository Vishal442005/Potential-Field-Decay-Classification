# Point-by-Point Response to Editor and Reviewers
**Manuscript Reference:** PR-D-26-16242  
**Title:** Potential Field Decay Classification (PFDC): Provably Robust Classification via Electrostatic Potential Fields  
**Journal:** *Pattern Recognition*, Elsevier  
**Authors:** Vishal Chandel, Adarsh Chandel  

---

Dear Dr. Ahmed Begga, Managing Editor, and Reviewers,

We express our sincere gratitude for your thorough, constructive, and rigorous review of our manuscript **PR-D-26-16242**. We have carefully revised the manuscript in accordance with all editorial formatting guidelines and detailed peer review feedback. 

Below is our comprehensive, point-by-point response detailing every change made, along with exact section, equation, and page references in the revised 34-page manuscript.

---

## PART I: RESPONSE TO MANAGING EDITOR'S COMMENTS

### Comment 1 (Formatting & Document Class):
> *"Please revise your manuscript to comply with the journal’s formatting guidelines. In particular, note the following requirements: The manuscript (including abstract and references) must be prepared in single-column, double-spaced format and the main text font size must be 10 pt. Please use the Elsevier template available at: https://mirrors.ctan.org/macros/latex/contrib/elsarticle.zip and set: `\documentclass[times, review, 10pt]{elsarticle}`"*

**Response:**
We have formatted the entire manuscript strictly using `\documentclass[times, review, 10pt]{elsarticle}` in single-column, double-spaced format with 10 pt Times New Roman font. All font sizes, baseline skips, and margins strictly conform to official Elsevier guidelines.

### Comment 2 (Page Count Constraints):
> *"Please ensure that a Regular Paper is longer than 20 pages and does not exceed 35 pages when correcting the manuscript format. The page count excludes other requested documents such as Highlights, Author Biographies, and the Declaration of Interest."*

**Response:**
The revised manuscript is exactly **34 pages** in the compiled review format, strictly satisfying the requirement of being longer than 20 pages and not exceeding 35 pages ($20 < 34 \le 35$). All auxiliary documents (Highlights, Cover Letter, Declarations) are provided as separate standalone documents.

### Comment 3 (Highlights Constraints):
> *"Highlights should consist of 3 to 5 bullet points, each a maximum of 85 characters, including spaces."*

**Response:**
We have provided 5 concise highlights, each strictly verified to be under 85 characters including spaces:
1. `Potential Field Decay Classification unifies core certainty with radial decay.` (78 chars)
2. `Certified L2 margin robustness prevents adversarial prediction label flips.` (75 chars)
3. `Accelerating learning rate quenches 89.7% of boundary chattering flips.` (71 chars)
4. `Hierarchical spatial Ball-Tree indexing achieves sub-linear O(log N) runtime.` (77 chars)
5. `Conservative force streamlines deliver 5.0x faster counterfactual recourse.` (75 chars)

### Comment 4 (Tables and Figures Formatting):
> *"The font size in tables must be 10 pt (minimum 8 pt). Please avoid vertical rules and shading in table cells. Also, avoid landscape or rotated tables and keep tables in the standard portrait layout when correcting them. The font size in footnotes, author names, affiliations, and figure/table captions must be 8 pt. Figures, diagrams, and tables must be placed in the text close to where they are first referenced."*

**Response:**
All 12 tables in the revised manuscript:
- Are set in standard portrait layout in clean `booktabs` format.
- Strictly avoid vertical rules (zero `|` characters) and avoid all cell shading.
- Use 8–10 pt font sizes (`\small` and `\footnotesize`).
- Are placed immediately adjacent to their textual citations in the manuscript body.
- All captions and footnotes are set to 8 pt font via `\usepackage[font=footnotesize,labelfont=bf]{caption}`.

### Comment 5 (Reference Count & Numbering):
> *"The number of references ranges from 35 to 55 for a regular paper. References must be numbered in the order of appearance in the text."*

**Response:**
The bibliography has been expanded to exactly **44 references**, strictly within the 35–55 range. All references are cited and numbered sequentially in order of appearance using `\bibliographystyle{elsarticle-num}`. We have enriched the literature review with high-impact 2020–2024 publications from *Pattern Recognition*, *IEEE TPAMI*, *ICML*, and *NeurIPS*.

### Comment 6 (Mandatory Declarations):
> *"Declaration of use/non-use Generative AI at any stage of manuscript preparation is mandatory. Upload Declaration of competing interests using the tool available at https://declarations.elsevier.com/."*

**Response:**
We have included both mandatory declarations prominently in the manuscript (Section 10) and provided separate signed declaration documents in `submission_documents/`.

---

## PART II: RESPONSE TO REVIEWER 2'S TECHNICAL COMMENTS

### Comment 1 (Removal of Non-Existent Zenodo DOI & Code Availability):
> *"Just like the first manuscript, the title page and Data and Code Availability section state: 'Permanent Research Archive DOI: https://doi.org/10.5281/zenodo.23936990'. Zenodo record IDs in the 239xxxxx range do not exist. Submitting a fake or unminted placeholder DOI is an immediate trigger for an administrative Desk Reject. Mint an actual Zenodo archive or remove the link and ensure GitHub is live and public."*

**Response:**
We sincerely apologize for the placeholder DOI string. We have completely excised all references to the placeholder Zenodo DOI. The Data and Code Availability section (Section 10) and title page now exclusively link to our active, public GitHub repository containing all source code, automated test suites, and data processing scripts:
`https://github.com/Vishal442005/Potential-Field-Decay-Classification`

### Comment 2 (Certified Robustness vs. Gradient Masking / Obfuscation):
> *"Fundamental Mathematical Flaw in the '100% Certified Adversarial Invariance' Claim (Theorem 2, Table 11, Fig. 16): Gradient Masking / Obfuscation != Certified Robustness. In Section 1.3.1 (Eqs. 2–3) and Section 6.7, you argue that because nabla_x P = 0 inside the core, the gradient vanishes, 'guaranteeing 100% certified robustness'. In adversarial ML (Athalye et al., ICML 2018), having nabla_x L = 0 is gradient masking, NOT certified robustness! Certified robustness means no perturbation with ||delta||_2 <= epsilon can change the classification. Contradiction in Table 11 & Figure 16: You state R_core = 0.35, yet PFDC Core Invariance stays 100.00% at epsilon = 0.50, 0.75, 1.50 while overall accuracy drops. If epsilon > R_core, points are pushed completely outside the core!"*

**Response:**
We thank Reviewer 2 for this critical and mathematically rigorous correction. We have completely restructured our adversarial robustness formulation in Section 4.3 (Theorem 2), Section 7.6, Table 8, and Figure 9:
1. **Delineation of Gradient Quenching vs. Certified Robustness:** We explicitly cite Athalye et al. (ICML 2018) and clarify that vanishing gradients ($\nabla_{\mathbf{x}} \mathcal{L} \equiv \mathbf{0}$) inside certainty cores represent first-order gradient quenching rather than universal robustness. We prove that while gradient quenching deprives first-order adversaries (FGSM, PGD) of directional torque, it does not constitute a certified robustness guarantee against arbitrary attacks.
2. **Universal Lipschitz Margin Certification (Theorem 2 Part 1):** We established the universal certified robustness guarantee strictly via the Lipschitz margin:
   $$r_{\mathrm{cert}}(\mathbf{x}) \triangleq \frac{|P(\mathbf{x})|}{L_P}$$
   where $L_P = L_I \sqrt{w_{\max}} \sum_{i=1}^N a_i$ is the global Lipschitz constant of the potential field. We prove that for any perturbation $\|\boldsymbol{\delta}\|_2 \le r_{\mathrm{cert}}(\mathbf{x})$, the sign $\hat{y}(\mathbf{x}+\boldsymbol{\delta}) \equiv \hat{y}(\mathbf{x})$ is unconditionally guaranteed against ANY attack.
3. **Table 8 & Figure 9 Correction:** We removed the flawed "100% Core Invariance" column. Table 8 now reports the true certified robust accuracy ($r_{\mathrm{cert}}(\mathbf{x}) \ge \varepsilon$) monotonically decreasing with $\varepsilon$:
   - $\varepsilon = 0.00$: $97.08\%$
   - $\varepsilon = 0.05$: $94.15\%$
   - $\varepsilon = 0.10$: $88.89\%$
   - $\varepsilon = 0.20$: $78.36\%$
   - $\varepsilon = 0.35$: $57.31\%$
   - $\varepsilon = 0.50$: $38.01\%$
   - $\varepsilon = 0.75$: $17.54\%$
   - $\varepsilon = 1.00$: $8.19\%$
   - $\varepsilon = 1.50$: $2.34\%$
   This certified curve forms a provable lower bound on empirical PGD accuracy, fully resolving the mathematical contradiction.

### Comment 3 (Clamping Lemma 1 Inflection Point):
> *"In Lemma 1, the stationary point of the derivative is given as u* = ((alpha - 1)/(lambda * alpha))^(1/alpha). But if lambda * alpha < alpha - 1, u* > 1, which lies outside the decay shell domain [0, 1]."*

**Response:**
We have revised Lemma 1 (Section 4.1, Eqs. 20–21) to explicitly clamp the critical point to the compact domain:
$$u^* = \min\left(1, \; \left(\frac{\alpha - 1}{\lambda \alpha}\right)^{1/\alpha}\right)$$
We included the complete proof demonstrating that when $\lambda \alpha < \alpha - 1$, $g'(u) > 0$ across the entire interval $[0, 1]$, such that the derivative increases monotonically and attains its global maximum at the outer boundary $u = 1$.

### Comment 4 (Force Field Normalization Factor):
> *"Equation 9 for the continuous force field F(x) = -nabla P(x) is missing the normalization factor (1 - exp(-lambda)) from the kernel denominator."*

**Response:**
We have updated Eq. 18 and all analytical gradient equations (Eqs. 28–30) to include the exact normalization factor $(1 - \exp(-\lambda))$ in the denominator:
$$\mathbf{F}(\mathbf{x}) = \sum_{i=1}^N q_i \cdot \frac{\lambda \alpha}{(1 - \exp(-\lambda)) R_i^{\mathrm{decay}}} u_i^{\alpha - 1} \exp(-\lambda u_i^\alpha) \cdot \frac{\mathbf{W}(\mathbf{x} - \mathbf{x}_i)}{d_{\mathbf{w}}(\mathbf{x}, \mathbf{x}_i)} \cdot \mathbb{I}_{\text{decay}}(d_{\mathbf{w}})$$

### Comment 5 (Reconciliation of Internal Data Inconsistencies):
> *"Check every table, figure, and text value to ensure 100% consistency with authentic experimental data."*

**Response:**
We performed an exhaustive audit against the authentic experimental CSV logs in `revision/results/` and reconciled all four previously reported numerical discrepancies:
1. **Ball-Tree Indexing Speedup:** Unified to **$2.81\times$ at $N=10,000$** ($71.11\text{ ms} \to 25.32\text{ ms}$) and **$2.40\times$ at $N=20,000$** ($141.83\text{ ms} \to 58.97\text{ ms}$) across Abstract, Section 7.7, Table 9, and Figure 10.
2. **Counterfactual Recourse Latency:** Unified to **$40.96\text{ ms}$ ($5.0\times$ speedup over Wachter's $206.64\text{ ms}$)** across Abstract, Section 7.9, Table 11, and Figure 11.
3. **Multi-Field 5-Fold CV Accuracies:** Unified across Table 5 and Table 7: Banknote $97.23 \pm 1.05\%$, Breast Cancer $96.84 \pm 2.12\%$, Ionosphere $94.29 \pm 2.72\%$, Sonar $81.28 \pm 4.12\%$.
4. **Ionosphere DC Ambient Ground Bias:** Unified to $\Delta V_{\mathrm{ambient}} \approx -1.84$ in normalized space ($+4.12$ raw space), restoring accuracy from $69.81\%$ to $94.29\%$.

### Comment 6 (Effective Dimensionality Participation Ratio Parentheses):
> *"In Section 6.2, the participation ratio formula lacked outer parentheses in the numerator."*

**Response:**
Corrected in Eq. 36:
$$d_{\mathrm{eff}} = \frac{\left(\sum_{j=1}^D w_j\right)^2}{\sum_{j=1}^D w_j^2} \approx \frac{(10 \times 1.952 + 990 \times 0.0078)^2}{10 \times (1.952)^2 + 990 \times (0.0078)^2} \approx 19.5 \approx 20.0$$

### Comment 7 (Clarification of Wachter Baseline on Zero-Gradient Surfaces):
> *"Explain why Wachter et al. achieved 3.3% convergence in recourse evaluations."*

**Response:**
We added an explicit explanatory note in Section 7.9 (directly below Table 11). We clarify that when Wachter's L-BFGS optimizer is applied directly to the PFDC potential surface, its line search freezes in zero-gradient vacuum regions ($\nabla P \equiv \mathbf{0}$), achieving only $3.3\%$ convergence. When paired with standard smooth neural networks, Wachter achieves $86.5\%$ convergence but requires $206.64\text{ ms}$ ($5.0\times$ slower than PFDC's $40.96\text{ ms}$).

### Comment 8 (Addition of Formal Optimization Box):
> *"Provide a complete algorithmic summary of the bi-level optimization scheme."*

**Response:**
We added **Algorithm 1: Bi-Level Alternating Electrostatic Optimization for PFDC** in Section 6, explicitly formalizing the inner convex coordinate descent step for support charges $(a_i, b)$ and the outer Hamiltonian leapfrog integration step for radii and metric weights $(R^{\mathrm{core}}, R^{\mathrm{decay}}, \mathbf{w})$.

---

## PART III: SUMMARY TABLE OF MANUSCRIPT REVISIONS

| Item | Topic | Revision Summary | Manuscript Pointer |
|---|---|---|---|
| 1 | Journal Format | elsarticle 10pt double-spaced review format | Entire document |
| 2 | Page Count | Exactly 34 pages ($20 < 34 \le 35$) | Pages 1--34 |
| 3 | Highlights | 5 bullets, each $\le 85$ characters | Highlights doc |
| 4 | References | 44 peer-reviewed references in elsarticle-num | Pages 30--34 |
| 5 | Fake DOI | Removed placeholder; added public GitHub link | Title page, Sec. 10 |
| 6 | Robustness | Certified Lipschitz margin $r_{\mathrm{cert}}$ vs. gradient quenching | Sec. 4.3, Table 8, Fig. 9 |
| 7 | Lemma 1 | Clamped inflection point $u^* = \min(1, \bar{u})$ | Sec. 4.1, Eqs. 20--21 |
| 8 | Force Normalization | Added $(1 - e^{-\lambda})$ denominator to $\mathbf{F}(\mathbf{x})$ | Sec. 3.3, Eq. 18 |
| 9 | Algorithm Box | Added Algorithm 1 for bi-level optimization | Sec. 6, Page 19 |
| 10 | Data Consistency | Reconciled all 4 internal numerical values | Tables 5, 7, 8, 9, 11 |
| 11 | Wachter Baseline | Explained 3.3% zero-gradient stall vs. 86.5% NN | Sec. 7.9 |
| 12 | Declarations | Mandatory Generative AI & Competing Interests | Sec. 10, Pages 29--30 |

We believe the manuscript is now thoroughly strengthened, mathematically sound, and ready for publication in *Pattern Recognition*.
