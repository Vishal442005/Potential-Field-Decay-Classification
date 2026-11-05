import os
import zipfile

def create_zip():
    zip_filename = "PFDC_Manuscript.zip"
    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as z:
        for f in ["PFDC_Manuscript.tex", "PFDC_Manuscript.pdf", "PFDC_Manuscript.docx", "references.bib", "elsarticle-num.bst"]:
            if os.path.exists(f):
                z.write(f, arcname=f)
        # Add figures
        if os.path.exists("figures"):
            for root, dirs, files in os.walk("figures"):
                for file in files:
                    full_path = os.path.join(root, file)
                    z.write(full_path, arcname=os.path.relpath(full_path, "."))
    print(f"Successfully packaged {zip_filename}, size: {os.path.getsize(zip_filename)} bytes")

if __name__ == "__main__":
    create_zip()
