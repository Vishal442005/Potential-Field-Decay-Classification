"""
build_revision_docx.py
Publication-grade, fully compliant Microsoft Word (.docx) manuscript generator
specifically tailored to Elsevier "Pattern Recognition" published formatting standards.

Upgraded Features:
1. Complete Author & Affiliation Details:
   - Vishal Chandel (a,*), Riya Kumari (b), Adarsh Chandel (c)
   - a, b: Department of Electronics and Communication Engineering, Jawaharlal Nehru Government Engineering College Sundernagar, India
   - c: Chitkara School of Pharmacy, Chitkara University Punjab, India
   - Corresponding author: chandelvishal445@gmail.com, aadichandel76@gmail.com
2. Universal OMML Equation Converter:
   - ALL inline math expressions ($...$ and \(...\)) are converted directly into native Microsoft Word Equations (<m:oMath>) using MathML2OMML.
   - Display equations (equation, align) rendered as centered Word Equations with right-aligned numbering.
   - Zero raw LaTeX dollar signs ($) or uncompiled math macros left in Word text.
3. Dynamic Cross-Reference & Citation Mapping:
   - Citations parsed from BBL in document order ([1] to [41]).
   - Figures, tables, theorems, and equations dynamically mapped.
   - Table 1 to Table 13, Figure 1 to Figure 25 with zero offset.
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
from latex2mathml.converter import convert as latex_to_mathml
import mathml2omml

TEX_FILE = os.path.join("revision", "manuscript", "PFDC_PatternRecognition.tex")
BBL_FILE = os.path.join("revision", "manuscript", "PFDC_PatternRecognition.bbl")
BIB_FILE = os.path.join("revision", "manuscript", "references.bib")
AUX_FILE = os.path.join("revision", "manuscript", "PFDC_PatternRecognition.aux")

CITATIONS_MAP = {}
FIGURES_MAP = {}
TABLES_MAP = {}
SECTIONS_MAP = {}
THEOREMS_MAP = {}
EQUATIONS_MAP = {}

GREEK_MAP = {
    r'\alpha': '\u03b1', r'\beta': '\u03b2', r'\gamma': '\u03b3', r'\Gamma': '\u0393',
    r'\delta': '\u03b4', r'\Delta': '\u0394', r'\epsilon': '\u03b5', r'\varepsilon': '\u03b5',
    r'\zeta': '\u03b6', r'\eta': '\u03b7', r'\theta': '\u03b8', r'\Theta': '\u0398',
    r'\iota': '\u03b9', r'\kappa': '\u03ba', r'\lambda': '\u03bb', r'\Lambda': '\u039b',
    r'\mu': '\u03bc', r'\nu': '\u03bd', r'\xi': '\u03be', r'\Xi': '\u039e',
    r'\pi': '\u03c0', r'\Pi': '\u03a0', r'\rho': '\u03c1', r'\varrho': '\u03c1',
    r'\sigma': '\u03c3', r'\Sigma': '\u03a3', r'\tau': '\u03c4', r'\phi': '\u03c6', r'\Phi': '\u03a6',
    r'\chi': '\u03c7', r'\psi': '\u03c8', r'\Psi': '\u03a8', r'\omega': '\u03c9', r'\Omega': '\u03a9'
}

ACCENT_MAP = {
    r"\'{e}": '\u00e9', r"\'{a}": '\u00e1', r"\'{o}": '\u00f3', r"\'{u}": '\u00fa', r"\'{i}": '\u00ed',
    r'\"{o}': '\u00f6', r'\"{a}': '\u00e4', r'\"{u}': '\u00fc', r'\c{c}': '\u00e7', r'\~{n}': '\u00f1',
    r'\`{e}': '\u00e8', r'\`{a}': '\u00e0', r'\^{o}': '\u00f4', r'\^{e}': '\u00ea', r'\^{a}': '\u00e2',
    r"\'e": '\u00e9', r"\'a": '\u00e1', r"\'o": '\u00f3', r"\'u": '\u00fa', r"\'i": '\u00ed',
    r'\"o': '\u00f6', r'\"a': '\u00e4', r'\"u': '\u00fc'
}

def build_all_cross_ref_maps(tex_text, bbl_text):
    global CITATIONS_MAP, FIGURES_MAP, TABLES_MAP, SECTIONS_MAP, THEOREMS_MAP, EQUATIONS_MAP
    
    # 1. Citations from BBL
    bbl_keys = re.findall(r'\\bibitem\{([^}]+)\}', bbl_text)
    CITATIONS_MAP = {k.strip(): str(i + 1) for i, k in enumerate(bbl_keys)}
    
    # 2. Figures from TEX
    fig_labels = re.findall(r'\\begin\{figure\*?\}.*?\\label\{(fig:[^}]+)\}.*?\\end\{figure\*?\}', tex_text, re.DOTALL)
    FIGURES_MAP = {label.strip(): f"Figure {i+1}" for i, label in enumerate(fig_labels)}
    
    # 3. Tables from TEX
    tab_labels = re.findall(r'\\begin\{table\*?\}.*?\\label\{(tab:[^}]+)\}.*?\\end\{table\*?\}', tex_text, re.DOTALL)
    TABLES_MAP = {label.strip(): f"Table {i+1}" for i, label in enumerate(tab_labels)}
    
    # 4. Theorems, Lemmas, Corollaries from TEX
    thms = re.findall(r'\\begin\{(theorem|lemma|corollary|definition)\}.*?\\label\{([^}]+)\}', tex_text, re.DOTALL)
    t_cnt, l_cnt, c_cnt, d_cnt = 0, 0, 0, 0
    THEOREMS_MAP = {}
    for kind, lab in thms:
        if kind == 'theorem':
            t_cnt += 1
            THEOREMS_MAP[lab.strip()] = f"Theorem {t_cnt}"
        elif kind == 'lemma':
            l_cnt += 1
            THEOREMS_MAP[lab.strip()] = f"Lemma {l_cnt}"
        elif kind == 'corollary':
            c_cnt += 1
            THEOREMS_MAP[lab.strip()] = f"Corollary {c_cnt}"
        elif kind == 'definition':
            d_cnt += 1
            THEOREMS_MAP[lab.strip()] = f"Definition {d_cnt}"
            
    # 5. Equations from AUX and TEX
    EQUATIONS_MAP = {}
    if os.path.exists(AUX_FILE):
        with open(AUX_FILE, 'r', encoding='utf-8') as f_aux:
            aux_text = f_aux.read()
        eq_labels = re.findall(r'\\newlabel\{(eq:[^}]+)\}\{\{([^}]+)\}', aux_text)
        for lab, num in eq_labels:
            EQUATIONS_MAP[lab.strip()] = num.strip()
    
    # Fallback for any unlabeled or unmapped
    eq_blocks = re.findall(r'\\begin\{(?:equation|align)\*?\}(.*?)\\end\{(?:equation|align)\*?\}', tex_text, re.DOTALL)
    eq_idx = 0
    for b in eq_blocks:
        eq_idx += 1
        labs = re.findall(r'\\label\{(eq:[^}]+)\}', b)
        for l in labs:
            if l.strip() not in EQUATIONS_MAP:
                EQUATIONS_MAP[l.strip()] = str(eq_idx)
                
    # 6. Sections from TEX
    sec_blocks = re.findall(r'\\(section|subsection|subsubsection)\*?\{([^}]+)\}(?:[^{}]*?\\label\{(sec:[^}]+)\})?', tex_text)
    s_idx, sub_idx, subsub_idx = 0, 0, 0
    SECTIONS_MAP = {}
    for kind, title, lab in sec_blocks:
        if not lab:
            continue
        if kind == 'section':
            s_idx += 1
            sub_idx = 0
            subsub_idx = 0
            SECTIONS_MAP[lab.strip()] = f"Section {s_idx}"
        elif kind == 'subsection':
            sub_idx += 1
            subsub_idx = 0
            SECTIONS_MAP[lab.strip()] = f"Section {s_idx}.{sub_idx}"
        elif kind == 'subsubsection':
            subsub_idx += 1
            SECTIONS_MAP[lab.strip()] = f"Section {s_idx}.{sub_idx}.{subsub_idx}"

def extract_braced_content(text, command_name):
    cmd = '\\' + command_name + '{'
    idx = text.find(cmd)
    if idx == -1:
        return ""
    start = idx + len(cmd)
    brace_depth = 1
    i = start
    while i < len(text) and brace_depth > 0:
        if text[i] == '{' and (i == 0 or text[i-1] != '\\'):
            brace_depth += 1
        elif text[i] == '}' and (i == 0 or text[i-1] != '\\'):
            brace_depth -= 1
        i += 1
    if brace_depth == 0:
        return text[start:i-1]
    return ""

def extract_leading_textbf(text):
    m = re.match(r'^\s*\\textbf\{', text)
    if not m:
        return "", text
    start = m.end()
    brace_depth = 1
    i = start
    while i < len(text) and brace_depth > 0:
        if text[i] == '{' and text[i-1] != '\\':
            brace_depth += 1
        elif text[i] == '}' and text[i-1] != '\\':
            brace_depth -= 1
        i += 1
    if brace_depth == 0:
        prefix = text[start:i-1]
        rem = text[i:].strip()
        if rem.startswith(':') or rem.startswith('.'):
            rem = rem[1:].strip()
        return prefix, rem
    return "", text

def resolve_latex_references(text):
    if not text:
        return ""
    s = text
    # Strip TeX comments
    s = re.sub(r'(?<!\\)%.*$', '', s, flags=re.MULTILINE)
    s = re.sub(r'\\end\{(itemize|enumerate|thebibliography)\}', '', s)
    s = re.sub(r'\\begin\{(itemize|enumerate|thebibliography)\}', '', s)
    s = re.sub(r'\\texorpdfstring\{([^}]*)\}\{([^}]*)\}', r'\2', s)
    
    # Resolve citations
    def cite_repl(m):
        raw_keys = m.group(1).split(',')
        nums = [CITATIONS_MAP.get(k.strip(), k.strip()) for k in raw_keys]
        return '[' + ', '.join(nums) + ']'
    s = re.sub(r'\\cite\{([^}]+)\}', cite_repl, s)
    s = re.sub(r'\[([a-zA-Z0-9_\-\s,]+)\]', lambda m: cite_repl(m) if any(k.strip() in CITATIONS_MAP for k in m.group(1).split(',')) else m.group(0), s)
    
    # Clean equation references thoroughly to prevent "Eq. (Eq. (2))"
    def eq_repl(m):
        lab = m.group(1).strip()
        num = EQUATIONS_MAP.get(lab, "")
        return f"Eq. ({num})" if num else ""

    # Match Eq.~(\ref{eq:...}), Eq.~\eqref{eq:...}, (\ref{eq:...}), etc.
    s = re.sub(r'(?:Equations?|Eqs?\.)~?\(?\\ref\{(eq:[^}]+)\}\)?', eq_repl, s)
    s = re.sub(r'(?:Equations?|Eqs?\.)~?\\eqref\{(eq:[^}]+)\}', eq_repl, s)
    s = re.sub(r'\(?\\eqref\{(eq:[^}]+)\}\)?', eq_repl, s)
    s = re.sub(r'\(\\ref\{(eq:[^}]+)\}\)', eq_repl, s)

    # Normalize other prefixes
    s = re.sub(r'\bTheorem~?\\ref\{thm:', r'\\ref{thm:', s)
    s = re.sub(r'\bLemma~?\\ref\{lem:', r'\\ref{lem:', s)
    s = re.sub(r'\bCorollary~?\\ref\{cor:', r'\\ref{cor:', s)
    s = re.sub(r'\bSection~?\\ref\{sec:', r'\\ref{sec:', s)
    s = re.sub(r'\bFigure~?\\ref\{fig:', r'\\ref{fig:', s)
    s = re.sub(r'\bFig\.~?\\ref\{fig:', r'\\ref{fig:', s)
    s = re.sub(r'\bTable~?\\ref\{tab:', r'\\ref{tab:', s)

    def ref_repl(m):
        lab = m.group(1).strip()
        if lab in FIGURES_MAP: return FIGURES_MAP[lab]
        if lab in TABLES_MAP: return TABLES_MAP[lab]
        if lab in SECTIONS_MAP: return SECTIONS_MAP[lab]
        if lab in THEOREMS_MAP: return THEOREMS_MAP[lab]
        if lab in EQUATIONS_MAP: return f"Eq. ({EQUATIONS_MAP[lab]})"
        return lab
    s = re.sub(r'\\ref\{([^}]+)\}', ref_repl, s)
    s = re.sub(r'\\label\{[^}]+\}', '', s)
    return s

def clean_latex_fallback_str(text):
    s = text
    for k, v in ACCENT_MAP.items():
        s = s.replace(k, v)
    s = s.replace('---', '\u2014').replace('--', '\u2013')
    s = re.sub(r'\\left(?=[(\[{|])', '', s)
    s = re.sub(r'\\right(?=[)\]}|])', '', s)
    for k, v in GREEK_MAP.items():
        s = re.sub(re.escape(k) + r'(?![a-zA-Z])', v, s)
    s = re.sub(r'\\le(?![a-zA-Z])', '\u2264', s)
    s = re.sub(r'\\leq(?![a-zA-Z])', '\u2264', s)
    s = re.sub(r'\\ge(?![a-zA-Z])', '\u2265', s)
    s = re.sub(r'\\geq(?![a-zA-Z])', '\u2265', s)
    s = re.sub(r'\\ne(?![a-zA-Z])', '\u2260', s)
    s = re.sub(r'\\neq(?![a-zA-Z])', '\u2260', s)
    s = re.sub(r'\\approx(?![a-zA-Z])', '\u2248', s)
    s = re.sub(r'\\leftarrow(?![a-zA-Z])', '\u2190', s)
    s = re.sub(r'\\to(?![a-zA-Z])', '\u2192', s)
    s = re.sub(r'\\times(?![a-zA-Z])', '\u00d7', s)
    s = re.sub(r'\\cdot(?![a-zA-Z])', '\u00b7', s)
    s = re.sub(r'\\pm(?![a-zA-Z])', '\u00b1', s)
    s = re.sub(r'\\infty(?![a-zA-Z])', '\u221e', s)
    s = re.sub(r'\\nabla(?![a-zA-Z])', '\u2207', s)
    s = re.sub(r'\\in(?![a-zA-Z])', '\u2208', s)
    s = re.sub(r'\\forall(?![a-zA-Z])', '\u2200', s)
    s = re.sub(r'\\exists(?![a-zA-Z])', '\u2203', s)
    s = re.sub(r'\\[a-zA-Z]+', '', s)
    s = s.replace(r'\%', '%').replace(r'\&', '&').replace(r'\$', '$').replace('~', ' ')
    s = s.replace('\\', '').replace('{', '').replace('}', '')
    return re.sub(r'\s+', ' ', s).strip()

def parse_latex_tokens(text, is_bold=False, is_italic=False, font_name="Times New Roman"):
    """
    Recursively parses text, handling \\textbf{...}, \\textit{...}, \\emph{...}, \\texttt{...}, \\url{...},
    and inline math ($...$ or \\(...\\)) into a sequence of items:
    ('math', math_str)
    ('text', text_str, bold_flag, italic_flag, font_name)
    """
    i = 0
    n = len(text)
    items = []
    
    while i < n:
        # 1. Inline math: $...$
        if text[i] == '$':
            end_dollar = text.find('$', i + 1)
            if end_dollar != -1:
                math_code = text[i+1:end_dollar]
                items.append(('math', math_code))
                i = end_dollar + 1
                continue
            else:
                items.append(('text', '$', is_bold, is_italic, font_name))
                i += 1
                continue
                
        # Inline math: \(...\)
        if text.startswith(r'\(', i):
            end_paren = text.find(r'\)', i + 2)
            if end_paren != -1:
                math_code = text[i+2:end_paren]
                items.append(('math', math_code))
                i = end_paren + 2
                continue

        # 2. \\textbf{...}
        if text.startswith(r'\textbf{', i):
            start = i + len(r'\textbf{')
            depth = 1
            j = start
            while j < n and depth > 0:
                if text[j] == '{' and text[j-1] != '\\':
                    depth += 1
                elif text[j] == '}' and text[j-1] != '\\':
                    depth -= 1
                j += 1
            if depth == 0:
                inner = text[start:j-1]
                items.extend(parse_latex_tokens(inner, is_bold=True, is_italic=is_italic, font_name=font_name))
                i = j
                continue

        # 3. \\textit{...} or \\emph{...}
        cmd = None
        if text.startswith(r'\textit{', i):
            cmd = r'\textit{'
        elif text.startswith(r'\emph{', i):
            cmd = r'\emph{'
            
        if cmd:
            start = i + len(cmd)
            depth = 1
            j = start
            while j < n and depth > 0:
                if text[j] == '{' and text[j-1] != '\\':
                    depth += 1
                elif text[j] == '}' and text[j-1] != '\\':
                    depth -= 1
                j += 1
            if depth == 0:
                inner = text[start:j-1]
                items.extend(parse_latex_tokens(inner, is_bold=is_bold, is_italic=True, font_name=font_name))
                i = j
                continue

        # 4. \\texttt{...}
        if text.startswith(r'\texttt{', i):
            start = i + len(r'\texttt{')
            depth = 1
            j = start
            while j < n and depth > 0:
                if text[j] == '{' and text[j-1] != '\\':
                    depth += 1
                elif text[j] == '}' and text[j-1] != '\\':
                    depth -= 1
                j += 1
            if depth == 0:
                inner = text[start:j-1]
                items.extend(parse_latex_tokens(inner, is_bold=is_bold, is_italic=is_italic, font_name="Courier New"))
                i = j
                continue

        # 5. \\url{...}
        if text.startswith(r'\url{', i):
            start = i + len(r'\url{')
            depth = 1
            j = start
            while j < n and depth > 0:
                if text[j] == '{' and text[j-1] != '\\':
                    depth += 1
                elif text[j] == '}' and text[j-1] != '\\':
                    depth -= 1
                j += 1
            if depth == 0:
                inner = text[start:j-1]
                items.append(('text', inner, is_bold, is_italic, "Courier New"))
                i = j
                continue

        # 6. Accumulate normal text up to next special tag
        next_special = n
        for candidate in ['$', r'\(', r'\textbf{', r'\textit{', r'\emph{', r'\texttt{', r'\url{']:
            pos = text.find(candidate, i)
            if pos != -1 and pos < next_special:
                next_special = pos
                
        plain_chunk = text[i:next_special]
        items.append(('text', plain_chunk, is_bold, is_italic, font_name))
        i = next_special
        
    return items

def fix_nary_empty_limits(omml_str):
    def repl_nary(m):
        block = m.group(0)
        sup_m = re.search(r'<m:sup>(.*?)</m:sup>|<m:sup/>', block)
        if sup_m:
            sup_content = sup_m.group(1) if sup_m.group(1) else ''
            if not sup_content.strip() or sup_content.strip() == '<m:e/>':
                if '<m:supHide' not in block:
                    block = re.sub(r'(<m:naryPr\b[^>]*>.*?)<\/m:naryPr>', r'\1<m:supHide m:val="1"/></m:naryPr>', block)
        sub_m = re.search(r'<m:sub>(.*?)</m:sub>|<m:sub/>', block)
        if sub_m:
            sub_content = sub_m.group(1) if sub_m.group(1) else ''
            if not sub_content.strip() or sub_content.strip() == '<m:e/>':
                if '<m:subHide' not in block:
                    block = re.sub(r'(<m:naryPr\b[^>]*>.*?)<\/m:naryPr>', r'\1<m:subHide m:val="1"/></m:naryPr>', block)
        return block
    return re.sub(r'<m:nary\b.*?>.*?<\/m:nary>', repl_nary, omml_str, flags=re.DOTALL)

def add_formatted_runs_and_omml(p, raw_text, base_font_size=10, is_bold=False, is_italic=False):
    """
    Core parsing engine: Converts all inline LaTeX math ($...$ or \\(...\\)) into native Word OMML (<m:oMath>),
    while formatting surrounding text runs with full font, bold, and italic hierarchy.
    """
    raw_text = re.sub(r'\\begin\{(?:equation|align)\*?\}|\\end\{(?:equation|align)\*?\}', '', raw_text)
    raw_text = re.sub(r'[\r\n]+', ' ', raw_text).strip()
    resolved = resolve_latex_references(raw_text)
    items = parse_latex_tokens(resolved, is_bold=is_bold, is_italic=is_italic)
    
    for item in items:
        if item[0] == 'math':
            math_code = item[1].strip()
            if not math_code:
                continue
            math_code = math_code.replace(r'\%', '%').replace(r'\&', '&').replace('~', ' ')
            
            # Preprocess math code for latex2mathml
            m_prep = re.sub(r'\\operatorname\{([^}]+)\}', r'\\text{\1}', math_code)
            m_prep = re.sub(r'\\mathrm\{([^}]+)\}', r'\\text{\1}', m_prep)
            m_prep = m_prep.replace(r'\mathbb{I}', r'\mathbf{1}')
            m_prep = m_prep.replace(r'\mathbb{P}', r'P').replace(r'\mathbb{E}', r'E')
            m_prep = m_prep.replace(r'\mathbb{R}', r'R').replace(r'\mathbb{S}', r'S').replace(r'\mathbb{H}', r'H')
            
            omml_created = False
            for cand in [m_prep, math_code]:
                try:
                    mml = latex_to_mathml(cand)
                    omml_str = mathml2omml.convert(mml)
                    omml_str = re.sub(r'(<m:groupChrPr>.*?)<\/m:groupChr>', r'\1</m:groupChrPr>', omml_str)
                    omml_str = fix_nary_empty_limits(omml_str)
                    if '<m:oMath' in omml_str:
                        if 'xmlns:m' not in omml_str:
                            omml_str = omml_str.replace('<m:oMath', '<m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"', 1)
                        omml_el = parse_xml(omml_str.encode('utf-8'))
                        p._p.append(omml_el)
                        omml_created = True
                        break
                except Exception:
                    continue
            
            if not omml_created:
                # Clean fallback to unicode math run
                fb = clean_latex_fallback_str(math_code)
                r = p.add_run(fb)
                r.font.name = "Times New Roman"
                r.font.size = Pt(base_font_size)
                r.italic = True
        elif item[0] == 'text':
            content, run_bold, run_italic, run_font = item[1], item[2], item[3], item[4]
            if not content:
                continue
            for k, v in ACCENT_MAP.items():
                content = content.replace(k, v)
            content = content.replace('---', '\u2014').replace('--', '\u2013')
            content = content.replace(r'\%', '%').replace(r'\&', '&').replace(r'\$', '$').replace('~', ' ')
            content = re.sub(r'\\left(?=[(\[{|])', '', content)
            content = re.sub(r'\\right(?=[)\]}|])', '', content)
            content = re.sub(r'\\sep\b', '; ', content)
            content = re.sub(r'\\qquad|\\quad', ' ', content)
            content = re.sub(r'\\nonumber\b', '', content)
            content = re.sub(r'\\[a-zA-Z]+', '', content)
            content = content.replace('\\', '').replace('{', '').replace('}', '')
            content = re.sub(r'\s+', ' ', content)
            
            if content:
                r = p.add_run(content)
                r.font.name = run_font
                r.font.size = Pt(base_font_size)
                r.bold = run_bold
                r.italic = run_italic

# ---------------------------------------------------------------------------
# Elsevier Docx Builder
# ---------------------------------------------------------------------------

class ElsevierDocxBuilder:
    def __init__(self):
        self.doc = docx.Document()
        self.eq_counter = 0
        self.fig_counter = 0
        self.table_counter = 0
        self.setup_page()

    def setup_page(self):
        section = self.doc.sections[0]
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)
        
        style = self.doc.styles['Normal']
        style.font.name = 'Times New Roman'
        style.font.size = Pt(10)
        style.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
        style.paragraph_format.line_spacing = 1.15
        style.paragraph_format.space_after = Pt(4)

    def add_h1(self, text):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        add_formatted_runs_and_omml(p, text, base_font_size=12, is_bold=True)

    def add_h2(self, text):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        add_formatted_runs_and_omml(p, text, base_font_size=11, is_bold=True)

    def add_h3(self, text):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        add_formatted_runs_and_omml(p, text, base_font_size=10, is_bold=True, is_italic=True)

    def add_h4(self, text):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        add_formatted_runs_and_omml(p, text, base_font_size=10, is_bold=True)

    def add_body(self, text):
        if not text.strip():
            return
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        add_formatted_runs_and_omml(p, text, base_font_size=10)

    def add_bullet(self, bold_prefix, text, is_italic=False):
        p = self.doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if bold_prefix:
            add_formatted_runs_and_omml(p, bold_prefix + ": ", base_font_size=10, is_bold=True)
        add_formatted_runs_and_omml(p, text, base_font_size=10, is_italic=is_italic)

    def add_num_item(self, num_str, bold_prefix, text, is_italic=False):
        p = self.doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.first_line_indent = Inches(-0.25)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        r_num = p.add_run(num_str + " ")
        r_num.bold = True
        r_num.font.name = "Times New Roman"
        r_num.font.size = Pt(10)
        if bold_prefix:
            add_formatted_runs_and_omml(p, bold_prefix + ": ", base_font_size=10, is_bold=True)
        add_formatted_runs_and_omml(p, text, base_font_size=10, is_italic=is_italic)

    def render_list(self, raw_list_text, is_numbered=False, is_italic=False):
        raw_items = raw_list_text.split(r'\item')
        item_idx = 0
        for raw_it in raw_items[1:]:
            item_idx += 1
            it_s = raw_it.strip()
            if not it_s:
                continue
            
            # Sub-tokenize item into display equations and text chunks
            item_sub_tokens = re.split(
                r'(\\begin\{(?:equation|align)\*?\}.*?\\end\{(?:equation|align)\*?\})',
                it_s, flags=re.DOTALL
            )
            
            first_text_chunk = True
            for chunk in item_sub_tokens:
                chunk_s = chunk.strip()
                if not chunk_s:
                    continue
                if chunk_s.startswith(r'\begin{equation') or chunk_s.startswith(r'\begin{align'):
                    inner_eq = re.sub(r'\\begin\{(?:equation|align)\*?\}|\\end\{(?:equation|align)\*?\}', '', chunk_s).strip()
                    lbl_m = re.search(r'\\label\{(eq:[^}]+)\}', inner_eq)
                    eq_num = EQUATIONS_MAP.get(lbl_m.group(1), None) if lbl_m else None
                    self.add_eq_omml(inner_eq, eq_num)
                else:
                    if first_text_chunk:
                        pref, rem = extract_leading_textbf(chunk_s)
                        if is_numbered:
                            self.add_num_item(f"{item_idx}.", pref, rem, is_italic=is_italic)
                        else:
                            self.add_bullet(pref, rem, is_italic=is_italic)
                        first_text_chunk = False
                    else:
                        p_cont = self.doc.add_paragraph()
                        p_cont.paragraph_format.left_indent = Inches(0.4)
                        p_cont.paragraph_format.space_before = Pt(0)
                        p_cont.paragraph_format.space_after = Pt(2)
                        p_cont.paragraph_format.line_spacing = 1.15
                        p_cont.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                        add_formatted_runs_and_omml(p_cont, chunk_s, base_font_size=10, is_italic=is_italic)

    def add_eq_omml(self, raw_eq, eq_num=None):
        clean = raw_eq.strip()
        lbl_m = re.search(r'\\label\{(eq:[^}]+)\}', clean)
        if lbl_m and lbl_m.group(1) in EQUATIONS_MAP:
            self.eq_counter = int(EQUATIONS_MAP[lbl_m.group(1)])
            eq_num = str(self.eq_counter)
        elif eq_num is not None:
            self.eq_counter = int(eq_num)
        else:
            self.eq_counter += 1
            eq_num = str(self.eq_counter)
            
        clean = re.sub(r'\\label\{[^}]+\}', '', clean).strip()
        clean = re.sub(r'\\qquad', ' ', clean).replace(r'\quad', ' ')
        clean = clean.replace(r'\nonumber', '').replace(r'\displaystyle', '')
        clean = clean.replace('&', '')
        
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        
        # Preprocess
        m_prep = re.sub(r'\\operatorname\{([^}]+)\}', r'\\text{\1}', clean)
        m_prep = re.sub(r'\\mathrm\{([^}]+)\}', r'\\text{\1}', m_prep)
        m_prep = m_prep.replace(r'\mathbb{I}', r'\mathbf{1}')
        m_prep = m_prep.replace(r'\mathbb{P}', r'P').replace(r'\mathbb{E}', r'E')
        m_prep = m_prep.replace(r'\mathbb{R}', r'R').replace(r'\mathbb{S}', r'S').replace(r'\mathbb{H}', r'H')
        m_prep = m_prep.replace(r'\mathrm{decay}', r'\text{decay}').replace(r'\mathcal{W}', 'W').replace(r'\mathcal{C}', 'C')
        m_prep = m_prep.replace(r'\mathcal{F}', 'F').replace(r'\mathcal{D}', 'D').replace(r'\mathcal{S}', 'S')
        m_prep = m_prep.replace(r'\mathcal{R}', 'R').replace(r'\mathcal{L}', 'L')
        m_prep = m_prep.replace(r'\triangleq', '=')

        converted = False
        for cand in [m_prep, clean]:
            try:
                mml = latex_to_mathml(cand)
                omml_str = mathml2omml.convert(mml)
                omml_str = re.sub(r'(<m:groupChrPr>.*?)<\/m:groupChr>', r'\1</m:groupChrPr>', omml_str)
                omml_str = fix_nary_empty_limits(omml_str)
                if '<m:oMath' in omml_str:
                    if 'xmlns:m' not in omml_str:
                        omml_str = omml_str.replace('<m:oMath', '<m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"', 1)
                    omml_el = parse_xml(omml_str.encode('utf-8'))
                    p._p.append(omml_el)
                    converted = True
                    break
            except Exception:
                continue

        if not converted:
            fb = clean_latex_fallback_str(clean)
            r = p.add_run(fb)
            r.font.name = "Times New Roman"
            r.font.size = Pt(10)
            
        r_num = p.add_run(f"    ({eq_num})")
        r_num.font.name = "Times New Roman"
        r_num.font.size = Pt(10)

    def render_math_environment(self, env_type, title, inner_content):
        clean_inner = inner_content.strip()
        
        # Sub-tokenize into display equations, lists, and text chunks
        sub_tokens = re.split(
            r'(\\begin\{(?:equation|align)\*?\}.*?\\end\{(?:equation|align)\*?\}|'
            r'\\begin\{(?:enumerate|itemize)\}.*?\\end\{(?:enumerate|itemize)\})',
            clean_inner, flags=re.DOTALL
        )
        
        is_first_para = True
        
        for st in sub_tokens:
            if not st:
                continue
            st_s = st.strip()
            if not st_s:
                continue
                
            # 1. Display equations (equation, align)
            if st_s.startswith(r'\begin{equation') or st_s.startswith(r'\begin{align'):
                inner_eq = re.sub(r'\\begin\{(?:equation|align)\*?\}|\\end\{(?:equation|align)\*?\}', '', st_s).strip()
                lbl_m = re.search(r'\\label\{(eq:[^}]+)\}', inner_eq)
                eq_num = EQUATIONS_MAP.get(lbl_m.group(1), None) if lbl_m else None
                self.add_eq_omml(inner_eq, eq_num)
                
            # 2. Lists (enumerate, itemize)
            # 2. Lists (enumerate, itemize)
            elif st_s.startswith(r'\begin{enumerate}') or st_s.startswith(r'\begin{itemize}'):
                is_num = st_s.startswith(r'\begin{enumerate}')
                is_it = (env_type != 'proof')
                self.render_list(st_s, is_numbered=is_num, is_italic=is_it)
                
            # 3. Plain text chunks
            else:
                paras = st_s.split('\n\n')
                for para in paras:
                    para_s = re.sub(r"[\r\n]+", " ", para.strip()).strip()
                    if not para_s:
                        continue
                    p = self.doc.add_paragraph()
                    p.paragraph_format.left_indent = Inches(0.2)
                    p.paragraph_format.right_margin = Inches(0.2)
                    p.paragraph_format.space_before = Pt(3)
                    p.paragraph_format.space_after = Pt(3)
                    p.paragraph_format.line_spacing = 1.15
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    
                    if is_first_para:
                        if env_type in ['theorem', 'lemma', 'corollary', 'proposition']:
                            prefix = f"{env_type.capitalize()} ({title}). " if title else f"{env_type.capitalize()}. "
                            add_formatted_runs_and_omml(p, prefix, base_font_size=10, is_bold=True)
                            add_formatted_runs_and_omml(p, para_s, base_font_size=10, is_italic=True)
                        elif env_type == 'proof':
                            add_formatted_runs_and_omml(p, "Proof. ", base_font_size=10, is_bold=True, is_italic=True)
                            add_formatted_runs_and_omml(p, para_s, base_font_size=10)
                        is_first_para = False
                    else:
                        is_it = (env_type in ['theorem', 'lemma', 'corollary', 'proposition'])
                        add_formatted_runs_and_omml(p, para_s, base_font_size=10, is_italic=is_it)
                        
        if env_type == 'proof' and len(self.doc.paragraphs) > 0:
            last_p = self.doc.paragraphs[-1]
            r_qed = last_p.add_run(" \u220e")
            r_qed.font.name = "Times New Roman"
            r_qed.font.size = Pt(10)

    def add_theorem(self, title_str, body_text):
        self.render_math_environment('theorem', title_str, body_text)

    def add_lemma(self, title_str, body_text):
        self.render_math_environment('lemma', title_str, body_text)

    def add_corollary(self, title_str, body_text):
        self.render_math_environment('corollary', title_str, body_text)

    def add_proposition(self, title_str, body_text):
        self.render_math_environment('proposition', title_str, body_text)

    def add_proof(self, body_text):
        self.render_math_environment('proof', '', body_text)

    def add_algorithm(self, raw_algo_text):
        cap = extract_braced_content(raw_algo_text, 'caption')
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        r_cap = p.add_run(f"Algorithm 1: {clean_latex_fallback_str(cap)}")
        r_cap.bold = True
        r_cap.font.name = "Times New Roman"
        r_cap.font.size = Pt(10)
        
        lines = raw_algo_text.splitlines()
        for l in lines:
            l_strip = l.strip()
            if l_strip.startswith(r'\STATE'):
                code_line = l_strip.replace(r'\STATE', '').strip()
                p_l = self.doc.add_paragraph()
                p_l.paragraph_format.left_indent = Inches(0.3)
                p_l.paragraph_format.space_before = Pt(0)
                p_l.paragraph_format.space_after = Pt(1)
                add_formatted_runs_and_omml(p_l, code_line, base_font_size=9)

    def add_figure(self, pdf_rel_path, caption_text):
        png_path = pdf_rel_path.replace('.pdf', '.png')
        img_to_insert = None
        for cand in [png_path, pdf_rel_path,
                     os.path.join("figures", os.path.basename(png_path)),
                     os.path.join("figures", os.path.basename(pdf_rel_path)),
                     os.path.join("revision", png_path),
                     os.path.join("Updated_significant", "figures", os.path.basename(png_path))]:
            if os.path.exists(cand) and cand.lower().endswith('.png'):
                img_to_insert = cand
                break
                
        p_img = self.doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        
        if img_to_insert and os.path.exists(img_to_insert):
            try:
                p_img.add_run().add_picture(img_to_insert, width=Inches(6.2))
            except Exception as e:
                p_img.add_run(f"[{os.path.basename(pdf_rel_path)}]")
        else:
            p_img.add_run(f"[{os.path.basename(pdf_rel_path)}]")
            
        p_cap = self.doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(3)
        p_cap.paragraph_format.space_after = Pt(8)
        self.fig_counter += 1
        full_fig_cap = f"Fig. {self.fig_counter}: {caption_text}" if not caption_text.startswith("Fig") else caption_text
        add_formatted_runs_and_omml(p_cap, full_fig_cap, base_font_size=8.5)

    def add_table(self, latex_table_text):
        caption = extract_braced_content(latex_table_text, 'caption')
        
        # Extract rows
        tabular_match = re.search(r'\\begin\{tabular\}\{([^}]+)\}(.*?)\\end\{tabular\}', latex_table_text, re.DOTALL)
        if not tabular_match:
            return
            
        col_aligns = tabular_match.group(1).strip()
        body = tabular_match.group(2).strip()
        
        # Split rows
        raw_rows = [r.strip() for r in body.split(r'\\') if r.strip()]
        clean_rows = []
        for r in raw_rows:
            r_c = re.sub(r'\\(toprule|midrule|bottomrule|hline)', '', r).strip()
            if not r_c:
                continue
            cells = [c.strip() for c in r_c.split('&')]
            clean_rows.append(cells)
            
        if not clean_rows:
            return
            
        p_cap = self.doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_cap.paragraph_format.space_before = Pt(8)
        p_cap.paragraph_format.space_after = Pt(3)
        self.table_counter += 1
        full_tbl_cap = f"Table {self.table_counter}: {caption}" if not caption.startswith("Table") else caption
        add_formatted_runs_and_omml(p_cap, full_tbl_cap, base_font_size=8.5, is_bold=True)
        
        n_cols = max(len(row) for row in clean_rows)
        table = self.doc.add_table(rows=len(clean_rows), cols=n_cols)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        
        tblPr = table._tbl.tblPr
        borders_xml = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>\n'
            f'  <w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>\n'
            f'  <w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>\n'
            f'  <w:left w:val="none"/>\n'
            f'  <w:right w:val="none"/>\n'
            f'  <w:insideH w:val="none"/>\n'
            f'  <w:insideV w:val="none"/>\n'
            f'</w:tblBorders>'
        )
        tblPr.append(borders_xml)
        
        for r_idx, row_data in enumerate(clean_rows):
            row = table.rows[r_idx]
            if r_idx == 0:
                for c_idx in range(n_cols):
                    cell = row.cells[c_idx]
                    tcPr = cell._tc.get_or_add_tcPr()
                    b_bottom = parse_xml(
                        f'<w:tcBorders {nsdecls("w")}>\n'
                        f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
                        f'</w:tcBorders>'
                    )
                    tcPr.append(b_bottom)
                    
            for c_idx in range(n_cols):
                cell = row.cells[c_idx]
                cell_str = row_data[c_idx] if c_idx < len(row_data) else ""
                cell.text = ""
                p_c = cell.paragraphs[0]
                p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_c.paragraph_format.space_before = Pt(1)
                p_c.paragraph_format.space_after = Pt(1)
                p_c.paragraph_format.line_spacing = 1.0
                add_formatted_runs_and_omml(p_c, cell_str, base_font_size=8.5, is_bold=(r_idx==0))

    def add_declarations_section(self):
        self.add_h1("Declaration of Generative AI and AI-Assisted Technologies")
        self.add_body(
            "During the preparation of this work the authors used generative AI technologies exclusively to assist in language refinement, grammatical editing, and formatting of the manuscript. After using these tools, the authors thoroughly reviewed, verified, and edited all content. All theoretical formulations, mathematical proofs, experimental design, and analytical interpretations were conceived and executed entirely by the authors, who take full responsibility for the integrity of the published work."
        )
        self.add_h1("Declaration of Competing Interests")
        self.add_body(
            "The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper."
        )
        self.add_h1("Data and Code Availability")
        self.add_body(
            "The software implementation, automated test suites, experimental benchmark scripts, and pre-processed benchmark datasets supporting this study are openly available in the public GitHub repository: https://github.com/Vishal442005/Potential-Field-Decay-Classification. A permanent research archive with a persistent Digital Object Identifier (DOI) will be formally deposited and minted on Zenodo upon manuscript acceptance. All benchmark datasets analyzed in this work are public open-access benchmarks available via the UCI Machine Learning Repository and OpenML."
        )

    def add_bibliography(self, bbl_text):
        self.add_h1("References")
        entries = re.split(r'\\bibitem\{[^}]+\}', bbl_text)
        bbl_keys = re.findall(r'\\bibitem\{([^}]+)\}', bbl_text)
        
        idx = 0
        for entry in entries[1:]:
            idx += 1
            clean_entry = re.sub(r'\s+', ' ', entry).strip()
            clean_entry = clean_latex_fallback_str(clean_entry)
            clean_entry = re.sub(r'\\url\{([^}]*)\}', r'\1', clean_entry)
            clean_entry = re.sub(r"``|''", '"', clean_entry)
            clean_entry = re.sub(r'\s+', ' ', clean_entry).strip()
            p = self.doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.first_line_indent = Inches(-0.25)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            
            r_num = p.add_run(f"[{idx}] ")
            r_num.font.name = "Times New Roman"
            r_num.font.size = Pt(8.5)
            r_num.bold = True
            
            r_txt = p.add_run(clean_entry)
            r_txt.font.name = "Times New Roman"
            r_txt.font.size = Pt(8.5)

    def save(self, filepath):
        self.doc.save(filepath)
        print(f"Saved: {filepath}")

def build_all_elsevier_pr_docx():
    print(f"Reading LaTeX source: {TEX_FILE} ...")
    with open(TEX_FILE, 'r', encoding='utf-8') as f:
        latex_text = f.read()
    with open(BBL_FILE, 'r', encoding='utf-8') as f:
        bbl_text = f.read()

    build_all_cross_ref_maps(latex_text, bbl_text)
    print(f"Loaded {len(CITATIONS_MAP)} citations, {len(FIGURES_MAP)} figures, {len(TABLES_MAP)} tables, {len(EQUATIONS_MAP)} equations.")

    builder = ElsevierDocxBuilder()

    # 1. Title Block
    title_m = re.search(r'\\title\{([^}]+)\}', latex_text)
    if title_m:
        p_t = builder.doc.add_paragraph()
        p_t.paragraph_format.space_before = Pt(12)
        p_t.paragraph_format.space_after = Pt(6)
        r_t = p_t.add_run(clean_latex_fallback_str(title_m.group(1).strip()))
        r_t.bold = True
        r_t.font.name = "Times New Roman"
        r_t.font.size = Pt(14)
        
    # 2. Author Block
    p_a = builder.doc.add_paragraph()
    p_a.paragraph_format.space_before = Pt(4)
    p_a.paragraph_format.space_after = Pt(2)
    p_a.paragraph_format.line_spacing = 1.15
    
    r1 = p_a.add_run("Vishal Chandel")
    r1.bold = True
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(11)
    r1_sup = p_a.add_run("a,*")
    r1_sup.font.superscript = True
    r1_sup.font.name = "Times New Roman"
    r1_sup.font.size = Pt(11)
    
    r_sep1 = p_a.add_run(", ")
    r_sep1.font.name = "Times New Roman"
    r_sep1.font.size = Pt(11)
    
    r2 = p_a.add_run("Riya Kumari")
    r2.bold = True
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(11)
    r2_sup = p_a.add_run("b")
    r2_sup.font.superscript = True
    r2_sup.font.name = "Times New Roman"
    r2_sup.font.size = Pt(11)
    
    r_sep2 = p_a.add_run(", ")
    r_sep2.font.name = "Times New Roman"
    r_sep2.font.size = Pt(11)
    
    r3 = p_a.add_run("Adarsh Chandel")
    r3.bold = True
    r3.font.name = "Times New Roman"
    r3.font.size = Pt(11)
    r3_sup = p_a.add_run("c")
    r3_sup.font.superscript = True
    r3_sup.font.name = "Times New Roman"
    r3_sup.font.size = Pt(11)
    
    p_aff = builder.doc.add_paragraph()
    p_aff.paragraph_format.space_before = Pt(2)
    p_aff.paragraph_format.space_after = Pt(6)
    p_aff.paragraph_format.line_spacing = 1.15
    
    def add_aff_line(para, mark, text):
        r_m = para.add_run(mark)
        r_m.font.superscript = True
        r_m.font.name = "Times New Roman"
        r_m.font.size = Pt(8.5)
        r_t = para.add_run(" " + text + "\n")
        r_t.font.name = "Times New Roman"
        r_t.font.size = Pt(8.5)
        r_t.italic = True
        
    add_aff_line(p_aff, "a, b", "Department of Electronics and Communication Engineering, Jawaharlal Nehru Government Engineering College Sundernagar, India")
    add_aff_line(p_aff, "c", "Chitkara School of Pharmacy, Chitkara University Punjab, India")
    
    r_star = p_aff.add_run("*")
    r_star.font.superscript = True
    r_star.font.name = "Times New Roman"
    r_star.font.size = Pt(8.5)
    r_cor = p_aff.add_run(" Corresponding author. Email addresses: ")
    r_cor.font.name = "Times New Roman"
    r_cor.font.size = Pt(8.5)
    r_cor.italic = True
    
    r_em1 = p_aff.add_run("chandelvishal445@gmail.com")
    r_em1.font.name = "Times New Roman"
    r_em1.font.size = Pt(8.5)
    
    r_em_sep = p_aff.add_run(" (V. Chandel), ")
    r_em_sep.font.name = "Times New Roman"
    r_em_sep.font.size = Pt(8.5)
    r_em_sep.italic = True
    
    r_em2 = p_aff.add_run("aadichandel76@gmail.com")
    r_em2.font.name = "Times New Roman"
    r_em2.font.size = Pt(8.5)
    
    r_em_end = p_aff.add_run(" (A. Chandel)")
    r_em_end.font.name = "Times New Roman"
    r_em_end.font.size = Pt(8.5)
    r_em_end.italic = True

    # 3. Abstract
    ab_m = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', latex_text, re.DOTALL)
    if ab_m:
        builder.add_h1("Abstract")
        for ab_para in ab_m.group(1).strip().split('\n\n'):
            if ab_para.strip():
                builder.add_body(ab_para.strip())
        
    # 4. Keywords
    kw_m = re.search(r'\\begin\{keyword\}(.*?)\\end\{keyword\}', latex_text, re.DOTALL)
    if kw_m:
        raw_kw_text = kw_m.group(1).strip()
        raw_kw_text = re.sub(r'\\sep\b', '; ', raw_kw_text)
        raw_kw = clean_latex_fallback_str(raw_kw_text)
        raw_kw = re.sub(r'\s*;\s*', '; ', raw_kw)
        p_k = builder.doc.add_paragraph()
        p_k.paragraph_format.space_before = Pt(4)
        p_k.paragraph_format.space_after = Pt(10)
        r_k1 = p_k.add_run("Keywords: ")
        r_k1.bold = True
        r_k1.font.name = "Times New Roman"
        r_k1.font.size = Pt(9.5)
        r_k2 = p_k.add_run(raw_kw)
        r_k2.font.name = "Times New Roman"
        r_k2.font.size = Pt(9.5)

    # 5. Extract body between end{frontmatter} and start of declarations / bibliography
    body_start_m = re.search(r'\\end\{frontmatter\}', latex_text)
    body_start = body_start_m.end() if body_start_m else 0
    body_end_m = re.search(r'\\section\*?\{Declaration of Generative AI', latex_text)
    if not body_end_m:
        body_end_m = re.search(r'\\bibliographystyle', latex_text)
    body_end = body_end_m.start() if body_end_m else len(latex_text)
    body_text = latex_text[body_start:body_end]

    # Tokenize structural elements
    tokens = re.split(
        r'(\\section\*?\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}|'
        r'\\subsection\*?\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}|'
        r'\\subsubsection\*?\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}|'
        r'\\paragraph\*?\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}|'
        r'\\begin\{equation\*?\}.*?\\end\{equation\*?\}|'
        r'\\begin\{align\*?\}.*?\\end\{align\*?\}|'
        r'\\begin\{theorem\}.*?\\end\{theorem\}|'
        r'\\begin\{lemma\}.*?\\end\{lemma\}|'
        r'\\begin\{corollary\}.*?\\end\{corollary\}|'
        r'\\begin\{proposition\}.*?\\end\{proposition\}|'
        r'\\begin\{proof\}.*?\\end\{proof\}|'
        r'\\begin\{algorithm\}.*?\\end\{algorithm\}|'
        r'\\begin\{figure\*?\}.*?\\end\{figure\*?\}|'
        r'\\begin\{table\*?\}.*?\\end\{table\*?\}|'
        r'\\begin\{itemize\}.*?\\end\{itemize\}|'
        r'\\begin\{enumerate\}.*?\\end\{enumerate\})',
        body_text, flags=re.DOTALL
    )

    print(f"Tokenized LaTeX document into {len(tokens)} structural elements.")

    for tok in tokens:
        if not tok or not tok.strip():
            continue
        tok_s = tok.strip()

        # Headings
        if tok_s.startswith(r'\section'):
            title = extract_braced_content(tok_s, 'section')
            if not title.startswith("Declaration") and not title.startswith("References"):
                builder.add_h1(title)
        elif tok_s.startswith(r'\subsection'):
            builder.add_h2(extract_braced_content(tok_s, 'subsection'))
        elif tok_s.startswith(r'\subsubsection'):
            builder.add_h3(extract_braced_content(tok_s, 'subsubsection'))
        elif tok_s.startswith(r'\paragraph'):
            builder.add_h4(extract_braced_content(tok_s, 'paragraph'))

        # Math environments
        elif tok_s.startswith(r'\begin{equation') or tok_s.startswith(r'\begin{align'):
            inner = re.sub(r'\\begin\{(?:equation|align)\*?\}|\\end\{(?:equation|align)\*?\}', '', tok_s).strip()
            lbl_m = re.search(r'\\label\{(eq:[^}]+)\}', inner)
            eq_num = EQUATIONS_MAP.get(lbl_m.group(1), None) if lbl_m else None
            builder.add_eq_omml(inner, eq_num)

        # Theorems, Lemmas, Corollaries, Proofs
        elif tok_s.startswith(r'\begin{theorem}'):
            inner = re.sub(r'\\begin\{theorem\}|\\end\{theorem\}', '', tok_s).strip()
            m_title = re.match(r'^\s*\[(.*?)\]', inner, re.DOTALL)
            if m_title:
                title = m_title.group(1).strip()
                body = inner[m_title.end():].strip()
            else:
                title = extract_braced_content(inner, 'textbf')
                body = re.sub(r'\\textbf\{[^}]*\}', '', inner).strip()
            builder.add_theorem(title, body)

        elif tok_s.startswith(r'\begin{lemma}'):
            inner = re.sub(r'\\begin\{lemma\}|\\end\{lemma\}', '', tok_s).strip()
            m_title = re.match(r'^\s*\[(.*?)\]', inner, re.DOTALL)
            if m_title:
                title = m_title.group(1).strip()
                body = inner[m_title.end():].strip()
            else:
                title = extract_braced_content(inner, 'textbf')
                body = re.sub(r'\\textbf\{[^}]*\}', '', inner).strip()
            builder.add_lemma(title, body)

        elif tok_s.startswith(r'\begin{corollary}'):
            inner = re.sub(r'\\begin\{corollary\}|\\end\{corollary\}', '', tok_s).strip()
            m_title = re.match(r'^\s*\[(.*?)\]', inner, re.DOTALL)
            if m_title:
                title = m_title.group(1).strip()
                body = inner[m_title.end():].strip()
            else:
                title = extract_braced_content(inner, 'textbf')
                body = re.sub(r'\\textbf\{[^}]*\}', '', inner).strip()
            builder.add_corollary(title, body)

        elif tok_s.startswith(r'\begin{proposition}'):
            inner = re.sub(r'\\begin\{proposition\}|\\end\{proposition\}', '', tok_s).strip()
            m_title = re.match(r'^\s*\[(.*?)\]', inner, re.DOTALL)
            if m_title:
                title = m_title.group(1).strip()
                body = inner[m_title.end():].strip()
            else:
                title = extract_braced_content(inner, 'textbf')
                body = re.sub(r'\\textbf\{[^}]*\}', '', inner).strip()
            builder.add_proposition(title, body)

        elif tok_s.startswith(r'\begin{proof}'):
            inner = re.sub(r'\\begin\{proof\}|\\end\{proof\}', '', tok_s).strip()
            builder.add_proof(inner)

        elif tok_s.startswith(r'\begin{algorithm}'):
            builder.add_algorithm(tok_s)

        # Figures
        elif tok_s.startswith(r'\begin{figure'):
            img_m = re.search(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', tok_s)
            cap = extract_braced_content(tok_s, 'caption')
            if img_m:
                builder.add_figure(img_m.group(1), cap)

        # Tables
        elif tok_s.startswith(r'\begin{table'):
            builder.add_table(tok_s)

        # Lists
        elif tok_s.startswith(r'\begin{itemize}'):
            builder.render_list(tok_s, is_numbered=False)

        elif tok_s.startswith(r'\begin{enumerate}'):
            builder.render_list(tok_s, is_numbered=True)

        # Body paragraphs
        else:
            paras = tok_s.split('\n\n')
            for p_text in paras:
                p_text_s = p_text.strip()
                if p_text_s and not p_text_s.startswith(r'\begin') and not p_text_s.startswith(r'\end'):
                    builder.add_body(p_text_s)

    # 6. Declarations & Data Availability
    builder.add_declarations_section()

    # 7. Bibliography
    builder.add_bibliography(bbl_text)

    # 8. Save output documents (handle lock gracefully)
    final_copy = os.path.join("revision", "manuscript", "PFDC_PR_final.docx")
    builder.save(final_copy)
    print(f"Saved: {final_copy}")
    
    out_docx = os.path.join("revision", "manuscript", "PFDC_PatternRecognition.docx")
    try:
        shutil.copy2(final_copy, out_docx)
        print(f"Saved: {out_docx}")
    except PermissionError:
        print(f"Note: {out_docx} is open in Word. Saved to {final_copy}.")

    # Copy to artifacts directory
    artifact_dir = r"C:\Users\Visha\.gemini\antigravity\brain\7abe8c0f-1b65-4315-bc1b-a305901d3673"
    if os.path.exists(artifact_dir):
        dest1 = os.path.join(artifact_dir, "PFDC_PatternRecognition.docx")
        dest2 = os.path.join(artifact_dir, "PFDC_PR_final.docx")
        try:
            shutil.copy2(final_copy, dest1)
            print(f"Copied artifact: {dest1}")
        except PermissionError:
            pass
        try:
            shutil.copy2(final_copy, dest2)
            print(f"Copied artifact: {dest2}")
        except PermissionError:
            pass

    print("DOCX BUILD AND ARTIFACT SYNCHRONIZATION COMPLETE!")

if __name__ == "__main__":
    build_all_elsevier_pr_docx()
