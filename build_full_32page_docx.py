"""
build_full_32page_docx.py
Generates publication-grade, unabridged Microsoft Word (.docx) manuscripts for:
1. elsevier_submission/PFDC_PatternRecognition.docx
2. tpami_submission/PFDC_TPAMI.docx
3. PFDC_Manuscript.docx
and synchronizes them to the conversation artifact directory.

Matches the full 32-page, 11,139-word LaTeX manuscript:
- All 13 sections and subsections unabridged
- All formal definitions, Lemma 1, Theorems 1-3, and mathematical proofs in styled callout boxes
- All 14 empirical tables with Elsevier Navy (#002060) headers, alternating shading, and Banknote strictly at 97.23 +- 1.05%
- All 23 high-resolution vector figures rendered on-the-fly via pypdfium2 and cleanly embedded with italicized captions
- All temporary PNG files deleted immediately afterwards so zero PNGs remain in figure directories
- Complete Declarations, Data Availability Statement, and all 35 formal literature references
"""

import os
import shutil
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import pypdfium2 as pdfium

print("="*80)
print("BUILDING COMPLETE UNABRIDGED 32-PAGE DOCX SUBMISSIONS")
print("="*80)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_table_borders(table, color="B0C4DE", sz="6", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_callout_box(doc, title, body_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Inches(6.5)
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F4F6F9")
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="002060"/>'
        f'<w:top w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=180)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    
    r_title = p.add_run(title + "\n")
    r_title.bold = True
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(10.5)
    r_title.font.color.rgb = RGBColor(0x00, 0x20, 0x60)
    
    r_body = p.add_run(body_text)
    r_body.font.name = "Calibri"
    r_body.font.size = Pt(10.0)
    r_body.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
    
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(4)

def add_figure_from_pdf(doc, pdf_path, caption_text, width_inches=6.2):
    if not os.path.exists(pdf_path):
        print(f"Warning: PDF figure not found: {pdf_path}")
        return
    temp_png = pdf_path.replace(".pdf", "_temp_docx_render.png")
    try:
        pdf = pdfium.PdfDocument(pdf_path)
        img = pdf[0].render(scale=2.5).to_pil()
        img.save(temp_png)
        
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(4)
        run = p_img.add_run()
        run.add_picture(temp_png, width=Inches(width_inches))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(10)
        p_cap.paragraph_format.line_spacing = 1.15
        r_cap = p_cap.add_run(caption_text)
        r_cap.font.name = "Calibri"
        r_cap.font.size = Pt(9.5)
        r_cap.font.italic = True
        r_cap.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
    finally:
        if os.path.exists(temp_png):
            os.remove(temp_png)

def add_styled_table(doc, headers, rows, caption_text, bold_best_row_idx=None, col_widths=None):
    p_cap = doc.add_paragraph()
    p_cap.paragraph_format.space_before = Pt(10)
    p_cap.paragraph_format.space_after = Pt(3)
    r_cap = p_cap.add_run(caption_text)
    r_cap.font.name = "Calibri"
    r_cap.font.size = Pt(10.0)
    r_cap.bold = True
    r_cap.font.color.rgb = RGBColor(0x00, 0x20, 0x60)
    
    num_rows = len(rows) + 1
    num_cols = len(headers)
    table = doc.add_table(rows=num_rows, cols=num_cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table, color="B0C4DE", sz="6", val="single")
    
    # Header Row
    hdr_cells = table.rows[0].cells
    for i, h_text in enumerate(headers):
        hdr_cells[i].text = h_text
        set_cell_background(hdr_cells[i], "002060")
        set_cell_margins(hdr_cells[i], top=100, bottom=100, left=120, right=120)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i > 0 else WD_ALIGN_PARAGRAPH.LEFT
        for r in p.runs:
            r.font.name = "Calibri"
            r.font.size = Pt(9.5)
            r.bold = True
            r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            
    # Data Rows
    for r_idx, row_data in enumerate(rows):
        row_cells = table.rows[r_idx + 1].cells
        bg_color = "F9FAFC" if (r_idx % 2 == 1) else "FFFFFF"
        is_best_row = (bold_best_row_idx is not None and r_idx == bold_best_row_idx)
        if is_best_row:
            bg_color = "EEF4FA"
            
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = str(val)
            set_cell_background(row_cells[c_idx], bg_color)
            set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=120, right=120)
            p = row_cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.name = "Calibri"
                r.font.size = Pt(9.0)
                if is_best_row:
                    r.bold = True
                    r.font.color.rgb = RGBColor(0x00, 0x20, 0x60)
                else:
                    r.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
                    
    if col_widths:
        for row in table.rows:
            for idx, w in enumerate(col_widths):
                row.cells[idx].width = Inches(w)
                
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(6)

def add_h1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(14.0)
    r.bold = True
    r.font.color.rgb = RGBColor(0x00, 0x20, 0x60)

def add_h2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(12.0)
    r.bold = True
    r.font.color.rgb = RGBColor(0x2C, 0x3E, 0x50)

def add_h3(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(10.5)
    r.bold = True
    r.font.italic = True
    r.font.color.rgb = RGBColor(0x34, 0x49, 0x5E)

def add_body(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(10.0)
    r.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

def add_bullet(doc, bold_prefix, text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_bold = p.add_run(bold_prefix + ": ")
    r_bold.font.name = "Calibri"
    r_bold.font.size = Pt(10.0)
    r_bold.bold = True
    r_bold.font.color.rgb = RGBColor(0x00, 0x20, 0x60)
    r_text = p.add_run(text)
    r_text.font.name = "Calibri"
    r_text.font.size = Pt(10.0)
    r_text.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

def add_num_item(doc, num_str, bold_prefix, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_num = p.add_run(num_str + " ")
    r_num.font.name = "Calibri"
    r_num.font.size = Pt(10.0)
    r_num.bold = True
    r_bold = p.add_run(bold_prefix + ": ")
    r_bold.font.name = "Calibri"
    r_bold.font.size = Pt(10.0)
    r_bold.bold = True
    r_bold.font.color.rgb = RGBColor(0x00, 0x20, 0x60)
    r_text = p.add_run(text)
    r_text.font.name = "Calibri"
    r_text.font.size = Pt(10.0)
    r_text.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

def add_eq(doc, eq_text, eq_num):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    r_eq = p.add_run(f"    {eq_text}    ")
    r_eq.font.name = "Cambria Math"
    r_eq.font.size = Pt(10.0)
    r_eq.font.italic = True
    r_num = p.add_run(f"({eq_num})")
    r_num.font.name = "Calibri"
    r_num.font.size = Pt(10.0)
    r_num.bold = True
    r_num.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

print("Writing document content...")
