"""
build_elsevier_pr_docx.py
Publication-grade, fully compliant Microsoft Word (.docx) manuscript generator
specifically tailored to Elsevier "Pattern Recognition" published formatting standards.

Upgraded to address all Reviewer 2 audit points:
1. Balanced-brace extraction for all \caption{...} blocks: complete, untruncated captions for all figures (Figs. 1, 6, 13, 14, 15).
2. Balanced-brace extraction for \textbf{...} in enumerate/itemize lists: eliminates all spurious colons such as 'O: (log N)' and '(dw: > ...)'.
3. Deduplication of macro prefixes: prevents 'Theorem Theorem 2', 'Section Section 6.2', 'Figure Figure 19', 'Table Table 7'.
4. Full 9-column restoration of Table 7: parses \multicolumn{2}{c} and strips \cmidrule so Banknote, Cancer, Ionosphere, and Sonar render perfectly.
5. Square-root handling: replaces \sqrt{...} with Unicode square root √(X) and preserves all math terms.
6. Unicode safety: all Greek and mathematical symbols use explicit unicode escapes, preventing encoding corruption.
7. Generates all 4 target docx files:
   - elsevier_submission/PFDC_PatternRecognition.docx
   - elsevier_submission/PFDC_PR_final.docx
   - tpami_submission/PFDC_TPAMI.docx
   - PFDC_Manuscript.docx
   and synchronizes them to the Brain Artifacts directory.
"""

import os
import re
import shutil
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import pypdfium2 as pdfium
from latex2mathml.converter import convert as latex_to_mathml
import mathml2omml

TEX_FILE = os.path.join("elsevier_submission", "PFDC_PatternRecognition.tex")
BBL_FILE = os.path.join("elsevier_submission", "PFDC_PatternRecognition.bbl")
BIB_FILE = os.path.join("elsevier_submission", "references.bib")

OUTPUT_DOCX_FILES = [
    os.path.join("elsevier_submission", "PFDC_PatternRecognition.docx"),
    os.path.join("elsevier_submission", "PFDC_PR_final.docx"),
    os.path.join("tpami_submission", "PFDC_TPAMI.docx"),
    "PFDC_Manuscript.docx"
]

BRAIN_DIR = r"C:\Users\Visha\.gemini\antigravity\brain\7abe8c0f-1b65-4315-bc1b-a305901d3673"

# ---------------------------------------------------------------------------
# Cross-Reference & Citation Dictionaries
# ---------------------------------------------------------------------------

CITATIONS_MAP = {
    'cortes1995support': '1', 'vapnik1998statistical': '2', 'scholkopf2002learning': '3',
    'broomhead1988multivariable': '4', 'omohundro1989five': '5', 'breiman2001random': '6',
    'friedman2001greedy': '7', 'chen2016xgboost': '8', 'ke2017lightgbm': '9',
    'lecun2015deep': '10', 'arik2021tabnet': '11', 'gorishniy2021revisiting': '12',
    'goodfellow2014explaining': '13', 'aizerman1964theoretical': '14', 'robbins1951stochastic': '15',
    'szegedy2014intriguing': '16', 'madry2018towards': '17', 'cohen2019certified': '18',
    'wachter2017counterfactual': '19', 'mothilal2020explaining': '20', 'ustun2019actionable': '21',
    'bartlett2002rademacher': '22', 'beyer1999nearest': '23', 'chen2018neural': '24',
    'bronstein2017geometric': '25'
}

FIGURES_MAP = {
    'fig:single_point_potential': 'Figure 1',
    'fig:stacking_2d': 'Figure 2',
    'fig:arch_overview': 'Figure 3',
    'fig:stacking_architecture': 'Figure 4',
    'fig:param_sweeps': 'Figure 5',
    'fig:haepo_dynamics': 'Figure 6',
    'fig:pfdc_2d': 'Figure 7',
    'fig:radial_chattering': 'Figure 8',
    'fig:weights': 'Figure 9',
    'fig:four_fields': 'Figure 10',
    'fig:ambient_bias': 'Figure 11',
    'fig:multiclass': 'Figure 12',
    'fig:multiclass_fields': 'Figure 13',
    'fig:loss_landscape': 'Figure 14',
    'fig:certified_radius': 'Figure 15',
    'fig:adversarial': 'Figure 16',
    'fig:indexing': 'Figure 17',
    'fig:medium_scale': 'Figure 18',
    'fig:balltree_geom': 'Figure 19',
    'fig:streamlines_portrait': 'Figure 20',
    'fig:xai': 'Figure 21',
    'fig:riemannian_manifolds': 'Figure 22',
    'fig:overall_radar': 'Figure 23'
}

TABLES_MAP = {
    'tab:paradigm_differentiation': 'Table 1',
    'tab:stacking_empirical': 'Table 2',
    'tab:chattering': 'Table 3',
    'tab:param_sweeps': 'Table 4',
    'tab:2d_benchmark': 'Table 5',
    'tab:1000d': 'Table 6',
    'tab:four_fields_acc': 'Table 7',
    'tab:four_fields_lat': 'Table 8',
    'tab:multidataset_6': 'Table 9',
    'tab:multiclass': 'Table 10',
    'tab:adversarial': 'Table 11',
    'tab:spatial_accel': 'Table 12',
    'tab:california_housing': 'Table 13',
    'tab:xai': 'Table 14'
}

SECTIONS_MAP = {
    'sec:intro': 'Section 1',
    'sec:existing_work': 'Section 1.1',
    'sec:pathologies': 'Section 1.2',
    'sec:theoretical_diff': 'Section 1.3',
    'sec:proposed_pfdc': 'Section 1.4',
    'sec:contributions': 'Section 1.5',
    'sec:subspace_stacking': 'Section 2.4',
    'sec:haepo': 'Section 5.3',
    'sec:highd_scaling': 'Section 6.2',
    'sec:four_fields': 'Section 6.3',
    'sec:ambient_bias': 'Section 6.5',
    'sec:adversarial_bench': 'Section 6.7',
    'sec:riemannian': 'Section 7'
}

THEOREMS_MAP = {
    'thm:rademacher': 'Theorem 1',
    'thm:robustness': 'Theorem 2'
}

GREEK_MAP = {
    r'\alpha': '\u03b1', r'\beta': '\u03b2', r'\gamma': '\u03b3', r'\delta': '\u03b4', r'\Delta': '\u0394',
    r'\epsilon': '\u03b5', r'\varepsilon': '\u03b5', r'\zeta': '\u03b6', r'\eta': '\u03b7', r'\theta': '\u03b8',
    r'\iota': '\u03b9', r'\kappa': '\u03ba', r'\lambda': '\u03bb', r'\Lambda': '\u039b',
    r'\nu': '\u03bd', r'\xi': '\u03be', r'\pi': '\u03c0', r'\rho': '\u03c1', r'\sigma': '\u03c3',
    r'\Sigma': '\u03a3', r'\tau': '\u03c4', r'\phi': '\u03c6', r'\Phi': '\u03a6', r'\psi': '\u03c8',
    r'\omega': '\u03c9', r'\Omega': '\u03a9'
}

SYM_MAP = {
    r'\le': '\u2264', r'\leq': '\u2264', r'\ge': '\u2265', r'\geq': '\u2265', r'\ne': '\u2260', r'\neq': '\u2260',
    r'\approx': '\u2248', r'\ll': '\u226a', r'\gg': '\u226b', r'\to': '\u2192', r'\leftarrow': '\u2190',
    r'\pm': '\u00b1', r'\mp': '\u2213', r'\times': '\u00d7', r'\cdot': '\u00b7',
    r'\notin': '\u2209', r'\subset': '\u2282', r'\forall': '\u2200', r'\exists': '\u2203',
    r'\nabla': '\u2207', r'\infty': '\u221e', r'\partial': '\u2202', r'\sum': '\u2211',
    r'\prod': '\u220f', r'\int': '\u222b', r'\oint': '\u222e', r'\equiv': '\u2261',
    r'\mathbb{R}': 'R', r'\mathbb{S}': 'S', r'\mathbb{H}': 'H',
    r'\mathcal{O}': 'O', r'\mathcal{L}': 'L', r'\mathcal{F}': 'F',
    r'\mathcal{N}': 'N', r'\mathcal{B}': 'B', r'\mathcal{H}': 'H',
    r'\mathcal{U}': 'U', r'\mathcal{M}': 'M', r'\mathcal{D}': 'D',
    r'\mathcal{X}': 'X', r'\mathcal{Y}': 'Y',
    r'\ell_2': '\u2113\u2082', r'\ell_1': '\u2113\u2081', r'\ell_\infty': '\u2113_\u221e', r'\ell_p': '\u2113_p',
    r'\lceil': '\u2308', r'\rceil': '\u2309', r'\lfloor': '\u230a', r'\rfloor': '\u230b',
    r'\bigoplus': '\u2a01', r'\dots': '\u2026', r'\ldots': '\u2026', r'\sim': '~',
    r'\perp': '\u27c2', r'\arccos': 'arccos', r'\lim': 'lim',
    r'\argmax': 'arg max', r'\argmin': 'arg min',
    r'\%': '%', r'\$': '$', r'\_': '_', r'\&': '&', r'~': ' '
}

ACCENT_MAP = {
    r'\"o': '\u00f6', r'\"{o}': '\u00f6', r'\"O': '\u00d6', r'\"{O}': '\u00d6',
    r'\"a': '\u00e4', r'\"{a}': '\u00e4', r'\"A': '\u00c4', r'\"{A}': '\u00c4',
    r'\"u': '\u00fc', r'\"{u}': '\u00fc', r'\"U': '\u00dc', r'\"{U}': '\u00dc',
    r"\'e": '\u00e9', r"\'{e}": '\u00e9', r"\'E": '\u00c9', r"\'{E}": '\u00c9',
    r"\`e": '\u00e8', r"\`{e}": '\u00e8',
    r"\^a": '\u00e2', r"\^{a}": '\u00e2', r"\^o": '\u00f4', r"\^{o}": '\u00f4',
    r"\~n": '\u00f1', r"\~{n}": '\u00f1',
    r'{\"o}': '\u00f6', r'{\"O}': '\u00d6', r'{\"a}': '\u00e4', r'{\"A}': '\u00c4',
    r'{\"u}': '\u00fc', r'{\"U}': '\u00dc', r'{\'e}': '\u00e9', r'{\'E}': '\u00c9'
}

# ---------------------------------------------------------------------------
# Balanced-Brace Helper Functions
# ---------------------------------------------------------------------------

def extract_braced_content(text, command_name):
    """Extracts content inside \command_name{...} with balanced curly braces."""
    pat = r'\\' + command_name + r'\{'
    m = re.search(pat, text)
    if not m:
        return ""
    start = m.end()
    depth = 1
    i = start
    while i < len(text) and depth > 0:
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
        i += 1
    if depth == 0:
        return text[start:i-1]
    return ""

def extract_leading_textbf(text):
    """
    Extracts leading \\textbf{...} prefix and remainder with balanced curly braces.
    Guarantees no early cutoff on nested formulas like \\textbf{Sub-linear $\\mathcal{O}(\\log N)$ ...}.
    """
    text = text.strip()
    if not text.startswith(r'\textbf{'):
        return "", text
    depth = 1
    start = len(r'\textbf{')
    i = start
    while i < len(text) and depth > 0:
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
        i += 1
    if depth == 0:
        prefix = text[start:i-1]
        rem = text[i:].strip()
        if rem.startswith(':'):
            rem = rem[1:].strip()
        return prefix, rem
    return "", text

def replace_balanced_sqrt(text):
    """Replaces \\sqrt{...} with Unicode square root symbol √(inside)."""
    while r'\sqrt{' in text:
        m = re.search(r'\\sqrt\{', text)
        if not m:
            break
        start = m.end()
        depth = 1
        i = start
        while i < len(text) and depth > 0:
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
            i += 1
        if depth == 0:
            inside = text[start:i-1]
            text = text[:m.start()] + '\u221a(' + inside + ')' + text[i:]
        else:
            break
    text = re.sub(r'\\sqrt\s*([a-zA-Z0-9])', lambda m: '\u221a' + m.group(1), text)
    return text

def clean_latex_str(text):
    if not text:
        return ""
    s = text
    # Strip TeX comments
    s = re.sub(r'(?<!\\)%.*$', '', s, flags=re.MULTILINE)
    
    # Strip list and bibliography environment closures
    s = re.sub(r'\\end\{(itemize|enumerate|thebibliography)\}', '', s)
    s = re.sub(r'\\begin\{(itemize|enumerate|thebibliography)\}', '', s)
    
    # Resolve hyperref texorpdfstring
    s = re.sub(r'\\texorpdfstring\{([^}]*)\}\{([^}]*)\}', r'\2', s)
    
    # Resolve citations
    def cite_repl(m):
        raw_keys = m.group(1).split(',')
        nums = [CITATIONS_MAP.get(k.strip(), k.strip()) for k in raw_keys]
        return '[' + ', '.join(nums) + ']'
    s = re.sub(r'\\cite\{([^}]+)\}', cite_repl, s)
    s = re.sub(r'\[([a-zA-Z0-9_\-\s,]+)\]', lambda m: cite_repl(m) if any(k.strip() in CITATIONS_MAP for k in m.group(1).split(',')) else m.group(0), s)
    
    # Normalize prefixes to avoid duplicate macros (e.g. Theorem~Theorem 2)
    s = re.sub(r'\bTheorem~?\\ref\{thm:', r'\\ref{thm:', s)
    s = re.sub(r'\bLemma~?\\ref\{lem:', r'\\ref{lem:', s)
    s = re.sub(r'\bSection~?\\ref\{sec:', r'\\ref{sec:', s)
    s = re.sub(r'\bFigure~?\\ref\{fig:', r'\\ref{fig:', s)
    s = re.sub(r'\bFig\.~?\\ref\{fig:', r'\\ref{fig:', s)
    s = re.sub(r'\bTable~?\\ref\{tab:', r'\\ref{tab:', s)
    
    # Resolve cross-references
    for k, v in FIGURES_MAP.items():
        s = s.replace(f'\\ref{{{k}}}', v).replace(f'[{k}]', v)
    for k, v in TABLES_MAP.items():
        s = s.replace(f'\\ref{{{k}}}', v).replace(f'[{k}]', v)
    for k, v in SECTIONS_MAP.items():
        s = s.replace(f'\\ref{{{k}}}', v).replace(f'[{k}]', v)
    for k, v in THEOREMS_MAP.items():
        s = s.replace(f'\\ref{{{k}}}', v).replace(f'[{k}]', v)
        
    # Safety pass for any duplicate prefixes
    s = re.sub(r'\bTheorem\s+Theorem\b', 'Theorem', s)
    s = re.sub(r'\bLemma\s+Lemma\b', 'Lemma', s)
    s = re.sub(r'\bSection\s+Section\b', 'Section', s)
    s = re.sub(r'\bFigure\s+Figure\b', 'Figure', s)
    s = re.sub(r'\bTable\s+Table\b', 'Table', s)
    
    s = re.sub(r'\\ref\{[^}]+\}', 'Ref.', s)
    s = re.sub(r'\\eqref\{[^}]+\}', '', s)
    s = re.sub(r'\\label\{[^}]+\}', '', s)
    
    # Accents
    for k, v in ACCENT_MAP.items():
        s = s.replace(k, v)
        
    # Double and triple hyphens to en-dash and em-dash
    s = s.replace('---', '\u2014')
    s = s.replace('--', '\u2013')
    
    # Replace balanced square root before backslashes are stripped
    s = replace_balanced_sqrt(s)
    
    # Greek (using word boundary for mu to protect \multicolumn)
    s = re.sub(r'\\mu\b', '\u03bc', s)
    for k, v in GREEK_MAP.items():
        s = s.replace(k, v)
        
    # Infty before in, and in with word boundary
    s = s.replace(r'\infty', '\u221e')
    s = re.sub(r'\\in\b', '\u2208', s)
    
    for k, v in SYM_MAP.items():
        s = s.replace(k, v)
        
    # Math functions
    func_map = {
        r'\exp': 'exp', r'\log': 'log', r'\ln': 'ln', r'\tanh': 'tanh',
        r'\argmax': 'arg max', r'\argmin': 'arg min',
        r'\max': 'max', r'\min': 'min', r'\sgn': 'sgn'
    }
    for k, v in func_map.items():
        s = re.sub(re.escape(k) + r'\b', v, s)
        
    # Formatting macros (multi-pass to peel nested braces)
    for _ in range(6):
        s = re.sub(r'\\textbf\{([^}]*)\}', r'\1', s)
        s = re.sub(r'\\textit\{([^}]*)\}', r'\1', s)
        s = re.sub(r'\\emph\{([^}]*)\}', r'\1', s)
        s = re.sub(r'\\mathrm\{([^}]*)\}', r'\1', s)
        s = re.sub(r'\\mathbf\{([^}]*)\}', r'\1', s)
        s = re.sub(r'\\bm\{([^}]*)\}', r'\1', s)
        s = re.sub(r'\\text\{([^}]*)\}', r'\1', s)
        s = re.sub(r'\\texttt\{([^}]*)\}', r'\1', s)
        s = re.sub(r'\\underline\{([^}]*)\}', r'\1', s)
        s = re.sub(r'\\operatorname\{([^}]*)\}', r'\1', s)
        s = re.sub(r'\\frac\{([^}]*)\}\{([^}]*)\}', r'(\1)/(\2)', s)
        s = re.sub(r'\\boldsymbol\{([^}]*)\}', r'\1', s)
        s = re.sub(r'\\widehat\{([^}]*)\}', lambda m: m.group(1) + '\u0302', s)
        s = re.sub(r'\\bar\{([^}]*)\}', lambda m: m.group(1) + '\u0304', s)
        s = re.sub(r'\\hat\{([^}]*)\}', lambda m: m.group(1) + '\u0302', s)
        s = re.sub(r'\\tilde\{([^}]*)\}', lambda m: m.group(1) + '\u0303', s)
        s = re.sub(r'\\vec\{([^}]*)\}', lambda m: m.group(1) + '\u2192', s)
        s = re.sub(r'_\{([^}]*)\}', r'_\1', s)
        s = re.sub(r'\^\{([^}]*)\}', r'^\1', s)

    # Clean any lingering unmatched LaTeX commands
    s = re.sub(r'\\[a-zA-Z]+\b\s*\{?', '', s)
    s = s.replace('$', '')
    s = s.replace('{', '').replace('}', '')
    s = s.replace('\\', '')
    s = re.sub(r'[ \t]+', ' ', s)
    return s.strip()

def clean_math_eq(text):
    s = text.strip()
    s = replace_balanced_sqrt(s)
    s = re.sub(r'\\mu\b', '\u03bc', s)
    for k, v in GREEK_MAP.items():
        s = s.replace(k, v)
    s = s.replace(r'\infty', '\u221e')
    s = re.sub(r'\\in\b', '\u2208', s)
    for k, v in SYM_MAP.items():
        s = s.replace(k, v)
    s = re.sub(r'\\frac\{([^}]*)\}\{([^}]*)\}', r'(\1)/(\2)', s)
    s = re.sub(r'\\left\(', '(', s)
    s = re.sub(r'\\right\)', ')', s)
    s = re.sub(r'\\left\[', '[', s)
    s = re.sub(r'\\right\]', ']', s)
    s = re.sub(r'\\left\\{', '{', s)
    s = re.sub(r'\\right\\}', '}', s)
    s = re.sub(r'\\left\|', '|', s)
    s = re.sub(r'\\right\|', '|', s)
    s = re.sub(r'\\mathbf\{([^}]*)\}', r'\1', s)
    s = re.sub(r'\\mathrm\{([^}]*)\}', r'\1', s)
    s = re.sub(r'\\text\{([^}]*)\}', r'\1', s)
    s = re.sub(r'\\bm\{([^}]*)\}', r'\1', s)
    s = re.sub(r'\\exp\b', 'exp', s)
    s = re.sub(r'\\log\b', 'log', s)
    s = re.sub(r'\\ln\b', 'ln', s)
    s = re.sub(r'\\tanh\b', 'tanh', s)
    s = re.sub(r'\\max\b', 'max', s)
    s = re.sub(r'\\min\b', 'min', s)
    s = re.sub(r'\\operatorname\{([^}]*)\}', r'\1', s)
    s = re.sub(r'_\{([^}]*)\}', r'_\1', s)
    s = re.sub(r'\^\{([^}]*)\}', r'^\1', s)
    s = s.replace('\\,', ' ').replace('\\;', ' ').replace('\\!', '').replace('\\quad', '   ').replace('\\qquad', '      ')
    s = s.replace('\\', '')
    s = s.replace('$', '')
    s = re.sub(r'[ \t]+', ' ', s)
    return s.strip()

# ---------------------------------------------------------------------------
# Elsevier Pattern Recognition Manuscript Builder Class
# ---------------------------------------------------------------------------

class ElsevierPRManuscriptBuilder:
    def __init__(self):
        self.doc = docx.Document()
        self.setup_page()
        self.eq_counter = 0
        self.fig_counter = 0
        self.tab_counter = 0
        self.sec_counter = 0
        self.subsec_counter = 0
        self.subsubsec_counter = 0
        self.thm_counter = 0
        self.lem_counter = 0
        
    def setup_page(self):
        section = self.doc.sections[0]
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)
        
        # NOTE: 100% clean unnumbered margins (matching camera-ready Elsevier PR papers)
        normal_style = self.doc.styles['Normal']
        normal_style.font.name = 'Times New Roman'
        normal_style.font.size = Pt(11.0)
        normal_style.font.color.rgb = RGBColor(0x11, 0x11, 0x11)
        normal_style.paragraph_format.line_spacing = 1.20
        normal_style.paragraph_format.space_after = Pt(4)
        normal_style.paragraph_format.space_before = Pt(0)

    def add_horizontal_rule(self, space_before=4, space_after=8):
        """Adds a clean academic horizontal divider rule (0.75 pt solid black)"""
        p_rule = self.doc.add_paragraph()
        p_rule.paragraph_format.space_before = Pt(space_before)
        p_rule.paragraph_format.space_after = Pt(space_after)
        pPr = p_rule._p.get_or_add_pPr()
        bdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="6" w:space="1" w:color="000000"/></w:pBdr>')
        pPr.append(bdr)

    def add_title_block(self):
        p_title = self.doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_title.paragraph_format.space_before = Pt(0)
        p_title.paragraph_format.space_after = Pt(10)
        r_title = p_title.add_run("Potential Field Decay Classification (PFDC): A Physics-Grounded Paradigm with Certified Invariance and Continuous Recourse")
        r_title.font.name = 'Times New Roman'
        r_title.font.size = Pt(18.0)
        r_title.bold = True
        r_title.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        
        p_auth = self.doc.add_paragraph()
        p_auth.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_auth.paragraph_format.space_after = Pt(3)
        
        r_auth1 = p_auth.add_run("Vishal Chandel")
        r_auth1.font.name = 'Times New Roman'
        r_auth1.font.size = Pt(12.0)
        r_auth1.bold = True
        r_auth1.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        
        r_sup1 = p_auth.add_run(" a, *")
        r_sup1.font.name = 'Times New Roman'
        r_sup1.font.size = Pt(9.5)
        r_sup1.font.superscript = True
        r_sup1.bold = True
        r_sup1.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        
        r_sep = p_auth.add_run(", ")
        r_sep.font.name = 'Times New Roman'
        r_sep.font.size = Pt(12.0)
        
        r_auth2 = p_auth.add_run("Adarsh Chandel")
        r_auth2.font.name = 'Times New Roman'
        r_auth2.font.size = Pt(12.0)
        r_auth2.bold = True
        r_auth2.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        
        r_sup2 = p_auth.add_run(" b")
        r_sup2.font.name = 'Times New Roman'
        r_sup2.font.size = Pt(9.5)
        r_sup2.font.superscript = True
        r_sup2.bold = True
        r_sup2.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        
        p_aff1 = self.doc.add_paragraph()
        p_aff1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_aff1.paragraph_format.space_after = Pt(2)
        r_a = p_aff1.add_run("a ")
        r_a.font.name = 'Times New Roman'
        r_a.font.size = Pt(8.5)
        r_a.font.superscript = True
        r_aff1_txt = p_aff1.add_run("Department of Electronics and Communication Engineering, Jawaharlal Nehru Government Engineering College Sundernagar, INDIA")
        r_aff1_txt.font.name = 'Times New Roman'
        r_aff1_txt.font.size = Pt(9.5)
        r_aff1_txt.font.italic = True
        r_aff1_txt.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
        
        p_aff2 = self.doc.add_paragraph()
        p_aff2.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_aff2.paragraph_format.space_after = Pt(3)
        r_b = p_aff2.add_run("b ")
        r_b.font.name = 'Times New Roman'
        r_b.font.size = Pt(8.5)
        r_b.font.superscript = True
        r_aff2_txt = p_aff2.add_run("Chitkara University, Punjab, INDIA")
        r_aff2_txt.font.name = 'Times New Roman'
        r_aff2_txt.font.size = Pt(9.5)
        r_aff2_txt.font.italic = True
        r_aff2_txt.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
        
        p_cor = self.doc.add_paragraph()
        p_cor.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_cor.paragraph_format.space_after = Pt(6)
        r_star = p_cor.add_run("* ")
        r_star.font.name = 'Times New Roman'
        r_star.font.size = Pt(8.5)
        r_star.font.superscript = True
        r_cor = p_cor.add_run("Corresponding author. E-mail: chandelvishal445@gmail.com\n")
        r_cor.font.name = 'Times New Roman'
        r_cor.font.size = Pt(9.0)
        r_cor.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
        
        r_doi = p_cor.add_run("Permanent Research Archive DOI: https://doi.org/10.5281/zenodo.23936990 | Code: https://github.com/Vishal442005/Potential-Field-Decay-Classification")
        r_doi.font.name = 'Times New Roman'
        r_doi.font.size = Pt(9.0)
        r_doi.font.italic = True
        r_doi.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    def add_highlights_block(self):
        """Elsevier Pattern Recognition unboxed Highlights section (3-5 bullets, <=85 characters each)"""
        p_hdr = self.doc.add_paragraph()
        p_hdr.paragraph_format.space_before = Pt(6)
        p_hdr.paragraph_format.space_after = Pt(4)
        p_hdr.paragraph_format.keep_with_next = True
        r_hdr = p_hdr.add_run("Highlights")
        r_hdr.font.name = "Times New Roman"
        r_hdr.font.size = Pt(11.0)
        r_hdr.bold = True
        r_hdr.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        
        highlights = [
            "Physics-grounded ML replacing global partitions with dual-zone potential fields.",
            "Certainty cores prove 100% certified adversarial invariance against PGD attacks.",
            "Rademacher complexity establishes formal PAC generalization under compact support.",
            "Conservative force field enables gradient-free continuous counterfactual recourse.",
            "Metric Ball-Tree indexing achieves sub-linear O(log N) scalable query evaluation."
        ]
        
        for h in highlights:
            assert len(h) <= 85, f"Highlight exceeds 85 chars: {len(h)} '{h}'"
            p_b = self.doc.add_paragraph()
            p_b.paragraph_format.left_indent = Inches(0.25)
            p_b.paragraph_format.space_before = Pt(0)
            p_b.paragraph_format.space_after = Pt(2)
            p_b.paragraph_format.line_spacing = 1.15
            
            r_bullet = p_b.add_run("\u2022 ")
            r_bullet.font.name = "Times New Roman"
            r_bullet.font.size = Pt(10.0)
            r_bullet.bold = True
            r_bullet.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
            
            r_txt = p_b.add_run(h)
            r_txt.font.name = "Times New Roman"
            r_txt.font.size = Pt(10.0)
            r_txt.font.color.rgb = RGBColor(0x11, 0x11, 0x11)
            
        p_sp = self.doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(2)
        p_sp.paragraph_format.space_after = Pt(4)

    def add_abstract_block(self, abstract_text, keywords_text):
        """Elsevier Pattern Recognition unboxed abstract and keywords block"""
        p_hdr = self.doc.add_paragraph()
        p_hdr.paragraph_format.space_before = Pt(6)
        p_hdr.paragraph_format.space_after = Pt(3)
        p_hdr.paragraph_format.keep_with_next = True
        r_hdr = p_hdr.add_run("Abstract")
        r_hdr.font.name = "Times New Roman"
        r_hdr.font.size = Pt(11.0)
        r_hdr.bold = True
        r_hdr.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        
        clean_ab = clean_latex_str(abstract_text)
        p_ab = self.doc.add_paragraph()
        p_ab.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ab.paragraph_format.space_before = Pt(0)
        p_ab.paragraph_format.space_after = Pt(6)
        p_ab.paragraph_format.line_spacing = 1.18
        r_txt = p_ab.add_run(clean_ab)
        r_txt.font.name = "Times New Roman"
        r_txt.font.size = Pt(10.0)
        r_txt.font.color.rgb = RGBColor(0x11, 0x11, 0x11)
        
        p_kw = self.doc.add_paragraph()
        p_kw.paragraph_format.space_before = Pt(4)
        p_kw.paragraph_format.space_after = Pt(6)
        p_kw.paragraph_format.line_spacing = 1.15
        
        r_kw_hdr = p_kw.add_run("Keywords: ")
        r_kw_hdr.font.name = "Times New Roman"
        r_kw_hdr.font.size = Pt(10.0)
        r_kw_hdr.bold = True
        r_kw_hdr.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        
        clean_kw = clean_latex_str(keywords_text)
        r_kw = p_kw.add_run(clean_kw)
        r_kw.font.name = "Times New Roman"
        r_kw.font.size = Pt(10.0)
        r_kw.font.italic = True
        r_kw.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    def add_h1(self, text):
        self.sec_counter += 1
        self.subsec_counter = 0
        self.subsubsec_counter = 0
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        is_unnumbered = any(text.lower().startswith(x) for x in ["reference", "declaration", "data and code", "credit", "acknowledg", "funding"])
        num_prefix = "" if is_unnumbered else f"{self.sec_counter}. "
        r = p.add_run(num_prefix + clean_latex_str(text))
        r.font.name = "Times New Roman"
        r.font.size = Pt(13.0)
        r.bold = True
        r.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    def add_h2(self, text):
        self.subsec_counter += 1
        self.subsubsec_counter = 0
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        
        clean_title = clean_latex_str(text)
        if "survey of existing" in clean_title.lower():
            clean_title = "Survey of Existing Literature"
        elif "pathologies of global" in clean_title.lower():
            clean_title = "Vulnerabilities of Boundary Partitioning"
            
        num_prefix = f"{self.sec_counter}.{self.subsec_counter}. "
        r = p.add_run(num_prefix + clean_title)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11.5)
        r.bold = True
        r.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    def add_h3(self, text):
        self.subsubsec_counter += 1
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(9)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        num_prefix = f"{self.sec_counter}.{self.subsec_counter}.{self.subsubsec_counter}. "
        r = p.add_run(num_prefix + clean_latex_str(text))
        r.font.name = "Times New Roman"
        r.font.size = Pt(10.5)
        r.bold = True
        r.font.italic = True
        r.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    def add_body(self, text):
        cleaned = clean_latex_str(text)
        if not cleaned:
            return
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.20
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r = p.add_run(cleaned)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11.0)
        r.font.color.rgb = RGBColor(0x11, 0x11, 0x11)

    def add_bullet(self, bold_prefix, text):
        p = self.doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.18
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if bold_prefix:
            clean_pref = clean_latex_str(bold_prefix).rstrip(': ')
            r_bold = p.add_run(clean_pref + ": ")
            r_bold.font.name = "Times New Roman"
            r_bold.font.size = Pt(11.0)
            r_bold.bold = True
            r_bold.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        r_text = p.add_run(clean_latex_str(text))
        r_text.font.name = "Times New Roman"
        r_text.font.size = Pt(11.0)
        r_text.font.color.rgb = RGBColor(0x11, 0x11, 0x11)

    def add_num_item(self, num_str, bold_prefix, text):
        p = self.doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.18
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r_num = p.add_run(num_str + " ")
        r_num.font.name = "Times New Roman"
        r_num.font.size = Pt(11.0)
        r_num.bold = True
        r_num.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        if bold_prefix:
            clean_pref = clean_latex_str(bold_prefix).rstrip(': ')
            r_bold = p.add_run(clean_pref + ": ")
            r_bold.font.name = "Times New Roman"
            r_bold.font.size = Pt(11.0)
            r_bold.bold = True
            r_bold.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        r_text = p.add_run(clean_latex_str(text))
        r_text.font.name = "Times New Roman"
        r_text.font.size = Pt(11.0)
        r_text.font.color.rgb = RGBColor(0x11, 0x11, 0x11)

    def add_eq_omml(self, raw_eq, eq_num=None):
        """Converts raw LaTeX equation into a native Microsoft Word OMML equation (<m:oMath>)"""
        if eq_num is None:
            self.eq_counter += 1
            eq_num = str(self.eq_counter)
            
        clean = re.sub(r'\\label\{[^}]+\}', '', raw_eq).strip()
        clean = re.sub(r'\\qquad', ' ', clean).replace(r'\quad', ' ')
        clean = clean.replace('&', '')
        
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        
        omml_added = False
        try:
            mml = latex_to_mathml(clean)
            omml_str = mathml2omml.convert(mml)
            if '<m:oMath' in omml_str and 'xmlns:m' not in omml_str:
                omml_str = omml_str.replace('<m:oMath', '<m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"', 1)
            omml_el = parse_xml(omml_str.encode('utf-8'))
            p._p.append(omml_el)
            omml_added = True
        except Exception as e:
            cleaned = clean_math_eq(raw_eq)
            r_eq = p.add_run(f"    {cleaned}    ")
            r_eq.font.name = "Cambria Math"
            r_eq.font.size = Pt(10.5)
            r_eq.font.italic = True
            
        r_space = p.add_run("       ")
        r_num = p.add_run(f"({eq_num})")
        r_num.font.name = "Times New Roman"
        r_num.font.size = Pt(10.5)
        r_num.bold = True
        r_num.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    def add_theorem(self, title_str, body_text):
        """Native unboxed Elsevier PR mathematical theorem formatting"""
        self.thm_counter += 1
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.18
        p.paragraph_format.left_indent = Inches(0.2)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        r_lead = p.add_run(f"Theorem {self.thm_counter}")
        r_lead.font.name = "Times New Roman"
        r_lead.font.size = Pt(11.0)
        r_lead.bold = True
        r_lead.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        
        clean_title = clean_latex_str(title_str).strip()
        if clean_title:
            r_title = p.add_run(f" ({clean_title}). ")
            r_title.font.name = "Times New Roman"
            r_title.font.size = Pt(11.0)
            r_title.bold = True
            r_title.font.italic = True
            r_title.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        else:
            r_dot = p.add_run(". ")
            r_dot.font.name = "Times New Roman"
            r_dot.font.size = Pt(11.0)
            r_dot.bold = True
            r_dot.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
            
        r_body = p.add_run(clean_latex_str(body_text))
        r_body.font.name = "Times New Roman"
        r_body.font.size = Pt(11.0)
        r_body.font.italic = True
        r_body.font.color.rgb = RGBColor(0x11, 0x11, 0x11)

    def add_lemma(self, title_str, body_text):
        """Native unboxed Elsevier PR mathematical lemma formatting"""
        self.lem_counter += 1
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.18
        p.paragraph_format.left_indent = Inches(0.2)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        r_lead = p.add_run(f"Lemma {self.lem_counter}")
        r_lead.font.name = "Times New Roman"
        r_lead.font.size = Pt(11.0)
        r_lead.bold = True
        r_lead.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        
        clean_title = clean_latex_str(title_str).strip()
        if clean_title:
            r_title = p.add_run(f" ({clean_title}). ")
            r_title.font.name = "Times New Roman"
            r_title.font.size = Pt(11.0)
            r_title.bold = True
            r_title.font.italic = True
            r_title.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        else:
            r_dot = p.add_run(". ")
            r_dot.font.name = "Times New Roman"
            r_dot.font.size = Pt(11.0)
            r_dot.bold = True
            r_dot.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
            
        r_body = p.add_run(clean_latex_str(body_text))
        r_body.font.name = "Times New Roman"
        r_body.font.size = Pt(11.0)
        r_body.font.italic = True
        r_body.font.color.rgb = RGBColor(0x11, 0x11, 0x11)

    def add_figure(self, pdf_rel_path, caption_text):
        self.fig_counter += 1
        pdf_path = pdf_rel_path.replace('\\', '/')
        if not os.path.exists(pdf_path):
            alt_path = os.path.join("figures", os.path.basename(pdf_path))
            if os.path.exists(alt_path):
                pdf_path = alt_path
            else:
                print(f"Warning: Cannot find PDF figure: {pdf_path}")
                return
                
        temp_png = f"temp_docx_fig_{self.fig_counter}.png"
        try:
            pdf = pdfium.PdfDocument(pdf_path)
            img = pdf[0].render(scale=2.5).to_pil()
            img.save(temp_png)
            
            p_img = self.doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(10)
            p_img.paragraph_format.space_after = Pt(4)
            r_img = p_img.add_run()
            r_img.add_picture(temp_png, width=Inches(6.2))
            
            p_cap = self.doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(12)
            p_cap.paragraph_format.line_spacing = 1.15
            
            r_num = p_cap.add_run(f"Figure {self.fig_counter}. ")
            r_num.font.name = "Times New Roman"
            r_num.font.size = Pt(10.0)
            r_num.bold = True
            r_num.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
            
            r_txt = p_cap.add_run(clean_latex_str(caption_text))
            r_txt.font.name = "Times New Roman"
            r_txt.font.size = Pt(10.0)
            r_txt.font.italic = True
            r_txt.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
        finally:
            if os.path.exists(temp_png):
                os.remove(temp_png)

    def add_table(self, caption_text, raw_tabular_body):
        self.tab_counter += 1
        
        lines = [l.strip() for l in raw_tabular_body.strip().split(r'\\') if l.strip()]
        parsed_rows = []  # list of lists of (cleaned_content, col_span)
        for line in lines:
            l_clean = re.sub(r'\\(toprule|midrule|bottomrule)', '', line)
            l_clean = re.sub(r'\\cmidrule(\([^)]*\))?\{[^}]*\}', '', l_clean).strip()
            if not l_clean:
                continue
            raw_cells = [c.strip() for c in l_clean.split('&')]
            row_items = []
            for c in raw_cells:
                mc = re.match(r'\\multicolumn\{(\d+)\}\{[^}]*\}\{(.*)\}', c, re.DOTALL)
                if mc:
                    span = int(mc.group(1))
                    content = clean_latex_str(mc.group(2).strip())
                    row_items.append((content, span))
                else:
                    content = clean_latex_str(c.strip())
                    row_items.append((content, 1))
            parsed_rows.append(row_items)
            
        if not parsed_rows:
            return
            
        # Determine total column count across all rows
        num_cols = max(sum(span for _, span in r) for r in parsed_rows)
        num_rows = len(parsed_rows)
        has_multi = any(span > 1 for r in parsed_rows for _, span in r)
        num_header_rows = 2 if has_multi else 1
        
        # Caption above table (Elsevier standard: Table 1. Caption)
        p_cap = self.doc.add_paragraph()
        p_cap.paragraph_format.space_before = Pt(12)
        p_cap.paragraph_format.space_after = Pt(4)
        p_cap.paragraph_format.keep_with_next = True
        r_num = p_cap.add_run(f"Table {self.tab_counter}. ")
        r_num.font.name = "Times New Roman"
        r_num.font.size = Pt(10.0)
        r_num.bold = True
        r_num.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        
        r_txt = p_cap.add_run(clean_latex_str(caption_text))
        r_txt.font.name = "Times New Roman"
        r_txt.font.size = Pt(10.0)
        r_txt.bold = True
        r_txt.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        
        tbl = self.doc.add_table(rows=num_rows, cols=num_cols)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        
        # Classic 3-line booktabs table
        tblPr = tbl._tbl.tblPr
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
            f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
            f'<w:insideH w:val="none"/>'
            f'<w:left w:val="none"/><w:right w:val="none"/><w:insideV w:val="none"/>'
            f'</w:tblBorders>'
        )
        tblPr.append(borders)
        
        # Populate and style cells
        for r_idx, row_items in enumerate(parsed_rows):
            is_header = (r_idx < num_header_rows)
            is_best_row = any("dual-charge" in str(val).lower() or "ours" in str(val).lower() for val, _ in row_items)
            curr_c = 0
            
            for content, span in row_items:
                if curr_c >= num_cols:
                    break
                cell = tbl.cell(r_idx, curr_c)
                cell.text = content
                
                # Merge across span columns if multicolumn
                if span > 1 and curr_c + span - 1 < num_cols:
                    merge_target = tbl.cell(r_idx, curr_c + span - 1)
                    cell.merge(merge_target)
                    
                tcPr = cell._tc.get_or_add_tcPr()
                if is_header and r_idx == num_header_rows - 1:
                    bdr = parse_xml(
                        f'<w:tcBorders {nsdecls("w")}>'
                        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
                        f'</w:tcBorders>'
                    )
                    tcPr.append(bdr)
                    
                tcMar = parse_xml(
                    f'<w:tcMar {nsdecls("w")}>'
                    f'<w:top w:w="70" w:type="dxa"/><w:bottom w:w="70" w:type="dxa"/>'
                    f'<w:left w:w="90" w:type="dxa"/><w:right w:w="90" w:type="dxa"/>'
                    f'</w:tcMar>'
                )
                tcPr.append(tcMar)
                
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER if (curr_c > 0 or is_header) else WD_ALIGN_PARAGRAPH.LEFT
                for r in p.runs:
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(9.5 if is_header else 9.0)
                    if is_header or is_best_row:
                        r.bold = True
                        r.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
                    else:
                        r.font.color.rgb = RGBColor(0x11, 0x11, 0x11)
                        
                curr_c += span
                
        p_after = self.doc.add_paragraph()
        p_after.paragraph_format.space_before = Pt(0)
        p_after.paragraph_format.space_after = Pt(8)

    def add_declarations_section(self):
        """Elsevier mandatory declaration statements, matching authors Vishal Chandel & Adarsh Chandel"""
        self.add_h1("CRediT Authorship Contribution Statement")
        self.add_body(
            "Vishal Chandel: Conceptualization, Methodology, Mathematical Formulations & Proofs, "
            "Software Architecture, Validation, Formal Analysis, Investigation, Data Curation, "
            "Writing - Original Draft, Writing - Review & Editing, Visualization, Project Administration. "
            "Adarsh Chandel: Validation, Formal Analysis, Investigation, Writing - Review & Editing."
        )

        self.add_h1("Declaration of Competing Interest")
        self.add_body(
            "The authors declare that they have no known competing financial interests or personal "
            "relationships that could have appeared to influence the work reported in this paper."
        )

        self.add_h1("Data and Code Availability")
        self.add_body(
            "The complete open-source software implementation of Potential Field Decay Classification (PFDC), "
            "including all synthetic benchmark generators, four real-world scientific datasets (Banknote Authentication, "
            "Breast Cancer Wisconsin, Ionosphere Radar, Sonar Array), and reproduction scripts, are openly accessible on GitHub at: "
            "https://github.com/Vishal442005/Potential-Field-Decay-Classification. "
            "The permanent citable software and benchmark artifact is permanently archived on Zenodo under DOI: "
            "10.5281/zenodo.23936990 (https://doi.org/10.5281/zenodo.23936990)."
        )

        self.add_h1("Funding")
        self.add_body(
            "This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors."
        )

    def add_bibliography(self, bib_items):
        self.add_h1("References")
        for idx, item in enumerate(bib_items):
            clean_item = re.sub(r'\\end\{thebibliography\}', '', item).strip()
            clean_item = re.sub(r'(\d+)--(\d+)', lambda m: f"{m.group(1)}\u2013{m.group(2)}", clean_item)
            clean_item = clean_latex_str(clean_item)
            
            p = self.doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            p.paragraph_format.first_line_indent = Inches(-0.3)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.15
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            
            r_num = p.add_run(f"[{idx+1}] ")
            r_num.font.name = "Times New Roman"
            r_num.font.size = Pt(9.5)
            r_num.bold = True
            r_num.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
            
            r_txt = p.add_run(clean_item)
            r_txt.font.name = "Times New Roman"
            r_txt.font.size = Pt(9.5)
            r_txt.font.color.rgb = RGBColor(0x11, 0x11, 0x11)

    def save(self, output_path):
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        self.doc.save(output_path)
        print(f"Saved: {output_path}")

# ---------------------------------------------------------------------------
# Master Execution Pipeline
# ---------------------------------------------------------------------------

def build_all_elsevier_pr_docx():
    print(f"Reading LaTeX source: {TEX_FILE} ...")
    with open(TEX_FILE, 'r', encoding='utf-8') as f:
        latex_text = f.read()

    ab_m = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', latex_text, re.DOTALL)
    abstract_text = ab_m.group(1).strip() if ab_m else ""
    
    kw_m = re.search(r'\\textbf\{Keywords:\}\s*(.*?)(?=\\section|\Z)', latex_text, re.DOTALL)
    keywords_text = kw_m.group(1).strip() if kw_m else ""
    if not keywords_text:
        keywords_text = "Potential Field Decay Classification, Certified Adversarial Robustness, Certainty Basins, Explainable AI, Counterfactual Recourse, Hamiltonian Annealing, Spatial Ball-Tree."
    
    body_start = latex_text.find(r'\section{Introduction}')
    body_end = latex_text.find(r'\section*{Data and Code Availability}')
    if body_end == -1:
        body_end = latex_text.find(r'\bibliographystyle')
    if body_end == -1:
        body_end = latex_text.find(r'\bibliography')
    if body_end == -1:
        body_end = latex_text.find(r'\end{document}')
        
    body = latex_text[body_start:body_end]
    
    patterns = [
        ('figure', r'\\begin\{figure\*?\}.*?\\end\{figure\*?\}'),
        ('table_env', r'\\begin\{table\*?\}.*?\\end\{table\*?\}'),
        ('theorem', r'\\begin\{theorem\}(?:\[[^\]]*\])?.*?\\end\{theorem\}'),
        ('lemma', r'\\begin\{lemma\}(?:\[[^\]]*\])?.*?\\end\{lemma\}'),
        ('equation', r'\\begin\{equation\}.*?\\end\{equation\}'),
        ('align', r'\\begin\{align\}.*?\\end\{align\}'),
        ('enumerate', r'\\begin\{enumerate\}.*?\\end\{enumerate\}'),
        ('itemize', r'\\begin\{itemize\}.*?\\end\{itemize\}'),
        ('section', r'\\section\*?\{(?:[^{}]|\{[^{}]*\})*\}'),
        ('subsection', r'\\subsection\*?\{(?:[^{}]|\{[^{}]*\})*\}'),
        ('subsubsection', r'\\subsubsection\*?\{(?:[^{}]|\{[^{}]*\})*\}'),
        ('floatbarrier', r'\\FloatBarrier')
    ]
    master_pat = '|'.join(f'(?P<{name}>{pat})' for name, pat in patterns)
    
    tokens = []
    last_pos = 0
    for m in re.finditer(master_pat, body, re.DOTALL):
        pre_text = body[last_pos:m.start()].strip()
        if pre_text:
            tokens.append(('paragraph', pre_text))
        kind = m.lastgroup
        val = m.group(kind)
        tokens.append((kind, val))
        last_pos = m.end()
        
    post_text = body[last_pos:].strip()
    if post_text:
        tokens.append(('paragraph', post_text))
        
    print(f"Tokenized LaTeX document into {len(tokens)} structural elements.")
    
    bib_items = []
    if os.path.exists(BBL_FILE):
        with open(BBL_FILE, 'r', encoding='utf-8') as f:
            bbl_text = f.read()
        raw_bbls = re.findall(r'\\bibitem\{[^}]+\}(.*?)(?=\\bibitem|\Z)', bbl_text, re.DOTALL)
        for b in raw_bbls:
            b_clean = re.sub(r'\\newblock', ' ', b)
            b_clean = re.sub(r'\\end\{thebibliography\}', '', b_clean).strip()
            if b_clean:
                bib_items.append(b_clean)
                
    if not bib_items and os.path.exists(BIB_FILE):
        with open(BIB_FILE, 'r', encoding='utf-8') as f:
            bib_text = f.read()
        raw_entries = re.findall(r'@\w+\{[^,]+,\s*(.*?)(?=@\w+\{|\Z)', bib_text, re.DOTALL)
        for e in raw_entries:
            title_match = re.search(r'title\s*=\s*\{([^}]+)\}', e)
            author_match = re.search(r'author\s*=\s*\{([^}]+)\}', e)
            year_match = re.search(r'year\s*=\s*\{([^}]+)\}', e)
            journal_match = re.search(r'(journal|booktitle)\s*=\s*\{([^}]+)\}', e)
            t = title_match.group(1) if title_match else ""
            a = author_match.group(1) if author_match else ""
            y = year_match.group(1) if year_match else ""
            j = journal_match.group(2) if journal_match else ""
            bib_items.append(f"{a}, \"{t}\", {j}, {y}.")
            
    print(f"Loaded {len(bib_items)} bibliographic references.")
    
    builder = ElsevierPRManuscriptBuilder()
    builder.add_title_block()
    builder.add_horizontal_rule()
    builder.add_highlights_block()
    builder.add_abstract_block(abstract_text, keywords_text)
    builder.add_horizontal_rule()
    
    for kind, val in tokens:
        if kind == 'section':
            sec_title = extract_braced_content(val, 'section') or re.search(r'\\section\*?\{(.*)\}', val, re.DOTALL).group(1)
            builder.add_h1(sec_title)
            
        elif kind == 'subsection':
            sub_title = extract_braced_content(val, 'subsection') or re.search(r'\\subsection\*?\{(.*)\}', val, re.DOTALL).group(1)
            builder.add_h2(sub_title)
            
        elif kind == 'subsubsection':
            subsub_title = extract_braced_content(val, 'subsubsection') or re.search(r'\\subsubsection\*?\{(.*)\}', val, re.DOTALL).group(1)
            builder.add_h3(subsub_title)
            
        elif kind == 'paragraph':
            paras = [p.strip() for p in val.split('\n\n') if p.strip()]
            for p in paras:
                p_clean = re.sub(r'\\label\{[^}]+\}', '', p).strip()
                if p_clean and not p_clean.startswith('%'):
                    builder.add_body(p_clean)
                    
        elif kind == 'enumerate':
            raw_items = re.split(r'\\item\b', val)[1:]
            for idx, it in enumerate(raw_items):
                it_clean = it.strip()
                it_clean = re.sub(r'\\end\{(itemize|enumerate|thebibliography)\}', '', it_clean).strip()
                it_clean = re.sub(r'\\begin\{(itemize|enumerate|thebibliography)\}', '', it_clean).strip()
                
                if r'\begin{equation}' in it_clean:
                    m = re.search(r'^(.*?)\\begin\{equation\}(.*?)\\end\{equation\}(.*)$', it_clean, re.DOTALL)
                    if m:
                        pre_part = m.group(1).strip()
                        eq_part = m.group(2).strip()
                        post_part = m.group(3).strip()
                        
                        prefix, text = extract_leading_textbf(pre_part)
                        builder.add_num_item(f"({idx+1})", prefix, text)
                        builder.add_eq_omml(eq_part)
                        if post_part:
                            builder.add_body(post_part)
                        continue
                        
                prefix, text = extract_leading_textbf(it_clean)
                builder.add_num_item(f"({idx+1})", prefix, text)
                
        elif kind == 'itemize':
            raw_items = re.split(r'\\item\b', val)[1:]
            for it in raw_items:
                it_clean = it.strip()
                it_clean = re.sub(r'\\end\{(itemize|enumerate|thebibliography)\}', '', it_clean).strip()
                it_clean = re.sub(r'\\begin\{(itemize|enumerate|thebibliography)\}', '', it_clean).strip()
                
                if r'\begin{equation}' in it_clean:
                    m = re.search(r'^(.*?)\\begin\{equation\}(.*?)\\end\{equation\}(.*)$', it_clean, re.DOTALL)
                    if m:
                        pre_part = m.group(1).strip()
                        eq_part = m.group(2).strip()
                        post_part = m.group(3).strip()
                        
                        prefix, text = extract_leading_textbf(pre_part)
                        builder.add_bullet(prefix, text)
                        builder.add_eq_omml(eq_part)
                        if post_part:
                            builder.add_body(post_part)
                        continue
                        
                prefix, text = extract_leading_textbf(it_clean)
                builder.add_bullet(prefix, text)
                
        elif kind == 'equation':
            eq_body = re.search(r'\\begin\{equation\}(.*?)\\end\{equation\}', val, re.DOTALL).group(1)
            eq_body_clean = re.sub(r'\\label\{[^}]+\}', '', eq_body).strip()
            builder.add_eq_omml(eq_body_clean)
            
        elif kind == 'align':
            align_body = re.search(r'\\begin\{align\}(.*?)\\end\{align\}', val, re.DOTALL).group(1)
            lines = [l.strip().replace('&=', '=').replace('&', '') for l in align_body.split(r'\\') if l.strip()]
            builder.eq_counter += 1
            main_num = builder.eq_counter
            for l_idx, l in enumerate(lines):
                l_clean = re.sub(r'\\label\{[^}]+\}', '', l).strip()
                if l_clean:
                    sub_num = f"{main_num}.{l_idx+1}" if len(lines) > 1 else str(main_num)
                    builder.add_eq_omml(l_clean, eq_num=sub_num)
                    
        elif kind == 'theorem':
            thm_m = re.search(r'\\begin\{theorem\}(?:\[([^\]]*)\])?(.*?)\\end\{theorem\}', val, re.DOTALL)
            thm_title = thm_m.group(1) if thm_m.group(1) else "Theorem"
            thm_body = thm_m.group(2)
            thm_body_clean = re.sub(r'\\label\{[^}]+\}', '', thm_body).strip()
            builder.add_theorem(thm_title, thm_body_clean)
            
        elif kind == 'lemma':
            lem_m = re.search(r'\\begin\{lemma\}(?:\[([^\]]*)\])?(.*?)\\end\{lemma\}', val, re.DOTALL)
            lem_title = lem_m.group(1) if lem_m.group(1) else "Lemma"
            lem_body = lem_m.group(2)
            lem_body_clean = re.sub(r'\\label\{[^}]+\}', '', lem_body).strip()
            builder.add_lemma(lem_title, lem_body_clean)
            
        elif kind == 'figure':
            img_m = re.search(r'\\includegraphics\[.*?\]\{([^}]+)\}', val)
            cap_text = extract_braced_content(val, 'caption')
            if not cap_text:
                cap_m = re.search(r'\\caption\{([^}]+)\}', val)
                cap_text = cap_m.group(1) if cap_m else ""
            if img_m and cap_text:
                img_path = img_m.group(1).strip()
                builder.add_figure(img_path, cap_text)
                
        elif kind == 'table_env':
            cap_text = extract_braced_content(val, 'caption')
            if not cap_text:
                cap_m = re.search(r'\\caption\{([^}]+)\}', val)
                cap_text = cap_m.group(1) if cap_m else ""
            tabular_m = re.search(r'\\begin\{tabular\}\{[^}]+\}(.*?)\\end\{tabular\}', val, re.DOTALL)
            if cap_text and tabular_m:
                tabular_body = tabular_m.group(1).strip()
                builder.add_table(cap_text, tabular_body)
                
        elif kind == 'floatbarrier':
            pass
            
    # Add Mandatory Declarations
    builder.add_declarations_section()
    
    # Add References
    builder.add_bibliography(bib_items)
    
    # Save Documents
    for out_path in OUTPUT_DOCX_FILES:
        builder.save(out_path)
        
    # Copy to Brain Artifacts Directory
    for doc_name in ["PFDC_PatternRecognition.docx", "PFDC_PR_final.docx", "PFDC_TPAMI.docx", "PFDC_Manuscript.docx"]:
        src = doc_name if os.path.exists(doc_name) else os.path.join("elsevier_submission", doc_name)
        if not os.path.exists(src):
            src = os.path.join("tpami_submission", doc_name)
        if os.path.exists(src):
            dst = os.path.join(BRAIN_DIR, doc_name)
            shutil.copy2(src, dst)
            print(f"Copied artifact: {dst}")

    # Also copy the PDF files to Brain Artifacts Directory
    for pdf_name, rel_path in [
        ("PFDC_PatternRecognition.pdf", "elsevier_submission/PFDC_PatternRecognition.pdf"),
        ("PFDC_TPAMI.pdf", "tpami_submission/PFDC_TPAMI.pdf"),
        ("PFDC_Manuscript.pdf", "PFDC_Manuscript.pdf")
    ]:
        if os.path.exists(rel_path):
            dst = os.path.join(BRAIN_DIR, pdf_name)
            shutil.copy2(rel_path, dst)
            print(f"Copied PDF artifact: {dst}")

    print("\n" + "="*80)
    print("SUCCESS: ALL ELSEVIER PATTERN RECOGNITION AND TPAMI DOCX/PDF BUILDS COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    build_all_elsevier_pr_docx()
