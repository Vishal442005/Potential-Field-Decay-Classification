import os
import re
import sys
import pdfplumber

sys.stdout.reconfigure(encoding='utf-8')

def detailed_paper_study(pdf_path):
    name = os.path.basename(pdf_path)
    print(f"\n{'='*75}\nPAPER: {name}\n{'='*75}")
    with pdfplumber.open(pdf_path) as pdf:
        num_pages = len(pdf.pages)
        print(f"Total Pages: {num_pages}")
        
        # Read text
        full_text = []
        for i in range(min(5, num_pages)):
            t = pdf.pages[i].extract_text() or ""
            full_text.append(f"--- Page {i+1} ---\n" + t)
        
        header_text = "\n".join(full_text[:2])
        print("\n--- Abstract / Opening Section Preview ---")
        lines = [l.strip() for l in header_text.splitlines() if l.strip()]
        for line in lines[:20]:
            print("  ", line[:100])
            
        print("\n--- Figure and Table Analysis Across Document ---")
        fig_count = 0
        tab_count = 0
        all_text = ""
        for p_idx, page in enumerate(pdf.pages):
            p_text = page.extract_text() or ""
            all_text += f"\nPAGE {p_idx+1}\n" + p_text
            for match in re.finditer(r'(Figure\s+[0-9]+[.:][^\n]+(?:\n[^\n]+)?)', p_text, re.IGNORECASE):
                fig_count += 1
                if fig_count <= 4:
                    print(f"  [Figure {fig_count} (p.{p_idx+1})]: {' '.join(match.group(1).split())[:130]}...")
            for match in re.finditer(r'(Table\s+[0-9]+[.:][^\n]+(?:\n[^\n]+)?)', p_text, re.IGNORECASE):
                tab_count += 1
                if tab_count <= 4:
                    print(f"  [Table {tab_count} (p.{p_idx+1})]: {' '.join(match.group(1).split())[:130]}...")
                    
        print(f"\nTotal Figures Detected: {fig_count}, Total Tables: {tab_count}")

pdf_dir = "related_papers"
for f in sorted(os.listdir(pdf_dir)):
    if f.endswith(".pdf"):
        detailed_paper_study(os.path.join(pdf_dir, f))
