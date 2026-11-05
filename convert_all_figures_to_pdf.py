import os
from PIL import Image

dirs_to_process = [
    "figures",
    os.path.join("elsevier_submission", "figures"),
    os.path.join("tpami_submission", "figures")
]

converted_count = 0
deleted_count = 0

for d in dirs_to_process:
    if not os.path.exists(d):
        continue
    for fname in os.listdir(d):
        if fname.lower().endswith(".png"):
            png_path = os.path.join(d, fname)
            base_name = os.path.splitext(fname)[0]
            pdf_path = os.path.join(d, base_name + ".pdf")
            
            try:
                im = Image.open(png_path)
                if im.mode in ("RGBA", "P"):
                    im = im.convert("RGB")
                im.save(pdf_path, "PDF", resolution=300.0)
                
                if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                    converted_count += 1
                    os.remove(png_path)
                    deleted_count += 1
                    print(f"[{d}] Converted & Deleted: {fname} -> {base_name}.pdf ({os.path.getsize(pdf_path)} bytes)")
                else:
                    print(f"Error: {pdf_path} failed to create or is empty.")
            except Exception as e:
                print(f"Error converting {png_path}: {e}")

print(f"\nTotal converted to PDF: {converted_count}")
print(f"Total PNGs deleted: {deleted_count}")
